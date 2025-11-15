"""
StudentModelInterface - Unified API for student data access.

CRITICAL RULE: All engines MUST use this interface to access student data.
NO direct database queries allowed outside this module.

This interface provides a clean abstraction over PostgreSQL + Chroma,
ensuring consistent data access patterns and performance optimizations.
"""

import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from .database import (
    AssessmentModel,
    ClassModel,
    IEPModel,
    MasteryModel,
    PredictionModel,
    SessionLocal,
    StudentModel,
)
from .schemas import (
    AccommodationType,
    AdaptiveRecommendation,
    AssessmentRecord,
    BulkImportResult,
    BulkImportRow,
    ClassMasteryDistribution,
    ClassRosterSummary,
    ConceptMastery,
    DisabilityCategory,
    GradeLevel,
    IEPAccommodation,
    IEPData,
    IEPUpdate,
    LearningPreference,
    MasterySnapshot,
    PredictionLog,
    ReadingLevel,
    StudentProfile,
    StudentProfileCreate,
    TierLevel,
)
from .vector_store import StudentVectorStore


# ═══════════════════════════════════════════════════════════
# STUDENT MODEL INTERFACE
# ═══════════════════════════════════════════════════════════


class StudentModelInterface:
    """
    Unified interface for all student data operations.

    Methods:
    - Student profiles: get, create, import
    - Class rosters: get roster, get IEP summary
    - Mastery tracking: get, update, distributions
    - IEP management: get, update, list students with IEPs
    - Assessments: get history, log new assessments
    - Predictions: log predictions, get accuracy metrics
    - Learning preferences: get preferences, find similar students
    """

    def __init__(self, db_session: Optional[Session] = None, vector_store: Optional[StudentVectorStore] = None):
        """
        Initialize interface.

        Args:
            db_session: SQLAlchemy session (creates new one if None)
            vector_store: Chroma vector store (creates new one if None)
        """
        self.db = db_session if db_session is not None else SessionLocal()
        self.vector_store = vector_store if vector_store is not None else StudentVectorStore()
        self._owns_session = db_session is None

    def close(self):
        """Close database session if we own it."""
        if self._owns_session:
            self.db.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()

    # ═══════════════════════════════════════════════════════════
    # STUDENT PROFILES
    # ═══════════════════════════════════════════════════════════

    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """
        Retrieve complete student profile.

        Args:
            student_id: Student identifier

        Returns:
            StudentProfile or None if not found
        """
        student = self.db.query(StudentModel).filter(StudentModel.student_id == student_id).first()

        if not student:
            return None

        # Get IEP accommodations if applicable
        accommodations = []
        if student.has_iep and student.iep_data:
            accommodations = [AccommodationType(acc["type"]) for acc in student.iep_data.accommodations if acc.get("enabled", True)]

        return StudentProfile(
            student_id=student.student_id,
            student_name=student.student_name,
            grade_level=student.grade_level,
            class_id=student.class_id,
            reading_level=student.reading_level,
            learning_preferences=[LearningPreference(pref) for pref in student.learning_preferences],
            has_iep=student.has_iep,
            primary_disability=student.primary_disability,
            accommodations=accommodations,
            created_at=student.created_at,
            updated_at=student.updated_at,
        )

    def create_student_profile(self, student_data: StudentProfileCreate) -> StudentProfile:
        """
        Create new student profile.

        Args:
            student_data: Student creation data

        Returns:
            Created StudentProfile
        """
        # Generate student_id if not provided
        import uuid
        student_id = f"s_{uuid.uuid4().hex[:8]}"

        # Create student record
        student = StudentModel(
            student_id=student_id,
            student_name=student_data.student_name,
            grade_level=student_data.grade_level,
            class_id=student_data.class_id,
            reading_level=student_data.reading_level,
            learning_preferences=[pref.value for pref in student_data.learning_preferences],
            has_iep=student_data.has_iep,
            primary_disability=student_data.primary_disability,
        )

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        # Add to vector store for learning preferences
        if student_data.learning_preferences:
            prefs_text = f"{student_data.student_name} is a {', '.join([p.value for p in student_data.learning_preferences])} learner with {student_data.reading_level.value} reading level."
            self.vector_store.add_student_preferences(
                student_id,
                prefs_text,
                metadata={
                    "learning_preferences": [p.value for p in student_data.learning_preferences],
                    "reading_level": student_data.reading_level.value,
                },
            )

        return self.get_student_profile(student_id)

    def create_iep(self, iep_data: "IEPCreate") -> "IEPData":
        """
        Create new IEP record for a student.

        Args:
            iep_data: IEP creation data

        Returns:
            Created IEPData
        """
        from datetime import datetime, timedelta

        # Create IEP record
        iep = IEPModel(
            student_id=iep_data.student_id,
            primary_disability=iep_data.primary_disability,
            secondary_disabilities=[d.value for d in iep_data.secondary_disabilities],
            accommodations=[
                {
                    "type": a.accommodation_type.value,
                    "enabled": a.enabled,
                    "settings": a.settings,
                }
                for a in iep_data.accommodations
            ],
            modifications=iep_data.modifications,
            goals=iep_data.goals,
            last_reviewed=iep_data.last_reviewed or datetime.utcnow(),
            next_review_due=iep_data.next_review_due or (datetime.utcnow() + timedelta(days=365)),
        )

        self.db.add(iep)
        self.db.commit()
        self.db.refresh(iep)

        return self.get_iep_accommodations(iep_data.student_id)

    def create_mastery_estimate(self, mastery_data: "ConceptMasteryCreate") -> "ConceptMastery":
        """
        Create new mastery estimate for a student-concept pair.

        Args:
            mastery_data: Mastery creation data

        Returns:
            Created ConceptMastery
        """
        # Use update_mastery_estimate which handles create-or-update
        return self.update_mastery_estimate(
            student_id=mastery_data.student_id,
            concept_id=mastery_data.concept_id,
            new_mastery=mastery_data.mastery_probability,
            concept_name=mastery_data.concept_name,
        )

    def bulk_import_students(self, students_data: List[BulkImportRow], class_id: str) -> BulkImportResult:
        """
        Bulk import students from CSV data (Page 5 UI).

        Args:
            students_data: List of student data rows
            class_id: Class to assign students to

        Returns:
            BulkImportResult with success/failure counts
        """
        successful = 0
        failed_rows = []
        errors = []
        created_ids = []

        for idx, row in enumerate(students_data):
            try:
                profile = StudentProfileCreate(
                    student_name=row.student_name,
                    grade_level=row.grade_level,
                    class_id=class_id,
                    reading_level=row.reading_level or ReadingLevel.PROFICIENT,
                    has_iep=row.iep_status,
                    primary_disability=row.primary_disability if row.iep_status else None,
                )

                created_profile = self.create_student_profile(profile)
                created_ids.append(created_profile.student_id)
                successful += 1

            except Exception as e:
                failed_rows.append(idx)
                errors.append(f"Row {idx}: {str(e)}")

        return BulkImportResult(
            total_rows=len(students_data),
            successful_imports=successful,
            failed_rows=failed_rows,
            errors=errors,
            created_student_ids=created_ids,
        )

    # ═══════════════════════════════════════════════════════════
    # CLASS ROSTERS
    # ═══════════════════════════════════════════════════════════

    def get_class_roster(self, class_id: str) -> Optional[ClassRosterSummary]:
        """
        Get class roster summary (Page 1 UI dropdown).

        Args:
            class_id: Class identifier

        Returns:
            ClassRosterSummary or None if not found
        """
        class_obj = self.db.query(ClassModel).filter(ClassModel.class_id == class_id).first()

        if not class_obj:
            return None

        # Count students and IEPs
        total_students = self.db.query(StudentModel).filter(StudentModel.class_id == class_id).count()
        students_with_ieps = (
            self.db.query(StudentModel)
            .filter(and_(StudentModel.class_id == class_id, StudentModel.has_iep == True))
            .count()
        )

        return ClassRosterSummary(
            class_id=class_obj.class_id,
            class_name=class_obj.class_name,
            grade_level=class_obj.grade_level,
            subject=class_obj.subject,
            total_students=total_students,
            students_with_ieps=students_with_ieps,
            teacher_id=class_obj.teacher_id,
        )

    def get_class_students(self, class_id: str) -> List[StudentProfile]:
        """
        Get all students in a class.

        Args:
            class_id: Class identifier

        Returns:
            List of StudentProfiles
        """
        students = self.db.query(StudentModel).filter(StudentModel.class_id == class_id).all()

        return [self.get_student_profile(s.student_id) for s in students]

    # ═══════════════════════════════════════════════════════════
    # MASTERY TRACKING
    # ═══════════════════════════════════════════════════════════

    def retrieve_concept_mastery(self, student_id: str, concept_ids: List[str]) -> List[ConceptMastery]:
        """
        Get mastery estimates for specific concepts (Page 3 UI).

        Args:
            student_id: Student identifier
            concept_ids: List of concept IDs to retrieve

        Returns:
            List of ConceptMastery objects
        """
        mastery_records = (
            self.db.query(MasteryModel)
            .filter(and_(MasteryModel.student_id == student_id, MasteryModel.concept_id.in_(concept_ids)))
            .all()
        )

        return [
            ConceptMastery(
                student_id=m.student_id,
                concept_id=m.concept_id,
                concept_name=m.concept_name,
                mastery_probability=m.mastery_probability,
                p_learn=m.p_learn,
                p_guess=m.p_guess,
                p_slip=m.p_slip,
                last_updated=m.last_updated,
                num_observations=m.num_observations,
            )
            for m in mastery_records
        ]

    def update_mastery_estimate(
        self, student_id: str, concept_id: str, new_mastery: float, concept_name: Optional[str] = None
    ) -> ConceptMastery:
        """
        Update mastery estimate (called by Engine 5 and Grader).

        Args:
            student_id: Student identifier
            concept_id: Concept identifier
            new_mastery: New mastery probability (0-1)
            concept_name: Human-readable name (optional)

        Returns:
            Updated ConceptMastery
        """
        mastery = (
            self.db.query(MasteryModel)
            .filter(and_(MasteryModel.student_id == student_id, MasteryModel.concept_id == concept_id))
            .first()
        )

        if mastery:
            # Update existing
            mastery.mastery_probability = new_mastery
            mastery.num_observations += 1
            mastery.last_updated = datetime.utcnow()
        else:
            # Create new
            mastery = MasteryModel(
                student_id=student_id,
                concept_id=concept_id,
                concept_name=concept_name or concept_id,
                mastery_probability=new_mastery,
                num_observations=1,
            )
            self.db.add(mastery)

        self.db.commit()
        self.db.refresh(mastery)

        return ConceptMastery(
            student_id=mastery.student_id,
            concept_id=mastery.concept_id,
            concept_name=mastery.concept_name,
            mastery_probability=mastery.mastery_probability,
            p_learn=mastery.p_learn,
            p_guess=mastery.p_guess,
            p_slip=mastery.p_slip,
            last_updated=mastery.last_updated,
            num_observations=mastery.num_observations,
        )

    def get_class_mastery_distribution(self, class_id: str, concept_id: str) -> Optional[ClassMasteryDistribution]:
        """
        Get mastery distribution for a class and concept (Page 3 UI chart).

        Args:
            class_id: Class identifier
            concept_id: Concept identifier

        Returns:
            ClassMasteryDistribution or None
        """
        # Get all students in class
        student_ids = [s.student_id for s in self.db.query(StudentModel).filter(StudentModel.class_id == class_id).all()]

        if not student_ids:
            return None

        # Get mastery data
        mastery_records = (
            self.db.query(MasteryModel)
            .filter(and_(MasteryModel.student_id.in_(student_ids), MasteryModel.concept_id == concept_id))
            .all()
        )

        if not mastery_records:
            return None

        masteries = [m.mastery_probability for m in mastery_records]

        # Calculate distribution
        below_50 = sum(1 for m in masteries if m < 0.5)
        between_50_75 = sum(1 for m in masteries if 0.5 <= m < 0.75)
        above_75 = sum(1 for m in masteries if m >= 0.75)

        return ClassMasteryDistribution(
            class_id=class_id,
            concept_id=concept_id,
            concept_name=mastery_records[0].concept_name,
            mean_mastery=statistics.mean(masteries),
            median_mastery=statistics.median(masteries),
            std_dev=statistics.stdev(masteries) if len(masteries) > 1 else 0.0,
            students_below_50=below_50,
            students_50_to_75=between_50_75,
            students_above_75=above_75,
        )

    # ═══════════════════════════════════════════════════════════
    # ASSESSMENT HISTORY
    # ═══════════════════════════════════════════════════════════

    def get_assessment_history(
        self, student_id: str, limit: int = 10, concept_id: Optional[str] = None
    ) -> List[AssessmentRecord]:
        """
        Get recent assessment history (Page 3 UI).

        Args:
            student_id: Student identifier
            limit: Max number of records
            concept_id: Filter by concept (optional)

        Returns:
            List of AssessmentRecords
        """
        query = self.db.query(AssessmentModel).filter(AssessmentModel.student_id == student_id)

        if concept_id:
            query = query.filter(AssessmentModel.concept_ids.contains([concept_id]))

        assessments = query.order_by(AssessmentModel.submitted_at.desc()).limit(limit).all()

        return [
            AssessmentRecord(
                assessment_id=a.assessment_id,
                student_id=a.student_id,
                concept_ids=a.concept_ids,
                raw_score=a.raw_score,
                max_score=a.max_score,
                percentage=a.percentage,
                responses=a.responses,
                correct_answers=a.correct_answers,
                incorrect_answers=a.incorrect_answers,
                assessment_type=a.assessment_type,
                tier_level=a.tier_level,
                submitted_at=a.submitted_at,
                graded_at=a.graded_at,
            )
            for a in assessments
        ]

    def log_assessment(self, assessment: AssessmentRecord) -> None:
        """
        Log new assessment submission.

        Args:
            assessment: AssessmentRecord to log
        """
        assessment_model = AssessmentModel(
            assessment_id=assessment.assessment_id,
            student_id=assessment.student_id,
            assessment_type=assessment.assessment_type,
            concept_ids=assessment.concept_ids,
            raw_score=assessment.raw_score,
            max_score=assessment.max_score,
            percentage=assessment.percentage,
            responses=assessment.responses,
            correct_answers=assessment.correct_answers,
            incorrect_answers=assessment.incorrect_answers,
            tier_level=assessment.tier_level,
            submitted_at=assessment.submitted_at,
            graded_at=assessment.graded_at,
        )

        self.db.add(assessment_model)
        self.db.commit()


    # ═══════════════════════════════════════════════════════════
    # IEP MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def get_iep_accommodations(self, student_id: str) -> Optional[IEPData]:
        """
        Get complete IEP data (Page 4 UI).

        Args:
            student_id: Student identifier

        Returns:
            IEPData or None if no IEP
        """
        iep = self.db.query(IEPModel).filter(IEPModel.student_id == student_id).first()

        if not iep:
            return None

        return IEPData(
            student_id=iep.student_id,
            primary_disability=iep.primary_disability,
            secondary_disabilities=[DisabilityCategory(d) for d in iep.secondary_disabilities],
            accommodations=[
                IEPAccommodation(
                    accommodation_type=AccommodationType(a["type"]),
                    enabled=a.get("enabled", True),
                    settings=a.get("settings", {})
                ) for a in iep.accommodations
            ],
            modifications=iep.modifications,
            goals=iep.goals,
            last_reviewed=iep.last_reviewed,
            next_review_due=iep.next_review_due,
        )

    def update_iep_accommodations(self, student_id: str, iep_update: IEPUpdate) -> IEPData:
        """
        Update IEP accommodations (Page 4 UI save button).

        Args:
            student_id: Student identifier
            iep_update: IEP update data

        Returns:
            Updated IEPData
        """
        iep = self.db.query(IEPModel).filter(IEPModel.student_id == student_id).first()

        if not iep:
            raise ValueError(f"No IEP found for student {student_id}")

        # Update fields if provided
        if iep_update.primary_disability is not None:
            iep.primary_disability = iep_update.primary_disability

        if iep_update.accommodations is not None:
            iep.accommodations = [
                {
                    "type": a.accommodation_type.value,
                    "enabled": a.enabled,
                    "settings": a.settings,
                }
                for a in iep_update.accommodations
            ]

        if iep_update.modifications is not None:
            iep.modifications = iep_update.modifications

        iep.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(iep)

        return self.get_iep_accommodations(student_id)

    def get_students_with_ieps(self, class_id: str) -> List[StudentProfile]:
        """
        Get all students with IEPs in a class (Page 4 UI list).

        Args:
            class_id: Class identifier

        Returns:
            List of StudentProfiles with IEPs
        """
        students = (
            self.db.query(StudentModel)
            .filter(and_(StudentModel.class_id == class_id, StudentModel.has_iep == True))
            .all()
        )

        return [self.get_student_profile(s.student_id) for s in students]

    # ═══════════════════════════════════════════════════════════
    # TIER ASSIGNMENT
    # ═══════════════════════════════════════════════════════════

    def get_students_by_tier(self, class_id: str, concept_id: str, tier_thresholds: Optional[Dict] = None) -> Dict[TierLevel, List[str]]:
        """
        Assign students to tiers based on mastery (Page 2 UI).

        Args:
            class_id: Class identifier
            concept_id: Concept for tier assignment
            tier_thresholds: Custom thresholds (default: Tier1 >=0.75, Tier3 <0.45)

        Returns:
            Dict mapping TierLevel to list of student_ids
        """
        if tier_thresholds is None:
            tier_thresholds = {"tier1_min": 0.75, "tier3_max": 0.45}

        # Get all students in class
        students = self.db.query(StudentModel).filter(StudentModel.class_id == class_id).all()

        tier_assignments = {TierLevel.TIER_1: [], TierLevel.TIER_2: [], TierLevel.TIER_3: []}

        for student in students:
            # Get mastery for concept
            mastery = (
                self.db.query(MasteryModel)
                .filter(and_(MasteryModel.student_id == student.student_id, MasteryModel.concept_id == concept_id))
                .first()
            )

            if mastery:
                mastery_prob = mastery.mastery_probability

                # Assign tier
                if mastery_prob >= tier_thresholds["tier1_min"]:
                    tier_assignments[TierLevel.TIER_1].append(student.student_id)
                elif mastery_prob <= tier_thresholds["tier3_max"]:
                    tier_assignments[TierLevel.TIER_3].append(student.student_id)
                else:
                    tier_assignments[TierLevel.TIER_2].append(student.student_id)
            else:
                # No mastery data - default to Tier 2
                tier_assignments[TierLevel.TIER_2].append(student.student_id)

        return tier_assignments

    # ═══════════════════════════════════════════════════════════
    # ADAPTIVE RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════

    def get_adaptive_recommendations(self, student_id: str) -> List[AdaptiveRecommendation]:
        """
        Get adaptive recommendations for a student (Page 3 UI, Engine 4).

        This is a placeholder - actual implementation would be in Engine 4.
        Here we provide basic rule-based recommendations.

        Args:
            student_id: Student identifier

        Returns:
            List of AdaptiveRecommendations
        """
        recommendations = []

        # Get student's mastery data
        mastery_records = self.db.query(MasteryModel).filter(MasteryModel.student_id == student_id).all()

        for mastery in mastery_records:
            # Rule 1: Ready to advance if mastery > 0.80
            if mastery.mastery_probability > 0.80:
                recommendations.append(
                    AdaptiveRecommendation(
                        student_id=student_id,
                        recommendation_type="tier_change",
                        message=f"Ready to advance to higher tier for {mastery.concept_name}",
                        confidence=mastery.mastery_probability,
                    )
                )

            # Rule 2: Needs intervention if mastery < 0.40
            elif mastery.mastery_probability < 0.40:
                recommendations.append(
                    AdaptiveRecommendation(
                        student_id=student_id,
                        recommendation_type="intervention",
                        message=f"Needs additional support for {mastery.concept_name}",
                        confidence=1.0 - mastery.mastery_probability,
                    )
                )

        return recommendations

    # ═══════════════════════════════════════════════════════════
    # LEARNING PREFERENCES
    # ═══════════════════════════════════════════════════════════

    def get_learning_preferences(self, student_id: str) -> Optional[Dict]:
        """
        Get student learning preferences from vector store.

        Args:
            student_id: Student identifier

        Returns:
            Dict with preferences data or None
        """
        return self.vector_store.get_student_preferences(student_id)

    def find_similar_students(self, student_id: str, n_results: int = 5) -> List[Dict]:
        """
        Find students with similar learning preferences (Engine 4).

        Args:
            student_id: Reference student
            n_results: Number of similar students

        Returns:
            List of similar students
        """
        return self.vector_store.find_similar_students(student_id, n_results)

    # ═══════════════════════════════════════════════════════════
    # PREDICTION TRACKING (Engine 6)
    # ═══════════════════════════════════════════════════════════

    def log_prediction(self, prediction: PredictionLog) -> None:
        """
        Log a prediction from an engine (Engine 6 tracking).

        Args:
            prediction: PredictionLog data
        """
        prediction_model = PredictionModel(
            prediction_id=prediction.prediction_id,
            engine_name=prediction.engine_name,
            student_id=prediction.student_id,
            concept_id=prediction.concept_id,
            predicted_mastery=prediction.predicted_mastery,
            predicted_tier=prediction.predicted_tier,
            predicted_at=prediction.predicted_at,
        )

        self.db.add(prediction_model)
        self.db.commit()

    def update_prediction_outcome(self, prediction_id: str, actual_mastery: float, actual_score: float) -> None:
        """
        Update prediction with actual outcome (called by Grader).

        Args:
            prediction_id: Prediction identifier
            actual_mastery: Actual mastery after assessment
            actual_score: Actual assessment score
        """
        prediction = self.db.query(PredictionModel).filter(PredictionModel.prediction_id == prediction_id).first()

        if prediction:
            prediction.actual_mastery = actual_mastery
            prediction.actual_score = actual_score
            prediction.error = prediction.predicted_mastery - actual_mastery
            prediction.outcome_recorded_at = datetime.utcnow()
            self.db.commit()

    def get_prediction_accuracy(self, engine_name: str, timeframe_days: int = 30) -> Dict:
        """
        Calculate prediction accuracy metrics for an engine (Engine 6).

        Args:
            engine_name: Engine identifier (e.g., "engine_5_diagnostic")
            timeframe_days: Days to look back

        Returns:
            Dict with accuracy metrics (RMSE, MAE, correlation)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)

        predictions = (
            self.db.query(PredictionModel)
            .filter(
                and_(
                    PredictionModel.engine_name == engine_name,
                    PredictionModel.predicted_at >= cutoff_date,
                    PredictionModel.actual_mastery.isnot(None),
                )
            )
            .all()
        )

        if not predictions:
            return {
                "num_predictions": 0,
                "rmse": None,
                "mae": None,
                "correlation": None,
                "overestimation_bias": None,
            }

        # Calculate metrics
        errors = [p.error for p in predictions]
        rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5
        mae = sum(abs(e) for e in errors) / len(errors)
        overestimation_bias = sum(errors) / len(errors)

        # Correlation (simple Pearson)
        predicted = [p.predicted_mastery for p in predictions]
        actual = [p.actual_mastery for p in predictions]

        if len(predicted) > 1:
            pred_mean = sum(predicted) / len(predicted)
            actual_mean = sum(actual) / len(actual)

            numerator = sum((p - pred_mean) * (a - actual_mean) for p, a in zip(predicted, actual))
            denom_pred = sum((p - pred_mean) ** 2 for p in predicted) ** 0.5
            denom_actual = sum((a - actual_mean) ** 2 for a in actual) ** 0.5

            correlation = numerator / (denom_pred * denom_actual) if denom_pred * denom_actual > 0 else 0.0
        else:
            correlation = 0.0

        return {
            "engine_name": engine_name,
            "timeframe_days": timeframe_days,
            "num_predictions": len(predictions),
            "rmse": rmse,
            "mae": mae,
            "correlation": correlation,
            "overestimation_bias": overestimation_bias,
        }

    # ═══════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════

    def get_students_needing_attention(self, class_id: str, threshold: float = 0.5) -> List[StudentProfile]:
        """
        Get students with low mastery scores (Page 3 UI alerts).

        Args:
            class_id: Class identifier
            threshold: Mastery threshold (default 0.5)

        Returns:
            List of students needing attention
        """
        # Get all students in class
        students = self.db.query(StudentModel).filter(StudentModel.class_id == class_id).all()

        students_needing_attention = []

        for student in students:
            # Get average mastery across all concepts
            mastery_records = self.db.query(MasteryModel).filter(MasteryModel.student_id == student.student_id).all()

            if mastery_records:
                avg_mastery = sum(m.mastery_probability for m in mastery_records) / len(mastery_records)

                if avg_mastery < threshold:
                    students_needing_attention.append(self.get_student_profile(student.student_id))

        return students_needing_attention

    def get_database_stats(self) -> Dict:
        """
        Get database statistics for monitoring.

        Returns:
            Dict with table counts
        """
        return {
            "classes": self.db.query(ClassModel).count(),
            "students": self.db.query(StudentModel).count(),
            "ieps": self.db.query(IEPModel).count(),
            "mastery_records": self.db.query(MasteryModel).count(),
            "assessments": self.db.query(AssessmentModel).count(),
            "predictions": self.db.query(PredictionModel).count(),
        }


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def get_interface() -> StudentModelInterface:
    """Get a new StudentModelInterface instance."""
    return StudentModelInterface()


# ═══════════════════════════════════════════════════════════
# CLI COMMANDS
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            """
Usage: python -m src.student_model.interface <command>

Commands:
  stats     - Show database statistics
  test      - Run basic functionality test

Example:
  python -m src.student_model.interface stats
        """
        )
        sys.exit(1)

    command = sys.argv[1]

    with get_interface() as interface:
        if command == "stats":
            stats = interface.get_database_stats()
            print("\n" + "=" * 50)
            print("📊 STUDENT MODEL STATISTICS")
            print("=" * 50)
            for table, count in stats.items():
                print(f"  {table:20s}: {count:5d} rows")
            print("=" * 50 + "\n")

            # Vector store stats
            vector_stats = interface.vector_store.get_collection_counts()
            print("=" * 50)
            print("🔍 VECTOR STORE STATISTICS")
            print("=" * 50)
            for collection, count in vector_stats.items():
                print(f"  {collection:25s}: {count:5d} documents")
            print("=" * 50 + "\n")

        elif command == "test":
            print("Testing StudentModelInterface...")
            print("✅ Interface initialized successfully!")
            print(f"Database stats: {interface.get_database_stats()}")

        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
