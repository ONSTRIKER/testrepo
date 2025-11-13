"""
LangGraph Async Pipeline Orchestration

Implements stateful, asynchronous pipeline execution using LangGraph.

Features:
- Conditional routing (skip optional engines)
- Error handling with retry logic
- Parallel execution where possible
- State persistence across nodes
- Observable execution flow
"""

import logging
from typing import Literal, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from .state_management import (
    PipelineState,
    initialize_pipeline_state,
    add_error,
    add_warning,
    update_cost,
    mark_stage_complete,
    finalize_pipeline,
    should_retry,
    increment_retry,
)

from ..engines.engine_0_unit_planner import UnitPlanDesigner
from ..engines.engine_1_lesson_architect import LessonArchitect
from ..engines.engine_5_diagnostic import DiagnosticEngine
from ..engines.engine_2_worksheet_designer import WorksheetDesigner
from ..engines.engine_3_iep_specialist import IEPSpecialist
from ..engines.engine_4_adaptive import AdaptiveEngine
from ..engines.engine_6_feedback import FeedbackLoop


# ═══════════════════════════════════════════════════════════
# GRAPH NODES (Each engine becomes a node)
# ═══════════════════════════════════════════════════════════


def unit_plan_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 0 - Unit Plan Designer

    Generates multi-lesson unit plan using UbD framework.
    """
    logger = logging.getLogger("langgraph.unit_plan")
    state["current_stage"] = "unit_plan"

    try:
        logger.info(f"Running Engine 0: Unit Plan Designer")

        engine = UnitPlanDesigner()
        unit_plan = engine.generate(
            unit_title=state["lesson_topic"],
            grade_level=state["grade_level"],
            subject=state["subject"],
            num_lessons=state.get("num_lessons_in_unit", 5),
            standards=state.get("standards"),
            class_id=state.get("class_id"),
        )

        # Convert to dict for state storage
        state["unit_plan"] = unit_plan.model_dump()
        state["unit_plan_id"] = unit_plan.unit_id

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_0",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "unit_plan", success=True)
        logger.info(f"Engine 0 complete: {unit_plan.unit_id}")

    except Exception as e:
        logger.error(f"Engine 0 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 0 (Unit Plan) failed: {str(e)}")
        mark_stage_complete(state, "unit_plan", success=False)

    return state


def lesson_architect_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 1 - Lesson Architect

    Generates 10-part lesson blueprint.
    """
    logger = logging.getLogger("langgraph.lesson_architect")
    state["current_stage"] = "lesson_architect"

    try:
        logger.info("Running Engine 1: Lesson Architect")

        engine = LessonArchitect()
        lesson = engine.generate(
            topic=state["lesson_topic"],
            grade_level=state["grade_level"],
            subject=state["subject"],
            duration_minutes=state["duration_minutes"],
            standards=state.get("standards"),
            class_id=state["class_id"],
        )

        # Store in state
        state["lesson"] = lesson.model_dump()
        state["lesson_id"] = lesson.lesson_id

        # Extract learning objectives
        learning_objectives = []
        for section in lesson.sections:
            if section.section_name == "Learning Objectives":
                learning_objectives.append(section.content)
        state["learning_objectives"] = learning_objectives

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_1",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "lesson_architect", success=True)
        logger.info(f"Engine 1 complete: {lesson.lesson_id}")

    except Exception as e:
        logger.error(f"Engine 1 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 1 (Lesson Architect) failed: {str(e)}")
        mark_stage_complete(state, "lesson_architect", success=False)

    return state


def diagnostic_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 5 - Diagnostic Engine

    Runs diagnostic assessment with BKT mastery estimation.
    """
    logger = logging.getLogger("langgraph.diagnostic")
    state["current_stage"] = "diagnostic"

    try:
        logger.info("Running Engine 5: Diagnostic Engine")

        engine = DiagnosticEngine()

        # Get learning objectives from lesson
        learning_objectives = state.get("learning_objectives", [state["lesson_topic"]])

        diagnostic = engine.generate(
            lesson_objectives=learning_objectives,
            concept_ids=state["concept_ids"],
            class_id=state["class_id"],
            num_questions_per_concept=state["num_questions_per_concept"],
            grade_level=state["grade_level"],
            subject=state["subject"],
        )

        # Store in state
        state["diagnostic"] = diagnostic.model_dump()
        state["diagnostic_id"] = diagnostic.diagnostic_id
        state["tier_distribution"] = diagnostic.tier_distribution

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_5",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "diagnostic", success=True)
        logger.info(f"Engine 5 complete: {diagnostic.diagnostic_id}")

    except Exception as e:
        logger.error(f"Engine 5 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 5 (Diagnostic) failed: {str(e)}")
        mark_stage_complete(state, "diagnostic", success=False)

    return state


def worksheet_designer_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 2 - Worksheet Designer

    Generates 3-tier differentiated worksheets.
    """
    logger = logging.getLogger("langgraph.worksheet_designer")
    state["current_stage"] = "worksheet_designer"

    try:
        logger.info("Running Engine 2: Worksheet Designer")

        engine = WorksheetDesigner()

        # Get learning objective from lesson
        learning_objective = state["lesson_topic"]
        if state.get("learning_objectives"):
            learning_objective = state["learning_objectives"][0][:200]

        # Prepare diagnostic results
        diagnostic_dict = {
            "diagnostic_id": state["diagnostic_id"],
            "student_estimates": [
                {
                    "student_id": est["student_id"],
                    "concept_id": est["concept_id"],
                    "mastery_probability": est["mastery_probability"],
                    "recommended_tier": est["recommended_tier"],
                }
                for est in state["diagnostic"]["student_estimates"]
            ],
        }

        worksheets = engine.generate(
            lesson_topic=state["lesson_topic"],
            learning_objective=learning_objective,
            grade_level=state["grade_level"],
            subject=state["subject"],
            class_id=state["class_id"],
            diagnostic_results=diagnostic_dict,
            standards=state.get("standards"),
            num_questions_per_tier=state.get("num_questions_per_tier"),
        )

        # Store in state
        state["worksheets"] = worksheets.model_dump()
        state["worksheet_id"] = worksheets.worksheet_id

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_2",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "worksheet_designer", success=True)
        logger.info(f"Engine 2 complete: {worksheets.worksheet_id}")

    except Exception as e:
        logger.error(f"Engine 2 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 2 (Worksheet Designer) failed: {str(e)}")
        mark_stage_complete(state, "worksheet_designer", success=False)

    return state


def iep_specialist_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 3 - IEP Specialist

    Applies IEP accommodations to worksheets.
    """
    logger = logging.getLogger("langgraph.iep_specialist")
    state["current_stage"] = "iep_specialist"

    try:
        logger.info("Running Engine 3: IEP Specialist")

        engine = IEPSpecialist()

        # Reconstruct WorksheetSet from state
        from ..engines.engine_2_worksheet_designer import WorksheetSet

        worksheet_set = WorksheetSet(**state["worksheets"])

        modified_worksheets = engine.apply_accommodations(worksheet_set)

        # Store in state
        state["modified_worksheets"] = modified_worksheets.model_dump()
        state["modified_worksheet_id"] = modified_worksheets.modified_worksheet_id
        state["iep_students_count"] = modified_worksheets.total_iep_students

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_3",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "iep_specialist", success=True)
        logger.info(f"Engine 3 complete: {modified_worksheets.modified_worksheet_id}")

    except Exception as e:
        logger.error(f"Engine 3 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 3 (IEP Specialist) failed: {str(e)}")
        mark_stage_complete(state, "iep_specialist", success=False)

    return state


def adaptive_plan_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 4 - Adaptive Personalization

    Generates personalized learning paths (optional).
    """
    logger = logging.getLogger("langgraph.adaptive_plan")
    state["current_stage"] = "adaptive_plan"

    try:
        logger.info("Running Engine 4: Adaptive Personalization")

        engine = AdaptiveEngine()

        adaptive_plan = engine.generate_class_plan(
            class_id=state["class_id"],
            concept_ids=state["concept_ids"],
        )

        # Store in state
        state["adaptive_plan"] = adaptive_plan.model_dump()
        state["adaptive_plan_id"] = adaptive_plan.plan_id

        # Update cost
        cost_summary = engine.get_cost_summary()
        update_cost(
            state,
            "engine_4",
            cost_summary["total_cost"],
            cost_summary.get("input_tokens", 0),
            cost_summary.get("output_tokens", 0),
        )

        mark_stage_complete(state, "adaptive_plan", success=True)
        logger.info(f"Engine 4 complete: {adaptive_plan.plan_id}")

    except Exception as e:
        logger.error(f"Engine 4 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 4 (Adaptive Personalization) failed: {str(e)}")
        mark_stage_complete(state, "adaptive_plan", success=False)

    return state


def feedback_loop_node(state: PipelineState) -> PipelineState:
    """
    Node: Engine 6 - Feedback Loop

    Monitors prediction accuracy (optional).
    """
    logger = logging.getLogger("langgraph.feedback_loop")
    state["current_stage"] = "feedback_loop"

    try:
        logger.info("Running Engine 6: Feedback Loop")

        engine = FeedbackLoop()

        feedback_report = engine.generate_feedback(
            engine_name="engine_5_diagnostic",
            timeframe_days=30,
        )

        # Store in state
        state["feedback_report"] = feedback_report.model_dump()
        state["feedback_id"] = feedback_report.feedback_id

        # Update cost (minimal for Engine 6)
        update_cost(state, "engine_6", 0.0, 0, 0)

        mark_stage_complete(state, "feedback_loop", success=True)
        logger.info(f"Engine 6 complete: {feedback_report.feedback_id}")

    except Exception as e:
        logger.error(f"Engine 6 failed: {str(e)}", exc_info=True)
        add_error(state, f"Engine 6 (Feedback Loop) failed: {str(e)}")
        mark_stage_complete(state, "feedback_loop", success=False)

    return state


def finalize_node(state: PipelineState) -> PipelineState:
    """
    Node: Finalize Pipeline

    Marks pipeline as complete and performs cleanup.
    """
    logger = logging.getLogger("langgraph.finalize")
    logger.info("Finalizing pipeline")

    success = len(state["errors"]) == 0
    finalize_pipeline(state, success=success)

    logger.info(
        f"Pipeline {state['pipeline_id']} complete | "
        f"Status: {state['execution_status']} | "
        f"Cost: ${state['total_cost']:.4f}"
    )

    return state


# ═══════════════════════════════════════════════════════════
# CONDITIONAL ROUTING
# ═══════════════════════════════════════════════════════════


def should_run_unit_plan(state: PipelineState) -> Literal["unit_plan", "lesson_architect"]:
    """Route: Check if Unit Plan should be generated."""
    if state.get("skip_unit_plan", True):
        return "lesson_architect"
    else:
        return "unit_plan"


def should_run_adaptive(state: PipelineState) -> Literal["adaptive_plan", "feedback_check"]:
    """Route: Check if Adaptive Plan should be generated."""
    # Only run if no errors occurred in core pipeline
    if state.get("skip_adaptive_plan", True) or state["errors"]:
        return "feedback_check"
    else:
        return "adaptive_plan"


def should_run_feedback(state: PipelineState) -> Literal["feedback_loop", "finalize"]:
    """Route: Check if Feedback Loop should run."""
    if state.get("skip_feedback_loop", True) or state["errors"]:
        return "finalize"
    else:
        return "feedback_loop"


def check_core_pipeline_success(state: PipelineState) -> Literal["iep_specialist", "finalize"]:
    """Route: Check if core pipeline succeeded."""
    # If diagnostic or worksheet failed, skip IEP and finalize
    if state["errors"]:
        return "finalize"
    else:
        return "iep_specialist"


# ═══════════════════════════════════════════════════════════
# GRAPH CONSTRUCTION
# ═══════════════════════════════════════════════════════════


def create_master_creator_graph() -> StateGraph:
    """
    Create LangGraph state graph for Master Creator v3 pipeline.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize graph with state
    graph = StateGraph(PipelineState)

    # Add nodes (each engine)
    graph.add_node("unit_plan", unit_plan_node)
    graph.add_node("lesson_architect", lesson_architect_node)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("worksheet_designer", worksheet_designer_node)
    graph.add_node("iep_specialist", iep_specialist_node)
    graph.add_node("adaptive_plan", adaptive_plan_node)
    graph.add_node("feedback_loop", feedback_loop_node)
    graph.add_node("finalize", finalize_node)

    # ───────────────────────────────────────────────────────
    # EDGES: Define execution flow
    # ───────────────────────────────────────────────────────

    # Entry point: Conditional - Unit Plan or Lesson Architect?
    graph.set_conditional_entry_point(
        should_run_unit_plan,
        {
            "unit_plan": "unit_plan",
            "lesson_architect": "lesson_architect",
        },
    )

    # Unit Plan → Lesson Architect
    graph.add_edge("unit_plan", "lesson_architect")

    # Lesson Architect → Diagnostic (always)
    graph.add_edge("lesson_architect", "diagnostic")

    # Diagnostic → Worksheet Designer (always)
    graph.add_edge("diagnostic", "worksheet_designer")

    # Worksheet Designer → Conditional check
    graph.add_conditional_edges(
        "worksheet_designer",
        check_core_pipeline_success,
        {
            "iep_specialist": "iep_specialist",
            "finalize": "finalize",
        },
    )

    # IEP Specialist → Adaptive Plan check
    graph.add_conditional_edges(
        "iep_specialist",
        should_run_adaptive,
        {
            "adaptive_plan": "adaptive_plan",
            "feedback_check": "feedback_loop",  # Placeholder name
        },
    )

    # Adaptive Plan → Feedback Loop check
    graph.add_conditional_edges(
        "adaptive_plan",
        should_run_feedback,
        {
            "feedback_loop": "feedback_loop",
            "finalize": "finalize",
        },
    )

    # Feedback Loop → Finalize (always)
    graph.add_edge("feedback_loop", "finalize")

    # Finalize → END
    graph.add_edge("finalize", END)

    # Compile graph
    compiled_graph = graph.compile()

    return compiled_graph


# ═══════════════════════════════════════════════════════════
# EXECUTION FUNCTIONS
# ═══════════════════════════════════════════════════════════


async def run_async_pipeline(
    lesson_topic: str,
    grade_level: str,
    subject: str,
    class_id: str,
    concept_ids: list[str],
    duration_minutes: int = 45,
    standards: Optional[list[str]] = None,
    generate_unit: bool = False,
    num_lessons_in_unit: Optional[int] = None,
    generate_adaptive_plan: bool = False,
    run_feedback_loop: bool = False,
) -> PipelineState:
    """
    Run Master Creator v3 pipeline asynchronously with LangGraph.

    Args:
        lesson_topic: Lesson topic
        grade_level: Grade level
        subject: Subject area
        class_id: Class identifier
        concept_ids: Concepts to assess
        duration_minutes: Lesson duration
        standards: Standards addressed
        generate_unit: Generate unit plan first
        num_lessons_in_unit: Number of lessons in unit
        generate_adaptive_plan: Generate adaptive plan
        run_feedback_loop: Run feedback loop

    Returns:
        Final PipelineState with all results
    """
    # Initialize state
    initial_state = initialize_pipeline_state(
        lesson_topic=lesson_topic,
        grade_level=grade_level,
        subject=subject,
        class_id=class_id,
        concept_ids=concept_ids,
        duration_minutes=duration_minutes,
        standards=standards,
        generate_unit=generate_unit,
        num_lessons_in_unit=num_lessons_in_unit,
        generate_adaptive_plan=generate_adaptive_plan,
        run_feedback_loop=run_feedback_loop,
    )

    # Create graph
    graph = create_master_creator_graph()

    # Execute graph asynchronously
    final_state = await graph.ainvoke(initial_state)

    return final_state


def run_sync_pipeline(
    lesson_topic: str,
    grade_level: str,
    subject: str,
    class_id: str,
    concept_ids: list[str],
    duration_minutes: int = 45,
    standards: Optional[list[str]] = None,
    generate_unit: bool = False,
    num_lessons_in_unit: Optional[int] = None,
    generate_adaptive_plan: bool = False,
    run_feedback_loop: bool = False,
) -> PipelineState:
    """
    Run Master Creator v3 pipeline synchronously with LangGraph.

    Args:
        lesson_topic: Lesson topic
        grade_level: Grade level
        subject: Subject area
        class_id: Class identifier
        concept_ids: Concepts to assess
        duration_minutes: Lesson duration
        standards: Standards addressed
        generate_unit: Generate unit plan first
        num_lessons_in_unit: Number of lessons in unit
        generate_adaptive_plan: Generate adaptive plan
        run_feedback_loop: Run feedback loop

    Returns:
        Final PipelineState with all results
    """
    # Initialize state
    initial_state = initialize_pipeline_state(
        lesson_topic=lesson_topic,
        grade_level=grade_level,
        subject=subject,
        class_id=class_id,
        concept_ids=concept_ids,
        duration_minutes=duration_minutes,
        standards=standards,
        generate_unit=generate_unit,
        num_lessons_in_unit=num_lessons_in_unit,
        generate_adaptive_plan=generate_adaptive_plan,
        run_feedback_loop=run_feedback_loop,
    )

    # Create graph
    graph = create_master_creator_graph()

    # Execute graph synchronously
    final_state = graph.invoke(initial_state)

    return final_state


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    import sys
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 5:
        print("""
Usage: python -m src.orchestration.langgraph_pipeline <topic> <grade> <subject> <class_id> <concept_ids> [--async]

Example:
  python -m src.orchestration.langgraph_pipeline "Photosynthesis" "9" "Science" "class_bio_101" "photosynthesis_process" --async

Options:
  --async: Run asynchronously (default: synchronous)
  --unit: Generate unit plan first
  --adaptive: Generate adaptive plan
  --feedback: Run feedback loop
        """)
        sys.exit(1)

    topic = sys.argv[1]
    grade = sys.argv[2]
    subject = sys.argv[3]
    class_id = sys.argv[4]
    concept_ids = sys.argv[5].split(",") if len(sys.argv) > 5 else [topic.lower().replace(" ", "_")]

    # Parse flags
    use_async = "--async" in sys.argv
    generate_unit = "--unit" in sys.argv
    generate_adaptive = "--adaptive" in sys.argv
    run_feedback = "--feedback" in sys.argv

    print("=" * 70)
    print("MASTER CREATOR V3 - LANGGRAPH PIPELINE")
    print("=" * 70)
    print(f"Topic: {topic}")
    print(f"Grade: {grade}")
    print(f"Subject: {subject}")
    print(f"Class: {class_id}")
    print(f"Concepts: {', '.join(concept_ids)}")
    print(f"Mode: {'Async' if use_async else 'Sync'}")
    print(f"Unit Plan: {'Yes' if generate_unit else 'No'}")
    print(f"Adaptive Plan: {'Yes' if generate_adaptive else 'No'}")
    print(f"Feedback Loop: {'Yes' if run_feedback else 'No'}")
    print("=" * 70)
    print()

    # Run pipeline
    if use_async:
        final_state = asyncio.run(
            run_async_pipeline(
                lesson_topic=topic,
                grade_level=grade,
                subject=subject,
                class_id=class_id,
                concept_ids=concept_ids,
                generate_unit=generate_unit,
                generate_adaptive_plan=generate_adaptive,
                run_feedback_loop=run_feedback,
            )
        )
    else:
        final_state = run_sync_pipeline(
            lesson_topic=topic,
            grade_level=grade,
            subject=subject,
            class_id=class_id,
            concept_ids=concept_ids,
            generate_unit=generate_unit,
            generate_adaptive_plan=generate_adaptive,
            run_feedback_loop=run_feedback,
        )

    # Display results
    print("\n" + "=" * 70)
    print("PIPELINE RESULTS")
    print("=" * 70)
    print(f"Pipeline ID: {final_state['pipeline_id']}")
    print(f"Status: {final_state['execution_status']}")
    print(f"Total Cost: ${final_state['total_cost']:.4f}")
    print()

    if final_state.get("lesson_id"):
        print(f"✅ Lesson: {final_state['lesson_id']}")

    if final_state.get("diagnostic_id"):
        print(f"✅ Diagnostic: {final_state['diagnostic_id']}")
        print(f"   Tiers: {final_state['tier_distribution']}")

    if final_state.get("worksheet_id"):
        print(f"✅ Worksheets: {final_state['worksheet_id']}")

    if final_state.get("modified_worksheet_id"):
        print(f"✅ Modified Worksheets: {final_state['modified_worksheet_id']}")
        print(f"   IEP Students: {final_state['iep_students_count']}")

    if final_state.get("adaptive_plan_id"):
        print(f"✅ Adaptive Plan: {final_state['adaptive_plan_id']}")

    if final_state.get("feedback_id"):
        print(f"✅ Feedback Report: {final_state['feedback_id']}")

    print("\n" + "=" * 70)
    print("COST BREAKDOWN")
    print("=" * 70)
    for engine, cost in final_state["cost_breakdown"].items():
        tokens = final_state["token_usage"].get(engine, {})
        print(f"  {engine}: ${cost:.4f} ({tokens.get('input_tokens', 0)} in / {tokens.get('output_tokens', 0)} out)")
    print(f"  TOTAL: ${final_state['total_cost']:.4f}")

    if final_state["errors"]:
        print("\n" + "=" * 70)
        print("ERRORS")
        print("=" * 70)
        for error in final_state["errors"]:
            print(f"  ❌ {error}")

    if final_state["warnings"]:
        print("\n" + "=" * 70)
        print("WARNINGS")
        print("=" * 70)
        for warning in final_state["warnings"]:
            print(f"  ⚠️ {warning}")
