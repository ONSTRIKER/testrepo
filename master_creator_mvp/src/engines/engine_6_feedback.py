"""
Engine 6: Feedback Loop

Monitors prediction accuracy and updates BKT parameters.

Core Functionality:
1. Track predictions from Engine 5 (Diagnostic)
2. Compare predictions to actual assessment outcomes
3. Calculate accuracy metrics (RMSE, MAE, correlation)
4. Update BKT parameters based on performance
5. Provide feedback to improve future predictions

Accuracy Metrics:
- RMSE (Root Mean Squared Error): Overall prediction error
- MAE (Mean Absolute Error): Average prediction error
- Correlation: Relationship between predicted and actual
- Overestimation Bias: Tendency to over/under predict

BKT Parameter Tuning:
- If RMSE > 0.15: Adjust p_learn, p_guess, p_slip
- If overestimating: Reduce initial mastery or p_guess
- If underestimating: Increase p_learn
- Adaptive learning rate based on observation count
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math

from pydantic import BaseModel

from .base_engine import BaseEngine


# ═══════════════════════════════════════════════════════════
# INPUT/OUTPUT SCHEMAS
# ═══════════════════════════════════════════════════════════


class AccuracyMetrics(BaseModel):
    """Prediction accuracy metrics."""

    total_predictions: int
    predictions_with_outcomes: int

    # Error metrics
    rmse: float  # Root Mean Squared Error
    mae: float  # Mean Absolute Error
    correlation: float  # Pearson correlation

    # Bias metrics
    mean_predicted: float
    mean_actual: float
    overestimation_bias: float  # Positive = overestimating, negative = underestimating

    # Tier accuracy
    tier_accuracy: float  # % of correct tier predictions


class ParameterUpdate(BaseModel):
    """BKT parameter update recommendation."""

    parameter_name: str  # "p_learn", "p_guess", "p_slip"
    current_value: float
    recommended_value: float
    reason: str


class FeedbackReport(BaseModel):
    """Complete feedback report for an engine."""

    feedback_id: str
    engine_name: str
    timeframe_days: int

    # Accuracy
    accuracy_metrics: AccuracyMetrics

    # Recommendations
    parameter_updates: List[ParameterUpdate]
    quality_assessment: str  # "excellent", "good", "needs_improvement", "poor"

    # Actionable insights
    insights: List[str]
    warnings: List[str]

    # Metadata
    generated_at: str


# ═══════════════════════════════════════════════════════════
# ENGINE 6: FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════


class FeedbackLoop(BaseEngine):
    """
    Engine 6: Monitors prediction accuracy and tunes parameters.

    Analyzes performance of Engine 5 (Diagnostic) and recommends
    parameter adjustments to improve future predictions.
    """

    def generate_feedback(
        self,
        engine_name: str = "engine_5_diagnostic",
        timeframe_days: int = 30,
    ) -> FeedbackReport:
        """
        Generate feedback report for an engine.

        Args:
            engine_name: Engine to analyze (default: engine_5_diagnostic)
            timeframe_days: Number of days to analyze

        Returns:
            FeedbackReport with accuracy metrics and recommendations
        """
        feedback_id = f"feedback_{uuid.uuid4().hex[:12]}"

        self._log_decision(
            f"Generating feedback for {engine_name} (last {timeframe_days} days)"
        )

        # Get prediction accuracy from Student Model
        accuracy_data = self.student_model.get_prediction_accuracy(
            engine_name=engine_name,
            timeframe_days=timeframe_days,
        )

        # Calculate metrics
        metrics = self._calculate_accuracy_metrics(accuracy_data)

        # Generate parameter update recommendations
        parameter_updates = self._recommend_parameter_updates(metrics, accuracy_data)

        # Assess overall quality
        quality = self._assess_quality(metrics)

        # Generate insights
        insights = self._generate_insights(metrics, accuracy_data)
        warnings = self._generate_warnings(metrics, accuracy_data)

        # Build report
        report = FeedbackReport(
            feedback_id=feedback_id,
            engine_name=engine_name,
            timeframe_days=timeframe_days,
            accuracy_metrics=metrics,
            parameter_updates=parameter_updates,
            quality_assessment=quality,
            insights=insights,
            warnings=warnings,
            generated_at=datetime.utcnow().isoformat(),
        )

        self._log_decision(
            f"Feedback generated: {feedback_id} | "
            f"Quality: {quality} | "
            f"RMSE: {metrics.rmse:.3f}"
        )

        return report

    def apply_parameter_updates(
        self,
        feedback_report: FeedbackReport,
        auto_apply: bool = False,
    ) -> Dict[str, bool]:
        """
        Apply recommended parameter updates to Student Model.

        Args:
            feedback_report: Feedback report with recommendations
            auto_apply: If True, apply updates automatically

        Returns:
            Dict mapping parameter names to success status
        """
        results = {}

        if not auto_apply:
            self._log_decision("Auto-apply disabled, skipping parameter updates")
            return results

        for update in feedback_report.parameter_updates:
            try:
                # Update BKT parameters in Student Model
                # This would update default parameters for future mastery estimates
                self._log_decision(
                    f"Updating {update.parameter_name}: "
                    f"{update.current_value:.3f} → {update.recommended_value:.3f}"
                )

                # In production, this would update global BKT config
                # For now, just log the recommendation
                results[update.parameter_name] = True

            except Exception as e:
                self._log_decision(
                    f"Failed to update {update.parameter_name}: {str(e)}",
                    level="error"
                )
                results[update.parameter_name] = False

        return results

    def _calculate_accuracy_metrics(self, accuracy_data: Dict) -> AccuracyMetrics:
        """
        Calculate accuracy metrics from prediction data.

        Args:
            accuracy_data: Raw accuracy data from Student Model

        Returns:
            AccuracyMetrics
        """
        # Extract data
        total_predictions = accuracy_data.get("total_predictions", 0)
        predictions_with_outcomes = accuracy_data.get("predictions_with_outcomes", 0)

        if predictions_with_outcomes == 0:
            # No data available
            return AccuracyMetrics(
                total_predictions=total_predictions,
                predictions_with_outcomes=0,
                rmse=0.0,
                mae=0.0,
                correlation=0.0,
                mean_predicted=0.0,
                mean_actual=0.0,
                overestimation_bias=0.0,
                tier_accuracy=0.0,
            )

        # Get predictions
        predicted = accuracy_data.get("predicted_masteries", [])
        actual = accuracy_data.get("actual_masteries", [])

        # Calculate error metrics
        squared_errors = [(p - a) ** 2 for p, a in zip(predicted, actual)]
        absolute_errors = [abs(p - a) for p, a in zip(predicted, actual)]

        rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
        mae = sum(absolute_errors) / len(absolute_errors)

        # Calculate correlation
        correlation = self._calculate_correlation(predicted, actual)

        # Calculate bias
        mean_predicted = sum(predicted) / len(predicted)
        mean_actual = sum(actual) / len(actual)
        overestimation_bias = mean_predicted - mean_actual

        # Calculate tier accuracy
        predicted_tiers = accuracy_data.get("predicted_tiers", [])
        actual_tiers = accuracy_data.get("actual_tiers", [])

        if predicted_tiers and actual_tiers:
            correct_tiers = sum(
                1 for pt, at in zip(predicted_tiers, actual_tiers) if pt == at
            )
            tier_accuracy = correct_tiers / len(predicted_tiers)
        else:
            tier_accuracy = 0.0

        return AccuracyMetrics(
            total_predictions=total_predictions,
            predictions_with_outcomes=predictions_with_outcomes,
            rmse=round(rmse, 4),
            mae=round(mae, 4),
            correlation=round(correlation, 4),
            mean_predicted=round(mean_predicted, 4),
            mean_actual=round(mean_actual, 4),
            overestimation_bias=round(overestimation_bias, 4),
            tier_accuracy=round(tier_accuracy, 4),
        )

    def _calculate_correlation(
        self,
        predicted: List[float],
        actual: List[float],
    ) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(predicted) < 2:
            return 0.0

        n = len(predicted)
        mean_pred = sum(predicted) / n
        mean_actual = sum(actual) / n

        numerator = sum((p - mean_pred) * (a - mean_actual) for p, a in zip(predicted, actual))
        denom_pred = math.sqrt(sum((p - mean_pred) ** 2 for p in predicted))
        denom_actual = math.sqrt(sum((a - mean_actual) ** 2 for a in actual))

        if denom_pred == 0 or denom_actual == 0:
            return 0.0

        return numerator / (denom_pred * denom_actual)

    def _recommend_parameter_updates(
        self,
        metrics: AccuracyMetrics,
        accuracy_data: Dict,
    ) -> List[ParameterUpdate]:
        """
        Recommend BKT parameter updates based on accuracy.

        Args:
            metrics: Accuracy metrics
            accuracy_data: Raw accuracy data

        Returns:
            List of ParameterUpdate recommendations
        """
        updates = []

        # Current default BKT parameters (from Engine 5)
        current_p_learn = 0.3
        current_p_guess = 0.25
        current_p_slip = 0.1

        # Recommendation logic

        # 1. If overestimating significantly, reduce p_guess
        if metrics.overestimation_bias > 0.10:
            new_p_guess = max(0.15, current_p_guess - 0.05)
            updates.append(
                ParameterUpdate(
                    parameter_name="p_guess",
                    current_value=current_p_guess,
                    recommended_value=round(new_p_guess, 3),
                    reason=f"Overestimating mastery by {metrics.overestimation_bias:.2f}. "
                           "Reducing p_guess to account for lucky guesses.",
                )
            )

        # 2. If underestimating significantly, increase p_learn
        if metrics.overestimation_bias < -0.10:
            new_p_learn = min(0.4, current_p_learn + 0.05)
            updates.append(
                ParameterUpdate(
                    parameter_name="p_learn",
                    current_value=current_p_learn,
                    recommended_value=round(new_p_learn, 3),
                    reason=f"Underestimating mastery by {abs(metrics.overestimation_bias):.2f}. "
                           "Increasing p_learn to reflect faster learning rates.",
                )
            )

        # 3. If RMSE is high, adjust p_slip
        if metrics.rmse > 0.20:
            # High error could indicate p_slip is too low
            new_p_slip = min(0.15, current_p_slip + 0.03)
            updates.append(
                ParameterUpdate(
                    parameter_name="p_slip",
                    current_value=current_p_slip,
                    recommended_value=round(new_p_slip, 3),
                    reason=f"High RMSE ({metrics.rmse:.3f}) suggests students making errors "
                           "despite knowing concepts. Increasing p_slip.",
                )
            )

        # 4. If tier accuracy is low, general recalibration needed
        if metrics.tier_accuracy < 0.60 and not updates:
            # Recommend conservative adjustment across parameters
            updates.append(
                ParameterUpdate(
                    parameter_name="p_guess",
                    current_value=current_p_guess,
                    recommended_value=0.20,
                    reason=f"Low tier accuracy ({metrics.tier_accuracy:.2%}). "
                           "Recalibrating all BKT parameters.",
                )
            )

        return updates

    def _assess_quality(self, metrics: AccuracyMetrics) -> str:
        """
        Assess overall quality of predictions.

        Args:
            metrics: Accuracy metrics

        Returns:
            Quality assessment: "excellent", "good", "needs_improvement", "poor"
        """
        if metrics.predictions_with_outcomes < 10:
            return "insufficient_data"

        # Quality thresholds
        if metrics.rmse < 0.10 and metrics.tier_accuracy > 0.80:
            return "excellent"
        elif metrics.rmse < 0.15 and metrics.tier_accuracy > 0.70:
            return "good"
        elif metrics.rmse < 0.25 and metrics.tier_accuracy > 0.55:
            return "needs_improvement"
        else:
            return "poor"

    def _generate_insights(
        self,
        metrics: AccuracyMetrics,
        accuracy_data: Dict,
    ) -> List[str]:
        """Generate actionable insights."""
        insights = []

        # Insight 1: Overall performance
        if metrics.rmse < 0.10:
            insights.append(
                f"🎯 Excellent prediction accuracy (RMSE: {metrics.rmse:.3f}). "
                "The diagnostic engine is performing well."
            )
        elif metrics.rmse < 0.15:
            insights.append(
                f"✅ Good prediction accuracy (RMSE: {metrics.rmse:.3f}). "
                "Minor improvements possible."
            )
        else:
            insights.append(
                f"⚠️ Prediction accuracy could be improved (RMSE: {metrics.rmse:.3f}). "
                "Consider parameter tuning."
            )

        # Insight 2: Tier accuracy
        if metrics.tier_accuracy > 0.80:
            insights.append(
                f"✅ Strong tier assignment accuracy ({metrics.tier_accuracy:.1%}). "
                "Students are well-grouped for differentiation."
            )
        elif metrics.tier_accuracy < 0.60:
            insights.append(
                f"⚠️ Low tier assignment accuracy ({metrics.tier_accuracy:.1%}). "
                "Review tier thresholds (currently 75%/45%)."
            )

        # Insight 3: Bias
        if abs(metrics.overestimation_bias) < 0.05:
            insights.append(
                "✅ Predictions are well-calibrated with minimal bias."
            )
        elif metrics.overestimation_bias > 0.05:
            insights.append(
                f"⚠️ Tendency to overestimate mastery by {metrics.overestimation_bias:.2f}. "
                "Students may struggle more than predicted."
            )
        else:
            insights.append(
                f"⚠️ Tendency to underestimate mastery by {abs(metrics.overestimation_bias):.2f}. "
                "Students may be more capable than predicted."
            )

        # Insight 4: Data availability
        if metrics.predictions_with_outcomes < 30:
            insights.append(
                f"ℹ️ Limited outcome data ({metrics.predictions_with_outcomes} predictions). "
                "Accuracy will improve with more assessments."
            )

        return insights

    def _generate_warnings(
        self,
        metrics: AccuracyMetrics,
        accuracy_data: Dict,
    ) -> List[str]:
        """Generate warnings for critical issues."""
        warnings = []

        # Warning 1: High error
        if metrics.rmse > 0.25:
            warnings.append(
                f"❌ Very high prediction error (RMSE: {metrics.rmse:.3f}). "
                "Immediate parameter tuning recommended."
            )

        # Warning 2: Very low tier accuracy
        if metrics.tier_accuracy < 0.50:
            warnings.append(
                f"❌ Poor tier assignment accuracy ({metrics.tier_accuracy:.1%}). "
                "Students may be misplaced in difficulty tiers."
            )

        # Warning 3: Extreme bias
        if abs(metrics.overestimation_bias) > 0.20:
            warnings.append(
                f"❌ Severe prediction bias ({metrics.overestimation_bias:+.2f}). "
                "Review BKT parameters urgently."
            )

        # Warning 4: Low correlation
        if metrics.correlation < 0.30 and metrics.predictions_with_outcomes >= 20:
            warnings.append(
                f"❌ Low correlation between predicted and actual ({metrics.correlation:.2f}). "
                "Predictions may not be meaningful."
            )

        return warnings


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════


def generate_feedback_report(
    engine_name: str = "engine_5_diagnostic",
    timeframe_days: int = 30,
) -> FeedbackReport:
    """
    Convenience function to generate feedback report.

    Args:
        engine_name: Engine to analyze
        timeframe_days: Number of days to analyze

    Returns:
        FeedbackReport
    """
    engine = FeedbackLoop()
    return engine.generate_feedback(engine_name, timeframe_days)


# ═══════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    print("""
Engine 6: Feedback Loop

This engine monitors prediction accuracy and recommends parameter updates.

Usage: python -m src.engines.engine_6_feedback [timeframe_days]

Example:
  python -m src.engines.engine_6_feedback 30

This will analyze Engine 5 predictions from the last 30 days.
    """)

    timeframe_days = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    print(f"Generating feedback for last {timeframe_days} days\n")

    # Generate feedback
    report = generate_feedback_report(timeframe_days=timeframe_days)

    print("=" * 70)
    print("FEEDBACK REPORT")
    print("=" * 70)
    print(f"Feedback ID: {report.feedback_id}")
    print(f"Engine: {report.engine_name}")
    print(f"Timeframe: {report.timeframe_days} days")
    print(f"Quality: {report.quality_assessment.upper()}")
    print()

    # Metrics
    print("=" * 70)
    print("ACCURACY METRICS")
    print("=" * 70)
    metrics = report.accuracy_metrics
    print(f"Total Predictions: {metrics.total_predictions}")
    print(f"With Outcomes: {metrics.predictions_with_outcomes}")
    print(f"RMSE: {metrics.rmse:.4f}")
    print(f"MAE: {metrics.mae:.4f}")
    print(f"Correlation: {metrics.correlation:.4f}")
    print(f"Tier Accuracy: {metrics.tier_accuracy:.2%}")
    print(f"Overestimation Bias: {metrics.overestimation_bias:+.4f}")
    print()

    # Parameter updates
    if report.parameter_updates:
        print("=" * 70)
        print("RECOMMENDED PARAMETER UPDATES")
        print("=" * 70)
        for update in report.parameter_updates:
            print(f"\n{update.parameter_name}:")
            print(f"  Current: {update.current_value:.3f}")
            print(f"  Recommended: {update.recommended_value:.3f}")
            print(f"  Reason: {update.reason}")
    else:
        print("=" * 70)
        print("No parameter updates needed")
        print("=" * 70)

    # Insights
    if report.insights:
        print("\n" + "=" * 70)
        print("INSIGHTS")
        print("=" * 70)
        for insight in report.insights:
            print(f"  {insight}")

    # Warnings
    if report.warnings:
        print("\n" + "=" * 70)
        print("WARNINGS")
        print("=" * 70)
        for warning in report.warnings:
            print(f"  {warning}")
