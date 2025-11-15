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
from ...content_storage.interface import ContentStorageInterface

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

        # Save to database
        graded_data = graded.model_dump()
        with ContentStorageInterface() as storage:
            storage.save_graded_assessment(
                graded_data=graded_data,
                assessment_id=request.assessment_id,
                student_id=request.student_id,
                cost_summary={"total_cost": graded.cost, "input_tokens": 0, "output_tokens": 0}
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
    try:
        # Query Student Model for assessment history
        with StudentModelInterface() as sm:
            assessments = sm.get_assessment_history(student_id, limit=100)

        # Find matching assessment
        matching_assessment = None
        for assessment in assessments:
            if assessment.assessment_id == assessment_id:
                matching_assessment = assessment
                break

        if not matching_assessment:
            raise HTTPException(
                status_code=404,
                detail=f"Assessment results not found for student {student_id} and assessment {assessment_id}"
            )

        return {
            "status": "success",
            "assessment": {
                "assessment_id": matching_assessment.assessment_id,
                "student_id": student_id,
                "percentage": matching_assessment.percentage,
                "raw_score": matching_assessment.raw_score,
                "max_score": matching_assessment.max_score,
                "submitted_at": matching_assessment.submitted_at,
                "graded_at": matching_assessment.graded_at,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/history")
async def get_student_assessment_history(student_id: str, limit: int = 10):
    """
    Get student assessment history.

    GET /api/assessments/students/{student_id}/history?limit=10

    Returns:
        List of graded assessments for student
    """
    try:
        with StudentModelInterface() as sm:
            assessments = sm.get_assessment_history(student_id, limit=limit)

        return {
            "status": "success",
            "assessments": [
                {
                    "assessment_id": a.assessment_id,
                    "percentage": a.percentage,
                    "raw_score": a.raw_score,
                    "max_score": a.max_score,
                    "submitted_at": a.submitted_at,
                    "graded_at": a.graded_at,
                }
                for a in assessments
            ],
            "count": len(assessments)
        }

    except Exception as e:
        logger.error(f"Error retrieving assessment history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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

            # Save to database
            graded_data = graded.model_dump()
            with ContentStorageInterface() as storage:
                storage.save_graded_assessment(
                    graded_data=graded_data,
                    assessment_id=assessment_id,
                    student_id=sub["student_id"],
                    cost_summary={"total_cost": graded.cost, "input_tokens": 0, "output_tokens": 0}
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
