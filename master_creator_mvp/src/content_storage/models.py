"""
Content Storage Models

Database models for storing generated educational content from all 9 engines:
- Unit Plans (Engine 0)
- Lesson Blueprints (Engine 1)
- Worksheets (Engine 2)
- IEP Modifications (Engine 3)
- Adaptive Plans (Engine 4)
- Diagnostic Results (Engine 5)
- Feedback Reports (Engine 6)
- Assessment Grading (Grader)

All engines save their outputs to these tables for retrieval and archival.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Reuse Base from student model
from ..student_model.database import Base

# ═══════════════════════════════════════════════════════════
# GENERATED CONTENT MODELS
# ═══════════════════════════════════════════════════════════


class UnitPlanModel(Base):
    """Stores generated unit plans from Engine 0."""

    __tablename__ = "unit_plans"

    unit_id = Column(String(50), primary_key=True, index=True)
    unit_title = Column(String(200), nullable=False)
    grade_level = Column(String(10), nullable=False)
    subject = Column(String(50), nullable=False)

    # Generated content (stored as JSON)
    content = Column(JSON, nullable=False)  # Full UnitPlan Pydantic model dump

    # Metadata
    num_lessons = Column(Integer, nullable=False)
    standards = Column(JSON, default=list)  # List of standard codes
    class_id = Column(String(50), nullable=True, index=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons = relationship("LessonModel", back_populates="unit", cascade="all, delete-orphan")


class LessonModel(Base):
    """Stores generated lesson blueprints from Engine 1."""

    __tablename__ = "lessons"

    lesson_id = Column(String(50), primary_key=True, index=True)
    topic = Column(String(200), nullable=False, index=True)
    grade_level = Column(String(10), nullable=False)
    subject = Column(String(50), nullable=False, index=True)

    # Unit relationship
    unit_id = Column(String(50), ForeignKey("unit_plans.unit_id"), nullable=True, index=True)
    lesson_number = Column(Integer, nullable=True)

    # Generated content (stored as JSON)
    content = Column(JSON, nullable=False)  # Full LessonBlueprint Pydantic model dump

    # Metadata
    duration_minutes = Column(Integer, nullable=False)
    standards = Column(JSON, default=list)
    class_id = Column(String(50), nullable=True, index=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    unit = relationship("UnitPlanModel", back_populates="lessons")
    worksheets = relationship("WorksheetModel", back_populates="lesson", cascade="all, delete-orphan")


class WorksheetModel(Base):
    """Stores generated worksheets from Engine 2 (3-tier differentiation)."""

    __tablename__ = "worksheets"

    worksheet_id = Column(String(50), primary_key=True, index=True)
    lesson_id = Column(String(50), ForeignKey("lessons.lesson_id"), nullable=False, index=True)

    # Worksheet metadata
    tier_level = Column(String(20), nullable=False, index=True)  # "tier_1", "tier_2", "tier_3"
    worksheet_type = Column(String(50), nullable=False)  # "practice", "assessment", "homework"

    # Generated content (stored as JSON)
    content = Column(JSON, nullable=False)  # Full Worksheet Pydantic model dump

    # Metadata
    num_questions = Column(Integer, nullable=False)
    estimated_duration = Column(Integer, nullable=True)  # minutes

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    lesson = relationship("LessonModel", back_populates="worksheets")


class IEPModificationModel(Base):
    """Stores IEP modifications from Engine 3."""

    __tablename__ = "iep_modifications"

    modification_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    lesson_id = Column(String(50), nullable=True, index=True)
    worksheet_id = Column(String(50), nullable=True, index=True)

    # Modification content
    content = Column(JSON, nullable=False)  # Full IEPModification Pydantic model dump

    # Metadata
    disability_category = Column(String(50), nullable=False)
    accommodations_applied = Column(JSON, default=list)

    # Compliance
    legal_compliant = Column(Boolean, default=True)
    compliance_report = Column(JSON, nullable=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AdaptivePlanModel(Base):
    """Stores adaptive learning plans from Engine 4."""

    __tablename__ = "adaptive_plans"

    plan_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    lesson_id = Column(String(50), nullable=True, index=True)

    # Adaptive plan content
    content = Column(JSON, nullable=False)  # Full AdaptivePlan Pydantic model dump

    # Metadata
    assigned_tier = Column(String(20), nullable=False)
    personalization_level = Column(String(20), nullable=False)  # "low", "medium", "high"

    # Performance predictions
    predicted_mastery = Column(Float, nullable=True)
    predicted_score = Column(Float, nullable=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiagnosticResultModel(Base):
    """Stores diagnostic results from Engine 5 (BKT analysis)."""

    __tablename__ = "diagnostic_results"

    diagnostic_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    assessment_id = Column(String(50), nullable=True, index=True)

    # Diagnostic content
    content = Column(JSON, nullable=False)  # Full DiagnosticResult Pydantic model dump

    # BKT analysis summary
    overall_mastery = Column(Float, nullable=False)  # Average across concepts
    concepts_analyzed = Column(JSON, default=list)
    recommended_tier = Column(String(20), nullable=False)

    # Cost tracking
    total_cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FeedbackReportModel(Base):
    """Stores feedback reports from Engine 6."""

    __tablename__ = "feedback_reports"

    report_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), nullable=True, index=True)
    class_id = Column(String(50), nullable=True, index=True)

    # Feedback content
    content = Column(JSON, nullable=False)  # Full FeedbackReport Pydantic model dump

    # Accuracy metrics
    prediction_accuracy = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    rmse = Column(Float, nullable=True)  # Root Mean Squared Error

    # BKT parameter updates
    bkt_updates_applied = Column(Boolean, default=False)

    # Cost tracking
    total_cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class GradedAssessmentModel(Base):
    """Stores graded assessment results from the Assessment Grader."""

    __tablename__ = "graded_assessments"

    graded_id = Column(String(50), primary_key=True, index=True)
    assessment_id = Column(String(50), nullable=False, index=True)
    student_id = Column(String(50), nullable=False, index=True)

    # Grading results
    content = Column(JSON, nullable=False)  # Full GradedAssessment Pydantic model dump

    # Scores
    raw_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False, index=True)

    # Analysis
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    # Cost tracking
    total_cost = Column(Float, default=0.0)

    # Timestamps
    graded_at = Column(DateTime, default=datetime.utcnow, index=True)


class PipelineExecutionModel(Base):
    """Stores pipeline execution metadata and results."""

    __tablename__ = "pipeline_executions"

    job_id = Column(String(50), primary_key=True, index=True)
    pipeline_type = Column(String(50), nullable=False)  # "full_9_engine", "lesson_only", etc.

    # Status tracking
    status = Column(String(20), nullable=False, index=True)  # "running", "complete", "failed"
    current_stage = Column(String(50), nullable=True)
    completed_stages = Column(JSON, default=list)

    # Content IDs
    unit_id = Column(String(50), nullable=True)
    lesson_id = Column(String(50), nullable=True)
    worksheet_ids = Column(JSON, default=list)

    # Execution metadata
    total_cost = Column(Float, default=0.0)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Error tracking
    errors = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_content_tables(engine):
    """Create all content storage tables."""
    Base.metadata.create_all(bind=engine, tables=[
        UnitPlanModel.__table__,
        LessonModel.__table__,
        WorksheetModel.__table__,
        IEPModificationModel.__table__,
        AdaptivePlanModel.__table__,
        DiagnosticResultModel.__table__,
        FeedbackReportModel.__table__,
        GradedAssessmentModel.__table__,
        PipelineExecutionModel.__table__,
    ])
    print("✅ All content storage tables created successfully!")
