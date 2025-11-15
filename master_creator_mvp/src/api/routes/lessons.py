"""
Lessons API Routes

Endpoints for lesson and unit plan generation (Engine 0, 1).
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging

from ...engines.engine_0_unit_planner import UnitPlanDesigner
from ...engines.engine_1_lesson_architect import LessonArchitect
from ...content_storage.interface import ContentStorageInterface

logger = logging.getLogger("api.lessons")

router = APIRouter()


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class UnitPlanRequest(BaseModel):
    """Request to generate unit plan."""

    unit_title: str
    grade_level: str
    subject: str
    num_lessons: int
    standards: Optional[List[str]] = None
    class_id: Optional[str] = None


class LessonRequest(BaseModel):
    """Request to generate lesson."""

    topic: str
    grade_level: str
    subject: str
    duration_minutes: int = 45
    standards: Optional[List[str]] = None
    class_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post("/units")
async def generate_unit_plan(request: UnitPlanRequest):
    """
    Generate multi-lesson unit plan using UbD framework.

    POST /api/lessons/units

    Request body:
    {
        "unit_title": "Ecosystems and Biodiversity",
        "grade_level": "9",
        "subject": "Science",
        "num_lessons": 8,
        "standards": ["NGSS-HS-LS2-1"],
        "class_id": "class_bio_101"
    }

    Returns:
        Complete unit plan with lessons, assessments, and resources
    """
    try:
        logger.info(f"Generating unit plan: {request.unit_title}")

        engine = UnitPlanDesigner()
        unit_plan = engine.generate(
            unit_title=request.unit_title,
            grade_level=request.grade_level,
            subject=request.subject,
            num_lessons=request.num_lessons,
            standards=request.standards,
            class_id=request.class_id,
        )

        cost_summary = engine.get_cost_summary()

        # Save to database
        with ContentStorageInterface() as storage:
            storage.save_unit_plan(
                unit_data=unit_plan.model_dump(),
                cost_summary=cost_summary,
                class_id=request.class_id
            )

        logger.info(f"Unit plan generated: {unit_plan.unit_id} | Cost: ${cost_summary['total_cost']:.4f}")

        return {
            "status": "success",
            "unit_plan": unit_plan.model_dump(),
            "cost": cost_summary,
        }

    except Exception as e:
        logger.error(f"Error generating unit plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lessons")
async def generate_lesson(request: LessonRequest):
    """
    Generate 10-part lesson blueprint.

    POST /api/lessons/lessons

    Request body:
    {
        "topic": "Photosynthesis Process",
        "grade_level": "9",
        "subject": "Science",
        "duration_minutes": 45,
        "standards": ["NGSS-HS-LS1-5"],
        "class_id": "class_bio_101"
    }

    Returns:
        Complete lesson blueprint with 10 sections
    """
    try:
        logger.info(f"Generating lesson: {request.topic}")

        engine = LessonArchitect()
        lesson = engine.generate(
            topic=request.topic,
            grade_level=request.grade_level,
            subject=request.subject,
            duration_minutes=request.duration_minutes,
            standards=request.standards,
            class_id=request.class_id,
        )

        cost_summary = engine.get_cost_summary()

        # Save to database
        with ContentStorageInterface() as storage:
            storage.save_lesson(
                lesson_data=lesson.model_dump(),
                cost_summary=cost_summary,
                class_id=request.class_id
            )

        logger.info(f"Lesson generated: {lesson.lesson_id} | Cost: ${cost_summary['total_cost']:.4f}")

        return {
            "status": "success",
            "lesson": lesson.model_dump(),
            "cost": cost_summary,
        }

    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """
    Get lesson by ID.

    GET /api/lessons/lessons/{lesson_id}

    Returns:
        Lesson blueprint if found
    """
    try:
        with ContentStorageInterface() as storage:
            lesson_data = storage.get_lesson(lesson_id)

        if not lesson_data:
            raise HTTPException(
                status_code=404,
                detail=f"Lesson not found: {lesson_id}"
            )

        return {
            "status": "success",
            "lesson": lesson_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lesson: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/units/{unit_id}")
async def get_unit(unit_id: str):
    """
    Get unit plan by ID.

    GET /api/lessons/units/{unit_id}

    Returns:
        Unit plan if found
    """
    try:
        with ContentStorageInterface() as storage:
            unit_data = storage.get_unit_plan(unit_id)

        if not unit_data:
            raise HTTPException(
                status_code=404,
                detail=f"Unit plan not found: {unit_id}"
            )

        return {
            "status": "success",
            "unit_plan": unit_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving unit plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
