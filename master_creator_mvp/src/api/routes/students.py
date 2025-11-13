"""
Students API Routes

Endpoints for student management and Student Model operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import io
import csv

from ...student_model.interface import StudentModelInterface
from ...student_model.schemas import (
    StudentProfile,
    StudentProfileCreate,
    IEPData,
    IEPAccommodationUpdate,
    ConceptMastery,
)

logger = logging.getLogger("api.students")

router = APIRouter()

# Shared Student Model instance
student_model = StudentModelInterface()


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class CreateStudentRequest(BaseModel):
    """Request to create student."""

    student_name: str
    grade_level: str
    has_iep: bool = False
    accommodations: Optional[List[str]] = None
    primary_disability: Optional[str] = None
    reading_level: Optional[str] = None


class UpdateIEPRequest(BaseModel):
    """Request to update IEP."""

    accommodations: List[Dict[str, str]]
    primary_disability: Optional[str] = None
    review_date: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.get("/classes/{class_id}/roster")
async def get_class_roster(class_id: str):
    """
    Get class roster.

    GET /api/students/classes/{class_id}/roster

    Returns:
        Class roster with total students and class name
    """
    try:
        roster = student_model.get_class_roster(class_id)

        return {
            "status": "success",
            "roster": roster.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error getting roster: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes/{class_id}/students")
async def get_class_students(class_id: str):
    """
    Get all students in a class.

    GET /api/students/classes/{class_id}/students

    Returns:
        List of student profiles
    """
    try:
        students = student_model.get_class_students(class_id)

        return {
            "status": "success",
            "students": [s.model_dump() for s in students],
            "count": len(students),
        }

    except Exception as e:
        logger.error(f"Error getting students: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}")
async def get_student_profile(student_id: str):
    """
    Get student profile by ID.

    GET /api/students/students/{student_id}

    Returns:
        Student profile
    """
    try:
        profile = student_model.get_student_profile(student_id)

        if not profile:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

        return {
            "status": "success",
            "student": profile.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/students")
async def create_student(request: CreateStudentRequest):
    """
    Create new student profile.

    POST /api/students/students

    Request body:
    {
        "student_name": "Alex Chen",
        "grade_level": "9",
        "has_iep": false,
        "reading_level": "grade_level"
    }

    Returns:
        Created student profile
    """
    try:
        from ...student_model.schemas import GradeLevel, ReadingLevel

        # Convert to StudentProfileCreate
        profile_data = StudentProfileCreate(
            student_name=request.student_name,
            grade_level=GradeLevel(request.grade_level),
            has_iep=request.has_iep,
            reading_level=ReadingLevel(request.reading_level) if request.reading_level else None,
        )

        profile = student_model.create_student_profile(profile_data)

        logger.info(f"Student created: {profile.student_id}")

        return {
            "status": "success",
            "student": profile.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error creating student: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classes/{class_id}/bulk-import")
async def bulk_import_students(class_id: str, file: UploadFile = File(...)):
    """
    Bulk import students from CSV.

    POST /api/students/classes/{class_id}/bulk-import

    CSV format:
    student_name,grade_level,has_iep,reading_level
    Alex Chen,9,false,grade_level
    Maria Gonzalez,9,true,below_grade_level

    Returns:
        Import results with success/failure counts
    """
    try:
        # Read CSV file
        contents = await file.read()
        csv_text = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_text))

        result = student_model.bulk_import_students(
            csv_data=csv_text,
            class_id=class_id,
        )

        logger.info(
            f"Bulk import complete: {result.successful_imports} successful, "
            f"{result.failed_imports} failed"
        )

        return {
            "status": "success" if result.failed_imports == 0 else "partial_success",
            "result": result.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error bulk importing students: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/mastery")
async def get_student_mastery(student_id: str, concept_ids: Optional[str] = None):
    """
    Get student mastery data.

    GET /api/students/students/{student_id}/mastery?concept_ids=photo,cellular

    Query params:
        concept_ids: Comma-separated concept IDs (optional, returns all if not specified)

    Returns:
        List of concept mastery records
    """
    try:
        # Parse concept_ids
        concept_list = concept_ids.split(",") if concept_ids else None

        mastery_records = student_model.retrieve_concept_mastery(
            student_id=student_id,
            concept_ids=concept_list,
        )

        return {
            "status": "success",
            "mastery": [m.model_dump() for m in mastery_records],
            "count": len(mastery_records),
        }

    except Exception as e:
        logger.error(f"Error getting mastery: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/iep")
async def get_student_iep(student_id: str):
    """
    Get student IEP accommodations.

    GET /api/students/students/{student_id}/iep

    Returns:
        IEP data if student has IEP
    """
    try:
        iep_data = student_model.get_iep_accommodations(student_id)

        if not iep_data:
            raise HTTPException(status_code=404, detail=f"No IEP found for student {student_id}")

        return {
            "status": "success",
            "iep": iep_data.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting IEP: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/students/{student_id}/iep")
async def update_student_iep(student_id: str, request: UpdateIEPRequest):
    """
    Update student IEP accommodations.

    PUT /api/students/students/{student_id}/iep

    Request body:
    {
        "accommodations": [
            {"type": "Extended Time", "details": "1.5x on all assessments"}
        ],
        "primary_disability": "Learning Disability",
        "review_date": "2025-05-15"
    }

    Returns:
        Updated IEP data
    """
    try:
        from ...student_model.schemas import DisabilityCategory

        # Convert to IEPAccommodationUpdate
        update_data = IEPAccommodationUpdate(
            accommodations=request.accommodations,
            primary_disability=DisabilityCategory(request.primary_disability) if request.primary_disability else None,
            review_date=request.review_date,
        )

        iep_data = student_model.update_iep_accommodations(student_id, update_data)

        logger.info(f"IEP updated for student {student_id}")

        return {
            "status": "success",
            "iep": iep_data.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error updating IEP: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes/{class_id}/iep-students")
async def get_iep_students(class_id: str):
    """
    Get all students with IEPs in a class.

    GET /api/students/classes/{class_id}/iep-students

    Returns:
        List of students with IEPs
    """
    try:
        students = student_model.get_students_with_ieps(class_id)

        return {
            "status": "success",
            "students": [s.model_dump() for s in students],
            "count": len(students),
        }

    except Exception as e:
        logger.error(f"Error getting IEP students: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes/{class_id}/mastery/{concept_id}")
async def get_class_mastery_distribution(class_id: str, concept_id: str):
    """
    Get class-wide mastery distribution for a concept.

    GET /api/students/classes/{class_id}/mastery/{concept_id}

    Returns:
        Mastery distribution with average, tiers, etc.
    """
    try:
        distribution = student_model.get_class_mastery_distribution(
            class_id=class_id,
            concept_id=concept_id,
        )

        return {
            "status": "success",
            "distribution": distribution.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error getting mastery distribution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
