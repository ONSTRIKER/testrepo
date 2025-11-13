"""
Unified Assessment Grader

Grades complete assessments with both multiple choice and constructed responses.

Integrates:
- Multiple choice grader (exact match)
- Rubric-based grader (Claude scoring)
- BKT mastery updates (feeds back to Engine 5)
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .multiple_choice import MultipleChoiceGrader, MCQuestion, MCResponse
from .rubric_engine import (
    RubricGradingEngine,
    Rubric,
    ConstructedResponse,
    ConstructedResponseGrade,
)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class AssessmentQuestion(BaseModel):
    """Single assessment question (any type)."""

    question_id: str
    question_text: str
    question_type: str  # "multiple_choice", "constructed_response", "true_false"
    concept_id: str
    points_possible: float

    # For MC questions
    correct_answer: Optional[str] = None

    # For constructed response
    rubric: Optional[Rubric] = None


class StudentSubmission(BaseModel):
    """Student submission for entire assessment."""

    submission_id: str
    student_id: str
    assessment_id: str
    responses: List[Dict]  # List of {question_id, answer}
    submitted_at: str


class GradedAssessment(BaseModel):
    """Complete graded assessment."""

    grading_id: str
    student_id: str
    assessment_id: str

    # Scores
    total_points_earned: float
    total_points_possible: float
    score_percentage: float

    # Question results
    mc_results: List[Dict]  # Multiple choice results
    cr_results: List[ConstructedResponseGrade]  # Constructed response results

    # Concept mastery (for BKT updates)
    concept_scores: Dict[str, Dict]  # {concept_id: {correct: int, total: int}}

    # Metadata
    graded_at: str
    cost: float


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# UNIFIED ASSESSMENT GRADER
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class AssessmentGrader:
    """
    Unified grader for complete assessments.

    Handles both multiple choice and constructed responses,
    and feeds results back to Student Model for BKT updates.
    """

    def __init__(
        self,
        student_model=None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize assessment grader.

        Args:
            student_model: StudentModelInterface instance
            anthropic_api_key: Anthropic API key for CR grading
        """
        self.student_model = student_model
        self.mc_grader = MultipleChoiceGrader()
        self.cr_grader = RubricGradingEngine(anthropic_api_key=anthropic_api_key)

    def grade_submission(
        self,
        questions: List[AssessmentQuestion],
        submission: StudentSubmission,
        update_mastery: bool = True,
    ) -> GradedAssessment:
        """
        Grade a complete assessment submission.

        Args:
            questions: List of assessment questions
            submission: Student submission
            update_mastery: If True, update Student Model with results

        Returns:
            GradedAssessment
        """
        grading_id = f"grading_{uuid.uuid4().hex[:12]}"

        # Separate MC and CR questions
        mc_questions = []
        cr_questions = []
        question_map = {}

        for q in questions:
            question_map[q.question_id] = q

            if q.question_type in ["multiple_choice", "true_false", "matching"]:
                mc_questions.append(q)
            elif q.question_type == "constructed_response":
                cr_questions.append(q)

        # Grade MC questions
        mc_results = self._grade_mc_questions(mc_questions, submission)

        # Grade CR questions
        cr_results = self._grade_cr_questions(cr_questions, submission)

        # Calculate totals
        total_points_earned = 0.0
        total_points_possible = 0.0

        for result in mc_results:
            total_points_earned += result["points_earned"]
            total_points_possible += result["points_possible"]

        for result in cr_results:
            total_points_earned += result.total_points_earned
            total_points_possible += result.total_points_possible

        score_percentage = (
            (total_points_earned / total_points_possible * 100)
            if total_points_possible > 0
            else 0.0
        )

        # Calculate concept-level scores (for BKT)
        concept_scores = self._calculate_concept_scores(
            mc_results, cr_results, question_map
        )

        # Build graded assessment
        graded = GradedAssessment(
            grading_id=grading_id,
            student_id=submission.student_id,
            assessment_id=submission.assessment_id,
            total_points_earned=round(total_points_earned, 2),
            total_points_possible=round(total_points_possible, 2),
            score_percentage=round(score_percentage, 2),
            mc_results=mc_results,
            cr_results=cr_results,
            concept_scores=concept_scores,
            graded_at=datetime.utcnow().isoformat(),
            cost=self.cr_grader.get_cost_summary()["total_cost"],
        )

        # Update mastery in Student Model
        if update_mastery and self.student_model:
            self._update_student_mastery(graded, question_map)

        return graded

    def _grade_mc_questions(
        self,
        mc_questions: List[AssessmentQuestion],
        submission: StudentSubmission,
    ) -> List[Dict]:
        """Grade multiple choice questions."""
        # Build MC question objects
        mc_question_objs = []
        for q in mc_questions:
            mc_question_objs.append(
                MCQuestion(
                    question_id=q.question_id,
                    question_text=q.question_text,
                    correct_answer=q.correct_answer,
                    question_type=q.question_type,
                )
            )

        # Build MC response objects
        mc_responses = []
        response_map = {r["question_id"]: r["answer"] for r in submission.responses}

        for q in mc_questions:
            if q.question_id in response_map:
                mc_responses.append(
                    MCResponse(
                        question_id=q.question_id,
                        student_answer=response_map[q.question_id],
                        concept_id=q.concept_id,
                    )
                )

        # Grade with MC grader
        if mc_question_objs and mc_responses:
            mc_grading = self.mc_grader.grade_assessment(mc_question_objs, mc_responses)
            return [
                {
                    "question_id": r.question_id,
                    "is_correct": r.is_correct,
                    "points_earned": r.points_earned,
                    "points_possible": r.points_possible,
                    "feedback": r.feedback,
                    "concept_id": next(
                        (q.concept_id for q in mc_questions if q.question_id == r.question_id),
                        None
                    ),
                }
                for r in mc_grading["results"]
            ]
        else:
            return []

    def _grade_cr_questions(
        self,
        cr_questions: List[AssessmentQuestion],
        submission: StudentSubmission,
    ) -> List[ConstructedResponseGrade]:
        """Grade constructed response questions."""
        cr_results = []
        response_map = {r["question_id"]: r["answer"] for r in submission.responses}

        for q in cr_questions:
            if q.question_id not in response_map:
                continue

            # Build constructed response object
            student_response = ConstructedResponse(
                question_id=q.question_id,
                student_id=submission.student_id,
                response_text=response_map[q.question_id],
                concept_id=q.concept_id,
            )

            # Grade with rubric engine
            if q.rubric:
                grade = self.cr_grader.grade_response(
                    question_text=q.question_text,
                    student_response=student_response,
                    rubric=q.rubric,
                )
                cr_results.append(grade)

        return cr_results

    def _calculate_concept_scores(
        self,
        mc_results: List[Dict],
        cr_results: List[ConstructedResponseGrade],
        question_map: Dict,
    ) -> Dict[str, Dict]:
        """
        Calculate scores per concept for BKT updates.

        Args:
            mc_results: MC grading results
            cr_results: CR grading results
            question_map: Map of question_id to AssessmentQuestion

        Returns:
            Dict mapping concept_id to {correct, total, mastery_estimate}
        """
        concept_scores = {}

        # Process MC results
        for result in mc_results:
            concept_id = result.get("concept_id")
            if not concept_id:
                continue

            if concept_id not in concept_scores:
                concept_scores[concept_id] = {"correct": 0, "total": 0}

            concept_scores[concept_id]["total"] += 1
            if result["is_correct"]:
                concept_scores[concept_id]["correct"] += 1

        # Process CR results (use score percentage as proxy for correctness)
        for result in cr_results:
            question = question_map.get(result.question_id)
            if not question or not question.concept_id:
                continue

            concept_id = question.concept_id

            if concept_id not in concept_scores:
                concept_scores[concept_id] = {"correct": 0, "total": 0}

            concept_scores[concept_id]["total"] += 1
            # Consider correct if score >= 70%
            if result.score_percentage >= 70:
                concept_scores[concept_id]["correct"] += 1

        # Calculate mastery estimates
        for concept_id, scores in concept_scores.items():
            scores["mastery_estimate"] = (
                scores["correct"] / scores["total"]
                if scores["total"] > 0
                else 0.0
            )

        return concept_scores

    def _update_student_mastery(
        self,
        graded: GradedAssessment,
        question_map: Dict,
    ):
        """
        Update Student Model with grading results.

        Uses Engine 5's BKT update method to refine mastery estimates.
        """
        try:
            # Import Engine 5 for mastery updates
            from ..engines.engine_5_diagnostic import DiagnosticEngine

            diagnostic_engine = DiagnosticEngine(student_model=self.student_model)

            # Update mastery for each concept
            for concept_id, scores in graded.concept_scores.items():
                # Build observations (True/False for each question)
                observations = (
                    [True] * scores["correct"] + [False] * (scores["total"] - scores["correct"])
                )

                # Update mastery using BKT
                diagnostic_engine.update_mastery_from_assessment(
                    student_id=graded.student_id,
                    concept_id=concept_id,
                    observations=observations,
                )

        except Exception as e:
            print(f"Error updating mastery: {str(e)}")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def grade_assessment(
    questions: List[AssessmentQuestion],
    submission: StudentSubmission,
    student_model=None,
) -> GradedAssessment:
    """
    Convenience function to grade assessment.

    Args:
        questions: Assessment questions
        submission: Student submission
        student_model: Optional Student Model for mastery updates

    Returns:
        GradedAssessment
    """
    grader = AssessmentGrader(student_model=student_model)
    return grader.grade_submission(questions, submission)
