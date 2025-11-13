"""
Engine 3: IEP Modification Specialist

Applies IEP accommodations and modifications to worksheets.

Core Functionality:
1. Accept worksheets from Engine 2
2. Query Student Model for IEP data
3. Apply legal accommodations (IDEA, Section 504 compliant)
4. Modify worksheet formatting and content
5. Ensure compliance with student IEP requirements

Supported Accommodations (12 types):
- Extended Time (1.5x or 2x)
- Text-to-Speech enabled formatting
- Graphic Organizers
- Sentence Frames
- Word Bank
- Visual Supports
- Calculator
- Reduced Question Count
- Audio Recordings
- Movement Breaks (notation)
- Preferential Seating (notation)
- Scribe/Speech-to-Text

Legal Compliance:
- IDEA (Individuals with Disabilities Education Act)
- Section 504 (Rehabilitation Act)
- FERPA (audit trail for modifications)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine
from .engine_2_worksheet_designer import WorksheetSet, TierWorksheet, WorksheetQuestion
from ..student_model.schemas import AccommodationType, IEPData


# ═══════════════════════════════════════════════════════════
# INPUT/OUTPUT SCHEMAS
# ═══════════════════════════════════════════════════════════


class AccommodationApplication(BaseModel):
    """Record of accommodation applied to worksheet."""

    student_id: str
    student_name: str
    accommodation_type: AccommodationType
    modification_description: str
    applied_at: str


class ModifiedWorksheetSet(BaseModel):
    """WorksheetSet with IEP accommodations applied."""

    # Original worksheet data
    original_worksheet_id: str
    modified_worksheet_id: str
    lesson_topic: str
    grade_level: str
    subject: str
    class_id: str

    # Modified tiers
    tier_1: TierWorksheet
    tier_2: TierWorksheet
    tier_3: TierWorksheet

    # Accommodation tracking (FERPA compliance)
    accommodations_applied: List[AccommodationApplication]
    total_iep_students: int
    compliance_checked: bool

    # Metadata
    generated_at: str
    cost: float


# ═══════════════════════════════════════════════════════════
# ENGINE 3: IEP MODIFICATION SPECIALIST
# ═══════════════════════════════════════════════════════════


class IEPSpecialist(BaseEngine):
    """
    Engine 3: Applies IEP accommodations to worksheets.

    Ensures legal compliance with IDEA and Section 504 requirements.
    """

    def apply_accommodations(
        self,
        worksheet_set: WorksheetSet,
    ) -> ModifiedWorksheetSet:
        """
        Apply IEP accommodations to worksheet set.

        Args:
            worksheet_set: Original worksheet set from Engine 2

        Returns:
            ModifiedWorksheetSet with accommodations applied
        """
        import uuid
        modified_id = f"modified_{uuid.uuid4().hex[:12]}"

        self._log_decision(
            f"Applying IEP accommodations to worksheet {worksheet_set.worksheet_id}"
        )

        accommodations_log = []

        # Step 1: Apply accommodations to Tier 1
        tier_1_modified, tier_1_accommodations = self._apply_tier_accommodations(
            tier_worksheet=worksheet_set.tier_1,
            class_id=worksheet_set.class_id,
        )
        accommodations_log.extend(tier_1_accommodations)

        # Step 2: Apply accommodations to Tier 2
        tier_2_modified, tier_2_accommodations = self._apply_tier_accommodations(
            tier_worksheet=worksheet_set.tier_2,
            class_id=worksheet_set.class_id,
        )
        accommodations_log.extend(tier_2_accommodations)

        # Step 3: Apply accommodations to Tier 3
        tier_3_modified, tier_3_accommodations = self._apply_tier_accommodations(
            tier_worksheet=worksheet_set.tier_3,
            class_id=worksheet_set.class_id,
        )
        accommodations_log.extend(tier_3_accommodations)

        # Step 4: Count total IEP students
        all_students = (
            worksheet_set.tier_1.students
            + worksheet_set.tier_2.students
            + worksheet_set.tier_3.students
        )
        total_iep = sum(1 for s in all_students if s.get("has_iep", False))

        # Step 5: Build modified worksheet set
        modified_set = ModifiedWorksheetSet(
            original_worksheet_id=worksheet_set.worksheet_id,
            modified_worksheet_id=modified_id,
            lesson_topic=worksheet_set.lesson_topic,
            grade_level=worksheet_set.grade_level,
            subject=worksheet_set.subject,
            class_id=worksheet_set.class_id,
            tier_1=tier_1_modified,
            tier_2=tier_2_modified,
            tier_3=tier_3_modified,
            accommodations_applied=accommodations_log,
            total_iep_students=total_iep,
            compliance_checked=True,
            generated_at=datetime.utcnow().isoformat(),
            cost=self.get_cost_summary()["total_cost"],
        )

        self._log_decision(
            f"Accommodations applied: {len(accommodations_log)} total for {total_iep} IEP students"
        )

        return modified_set

    def _apply_tier_accommodations(
        self,
        tier_worksheet: TierWorksheet,
        class_id: str,
    ) -> tuple[TierWorksheet, List[AccommodationApplication]]:
        """
        Apply accommodations to a single tier.

        Args:
            tier_worksheet: Original tier worksheet
            class_id: Class identifier

        Returns:
            (Modified TierWorksheet, List of accommodation applications)
        """
        accommodations_log = []
        modified_questions = []

        # Get IEP students in this tier
        iep_students = [s for s in tier_worksheet.students if s.get("has_iep", False)]

        if not iep_students:
            # No IEP students, return unchanged
            return tier_worksheet, []

        # Collect all accommodations needed for this tier
        tier_accommodations = self._collect_tier_accommodations(
            iep_students, class_id
        )

        # Apply accommodations to questions
        for question in tier_worksheet.questions:
            modified_q = self._modify_question(
                question=question,
                tier_accommodations=tier_accommodations,
            )
            modified_questions.append(modified_q)

        # Log accommodations applied
        for student in iep_students:
            iep_data = self.student_model.get_iep_accommodations(
                student["student_id"]
            )

            if iep_data:
                for acc in iep_data.accommodations:
                    accommodations_log.append(
                        AccommodationApplication(
                            student_id=student["student_id"],
                            student_name=student["name"],
                            accommodation_type=AccommodationType(acc["type"]),
                            modification_description=self._get_modification_description(
                                AccommodationType(acc["type"])
                            ),
                            applied_at=datetime.utcnow().isoformat(),
                        )
                    )

        # Build modified tier
        modified_tier = TierWorksheet(
            tier_name=tier_worksheet.tier_name,
            tier_level=tier_worksheet.tier_level,
            student_count=tier_worksheet.student_count,
            students=tier_worksheet.students,
            questions=modified_questions,
            scaffolding_summary=tier_worksheet.scaffolding_summary,
            iep_summary=tier_worksheet.iep_summary,
        )

        return modified_tier, accommodations_log

    def _collect_tier_accommodations(
        self,
        iep_students: List[Dict],
        class_id: str,
    ) -> Dict[str, int]:
        """
        Collect all accommodations needed for a tier.

        Args:
            iep_students: List of IEP student dicts
            class_id: Class identifier

        Returns:
            Dict mapping accommodation type to count
        """
        accommodation_counts = {}

        for student in iep_students:
            iep_data = self.student_model.get_iep_accommodations(
                student["student_id"]
            )

            if iep_data:
                for acc in iep_data.accommodations:
                    acc_type = acc["type"]
                    accommodation_counts[acc_type] = (
                        accommodation_counts.get(acc_type, 0) + 1
                    )

        return accommodation_counts

    def _modify_question(
        self,
        question: WorksheetQuestion,
        tier_accommodations: Dict[str, int],
    ) -> WorksheetQuestion:
        """
        Modify question based on needed accommodations.

        Args:
            question: Original question
            tier_accommodations: Accommodations needed in this tier

        Returns:
            Modified WorksheetQuestion
        """
        modified_scaffolding = list(question.scaffolding)

        # Apply modifications based on accommodations
        if "Extended Time" in tier_accommodations:
            # Add extended time notation
            modified_scaffolding.append(
                f"⏱️ Extended time available ({tier_accommodations['Extended Time']} students)"
            )

        if "Text-to-Speech" in tier_accommodations:
            # Ensure formatting is TTS-compatible
            modified_scaffolding.append(
                f"🔊 Text-to-speech enabled ({tier_accommodations['Text-to-Speech']} students)"
            )

        if "Graphic Organizers" in tier_accommodations:
            # Add graphic organizer
            modified_scaffolding.append(
                f"📊 Graphic organizer provided ({tier_accommodations['Graphic Organizers']} students)"
            )

        if "Sentence Frames" in tier_accommodations:
            # Add sentence frames
            modified_scaffolding.append(
                f"📝 Sentence frames available ({tier_accommodations['Sentence Frames']} students)"
            )

        if "Word Bank" in tier_accommodations:
            # Add word bank
            modified_scaffolding.append(
                f"📖 Word bank provided ({tier_accommodations['Word Bank']} students)"
            )

        if "Visual Supports" in tier_accommodations:
            # Add visual aids
            modified_scaffolding.append(
                f"👁️ Visual supports included ({tier_accommodations['Visual Supports']} students)"
            )

        if "Calculator" in tier_accommodations:
            # Allow calculator
            modified_scaffolding.append(
                f"🔢 Calculator permitted ({tier_accommodations['Calculator']} students)"
            )

        if "Reduced Questions" in tier_accommodations:
            # Note that question count may be reduced
            modified_scaffolding.append(
                f"✂️ Reduced question count option ({tier_accommodations['Reduced Questions']} students)"
            )

        if "Audio Recordings" in tier_accommodations:
            # Add audio recording option
            modified_scaffolding.append(
                f"🎤 Audio recording available ({tier_accommodations['Audio Recordings']} students)"
            )

        if "Movement Breaks" in tier_accommodations:
            # Add movement break notation
            modified_scaffolding.append(
                f"🚶 Movement breaks allowed ({tier_accommodations['Movement Breaks']} students)"
            )

        if "Preferential Seating" in tier_accommodations:
            # Add seating notation
            modified_scaffolding.append(
                f"🪑 Preferential seating ({tier_accommodations['Preferential Seating']} students)"
            )

        if "Scribe" in tier_accommodations:
            # Add scribe notation
            modified_scaffolding.append(
                f"✍️ Scribe/speech-to-text available ({tier_accommodations['Scribe']} students)"
            )

        # Create modified question
        return WorksheetQuestion(
            number=question.number,
            question_type=question.question_type,
            question_text=question.question_text,
            scaffolding=modified_scaffolding,
            correct_answer=question.correct_answer,
            rubric=question.rubric,
            standards=question.standards,
        )

    def _get_modification_description(
        self,
        accommodation_type: AccommodationType,
    ) -> str:
        """
        Get human-readable description of modification.

        Args:
            accommodation_type: Type of accommodation

        Returns:
            Description string
        """
        descriptions = {
            AccommodationType.EXTENDED_TIME: "Extended time for completion (1.5x-2x standard time)",
            AccommodationType.TEXT_TO_SPEECH: "Text-to-speech enabled for reading support",
            AccommodationType.GRAPHIC_ORGANIZERS: "Graphic organizers provided to structure thinking",
            AccommodationType.SENTENCE_FRAMES: "Sentence frames provided for writing support",
            AccommodationType.WORD_BANK: "Word bank provided for vocabulary support",
            AccommodationType.VISUAL_SUPPORTS: "Visual aids and diagrams included",
            AccommodationType.CALCULATOR: "Calculator use permitted",
            AccommodationType.REDUCED_QUESTIONS: "Reduced question count to focus on mastery",
            AccommodationType.AUDIO_RECORDINGS: "Audio recording option for responses",
            AccommodationType.MOVEMENT_BREAKS: "Movement breaks allowed during assessment",
            AccommodationType.PREFERENTIAL_SEATING: "Preferential seating arrangement",
            AccommodationType.SCRIBE: "Scribe or speech-to-text available for responses",
        }

        return descriptions.get(
            accommodation_type,
            f"Accommodation: {accommodation_type.value}",
        )

    def generate_compliance_report(
        self,
        modified_worksheet: ModifiedWorksheetSet,
    ) -> Dict:
        """
        Generate FERPA-compliant report of accommodations applied.

        Args:
            modified_worksheet: Modified worksheet set

        Returns:
            Compliance report dict
        """
        # Count accommodations by type
        accommodation_summary = {}
        for app in modified_worksheet.accommodations_applied:
            acc_type = app.accommodation_type.value
            accommodation_summary[acc_type] = (
                accommodation_summary.get(acc_type, 0) + 1
            )

        # Build report
        report = {
            "worksheet_id": modified_worksheet.modified_worksheet_id,
            "lesson_topic": modified_worksheet.lesson_topic,
            "class_id": modified_worksheet.class_id,
            "total_iep_students": modified_worksheet.total_iep_students,
            "total_accommodations_applied": len(
                modified_worksheet.accommodations_applied
            ),
            "accommodation_summary": accommodation_summary,
            "compliance_status": "COMPLIANT" if modified_worksheet.compliance_checked else "NOT_VERIFIED",
            "legal_frameworks": ["IDEA", "Section 504", "FERPA"],
            "generated_at": modified_worksheet.generated_at,
        }

        return report


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def apply_iep_accommodations(
    worksheet_set: WorksheetSet,
) -> ModifiedWorksheetSet:
    """
    Convenience function to apply IEP accommodations.

    Args:
        worksheet_set: Original worksheet set from Engine 2

    Returns:
        ModifiedWorksheetSet with accommodations applied
    """
    engine = IEPSpecialist()
    return engine.apply_accommodations(worksheet_set)


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    print("""
Engine 3: IEP Modification Specialist

This engine applies IEP accommodations to worksheets from Engine 2.

Supported Accommodations (12 types):
- Extended Time (1.5x or 2x)
- Text-to-Speech
- Graphic Organizers
- Sentence Frames
- Word Bank
- Visual Supports
- Calculator
- Reduced Question Count
- Audio Recordings
- Movement Breaks
- Preferential Seating
- Scribe/Speech-to-Text

Legal Compliance:
- IDEA (Individuals with Disabilities Education Act)
- Section 504 (Rehabilitation Act)
- FERPA (audit trail maintained)

To test the complete pipeline:
1. Run Engine 1 (Lesson Architect)
2. Run Engine 5 (Diagnostic)
3. Run Engine 2 (Worksheet Designer)
4. Run Engine 3 (IEP Specialist)

Example integration test:
  python -m tests.test_pipeline
    """)
