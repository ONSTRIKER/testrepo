"""
Generate Synthetic Student Profiles for Cold Start

Creates 18 diverse student profiles with:
- Mix of IEP and non-IEP students (6 IEP, 12 non-IEP)
- Different grade levels (9-12)
- Varied reading levels
- Initial mastery estimates for common science concepts
- Realistic accommodations for IEP students

Usage:
    python scripts/generate_cold_start_data.py
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any


def generate_student_profiles() -> List[Dict[str, Any]]:
    """
    Generate 18 synthetic student profiles.

    Distribution:
    - 12 non-IEP students (Tier 1: 4, Tier 2: 5, Tier 3: 3)
    - 6 IEP students (representing ~33% of class, typical range 10-40%)
    - Mix of grade levels (primarily 9th grade for biology)
    - Varied reading levels
    """

    profiles = []

    # ═══════════════════════════════════════════════════════════
    # TIER 1 STUDENTS (High Achievers) - 4 students
    # ═══════════════════════════════════════════════════════════

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Emma Chen",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "above_grade_level",
        "tier_classification": "tier_1",
        "initial_mastery": {
            "photosynthesis_process": 0.85,
            "cellular_respiration": 0.80,
            "cell_structure": 0.90,
            "dna_replication": 0.75,
            "ecosystems": 0.88,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "kinesthetic"],
            "engagement_level": "high",
        },
        "notes": "Advanced student, participates actively, asks probing questions"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Marcus Washington",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "above_grade_level",
        "tier_classification": "tier_1",
        "initial_mastery": {
            "photosynthesis_process": 0.82,
            "cellular_respiration": 0.85,
            "cell_structure": 0.88,
            "dna_replication": 0.80,
            "ecosystems": 0.83,
        },
        "learning_preferences": {
            "preferred_modalities": ["reading", "visual"],
            "engagement_level": "high",
        },
        "notes": "Strong analytical skills, enjoys lab work"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Sophia Rodriguez",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_1",
        "initial_mastery": {
            "photosynthesis_process": 0.78,
            "cellular_respiration": 0.82,
            "cell_structure": 0.85,
            "dna_replication": 0.77,
            "ecosystems": 0.80,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "auditory"],
            "engagement_level": "high",
        },
        "notes": "Excellent at connecting concepts, collaborative learner"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "James Kim",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_1",
        "initial_mastery": {
            "photosynthesis_process": 0.80,
            "cellular_respiration": 0.78,
            "cell_structure": 0.83,
            "dna_replication": 0.81,
            "ecosystems": 0.79,
        },
        "learning_preferences": {
            "preferred_modalities": ["kinesthetic", "visual"],
            "engagement_level": "high",
        },
        "notes": "Hands-on learner, excels in lab activities"
    })

    # ═══════════════════════════════════════════════════════════
    # TIER 2 STUDENTS (On-Grade Level) - 5 students
    # ═══════════════════════════════════════════════════════════

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Olivia Martinez",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_2",
        "initial_mastery": {
            "photosynthesis_process": 0.65,
            "cellular_respiration": 0.62,
            "cell_structure": 0.68,
            "dna_replication": 0.60,
            "ecosystems": 0.67,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "auditory"],
            "engagement_level": "medium",
        },
        "notes": "Benefits from graphic organizers and visual aids"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Liam Johnson",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_2",
        "initial_mastery": {
            "photosynthesis_process": 0.63,
            "cellular_respiration": 0.65,
            "cell_structure": 0.64,
            "dna_replication": 0.62,
            "ecosystems": 0.66,
        },
        "learning_preferences": {
            "preferred_modalities": ["auditory", "kinesthetic"],
            "engagement_level": "medium",
        },
        "notes": "Steady learner, benefits from repetition and practice"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Ava Patel",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_2",
        "initial_mastery": {
            "photosynthesis_process": 0.60,
            "cellular_respiration": 0.63,
            "cell_structure": 0.61,
            "dna_replication": 0.58,
            "ecosystems": 0.64,
        },
        "learning_preferences": {
            "preferred_modalities": ["reading", "visual"],
            "engagement_level": "medium",
        },
        "notes": "Strong work ethic, sometimes needs extra time"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Noah Thompson",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_2",
        "initial_mastery": {
            "photosynthesis_process": 0.58,
            "cellular_respiration": 0.60,
            "cell_structure": 0.62,
            "dna_replication": 0.55,
            "ecosystems": 0.61,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "kinesthetic"],
            "engagement_level": "medium",
        },
        "notes": "Strong conceptual understanding, reading challenges"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Isabella Garcia",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "grade_level",
        "tier_classification": "tier_2",
        "initial_mastery": {
            "photosynthesis_process": 0.64,
            "cellular_respiration": 0.61,
            "cell_structure": 0.66,
            "dna_replication": 0.63,
            "ecosystems": 0.62,
        },
        "learning_preferences": {
            "preferred_modalities": ["auditory", "visual"],
            "engagement_level": "medium",
        },
        "notes": "Collaborative learner, works well in groups"
    })

    # ═══════════════════════════════════════════════════════════
    # TIER 3 STUDENTS (Intensive Support) - 3 non-IEP students
    # ═══════════════════════════════════════════════════════════

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Ethan Brown",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "initial_mastery": {
            "photosynthesis_process": 0.40,
            "cellular_respiration": 0.38,
            "cell_structure": 0.42,
            "dna_replication": 0.35,
            "ecosystems": 0.41,
        },
        "learning_preferences": {
            "preferred_modalities": ["kinesthetic", "visual"],
            "engagement_level": "medium",
        },
        "notes": "Needs significant scaffolding, benefits from sentence frames"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Mia Davis",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "initial_mastery": {
            "photosynthesis_process": 0.38,
            "cellular_respiration": 0.40,
            "cell_structure": 0.37,
            "dna_replication": 0.36,
            "ecosystems": 0.39,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "auditory"],
            "engagement_level": "low",
        },
        "notes": "English learner, benefits from visual supports and word banks"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Alexander Wilson",
        "grade_level": "9",
        "has_iep": False,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "initial_mastery": {
            "photosynthesis_process": 0.42,
            "cellular_respiration": 0.39,
            "cell_structure": 0.44,
            "dna_replication": 0.38,
            "ecosystems": 0.40,
        },
        "learning_preferences": {
            "preferred_modalities": ["kinesthetic", "auditory"],
            "engagement_level": "medium",
        },
        "notes": "Benefits from hands-on activities and reduced question sets"
    })

    # ═══════════════════════════════════════════════════════════
    # IEP STUDENTS - 6 students (various disabilities)
    # ═══════════════════════════════════════════════════════════

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Daniel Lee",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_2",
        "primary_disability": "Specific Learning Disability",
        "disability_category": "LEARNING_DISABILITY",
        "accommodations": [
            {
                "type": "EXTENDED_TIME",
                "description": "1.5x time on all assessments",
                "details": "Student processes information more slowly"
            },
            {
                "type": "TEXT_TO_SPEECH",
                "description": "Text-to-speech for all reading materials",
                "details": "Dyslexia - struggles with decoding"
            },
            {
                "type": "GRAPHIC_ORGANIZERS",
                "description": "Graphic organizers for all note-taking",
                "details": "Helps organize information visually"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.55,
            "cellular_respiration": 0.52,
            "cell_structure": 0.58,
            "dna_replication": 0.50,
            "ecosystems": 0.56,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "auditory"],
            "engagement_level": "medium",
        },
        "notes": "Strong conceptual understanding when given proper supports"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Aiden Taylor",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "grade_level",
        "tier_classification": "tier_2",
        "primary_disability": "ADHD",
        "disability_category": "ADHD",
        "accommodations": [
            {
                "type": "MOVEMENT_BREAKS",
                "description": "Movement breaks every 20 minutes",
                "details": "Helps maintain focus and attention"
            },
            {
                "type": "PREFERENTIAL_SEATING",
                "description": "Preferential seating near teacher",
                "details": "Minimizes distractions"
            },
            {
                "type": "REDUCED_QUESTIONS",
                "description": "Reduced number of questions on assignments",
                "details": "Maintains quality while reducing overwhelm"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.68,
            "cellular_respiration": 0.65,
            "cell_structure": 0.70,
            "dna_replication": 0.63,
            "ecosystems": 0.67,
        },
        "learning_preferences": {
            "preferred_modalities": ["kinesthetic", "visual"],
            "engagement_level": "medium",
        },
        "notes": "Bright student, benefits from structured environment and movement"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Charlotte Anderson",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "primary_disability": "Autism Spectrum Disorder",
        "disability_category": "AUTISM",
        "accommodations": [
            {
                "type": "VISUAL_SUPPORTS",
                "description": "Visual schedules and supports",
                "details": "Reduces anxiety about transitions and expectations"
            },
            {
                "type": "SENTENCE_FRAMES",
                "description": "Sentence frames for written responses",
                "details": "Provides structure for expression"
            },
            {
                "type": "PREFERENTIAL_SEATING",
                "description": "Quiet area away from high-traffic zones",
                "details": "Reduces sensory overload"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.48,
            "cellular_respiration": 0.45,
            "cell_structure": 0.50,
            "dna_replication": 0.43,
            "ecosystems": 0.47,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "reading"],
            "engagement_level": "medium",
        },
        "notes": "Detail-oriented, strong memorization, benefits from structured routines"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Ryan Martinez",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "primary_disability": "Specific Learning Disability - Dysgraphia",
        "disability_category": "LEARNING_DISABILITY",
        "accommodations": [
            {
                "type": "SCRIBE",
                "description": "Scribe for extended written responses",
                "details": "Physical act of writing is extremely difficult"
            },
            {
                "type": "EXTENDED_TIME",
                "description": "Double time on written assessments",
                "details": "Writing takes significantly longer"
            },
            {
                "type": "WORD_BANK",
                "description": "Word banks for fill-in-blank questions",
                "details": "Reduces spelling/writing demands"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.60,
            "cellular_respiration": 0.58,
            "cell_structure": 0.62,
            "dna_replication": 0.55,
            "ecosystems": 0.59,
        },
        "learning_preferences": {
            "preferred_modalities": ["auditory", "kinesthetic"],
            "engagement_level": "medium",
        },
        "notes": "Strong verbal skills, written output does not reflect understanding"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Grace Johnson",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_3",
        "primary_disability": "Speech-Language Impairment",
        "disability_category": "SPEECH_LANGUAGE",
        "accommodations": [
            {
                "type": "AUDIO_RECORDINGS",
                "description": "Audio recordings of lectures",
                "details": "Can review material at own pace"
            },
            {
                "type": "EXTENDED_TIME",
                "description": "Extended time for oral presentations",
                "details": "Needs extra time to formulate verbal responses"
            },
            {
                "type": "SENTENCE_FRAMES",
                "description": "Sentence frames for verbal and written responses",
                "details": "Provides language structure support"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.52,
            "cellular_respiration": 0.50,
            "cell_structure": 0.54,
            "dna_replication": 0.48,
            "ecosystems": 0.53,
        },
        "learning_preferences": {
            "preferred_modalities": ["visual", "reading"],
            "engagement_level": "medium",
        },
        "notes": "Strong comprehension, expressive language challenges"
    })

    profiles.append({
        "student_id": f"student_{uuid.uuid4().hex[:12]}",
        "student_name": "Jackson White",
        "grade_level": "9",
        "has_iep": True,
        "reading_level": "below_grade_level",
        "tier_classification": "tier_2",
        "primary_disability": "Emotional Disturbance - Anxiety Disorder",
        "disability_category": "EMOTIONAL_DISTURBANCE",
        "accommodations": [
            {
                "type": "EXTENDED_TIME",
                "description": "Extended time on assessments",
                "details": "Anxiety can slow processing during tests"
            },
            {
                "type": "MOVEMENT_BREAKS",
                "description": "Breaks as needed to manage anxiety",
                "details": "Can leave room for brief breaks to self-regulate"
            },
            {
                "type": "PREFERENTIAL_SEATING",
                "description": "Seat near door for easy exit",
                "details": "Reduces anxiety about being 'trapped'"
            }
        ],
        "initial_mastery": {
            "photosynthesis_process": 0.70,
            "cellular_respiration": 0.68,
            "cell_structure": 0.72,
            "dna_replication": 0.66,
            "ecosystems": 0.69,
        },
        "learning_preferences": {
            "preferred_modalities": ["reading", "visual"],
            "engagement_level": "medium",
        },
        "notes": "Capable student, anxiety interferes with performance on assessments"
    })

    return profiles


def save_profiles_to_json(profiles: List[Dict[str, Any]], output_path: str = "data/cold_start_students.json"):
    """Save profiles to JSON file."""
    import os

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Add metadata
    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_students": len(profiles),
        "class_id": "class_bio_101_cold_start",
        "class_name": "Biology 101 - Period 3",
        "grade_level": "9",
        "subject": "Science",
        "teacher_name": "Ms. Johnson",
        "students": profiles,
        "statistics": {
            "total": len(profiles),
            "non_iep": sum(1 for p in profiles if not p["has_iep"]),
            "iep": sum(1 for p in profiles if p["has_iep"]),
            "tier_1": sum(1 for p in profiles if p.get("tier_classification") == "tier_1"),
            "tier_2": sum(1 for p in profiles if p.get("tier_classification") == "tier_2"),
            "tier_3": sum(1 for p in profiles if p.get("tier_classification") == "tier_3"),
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(profiles)} student profiles")
    print(f"📁 Saved to: {output_path}")
    print(f"\nClass Statistics:")
    print(f"  Total Students: {data['statistics']['total']}")
    print(f"  Non-IEP: {data['statistics']['non_iep']}")
    print(f"  IEP: {data['statistics']['iep']} ({data['statistics']['iep']/data['statistics']['total']*100:.1f}%)")
    print(f"  Tier 1: {data['statistics']['tier_1']}")
    print(f"  Tier 2: {data['statistics']['tier_2']}")
    print(f"  Tier 3: {data['statistics']['tier_3']}")

    return data


def main():
    """Generate and save cold start student profiles."""
    print("=" * 60)
    print("Generating Cold Start Student Profiles")
    print("=" * 60)
    print()

    # Generate profiles
    profiles = generate_student_profiles()

    # Save to JSON
    output_path = "/home/user/testrepo/master_creator_mvp/data/cold_start_students.json"
    data = save_profiles_to_json(profiles, output_path)

    print(f"\n✨ Cold start data generation complete!")
    print(f"\nTo use this data:")
    print(f"  1. Import into database: python scripts/import_cold_start_data.py")
    print(f"  2. Or load directly in tests: json.load(open('{output_path}'))")


if __name__ == "__main__":
    main()
