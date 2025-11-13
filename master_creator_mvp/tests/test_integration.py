"""
Integration Tests for Full Pipeline

Tests the complete Master Creator v3 pipeline end-to-end.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# PIPELINE INTEGRATION TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


@pytest.mark.integration
@pytest.mark.slow
class TestFullPipeline:
    """Test complete pipeline: Engine 1 -> 5 -> 2 -> 3."""

    @patch("anthropic.Anthropic")
    @patch("src.student_model.interface.StudentModelInterface")
    def test_synchronous_pipeline_complete_flow(
        self, mock_student_model, mock_anthropic, mock_lesson_input, test_config
    ):
        """Test synchronous pipeline with all stages."""
        from src.orchestration.pipeline import MasterCreatorPipeline

        # Mock Claude API responses
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Mock lesson response
        lesson_response = MagicMock()
        lesson_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "sections": [
                            {
                                "section_name": "Opening / Hook",
                                "duration_minutes": 5,
                                "content": "Test content",
                            },
                            {
                                "section_name": "Learning Objectives",
                                "duration_minutes": 2,
                                "content": "Test objective",
                            },
                        ],
                        "citations": [],
                        "timestamp": "2025-01-01T00:00:00",
                    }
                )
            )
        ]
        lesson_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        # Mock diagnostic questions response
        diagnostic_response = MagicMock()
        diagnostic_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "questions": [
                            {
                                "question_id": "q1",
                                "question_text": "Test question",
                                "question_type": "multiple_choice",
                                "concept_id": "test_concept",
                                "difficulty_level": "medium",
                                "correct_answer": "A",
                                "options": ["A", "B", "C", "D"],
                            }
                        ]
                    }
                )
            )
        ]
        diagnostic_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        # Mock worksheet responses (3 calls for 3 tiers)
        worksheet_response = MagicMock()
        worksheet_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "questions": [
                            {
                                "number": 1,
                                "question_type": "multiple_choice",
                                "question_text": "Test worksheet question",
                                "scaffolding": ["Test scaffolding"],
                                "correct_answer": "A",
                            }
                        ]
                    }
                )
            )
        ]
        worksheet_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        # Set up mock to return different responses
        mock_client.messages.create.side_effect = [
            lesson_response,
            diagnostic_response,
            worksheet_response,
            worksheet_response,
            worksheet_response,
        ]

        # Mock Student Model responses
        mock_sm_instance = mock_student_model.return_value

        # Mock get_class_students
        mock_sm_instance.get_class_students.return_value = [
            MagicMock(
                student_id=f"student_{i:03d}",
                student_name=f"Student {i}",
                has_iep=(i % 3 == 0),
                reading_level=MagicMock(value="grade_level"),
            )
            for i in range(1, 19)
        ]

        # Mock get_class_roster
        mock_sm_instance.get_class_roster.return_value = MagicMock(
            class_id="class_test_001",
            class_name="Test Class",
            total_students=18,
        )

        # Mock retrieve_concept_mastery
        mock_sm_instance.retrieve_concept_mastery.return_value = [
            MagicMock(
                concept_id="test_concept",
                mastery_probability=0.5,
                p_learn=0.3,
                p_guess=0.25,
                p_slip=0.1,
                num_observations=0,
            )
        ]

        # Mock get_student_profile
        mock_sm_instance.get_student_profile.return_value = MagicMock(
            student_id="student_001",
            student_name="Test Student",
            has_iep=False,
        )

        # Mock get_iep_accommodations
        mock_sm_instance.get_iep_accommodations.return_value = None

        # Create pipeline
        pipeline = MasterCreatorPipeline()

        # Run pipeline (skip unit plan, adaptive, feedback)
        from src.orchestration.pipeline import PipelineInput

        input_params = PipelineInput(
            lesson_topic="Photosynthesis",
            grade_level="9",
            subject="Science",
            class_id="class_test_001",
            duration_minutes=45,
            standards=["NGSS-HS-LS1-5"],
            concept_ids=["photosynthesis_process"],
            num_questions_per_concept=3,
        )

        result = pipeline.run(input_params)

        # Assertions
        assert result.status == "success"
        assert result.lesson is not None
        assert result.diagnostic is not None
        assert result.worksheets is not None
        assert result.modified_worksheets is not None
        assert result.total_cost > 0
        assert len(result.errors) == 0

        # Verify lesson structure
        assert result.lesson.lesson_id is not None
        assert len(result.lesson.sections) >= 2

        # Verify diagnostic structure
        assert result.diagnostic.diagnostic_id is not None
        assert len(result.diagnostic.questions) > 0

        # Verify worksheets structure
        assert result.worksheets.worksheet_id is not None
        assert result.worksheets.tier_1 is not None
        assert result.worksheets.tier_2 is not None
        assert result.worksheets.tier_3 is not None

        # Verify IEP modifications
        assert result.modified_worksheets.modified_worksheet_id is not None

    def test_state_initialization(self):
        """Test LangGraph state initialization."""
        from src.orchestration.state_management import initialize_pipeline_state

        state = initialize_pipeline_state(
            lesson_topic="Photosynthesis",
            grade_level="9",
            subject="Science",
            class_id="class_test_001",
            concept_ids=["photosynthesis_process"],
        )

        # Verify state structure
        assert state["pipeline_id"] is not None
        assert state["execution_status"] == "in_progress"
        assert state["lesson_topic"] == "Photosynthesis"
        assert state["grade_level"] == "9"
        assert state["concept_ids"] == ["photosynthesis_process"]
        assert state["total_cost"] == 0.0
        assert state["errors"] == []
        assert state["warnings"] == []


@pytest.mark.integration
class TestEngineIntegration:
    """Test integration between engines."""

    @patch("anthropic.Anthropic")
    @patch("src.student_model.interface.StudentModelInterface")
    def test_engine_1_to_engine_5_integration(self, mock_student_model, mock_anthropic):
        """Test Engine 1 output feeds into Engine 5."""
        from src.engines.engine_1_lesson_architect import LessonArchitect
        from src.engines.engine_5_diagnostic import DiagnosticEngine

        # Mock Claude
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Lesson response
        lesson_response = MagicMock()
        lesson_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "sections": [
                            {
                                "section_name": "Learning Objectives",
                                "duration_minutes": 2,
                                "content": "Students will explain photosynthesis",
                            }
                        ],
                        "citations": [],
                        "timestamp": "2025-01-01",
                    }
                )
            )
        ]
        lesson_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        # Diagnostic response
        diagnostic_response = MagicMock()
        diagnostic_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "questions": [
                            {
                                "question_id": "q1",
                                "question_text": "Test",
                                "question_type": "multiple_choice",
                                "concept_id": "test",
                                "difficulty_level": "medium",
                                "correct_answer": "A",
                                "options": ["A"],
                            }
                        ]
                    }
                )
            )
        ]
        diagnostic_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        mock_client.messages.create.side_effect = [lesson_response, diagnostic_response]

        # Mock Student Model
        mock_sm_instance = mock_student_model.return_value
        mock_sm_instance.get_class_students.return_value = []
        mock_sm_instance.get_class_roster.return_value = MagicMock(total_students=0)
        mock_sm_instance.retrieve_concept_mastery.return_value = []

        # Generate lesson
        engine_1 = LessonArchitect()
        lesson = engine_1.generate(
            topic="Photosynthesis",
            grade_level="9",
            subject="Science",
            duration_minutes=45,
        )

        # Extract objectives
        objectives = []
        for section in lesson.sections:
            if section.section_name == "Learning Objectives":
                objectives.append(section.content)

        # Generate diagnostic using lesson objectives
        engine_5 = DiagnosticEngine()
        diagnostic = engine_5.generate(
            lesson_objectives=objectives,
            concept_ids=["photosynthesis_process"],
            class_id="class_test_001",
            num_questions_per_concept=1,
            grade_level="9",
            subject="Science",
        )

        # Verify integration
        assert len(objectives) > 0
        assert diagnostic.diagnostic_id is not None
        assert len(diagnostic.questions) > 0


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# COST TRACKING TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


@pytest.mark.integration
class TestCostTracking:
    """Test cost tracking across pipeline."""

    @patch("anthropic.Anthropic")
    @patch("src.student_model.interface.StudentModelInterface")
    def test_cost_accumulation(self, mock_student_model, mock_anthropic):
        """Test that costs accumulate correctly across engines."""
        from src.engines.engine_1_lesson_architect import LessonArchitect

        # Mock Claude
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        response = MagicMock()
        response.content = [MagicMock(text=json.dumps({"sections": [], "citations": [], "timestamp": "2025-01-01"}))]
        response.usage = MagicMock(input_tokens=1000, output_tokens=2000)

        mock_client.messages.create.return_value = response

        engine = LessonArchitect()

        # Generate lesson
        lesson = engine.generate(
            topic="Test",
            grade_level="9",
            subject="Science",
        )

        # Get cost summary
        cost_summary = engine.get_cost_summary()

        # Verify cost calculation
        assert cost_summary["input_tokens"] == 1000
        assert cost_summary["output_tokens"] == 2000
        assert cost_summary["total_cost"] > 0

        # Approximate cost check (~$3/M input, ~$15/M output)
        expected_cost = (1000 / 1_000_000 * 3) + (2000 / 1_000_000 * 15)
        assert abs(cost_summary["total_cost"] - expected_cost) < 0.001


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ERROR HANDLING TESTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in pipeline."""

    @patch("anthropic.Anthropic")
    @patch("src.student_model.interface.StudentModelInterface")
    def test_pipeline_handles_engine_failure(self, mock_student_model, mock_anthropic):
        """Test that pipeline handles engine failures gracefully."""
        from src.orchestration.pipeline import MasterCreatorPipeline, PipelineInput

        # Mock Claude to raise exception
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        pipeline = MasterCreatorPipeline()

        input_params = PipelineInput(
            lesson_topic="Test",
            grade_level="9",
            subject="Science",
            class_id="test",
            concept_ids=["test"],
            num_questions_per_concept=1,
        )

        result = pipeline.run(input_params)

        # Verify error is captured
        assert result.status == "failure"
        assert len(result.errors) > 0
        assert "API Error" in str(result.errors)
