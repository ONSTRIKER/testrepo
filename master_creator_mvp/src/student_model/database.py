"""
PostgreSQL database models and connection management for Student Model.

This module defines SQLAlchemy ORM models for:
- Student profiles and demographics
- IEP data and accommodations
- Assessment history and scores
- Concept mastery with Bayesian parameters
- Prediction tracking for Engine 6
- Class/roster management

All engines access student data through StudentModelInterface, which queries these tables.
"""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import QueuePool

from .schemas import (
    AccommodationType,
    DisabilityCategory,
    GradeLevel,
    ReadingLevel,
    Subject,
    TierLevel,
)

# Base class for all models
Base = declarative_base()

# Database connection configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./master_creator.db"  # Default to SQLite for local development
)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# DATABASE CONNECTION
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def get_engine(pool_size: int = 20, max_overflow: int = 40):
    """
    Create SQLAlchemy engine with connection pooling.

    Args:
        pool_size: Number of permanent connections (default 20)
        max_overflow: Max temporary connections beyond pool_size (default 40)

    Returns:
        SQLAlchemy Engine instance
    """
    # SQLite doesn't support connection pooling the same way as PostgreSQL
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},  # Allow multi-threading
            echo=False,  # Set True for SQL logging
        )
    else:
        # PostgreSQL or other databases
        return create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            echo=False,  # Set True for SQL logging
        )


def get_session_maker(engine=None):
    """Create sessionmaker bound to engine."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Global session maker (initialized on first import)
SessionLocal = get_session_maker()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# TABLE MODELS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class ClassModel(Base):
    """Class/roster information."""

    __tablename__ = "classes"

    class_id = Column(String(50), primary_key=True, index=True)
    class_name = Column(String(100), nullable=False)  # e.g., "Period 3 Biology"
    grade_level = Column(SQLEnum(GradeLevel), nullable=False)
    subject = Column(SQLEnum(Subject), nullable=False)
    teacher_id = Column(String(50), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    students = relationship("StudentModel", back_populates="class_obj")


class StudentModel(Base):
    """Core student profile data."""

    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True, index=True)
    student_name = Column(String(100), nullable=False, index=True)
    grade_level = Column(SQLEnum(GradeLevel), nullable=False)
    class_id = Column(String(50), ForeignKey("classes.class_id"), nullable=False, index=True)

    # Academic background
    reading_level = Column(SQLEnum(ReadingLevel), default=ReadingLevel.PROFICIENT)
    learning_preferences = Column(
        JSON, default=list
    )  # List of LearningPreference enum values

    # Special education flags
    has_iep = Column(Boolean, default=False, index=True)
    primary_disability = Column(SQLEnum(DisabilityCategory), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_obj = relationship("ClassModel", back_populates="students")
    iep_data = relationship("IEPModel", back_populates="student", uselist=False)
    assessments = relationship("AssessmentModel", back_populates="student")
    mastery_data = relationship("MasteryModel", back_populates="student")
    predictions = relationship("PredictionModel", back_populates="student")


class IEPModel(Base):
    """IEP (Individual Education Program) data."""

    __tablename__ = "iep_data"

    iep_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        String(50), ForeignKey("students.student_id"), nullable=False, unique=True, index=True
    )

    # Disability information
    primary_disability = Column(SQLEnum(DisabilityCategory), nullable=False)
    secondary_disabilities = Column(JSON, default=list)  # List of DisabilityCategory values

    # Accommodations (stored as JSON array)
    # Format: [{"type": "Extended Time", "enabled": true, "settings": {"multiplier": 1.5}}, ...]
    accommodations = Column(JSON, default=list)

    # Modifications (stored as JSON dict)
    # Format: {"alternate_grading": true, "reduced_content": false, ...}
    modifications = Column(JSON, default=dict)

    # IEP goals (list of strings)
    goals = Column(JSON, default=list)

    # Review dates
    last_reviewed = Column(DateTime, nullable=False)
    next_review_due = Column(DateTime, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("StudentModel", back_populates="iep_data")


class MasteryModel(Base):
    """Concept mastery tracking with Bayesian Knowledge Tracing parameters."""

    __tablename__ = "mastery_data"

    mastery_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False, index=True)
    concept_id = Column(String(100), nullable=False, index=True)  # e.g., "photosynthesis_process"
    concept_name = Column(String(200), nullable=False)  # Human-readable

    # Bayesian Knowledge Tracing parameters (Engine 5)
    mastery_probability = Column(Float, nullable=False)  # P(mastery) - primary estimate
    p_learn = Column(Float, default=0.3)  # Probability of learning
    p_guess = Column(Float, default=0.25)  # Probability of guessing correctly
    p_slip = Column(Float, default=0.1)  # Probability of slipping (error)

    # Tracking
    num_observations = Column(Integer, default=0)  # Number of assessment attempts
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("StudentModel", back_populates="mastery_data")

    # Unique constraint: one mastery record per student-concept pair
    __table_args__ = (
        {"mysql_engine": "InnoDB", "extend_existing": True},
    )


class AssessmentModel(Base):
    """Assessment submission and scoring records."""

    __tablename__ = "assessments"

    assessment_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False, index=True)

    # Assessment metadata
    assessment_type = Column(String(50), nullable=False)  # e.g., "diagnostic", "worksheet", "quiz"
    concept_ids = Column(JSON, nullable=False)  # List of concept IDs assessed

    # Scores
    raw_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)

    # Question-level data (stored as JSON)
    # Format: {"q1": "answer text", "q2": "B", ...}
    responses = Column(JSON, default=dict)
    correct_answers = Column(JSON, default=list)  # List of question IDs
    incorrect_answers = Column(JSON, default=list)  # List of question IDs

    # Tier assignment (if applicable)
    tier_level = Column(SQLEnum(TierLevel), nullable=True)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("StudentModel", back_populates="assessments")


class PredictionModel(Base):
    """Prediction tracking for Engine 6 accuracy monitoring."""

    __tablename__ = "predictions"

    prediction_id = Column(String(50), primary_key=True, index=True)
    engine_name = Column(String(50), nullable=False, index=True)  # e.g., "engine_5_diagnostic"
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False, index=True)
    concept_id = Column(String(100), nullable=False, index=True)

    # Prediction
    predicted_mastery = Column(Float, nullable=False)
    predicted_tier = Column(SQLEnum(TierLevel), nullable=True)

    # Actual outcome (populated by Grader)
    actual_mastery = Column(Float, nullable=True)
    actual_score = Column(Float, nullable=True)

    # Error tracking
    error = Column(Float, nullable=True)  # predicted - actual

    # Timestamps
    predicted_at = Column(DateTime, default=datetime.utcnow)
    outcome_recorded_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("StudentModel", back_populates="predictions")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# DATABASE INITIALIZATION
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def create_tables(engine=None):
    """
    Create all tables in the database.

    Args:
        engine: SQLAlchemy engine (creates new one if None)
    """
    if engine is None:
        engine = get_engine()

    Base.metadata.create_all(bind=engine)
    print(" All database tables created successfully!")


def drop_tables(engine=None):
    """
    Drop all tables from the database (USE WITH CAUTION!).

    Args:
        engine: SQLAlchemy engine (creates new one if None)
    """
    if engine is None:
        engine = get_engine()

    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped!")


def reset_database(engine=None):
    """
    Drop and recreate all tables (DESTROYS ALL DATA!).

    Args:
        engine: SQLAlchemy engine (creates new one if None)
    """
    if engine is None:
        engine = get_engine()

    print("�  Resetting database (this will delete all data)...")
    drop_tables(engine)
    create_tables(engine)
    print(" Database reset complete!")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# UTILITY FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def get_table_counts(session):
    """
    Get row counts for all tables (useful for verification).

    Args:
        session: SQLAlchemy session

    Returns:
        Dict mapping table names to row counts
    """
    counts = {
        "classes": session.query(ClassModel).count(),
        "students": session.query(StudentModel).count(),
        "iep_data": session.query(IEPModel).count(),
        "mastery_data": session.query(MasteryModel).count(),
        "assessments": session.query(AssessmentModel).count(),
        "predictions": session.query(PredictionModel).count(),
    }
    return counts


def print_database_stats(session):
    """Print summary statistics for the database."""
    counts = get_table_counts(session)

    print("\n" + "=" * 50)
    print("=� DATABASE STATISTICS")
    print("=" * 50)
    for table, count in counts.items():
        print(f"  {table:20s}: {count:5d} rows")
    print("=" * 50 + "\n")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLI COMMANDS (for manual database management)
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            """
Usage: python -m src.student_model.database <command>

Commands:
  init     - Create all database tables
  reset    - Drop and recreate all tables (DESTROYS DATA!)
  stats    - Show database statistics
  drop     - Drop all tables (DESTROYS DATA!)

Example:
  python -m src.student_model.database init
        """
        )
        sys.exit(1)

    command = sys.argv[1]
    engine = get_engine()

    if command == "init":
        create_tables(engine)
    elif command == "reset":
        confirm = input("�  This will DELETE ALL DATA. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            reset_database(engine)
        else:
            print("Cancelled.")
    elif command == "stats":
        session = SessionLocal()
        try:
            print_database_stats(session)
        finally:
            session.close()
    elif command == "drop":
        confirm = input("�  This will DROP ALL TABLES. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            drop_tables(engine)
        else:
            print("Cancelled.")
    else:
        print(f"L Unknown command: {command}")
        sys.exit(1)
