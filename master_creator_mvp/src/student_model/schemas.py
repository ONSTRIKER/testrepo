"""
Pydantic schemas for Student Model data structures.

These schemas define type-safe data models for:
- Student profiles and demographics
- IEP accommodations and modifications
- Assessment history and scores
- Concept mastery estimates (Bayesian Knowledge Tracing)
- Learning preferences and vectors

All engines and UI pages use these schemas for data exchange.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ENUMS - Standardized categorical values
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class GradeLevel(str, Enum):
    """K-12 grade levels."""

    GRADE_9 = "9"
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"


class Subject(str, Enum):
    """Academic subjects."""

    ELA = "English Language Arts"
    MATH = "Mathematics"
    SCIENCE = "Science"
    SOCIAL_STUDIES = "Social Studies"
    ELECTIVE = "Elective"


class ReadingLevel(str, Enum):
    """Reading proficiency levels."""

    BELOW_BASIC = "Below Basic"
    BASIC = "Basic"
    PROFICIENT = "Proficient"
    ADVANCED = "Advanced"


class DisabilityCategory(str, Enum):
    """Primary disability categories (IDEA)."""

    LEARNING_DISABILITY = "Specific Learning Disability"
    ADHD = "ADHD"
    AUTISM = "Autism Spectrum Disorder"
    SPEECH_LANGUAGE = "Speech/Language Impairment"
    INTELLECTUAL_DISABILITY = "Intellectual Disability"
    EMOTIONAL_DISTURBANCE = "Emotional Disturbance"
    OTHER_HEALTH_IMPAIRMENT = "Other Health Impairment"
    NONE = "None"


class AccommodationType(str, Enum):
    """Standard IEP accommodations."""

    EXTENDED_TIME = "Extended Time"
    TEXT_TO_SPEECH = "Text-to-Speech"
    REDUCED_QUESTIONS = "Reduced Question Count"
    GRAPHIC_ORGANIZERS = "Graphic Organizers"
    CALCULATOR = "Calculator"
    SCRIBE = "Scribe"
    PREFERENTIAL_SEATING = "Preferential Seating"
    MOVEMENT_BREAKS = "Movement Breaks"
    SENTENCE_FRAMES = "Sentence Frames"
    WORD_BANK = "Word Bank"
    VISUAL_SUPPORTS = "Visual Supports"
    AUDIO_RECORDINGS = "Audio Recordings"


class TierLevel(str, Enum):
    """Differentiation tiers (RTI framework)."""

    TIER_1 = "Tier 1"  # Light support
    TIER_2 = "Tier 2"  # Moderate support
    TIER_3 = "Tier 3"  # Heavy support


class LearningPreference(str, Enum):
    """VARK learning styles."""

    VISUAL = "Visual"
    AUDITORY = "Auditory"
    READING_WRITING = "Reading/Writing"
    KINESTHETIC = "Kinesthetic"


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# STUDENT PROFILE SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class StudentProfile(BaseModel):
    """Complete student profile for Student Model."""

    model_config = ConfigDict(from_attributes=True)

    # Identity
    student_id: str = Field(..., description="Unique student identifier")
    student_name: str = Field(..., description="Full name")
    grade_level: GradeLevel
    class_id: str = Field(..., description="Class roster identifier")

    # Academic background
    reading_level: ReadingLevel
    learning_preferences: List[LearningPreference] = Field(
        default_factory=list, description="Primary learning modalities"
    )

    # Special education
    has_iep: bool = Field(default=False)
    primary_disability: Optional[DisabilityCategory] = None
    accommodations: List[AccommodationType] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("accommodations")
    @classmethod
    def validate_iep_consistency(cls, v: List[AccommodationType], info) -> List[AccommodationType]:
        """Ensure accommodations are only present if has_iep=True."""
        if v and not info.data.get("has_iep"):
            raise ValueError("Cannot have accommodations without IEP")
        return v


class StudentProfileCreate(BaseModel):
    """Schema for creating new student profiles."""

    student_name: str
    grade_level: GradeLevel
    class_id: str
    reading_level: ReadingLevel = ReadingLevel.PROFICIENT
    learning_preferences: List[LearningPreference] = []
    has_iep: bool = False
    primary_disability: Optional[DisabilityCategory] = None
    accommodations: List[AccommodationType] = []


class ClassRosterSummary(BaseModel):
    """Summary view of a class for UI dropdowns."""

    class_id: str
    class_name: str = Field(..., description="e.g., 'Period 3 Biology'")
    grade_level: GradeLevel
    subject: Subject
    total_students: int
    students_with_ieps: int
    teacher_id: str


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# IEP & ACCOMMODATIONS SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class IEPAccommodation(BaseModel):
    """Individual accommodation with settings."""

    accommodation_type: AccommodationType
    enabled: bool = True
    settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="e.g., {'multiplier': 1.5} for extended time",
    )


class AccommodationCreate(BaseModel):
    """Schema for creating accommodations."""

    accommodation_type: AccommodationType
    enabled: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class IEPCreate(BaseModel):
    """Schema for creating IEP records."""

    student_id: str
    primary_disability: DisabilityCategory
    secondary_disabilities: List[DisabilityCategory] = []
    accommodations: List[AccommodationCreate] = []
    modifications: Dict[str, Any] = Field(default_factory=dict)
    goals: List[str] = Field(default_factory=list)
    last_reviewed: Optional[datetime] = None
    next_review_due: Optional[datetime] = None


class IEPData(BaseModel):
    """Complete IEP information for a student."""

    student_id: str
    primary_disability: DisabilityCategory
    secondary_disabilities: List[DisabilityCategory] = []
    accommodations: List[IEPAccommodation]
    modifications: Dict[str, Any] = Field(
        default_factory=dict,
        description="e.g., {'alternate_grading': True}",
    )
    goals: List[str] = Field(default_factory=list, description="IEP learning goals")
    last_reviewed: datetime
    next_review_due: datetime


class IEPUpdate(BaseModel):
    """Schema for updating IEP accommodations (Page 4 UI)."""

    primary_disability: Optional[DisabilityCategory] = None
    accommodations: Optional[List[IEPAccommodation]] = None
    modifications: Optional[Dict[str, Any]] = None


class IEPAccommodationUpdate(BaseModel):
    """Schema for updating IEP accommodations via API."""

    primary_disability: Optional[DisabilityCategory] = None
    accommodations: Optional[List[IEPAccommodation]] = None
    modifications: Optional[Dict[str, Any]] = None
    review_date: Optional[datetime] = None


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# MASTERY & ASSESSMENT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class ConceptMasteryCreate(BaseModel):
    """Schema for creating concept mastery records."""

    student_id: str
    concept_id: str
    concept_name: str
    mastery_probability: float = Field(..., ge=0.0, le=1.0)
    p_learn: float = Field(default=0.3, ge=0.0, le=1.0)
    p_guess: float = Field(default=0.25, ge=0.0, le=1.0)
    p_slip: float = Field(default=0.1, ge=0.0, le=1.0)
    num_observations: int = Field(default=0)


class ConceptMastery(BaseModel):
    """Bayesian Knowledge Tracing estimate for a concept."""

    student_id: str
    concept_id: str = Field(..., description="e.g., 'photosynthesis_process'")
    concept_name: str = Field(..., description="Human-readable label")

    # Bayesian parameters (Engine 5 uses these)
    mastery_probability: float = Field(
        ..., ge=0.0, le=1.0, description="P(mastery) estimate"
    )
    p_learn: float = Field(0.3, ge=0.0, le=1.0, description="Prob of learning")
    p_guess: float = Field(0.25, ge=0.0, le=1.0, description="Prob of guessing")
    p_slip: float = Field(0.1, ge=0.0, le=1.0, description="Prob of slipping")

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    num_observations: int = Field(0, description="# of assessment attempts")


class AssessmentRecord(BaseModel):
    """Single assessment submission and score."""

    assessment_id: str
    student_id: str
    concept_ids: List[str] = Field(..., description="Concepts assessed")

    # Scores
    raw_score: float = Field(..., description="Points earned")
    max_score: float = Field(..., description="Total points possible")
    percentage: float = Field(..., ge=0.0, le=100.0)

    # Question-level data
    responses: Dict[str, Any] = Field(
        default_factory=dict, description="Question ID ' student response"
    )
    correct_answers: List[str] = Field(default_factory=list)
    incorrect_answers: List[str] = Field(default_factory=list)

    # Metadata
    assessment_type: str = Field(..., description="e.g., 'diagnostic', 'worksheet'")
    tier_level: Optional[TierLevel] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    graded_at: Optional[datetime] = None


class MasterySnapshot(BaseModel):
    """Current mastery across multiple concepts (for dashboards)."""

    student_id: str
    concepts: List[ConceptMastery]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassMasteryDistribution(BaseModel):
    """Aggregated mastery data for a class (Page 3 UI)."""

    class_id: str
    concept_id: str
    concept_name: str

    # Statistics
    mean_mastery: float = Field(..., ge=0.0, le=1.0)
    median_mastery: float = Field(..., ge=0.0, le=1.0)
    std_dev: float = Field(..., ge=0.0)

    # Distribution
    students_below_50: int
    students_50_to_75: int
    students_above_75: int

    last_updated: datetime = Field(default_factory=datetime.utcnow)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# TIER ASSIGNMENT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TierAssignment(BaseModel):
    """Student-to-tier mapping for differentiated worksheets."""

    student_id: str
    tier_level: TierLevel
    justification: str = Field(
        ...,
        description="Why this tier? e.g., 'Mastery at 45%, IEP accommodations'",
    )
    assigned_by: str = Field(..., description="'engine' or 'teacher'")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class TierDistribution(BaseModel):
    """How students are distributed across tiers (Page 2 UI)."""

    class_id: str
    tier_1_students: List[str] = Field(default_factory=list)
    tier_2_students: List[str] = Field(default_factory=list)
    tier_3_students: List[str] = Field(default_factory=list)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ADAPTIVE RECOMMENDATIONS SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class AdaptiveRecommendation(BaseModel):
    """Personalized next steps for a student (Engine 4 output)."""

    student_id: str
    recommendation_type: str = Field(
        ..., description="e.g., 'tier_change', 'intervention', 'enrichment'"
    )
    message: str = Field(
        ..., description="e.g., 'Ready for Tier 1 on next topic'"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# PREDICTION TRACKING SCHEMAS (Engine 6)
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class PredictionLog(BaseModel):
    """Stores predictions made by engines for accuracy tracking."""

    prediction_id: str
    engine_name: str = Field(..., description="e.g., 'engine_5_diagnostic'")
    student_id: str
    concept_id: str

    # Prediction
    predicted_mastery: float = Field(..., ge=0.0, le=1.0)
    predicted_tier: Optional[TierLevel] = None

    # Actual outcome (populated by Grader)
    actual_mastery: Optional[float] = Field(None, ge=0.0, le=1.0)
    actual_score: Optional[float] = None

    # Accuracy metrics
    error: Optional[float] = Field(
        None, description="Predicted - Actual (for regression)"
    )

    predicted_at: datetime = Field(default_factory=datetime.utcnow)
    outcome_recorded_at: Optional[datetime] = None


class AccuracyMetrics(BaseModel):
    """Aggregated accuracy statistics (Engine 6 output)."""

    engine_name: str
    timeframe_days: int
    num_predictions: int

    # Metrics
    rmse: float = Field(..., description="Root Mean Squared Error")
    mae: float = Field(..., description="Mean Absolute Error")
    correlation: float = Field(..., ge=-1.0, le=1.0)

    # Insights
    overestimation_bias: float = Field(
        ..., description="Positive = overestimates, negative = underestimates"
    )
    worst_concepts: List[str] = Field(
        default_factory=list, description="Concepts with highest error"
    )

    generated_at: datetime = Field(default_factory=datetime.utcnow)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# BULK IMPORT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class BulkImportRow(BaseModel):
    """Single row from CSV upload (Page 5 UI)."""

    student_name: str
    grade_level: GradeLevel
    reading_level: Optional[ReadingLevel] = ReadingLevel.PROFICIENT
    iep_status: bool = Field(False, description="Parsed from Yes/No")
    primary_disability: Optional[DisabilityCategory] = None


class BulkImportResult(BaseModel):
    """Result of CSV upload operation."""

    total_rows: int
    successful_imports: int
    failed_rows: List[int] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    created_student_ids: List[str] = Field(default_factory=list)
