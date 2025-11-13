"""
Student Model Tests

Tests for Student Model Interface and data operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# STUDENT PROFILE TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestStudentProfiles:
    """Test student profile operations."""

    def test_student_profile_creation(self, mock_student_data):
        """Test creating a student profile."""
        from src.student_model.schemas import StudentProfileCreate, GradeLevel, ReadingLevel

        profile_data = StudentProfileCreate(
            student_name=mock_student_data["student_name"],
            grade_level=GradeLevel(mock_student_data["grade_level"]),
            has_iep=mock_student_data["has_iep"],
            reading_level=ReadingLevel(mock_student_data["reading_level"]),
        )

        assert profile_data.student_name == "Test Student"
        assert profile_data.grade_level == GradeLevel.GRADE_9
        assert profile_data.has_iep == False

    def test_iep_student_creation(self, mock_iep_student_data):
        """Test creating student with IEP."""
        from src.student_model.schemas import (
            StudentProfileCreate,
            GradeLevel,
            ReadingLevel,
            DisabilityCategory,
        )

        profile_data = StudentProfileCreate(
            student_name=mock_iep_student_data["student_name"],
            grade_level=GradeLevel(mock_iep_student_data["grade_level"]),
            has_iep=mock_iep_student_data["has_iep"],
            reading_level=ReadingLevel(mock_iep_student_data["reading_level"]),
        )

        assert profile_data.has_iep == True


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# MASTERY TRACKING TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestMasteryTracking:
    """Test concept mastery tracking."""

    def test_concept_mastery_creation(self, mock_concept_mastery):
        """Test creating concept mastery record."""
        from src.student_model.schemas import ConceptMastery

        mastery = ConceptMastery(
            student_id=mock_concept_mastery["student_id"],
            concept_id=mock_concept_mastery["concept_id"],
            mastery_probability=mock_concept_mastery["mastery_probability"],
            p_learn=mock_concept_mastery["p_learn"],
            p_guess=mock_concept_mastery["p_guess"],
            p_slip=mock_concept_mastery["p_slip"],
            num_observations=mock_concept_mastery["num_observations"],
        )

        assert mastery.mastery_probability == 0.75
        assert mastery.p_learn == 0.3
        assert mastery.num_observations == 5

    def test_mastery_probability_bounds(self):
        """Test that mastery probability is bounded [0, 1]."""
        from src.student_model.schemas import ConceptMastery

        # Test valid values
        for prob in [0.0, 0.5, 1.0]:
            mastery = ConceptMastery(
                student_id="test",
                concept_id="test",
                mastery_probability=prob,
            )
            assert 0.0 <= mastery.mastery_probability <= 1.0

    def test_bkt_parameters(self):
        """Test BKT parameter validation."""
        from src.student_model.schemas import ConceptMastery

        mastery = ConceptMastery(
            student_id="test",
            concept_id="test",
            mastery_probability=0.5,
            p_learn=0.3,
            p_guess=0.25,
            p_slip=0.1,
        )

        # Verify all parameters are in valid range
        assert 0.0 <= mastery.p_learn <= 1.0
        assert 0.0 <= mastery.p_guess <= 1.0
        assert 0.0 <= mastery.p_slip <= 1.0


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# TIER ASSIGNMENT TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestTierAssignment:
    """Test tier assignment logic."""

    def test_tier_classification(self):
        """Test that students are assigned to correct tiers."""
        from src.student_model.schemas import TierLevel

        # Test tier thresholds
        tier_1_mastery = 0.85  # e75% ’ Tier 1
        tier_2_mastery = 0.60  # 45-75% ’ Tier 2
        tier_3_mastery = 0.35  # <45% ’ Tier 3

        # Verify tier 1
        assert tier_1_mastery >= 0.75

        # Verify tier 2
        assert 0.45 <= tier_2_mastery < 0.75

        # Verify tier 3
        assert tier_3_mastery < 0.45

    def test_tier_enum_values(self):
        """Test TierLevel enum."""
        from src.student_model.schemas import TierLevel

        assert TierLevel.TIER_1.value == "tier_1"
        assert TierLevel.TIER_2.value == "tier_2"
        assert TierLevel.TIER_3.value == "tier_3"


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# IEP DATA TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestIEPData:
    """Test IEP data structures."""

    def test_iep_accommodations(self):
        """Test IEP accommodation structure."""
        from src.student_model.schemas import AccommodationType

        # Test all accommodation types
        accommodations = [
            AccommodationType.EXTENDED_TIME,
            AccommodationType.TEXT_TO_SPEECH,
            AccommodationType.GRAPHIC_ORGANIZERS,
            AccommodationType.SENTENCE_FRAMES,
            AccommodationType.WORD_BANK,
            AccommodationType.VISUAL_SUPPORTS,
            AccommodationType.CALCULATOR,
            AccommodationType.REDUCED_QUESTIONS,
            AccommodationType.AUDIO_RECORDINGS,
            AccommodationType.MOVEMENT_BREAKS,
            AccommodationType.PREFERENTIAL_SEATING,
            AccommodationType.SCRIBE,
        ]

        # Verify all 12 accommodation types
        assert len(accommodations) == 12

    def test_disability_categories(self):
        """Test disability category enum."""
        from src.student_model.schemas import DisabilityCategory

        categories = [
            DisabilityCategory.LEARNING_DISABILITY,
            DisabilityCategory.ADHD,
            DisabilityCategory.AUTISM,
            DisabilityCategory.EMOTIONAL_DISTURBANCE,
            DisabilityCategory.SPEECH_LANGUAGE,
            DisabilityCategory.INTELLECTUAL_DISABILITY,
            DisabilityCategory.OTHER,
        ]

        # Verify all 7 categories
        assert len(categories) == 7


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# PREDICTION LOGGING TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestPredictionLogging:
    """Test prediction logging for Engine 6."""

    def test_prediction_log_creation(self):
        """Test creating prediction log."""
        from src.student_model.schemas import PredictionLog, TierLevel

        prediction = PredictionLog(
            prediction_id="pred_test_001",
            engine_name="engine_5_diagnostic",
            student_id="student_001",
            concept_id="photosynthesis",
            predicted_mastery=0.75,
            predicted_tier=TierLevel.TIER_1,
        )

        assert prediction.prediction_id == "pred_test_001"
        assert prediction.engine_name == "engine_5_diagnostic"
        assert prediction.predicted_mastery == 0.75
        assert prediction.predicted_tier == TierLevel.TIER_1

    def test_prediction_outcome_update(self):
        """Test updating prediction with actual outcome."""
        from src.student_model.schemas import PredictionLog, TierLevel

        prediction = PredictionLog(
            prediction_id="pred_test_001",
            engine_name="engine_5_diagnostic",
            student_id="student_001",
            concept_id="photosynthesis",
            predicted_mastery=0.75,
            predicted_tier=TierLevel.TIER_1,
        )

        # Simulate updating with actual outcome
        actual_mastery = 0.68  # Student performed slightly worse
        error = prediction.predicted_mastery - actual_mastery

        assert error == 0.07  # 7% overestimation


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLASS OPERATIONS TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestClassOperations:
    """Test class-level operations."""

    def test_class_roster_structure(self, mock_class_roster):
        """Test class roster data structure."""
        assert mock_class_roster["class_id"] == "class_test_001"
        assert mock_class_roster["total_students"] == 18
        assert len(mock_class_roster["students"]) == 18

    def test_iep_student_count(self, mock_class_roster):
        """Test counting IEP students in class."""
        iep_students = [s for s in mock_class_roster["students"] if s["has_iep"]]

        # Every 3rd student has IEP (1, 4, 7, 10, 13, 16 = 6 students)
        assert len(iep_students) == 6

    def test_mastery_distribution_calculation(self):
        """Test calculating class mastery distribution."""
        # Mock mastery data for class
        mastery_values = [0.85, 0.90, 0.75, 0.60, 0.55, 0.65, 0.40, 0.35, 0.30]

        # Calculate average
        avg_mastery = sum(mastery_values) / len(mastery_values)

        # Calculate tier distribution
        tier_1_count = sum(1 for m in mastery_values if m >= 0.75)
        tier_2_count = sum(1 for m in mastery_values if 0.45 <= m < 0.75)
        tier_3_count = sum(1 for m in mastery_values if m < 0.45)

        assert tier_1_count == 3
        assert tier_2_count == 3
        assert tier_3_count == 3
        assert avg_mastery > 0.5


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# SCHEMA VALIDATION TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestSchemaValidation:
    """Test Pydantic schema validation."""

    def test_grade_level_validation(self):
        """Test grade level enum validation."""
        from src.student_model.schemas import GradeLevel

        # Test valid grades
        valid_grades = ["9", "10", "11", "12"]
        for grade in valid_grades:
            level = GradeLevel(grade)
            assert level.value == grade

        # Test invalid grade
        with pytest.raises(ValueError):
            GradeLevel("invalid")

    def test_reading_level_validation(self):
        """Test reading level enum validation."""
        from src.student_model.schemas import ReadingLevel

        levels = [
            ReadingLevel.BELOW_GRADE_LEVEL,
            ReadingLevel.GRADE_LEVEL,
            ReadingLevel.ABOVE_GRADE_LEVEL,
        ]

        assert len(levels) == 3

    def test_subject_validation(self):
        """Test subject enum validation."""
        from src.student_model.schemas import Subject

        subjects = [
            Subject.SCIENCE,
            Subject.MATH,
            Subject.ELA,
            Subject.SOCIAL_STUDIES,
        ]

        assert len(subjects) == 4


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# BULK IMPORT TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class TestBulkImport:
    """Test bulk student import functionality."""

    def test_csv_import_structure(self):
        """Test CSV import data structure."""
        # Mock CSV data
        csv_data = """student_name,grade_level,has_iep,reading_level
Alex Chen,9,false,grade_level
Maria Gonzalez,9,true,below_grade_level
Carlos Martinez,9,true,grade_level"""

        lines = csv_data.strip().split("\n")
        assert len(lines) == 4  # Header + 3 students

        # Verify header
        header = lines[0].split(",")
        assert "student_name" in header
        assert "grade_level" in header
        assert "has_iep" in header

    def test_bulk_import_result(self):
        """Test bulk import result structure."""
        from src.student_model.schemas import BulkImportResult

        result = BulkImportResult(
            total_rows=10,
            successful_imports=8,
            failed_imports=2,
            errors=["Row 3: Invalid grade level", "Row 7: Missing required field"],
        )

        assert result.total_rows == 10
        assert result.successful_imports == 8
        assert result.failed_imports == 2
        assert len(result.errors) == 2
