"""
Import Cold Start Student Profiles into Database

Loads the generated student profiles and populates the database
with students, IEP records, and initial mastery estimates.

Usage:
    python scripts/import_cold_start_data.py [--file path/to/students.json]
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from student_model.interface import StudentModelInterface
from student_model.schemas import (
    StudentProfileCreate,
    GradeLevel,
    ReadingLevel,
    DisabilityCategory,
    AccommodationType,
    IEPCreate,
    AccommodationCreate,
    ConceptMasteryCreate,
)


def map_disability_category(category_str: str) -> DisabilityCategory:
    """Map string to DisabilityCategory enum."""
    mapping = {
        "LEARNING_DISABILITY": DisabilityCategory.LEARNING_DISABILITY,
        "ADHD": DisabilityCategory.ADHD,
        "AUTISM": DisabilityCategory.AUTISM,
        "EMOTIONAL_DISTURBANCE": DisabilityCategory.EMOTIONAL_DISTURBANCE,
        "SPEECH_LANGUAGE": DisabilityCategory.SPEECH_LANGUAGE,
        "INTELLECTUAL_DISABILITY": DisabilityCategory.INTELLECTUAL_DISABILITY,
        "OTHER": DisabilityCategory.OTHER,
    }
    return mapping.get(category_str, DisabilityCategory.OTHER)


def map_accommodation_type(type_str: str) -> AccommodationType:
    """Map string to AccommodationType enum."""
    mapping = {
        "EXTENDED_TIME": AccommodationType.EXTENDED_TIME,
        "TEXT_TO_SPEECH": AccommodationType.TEXT_TO_SPEECH,
        "GRAPHIC_ORGANIZERS": AccommodationType.GRAPHIC_ORGANIZERS,
        "SENTENCE_FRAMES": AccommodationType.SENTENCE_FRAMES,
        "WORD_BANK": AccommodationType.WORD_BANK,
        "VISUAL_SUPPORTS": AccommodationType.VISUAL_SUPPORTS,
        "CALCULATOR": AccommodationType.CALCULATOR,
        "REDUCED_QUESTIONS": AccommodationType.REDUCED_QUESTIONS,
        "AUDIO_RECORDINGS": AccommodationType.AUDIO_RECORDINGS,
        "MOVEMENT_BREAKS": AccommodationType.MOVEMENT_BREAKS,
        "PREFERENTIAL_SEATING": AccommodationType.PREFERENTIAL_SEATING,
        "SCRIBE": AccommodationType.SCRIBE,
    }
    return mapping.get(type_str, AccommodationType.EXTENDED_TIME)


def map_reading_level(level_str: str) -> ReadingLevel:
    """Map string to ReadingLevel enum."""
    mapping = {
        "above_grade_level": ReadingLevel.PROFICIENT,
        "grade_level": ReadingLevel.BASIC,
        "below_grade_level": ReadingLevel.BELOW_BASIC,
    }
    return mapping.get(level_str, ReadingLevel.BASIC)


def import_student_profiles(json_file_path: str, dry_run: bool = False):
    """
    Import student profiles from JSON file into database.

    Args:
        json_file_path: Path to JSON file with student data
        dry_run: If True, print what would be imported without actually importing
    """
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 60)
    print("Importing Cold Start Student Profiles")
    print("=" * 60)
    print(f"File: {json_file_path}")
    print(f"Generated: {data.get('generated_at')}")
    print(f"Class: {data.get('class_name')}")
    print(f"Total Students: {data.get('total_students')}")
    print(f"Dry Run: {dry_run}")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No data will be written to database")
        print()

    # Initialize Student Model Interface
    student_model = StudentModelInterface()

    imported_count = 0
    iep_count = 0
    mastery_records = 0

    for i, profile in enumerate(data["students"], 1):
        print(f"[{i}/{len(data['students'])}] Importing: {profile['student_name']}")

        if dry_run:
            print(f"  Would create student profile:")
            print(f"    - Grade: {profile['grade_level']}")
            print(f"    - IEP: {profile['has_iep']}")
            print(f"    - Reading Level: {profile['reading_level']}")

            if profile['has_iep']:
                print(f"    - Disability: {profile['primary_disability']}")
                print(f"    - Accommodations: {len(profile['accommodations'])}")

            print(f"    - Initial Mastery Estimates: {len(profile['initial_mastery'])}")
            imported_count += 1
            if profile['has_iep']:
                iep_count += 1
            mastery_records += len(profile['initial_mastery'])
            continue

        try:
            # Create student profile
            student_data = StudentProfileCreate(
                student_name=profile["student_name"],
                grade_level=GradeLevel(profile["grade_level"]),
                has_iep=profile["has_iep"],
                reading_level=map_reading_level(profile["reading_level"]),
            )

            # Create student in database
            student_id = student_model.create_student_profile(student_data)
            print(f"  ✅ Created student: {student_id}")
            imported_count += 1

            # Create IEP if applicable
            if profile["has_iep"] and "accommodations" in profile:
                accommodations = [
                    AccommodationCreate(
                        accommodation_type=map_accommodation_type(acc["type"]),
                        description=acc["description"],
                        details=acc.get("details", ""),
                    )
                    for acc in profile["accommodations"]
                ]

                iep_data = IEPCreate(
                    student_id=student_id,
                    primary_disability=map_disability_category(
                        profile["disability_category"]
                    ),
                    accommodations=accommodations,
                )

                iep_id = student_model.create_iep(iep_data)
                print(f"  ✅ Created IEP with {len(accommodations)} accommodations")
                iep_count += 1

            # Create initial mastery estimates
            if "initial_mastery" in profile:
                for concept_id, mastery_prob in profile["initial_mastery"].items():
                    mastery_data = ConceptMasteryCreate(
                        student_id=student_id,
                        concept_id=concept_id,
                        mastery_probability=mastery_prob,
                        p_learn=0.3,  # Default BKT parameters
                        p_guess=0.25,
                        p_slip=0.1,
                        num_observations=0,  # Cold start - no observations yet
                    )

                    student_model.create_mastery_estimate(mastery_data)
                    mastery_records += 1

                print(
                    f"  ✅ Created {len(profile['initial_mastery'])} mastery estimates"
                )

        except Exception as e:
            print(f"  ❌ Error importing {profile['student_name']}: {str(e)}")
            continue

    print()
    print("=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"Students Imported: {imported_count}/{len(data['students'])}")
    print(f"IEP Records Created: {iep_count}")
    print(f"Mastery Estimates Created: {mastery_records}")
    print()

    if dry_run:
        print("🔍 This was a DRY RUN - no data was written")
        print("Run without --dry-run to actually import data")
    else:
        print("✨ Import complete!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import cold start student profiles into database"
    )
    parser.add_argument(
        "--file",
        default="/home/user/testrepo/master_creator_mvp/data/cold_start_students.json",
        help="Path to JSON file with student data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be imported without actually importing",
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ Error: File not found: {args.file}")
        print(f"\nGenerate cold start data first:")
        print(f"  python scripts/generate_cold_start_data.py")
        sys.exit(1)

    try:
        import_student_profiles(args.file, dry_run=args.dry_run)
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
