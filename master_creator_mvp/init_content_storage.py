#!/usr/bin/env python3
"""
Initialize content storage database tables.

This script creates all tables needed for storing generated educational content.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.student_model.database import get_engine, create_tables as create_student_tables
from src.content_storage.models import create_content_tables

def main():
    """Initialize all database tables."""
    print("=" * 60)
    print("Master Creator v3 MVP - Database Initialization")
    print("=" * 60)

    # Create engine
    engine = get_engine()
    print(f"\n📊 Database URL: {engine.url}")

    # Create student model tables (if not exists)
    print("\n1️⃣  Creating Student Model tables...")
    create_student_tables(engine)

    # Create content storage tables
    print("\n2️⃣  Creating Content Storage tables...")
    create_content_tables(engine)

    print("\n" + "=" * 60)
    print("✅ All database tables created successfully!")
    print("=" * 60)

    print("\nCreated tables:")
    print("  Student Model:")
    print("    - classes")
    print("    - students")
    print("    - iep_data")
    print("    - mastery_data")
    print("    - assessments")
    print("    - predictions")
    print("\n  Content Storage:")
    print("    - unit_plans")
    print("    - lessons")
    print("    - worksheets")
    print("    - iep_modifications")
    print("    - adaptive_plans")
    print("    - diagnostic_results")
    print("    - feedback_reports")
    print("    - graded_assessments")
    print("    - pipeline_executions")

    print("\n💡 Next steps:")
    print("  1. Load sample data: python load_sample_data.py")
    print("  2. Start backend: python run_server.py")
    print("  3. Start frontend: cd frontend && npm run dev")
    print()

if __name__ == "__main__":
    main()
