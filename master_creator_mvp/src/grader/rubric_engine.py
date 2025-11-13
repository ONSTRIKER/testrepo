"""
Rubric-Based Grading Engine

Uses Claude to score constructed responses against rubrics.

Rubric Types:
- Holistic (overall score)
- Analytic (multiple criteria scored separately)
- Single-point (meets/doesn't meet standard)
"""

import json
from typing import Dict, List, Optional
from pydantic import BaseModel
import os

from anthropic import Anthropic


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class RubricCriterion(BaseModel):
    """Single rubric criterion."""

    criterion_name: str
    description: str
    points_possible: float
    levels: Dict[str, str]  # {score: description}


class Rubric(BaseModel):
    """Complete grading rubric."""

    rubric_id: str
    rubric_type: str  # "holistic", "analytic", "single_point"
    total_points: float
    criteria: List[RubricCriterion]
    exemplar_response: Optional[str] = None  # Example of excellent response


class ConstructedResponse(BaseModel):
    """Student constructed response."""

    question_id: str
    student_id: str
    response_text: str
    concept_id: Optional[str] = None


class CriterionScore(BaseModel):
    """Score for one rubric criterion."""

    criterion_name: str
    points_earned: float
    points_possible: float
    level_achieved: str
    feedback: str


class ConstructedResponseGrade(BaseModel):
    """Grade for constructed response."""

    question_id: str
    student_id: str

    # Scoring
    total_points_earned: float
    total_points_possible: float
    score_percentage: float

    # Criterion-level scores
    criterion_scores: List[CriterionScore]

    # Feedback
    overall_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# RUBRIC GRADING ENGINE
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class RubricGradingEngine:
    """
    Uses Claude to score constructed responses against rubrics.

    Provides detailed, criterion-based feedback.
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize grading engine.

        Args:
            anthropic_api_key: Anthropic API key (or from env)
        """
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def grade_response(
        self,
        question_text: str,
        student_response: ConstructedResponse,
        rubric: Rubric,
    ) -> ConstructedResponseGrade:
        """
        Grade a constructed response using rubric.

        Args:
            question_text: The question asked
            student_response: Student's answer
            rubric: Grading rubric

        Returns:
            ConstructedResponseGrade with detailed feedback
        """
        # Build grading prompt
        system_prompt = self._build_system_prompt(rubric)
        user_prompt = self._build_user_prompt(
            question_text, student_response.response_text, rubric
        )

        # Call Claude
        response_text = self._call_claude(system_prompt, user_prompt)

        # Parse response
        grade_data = self._parse_grading_response(response_text, rubric)

        # Build grade object
        grade = ConstructedResponseGrade(
            question_id=student_response.question_id,
            student_id=student_response.student_id,
            total_points_earned=grade_data["total_points_earned"],
            total_points_possible=rubric.total_points,
            score_percentage=round(
                (grade_data["total_points_earned"] / rubric.total_points * 100), 2
            ),
            criterion_scores=grade_data["criterion_scores"],
            overall_feedback=grade_data["overall_feedback"],
            strengths=grade_data["strengths"],
            areas_for_improvement=grade_data["areas_for_improvement"],
        )

        return grade

    def grade_batch(
        self,
        question_text: str,
        student_responses: List[ConstructedResponse],
        rubric: Rubric,
    ) -> List[ConstructedResponseGrade]:
        """
        Grade multiple responses to the same question.

        Args:
            question_text: The question
            student_responses: List of student responses
            rubric: Grading rubric

        Returns:
            List of grades
        """
        grades = []

        for response in student_responses:
            try:
                grade = self.grade_response(question_text, response, rubric)
                grades.append(grade)
            except Exception as e:
                print(f"Error grading response from {response.student_id}: {str(e)}")

        return grades

    def _build_system_prompt(self, rubric: Rubric) -> str:
        """Build system prompt for grading."""
        return f"""You are an expert K-12 teacher grading student responses.

Your task is to score a student's constructed response using the provided rubric.

RUBRIC TYPE: {rubric.rubric_type}
TOTAL POINTS: {rubric.total_points}

Be:
- Fair and objective
- Constructive in feedback
- Specific about strengths and areas for improvement
- Aligned with rubric criteria

Respond ONLY with valid JSON in this exact format:

{{
  "criterion_scores": [
    {{
      "criterion_name": "Content Accuracy",
      "points_earned": 3.5,
      "points_possible": 4.0,
      "level_achieved": "Proficient",
      "feedback": "Student demonstrates solid understanding..."
    }},
    ...
  ],
  "overall_feedback": "This response shows...",
  "strengths": [
    "Clear explanation of photosynthesis process",
    "Accurate use of scientific vocabulary"
  ],
  "areas_for_improvement": [
    "Could provide more detail about chloroplast role",
    "Consider adding a specific example"
  ]
}}"""

    def _build_user_prompt(
        self,
        question_text: str,
        student_response: str,
        rubric: Rubric,
    ) -> str:
        """Build user prompt with question, response, and rubric."""
        prompt = f"""Grade this student response using the rubric.

**QUESTION:**
{question_text}

**STUDENT RESPONSE:**
{student_response}

**RUBRIC CRITERIA:**
"""

        for i, criterion in enumerate(rubric.criteria, 1):
            prompt += f"\n{i}. {criterion.criterion_name} ({criterion.points_possible} points)"
            prompt += f"\n   {criterion.description}\n"
            for score, desc in criterion.levels.items():
                prompt += f"   - {score}: {desc}\n"

        if rubric.exemplar_response:
            prompt += f"\n**EXEMPLAR RESPONSE (for reference):**\n{rubric.exemplar_response}\n"

        prompt += """
Score each criterion and provide specific, constructive feedback.

Respond ONLY with the JSON object. No additional text."""

        return prompt

    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API for grading."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )

        # Track tokens
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens

        return response.content[0].text

    def _parse_grading_response(self, response_text: str, rubric: Rubric) -> Dict:
        """Parse Claude's grading response."""
        try:
            data = json.loads(response_text)

            # Calculate total points
            total_points_earned = sum(
                cs["points_earned"] for cs in data["criterion_scores"]
            )

            # Build criterion scores
            criterion_scores = []
            for cs in data["criterion_scores"]:
                criterion_scores.append(
                    CriterionScore(
                        criterion_name=cs["criterion_name"],
                        points_earned=cs["points_earned"],
                        points_possible=cs["points_possible"],
                        level_achieved=cs["level_achieved"],
                        feedback=cs["feedback"],
                    )
                )

            return {
                "total_points_earned": round(total_points_earned, 2),
                "criterion_scores": criterion_scores,
                "overall_feedback": data["overall_feedback"],
                "strengths": data["strengths"],
                "areas_for_improvement": data["areas_for_improvement"],
            }

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "total_points_earned": 0.0,
                "criterion_scores": [
                    CriterionScore(
                        criterion_name=c.criterion_name,
                        points_earned=0.0,
                        points_possible=c.points_possible,
                        level_achieved="Error",
                        feedback="Error parsing grading response",
                    )
                    for c in rubric.criteria
                ],
                "overall_feedback": "Error grading response. Please try again.",
                "strengths": [],
                "areas_for_improvement": ["Error occurred during grading"],
            }

    def get_cost_summary(self) -> Dict:
        """Get cost summary for grading operations."""
        # Claude Sonnet 4.5 pricing: ~$3/M input, ~$15/M output
        input_cost = (self.total_input_tokens / 1_000_000) * 3.0
        output_cost = (self.total_output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost

        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(total_cost, 4),
        }


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def create_simple_rubric(
    question_id: str,
    criteria: List[Dict],
    total_points: float,
) -> Rubric:
    """
    Create a simple rubric.

    Args:
        question_id: Question identifier
        criteria: List of criterion dicts
        total_points: Total points possible

    Returns:
        Rubric object
    """
    rubric_criteria = []

    for criterion in criteria:
        rubric_criteria.append(
            RubricCriterion(
                criterion_name=criterion["name"],
                description=criterion["description"],
                points_possible=criterion["points"],
                levels=criterion.get("levels", {
                    "4": "Excellent",
                    "3": "Proficient",
                    "2": "Developing",
                    "1": "Beginning",
                    "0": "Not Met"
                }),
            )
        )

    return Rubric(
        rubric_id=f"rubric_{question_id}",
        rubric_type="analytic",
        total_points=total_points,
        criteria=rubric_criteria,
    )
