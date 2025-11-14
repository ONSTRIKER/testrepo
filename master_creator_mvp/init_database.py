"""
Initialize the Master Creator MVP database.
Creates all necessary tables for the Student Model.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.student_model.database import Base, get_engine

print("=" * 60)
print("Master Creator MVP - Database Initialization")
print("=" * 60)
print()

try:
    # Create engine
    engine = get_engine()

    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    print("✓ Database tables created successfully!")
    print()
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    print()
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)

except Exception as e:
    print(f"✗ Error creating database: {e}")
    sys.exit(1)
