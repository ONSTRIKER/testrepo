"""
Pipeline API Routes

Endpoints for full pipeline orchestration.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import asyncio

from ...orchestration.langgraph_pipeline import run_async_pipeline, run_sync_pipeline
from ...orchestration.pipeline import run_pipeline

logger = logging.getLogger("api.pipeline")

router = APIRouter()

# Store for async pipeline results (in production, use Redis/database)
pipeline_results = {}


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class PipelineRequest(BaseModel):
    """Request to run complete pipeline."""

    lesson_topic: str
    grade_level: str
    subject: str
    class_id: str
    concept_ids: List[str]
    duration_minutes: int = 45
    standards: Optional[List[str]] = None

    # Optional engines
    generate_unit: bool = False
    num_lessons_in_unit: Optional[int] = None
    generate_adaptive_plan: bool = False
    run_feedback_loop: bool = False

    # Execution mode
    use_langgraph: bool = False  # If True, use LangGraph async pipeline
    run_async: bool = False  # If True, run in background


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post("/run")
async def run_complete_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """
    Run complete lesson generation pipeline.

    POST /api/pipeline/run

    Request body:
    {
        "lesson_topic": "Photosynthesis",
        "grade_level": "9",
        "subject": "Science",
        "class_id": "class_bio_101",
        "concept_ids": ["photosynthesis_process"],
        "duration_minutes": 45,
        "standards": ["NGSS-HS-LS1-5"],
        "generate_unit": false,
        "generate_adaptive_plan": true,
        "run_feedback_loop": false,
        "use_langgraph": true,
        "run_async": false
    }

    Returns:
        Complete pipeline results with lesson, diagnostic, worksheets, and IEP modifications
    """
    try:
        logger.info(f"Running pipeline: {request.lesson_topic} | LangGraph: {request.use_langgraph} | Async: {request.run_async}")

        if request.run_async:
            # Run in background
            pipeline_id = f"pipeline_{len(pipeline_results)}"

            async def run_background_pipeline():
                if request.use_langgraph:
                    result = await run_async_pipeline(
                        lesson_topic=request.lesson_topic,
                        grade_level=request.grade_level,
                        subject=request.subject,
                        class_id=request.class_id,
                        concept_ids=request.concept_ids,
                        duration_minutes=request.duration_minutes,
                        standards=request.standards,
                        generate_unit=request.generate_unit,
                        num_lessons_in_unit=request.num_lessons_in_unit,
                        generate_adaptive_plan=request.generate_adaptive_plan,
                        run_feedback_loop=request.run_feedback_loop,
                    )
                else:
                    result = run_pipeline(
                        lesson_topic=request.lesson_topic,
                        grade_level=request.grade_level,
                        subject=request.subject,
                        class_id=request.class_id,
                        concept_ids=request.concept_ids,
                        duration_minutes=request.duration_minutes,
                        standards=request.standards,
                    )

                pipeline_results[pipeline_id] = result

            background_tasks.add_task(run_background_pipeline)

            return {
                "status": "processing",
                "pipeline_id": pipeline_id,
                "message": "Pipeline running in background. Use GET /api/pipeline/status/{pipeline_id} to check progress."
            }

        else:
            # Run synchronously
            if request.use_langgraph:
                # Use LangGraph async pipeline
                result = await run_async_pipeline(
                    lesson_topic=request.lesson_topic,
                    grade_level=request.grade_level,
                    subject=request.subject,
                    class_id=request.class_id,
                    concept_ids=request.concept_ids,
                    duration_minutes=request.duration_minutes,
                    standards=request.standards,
                    generate_unit=request.generate_unit,
                    num_lessons_in_unit=request.num_lessons_in_unit,
                    generate_adaptive_plan=request.generate_adaptive_plan,
                    run_feedback_loop=request.run_feedback_loop,
                )

                logger.info(f"LangGraph pipeline complete: {result['pipeline_id']} | Status: {result['execution_status']}")

                return {
                    "status": "success",
                    "pipeline_result": result,
                }

            else:
                # Use synchronous pipeline
                result = run_pipeline(
                    lesson_topic=request.lesson_topic,
                    grade_level=request.grade_level,
                    subject=request.subject,
                    class_id=request.class_id,
                    concept_ids=request.concept_ids,
                    duration_minutes=request.duration_minutes,
                    standards=request.standards,
                )

                logger.info(f"Pipeline complete: {result.pipeline_id} | Status: {result.status}")

                return {
                    "status": "success",
                    "pipeline_result": result.model_dump(),
                }

    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """
    Get status of async pipeline.

    GET /api/pipeline/status/{pipeline_id}

    Returns:
        Pipeline status and results if complete
    """
    if pipeline_id not in pipeline_results:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")

    result = pipeline_results[pipeline_id]

    # Check if LangGraph result (dict) or synchronous result (object)
    if isinstance(result, dict):
        status = result.get("execution_status", "completed")
    else:
        status = result.status

    return {
        "status": status,
        "pipeline_id": pipeline_id,
        "result": result if isinstance(result, dict) else result.model_dump(),
    }


@router.post("/run-core")
async def run_core_pipeline(request: PipelineRequest):
    """
    Run core pipeline only (Lesson → Diagnostic → Worksheets → IEP).

    POST /api/pipeline/run-core

    Faster endpoint that skips optional engines (Unit Plan, Adaptive, Feedback).

    Returns:
        Core pipeline results
    """
    try:
        logger.info(f"Running core pipeline: {request.lesson_topic}")

        # Always use sync pipeline for core-only
        result = run_pipeline(
            lesson_topic=request.lesson_topic,
            grade_level=request.grade_level,
            subject=request.subject,
            class_id=request.class_id,
            concept_ids=request.concept_ids,
            duration_minutes=request.duration_minutes,
            standards=request.standards,
        )

        logger.info(f"Core pipeline complete: {result.pipeline_id}")

        return {
            "status": "success",
            "pipeline_result": result.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error running core pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{pipeline_id}")
async def get_pipeline_results(pipeline_id: str):
    """
    Get complete pipeline results by ID.

    GET /api/pipeline/results/{pipeline_id}

    Returns:
        Full pipeline results if found
    """
    # TODO: Implement pipeline retrieval from database
    raise HTTPException(status_code=501, detail="Pipeline retrieval not yet implemented")
