"""
Engine 2: Worksheet Designer

Generates 3-tier differentiated worksheets based on diagnostic results.

Core Functionality:
1. Accept tier assignments from Engine 5 (Diagnostic)
2. Generate differentiated worksheets for each tier
3. Same learning objective across all tiers, different scaffolding
4. Query Student Model for reading levels and learning preferences
5. Prepare worksheets for Engine 3 (IEP modifications)

Tier Structure:
- Tier 1 (e75% mastery): Light support, extension activities
- Tier 2 (45-75% mastery): Moderate support, guided practice
- Tier 3 (<45% mastery): Heavy support, extra scaffolding

Differentiation Strategies:
- Vocabulary complexity
- Question types (open-ended vs. structured)
- Scaffolding level (word banks, sentence frames, diagrams)
- Response length expectations
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine
from ..student_model.schemas import TierLevel, StudentProfile


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# INPUT/OUTPUT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class WorksheetQuestion(BaseModel):
    """Single worksheet question."""

    number: int
    question_type: str  # "multiple_choice", "short_answer", "constructed_response", etc.
    question_text: str
    scaffolding: List[str]  # List of scaffolding supports
    correct_answer: Optional[str] = None  # For answer key
    rubric: Optional[str] = None  # For constructed response
    standards: Optional[str] = None


class TierWorksheet(BaseModel):
    """Worksheet for one tier."""

    tier_name: str
    tier_level: TierLevel
    student_count: int
    students: List[Dict]  # Student roster with mastery info
    questions: List[WorksheetQuestion]
    scaffolding_summary: str
    iep_summary: Optional[str] = None  # Summary of IEP needs in this tier


class WorksheetSet(BaseModel):
    """Complete set of 3-tier differentiated worksheets."""

    worksheet_id: str
    lesson_topic: str
    grade_level: str
    subject: str
    class_id: str
    class_name: str
    total_students: int

    # Learning objective (same across all tiers)
    learning_objective: str

    # 3 tiers
    tier_1: TierWorksheet
    tier_2: TierWorksheet
    tier_3: TierWorksheet

    # Metadata
    generated_at: str
    cost: float


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ENGINE 2: WORKSHEET DESIGNER
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class WorksheetDesigner(BaseEngine):
    """
    Engine 2: Generates 3-tier differentiated worksheets.

    Takes diagnostic results from Engine 5 and creates scaffolded
    practice materials targeting the same learning objective.
    """

    def generate(
        self,
        lesson_topic: str,
        learning_objective: str,
        grade_level: str,
        subject: str,
        class_id: str,
        diagnostic_results: Dict,  # From Engine 5
        standards: Optional[List[str]] = None,
        num_questions_per_tier: Dict[str, int] = None,
    ) -> WorksheetSet:
        """
        Generate 3-tier differentiated worksheets.

        Args:
            lesson_topic: Lesson topic (e.g., "Photosynthesis Process")
            learning_objective: Main learning objective (same for all tiers)
            grade_level: Grade level
            subject: Subject area
            class_id: Class identifier
            diagnostic_results: Results from Engine 5 with tier assignments
            standards: List of standards addressed
            num_questions_per_tier: Dict specifying question counts per tier
                                   (default: {"tier_1": 5, "tier_2": 4, "tier_3": 3})

        Returns:
            WorksheetSet with 3 differentiated worksheets
        """
        worksheet_id = f"worksheet_{uuid.uuid4().hex[:12]}"

        self._log_decision(
            f"Generating 3-tier worksheets for {lesson_topic}, class {class_id}"
        )

        # Default question counts
        if num_questions_per_tier is None:
            num_questions_per_tier = {
                "tier_1": 5,
                "tier_2": 4,
                "tier_3": 3,
            }

        # Step 1: Get class information
        roster = self.student_model.get_class_roster(class_id)

        # Step 2: Organize students by tier (from diagnostic results)
        tier_assignments = self._organize_students_by_tier(
            diagnostic_results["student_estimates"]
        )

        # Step 3: Get student profiles for each tier
        tier_1_students = self._get_student_roster(
            tier_assignments["tier_1"], class_id
        )
        tier_2_students = self._get_student_roster(
            tier_assignments["tier_2"], class_id
        )
        tier_3_students = self._get_student_roster(
            tier_assignments["tier_3"], class_id
        )

        # Step 4: Generate questions for each tier via Claude
        tier_1_questions = self._generate_tier_questions(
            tier_level="tier_1",
            learning_objective=learning_objective,
            lesson_topic=lesson_topic,
            grade_level=grade_level,
            subject=subject,
            num_questions=num_questions_per_tier["tier_1"],
            student_profiles=tier_1_students,
            standards=standards,
        )

        tier_2_questions = self._generate_tier_questions(
            tier_level="tier_2",
            learning_objective=learning_objective,
            lesson_topic=lesson_topic,
            grade_level=grade_level,
            subject=subject,
            num_questions=num_questions_per_tier["tier_2"],
            student_profiles=tier_2_students,
            standards=standards,
        )

        tier_3_questions = self._generate_tier_questions(
            tier_level="tier_3",
            learning_objective=learning_objective,
            lesson_topic=lesson_topic,
            grade_level=grade_level,
            subject=subject,
            num_questions=num_questions_per_tier["tier_3"],
            student_profiles=tier_3_students,
            standards=standards,
        )

        # Step 5: Build TierWorksheet objects
        tier_1_ws = TierWorksheet(
            tier_name="Tier 1 - Light Support",
            tier_level=TierLevel.TIER_1,
            student_count=len(tier_1_students),
            students=tier_1_students,
            questions=tier_1_questions,
            scaffolding_summary="Minimal scaffolding, extension activities, higher-order thinking",
            iep_summary=self._get_iep_summary(tier_1_students),
        )

        tier_2_ws = TierWorksheet(
            tier_name="Tier 2 - Moderate Support",
            tier_level=TierLevel.TIER_2,
            student_count=len(tier_2_students),
            students=tier_2_students,
            questions=tier_2_questions,
            scaffolding_summary="Guided practice, word banks, graphic organizers",
            iep_summary=self._get_iep_summary(tier_2_students),
        )

        tier_3_ws = TierWorksheet(
            tier_name="Tier 3 - Heavy Support",
            tier_level=TierLevel.TIER_3,
            student_count=len(tier_3_students),
            students=tier_3_students,
            questions=tier_3_questions,
            scaffolding_summary="Extensive scaffolding, sentence frames, reduced complexity",
            iep_summary=self._get_iep_summary(tier_3_students),
        )

        # Step 6: Build complete WorksheetSet
        worksheet_set = WorksheetSet(
            worksheet_id=worksheet_id,
            lesson_topic=lesson_topic,
            grade_level=grade_level,
            subject=subject,
            class_id=class_id,
            class_name=roster.class_name,
            total_students=roster.total_students,
            learning_objective=learning_objective,
            tier_1=tier_1_ws,
            tier_2=tier_2_ws,
            tier_3=tier_3_ws,
            generated_at=datetime.utcnow().isoformat(),
            cost=self.get_cost_summary()["total_cost"],
        )

        self._log_decision(
            f"Worksheets complete: {worksheet_id} | "
            f"Tier 1: {tier_1_ws.student_count}, "
            f"Tier 2: {tier_2_ws.student_count}, "
            f"Tier 3: {tier_3_ws.student_count}"
        )

        return worksheet_set

    def _organize_students_by_tier(
        self,
        student_estimates: List[Dict],
    ) -> Dict[str, List[str]]:
        """
        Organize student IDs by tier based on mastery estimates.

        Args:
            student_estimates: List of StudentMasteryEstimate dicts from Engine 5

        Returns:
            Dict with tier_1/tier_2/tier_3 keys and student ID lists
        """
        tiers = {
            "tier_1": [],
            "tier_2": [],
            "tier_3": [],
        }

        for estimate in student_estimates:
            student_id = estimate["student_id"]
            tier = estimate["recommended_tier"]

            if tier == TierLevel.TIER_1 or tier == "tier_1":
                tiers["tier_1"].append(student_id)
            elif tier == TierLevel.TIER_2 or tier == "tier_2":
                tiers["tier_2"].append(student_id)
            else:
                tiers["tier_3"].append(student_id)

        return tiers

    def _get_student_roster(
        self,
        student_ids: List[str],
        class_id: str,
    ) -> List[Dict]:
        """
        Get student roster with IEP and mastery info.

        Args:
            student_ids: List of student IDs
            class_id: Class identifier

        Returns:
            List of dicts with student info
        """
        roster = []

        for student_id in student_ids:
            profile = self.student_model.get_student_profile(student_id)

            if not profile:
                continue

            student_dict = {
                "student_id": student_id,
                "name": profile.student_name,
                "has_iep": profile.has_iep,
            }

            # Add IEP accommodations if applicable
            if profile.has_iep:
                iep_data = self.student_model.get_iep_accommodations(student_id)
                if iep_data:
                    student_dict["iep_accommodations"] = [
                        acc["type"] for acc in iep_data.accommodations
                    ]
                    student_dict["primary_disability"] = iep_data.primary_disability.value

            roster.append(student_dict)

        return roster

    def _generate_tier_questions(
        self,
        tier_level: str,
        learning_objective: str,
        lesson_topic: str,
        grade_level: str,
        subject: str,
        num_questions: int,
        student_profiles: List[Dict],
        standards: Optional[List[str]],
    ) -> List[WorksheetQuestion]:
        """
        Generate questions for a specific tier via Claude.

        Args:
            tier_level: "tier_1", "tier_2", or "tier_3"
            learning_objective: Main learning objective
            lesson_topic: Topic
            grade_level: Grade level
            subject: Subject
            num_questions: Number of questions to generate
            student_profiles: Student roster for this tier
            standards: Standards addressed

        Returns:
            List of WorksheetQuestion objects
        """
        # Build tier-specific scaffolding guidance
        if tier_level == "tier_1":
            scaffolding_guidance = """
Tier 1 students (e75% mastery) need MINIMAL scaffolding:
- Open-ended, higher-order thinking questions
- Extension activities and real-world applications
- Minimal word banks or sentence frames
- Encourage synthesis and analysis
- Challenge students to explain and justify
"""
        elif tier_level == "tier_2":
            scaffolding_guidance = """
Tier 2 students (45-75% mastery) need MODERATE scaffolding:
- Mix of structured and open-ended questions
- Word banks and graphic organizers provided
- Sentence frames for constructed response
- Clear examples and step-by-step guidance
- Balance between challenge and support
"""
        else:  # tier_3
            scaffolding_guidance = """
Tier 3 students (<45% mastery) need HEAVY scaffolding:
- Highly structured questions with clear prompts
- Extensive word banks and sentence frames
- Visual supports and diagrams
- Reduced question complexity
- Focus on foundational understanding
- Multiple examples and models
"""

        system_prompt = f"""You are an expert at creating differentiated worksheets for K-12 education.

Your task is to generate {num_questions} questions for {tier_level.upper()} students.

{scaffolding_guidance}

CRITICAL: All tiers target the SAME learning objective but with DIFFERENT scaffolding levels.

Respond ONLY with valid JSON in this exact format:

{{
  "questions": [
    {{
      "number": 1,
      "question_type": "constructed_response",
      "question_text": "Question text here...",
      "scaffolding": ["List of scaffolding supports", "Word bank provided", "Diagram included"],
      "correct_answer": "Answer for teacher answer key",
      "rubric": "Rubric for grading (if applicable)",
      "standards": "NGSS-HS-LS1-5"
    }},
    ...
  ]
}}

Question types to use:
- Tier 1: Constructed response, short answer, analysis questions
- Tier 2: Mix of multiple choice, short answer, fill-in-blank
- Tier 3: Fill-in-blank, matching, simple multiple choice
"""

        user_prompt = f"""Create {num_questions} differentiated questions for {tier_level.upper()}.

**Learning Objective (SAME for all tiers):**
{learning_objective}

**Topic:** {lesson_topic}
**Grade Level:** {grade_level}
**Subject:** {subject}
**Students in this tier:** {len(student_profiles)}
"""

        if standards:
            user_prompt += f"\n**Standards:**\n{chr(10).join(f'- {s}' for s in standards)}\n"

        # Add IEP context if applicable
        iep_count = sum(1 for s in student_profiles if s.get("has_iep", False))
        if iep_count > 0:
            user_prompt += f"\n**Note:** {iep_count} students have IEPs (accommodations will be applied by Engine 3)\n"

        user_prompt += """
Generate the questions in JSON format. Ensure:
1. Questions align with the learning objective
2. Scaffolding is appropriate for the tier level
3. Question types match tier expectations
4. Include answer key and rubrics

Respond ONLY with the JSON object."""

        self._log_decision(f"Calling Claude API for {tier_level} questions")
        response_text = self._call_claude(system_prompt, user_prompt)

        # Parse response
        questions_data = self._parse_questions_response(response_text)

        # Convert to WorksheetQuestion objects
        questions = []
        for q in questions_data["questions"]:
            questions.append(
                WorksheetQuestion(
                    number=q["number"],
                    question_type=q["question_type"],
                    question_text=q["question_text"],
                    scaffolding=q.get("scaffolding", []),
                    correct_answer=q.get("correct_answer"),
                    rubric=q.get("rubric"),
                    standards=q.get("standards"),
                )
            )

        self._log_decision(f"Generated {len(questions)} questions for {tier_level}")
        return questions

    def _parse_questions_response(self, response_text: str) -> Dict:
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
            self._log_decision("Could not parse questions response", level="error")
            return {
                "questions": [
                    {
                        "number": 1,
                        "question_type": "error",
                        "question_text": "Error generating questions. Please try again.",
                        "scaffolding": [],
                        "correct_answer": "N/A",
                    }
                ]
            }

    def _get_iep_summary(self, students: List[Dict]) -> Optional[str]:
        """
        Generate IEP summary for a tier.

        Args:
            students: Student roster

        Returns:
            Summary string or None
        """
        iep_students = [s for s in students if s.get("has_iep", False)]

        if not iep_students:
            return None

        # Count accommodation types
        accommodation_counts = {}
        for student in iep_students:
            for acc in student.get("iep_accommodations", []):
                accommodation_counts[acc] = accommodation_counts.get(acc, 0) + 1

        # Build summary
        summary = f"{len(students)} students " {len(iep_students)} with IEPs"

        if accommodation_counts:
            top_accommodations = sorted(
                accommodation_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            acc_summary = ", ".join(
                f"{acc} ({count})" for acc, count in top_accommodations
            )
            summary += f" " Accommodations: {acc_summary}"

        return summary


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def generate_worksheets(
    lesson_topic: str,
    learning_objective: str,
    grade_level: str,
    subject: str,
    class_id: str,
    diagnostic_results: Dict,
    standards: Optional[List[str]] = None,
) -> WorksheetSet:
    """
    Convenience function to generate differentiated worksheets.

    Args:
        lesson_topic: Lesson topic
        learning_objective: Main learning objective
        grade_level: Grade level
        subject: Subject area
        class_id: Class identifier
        diagnostic_results: Results from Engine 5
        standards: Standards addressed

    Returns:
        WorksheetSet
    """
    engine = WorksheetDesigner()
    return engine.generate(
        lesson_topic=lesson_topic,
        learning_objective=learning_objective,
        grade_level=grade_level,
        subject=subject,
        class_id=class_id,
        diagnostic_results=diagnostic_results,
        standards=standards,
    )


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLI TESTING
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import sys

    print("""
Engine 2: Worksheet Designer

This engine requires diagnostic results from Engine 5.

To test the complete pipeline:
1. Run Engine 1 (Lesson Architect) to generate lesson
2. Run Engine 5 (Diagnostic) to get tier assignments
3. Run Engine 2 (Worksheet Designer) to generate worksheets

Example integration test:
  python -m tests.test_pipeline
    """)
