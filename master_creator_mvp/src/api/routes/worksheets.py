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
    # TODO: Implement worksheet retrieval from database
    raise HTTPException(status_code=501, detail="Worksheet retrieval not yet implemented")


@router.get("/{worksheet_id}/compliance-report")
async def get_compliance_report(worksheet_id: str):
    """
    Get FERPA compliance report for worksheet.

    GET /api/worksheets/{worksheet_id}/compliance-report

    Returns:
        Compliance report showing all IEP accommodations applied
    """
    # TODO: Implement compliance report generation
    raise HTTPException(status_code=501, detail="Compliance report not yet implemented")
