"""
Adaptive API Routes

Endpoints for adaptive personalization (Engine 4) and feedback loop (Engine 6).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from ...engines.engine_4_adaptive import AdaptiveEngine
from ...engines.engine_6_feedback import FeedbackLoop
from ...content_storage.interface import ContentStorageInterface

logger = logging.getLogger("api.adaptive")

router = APIRouter()


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class AdaptivePlanRequest(BaseModel):
    """Request to generate adaptive plan."""

    class_id: str
    concept_ids: List[str]


class FeedbackRequest(BaseModel):
    """Request to generate feedback report."""

    engine_name: str = "engine_5_diagnostic"
    timeframe_days: int = 30


# ═══════════════════════════════════════════════════════════
# ADAPTIVE ENDPOINTS (Engine 4)
# ═══════════════════════════════════════════════════════════


@router.post("/plan")
async def generate_adaptive_plan(request: AdaptivePlanRequest):
    """
    Generate class-wide adaptive learning plan.

    POST /api/adaptive/plan

    Request body:
    {
        "class_id": "class_bio_101",
        "concept_ids": ["photosynthesis_process", "cellular_respiration"]
    }

    Returns:
        Adaptive plan with groupings and personalized paths
    """
    try:
        logger.info(f"Generating adaptive plan for class {request.class_id}")

        engine = AdaptiveEngine()
        plan = engine.generate_class_plan(
            class_id=request.class_id,
            concept_ids=request.concept_ids,
        )

        cost_summary = engine.get_cost_summary()

        # Save to database
        plan_data = plan.model_dump()
        with ContentStorageInterface() as storage:
            # Save for each student in the plan
            for student_path in plan_data.get("student_paths", []):
                storage.save_adaptive_plan(
                    plan_data=plan_data,
                    student_id=student_path.get("student_id"),
                    cost_summary=cost_summary
                )

        logger.info(f"Adaptive plan generated: {plan.plan_id} | Cost: ${cost_summary['total_cost']:.4f}")

        return {
            "status": "success",
            "adaptive_plan": plan.model_dump(),
            "cost": cost_summary,
        }

    except Exception as e:
        logger.error(f"Error generating adaptive plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/students/{student_id}/path")
async def generate_student_path(student_id: str, concept_ids: List[str]):
    """
    Generate personalized learning path for one student.

    POST /api/adaptive/students/{student_id}/path

    Request body:
    {
        "concept_ids": ["photosynthesis_process", "cellular_respiration"]
    }

    Returns:
        Personalized learning path with ZPD recommendations
    """
    try:
        logger.info(f"Generating learning path for student {student_id}")

        engine = AdaptiveEngine()
        path = engine.generate_student_path(
            student_id=student_id,
            concept_ids=concept_ids,
        )

        logger.info(f"Learning path generated: {path.path_id}")

        return {
            "status": "success",
            "learning_path": path.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}")
async def get_adaptive_plan(plan_id: str):
    """
    Get adaptive plan by ID.

    GET /api/adaptive/plans/{plan_id}

    Returns:
        Adaptive plan if found
    """
    try:
        with ContentStorageInterface() as storage:
            plan_data = storage.get_adaptive_plan(plan_id)

        if not plan_data:
            raise HTTPException(
                status_code=404,
                detail=f"Adaptive plan not found: {plan_id}"
            )

        return {
            "status": "success",
            "adaptive_plan": plan_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving adaptive plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# FEEDBACK ENDPOINTS (Engine 6)
# ═══════════════════════════════════════════════════════════


@router.post("/feedback")
async def generate_feedback_report(request: FeedbackRequest):
    """
    Generate feedback report for engine performance.

    POST /api/adaptive/feedback

    Request body:
    {
        "engine_name": "engine_5_diagnostic",
        "timeframe_days": 30
    }

    Returns:
        Feedback report with accuracy metrics and parameter recommendations
    """
    try:
        logger.info(f"Generating feedback for {request.engine_name}")

        engine = FeedbackLoop()
        report = engine.generate_feedback(
            engine_name=request.engine_name,
            timeframe_days=request.timeframe_days,
        )

        # Save to database
        report_data = report.model_dump()
        with ContentStorageInterface() as storage:
            storage.save_feedback_report(
                report_data=report_data,
                cost_summary={"total_cost": report_data.get("total_cost", 0.0), "input_tokens": 0, "output_tokens": 0}
            )

        logger.info(
            f"Feedback generated: {report.feedback_id} | "
            f"Quality: {report.quality_assessment} | "
            f"RMSE: {report.accuracy_metrics.rmse:.3f}"
        )

        return {
            "status": "success",
            "feedback_report": report.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/{feedback_id}")
async def get_feedback_report(feedback_id: str):
    """
    Get feedback report by ID.

    GET /api/adaptive/feedback/{feedback_id}

    Returns:
        Feedback report if found
    """
    try:
        with ContentStorageInterface() as storage:
            report_data = storage.get_feedback_report(feedback_id)

        if not report_data:
            raise HTTPException(
                status_code=404,
                detail=f"Feedback report not found: {feedback_id}"
            )

        return {
            "status": "success",
            "feedback_report": report_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feedback report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/engine/{engine_name}/latest")
async def get_latest_feedback(engine_name: str):
    """
    Get latest feedback report for an engine.

    GET /api/adaptive/feedback/engine/{engine_name}/latest

    Returns:
        Most recent feedback report
    """
    try:
        # For MVP, return a placeholder indicating this needs Student Model query
        return {
            "status": "success",
            "message": "Latest feedback retrieval requires complex query - use feedback_id endpoint for now",
            "suggestion": "Generate new feedback report using POST /api/adaptive/feedback"
        }

    except Exception as e:
        logger.error(f"Error retrieving latest feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
