"""
Engine 5: Diagnostic Engine

Generates diagnostic assessments and estimates student mastery using
Bayesian Knowledge Tracing (BKT).

Core Functionality:
1. Generate diagnostic questions from lesson objectives
2. Assess student understanding with BKT algorithm
3. Update Student Model with mastery estimates
4. Log predictions for Engine 6 accuracy tracking
5. Provide tier recommendations for Engine 2

Bayesian Knowledge Tracing Parameters:
- p_learn: Probability of learning (default 0.3)
- p_guess: Probability of guessing correctly (default 0.25)
- p_slip: Probability of making an error despite knowing (default 0.1)
- mastery_probability: P(student has mastered concept)

BKT Update Formula:
P(L_t+1) = P(L_t | evidence) + (1 - P(L_t | evidence)) * p_learn

Where:
P(L_t | correct) = (P(L_t) * (1 - p_slip)) / (P(L_t) * (1 - p_slip) + (1 - P(L_t)) * p_guess)
P(L_t | incorrect) = (P(L_t) * p_slip) / (P(L_t) * p_slip + (1 - P(L_t)) * (1 - p_guess))
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine
from ..student_model.schemas import TierLevel, ConceptMastery, PredictionLog


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# INPUT/OUTPUT SCHEMAS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class DiagnosticQuestion(BaseModel):
    """Single diagnostic question."""

    question_id: str
    question_text: str
    question_type: str  # "multiple_choice", "true_false", "short_answer"
    concept_id: str
    difficulty_level: str  # "easy", "medium", "hard"
    correct_answer: str
    options: Optional[List[str]] = None  # For multiple choice
    rubric: Optional[str] = None  # For constructed response
    explanation: Optional[str] = None


class StudentMasteryEstimate(BaseModel):
    """Mastery estimate for one student on one concept."""

    student_id: str
    concept_id: str
    mastery_probability: float
    p_learn: float
    p_guess: float
    p_slip: float
    num_observations: int
    recommended_tier: TierLevel
    confidence: str  # "low", "medium", "high"


class DiagnosticResults(BaseModel):
    """Complete diagnostic assessment results."""

    diagnostic_id: str
    class_id: str
    concept_ids: List[str]
    questions: List[DiagnosticQuestion]
    student_estimates: List[StudentMasteryEstimate]
    tier_distribution: Dict[str, int]  # {tier_1: count, tier_2: count, tier_3: count}
    generated_at: str
    cost: float


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# BAYESIAN KNOWLEDGE TRACING
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class BayesianKnowledgeTracing:
    """
    Bayesian Knowledge Tracing (BKT) implementation.

    Estimates P(student has mastered concept) based on observed performance.
    """

    def __init__(
        self,
        p_learn: float = 0.3,
        p_guess: float = 0.25,
        p_slip: float = 0.1,
        initial_mastery: float = 0.5,
    ):
        """
        Initialize BKT parameters.

        Args:
            p_learn: Probability of learning (transition from not-mastered to mastered)
            p_guess: Probability of guessing correctly without mastery
            p_slip: Probability of making an error despite mastery
            initial_mastery: Initial estimate for new students (default 0.5)
        """
        self.p_learn = p_learn
        self.p_guess = p_guess
        self.p_slip = p_slip
        self.initial_mastery = initial_mastery

    def update(
        self,
        prior_mastery: float,
        observation_correct: bool,
    ) -> float:
        """
        Update mastery probability given an observation.

        Args:
            prior_mastery: P(mastery) before observation
            observation_correct: True if student answered correctly

        Returns:
            Updated mastery probability
        """
        if observation_correct:
            # Correct answer
            posterior = self._update_correct(prior_mastery)
        else:
            # Incorrect answer
            posterior = self._update_incorrect(prior_mastery)

        # Apply learning: P(L_t+1) = P(L_t | evidence) + (1 - P(L_t | evidence)) * p_learn
        updated_mastery = posterior + (1 - posterior) * self.p_learn

        # Clamp to [0, 1]
        return max(0.0, min(1.0, updated_mastery))

    def _update_correct(self, prior: float) -> float:
        """
        Update given correct answer.

        P(L_t | correct) = P(L_t) * (1 - p_slip) / [P(L_t) * (1 - p_slip) + (1 - P(L_t)) * p_guess]
        """
        numerator = prior * (1 - self.p_slip)
        denominator = numerator + (1 - prior) * self.p_guess

        if denominator == 0:
            return prior

        return numerator / denominator

    def _update_incorrect(self, prior: float) -> float:
        """
        Update given incorrect answer.

        P(L_t | incorrect) = P(L_t) * p_slip / [P(L_t) * p_slip + (1 - P(L_t)) * (1 - p_guess)]
        """
        numerator = prior * self.p_slip
        denominator = numerator + (1 - prior) * (1 - self.p_guess)

        if denominator == 0:
            return prior

        return numerator / denominator

    def bulk_update(
        self,
        prior_mastery: float,
        observations: List[bool],
    ) -> float:
        """
        Update mastery based on multiple observations.

        Args:
            prior_mastery: Initial mastery probability
            observations: List of correctness values (True/False)

        Returns:
            Final mastery probability after all observations
        """
        current_mastery = prior_mastery

        for obs in observations:
            current_mastery = self.update(current_mastery, obs)

        return current_mastery

    def get_confidence(self, mastery: float, num_observations: int) -> str:
        """
        Determine confidence level in mastery estimate.

        Args:
            mastery: Current mastery probability
            num_observations: Number of observations

        Returns:
            Confidence level: "low", "medium", "high"
        """
        if num_observations < 3:
            return "low"
        elif num_observations < 10:
            # Check if mastery is near boundaries (high confidence)
            if mastery < 0.3 or mastery > 0.7:
                return "medium"
            else:
                return "low"
        else:
            # 10+ observations
            if mastery < 0.2 or mastery > 0.8:
                return "high"
            else:
                return "medium"


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ENGINE 5: DIAGNOSTIC ENGINE
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class DiagnosticEngine(BaseEngine):
    """
    Engine 5: Generates diagnostic assessments and estimates mastery.

    Uses Bayesian Knowledge Tracing to update student mastery probabilities
    and provide tier recommendations for Engine 2.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bkt = BayesianKnowledgeTracing()

    def generate(
        self,
        lesson_objectives: List[str],
        concept_ids: List[str],
        class_id: str,
        num_questions_per_concept: int = 3,
        grade_level: str = "9",
        subject: str = "Science",
    ) -> DiagnosticResults:
        """
        Generate diagnostic assessment and estimate student mastery.

        Args:
            lesson_objectives: Learning objectives from Engine 1
            concept_ids: Concept IDs to assess (e.g., ["photosynthesis_process"])
            class_id: Class identifier
            num_questions_per_concept: Questions per concept (default 3)
            grade_level: Grade level for question generation
            subject: Subject area

        Returns:
            DiagnosticResults with questions and mastery estimates
        """
        diagnostic_id = f"diagnostic_{uuid.uuid4().hex[:12]}"

        self._log_decision(
            f"Generating diagnostic for {len(concept_ids)} concepts, class {class_id}"
        )

        # Step 1: Generate diagnostic questions via Claude
        questions = self._generate_questions(
            lesson_objectives=lesson_objectives,
            concept_ids=concept_ids,
            num_questions_per_concept=num_questions_per_concept,
            grade_level=grade_level,
            subject=subject,
        )

        # Step 2: Get student roster
        students = self.student_model.get_class_students(class_id)
        self._log_decision(f"Retrieved {len(students)} students from Student Model")

        # Step 3: Estimate mastery for each student-concept pair
        student_estimates = []

        for student in students:
            for concept_id in concept_ids:
                estimate = self._estimate_student_mastery(
                    student_id=student.student_id,
                    concept_id=concept_id,
                )
                student_estimates.append(estimate)

        # Step 4: Calculate tier distribution
        tier_counts = {
            "tier_1": sum(1 for e in student_estimates if e.recommended_tier == TierLevel.TIER_1),
            "tier_2": sum(1 for e in student_estimates if e.recommended_tier == TierLevel.TIER_2),
            "tier_3": sum(1 for e in student_estimates if e.recommended_tier == TierLevel.TIER_3),
        }

        # Step 5: Log predictions for Engine 6
        self._log_predictions(diagnostic_id, student_estimates)

        # Build results
        results = DiagnosticResults(
            diagnostic_id=diagnostic_id,
            class_id=class_id,
            concept_ids=concept_ids,
            questions=questions,
            student_estimates=student_estimates,
            tier_distribution=tier_counts,
            generated_at=datetime.utcnow().isoformat(),
            cost=self.get_cost_summary()["total_cost"],
        )

        self._log_decision(
            f"Diagnostic complete: {len(questions)} questions, "
            f"Tiers: {tier_counts['tier_1']}/{tier_counts['tier_2']}/{tier_counts['tier_3']}"
        )

        return results

    def _generate_questions(
        self,
        lesson_objectives: List[str],
        concept_ids: List[str],
        num_questions_per_concept: int,
        grade_level: str,
        subject: str,
    ) -> List[DiagnosticQuestion]:
        """
        Generate diagnostic questions via Claude.

        Args:
            lesson_objectives: Learning objectives to assess
            concept_ids: Concept IDs
            num_questions_per_concept: Number of questions per concept
            grade_level: Grade level
            subject: Subject area

        Returns:
            List of diagnostic questions
        """
        system_prompt = """You are an expert assessment designer for K-12 education.

Your task is to create diagnostic questions that accurately assess student understanding.

Requirements:
- Questions must align with learning objectives
- Mix difficulty levels (easy, medium, hard)
- Use varied question types (multiple choice, true/false, short answer)
- Provide clear correct answers and explanations
- Be age-appropriate and accessible

Respond ONLY with valid JSON in this exact format:

{
  "questions": [
    {
      "question_id": "q1_photosynthesis_easy",
      "question_text": "What gas do plants release during photosynthesis?",
      "question_type": "multiple_choice",
      "concept_id": "photosynthesis_process",
      "difficulty_level": "easy",
      "correct_answer": "B",
      "options": ["A) Carbon dioxide", "B) Oxygen", "C) Nitrogen", "D) Hydrogen"],
      "explanation": "Plants release oxygen as a byproduct of photosynthesis."
    },
    ...
  ]
}"""

        user_prompt = f"""Create {num_questions_per_concept} diagnostic questions for each of these concepts:

**Grade Level:** {grade_level}
**Subject:** {subject}

**Learning Objectives:**
{chr(10).join(f'- {obj}' for obj in lesson_objectives)}

**Concepts to Assess:**
{chr(10).join(f'- {cid}' for cid in concept_ids)}

**Requirements:**
- Total questions: {len(concept_ids) * num_questions_per_concept}
- Mix difficulty: ~40% easy, ~40% medium, ~20% hard
- Vary question types for engagement
- Ensure questions test understanding, not just recall

Respond ONLY with the JSON object. No additional text."""

        self._log_decision("Calling Claude API for question generation")
        response_text = self._call_claude(system_prompt, user_prompt)

        # Parse response
        questions_data = self._parse_questions_response(response_text)

        # Convert to DiagnosticQuestion objects
        questions = []
        for q in questions_data["questions"]:
            questions.append(
                DiagnosticQuestion(
                    question_id=q["question_id"],
                    question_text=q["question_text"],
                    question_type=q["question_type"],
                    concept_id=q["concept_id"],
                    difficulty_level=q["difficulty_level"],
                    correct_answer=q["correct_answer"],
                    options=q.get("options"),
                    rubric=q.get("rubric"),
                    explanation=q.get("explanation"),
                )
            )

        self._log_decision(f"Generated {len(questions)} diagnostic questions")
        return questions

    def _parse_questions_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response for questions."""
        try:
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            self._log_decision("JSON parse error, attempting extraction", level="warning")

            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    return data
                except:
                    pass

            # Fallback
            self._log_decision("Could not parse questions response", level="error")
            return {
                "questions": [
                    {
                        "question_id": "error_q1",
                        "question_text": "Error generating questions. Please try again.",
                        "question_type": "multiple_choice",
                        "concept_id": "unknown",
                        "difficulty_level": "medium",
                        "correct_answer": "A",
                        "options": ["A) Error", "B) Error", "C) Error", "D) Error"],
                        "explanation": response_text[:200],
                    }
                ]
            }

    def _estimate_student_mastery(
        self,
        student_id: str,
        concept_id: str,
    ) -> StudentMasteryEstimate:
        """
        Estimate mastery for one student-concept pair using BKT.

        Args:
            student_id: Student identifier
            concept_id: Concept identifier

        Returns:
            StudentMasteryEstimate with BKT parameters
        """
        # Query Student Model for existing mastery data
        mastery_records = self.student_model.retrieve_concept_mastery(
            student_id=student_id,
            concept_ids=[concept_id],
        )

        if mastery_records and len(mastery_records) > 0:
            # Existing mastery data
            mastery = mastery_records[0]
            current_mastery = mastery.mastery_probability
            p_learn = mastery.p_learn
            p_guess = mastery.p_guess
            p_slip = mastery.p_slip
            num_obs = mastery.num_observations
        else:
            # New student-concept: use defaults
            current_mastery = self.bkt.initial_mastery
            p_learn = self.bkt.p_learn
            p_guess = self.bkt.p_guess
            p_slip = self.bkt.p_slip
            num_obs = 0

        # Determine tier based on mastery thresholds
        if current_mastery >= 0.75:
            tier = TierLevel.TIER_1
        elif current_mastery >= 0.45:
            tier = TierLevel.TIER_2
        else:
            tier = TierLevel.TIER_3

        # Calculate confidence
        confidence = self.bkt.get_confidence(current_mastery, num_obs)

        return StudentMasteryEstimate(
            student_id=student_id,
            concept_id=concept_id,
            mastery_probability=round(current_mastery, 4),
            p_learn=p_learn,
            p_guess=p_guess,
            p_slip=p_slip,
            num_observations=num_obs,
            recommended_tier=tier,
            confidence=confidence,
        )

    def update_mastery_from_assessment(
        self,
        student_id: str,
        concept_id: str,
        observations: List[bool],
    ) -> StudentMasteryEstimate:
        """
        Update student mastery based on assessment responses.

        This method is called by the Grader after scoring an assessment.

        Args:
            student_id: Student identifier
            concept_id: Concept identifier
            observations: List of correctness (True/False) for each question

        Returns:
            Updated mastery estimate
        """
        # Get current mastery
        mastery_records = self.student_model.retrieve_concept_mastery(
            student_id=student_id,
            concept_ids=[concept_id],
        )

        if mastery_records and len(mastery_records) > 0:
            prior_mastery = mastery_records[0].mastery_probability
            num_obs = mastery_records[0].num_observations
        else:
            prior_mastery = self.bkt.initial_mastery
            num_obs = 0

        # Apply BKT updates
        updated_mastery = self.bkt.bulk_update(prior_mastery, observations)

        # Update Student Model
        self.student_model.update_mastery_estimate(
            student_id=student_id,
            concept_id=concept_id,
            new_mastery=updated_mastery,
        )

        # New observation count
        new_num_obs = num_obs + len(observations)

        # Determine new tier
        if updated_mastery >= 0.75:
            tier = TierLevel.TIER_1
        elif updated_mastery >= 0.45:
            tier = TierLevel.TIER_2
        else:
            tier = TierLevel.TIER_3

        confidence = self.bkt.get_confidence(updated_mastery, new_num_obs)

        self._log_decision(
            f"Updated mastery for {student_id}/{concept_id}: "
            f"{prior_mastery:.3f} ' {updated_mastery:.3f} (tier: {tier.value})"
        )

        return StudentMasteryEstimate(
            student_id=student_id,
            concept_id=concept_id,
            mastery_probability=round(updated_mastery, 4),
            p_learn=self.bkt.p_learn,
            p_guess=self.bkt.p_guess,
            p_slip=self.bkt.p_slip,
            num_observations=new_num_obs,
            recommended_tier=tier,
            confidence=confidence,
        )

    def _log_predictions(
        self,
        diagnostic_id: str,
        estimates: List[StudentMasteryEstimate],
    ) -> None:
        """
        Log mastery predictions to Student Model for Engine 6 tracking.

        Args:
            diagnostic_id: Diagnostic identifier
            estimates: Student mastery estimates
        """
        for estimate in estimates:
            prediction = PredictionLog(
                prediction_id=f"{diagnostic_id}_{estimate.student_id}_{estimate.concept_id}",
                engine_name="engine_5_diagnostic",
                student_id=estimate.student_id,
                concept_id=estimate.concept_id,
                predicted_mastery=estimate.mastery_probability,
                predicted_tier=estimate.recommended_tier,
            )

            self.student_model.log_prediction(prediction)

        self._log_decision(f"Logged {len(estimates)} predictions for Engine 6 tracking")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CONVENIENCE FUNCTIONS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def generate_diagnostic(
    lesson_objectives: List[str],
    concept_ids: List[str],
    class_id: str,
    num_questions_per_concept: int = 3,
    grade_level: str = "9",
    subject: str = "Science",
) -> DiagnosticResults:
    """
    Convenience function to generate diagnostic assessment.

    Args:
        lesson_objectives: Learning objectives
        concept_ids: Concept IDs to assess
        class_id: Class identifier
        num_questions_per_concept: Questions per concept
        grade_level: Grade level
        subject: Subject area

    Returns:
        DiagnosticResults
    """
    engine = DiagnosticEngine()
    return engine.generate(
        lesson_objectives=lesson_objectives,
        concept_ids=concept_ids,
        class_id=class_id,
        num_questions_per_concept=num_questions_per_concept,
        grade_level=grade_level,
        subject=subject,
    )


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLI TESTING
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("""
Usage: python -m src.engines.engine_5_diagnostic <class_id> <concept_id>

Example:
  python -m src.engines.engine_5_diagnostic "class_bio_101" "photosynthesis_process"
        """)
        sys.exit(1)

    class_id = sys.argv[1]
    concept_id = sys.argv[2]

    print(f"Generating diagnostic for class {class_id}, concept {concept_id}\n")

    # Generate diagnostic
    results = generate_diagnostic(
        lesson_objectives=[
            "Students will explain the process of photosynthesis",
            "Students will identify the reactants and products",
            "Students will describe the role of chlorophyll",
        ],
        concept_ids=[concept_id],
        class_id=class_id,
        num_questions_per_concept=3,
        grade_level="9",
        subject="Science",
    )

    print("=" * 70)
    print(f"DIAGNOSTIC ASSESSMENT: {results.diagnostic_id}")
    print("=" * 70)
    print(f"Class: {results.class_id}")
    print(f"Concepts: {', '.join(results.concept_ids)}")
    print(f"Questions: {len(results.questions)}")
    print(f"Students Assessed: {len(results.student_estimates)}")
    print(f"Cost: ${results.cost:.4f}")
    print("\n")

    # Display questions
    print("=" * 70)
    print("DIAGNOSTIC QUESTIONS")
    print("=" * 70)
    for q in results.questions:
        print(f"\n[{q.question_id}] ({q.difficulty_level})")
        print(f"{q.question_text}")
        if q.options:
            for opt in q.options:
                print(f"  {opt}")
        print(f"Correct Answer: {q.correct_answer}")
        if q.explanation:
            print(f"Explanation: {q.explanation}")

    # Display tier distribution
    print("\n" + "=" * 70)
    print("TIER DISTRIBUTION")
    print("=" * 70)
    print(f"Tier 1 (e75% mastery): {results.tier_distribution['tier_1']} students")
    print(f"Tier 2 (45-75% mastery): {results.tier_distribution['tier_2']} students")
    print(f"Tier 3 (<45% mastery): {results.tier_distribution['tier_3']} students")

    # Sample estimates
    print("\n" + "=" * 70)
    print("SAMPLE STUDENT ESTIMATES")
    print("=" * 70)
    for i, est in enumerate(results.student_estimates[:5]):
        print(f"\nStudent {est.student_id}:")
        print(f"  Mastery: {est.mastery_probability:.3f} ({est.confidence} confidence)")
        print(f"  Recommended Tier: {est.recommended_tier.value}")
        print(f"  Observations: {est.num_observations}")
