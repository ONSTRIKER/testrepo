"""
Multiple Choice Grader

Grades multiple choice and simple objective questions.

Question Types Supported:
- Multiple choice (A/B/C/D)
- True/False
- Matching
- Fill-in-the-blank (exact match)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class MCQuestion(BaseModel):
    """Multiple choice question."""

    question_id: str
    question_text: str
    correct_answer: str  # "A", "B", "C", "D", or exact text
    question_type: str  # "multiple_choice", "true_false", "matching"


class MCResponse(BaseModel):
    """Student response to MC question."""

    question_id: str
    student_answer: str
    concept_id: Optional[str] = None


class MCGradingResult(BaseModel):
    """Grading result for one MC question."""

    question_id: str
    is_correct: bool
    student_answer: str
    correct_answer: str
    points_earned: float
    points_possible: float
    feedback: Optional[str] = None


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# MULTIPLE CHOICE GRADER
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class MultipleChoiceGrader:
    """
    Grades multiple choice and objective questions.

    Simple deterministic grading based on exact match.
    """

    def grade_question(
        self,
        question: MCQuestion,
        response: MCResponse,
        points_possible: float = 1.0,
    ) -> MCGradingResult:
        """
        Grade a single multiple choice question.

        Args:
            question: Question with correct answer
            response: Student response
            points_possible: Points for correct answer

        Returns:
            MCGradingResult
        """
        # Normalize answers (case-insensitive, strip whitespace)
        correct_normalized = question.correct_answer.strip().upper()
        student_normalized = response.student_answer.strip().upper()

        # Check if correct
        is_correct = correct_normalized == student_normalized

        # Points earned
        points_earned = points_possible if is_correct else 0.0

        # Feedback
        if is_correct:
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. The correct answer is {question.correct_answer}."

        return MCGradingResult(
            question_id=question.question_id,
            is_correct=is_correct,
            student_answer=response.student_answer,
            correct_answer=question.correct_answer,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
        )

    def grade_assessment(
        self,
        questions: List[MCQuestion],
        responses: List[MCResponse],
        points_per_question: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        Grade an entire multiple choice assessment.

        Args:
            questions: List of questions with correct answers
            responses: List of student responses
            points_per_question: Optional dict of question_id -> points

        Returns:
            Dict with grading results and summary
        """
        # Create question lookup
        question_map = {q.question_id: q for q in questions}

        # Grade each response
        results = []
        total_points_earned = 0.0
        total_points_possible = 0.0
        correct_count = 0

        for response in responses:
            question = question_map.get(response.question_id)

            if not question:
                # Question not found
                continue

            # Get points for this question
            if points_per_question:
                points = points_per_question.get(response.question_id, 1.0)
            else:
                points = 1.0

            # Grade
            result = self.grade_question(question, response, points)
            results.append(result)

            # Update totals
            total_points_earned += result.points_earned
            total_points_possible += result.points_possible

            if result.is_correct:
                correct_count += 1

        # Calculate summary statistics
        score_percentage = (
            (total_points_earned / total_points_possible * 100)
            if total_points_possible > 0
            else 0.0
        )

        accuracy = (
            (correct_count / len(results) * 100)
            if len(results) > 0
            else 0.0
        )

        return {
            "results": results,
            "summary": {
                "total_questions": len(results),
                "correct_count": correct_count,
                "incorrect_count": len(results) - correct_count,
                "accuracy_percentage": round(accuracy, 2),
                "points_earned": round(total_points_earned, 2),
                "points_possible": round(total_points_possible, 2),
                "score_percentage": round(score_percentage, 2),
            },
        }


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def grade_mc_assessment(
    questions: List[MCQuestion],
    responses: List[MCResponse],
) -> Dict:
    """
    Convenience function to grade MC assessment.

    Args:
        questions: Questions with correct answers
        responses: Student responses

    Returns:
        Grading results with summary
    """
    grader = MultipleChoiceGrader()
    return grader.grade_assessment(questions, responses)
