"""
Pytest Configuration and Fixtures

Shared fixtures for all tests.
"""

import pytest
import os
from typing import Dict, List

# Mock environment variables for testing
os.environ["ANTHROPIC_API_KEY"] = "test_key_mock_do_not_use"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"


# ═══════════════════════════════════════════════════════════
# MOCK DATA FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_student_data():
    """Mock student data for testing."""
    return {
        "student_id": "student_test_001",
        "student_name": "Test Student",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
    }


@pytest.fixture
def mock_iep_student_data():
    """Mock student with IEP."""
    return {
        "student_id": "student_test_002",
        "student_name": "IEP Test Student",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "primary_disability": "Learning Disability",
        "accommodations": [
            {"type": "Extended Time", "details": "1.5x on assessments"},
            {"type": "Text-to-Speech", "details": "All reading materials"},
        ],
    }


@pytest.fixture
def mock_class_roster():
    """Mock class roster with 18 students."""
    return {
        "class_id": "class_test_001",
        "class_name": "Test Biology 101",
        "total_students": 18,
        "students": [
            {"student_id": f"student_{i:03d}", "student_name": f"Student {i}", "has_iep": i % 3 == 0}
            for i in range(1, 19)
        ],
    }


@pytest.fixture
def mock_concept_mastery():
    """Mock concept mastery data."""
    return {
        "student_id": "student_test_001",
        "concept_id": "photosynthesis_process",
        "mastery_probability": 0.75,
        "p_learn": 0.3,
        "p_guess": 0.25,
        "p_slip": 0.1,
        "num_observations": 5,
    }


@pytest.fixture
def mock_lesson_input():
    """Mock lesson generation input."""
    return {
        "topic": "Photosynthesis",
        "grade_level": "9",
        "subject": "Science",
        "duration_minutes": 45,
        "standards": ["NGSS-HS-LS1-5"],
        "class_id": "class_test_001",
    }


@pytest.fixture
def mock_diagnostic_input():
    """Mock diagnostic input."""
    return {
        "lesson_objectives": [
            "Students will explain the process of photosynthesis",
            "Students will identify reactants and products",
        ],
        "concept_ids": ["photosynthesis_process"],
        "class_id": "class_test_001",
        "num_questions_per_concept": 3,
        "grade_level": "9",
        "subject": "Science",
    }


@pytest.fixture
def mock_worksheet_input():
    """Mock worksheet generation input."""
    return {
        "lesson_topic": "Photosynthesis",
        "learning_objective": "Students will explain the process of photosynthesis",
        "grade_level": "9",
        "subject": "Science",
        "class_id": "class_test_001",
        "diagnostic_results": {
            "diagnostic_id": "diag_test_001",
            "student_estimates": [
                {
                    "student_id": f"student_{i:03d}",
                    "concept_id": "photosynthesis_process",
                    "mastery_probability": 0.85 if i <= 6 else (0.65 if i <= 14 else 0.35),
                    "recommended_tier": "tier_1" if i <= 6 else ("tier_2" if i <= 14 else "tier_3"),
                }
                for i in range(1, 19)
            ],
        },
        "standards": ["NGSS-HS-LS1-5"],
    }


@pytest.fixture
def mock_assessment_questions():
    """Mock assessment questions."""
    return [
        {
            "question_id": "q1",
            "question_text": "What is the primary function of chlorophyll?",
            "question_type": "multiple_choice",
            "concept_id": "photosynthesis_process",
            "points_possible": 1.0,
            "correct_answer": "B",
        },
        {
            "question_id": "q2",
            "question_text": "Explain the process of photosynthesis in your own words.",
            "question_type": "constructed_response",
            "concept_id": "photosynthesis_process",
            "points_possible": 4.0,
            "rubric": {
                "rubric_id": "rubric_q2",
                "rubric_type": "analytic",
                "total_points": 4.0,
                "criteria": [
                    {
                        "criterion_name": "Content Accuracy",
                        "description": "Accurate explanation of photosynthesis",
                        "points_possible": 2.0,
                        "levels": {
                            "2": "Fully accurate",
                            "1": "Partially accurate",
                            "0": "Inaccurate",
                        },
                    },
                    {
                        "criterion_name": "Clarity",
                        "description": "Clear and organized explanation",
                        "points_possible": 2.0,
                        "levels": {
                            "2": "Very clear",
                            "1": "Somewhat clear",
                            "0": "Unclear",
                        },
                    },
                ],
            },
        },
    ]


@pytest.fixture
def mock_assessment_responses():
    """Mock student assessment responses."""
    return [
        {"question_id": "q1", "answer": "B"},
        {
            "question_id": "q2",
            "answer": "Photosynthesis is the process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
        },
    ]


# ═══════════════════════════════════════════════════════════
# MOCK ENGINE RESPONSES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_lesson_output():
    """Mock lesson output from Engine 1."""
    return {
        "lesson_id": "lesson_test_001",
        "topic": "Photosynthesis",
        "grade_level": "9",
        "subject": "Science",
        "sections": [
            {"section_name": "Opening / Hook", "duration_minutes": 5, "content": "Show time-lapse of plant growth"},
            {
                "section_name": "Learning Objectives",
                "duration_minutes": 2,
                "content": "Students will explain the process of photosynthesis",
            },
            {"section_name": "Standards Alignment", "duration_minutes": 1, "content": "NGSS-HS-LS1-5"},
            {"section_name": "Direct Instruction", "duration_minutes": 15, "content": "..."},
            {"section_name": "Guided Practice", "duration_minutes": 10, "content": "..."},
            {"section_name": "Independent Practice", "duration_minutes": 10, "content": "..."},
            {"section_name": "Assessment", "duration_minutes": 5, "content": "..."},
            {"section_name": "Differentiation Strategies", "duration_minutes": 0, "content": "..."},
            {"section_name": "Materials & Resources", "duration_minutes": 0, "content": "..."},
            {"section_name": "Closure", "duration_minutes": 5, "content": "..."},
        ],
    }


@pytest.fixture
def mock_diagnostic_output():
    """Mock diagnostic output from Engine 5."""
    return {
        "diagnostic_id": "diagnostic_test_001",
        "class_id": "class_test_001",
        "concept_ids": ["photosynthesis_process"],
        "questions": [
            {
                "question_id": "q1",
                "question_text": "What gas do plants release during photosynthesis?",
                "question_type": "multiple_choice",
                "concept_id": "photosynthesis_process",
                "difficulty_level": "easy",
                "correct_answer": "B",
                "options": ["A) Carbon dioxide", "B) Oxygen", "C) Nitrogen", "D) Hydrogen"],
            }
        ],
        "student_estimates": [],
        "tier_distribution": {"tier_1": 6, "tier_2": 8, "tier_3": 4},
    }


# ═══════════════════════════════════════════════════════════
# TEST CONFIGURATION
# ═══════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "skip_api_calls": True,  # Skip actual API calls in tests
        "use_mock_data": True,  # Use mock data instead of real database
        "log_level": "INFO",
    }


# ═══════════════════════════════════════════════════════════
# PYTEST CONFIGURATION
# ═══════════════════════════════════════════════════════════


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "api: mark test as API test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on file location
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        if "test_pipeline" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
