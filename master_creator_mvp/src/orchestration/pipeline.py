"""
Master Creator v3 MVP - Pipeline Orchestration

Orchestrates the complete lesson generation pipeline:
1. Engine 1: Lesson Architect (10-part lesson blueprint)
2. Engine 5: Diagnostic Engine (BKT mastery estimation)
3. Engine 2: Worksheet Designer (3-tier differentiation)
4. Engine 3: IEP Specialist (accommodation application)

This is the synchronous version. For async/LangGraph orchestration,
see langgraph_pipeline.py (TODO).
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..engines.engine_1_lesson_architect import LessonArchitect, LessonBlueprint
from ..engines.engine_5_diagnostic import DiagnosticEngine, DiagnosticResults
from ..engines.engine_2_worksheet_designer import WorksheetDesigner, WorksheetSet
from ..engines.engine_3_iep_specialist import IEPSpecialist, ModifiedWorksheetSet


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# PIPELINE INPUT/OUTPUT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class PipelineInput(BaseModel):
    """Input for complete pipeline."""

    # Lesson parameters
    lesson_topic: str
    grade_level: str
    subject: str
    class_id: str
    duration_minutes: int = 45
    standards: Optional[List[str]] = None

    # Diagnostic parameters
    concept_ids: List[str]  # Concepts to assess
    num_questions_per_concept: int = 3

    # Worksheet parameters
    num_questions_per_tier: Optional[Dict[str, int]] = None


class PipelineOutput(BaseModel):
    """Output from complete pipeline."""

    # Pipeline metadata
    pipeline_id: str
    status: str  # "success", "partial_failure", "failure"
    started_at: str
    completed_at: str
    total_duration_seconds: float

    # Stage outputs
    lesson: Optional[LessonBlueprint] = None
    diagnostic: Optional[DiagnosticResults] = None
    worksheets: Optional[WorksheetSet] = None
    modified_worksheets: Optional[ModifiedWorksheetSet] = None

    # Cost tracking
    total_cost: float
    cost_breakdown: Dict[str, float]

    # Error tracking
    errors: List[str]
    warnings: List[str]


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# PIPELINE ORCHESTRATOR
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class MasterCreatorPipeline:
    """
    Orchestrates the complete Master Creator v3 pipeline.

    Runs all 4 engines sequentially and aggregates results.
    """

    def __init__(
        self,
        student_model=None,
        anthropic_api_key: Optional[str] = None,
        enable_logging: bool = True,
    ):
        """
        Initialize pipeline.

        Args:
            student_model: Shared StudentModelInterface instance
            anthropic_api_key: Anthropic API key
            enable_logging: Enable logging (default True)
        """
        # Initialize engines
        self.engine_1 = LessonArchitect(
            student_model=student_model,
            anthropic_api_key=anthropic_api_key,
        )
        self.engine_5 = DiagnosticEngine(
            student_model=student_model,
            anthropic_api_key=anthropic_api_key,
        )
        self.engine_2 = WorksheetDesigner(
            student_model=student_model,
            anthropic_api_key=anthropic_api_key,
        )
        self.engine_3 = IEPSpecialist(
            student_model=student_model,
            anthropic_api_key=anthropic_api_key,
        )

        # Logging
        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger("MasterCreatorPipeline")

    def run(self, input_params: PipelineInput) -> PipelineOutput:
        """
        Run complete pipeline.

        Args:
            input_params: Pipeline input parameters

        Returns:
            PipelineOutput with results from all engines
        """
        import uuid
        import time

        pipeline_id = f"pipeline_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        started_at = datetime.utcnow().isoformat()

        errors = []
        warnings = []
        cost_breakdown = {}

        # Initialize outputs
        lesson = None
        diagnostic = None
        worksheets = None
        modified_worksheets = None

        self.logger.info(f"Starting pipeline {pipeline_id} for {input_params.lesson_topic}")

        try:
            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
            # STAGE 1: LESSON ARCHITECT (Engine 1)
            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

            self.logger.info("Stage 1: Generating lesson blueprint (Engine 1)")

            lesson = self.engine_1.generate(
                topic=input_params.lesson_topic,
                grade_level=input_params.grade_level,
                subject=input_params.subject,
                duration_minutes=input_params.duration_minutes,
                standards=input_params.standards,
                class_id=input_params.class_id,
            )

            cost_breakdown["engine_1"] = self.engine_1.get_cost_summary()["total_cost"]
            self.logger.info(
                f"Engine 1 complete: {lesson.lesson_id} | "
                f"Cost: ${cost_breakdown['engine_1']:.4f}"
            )

            # Extract learning objectives for diagnostic
            learning_objectives = []
            for section in lesson.sections:
                if section.section_name == "Learning Objectives":
                    learning_objectives.append(section.content)
                    break

            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
            # STAGE 2: DIAGNOSTIC ENGINE (Engine 5)
            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

            self.logger.info("Stage 2: Running diagnostic assessment (Engine 5)")

            diagnostic = self.engine_5.generate(
                lesson_objectives=learning_objectives if learning_objectives else [input_params.lesson_topic],
                concept_ids=input_params.concept_ids,
                class_id=input_params.class_id,
                num_questions_per_concept=input_params.num_questions_per_concept,
                grade_level=input_params.grade_level,
                subject=input_params.subject,
            )

            cost_breakdown["engine_5"] = self.engine_5.get_cost_summary()["total_cost"]
            self.logger.info(
                f"Engine 5 complete: {diagnostic.diagnostic_id} | "
                f"Tiers: {diagnostic.tier_distribution} | "
                f"Cost: ${cost_breakdown['engine_5']:.4f}"
            )

            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
            # STAGE 3: WORKSHEET DESIGNER (Engine 2)
            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

            self.logger.info("Stage 3: Generating differentiated worksheets (Engine 2)")

            # Prepare diagnostic results for Engine 2
            diagnostic_dict = {
                "diagnostic_id": diagnostic.diagnostic_id,
                "student_estimates": [
                    {
                        "student_id": est.student_id,
                        "concept_id": est.concept_id,
                        "mastery_probability": est.mastery_probability,
                        "recommended_tier": est.recommended_tier,
                    }
                    for est in diagnostic.student_estimates
                ],
            }

            # Get learning objective from lesson
            learning_objective = input_params.lesson_topic
            for section in lesson.sections:
                if section.section_name == "Learning Objectives":
                    learning_objective = section.content[:200]  # First 200 chars
                    break

            worksheets = self.engine_2.generate(
                lesson_topic=input_params.lesson_topic,
                learning_objective=learning_objective,
                grade_level=input_params.grade_level,
                subject=input_params.subject,
                class_id=input_params.class_id,
                diagnostic_results=diagnostic_dict,
                standards=input_params.standards,
                num_questions_per_tier=input_params.num_questions_per_tier,
            )

            cost_breakdown["engine_2"] = self.engine_2.get_cost_summary()["total_cost"]
            self.logger.info(
                f"Engine 2 complete: {worksheets.worksheet_id} | "
                f"Cost: ${cost_breakdown['engine_2']:.4f}"
            )

            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
            # STAGE 4: IEP SPECIALIST (Engine 3)
            # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

            self.logger.info("Stage 4: Applying IEP accommodations (Engine 3)")

            modified_worksheets = self.engine_3.apply_accommodations(
                worksheet_set=worksheets,
            )

            cost_breakdown["engine_3"] = self.engine_3.get_cost_summary()["total_cost"]
            self.logger.info(
                f"Engine 3 complete: {modified_worksheets.modified_worksheet_id} | "
                f"IEP students: {modified_worksheets.total_iep_students} | "
                f"Accommodations: {len(modified_worksheets.accommodations_applied)} | "
                f"Cost: ${cost_breakdown['engine_3']:.4f}"
            )

        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            errors.append(f"Pipeline execution error: {str(e)}")

        # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
        # BUILD OUTPUT
        # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

        end_time = time.time()
        completed_at = datetime.utcnow().isoformat()
        total_duration = end_time - start_time

        total_cost = sum(cost_breakdown.values())

        # Determine status
        if errors:
            status = "failure"
        elif warnings:
            status = "partial_failure"
        else:
            status = "success"

        output = PipelineOutput(
            pipeline_id=pipeline_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            total_duration_seconds=round(total_duration, 2),
            lesson=lesson,
            diagnostic=diagnostic,
            worksheets=worksheets,
            modified_worksheets=modified_worksheets,
            total_cost=round(total_cost, 4),
            cost_breakdown=cost_breakdown,
            errors=errors,
            warnings=warnings,
        )

        self.logger.info(
            f"Pipeline {pipeline_id} complete | "
            f"Status: {status} | "
            f"Duration: {total_duration:.2f}s | "
            f"Cost: ${total_cost:.4f}"
        )

        return output

    def get_total_cost(self) -> float:
        """Get total cost across all engines."""
        return (
            self.engine_1.get_cost_summary()["total_cost"]
            + self.engine_5.get_cost_summary()["total_cost"]
            + self.engine_2.get_cost_summary()["total_cost"]
            + self.engine_3.get_cost_summary()["total_cost"]
        )

    def reset_all_tracking(self):
        """Reset cost and usage tracking for all engines."""
        self.engine_1.reset_tracking()
        self.engine_5.reset_tracking()
        self.engine_2.reset_tracking()
        self.engine_3.reset_tracking()


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTION
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def run_pipeline(
    lesson_topic: str,
    grade_level: str,
    subject: str,
    class_id: str,
    concept_ids: List[str],
    duration_minutes: int = 45,
    standards: Optional[List[str]] = None,
) -> PipelineOutput:
    """
    Convenience function to run complete pipeline.

    Args:
        lesson_topic: Lesson topic
        grade_level: Grade level
        subject: Subject area
        class_id: Class identifier
        concept_ids: Concepts to assess
        duration_minutes: Lesson duration
        standards: Standards addressed

    Returns:
        PipelineOutput with all results
    """
    pipeline = MasterCreatorPipeline()

    input_params = PipelineInput(
        lesson_topic=lesson_topic,
        grade_level=grade_level,
        subject=subject,
        class_id=class_id,
        duration_minutes=duration_minutes,
        standards=standards,
        concept_ids=concept_ids,
    )

    return pipeline.run(input_params)


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLI TESTING
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("""
Usage: python -m src.orchestration.pipeline <topic> <grade> <subject> <class_id> <concept_ids>

Example:
  python -m src.orchestration.pipeline "Photosynthesis" "9" "Science" "class_bio_101" "photosynthesis_process,cellular_respiration"

This will run the complete pipeline:
1. Engine 1: Generate lesson blueprint
2. Engine 5: Run diagnostic assessment
3. Engine 2: Generate differentiated worksheets
4. Engine 3: Apply IEP accommodations
        """)
        sys.exit(1)

    topic = sys.argv[1]
    grade = sys.argv[2]
    subject = sys.argv[3]
    class_id = sys.argv[4]
    concept_ids = sys.argv[5].split(",") if len(sys.argv) > 5 else [topic.lower().replace(" ", "_")]

    print(f"Running Master Creator v3 Pipeline")
    print("=" * 70)
    print(f"Topic: {topic}")
    print(f"Grade: {grade}")
    print(f"Subject: {subject}")
    print(f"Class: {class_id}")
    print(f"Concepts: {', '.join(concept_ids)}")
    print("=" * 70)
    print()

    # Run pipeline
    result = run_pipeline(
        lesson_topic=topic,
        grade_level=grade,
        subject=subject,
        class_id=class_id,
        concept_ids=concept_ids,
        standards=["NGSS-HS-LS1-5"] if "photo" in topic.lower() else [],
    )

    # Display results
    print("\n" + "=" * 70)
    print("PIPELINE RESULTS")
    print("=" * 70)
    print(f"Pipeline ID: {result.pipeline_id}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.total_duration_seconds}s")
    print(f"Total Cost: ${result.total_cost:.4f}")
    print()

    if result.lesson:
        print(f"Lesson: {result.lesson.lesson_id} ({len(result.lesson.sections)} sections)")

    if result.diagnostic:
        print(f"Diagnostic: {result.diagnostic.diagnostic_id} ({len(result.diagnostic.questions)} questions)")
        print(f"  Tier Distribution: {result.diagnostic.tier_distribution}")

    if result.worksheets:
        print(f"Worksheets: {result.worksheets.worksheet_id}")
        print(f"  Tier 1: {result.worksheets.tier_1.student_count} students, {len(result.worksheets.tier_1.questions)} questions")
        print(f"  Tier 2: {result.worksheets.tier_2.student_count} students, {len(result.worksheets.tier_2.questions)} questions")
        print(f"  Tier 3: {result.worksheets.tier_3.student_count} students, {len(result.worksheets.tier_3.questions)} questions")

    if result.modified_worksheets:
        print(f"Modified Worksheets: {result.modified_worksheets.modified_worksheet_id}")
        print(f"  IEP Students: {result.modified_worksheets.total_iep_students}")
        print(f"  Accommodations Applied: {len(result.modified_worksheets.accommodations_applied)}")

    print("\n" + "=" * 70)
    print("COST BREAKDOWN")
    print("=" * 70)
    for engine, cost in result.cost_breakdown.items():
        print(f"  {engine}: ${cost:.4f}")
    print(f"  TOTAL: ${result.total_cost:.4f}")

    if result.errors:
        print("\n" + "=" * 70)
        print("ERRORS")
        print("=" * 70)
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\n" + "=" * 70)
        print("WARNINGS")
        print("=" * 70)
        for warning in result.warnings:
            print(f"  - {warning}")
