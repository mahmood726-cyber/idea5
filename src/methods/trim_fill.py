"""
Trim-and-fill method for publication bias correction.

The trim-and-fill method (Duval & Tweedie, 2000) is a nonparametric method
for estimating the number of missing studies and adjusting the meta-analysis
accordingly.

References:
    Duval, S., & Tweedie, R. (2000). Trim and fill: A simple funnel-plot-based
    method of testing and adjusting for publication bias in meta-analysis.
    Biometrics, 56(2), 455-463.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class TrimFillResult:
    """Results from trim-and-fill analysis."""
    n_missing: int
    side: str
    original_effect: float
    original_se: float
    original_ci: Tuple[float, float]
    adjusted_effect: float
    adjusted_se: float
    adjusted_ci: Tuple[float, float]
    filled_effect_sizes: np.ndarray
    filled_variances: np.ndarray
    interpretation: str

    def __repr__(self):
        return (
            f"Trim-and-Fill Analysis\n"
            f"{'=' * 60}\n"
            f"Estimated missing studies: {self.n_missing} ({self.side} side)\n"
            f"\n"
            f"Original pooled effect: {self.original_effect:.4f} "
            f"[{self.original_ci[0]:.4f}, {self.original_ci[1]:.4f}]\n"
            f"Adjusted pooled effect: {self.adjusted_effect:.4f} "
            f"[{self.adjusted_ci[0]:.4f}, {self.adjusted_ci[1]:.4f}]\n"
            f"\n{self.interpretation}"
        )


def trim_and_fill(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    estimator: str = 'L0',
    side: str = 'auto',
    alpha: float = 0.05
) -> TrimFillResult:
    """
    Trim-and-fill method for estimating and adjusting for publication bias.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of variances
        estimator: Method for estimating missing studies ('R0', 'L0', 'Q0')
            - R0: Based on rank of most extreme study
            - L0: Linear estimator (default, recommended)
            - Q0: Quadratic estimator
        side: Which side of funnel plot to trim ('left', 'right', 'auto')
        alpha: Significance level for confidence intervals

    Returns:
        TrimFillResult object with original and adjusted estimates
    """
    n = len(effect_sizes)
    weights = 1 / variances

    # Original pooled estimate (fixed-effect)
    original_effect = np.sum(weights * effect_sizes) / np.sum(weights)
    original_se = np.sqrt(1 / np.sum(weights))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    original_ci = (
        original_effect - z_crit * original_se,
        original_effect + z_crit * original_se
    )

    # Determine which side to trim
    if side == 'auto':
        # Center effect sizes around pooled estimate
        centered = effect_sizes - original_effect
        # Determine asymmetry direction
        left_tail = np.sum(centered < 0)
        right_tail = np.sum(centered > 0)
        side = 'right' if left_tail > right_tail else 'left'

    # Rank studies by effect size
    if side == 'left':
        # Missing studies on left (negative side)
        ranks = np.argsort(effect_sizes)
    else:
        # Missing studies on right (positive side)
        ranks = np.argsort(-effect_sizes)

    # Iterative trimming procedure
    n_trim = _estimate_missing_studies(
        effect_sizes[ranks],
        variances[ranks],
        estimator,
        side
    )

    if n_trim == 0:
        # No trimming needed
        return TrimFillResult(
            n_missing=0,
            side=side,
            original_effect=original_effect,
            original_se=original_se,
            original_ci=original_ci,
            adjusted_effect=original_effect,
            adjusted_se=original_se,
            adjusted_ci=original_ci,
            filled_effect_sizes=effect_sizes.copy(),
            filled_variances=variances.copy(),
            interpretation="No publication bias detected. No adjustment needed."
        )

    # Trim extreme studies
    trimmed_indices = ranks[n_trim:]
    trimmed_effects = effect_sizes[trimmed_indices]
    trimmed_vars = variances[trimmed_indices]

    # Estimate center of symmetric funnel
    trimmed_weights = 1 / trimmed_vars
    center = np.sum(trimmed_weights * trimmed_effects) / np.sum(trimmed_weights)

    # Fill in missing studies (mirror image)
    filled_effects_new = []
    filled_vars_new = []

    for i in range(n_trim):
        original_idx = ranks[i]
        original_effect = effect_sizes[original_idx]
        original_var = variances[original_idx]

        # Mirror around center
        mirrored_effect = 2 * center - original_effect
        filled_effects_new.append(mirrored_effect)
        filled_vars_new.append(original_var)

    # Combine original and filled studies
    filled_effects = np.concatenate([effect_sizes, filled_effects_new])
    filled_vars = np.concatenate([variances, filled_vars_new])

    # Adjusted pooled estimate
    filled_weights = 1 / filled_vars
    adjusted_effect = np.sum(filled_weights * filled_effects) / np.sum(filled_weights)
    adjusted_se = np.sqrt(1 / np.sum(filled_weights))
    adjusted_ci = (
        adjusted_effect - z_crit * adjusted_se,
        adjusted_effect + z_crit * adjusted_se
    )

    # Interpretation
    change = abs(adjusted_effect - original_effect)
    relative_change = 100 * change / abs(original_effect) if original_effect != 0 else 0

    interpretation = (
        f"Trim-and-fill suggests {n_trim} missing studies on the {side} side.\n"
        f"The adjusted effect estimate changed by {change:.4f} ({relative_change:.1f}%).\n"
    )

    if relative_change > 10:
        interpretation += (
            f"Substantial change in effect estimate suggests publication bias may\n"
            f"be affecting the meta-analysis results."
        )
    else:
        interpretation += (
            f"Modest change in effect estimate. Publication bias appears limited."
        )

    return TrimFillResult(
        n_missing=n_trim,
        side=side,
        original_effect=original_effect,
        original_se=original_se,
        original_ci=original_ci,
        adjusted_effect=adjusted_effect,
        adjusted_se=adjusted_se,
        adjusted_ci=adjusted_ci,
        filled_effect_sizes=filled_effects,
        filled_variances=filled_vars,
        interpretation=interpretation
    )


def _estimate_missing_studies(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    estimator: str,
    side: str
) -> int:
    """
    Estimate number of missing studies using iterative algorithm.

    Parameters:
        effect_sizes: Sorted array of effect sizes
        variances: Corresponding variances
        estimator: Estimation method ('R0', 'L0', 'Q0')
        side: Side being trimmed

    Returns:
        Estimated number of missing studies
    """
    n = len(effect_sizes)
    n_trim = 0

    for k in range(n):
        if k == 0:
            # No trimming yet
            gamma_k = _calculate_gamma(effect_sizes, variances, 0, estimator)
        else:
            # Trim k most extreme studies
            trimmed_effects = effect_sizes[k:]
            trimmed_vars = variances[k:]
            gamma_k = _calculate_gamma(trimmed_effects, trimmed_vars, k, estimator)

        # Check if we should continue trimming
        if gamma_k < k:
            break
        n_trim = k

    return int(n_trim)


def _calculate_gamma(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    n_trimmed: int,
    estimator: str
) -> float:
    """
    Calculate gamma statistic for trim-and-fill.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of variances
        n_trimmed: Number of studies already trimmed
        estimator: Estimation method

    Returns:
        Gamma statistic
    """
    n = len(effect_sizes)
    if n == 0:
        return 0

    # Centered effect sizes
    weights = 1 / variances
    center = np.sum(weights * effect_sizes) / np.sum(weights)
    centered = effect_sizes - center

    # Signed ranks
    abs_centered = np.abs(centered)
    ranks = stats.rankdata(abs_centered)
    signed_ranks = ranks * np.sign(centered)

    if estimator == 'R0':
        # Rank-based estimator
        T = np.sum(signed_ranks)
        gamma = (T - 0.5 * n * (n + 1)) / n
    elif estimator == 'L0':
        # Linear estimator (default)
        T = np.sum(signed_ranks)
        S = np.sum(ranks)
        gamma = (4 * T - n * (n + 1)) / (2 * n - 1)
    elif estimator == 'Q0':
        # Quadratic estimator
        T = np.sum(signed_ranks)
        gamma = (T - n * (n + 1) / 4) / np.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    else:
        raise ValueError(f"Unknown estimator: {estimator}")

    return max(0, gamma)
