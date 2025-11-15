"""
Engine 1: Lesson Architect

Creates comprehensive 10-part lesson blueprints with standards alignment.

10-Part Lesson Structure:
1. Opening / Hook (5 mins)
2. Learning Objectives
3. Standards Alignment
4. Direct Instruction (15 mins)
5. Guided Practice (10 mins)
6. Independent Practice (10 mins)
7. Assessment (5 mins)
8. Differentiation Strategies
9. Materials & Resources
10. Closure (5 mins)

Queries Student Model for:
- Class composition (number of students, IEP needs)
- Prerequisite knowledge (mastery data)
- Reading levels and learning preferences
"""

import json
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine


# ═══════════════════════════════════════════════════════════
# INPUT/OUTPUT SCHEMAS
# ═══════════════════════════════════════════════════════════


class LessonInput(BaseModel):
    """Input for lesson generation."""

    topic: str
    grade_level: str  # "9", "10", "11", "12"
    subject: str  # "Science", "Math", etc.
    duration_minutes: int = 45
    standards: List[str] = []
    class_id: Optional[str] = None  # If provided, queries Student Model for context


class LessonSection(BaseModel):
    """Single section of the lesson."""

    section_number: int
    section_name: str
    duration_minutes: Optional[int] = None
    content: str
    teacher_notes: Optional[str] = None


class LessonBlueprint(BaseModel):
    """Complete 10-part lesson blueprint."""

    lesson_id: str
    topic: str
    grade_level: str
    subject: str
    duration_minutes: int
    standards: List[str]
    
    # 10 sections
    sections: List[LessonSection]
    
    # Additional metadata
    class_context: Optional[Dict] = None  # Student Model data if class_id provided
    research_citations: List[str] = []
    generated_at: str


# ═══════════════════════════════════════════════════════════
# ENGINE 1: LESSON ARCHITECT
# ═══════════════════════════════════════════════════════════


class LessonArchitect(BaseEngine):
    """
    Engine 1: Generates comprehensive 10-part lesson blueprints.
    
    Uses Understanding by Design (UbD) framework and integrates
    with Student Model for class-specific adaptations.
    """

    def generate(
        self,
        topic: str,
        grade_level: str,
        subject: str,
        duration_minutes: int = 45,
        standards: Optional[List[str]] = None,
        class_id: Optional[str] = None,
    ) -> LessonBlueprint:
        """
        Generate a complete 10-part lesson blueprint.

        Args:
            topic: Lesson topic (e.g., "Photosynthesis Process")
            grade_level: Grade level ("9", "10", "11", "12")
            subject: Subject area
            duration_minutes: Lesson duration (default 45)
            standards: List of standards (NGSS, CCSS, etc.)
            class_id: Optional class ID to query Student Model

        Returns:
            LessonBlueprint with all 10 sections
        """
        # Generate lesson ID
        import uuid
        lesson_id = f"lesson_{uuid.uuid4().hex[:12]}"

        self._log_decision(f"Generating lesson: {topic} (Grade {grade_level}, {subject})")

        # Step 1: Query Student Model for class context (if provided)
        class_context = None
        if class_id:
            class_context = self._get_class_context(class_id)
            # Only log if class was found (doesn't have 'error' key)
            if class_context and 'error' not in class_context:
                self._log_decision(
                    f"Class context: {class_context['total_students']} students, "
                    f"{class_context['students_with_ieps']} with IEPs"
                )
            else:
                self._log_decision(f"Class {class_id} not found, proceeding without class context", level="warning")
                class_context = None  # Set to None so it's not used in prompts

        # Step 2: Build prompt for Claude
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            topic=topic,
            grade_level=grade_level,
            subject=subject,
            duration_minutes=duration_minutes,
            standards=standards or [],
            class_context=class_context,
        )

        # Step 3: Call Claude API
        self._log_decision("Calling Claude API for lesson generation")
        response_text = self._call_claude(system_prompt, user_prompt)

        # Step 4: Parse response into structured format
        lesson_data = self._parse_lesson_response(response_text)

        # Step 5: Build LessonBlueprint
        sections = []
        for idx, section_data in enumerate(lesson_data["sections"], start=1):
            sections.append(
                LessonSection(
                    section_number=idx,
                    section_name=section_data["name"],
                    duration_minutes=section_data.get("duration"),
                    content=section_data["content"],
                    teacher_notes=section_data.get("notes"),
                )
            )

        blueprint = LessonBlueprint(
            lesson_id=lesson_id,
            topic=topic,
            grade_level=grade_level,
            subject=subject,
            duration_minutes=duration_minutes,
            standards=standards or [],
            sections=sections,
            class_context=class_context,
            research_citations=lesson_data.get("citations", []),
            generated_at=lesson_data.get("timestamp", ""),
        )

        self._log_decision(f"Lesson generated successfully: {lesson_id}")
        cost_summary = self.get_cost_summary()
        self._log_decision(f"Cost: ${cost_summary['total_cost']:.4f}")

        return blueprint

    def _get_class_context(self, class_id: str) -> Dict:
        """
        Query Student Model for class composition.

        Args:
            class_id: Class identifier

        Returns:
            Dict with class context (student count, IEPs, reading levels)
        """
        # Get class roster summary
        roster = self.student_model.get_class_roster(class_id)

        if not roster:
            self._log_decision(f"Class {class_id} not found", level="warning")
            return {"error": "Class not found"}

        # Get detailed student profiles
        students = self.student_model.get_class_students(class_id)

        # Aggregate reading levels
        reading_level_counts = {}
        for student in students:
            level = student.reading_level.value
            reading_level_counts[level] = reading_level_counts.get(level, 0) + 1

        # Get students with IEPs (detailed)
        iep_students = [s for s in students if s.has_iep]

        return {
            "class_id": class_id,
            "class_name": roster.class_name,
            "total_students": roster.total_students,
            "students_with_ieps": roster.students_with_ieps,
            "reading_level_distribution": reading_level_counts,
            "iep_accommodations_needed": len(iep_students) > 0,
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt for Claude."""
        return """You are an expert K-12 educator specializing in lesson planning using the Understanding by Design (UbD) framework.

Your task is to create comprehensive, standards-aligned lesson plans that:
- Engage diverse learners including students with IEPs
- Follow evidence-based instructional practices
- Include clear learning objectives and assessments
- Provide differentiation strategies
- Reference educational research when appropriate

You must respond ONLY with valid JSON in this exact format:

{
  "sections": [
    {
      "name": "Opening / Hook",
      "duration": 5,
      "content": "Detailed description of the opening activity...",
      "notes": "Teacher notes and tips..."
    },
    ... (10 sections total)
  ],
  "citations": ["Module X: Research citation...", ...],
  "timestamp": "2024-11-13T12:00:00Z"
}

The 10 required sections are:
1. Opening / Hook
2. Learning Objectives
3. Standards Alignment
4. Direct Instruction
5. Guided Practice
6. Independent Practice
7. Assessment
8. Differentiation Strategies
9. Materials & Resources
10. Closure

Be specific, practical, and teacher-friendly. Avoid jargon."""

    def _build_user_prompt(
        self,
        topic: str,
        grade_level: str,
        subject: str,
        duration_minutes: int,
        standards: List[str],
        class_context: Optional[Dict],
    ) -> str:
        """Build user prompt with all context."""
        prompt = f"""Create a {duration_minutes}-minute lesson plan for:

**Topic:** {topic}
**Grade Level:** {grade_level}
**Subject:** {subject}
**Duration:** {duration_minutes} minutes
"""

        if standards:
            prompt += f"\n**Standards to Address:**\n"
            for standard in standards:
                prompt += f"- {standard}\n"

        if class_context:
            prompt += f"""
**Class Context:**
- Total Students: {class_context['total_students']}
- Students with IEPs: {class_context['students_with_ieps']}
- Reading Level Distribution: {class_context.get('reading_level_distribution', 'Not specified')}
- IEP Accommodations Needed: {'Yes' if class_context['iep_accommodations_needed'] else 'No'}

Please consider this class composition when designing differentiation strategies.
"""

        prompt += """
Generate a complete 10-section lesson plan in JSON format as specified in the system prompt.

Ensure the lesson:
1. Has an engaging hook that connects to students' lives
2. Includes clear, measurable learning objectives
3. Properly aligns with the specified standards
4. Uses evidence-based instructional strategies
5. Includes formative assessment throughout
6. Provides concrete differentiation strategies (not just "provide support")
7. Lists all necessary materials
8. Has a meaningful closure that reinforces learning

Respond ONLY with the JSON object. No additional text."""

        return prompt

    def _parse_lesson_response(self, response_text: str) -> Dict:
        """
        Parse Claude's JSON response.

        Args:
            response_text: Claude's response (should be JSON)

        Returns:
            Dict with parsed lesson data
        """
        import re

        # Try different extraction methods in order

        # Method 1: Direct JSON parse
        try:
            lesson_data = json.loads(response_text)
            return lesson_data
        except json.JSONDecodeError:
            pass

        # Method 2: Extract from markdown code blocks (```json ... ```)
        try:
            self._log_decision("Attempting to extract JSON from markdown", level="info")
            json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_block_match:
                lesson_data = json.loads(json_block_match.group(1))
                self._log_decision("Successfully extracted JSON from markdown block", level="info")
                return lesson_data
        except (json.JSONDecodeError, AttributeError) as e:
            self._log_decision(f"Markdown extraction failed: {e}", level="warning")

        # Method 3: Find first complete JSON object
        try:
            self._log_decision("Attempting regex JSON extraction", level="info")
            json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response_text, re.DOTALL)
            if json_match:
                lesson_data = json.loads(json_match.group(0))
                self._log_decision("Successfully extracted JSON via regex", level="info")
                return lesson_data
        except (json.JSONDecodeError, AttributeError) as e:
            self._log_decision(f"Regex extraction failed: {e}", level="warning")

        # Fallback: Return error structure with response preview
        self._log_decision("Could not parse lesson response - all methods failed", level="error")
        self._log_decision(f"Response preview: {response_text[:200]}...", level="error")

        return {
            "sections": [
                {
                    "name": "Error",
                    "duration": None,
                    "content": "Failed to parse lesson response. Please try again.",
                    "notes": response_text[:1000],  # Increased from 500 to see more
                }
            ],
            "citations": [],
            "timestamp": "",
        }


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def generate_lesson(
    topic: str,
    grade_level: str,
    subject: str,
    duration_minutes: int = 45,
    standards: Optional[List[str]] = None,
    class_id: Optional[str] = None,
) -> LessonBlueprint:
    """
    Convenience function to generate a lesson.

    Args:
        topic: Lesson topic
        grade_level: Grade level
        subject: Subject area
        duration_minutes: Duration in minutes
        standards: List of standards
        class_id: Optional class ID

    Returns:
        LessonBlueprint
    """
    engine = LessonArchitect()
    return engine.generate(
        topic=topic,
        grade_level=grade_level,
        subject=subject,
        duration_minutes=duration_minutes,
        standards=standards,
        class_id=class_id,
    )


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("""
Usage: python -m src.engines.engine_1_lesson_architect <topic> <grade> <subject>

Example:
  python -m src.engines.engine_1_lesson_architect "Photosynthesis" "9" "Science"
        """)
        sys.exit(1)

    topic = sys.argv[1]
    grade = sys.argv[2]
    subject = sys.argv[3]

    print(f"Generating lesson: {topic} (Grade {grade}, {subject})\n")

    # Generate lesson
    blueprint = generate_lesson(
        topic=topic,
        grade_level=grade,
        subject=subject,
        duration_minutes=45,
        standards=["NGSS-HS-LS1-5: Photosynthesis model"] if "photo" in topic.lower() else [],
    )

    print("=" * 70)
    print(f"LESSON: {blueprint.topic}")
    print("=" * 70)
    print(f"Lesson ID: {blueprint.lesson_id}")
    print(f"Duration: {blueprint.duration_minutes} minutes")
    print(f"Standards: {', '.join(blueprint.standards) if blueprint.standards else 'None'}")
    print("\n")

    for section in blueprint.sections:
        print(f"{'='*70}")
        print(f"SECTION {section.section_number}: {section.section_name}")
        if section.duration_minutes:
            print(f"Duration: {section.duration_minutes} minutes")
        print(f"{'='*70}")
        print(section.content)
        if section.teacher_notes:
            print(f"\n💡 Teacher Notes: {section.teacher_notes}")
        print("\n")

    print("=" * 70)
    print("COST SUMMARY")
    print("=" * 70)
    engine = LessonArchitect()
    cost_summary = engine.get_cost_summary()
    print(f"Total Cost: ${cost_summary['total_cost']:.4f}")
    print(f"Input Tokens: {cost_summary['total_input_tokens']}")
    print(f"Output Tokens: {cost_summary['total_output_tokens']}")
