"""
Content Storage Interface

Unified interface for saving and retrieving generated educational content.
All engines should use this interface to persist their outputs.

Usage:
    with ContentStorageInterface() as storage:
        lesson_id = storage.save_lesson(lesson_data, cost_summary)
        lesson = storage.get_lesson(lesson_id)
"""

from typing import Dict, Optional, List
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from ..student_model.database import get_session_maker
from .models import (
    UnitPlanModel,
    LessonModel,
    WorksheetModel,
    IEPModificationModel,
    AdaptivePlanModel,
    DiagnosticResultModel,
    FeedbackReportModel,
    GradedAssessmentModel,
    PipelineExecutionModel,
)

logger = logging.getLogger("content_storage")


class ContentStorageInterface:
    """
    Context manager interface for content storage operations.

    Provides methods for:
    - Saving generated content from all engines
    - Retrieving content by ID
    - Querying content by filters
    - Managing pipeline execution state
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize interface with database session.

        Args:
            session: SQLAlchemy session (creates new one if None)
        """
        self.session = session
        self._should_close = session is None

    def __enter__(self):
        """Context manager entry - create session if needed."""
        if self.session is None:
            SessionMaker = get_session_maker()
            self.session = SessionMaker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session if we created it."""
        if self._should_close and self.session:
            self.session.close()

    # ═══════════════════════════════════════════════════════════
    # UNIT PLANS (Engine 0)
    # ═══════════════════════════════════════════════════════════

    def save_unit_plan(
        self,
        unit_data: Dict,
        cost_summary: Dict,
        class_id: Optional[str] = None
    ) -> str:
        """
        Save generated unit plan to database.

        Args:
            unit_data: Full unit plan data (from Pydantic model dump)
            cost_summary: Cost tracking dict {total_cost, input_tokens, output_tokens}
            class_id: Optional class ID

        Returns:
            unit_id of saved unit plan
        """
        unit = UnitPlanModel(
            unit_id=unit_data["unit_id"],
            unit_title=unit_data["unit_title"],
            grade_level=unit_data["grade_level"],
            subject=unit_data["subject"],
            content=unit_data,
            num_lessons=unit_data.get("num_lessons", 0),
            standards=unit_data.get("standards", []),
            class_id=class_id,
            total_cost=cost_summary.get("total_cost", 0.0),
            input_tokens=cost_summary.get("input_tokens", 0),
            output_tokens=cost_summary.get("output_tokens", 0),
        )

        self.session.add(unit)
        self.session.commit()
        logger.info(f"Saved unit plan: {unit.unit_id}")
        return unit.unit_id

    def get_unit_plan(self, unit_id: str) -> Optional[Dict]:
        """
        Retrieve unit plan by ID.

        Args:
            unit_id: Unit plan ID

        Returns:
            Full unit plan data dict, or None if not found
        """
        unit = self.session.query(UnitPlanModel).filter_by(unit_id=unit_id).first()
        if unit:
            return unit.content
        return None

    def list_unit_plans(
        self,
        class_id: Optional[str] = None,
        subject: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List unit plans with optional filters."""
        query = self.session.query(UnitPlanModel)

        if class_id:
            query = query.filter_by(class_id=class_id)
        if subject:
            query = query.filter_by(subject=subject)

        query = query.order_by(UnitPlanModel.created_at.desc()).limit(limit)

        return [
            {
                "unit_id": u.unit_id,
                "unit_title": u.unit_title,
                "grade_level": u.grade_level,
                "subject": u.subject,
                "num_lessons": u.num_lessons,
                "created_at": u.created_at.isoformat(),
            }
            for u in query.all()
        ]

    # ═══════════════════════════════════════════════════════════
    # LESSONS (Engine 1)
    # ═══════════════════════════════════════════════════════════

    def save_lesson(
        self,
        lesson_data: Dict,
        cost_summary: Dict,
        unit_id: Optional[str] = None,
        lesson_number: Optional[int] = None,
        class_id: Optional[str] = None
    ) -> str:
        """
        Save generated lesson blueprint to database.

        Args:
            lesson_data: Full lesson data (from Pydantic model dump)
            cost_summary: Cost tracking dict
            unit_id: Optional parent unit ID
            lesson_number: Optional lesson sequence number
            class_id: Optional class ID

        Returns:
            lesson_id of saved lesson
        """
        lesson = LessonModel(
            lesson_id=lesson_data["lesson_id"],
            topic=lesson_data["topic"],
            grade_level=lesson_data["grade_level"],
            subject=lesson_data["subject"],
            unit_id=unit_id,
            lesson_number=lesson_number,
            content=lesson_data,
            duration_minutes=lesson_data.get("duration_minutes", 45),
            standards=lesson_data.get("standards", []),
            class_id=class_id,
            total_cost=cost_summary.get("total_cost", 0.0),
            input_tokens=cost_summary.get("input_tokens", 0),
            output_tokens=cost_summary.get("output_tokens", 0),
        )

        self.session.add(lesson)
        self.session.commit()
        logger.info(f"Saved lesson: {lesson.lesson_id}")
        return lesson.lesson_id

    def get_lesson(self, lesson_id: str) -> Optional[Dict]:
        """
        Retrieve lesson blueprint by ID.

        Args:
            lesson_id: Lesson ID

        Returns:
            Full lesson data dict, or None if not found
        """
        lesson = self.session.query(LessonModel).filter_by(lesson_id=lesson_id).first()
        if lesson:
            return lesson.content
        return None

    def list_lessons(
        self,
        unit_id: Optional[str] = None,
        class_id: Optional[str] = None,
        subject: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List lessons with optional filters."""
        query = self.session.query(LessonModel)

        if unit_id:
            query = query.filter_by(unit_id=unit_id)
        if class_id:
            query = query.filter_by(class_id=class_id)
        if subject:
            query = query.filter_by(subject=subject)

        query = query.order_by(LessonModel.created_at.desc()).limit(limit)

        return [
            {
                "lesson_id": l.lesson_id,
                "topic": l.topic,
                "grade_level": l.grade_level,
                "subject": l.subject,
                "duration_minutes": l.duration_minutes,
                "created_at": l.created_at.isoformat(),
            }
            for l in query.all()
        ]

    # ═══════════════════════════════════════════════════════════
    # WORKSHEETS (Engine 2)
    # ═══════════════════════════════════════════════════════════

    def save_worksheet(
        self,
        worksheet_data: Dict,
        lesson_id: str,
        tier_level: str,
        cost_summary: Dict
    ) -> str:
        """Save generated worksheet to database."""
        worksheet = WorksheetModel(
            worksheet_id=worksheet_data["worksheet_id"],
            lesson_id=lesson_id,
            tier_level=tier_level,
            worksheet_type=worksheet_data.get("worksheet_type", "practice"),
            content=worksheet_data,
            num_questions=worksheet_data.get("num_questions", 0),
            estimated_duration=worksheet_data.get("estimated_duration"),
            total_cost=cost_summary.get("total_cost", 0.0),
            input_tokens=cost_summary.get("input_tokens", 0),
            output_tokens=cost_summary.get("output_tokens", 0),
        )

        self.session.add(worksheet)
        self.session.commit()
        logger.info(f"Saved worksheet: {worksheet.worksheet_id} (Tier: {tier_level})")
        return worksheet.worksheet_id

    def get_worksheet(self, worksheet_id: str) -> Optional[Dict]:
        """Retrieve worksheet by ID."""
        worksheet = self.session.query(WorksheetModel).filter_by(worksheet_id=worksheet_id).first()
        if worksheet:
            return worksheet.content
        return None

    def list_worksheets_for_lesson(self, lesson_id: str) -> List[Dict]:
        """Get all worksheets for a lesson (all tiers)."""
        worksheets = self.session.query(WorksheetModel).filter_by(lesson_id=lesson_id).all()
        return [
            {
                "worksheet_id": w.worksheet_id,
                "tier_level": w.tier_level,
                "worksheet_type": w.worksheet_type,
                "num_questions": w.num_questions,
                "created_at": w.created_at.isoformat(),
            }
            for w in worksheets
        ]

    # ═══════════════════════════════════════════════════════════
    # IEP MODIFICATIONS (Engine 3)
    # ═══════════════════════════════════════════════════════════

    def save_iep_modification(
        self,
        modification_data: Dict,
        student_id: str,
        cost_summary: Dict,
        lesson_id: Optional[str] = None,
        worksheet_id: Optional[str] = None
    ) -> str:
        """Save IEP modification to database."""
        modification = IEPModificationModel(
            modification_id=modification_data["modification_id"],
            student_id=student_id,
            lesson_id=lesson_id,
            worksheet_id=worksheet_id,
            content=modification_data,
            disability_category=modification_data.get("disability_category", "Unknown"),
            accommodations_applied=modification_data.get("accommodations_applied", []),
            legal_compliant=modification_data.get("legal_compliant", True),
            compliance_report=modification_data.get("compliance_report"),
            total_cost=cost_summary.get("total_cost", 0.0),
        )

        self.session.add(modification)
        self.session.commit()
        logger.info(f"Saved IEP modification: {modification.modification_id}")
        return modification.modification_id

    def get_iep_modification(self, modification_id: str) -> Optional[Dict]:
        """Retrieve IEP modification by ID."""
        mod = self.session.query(IEPModificationModel).filter_by(modification_id=modification_id).first()
        if mod:
            return mod.content
        return None

    # ═══════════════════════════════════════════════════════════
    # ADAPTIVE PLANS (Engine 4)
    # ═══════════════════════════════════════════════════════════

    def save_adaptive_plan(
        self,
        plan_data: Dict,
        student_id: str,
        cost_summary: Dict,
        lesson_id: Optional[str] = None
    ) -> str:
        """Save adaptive plan to database."""
        plan = AdaptivePlanModel(
            plan_id=plan_data["plan_id"],
            student_id=student_id,
            lesson_id=lesson_id,
            content=plan_data,
            assigned_tier=plan_data.get("assigned_tier", "tier_2"),
            personalization_level=plan_data.get("personalization_level", "medium"),
            predicted_mastery=plan_data.get("predicted_mastery"),
            predicted_score=plan_data.get("predicted_score"),
            total_cost=cost_summary.get("total_cost", 0.0),
        )

        self.session.add(plan)
        self.session.commit()
        logger.info(f"Saved adaptive plan: {plan.plan_id}")
        return plan.plan_id

    def get_adaptive_plan(self, plan_id: str) -> Optional[Dict]:
        """Retrieve adaptive plan by ID."""
        plan = self.session.query(AdaptivePlanModel).filter_by(plan_id=plan_id).first()
        if plan:
            return plan.content
        return None

    # ═══════════════════════════════════════════════════════════
    # DIAGNOSTIC RESULTS (Engine 5)
    # ═══════════════════════════════════════════════════════════

    def save_diagnostic_result(
        self,
        diagnostic_data: Dict,
        student_id: str,
        cost_summary: Dict,
        assessment_id: Optional[str] = None
    ) -> str:
        """Save diagnostic result to database."""
        diagnostic = DiagnosticResultModel(
            diagnostic_id=diagnostic_data["diagnostic_id"],
            student_id=student_id,
            assessment_id=assessment_id,
            content=diagnostic_data,
            overall_mastery=diagnostic_data.get("overall_mastery", 0.0),
            concepts_analyzed=diagnostic_data.get("concepts_analyzed", []),
            recommended_tier=diagnostic_data.get("recommended_tier", "tier_2"),
            total_cost=cost_summary.get("total_cost", 0.0),
        )

        self.session.add(diagnostic)
        self.session.commit()
        logger.info(f"Saved diagnostic result: {diagnostic.diagnostic_id}")
        return diagnostic.diagnostic_id

    def get_diagnostic_result(self, diagnostic_id: str) -> Optional[Dict]:
        """Retrieve diagnostic result by ID."""
        diag = self.session.query(DiagnosticResultModel).filter_by(diagnostic_id=diagnostic_id).first()
        if diag:
            return diag.content
        return None

    # ═══════════════════════════════════════════════════════════
    # FEEDBACK REPORTS (Engine 6)
    # ═══════════════════════════════════════════════════════════

    def save_feedback_report(
        self,
        report_data: Dict,
        cost_summary: Dict,
        student_id: Optional[str] = None,
        class_id: Optional[str] = None
    ) -> str:
        """Save feedback report to database."""
        report = FeedbackReportModel(
            report_id=report_data["report_id"],
            student_id=student_id,
            class_id=class_id,
            content=report_data,
            prediction_accuracy=report_data.get("prediction_accuracy"),
            mae=report_data.get("mae"),
            rmse=report_data.get("rmse"),
            bkt_updates_applied=report_data.get("bkt_updates_applied", False),
            total_cost=cost_summary.get("total_cost", 0.0),
        )

        self.session.add(report)
        self.session.commit()
        logger.info(f"Saved feedback report: {report.report_id}")
        return report.report_id

    def get_feedback_report(self, report_id: str) -> Optional[Dict]:
        """Retrieve feedback report by ID."""
        report = self.session.query(FeedbackReportModel).filter_by(report_id=report_id).first()
        if report:
            return report.content
        return None

    # ═══════════════════════════════════════════════════════════
    # GRADED ASSESSMENTS
    # ═══════════════════════════════════════════════════════════

    def save_graded_assessment(
        self,
        graded_data: Dict,
        assessment_id: str,
        student_id: str,
        cost_summary: Dict
    ) -> str:
        """Save graded assessment to database."""
        graded = GradedAssessmentModel(
            graded_id=graded_data["graded_id"],
            assessment_id=assessment_id,
            student_id=student_id,
            content=graded_data,
            raw_score=graded_data.get("raw_score", 0.0),
            max_score=graded_data.get("max_score", 100.0),
            percentage=graded_data.get("percentage", 0.0),
            strengths=graded_data.get("strengths", []),
            weaknesses=graded_data.get("weaknesses", []),
            recommendations=graded_data.get("recommendations", []),
            total_cost=cost_summary.get("total_cost", 0.0),
        )

        self.session.add(graded)
        self.session.commit()
        logger.info(f"Saved graded assessment: {graded.graded_id}")
        return graded.graded_id

    def get_graded_assessment(self, graded_id: str) -> Optional[Dict]:
        """Retrieve graded assessment by ID."""
        graded = self.session.query(GradedAssessmentModel).filter_by(graded_id=graded_id).first()
        if graded:
            return graded.content
        return None

    # ═══════════════════════════════════════════════════════════
    # PIPELINE EXECUTION TRACKING
    # ═══════════════════════════════════════════════════════════

    def create_pipeline_job(
        self,
        job_id: str,
        pipeline_type: str = "full_9_engine"
    ) -> str:
        """Create new pipeline execution job."""
        pipeline = PipelineExecutionModel(
            job_id=job_id,
            pipeline_type=pipeline_type,
            status="running",
            completed_stages=[],
        )

        self.session.add(pipeline)
        self.session.commit()
        logger.info(f"Created pipeline job: {job_id}")
        return job_id

    def update_pipeline_status(
        self,
        job_id: str,
        status: str,
        current_stage: Optional[str] = None,
        completed_stage: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Update pipeline execution status."""
        pipeline = self.session.query(PipelineExecutionModel).filter_by(job_id=job_id).first()
        if not pipeline:
            logger.warning(f"Pipeline job not found: {job_id}")
            return

        pipeline.status = status
        if current_stage:
            pipeline.current_stage = current_stage
        if completed_stage:
            if completed_stage not in pipeline.completed_stages:
                pipeline.completed_stages.append(completed_stage)
        if error:
            pipeline.errors.append(error)

        if status == "complete":
            pipeline.end_time = datetime.utcnow()
            if pipeline.start_time:
                duration = (pipeline.end_time - pipeline.start_time).total_seconds()
                pipeline.duration_seconds = duration

        self.session.commit()

    def get_pipeline_status(self, job_id: str) -> Optional[Dict]:
        """Get pipeline execution status."""
        pipeline = self.session.query(PipelineExecutionModel).filter_by(job_id=job_id).first()
        if pipeline:
            return {
                "job_id": pipeline.job_id,
                "status": pipeline.status,
                "current_stage": pipeline.current_stage,
                "completed_stages": pipeline.completed_stages,
                "total_cost": pipeline.total_cost,
                "duration_seconds": pipeline.duration_seconds,
                "errors": pipeline.errors,
            }
        return None
