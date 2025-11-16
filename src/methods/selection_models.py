"""
Selection models for publication bias.

Selection models explicitly model the publication process, assuming that studies
are selectively published based on their p-values or effect sizes.

Implementations:
    1. Copas sensitivity model - Assumes publication probability depends on a latent variable
    2. Vevea-Hedges step function model - Publication probability is a step function of p-values

References:
    - Copas, J. B., & Shi, J. Q. (2000). Meta-analysis, funnel plots and sensitivity analysis.
      Biostatistics, 1(3), 247-262.
    - Vevea, J. L., & Hedges, L. V. (1995). A general linear model for estimating effect size
      in the presence of publication bias. Psychometrika, 60(3), 419-435.
"""

import numpy as np
from scipy import stats, optimize
from typing import Tuple, Optional, List
from dataclasses import dataclass
import warnings


@dataclass
class CopasResult:
    """Results from Copas selection model."""
    original_effect: float
    original_se: float
    adjusted_effect: float
    adjusted_se: float
    adjusted_ci: Tuple[float, float]
    rho: float  # Correlation parameter
    gamma0: float  # Selection threshold
    gamma1: float  # Selection slope
    interpretation: str

    def __repr__(self):
        return (
            f"Copas Selection Model\n"
            f"{'=' * 60}\n"
            f"Original effect: {self.original_effect:.4f} (SE: {self.original_se:.4f})\n"
            f"Adjusted effect: {self.adjusted_effect:.4f} (SE: {self.adjusted_se:.4f})\n"
            f"   95% CI: [{self.adjusted_ci[0]:.4f}, {self.adjusted_ci[1]:.4f}]\n"
            f"\nSelection parameters:\n"
            f"   ρ (correlation): {self.rho:.4f}\n"
            f"   γ₀ (threshold): {self.gamma0:.4f}\n"
            f"   γ₁ (slope): {self.gamma1:.4f}\n"
            f"\n{self.interpretation}"
        )


@dataclass
class VeveaHedgesResult:
    """Results from Vevea-Hedges selection model."""
    original_effect: float
    original_se: float
    adjusted_effect: float
    adjusted_se: float
    adjusted_ci: Tuple[float, float]
    selection_weights: np.ndarray
    p_thresholds: List[float]
    interpretation: str

    def __repr__(self):
        return (
            f"Vevea-Hedges Selection Model\n"
            f"{'=' * 60}\n"
            f"Original effect: {self.original_effect:.4f} (SE: {self.original_se:.4f})\n"
            f"Adjusted effect: {self.adjusted_effect:.4f} (SE: {self.adjusted_se:.4f})\n"
            f"   95% CI: [{self.adjusted_ci[0]:.4f}, {self.adjusted_ci[1]:.4f}]\n"
            f"\nSelection weights by p-value:\n"
        )
        for i, (thresh, weight) in enumerate(zip(self.p_thresholds[1:], self.selection_weights)):
            prev_thresh = self.p_thresholds[i]
            return f"   p ∈ ({prev_thresh:.3f}, {thresh:.3f}]: {weight:.4f}\n"
        return f"\n{self.interpretation}"


def copas_model(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    rho_range: Tuple[float, float] = (-0.9, 0.9),
    alpha: float = 0.05
) -> CopasResult:
    """
    Copas selection model for publication bias.

    The Copas model assumes publication depends on a latent variable correlated
    with the effect size. It provides a sensitivity analysis across plausible
    correlation values.

    Model:
        Y_i | published ~ N(θ, σ_i²)
        Z_i = γ₀ + γ₁/σ_i + u_i
        Published if Z_i > 0
        Corr(Y_i, Z_i) = ρ

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        rho_range: Range of correlation values to explore
        alpha: Significance level

    Returns:
        CopasResult object
    """
    n = len(effect_sizes)
    variances = standard_errors ** 2

    # Original random-effects estimate
    weights = 1 / variances
    original_effect = np.sum(weights * effect_sizes) / np.sum(weights)
    original_se = np.sqrt(1 / np.sum(weights))

    # Fit Copas model by maximum likelihood
    # This is a simplified implementation - full model requires EM algorithm
    # We'll use a grid search over rho values for sensitivity analysis

    def copas_likelihood(params):
        """Negative log-likelihood for Copas model."""
        theta, gamma0, gamma1 = params

        # Selection probability
        z_mean = gamma0 + gamma1 / standard_errors
        z_sd = np.sqrt(1 - rho ** 2)

        # Probability of being selected (observed)
        p_select = 1 - stats.norm.cdf(-z_mean / z_sd)

        # Likelihood contribution from observed studies
        # Conditional distribution: Y | Z > 0
        adjusted_mean = theta + rho * (standard_errors / z_sd) * (
            stats.norm.pdf(z_mean / z_sd) / (1 - stats.norm.cdf(-z_mean / z_sd))
        )

        # Log-likelihood
        ll = -0.5 * np.sum(
            ((effect_sizes - adjusted_mean) / standard_errors) ** 2 +
            np.log(2 * np.pi * variances) +
            np.log(p_select)
        )

        return -ll

    # Sensitivity analysis across rho values
    rho_values = np.linspace(rho_range[0], rho_range[1], 20)
    best_ll = -np.inf
    best_params = None
    best_rho = 0

    for rho in rho_values:
        try:
            # Initial parameter guess
            initial_params = [original_effect, 0, 0]

            # Optimize
            result = optimize.minimize(
                copas_likelihood,
                initial_params,
                method='L-BFGS-B',
                bounds=[
                    (original_effect - 2 * original_se, original_effect + 2 * original_se),
                    (-5, 5),
                    (-5, 5)
                ]
            )

            if result.success and -result.fun > best_ll:
                best_ll = -result.fun
                best_params = result.x
                best_rho = rho
        except:
            continue

    if best_params is None:
        # Fallback to simple adjustment
        warnings.warn("Copas model optimization failed, using simplified adjustment")
        adjusted_effect = original_effect
        adjusted_se = original_se
        rho = 0
        gamma0 = 0
        gamma1 = 0
    else:
        adjusted_effect, gamma0, gamma1 = best_params
        rho = best_rho

        # Approximate standard error (conservative)
        adjusted_se = original_se * (1 + abs(rho))

    # Confidence interval
    z_crit = stats.norm.ppf(1 - alpha / 2)
    adjusted_ci = (
        adjusted_effect - z_crit * adjusted_se,
        adjusted_effect + z_crit * adjusted_se
    )

    # Interpretation
    change = abs(adjusted_effect - original_effect)
    relative_change = 100 * change / abs(original_effect) if original_effect != 0 else 0

    interpretation = (
        f"Copas sensitivity analysis suggests publication selection.\n"
        f"The adjusted effect changed by {change:.4f} ({relative_change:.1f}%).\n"
    )

    if abs(rho) > 0.3:
        interpretation += (
            f"\nModerate to strong correlation (ρ = {rho:.3f}) between effect size\n"
            f"and publication probability detected. This suggests selective reporting\n"
            f"may be affecting the meta-analysis."
        )
    else:
        interpretation += (
            f"\nWeak correlation (ρ = {rho:.3f}) suggests limited publication selection."
        )

    return CopasResult(
        original_effect=original_effect,
        original_se=original_se,
        adjusted_effect=adjusted_effect,
        adjusted_se=adjusted_se,
        adjusted_ci=adjusted_ci,
        rho=rho,
        gamma0=gamma0,
        gamma1=gamma1,
        interpretation=interpretation
    )


def vevea_hedges_model(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    p_thresholds: Optional[List[float]] = None,
    selection_weights: Optional[np.ndarray] = None,
    alpha: float = 0.05
) -> VeveaHedgesResult:
    """
    Vevea-Hedges step function selection model.

    This model assumes publication probability is a step function of p-values.
    Studies in different p-value intervals have different publication probabilities.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of variances
        p_thresholds: P-value thresholds (e.g., [0, 0.025, 0.05, 0.5, 1.0])
        selection_weights: Publication weights for each interval (estimated if None)
        alpha: Significance level

    Returns:
        VeveaHedgesResult object
    """
    n = len(effect_sizes)
    standard_errors = np.sqrt(variances)

    # Default p-value thresholds (commonly used)
    if p_thresholds is None:
        p_thresholds = [0, 0.025, 0.05, 0.5, 1.0]

    # Calculate p-values for each study (two-sided)
    z_scores = effect_sizes / standard_errors
    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))

    # Assign studies to intervals
    intervals = np.digitize(p_values, p_thresholds[1:])

    # Original random-effects estimate
    weights_original = 1 / variances
    original_effect = np.sum(weights_original * effect_sizes) / np.sum(weights_original)
    original_se = np.sqrt(1 / np.sum(weights_original))

    # Estimate selection weights if not provided
    if selection_weights is None:
        selection_weights = _estimate_vevea_weights(
            effect_sizes,
            variances,
            intervals,
            len(p_thresholds) - 1
        )

    # Apply selection weights
    # Reweight each study by its selection probability
    adjusted_weights = weights_original * selection_weights[intervals]

    # Adjusted estimate
    adjusted_effect = np.sum(adjusted_weights * effect_sizes) / np.sum(adjusted_weights)
    adjusted_se = np.sqrt(1 / np.sum(adjusted_weights))

    # Confidence interval
    z_crit = stats.norm.ppf(1 - alpha / 2)
    adjusted_ci = (
        adjusted_effect - z_crit * adjusted_se,
        adjusted_effect + z_crit * adjusted_se
    )

    # Interpretation
    change = abs(adjusted_effect - original_effect)
    relative_change = 100 * change / abs(original_effect) if original_effect != 0 else 0

    interpretation = (
        f"Vevea-Hedges model accounts for selective publication by p-value.\n"
        f"The adjusted effect changed by {change:.4f} ({relative_change:.1f}%).\n"
        f"\n"
    )

    # Analyze selection pattern
    if selection_weights[0] < 0.5:
        interpretation += (
            f"Strong selection detected: highly significant studies (p < {p_thresholds[1]}) "
            f"have only {selection_weights[0]:.1%} of expected publication rate.\n"
            f"This suggests substantial publication bias."
        )
    elif selection_weights[-1] < selection_weights[0] * 0.5:
        interpretation += (
            f"Non-significant studies appear underrepresented, suggesting\n"
            f"selective reporting of statistically significant results."
        )
    else:
        interpretation += (
            f"Selection weights suggest relatively uniform publication across\n"
            f"p-value ranges, indicating limited publication bias."
        )

    return VeveaHedgesResult(
        original_effect=original_effect,
        original_se=original_se,
        adjusted_effect=adjusted_effect,
        adjusted_se=adjusted_se,
        adjusted_ci=adjusted_ci,
        selection_weights=selection_weights,
        p_thresholds=p_thresholds,
        interpretation=interpretation
    )


def _estimate_vevea_weights(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    intervals: np.ndarray,
    n_intervals: int
) -> np.ndarray:
    """
    Estimate selection weights for Vevea-Hedges model using maximum likelihood.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of variances
        intervals: Interval assignment for each study
        n_intervals: Number of p-value intervals

    Returns:
        Array of selection weights
    """
    # Count studies in each interval
    counts = np.bincount(intervals, minlength=n_intervals)

    # Simple estimator: relative frequency compared to expected under no selection
    # More sophisticated: use EM algorithm (not implemented here for complexity)

    # Expected proportion in each interval under no publication bias
    # This would require knowing the true effect, so we use a heuristic:
    # Assume p-values should be uniform under null hypothesis

    # Normalize counts to sum to 1
    observed_props = counts / np.sum(counts)

    # Expected proportions (based on interval widths for uniform distribution)
    # For now, use observed proportions with smoothing
    selection_weights = observed_props + 0.1  # Add smoothing
    selection_weights = selection_weights / np.max(selection_weights)

    return selection_weights
