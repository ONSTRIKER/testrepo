"""
Engine 0: Unit Plan Designer

Generates multi-lesson unit plans using Understanding by Design (UbD) framework.

Core Functionality:
1. Design backward from desired outcomes (UbD Stage 1)
2. Determine acceptable evidence (UbD Stage 2)
3. Plan learning experiences (UbD Stage 3)
4. Generate cohesive multi-lesson sequences
5. Ensure conceptual coherence across lessons

Understanding by Design (UbD) Framework:
- Stage 1: Identify Desired Results (enduring understandings, essential questions)
- Stage 2: Determine Acceptable Evidence (assessments, performance tasks)
- Stage 3: Plan Learning Experiences and Instruction (WHERETO elements)

WHERETO Elements:
- W: Where and why (hook, purpose)
- H: Hook and hold (engagement)
- E: Equip, explore, enable (skill-building)
- R: Rethink, reflect, revise (metacognition)
- E: Evaluate (self-assessment)
- T: Tailored (differentiation)
- O: Organized (coherent structure)
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine


# ═══════════════════════════════════════════════════════════
# INPUT/OUTPUT SCHEMAS
# ═══════════════════════════════════════════════════════════


class LessonOutline(BaseModel):
    """Single lesson within a unit."""

    lesson_number: int
    lesson_title: str
    duration_minutes: int
    learning_objectives: List[str]
    key_concepts: List[str]
    activities: List[str]
    assessment_type: str  # "formative", "summative", "diagnostic"


class UnitPlan(BaseModel):
    """Complete unit plan with multiple lessons."""

    unit_id: str
    unit_title: str
    grade_level: str
    subject: str
    total_lessons: int
    total_duration_days: int

    # UbD Stage 1: Desired Results
    enduring_understandings: List[str]
    essential_questions: List[str]
    key_knowledge: List[str]
    key_skills: List[str]
    standards: List[str]

    # UbD Stage 2: Evidence
    summative_assessments: List[str]
    formative_assessments: List[str]
    performance_tasks: List[str]

    # UbD Stage 3: Learning Plan
    lessons: List[LessonOutline]
    differentiation_strategies: List[str]
    resources: List[str]

    # Metadata
    generated_at: str
    cost: float


# ═══════════════════════════════════════════════════════════
# ENGINE 0: UNIT PLAN DESIGNER
# ═══════════════════════════════════════════════════════════


class UnitPlanDesigner(BaseEngine):
    """
    Engine 0: Generates multi-lesson unit plans using UbD framework.

    Provides coherent instructional sequences that build toward
    enduring understandings.
    """

    def generate(
        self,
        unit_title: str,
        grade_level: str,
        subject: str,
        num_lessons: int,
        standards: Optional[List[str]] = None,
        class_id: Optional[str] = None,
    ) -> UnitPlan:
        """
        Generate complete unit plan.

        Args:
            unit_title: Unit title (e.g., "Ecosystems and Biodiversity")
            grade_level: Grade level
            subject: Subject area
            num_lessons: Number of lessons in unit (typically 5-15)
            standards: Standards addressed
            class_id: Optional class ID for context

        Returns:
            UnitPlan with multi-lesson sequence
        """
        unit_id = f"unit_{uuid.uuid4().hex[:12]}"

        self._log_decision(
            f"Generating unit plan: {unit_title} ({num_lessons} lessons)"
        )

        # Get class context if provided
        class_context = None
        if class_id:
            class_context = self._get_class_context(class_id)

        # Generate unit plan via Claude
        unit_data = self._generate_unit_plan(
            unit_title=unit_title,
            grade_level=grade_level,
            subject=subject,
            num_lessons=num_lessons,
            standards=standards,
            class_context=class_context,
        )

        # Build UnitPlan object
        unit_plan = UnitPlan(
            unit_id=unit_id,
            unit_title=unit_title,
            grade_level=grade_level,
            subject=subject,
            total_lessons=num_lessons,
            total_duration_days=unit_data.get("total_duration_days", num_lessons * 2),
            enduring_understandings=unit_data["enduring_understandings"],
            essential_questions=unit_data["essential_questions"],
            key_knowledge=unit_data["key_knowledge"],
            key_skills=unit_data["key_skills"],
            standards=standards or unit_data.get("standards", []),
            summative_assessments=unit_data["summative_assessments"],
            formative_assessments=unit_data["formative_assessments"],
            performance_tasks=unit_data["performance_tasks"],
            lessons=[LessonOutline(**lesson) for lesson in unit_data["lessons"]],
            differentiation_strategies=unit_data["differentiation_strategies"],
            resources=unit_data["resources"],
            generated_at=datetime.utcnow().isoformat(),
            cost=self.get_cost_summary()["total_cost"],
        )

        self._log_decision(
            f"Unit plan complete: {unit_id} ({len(unit_plan.lessons)} lessons)"
        )

        return unit_plan

    def _generate_unit_plan(
        self,
        unit_title: str,
        grade_level: str,
        subject: str,
        num_lessons: int,
        standards: Optional[List[str]],
        class_context: Optional[Dict],
    ) -> Dict:
        """
        Generate unit plan via Claude API.

        Args:
            unit_title: Unit title
            grade_level: Grade level
            subject: Subject
            num_lessons: Number of lessons
            standards: Standards
            class_context: Class context from Student Model

        Returns:
            Dict with unit plan data
        """
        system_prompt = """You are an expert curriculum designer specializing in Understanding by Design (UbD).

Your task is to create a comprehensive unit plan using the UbD framework.

UbD Framework (Backward Design):
1. STAGE 1: Identify Desired Results
   - What should students understand, know, and be able to do?
   - Enduring understandings (big ideas that transfer)
   - Essential questions (open-ended, thought-provoking)

2. STAGE 2: Determine Acceptable Evidence
   - How will we know if students have achieved the desired results?
   - Summative assessments (end-of-unit)
   - Formative assessments (ongoing)
   - Performance tasks (authentic application)

3. STAGE 3: Plan Learning Experiences
   - What activities will lead to desired results?
   - WHERETO elements for engagement and effectiveness
   - Lesson-by-lesson progression

Respond ONLY with valid JSON in this exact format:

{
  "total_duration_days": 10,
  "enduring_understandings": [
    "Ecosystems are complex systems where organisms interact...",
    ...
  ],
  "essential_questions": [
    "How do organisms depend on and compete for biotic and abiotic factors?",
    ...
  ],
  "key_knowledge": ["Food webs", "Energy flow", ...],
  "key_skills": ["Analyzing data", "Creating models", ...],
  "standards": ["NGSS-HS-LS2-1", ...],
  "summative_assessments": [
    "Ecosystem analysis project",
    "Unit exam covering energy flow and matter cycling"
  ],
  "formative_assessments": [
    "Daily exit tickets",
    "Concept maps",
    "Lab reports"
  ],
  "performance_tasks": [
    "Design a sustainable ecosystem model"
  ],
  "lessons": [
    {
      "lesson_number": 1,
      "lesson_title": "Introduction to Ecosystems",
      "duration_minutes": 45,
      "learning_objectives": [
        "Define ecosystem and identify biotic/abiotic factors",
        "Explain relationships between organisms"
      ],
      "key_concepts": ["Ecosystem", "Biotic factors", "Abiotic factors"],
      "activities": [
        "Video: What is an ecosystem?",
        "Small group: Identify factors in local ecosystem",
        "Exit ticket: Draw and label ecosystem"
      ],
      "assessment_type": "formative"
    },
    ...
  ],
  "differentiation_strategies": [
    "Tiered activities based on readiness",
    "Choice boards for performance tasks",
    "Flexible grouping"
  ],
  "resources": [
    "Textbook chapters 5-7",
    "Khan Academy: Ecology videos",
    "Lab materials for ecosystem investigation"
  ]
}"""

        user_prompt = f"""Create a {num_lessons}-lesson unit plan using the UbD framework.

**Unit Title:** {unit_title}
**Grade Level:** {grade_level}
**Subject:** {subject}
**Number of Lessons:** {num_lessons}
"""

        if standards:
            user_prompt += f"\n**Standards:**\n{chr(10).join(f'- {s}' for s in standards)}\n"

        if class_context:
            user_prompt += f"""
**Class Context:**
- Total Students: {class_context.get('total_students', 'Unknown')}
- Students with IEPs: {class_context.get('students_with_ieps', 'Unknown')}
- Reading Levels: {class_context.get('reading_level_distribution', 'Mixed')}
"""

        user_prompt += """
Create a comprehensive unit plan that:
1. Builds toward enduring understandings (Stage 1)
2. Includes varied assessments (Stage 2)
3. Sequences lessons coherently (Stage 3)
4. Incorporates differentiation strategies
5. Provides 2-3 enduring understandings
6. Provides 3-5 essential questions

Respond ONLY with the JSON object. No additional text."""

        self._log_decision("Calling Claude API for unit plan generation")
        response_text = self._call_claude(system_prompt, user_prompt)

        # Parse response
        unit_data = self._parse_unit_response(response_text)

        return unit_data

    def _parse_unit_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response."""
        try:
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            self._log_decision("JSON parse error, attempting extraction", level="warning")

            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    return data
                except:
                    pass

            # Fallback
            self._log_decision("Could not parse unit response", level="error")
            return {
                "total_duration_days": 10,
                "enduring_understandings": ["Error generating unit plan"],
                "essential_questions": ["Please try again"],
                "key_knowledge": [],
                "key_skills": [],
                "standards": [],
                "summative_assessments": [],
                "formative_assessments": [],
                "performance_tasks": [],
                "lessons": [
                    {
                        "lesson_number": 1,
                        "lesson_title": "Error",
                        "duration_minutes": 45,
                        "learning_objectives": ["Error"],
                        "key_concepts": [],
                        "activities": [],
                        "assessment_type": "formative",
                    }
                ],
                "differentiation_strategies": [],
                "resources": [],
            }

    def _get_class_context(self, class_id: str) -> Dict:
        """
        Get class context from Student Model.

        Args:
            class_id: Class identifier

        Returns:
            Dict with class context
        """
        try:
            roster = self.student_model.get_class_roster(class_id)
            students = self.student_model.get_class_students(class_id)

            # Count IEP students
            students_with_ieps = sum(1 for s in students if s.has_iep)

            # Get reading level distribution
            reading_levels = {}
            for student in students:
                level = student.reading_level.value if student.reading_level else "unknown"
                reading_levels[level] = reading_levels.get(level, 0) + 1

            return {
                "total_students": roster.total_students,
                "students_with_ieps": students_with_ieps,
                "reading_level_distribution": reading_levels,
            }
        except Exception as e:
            self._log_decision(f"Could not fetch class context: {str(e)}", level="warning")
            return {}


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def generate_unit_plan(
    unit_title: str,
    grade_level: str,
    subject: str,
    num_lessons: int,
    standards: Optional[List[str]] = None,
) -> UnitPlan:
    """
    Convenience function to generate unit plan.

    Args:
        unit_title: Unit title
        grade_level: Grade level
        subject: Subject area
        num_lessons: Number of lessons
        standards: Standards addressed

    Returns:
        UnitPlan
    """
    engine = UnitPlanDesigner()
    return engine.generate(
        unit_title=unit_title,
        grade_level=grade_level,
        subject=subject,
        num_lessons=num_lessons,
        standards=standards,
    )


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("""
Usage: python -m src.engines.engine_0_unit_planner <unit_title> <grade> <subject> <num_lessons>

Example:
  python -m src.engines.engine_0_unit_planner "Ecosystems and Biodiversity" "9" "Science" "8"
        """)
        sys.exit(1)

    unit_title = sys.argv[1]
    grade = sys.argv[2]
    subject = sys.argv[3]
    num_lessons = int(sys.argv[4])

    print(f"Generating unit plan: {unit_title}\n")

    # Generate unit plan
    unit = generate_unit_plan(
        unit_title=unit_title,
        grade_level=grade,
        subject=subject,
        num_lessons=num_lessons,
        standards=["NGSS-HS-LS2-1"] if "eco" in unit_title.lower() else [],
    )

    print("=" * 70)
    print(f"UNIT PLAN: {unit.unit_title}")
    print("=" * 70)
    print(f"Unit ID: {unit.unit_id}")
    print(f"Grade: {unit.grade_level} | Subject: {unit.subject}")
    print(f"Duration: {unit.total_duration_days} days ({unit.total_lessons} lessons)")
    print(f"Cost: ${unit.cost:.4f}")
    print()

    # UbD Stage 1
    print("=" * 70)
    print("STAGE 1: DESIRED RESULTS (UbD)")
    print("=" * 70)
    print("\nEnduring Understandings:")
    for i, eu in enumerate(unit.enduring_understandings, 1):
        print(f"  {i}. {eu}")

    print("\nEssential Questions:")
    for i, eq in enumerate(unit.essential_questions, 1):
        print(f"  {i}. {eq}")

    print(f"\nKey Knowledge: {', '.join(unit.key_knowledge[:5])}")
    print(f"Key Skills: {', '.join(unit.key_skills[:5])}")

    # UbD Stage 2
    print("\n" + "=" * 70)
    print("STAGE 2: ACCEPTABLE EVIDENCE (UbD)")
    print("=" * 70)
    print("\nSummative Assessments:")
    for i, sa in enumerate(unit.summative_assessments, 1):
        print(f"  {i}. {sa}")

    print("\nPerformance Tasks:")
    for i, pt in enumerate(unit.performance_tasks, 1):
        print(f"  {i}. {pt}")

    # UbD Stage 3
    print("\n" + "=" * 70)
    print("STAGE 3: LEARNING PLAN (UbD)")
    print("=" * 70)
    for lesson in unit.lessons:
        print(f"\nLesson {lesson.lesson_number}: {lesson.lesson_title}")
        print(f"  Duration: {lesson.duration_minutes} min")
        print(f"  Objectives: {', '.join(lesson.learning_objectives[:2])}")
        print(f"  Assessment: {lesson.assessment_type}")
