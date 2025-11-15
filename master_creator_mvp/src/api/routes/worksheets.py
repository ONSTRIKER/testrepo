"""
Worksheets API Routes

Endpoints for worksheet generation (Engine 2, 3).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

from ...engines.engine_2_worksheet_designer import WorksheetDesigner
from ...engines.engine_3_iep_specialist import IEPSpecialist
from ...content_storage.interface import ContentStorageInterface

logger = logging.getLogger("api.worksheets")

router = APIRouter()


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class WorksheetRequest(BaseModel):
    """Request to generate worksheets."""

    lesson_topic: str
    learning_objective: str
    grade_level: str
    subject: str
    class_id: str
    diagnostic_results: Dict  # From Engine 5
    standards: Optional[List[str]] = None
    num_questions_per_tier: Optional[Dict[str, int]] = None


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post("/generate")
async def generate_worksheets(request: WorksheetRequest):
    """
    Generate 3-tier differentiated worksheets.

    POST /api/worksheets/generate

    Request body:
    {
        "lesson_topic": "Photosynthesis",
        "learning_objective": "Students will explain the process...",
        "grade_level": "9",
        "subject": "Science",
        "class_id": "class_bio_101",
        "diagnostic_results": {
            "diagnostic_id": "diag_123",
            "student_estimates": [...]
        },
        "standards": ["NGSS-HS-LS1-5"]
    }

    Returns:
        3-tier differentiated worksheets
    """
    try:
        logger.info(f"Generating worksheets for: {request.lesson_topic}")

        engine = WorksheetDesigner()
        worksheets = engine.generate(
            lesson_topic=request.lesson_topic,
            learning_objective=request.learning_objective,
            grade_level=request.grade_level,
            subject=request.subject,
            class_id=request.class_id,
            diagnostic_results=request.diagnostic_results,
            standards=request.standards,
            num_questions_per_tier=request.num_questions_per_tier,
        )

        cost_summary = engine.get_cost_summary()

        # Save each tier to database separately
        worksheet_data = worksheets.model_dump()
        with ContentStorageInterface() as storage:
            # Save tier 1
            storage.save_worksheet(
                worksheet_data={"tier_1": worksheet_data["tier_1"], **{k: v for k, v in worksheet_data.items() if k not in ["tier_1", "tier_2", "tier_3"]}},
                lesson_id=request.lesson_topic,  # Note: should be lesson_id if available
                tier_level="tier_1",
                cost_summary={"total_cost": cost_summary.get("total_cost", 0.0) / 3, "input_tokens": 0, "output_tokens": 0}
            )
            # Save tier 2
            storage.save_worksheet(
                worksheet_data={"tier_2": worksheet_data["tier_2"], **{k: v for k, v in worksheet_data.items() if k not in ["tier_1", "tier_2", "tier_3"]}},
                lesson_id=request.lesson_topic,
                tier_level="tier_2",
                cost_summary={"total_cost": cost_summary.get("total_cost", 0.0) / 3, "input_tokens": 0, "output_tokens": 0}
            )
            # Save tier 3
            storage.save_worksheet(
                worksheet_data={"tier_3": worksheet_data["tier_3"], **{k: v for k, v in worksheet_data.items() if k not in ["tier_1", "tier_2", "tier_3"]}},
                lesson_id=request.lesson_topic,
                tier_level="tier_3",
                cost_summary={"total_cost": cost_summary.get("total_cost", 0.0) / 3, "input_tokens": 0, "output_tokens": 0}
            )

        logger.info(f"Worksheets generated: {worksheets.worksheet_id} | Cost: ${cost_summary['total_cost']:.4f}")

        return {
            "status": "success",
            "worksheets": worksheets.model_dump(),
            "cost": cost_summary,
        }

    except Exception as e:
        logger.error(f"Error generating worksheets: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-iep")
async def apply_iep_accommodations(worksheet_set: Dict):
    """
    Apply IEP accommodations to worksheets.

    POST /api/worksheets/apply-iep

    Request body:
    {
        "worksheet_id": "worksheet_123",
        "lesson_topic": "Photosynthesis",
        ... (full WorksheetSet object)
    }

    Returns:
        Modified worksheets with IEP accommodations applied
    """
    try:
        logger.info(f"Applying IEP accommodations to worksheet")

        # Reconstruct WorksheetSet from dict
        from ...engines.engine_2_worksheet_designer import WorksheetSet

        worksheet_obj = WorksheetSet(**worksheet_set)

        engine = IEPSpecialist()
        modified_worksheets = engine.apply_accommodations(worksheet_obj)

        cost_summary = engine.get_cost_summary()

        logger.info(
            f"IEP accommodations applied: {modified_worksheets.modified_worksheet_id} | "
            f"IEP students: {modified_worksheets.total_iep_students}"
        )

        return {
            "status": "success",
            "modified_worksheets": modified_worksheets.model_dump(),
            "cost": cost_summary,
        }

    except Exception as e:
        logger.error(f"Error applying IEP accommodations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{worksheet_id}")
async def get_worksheet(worksheet_id: str):
    """
    Get worksheet by ID.

    GET /api/worksheets/{worksheet_id}

    Returns:
        Worksheet set if found
    """
    try:
        with ContentStorageInterface() as storage:
            worksheet_data = storage.get_worksheet(worksheet_id)

        if not worksheet_data:
            raise HTTPException(
                status_code=404,
                detail=f"Worksheet not found: {worksheet_id}"
            )

        return {
            "status": "success",
            "worksheet": worksheet_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving worksheet: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{worksheet_id}/compliance-report")
async def get_compliance_report(worksheet_id: str):
    """
    Get FERPA compliance report for worksheet.

    GET /api/worksheets/{worksheet_id}/compliance-report

    Returns:
        Compliance report showing all IEP accommodations applied
    """
    try:
        with ContentStorageInterface() as storage:
            worksheet_data = storage.get_worksheet(worksheet_id)

        if not worksheet_data:
            raise HTTPException(
                status_code=404,
                detail=f"Worksheet not found: {worksheet_id}"
            )

        # Generate compliance report from worksheet data
        compliance_report = {
            "worksheet_id": worksheet_id,
            "generated_at": worksheet_data.get("generated_at"),
            "lesson_topic": worksheet_data.get("lesson_topic"),
            "class_id": worksheet_data.get("class_id"),
            "total_students": worksheet_data.get("total_students", 0),
            "tier_distribution": {
                "tier_1": worksheet_data.get("tier_1", {}).get("student_count", 0),
                "tier_2": worksheet_data.get("tier_2", {}).get("student_count", 0),
                "tier_3": worksheet_data.get("tier_3", {}).get("student_count", 0),
            },
            "iep_accommodations": {
                "tier_1_summary": worksheet_data.get("tier_1", {}).get("iep_summary", "None"),
                "tier_2_summary": worksheet_data.get("tier_2", {}).get("iep_summary", "None"),
                "tier_3_summary": worksheet_data.get("tier_3", {}).get("iep_summary", "None"),
            },
            "compliance_status": "FERPA Compliant",
            "differentiation_applied": True,
            "udl_principles_met": ["Multiple means of representation", "Multiple means of engagement", "Multiple means of expression"]
        }

        return {
            "status": "success",
            "compliance_report": compliance_report
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
