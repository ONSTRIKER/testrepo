"""
Assessments API Routes

Endpoints for assessment grading and scoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

from ...grader.constructed_response import AssessmentGrader, AssessmentQuestion, StudentSubmission
from ...student_model.interface import StudentModelInterface

logger = logging.getLogger("api.assessments")

router = APIRouter()

# Shared instances
student_model = StudentModelInterface()


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class SubmitAssessmentRequest(BaseModel):
    """Request to submit and grade assessment."""

    assessment_id: str
    student_id: str
    questions: List[Dict]  # List of AssessmentQuestion dicts
    responses: List[Dict]  # List of {question_id, answer}
    update_mastery: bool = True


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post("/submit")
async def submit_assessment(request: SubmitAssessmentRequest):
    """
    Submit and grade assessment.

    POST /api/assessments/submit

    Request body:
    {
        "assessment_id": "assessment_123",
        "student_id": "student_456",
        "questions": [
            {
                "question_id": "q1",
                "question_text": "What is photosynthesis?",
                "question_type": "constructed_response",
                "concept_id": "photosynthesis_process",
                "points_possible": 5.0,
                "rubric": {...}
            }
        ],
        "responses": [
            {"question_id": "q1", "answer": "Photosynthesis is..."}
        ],
        "update_mastery": true
    }

    Returns:
        Graded assessment with scores and feedback
    """
    try:
        logger.info(f"Grading assessment {request.assessment_id} for student {request.student_id}")

        # Convert questions to AssessmentQuestion objects
        questions = [AssessmentQuestion(**q) for q in request.questions]

        # Create submission
        from datetime import datetime
        import uuid

        submission = StudentSubmission(
            submission_id=f"submission_{uuid.uuid4().hex[:12]}",
            student_id=request.student_id,
            assessment_id=request.assessment_id,
            responses=request.responses,
            submitted_at=datetime.utcnow().isoformat(),
        )

        # Grade assessment
        grader = AssessmentGrader(student_model=student_model)
        graded = grader.grade_submission(
            questions=questions,
            submission=submission,
            update_mastery=request.update_mastery,
        )

        logger.info(
            f"Assessment graded: {graded.grading_id} | "
            f"Score: {graded.score_percentage:.1f}% | "
            f"Cost: ${graded.cost:.4f}"
        )

        return {
            "status": "success",
            "graded_assessment": graded.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error grading assessment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assessment_id}/results/{student_id}")
async def get_assessment_results(assessment_id: str, student_id: str):
    """
    Get graded assessment results.

    GET /api/assessments/{assessment_id}/results/{student_id}

    Returns:
        Graded assessment if found
    """
    # TODO: Implement assessment retrieval from database
    raise HTTPException(status_code=501, detail="Assessment retrieval not yet implemented")


@router.get("/students/{student_id}/history")
async def get_student_assessment_history(student_id: str, limit: int = 10):
    """
    Get student assessment history.

    GET /api/assessments/students/{student_id}/history?limit=10

    Returns:
        List of graded assessments for student
    """
    # TODO: Implement assessment history retrieval
    raise HTTPException(status_code=501, detail="Assessment history not yet implemented")


@router.post("/batch-grade")
async def batch_grade_assessments(
    assessment_id: str,
    questions: List[Dict],
    submissions: List[Dict],
):
    """
    Grade multiple student submissions for the same assessment.

    POST /api/assessments/batch-grade

    Request body:
    {
        "assessment_id": "assessment_123",
        "questions": [...],
        "submissions": [
            {"student_id": "s1", "responses": [...]},
            {"student_id": "s2", "responses": [...]}
        ]
    }

    Returns:
        List of graded assessments
    """
    try:
        logger.info(f"Batch grading assessment {assessment_id} for {len(submissions)} students")

        # Convert questions
        question_objs = [AssessmentQuestion(**q) for q in questions]

        # Grade each submission
        grader = AssessmentGrader(student_model=student_model)
        graded_results = []

        for sub in submissions:
            from datetime import datetime
            import uuid

            submission = StudentSubmission(
                submission_id=f"submission_{uuid.uuid4().hex[:12]}",
                student_id=sub["student_id"],
                assessment_id=assessment_id,
                responses=sub["responses"],
                submitted_at=datetime.utcnow().isoformat(),
            )

            graded = grader.grade_submission(
                questions=question_objs,
                submission=submission,
                update_mastery=True,
            )

            graded_results.append(graded.model_dump())

        logger.info(f"Batch grading complete: {len(graded_results)} assessments graded")

        return {
            "status": "success",
            "graded_assessments": graded_results,
            "count": len(graded_results),
        }

    except Exception as e:
        logger.error(f"Error batch grading: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
