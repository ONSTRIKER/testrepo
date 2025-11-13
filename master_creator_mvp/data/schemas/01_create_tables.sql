-- Master Creator v3 MVP - Database Schema
-- PostgreSQL DDL for Student Model tables
--
-- This script creates all tables needed for the Student Model.
-- It will be automatically executed when PostgreSQL container starts.

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════
-- ENUMS - Define custom types
-- ═══════════════════════════════════════════════════════════

CREATE TYPE grade_level AS ENUM ('9', '10', '11', '12');

CREATE TYPE subject AS ENUM (
    'English Language Arts',
    'Mathematics',
    'Science',
    'Social Studies',
    'Elective'
);

CREATE TYPE reading_level AS ENUM (
    'Below Basic',
    'Basic',
    'Proficient',
    'Advanced'
);

CREATE TYPE disability_category AS ENUM (
    'Specific Learning Disability',
    'ADHD',
    'Autism Spectrum Disorder',
    'Speech/Language Impairment',
    'Intellectual Disability',
    'Emotional Disturbance',
    'Other Health Impairment',
    'None'
);

CREATE TYPE tier_level AS ENUM ('Tier 1', 'Tier 2', 'Tier 3');

-- ═══════════════════════════════════════════════════════════
-- TABLES
-- ═══════════════════════════════════════════════════════════

-- Classes/Rosters
CREATE TABLE classes (
    class_id VARCHAR(50) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    grade_level grade_level NOT NULL,
    subject subject NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_classes_teacher ON classes(teacher_id);

-- Students
CREATE TABLE students (
    student_id VARCHAR(50) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    grade_level grade_level NOT NULL,
    class_id VARCHAR(50) NOT NULL REFERENCES classes(class_id) ON DELETE CASCADE,
    reading_level reading_level DEFAULT 'Proficient',
    learning_preferences JSONB DEFAULT '[]'::jsonb,
    has_iep BOOLEAN DEFAULT FALSE,
    primary_disability disability_category,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_students_name ON students(student_name);
CREATE INDEX idx_students_iep ON students(has_iep);

-- IEP Data
CREATE TABLE iep_data (
    iep_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,
    primary_disability disability_category NOT NULL,
    secondary_disabilities JSONB DEFAULT '[]'::jsonb,
    accommodations JSONB DEFAULT '[]'::jsonb,
    modifications JSONB DEFAULT '{}'::jsonb,
    goals JSONB DEFAULT '[]'::jsonb,
    last_reviewed TIMESTAMP NOT NULL,
    next_review_due TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_iep_student ON iep_data(student_id);
CREATE INDEX idx_iep_review_due ON iep_data(next_review_due);

-- Mastery Data (Bayesian Knowledge Tracing)
CREATE TABLE mastery_data (
    mastery_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    concept_id VARCHAR(100) NOT NULL,
    concept_name VARCHAR(200) NOT NULL,
    mastery_probability FLOAT NOT NULL CHECK (mastery_probability >= 0 AND mastery_probability <= 1),
    p_learn FLOAT DEFAULT 0.3 CHECK (p_learn >= 0 AND p_learn <= 1),
    p_guess FLOAT DEFAULT 0.25 CHECK (p_guess >= 0 AND p_guess <= 1),
    p_slip FLOAT DEFAULT 0.1 CHECK (p_slip >= 0 AND p_slip <= 1),
    num_observations INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, concept_id)
);

CREATE INDEX idx_mastery_student ON mastery_data(student_id);
CREATE INDEX idx_mastery_concept ON mastery_data(concept_id);
CREATE INDEX idx_mastery_probability ON mastery_data(mastery_probability);

-- Assessments
CREATE TABLE assessments (
    assessment_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL,
    concept_ids JSONB NOT NULL,
    raw_score FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    percentage FLOAT NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    responses JSONB DEFAULT '{}'::jsonb,
    correct_answers JSONB DEFAULT '[]'::jsonb,
    incorrect_answers JSONB DEFAULT '[]'::jsonb,
    tier_level tier_level,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP
);

CREATE INDEX idx_assessments_student ON assessments(student_id);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
CREATE INDEX idx_assessments_submitted ON assessments(submitted_at);

-- Predictions (for Engine 6 accuracy tracking)
CREATE TABLE predictions (
    prediction_id VARCHAR(50) PRIMARY KEY,
    engine_name VARCHAR(50) NOT NULL,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    concept_id VARCHAR(100) NOT NULL,
    predicted_mastery FLOAT NOT NULL CHECK (predicted_mastery >= 0 AND predicted_mastery <= 1),
    predicted_tier tier_level,
    actual_mastery FLOAT CHECK (actual_mastery >= 0 AND actual_mastery <= 1),
    actual_score FLOAT,
    error FLOAT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outcome_recorded_at TIMESTAMP
);

CREATE INDEX idx_predictions_engine ON predictions(engine_name);
CREATE INDEX idx_predictions_student ON predictions(student_id);
CREATE INDEX idx_predictions_concept ON predictions(concept_id);
CREATE INDEX idx_predictions_timestamp ON predictions(predicted_at);

-- ═══════════════════════════════════════════════════════════
-- TRIGGERS - Auto-update timestamps
-- ═══════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_classes_updated_at BEFORE UPDATE ON classes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_iep_updated_at BEFORE UPDATE ON iep_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mastery_updated_at BEFORE UPDATE ON mastery_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════
-- COMMENTS - Documentation for tables and columns
-- ═══════════════════════════════════════════════════════════

COMMENT ON TABLE classes IS 'Class rosters for organizing students';
COMMENT ON TABLE students IS 'Core student profile data';
COMMENT ON TABLE iep_data IS 'Individual Education Program information (IDEA compliant)';
COMMENT ON TABLE mastery_data IS 'Concept mastery estimates using Bayesian Knowledge Tracing';
COMMENT ON TABLE assessments IS 'Assessment submissions and scoring records';
COMMENT ON TABLE predictions IS 'Prediction tracking for Engine 6 accuracy monitoring';

COMMENT ON COLUMN students.learning_preferences IS 'VARK learning modalities (JSON array)';
COMMENT ON COLUMN iep_data.accommodations IS 'List of IEP accommodations with settings (JSON)';
COMMENT ON COLUMN iep_data.modifications IS 'IEP modifications that alter standards (JSON)';
COMMENT ON COLUMN mastery_data.mastery_probability IS 'P(mastery) - Main BKT estimate';
COMMENT ON COLUMN mastery_data.p_learn IS 'Probability of learning (BKT parameter)';
COMMENT ON COLUMN mastery_data.p_guess IS 'Probability of guessing correctly (BKT parameter)';
COMMENT ON COLUMN mastery_data.p_slip IS 'Probability of slipping/error (BKT parameter)';

-- ═══════════════════════════════════════════════════════════
-- COMPLETION MESSAGE
-- ═══════════════════════════════════════════════════════════

DO $$
BEGIN
    RAISE NOTICE '✅ Master Creator v3 database schema created successfully!';
    RAISE NOTICE 'Tables: classes, students, iep_data, mastery_data, assessments, predictions';
END $$;
