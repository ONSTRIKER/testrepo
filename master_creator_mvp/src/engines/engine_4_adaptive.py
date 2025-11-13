"""
Engine 4: Adaptive Personalization Engine

Generates personalized learning paths based on student mastery and ZPD.

Core Functionality:
1. Analyze student mastery across concepts
2. Identify Zone of Proximal Development (ZPD)
3. Generate adaptive learning paths
4. Recommend next-best content
5. Create branching logic for different trajectories

Zone of Proximal Development (ZPD):
- Target concepts at 40-60% mastery for optimal learning
- Too easy (<40%): Risk of boredom
- Too hard (>60%): Risk of frustration
- Just right (40-60%): Optimal challenge

Adaptive Strategies:
- Mastery-based progression (unlock next topic after 75% mastery)
- Spiral review (revisit concepts at increasing intervals)
- Peer grouping (cluster students with similar profiles)
- Content variation (different modalities for different learners)
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base_engine import BaseEngine
from ..student_model.schemas import StudentProfile, ConceptMastery


# ═══════════════════════════════════════════════════════════
# INPUT/OUTPUT SCHEMAS
# ═══════════════════════════════════════════════════════════


class ConceptRecommendation(BaseModel):
    """Recommendation for a specific concept."""

    concept_id: str
    concept_name: str
    current_mastery: float
    target_mastery: float
    in_zpd: bool  # True if in Zone of Proximal Development
    priority: str  # "high", "medium", "low"
    recommended_activities: List[str]
    estimated_time_minutes: int


class LearningPath(BaseModel):
    """Personalized learning path for a student."""

    student_id: str
    student_name: str
    path_id: str

    # Current state
    overall_mastery: float  # Average across all concepts
    mastered_concepts: List[str]  # ≥75% mastery
    developing_concepts: List[str]  # 45-75% mastery
    struggling_concepts: List[str]  # <45% mastery

    # Recommendations
    next_concepts: List[ConceptRecommendation]  # Prioritized by ZPD
    review_concepts: List[str]  # Concepts to review
    extension_concepts: List[str]  # Advanced concepts for mastered students

    # Peer grouping
    similar_students: List[str]  # Students with similar profiles
    suggested_group: str  # "advanced", "on_track", "needs_support"

    # Metadata
    generated_at: str


class ClassAdaptivePlan(BaseModel):
    """Adaptive plan for entire class."""

    class_id: str
    plan_id: str
    total_students: int

    # Grouping
    advanced_group: List[str]  # Students for extension
    on_track_group: List[str]  # Students on pace
    support_group: List[str]  # Students needing intervention

    # Class-wide recommendations
    concepts_to_reteach: List[str]  # <50% class mastery
    concepts_to_extend: List[str]  # >80% class mastery
    flexible_grouping_suggestions: List[Dict]  # Suggested groupings

    # Individual paths
    student_paths: List[LearningPath]

    # Metadata
    generated_at: str
    cost: float


# ═══════════════════════════════════════════════════════════
# ENGINE 4: ADAPTIVE PERSONALIZATION ENGINE
# ═══════════════════════════════════════════════════════════


class AdaptiveEngine(BaseEngine):
    """
    Engine 4: Generates personalized learning paths using ZPD.

    Analyzes student mastery and creates adaptive recommendations
    for optimal challenge and engagement.
    """

    def generate_student_path(
        self,
        student_id: str,
        concept_ids: List[str],
    ) -> LearningPath:
        """
        Generate personalized learning path for one student.

        Args:
            student_id: Student identifier
            concept_ids: Concepts to analyze

        Returns:
            LearningPath with personalized recommendations
        """
        path_id = f"path_{uuid.uuid4().hex[:12]}"

        self._log_decision(f"Generating learning path for student {student_id}")

        # Get student profile
        profile = self.student_model.get_student_profile(student_id)
        if not profile:
            raise ValueError(f"Student {student_id} not found")

        # Get mastery data
        mastery_records = self.student_model.retrieve_concept_mastery(
            student_id=student_id,
            concept_ids=concept_ids,
        )

        # Categorize concepts by mastery
        mastered = []
        developing = []
        struggling = []
        overall_mastery_sum = 0.0

        for record in mastery_records:
            mastery = record.mastery_probability
            overall_mastery_sum += mastery

            if mastery >= 0.75:
                mastered.append(record.concept_id)
            elif mastery >= 0.45:
                developing.append(record.concept_id)
            else:
                struggling.append(record.concept_id)

        overall_mastery = overall_mastery_sum / len(mastery_records) if mastery_records else 0.5

        # Generate recommendations (prioritize ZPD concepts)
        recommendations = self._generate_recommendations(
            student_id=student_id,
            mastery_records=mastery_records,
            profile=profile,
        )

        # Find similar students
        similar_students = self._find_similar_students(
            student_id=student_id,
            n_results=5,
        )

        # Determine suggested group
        if overall_mastery >= 0.75:
            suggested_group = "advanced"
            extension_concepts = self._get_extension_concepts(concept_ids, mastery_records)
        elif overall_mastery >= 0.45:
            suggested_group = "on_track"
            extension_concepts = []
        else:
            suggested_group = "needs_support"
            extension_concepts = []

        # Identify concepts to review
        review_concepts = [c for c in developing if len(developing) > 3][:3]

        # Build learning path
        path = LearningPath(
            student_id=student_id,
            student_name=profile.student_name,
            path_id=path_id,
            overall_mastery=round(overall_mastery, 3),
            mastered_concepts=mastered,
            developing_concepts=developing,
            struggling_concepts=struggling,
            next_concepts=recommendations,
            review_concepts=review_concepts,
            extension_concepts=extension_concepts,
            similar_students=similar_students,
            suggested_group=suggested_group,
            generated_at=datetime.utcnow().isoformat(),
        )

        self._log_decision(
            f"Learning path generated: {path_id} | "
            f"Overall mastery: {overall_mastery:.2f} | "
            f"Group: {suggested_group}"
        )

        return path

    def generate_class_plan(
        self,
        class_id: str,
        concept_ids: List[str],
    ) -> ClassAdaptivePlan:
        """
        Generate adaptive plan for entire class.

        Args:
            class_id: Class identifier
            concept_ids: Concepts to analyze

        Returns:
            ClassAdaptivePlan with grouping and recommendations
        """
        plan_id = f"adaptive_plan_{uuid.uuid4().hex[:12]}"

        self._log_decision(f"Generating adaptive plan for class {class_id}")

        # Get all students
        students = self.student_model.get_class_students(class_id)

        # Generate individual paths
        student_paths = []
        advanced_group = []
        on_track_group = []
        support_group = []

        for student in students:
            try:
                path = self.generate_student_path(
                    student_id=student.student_id,
                    concept_ids=concept_ids,
                )
                student_paths.append(path)

                # Assign to group
                if path.suggested_group == "advanced":
                    advanced_group.append(student.student_id)
                elif path.suggested_group == "on_track":
                    on_track_group.append(student.student_id)
                else:
                    support_group.append(student.student_id)

            except Exception as e:
                self._log_decision(f"Error generating path for {student.student_id}: {str(e)}", level="warning")

        # Analyze class-wide mastery
        class_mastery = self._analyze_class_mastery(class_id, concept_ids)

        # Determine concepts to reteach (low class mastery)
        concepts_to_reteach = [
            cid for cid, avg_mastery in class_mastery.items() if avg_mastery < 0.5
        ]

        # Determine concepts to extend (high class mastery)
        concepts_to_extend = [
            cid for cid, avg_mastery in class_mastery.items() if avg_mastery > 0.8
        ]

        # Generate flexible grouping suggestions
        flexible_grouping = self._generate_flexible_grouping(student_paths, concept_ids)

        # Build class plan
        plan = ClassAdaptivePlan(
            class_id=class_id,
            plan_id=plan_id,
            total_students=len(students),
            advanced_group=advanced_group,
            on_track_group=on_track_group,
            support_group=support_group,
            concepts_to_reteach=concepts_to_reteach,
            concepts_to_extend=concepts_to_extend,
            flexible_grouping_suggestions=flexible_grouping,
            student_paths=student_paths,
            generated_at=datetime.utcnow().isoformat(),
            cost=self.get_cost_summary()["total_cost"],
        )

        self._log_decision(
            f"Class plan generated: {plan_id} | "
            f"Advanced: {len(advanced_group)}, "
            f"On-track: {len(on_track_group)}, "
            f"Support: {len(support_group)}"
        )

        return plan

    def _generate_recommendations(
        self,
        student_id: str,
        mastery_records: List[ConceptMastery],
        profile: StudentProfile,
    ) -> List[ConceptRecommendation]:
        """
        Generate prioritized concept recommendations.

        Args:
            student_id: Student identifier
            mastery_records: Mastery data
            profile: Student profile

        Returns:
            List of ConceptRecommendation objects
        """
        recommendations = []

        for record in mastery_records:
            mastery = record.mastery_probability

            # Determine if in ZPD (40-60% mastery = optimal challenge)
            in_zpd = 0.40 <= mastery <= 0.60

            # Determine priority
            if in_zpd:
                priority = "high"
            elif mastery < 0.40:
                priority = "medium"  # Needs foundation building
            else:
                priority = "low"  # Already mastered or close

            # Target mastery
            target_mastery = 0.75

            # Recommend activities based on mastery level
            if mastery < 0.30:
                activities = [
                    "Review foundational concepts",
                    "Work with peer tutor or teacher",
                    "Complete scaffolded practice",
                ]
                estimated_time = 60
            elif mastery < 0.50:
                activities = [
                    "Guided practice with feedback",
                    "Conceptual videos and examples",
                    "Practice problems with hints",
                ]
                estimated_time = 45
            elif mastery < 0.75:
                activities = [
                    "Independent practice",
                    "Apply concepts to new contexts",
                    "Peer teaching opportunities",
                ]
                estimated_time = 30
            else:
                activities = [
                    "Extension activities",
                    "Real-world applications",
                    "Create teaching materials for peers",
                ]
                estimated_time = 20

            recommendations.append(
                ConceptRecommendation(
                    concept_id=record.concept_id,
                    concept_name=record.concept_id.replace("_", " ").title(),
                    current_mastery=round(mastery, 3),
                    target_mastery=target_mastery,
                    in_zpd=in_zpd,
                    priority=priority,
                    recommended_activities=activities,
                    estimated_time_minutes=estimated_time,
                )
            )

        # Sort by priority (high first, then medium, then low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order[r.priority])

        return recommendations

    def _find_similar_students(
        self,
        student_id: str,
        n_results: int = 5,
    ) -> List[str]:
        """
        Find students with similar learning profiles using vector search.

        Args:
            student_id: Student identifier
            n_results: Number of similar students to return

        Returns:
            List of similar student IDs
        """
        try:
            # Use Student Model's vector store for semantic similarity
            similar = self.student_model.vector_store.find_similar_students(
                student_id=student_id,
                n_results=n_results,
            )
            return similar
        except Exception as e:
            self._log_decision(f"Could not find similar students: {str(e)}", level="warning")
            return []

    def _get_extension_concepts(
        self,
        concept_ids: List[str],
        mastery_records: List[ConceptMastery],
    ) -> List[str]:
        """
        Get extension concepts for advanced students.

        Args:
            concept_ids: All concept IDs
            mastery_records: Student's mastery records

        Returns:
            List of extension concept IDs
        """
        # For now, return conceptual extensions
        # In production, this would query a concept graph
        mastered_ids = {r.concept_id for r in mastery_records if r.mastery_probability >= 0.75}

        # Simple heuristic: suggest related advanced concepts
        extensions = []
        for cid in concept_ids:
            if cid in mastered_ids:
                # Suggest advanced version
                extensions.append(f"{cid}_advanced")

        return extensions[:3]

    def _analyze_class_mastery(
        self,
        class_id: str,
        concept_ids: List[str],
    ) -> Dict[str, float]:
        """
        Analyze average mastery per concept across class.

        Args:
            class_id: Class identifier
            concept_ids: Concepts to analyze

        Returns:
            Dict mapping concept_id to average mastery
        """
        class_mastery = {}

        for concept_id in concept_ids:
            try:
                distribution = self.student_model.get_class_mastery_distribution(
                    class_id=class_id,
                    concept_id=concept_id,
                )
                class_mastery[concept_id] = distribution.average_mastery
            except Exception as e:
                self._log_decision(f"Could not get mastery for {concept_id}: {str(e)}", level="warning")
                class_mastery[concept_id] = 0.5

        return class_mastery

    def _generate_flexible_grouping(
        self,
        student_paths: List[LearningPath],
        concept_ids: List[str],
    ) -> List[Dict]:
        """
        Generate flexible grouping suggestions.

        Args:
            student_paths: All student learning paths
            concept_ids: Concepts

        Returns:
            List of grouping suggestions
        """
        groupings = []

        # Group by ZPD for each concept
        for concept_id in concept_ids[:3]:  # Top 3 concepts
            zpd_group = []
            for path in student_paths:
                for rec in path.next_concepts:
                    if rec.concept_id == concept_id and rec.in_zpd:
                        zpd_group.append(path.student_id)

            if len(zpd_group) >= 3:
                groupings.append({
                    "concept": concept_id,
                    "students": zpd_group,
                    "purpose": f"Small group instruction for {concept_id.replace('_', ' ')}",
                    "size": len(zpd_group),
                })

        return groupings


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def generate_adaptive_plan(
    class_id: str,
    concept_ids: List[str],
) -> ClassAdaptivePlan:
    """
    Convenience function to generate class adaptive plan.

    Args:
        class_id: Class identifier
        concept_ids: Concepts to analyze

    Returns:
        ClassAdaptivePlan
    """
    engine = AdaptiveEngine()
    return engine.generate_class_plan(class_id, concept_ids)


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("""
Usage: python -m src.engines.engine_4_adaptive <class_id> <concept_ids>

Example:
  python -m src.engines.engine_4_adaptive "class_bio_101" "photosynthesis_process,cellular_respiration"
        """)
        sys.exit(1)

    class_id = sys.argv[1]
    concept_ids = sys.argv[2].split(",")

    print(f"Generating adaptive plan for class {class_id}\n")

    # Generate adaptive plan
    plan = generate_adaptive_plan(class_id, concept_ids)

    print("=" * 70)
    print("CLASS ADAPTIVE PLAN")
    print("=" * 70)
    print(f"Plan ID: {plan.plan_id}")
    print(f"Total Students: {plan.total_students}")
    print(f"Cost: ${plan.cost:.4f}")
    print()

    print("=" * 70)
    print("GROUPING")
    print("=" * 70)
    print(f"Advanced Group: {len(plan.advanced_group)} students")
    print(f"On-Track Group: {len(plan.on_track_group)} students")
    print(f"Support Group: {len(plan.support_group)} students")
    print()

    print("=" * 70)
    print("CLASS-WIDE RECOMMENDATIONS")
    print("=" * 70)
    print(f"Concepts to Reteach (<50% mastery): {', '.join(plan.concepts_to_reteach) if plan.concepts_to_reteach else 'None'}")
    print(f"Concepts to Extend (>80% mastery): {', '.join(plan.concepts_to_extend) if plan.concepts_to_extend else 'None'}")
    print()

    if plan.flexible_grouping_suggestions:
        print("=" * 70)
        print("FLEXIBLE GROUPING SUGGESTIONS")
        print("=" * 70)
        for group in plan.flexible_grouping_suggestions:
            print(f"\n{group['purpose']}")
            print(f"  Students: {group['size']}")
            print(f"  Concept: {group['concept']}")

    # Show sample student paths
    print("\n" + "=" * 70)
    print("SAMPLE STUDENT PATHS")
    print("=" * 70)
    for path in plan.student_paths[:3]:
        print(f"\n{path.student_name} ({path.student_id})")
        print(f"  Overall Mastery: {path.overall_mastery:.2%}")
        print(f"  Group: {path.suggested_group}")
        print(f"  Mastered: {len(path.mastered_concepts)} concepts")
        print(f"  In ZPD: {sum(1 for r in path.next_concepts if r.in_zpd)} concepts")
        if path.next_concepts:
            top_rec = path.next_concepts[0]
            print(f"  Next Priority: {top_rec.concept_name} ({top_rec.priority} priority)")
