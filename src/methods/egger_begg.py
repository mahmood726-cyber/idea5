"""
Egger's regression test and Begg's rank correlation test for publication bias.

References:
    - Egger, M., Smith, G. D., Schneider, M., & Minder, C. (1997). Bias in meta-analysis
      detected by a simple, graphical test. BMJ, 315(7109), 629-634.
    - Begg, C. B., & Mazumdar, M. (1994). Operating characteristics of a rank correlation
      test for publication bias. Biometrics, 50(4), 1088-1101.
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class EggerTestResult:
    """Results from Egger's regression test."""
    intercept: float
    intercept_se: float
    t_statistic: float
    p_value: float
    slope: float
    slope_se: float
    significant: bool
    interpretation: str

    def __repr__(self):
        return (
            f"Egger's Test\n"
            f"{'=' * 50}\n"
            f"Intercept: {self.intercept:.4f} (SE: {self.intercept_se:.4f})\n"
            f"t-statistic: {self.t_statistic:.4f}\n"
            f"p-value: {self.p_value:.4f}\n"
            f"Significant: {self.significant}\n"
            f"\n{self.interpretation}"
        )


@dataclass
class BeggTestResult:
    """Results from Begg's rank correlation test."""
    tau: float
    z_statistic: float
    p_value: float
    significant: bool
    interpretation: str

    def __repr__(self):
        return (
            f"Begg's Test\n"
            f"{'=' * 50}\n"
            f"Kendall's tau: {self.tau:.4f}\n"
            f"z-statistic: {self.z_statistic:.4f}\n"
            f"p-value: {self.p_value:.4f}\n"
            f"Significant: {self.significant}\n"
            f"\n{self.interpretation}"
        )


def egger_test(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05
) -> EggerTestResult:
    """
    Egger's regression test for funnel plot asymmetry.

    The test regresses the standardized effect (effect/SE) on precision (1/SE).
    A significant intercept indicates funnel plot asymmetry, suggesting publication bias.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        alpha: Significance level (default: 0.05)

    Returns:
        EggerTestResult object with test statistics and interpretation
    """
    # Calculate precision and standardized effect
    precision = 1 / standard_errors
    standardized_effect = effect_sizes / standard_errors

    # Weighted least squares regression
    # Model: standardized_effect = intercept + slope * precision
    # Weights: 1/variance of standardized effect = precision^2
    weights = precision

    # Design matrix
    X = np.column_stack([np.ones_like(precision), precision])

    # Weighted regression
    W = np.diag(weights)
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ standardized_effect

    # Coefficients
    beta = np.linalg.solve(XtWX, XtWy)
    intercept, slope = beta

    # Fitted values and residuals
    fitted = X @ beta
    residuals = standardized_effect - fitted

    # Variance estimation
    n = len(effect_sizes)
    df = n - 2
    mse = np.sum(weights * residuals ** 2) / df

    # Standard errors
    cov_matrix = mse * np.linalg.inv(XtWX)
    intercept_se = np.sqrt(cov_matrix[0, 0])
    slope_se = np.sqrt(cov_matrix[1, 1])

    # t-test for intercept
    t_statistic = intercept / intercept_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df))

    significant = p_value < alpha

    # Interpretation
    if significant:
        direction = "positive" if intercept > 0 else "negative"
        interpretation = (
            f"Significant funnel plot asymmetry detected (p < {alpha}).\n"
            f"The {direction} intercept suggests small-study effects, which may\n"
            f"indicate publication bias or genuine heterogeneity."
        )
    else:
        interpretation = (
            f"No significant funnel plot asymmetry detected (p >= {alpha}).\n"
            f"However, absence of asymmetry does not rule out publication bias,\n"
            f"especially with small meta-analyses."
        )

    return EggerTestResult(
        intercept=intercept,
        intercept_se=intercept_se,
        t_statistic=t_statistic,
        p_value=p_value,
        slope=slope,
        slope_se=slope_se,
        significant=significant,
        interpretation=interpretation
    )


def begg_test(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    alpha: float = 0.05
) -> BeggTestResult:
    """
    Begg's rank correlation test for publication bias.

    The test examines the correlation between effect sizes and their variances
    using Kendall's tau rank correlation coefficient.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of variances
        alpha: Significance level (default: 0.05)

    Returns:
        BeggTestResult object with test statistics and interpretation
    """
    # Standardize effect sizes by variance
    standardized_effects = effect_sizes / np.sqrt(variances)

    # Calculate Kendall's tau between standardized effects and variances
    tau, p_value_tau = stats.kendalltau(standardized_effects, variances)

    # For Begg's test, we use a different variance adjustment
    # Rank correlation between effect sizes and standard errors
    standard_errors = np.sqrt(variances)
    tau, _ = stats.kendalltau(effect_sizes, variances)

    # Calculate z-statistic
    n = len(effect_sizes)
    # Variance of tau under null hypothesis
    var_tau = 2 * (2 * n + 5) / (9 * n * (n - 1))
    z_statistic = tau / np.sqrt(var_tau)

    # Two-sided p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_statistic)))

    significant = p_value < alpha

    # Interpretation
    if significant:
        direction = "positive" if tau > 0 else "negative"
        interpretation = (
            f"Significant rank correlation detected (p < {alpha}).\n"
            f"The {direction} correlation between effect sizes and variances\n"
            f"suggests potential publication bias or small-study effects."
        )
    else:
        interpretation = (
            f"No significant rank correlation detected (p >= {alpha}).\n"
            f"Begg's test has low power, especially in small meta-analyses.\n"
            f"Consider using additional methods for comprehensive assessment."
        )

    return BeggTestResult(
        tau=tau,
        z_statistic=z_statistic,
        p_value=p_value,
        significant=significant,
        interpretation=interpretation
    )


def harbord_test(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05
) -> Dict:
    """
    Harbord's modified test for binary outcome data.

    More appropriate than Egger's test for binary outcomes (e.g., log odds ratios).

    Parameters:
        effect_sizes: Array of effect sizes (log odds ratios)
        standard_errors: Array of standard errors
        alpha: Significance level

    Returns:
        Dictionary with test results
    """
    # Z-scores
    z = effect_sizes / standard_errors

    # Variance
    v = standard_errors ** 2

    # Regression: Z/sqrt(V) ~ sqrt(V)
    y = z / np.sqrt(v)
    x = np.sqrt(v)

    # Weighted regression (weights = v)
    weights = v
    X = np.column_stack([np.ones_like(x), x])

    W = np.diag(weights)
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ y

    beta = np.linalg.solve(XtWX, XtWy)
    intercept, slope = beta

    # Standard errors
    fitted = X @ beta
    residuals = y - fitted
    n = len(effect_sizes)
    df = n - 2
    mse = np.sum(weights * residuals ** 2) / df

    cov_matrix = mse * np.linalg.inv(XtWX)
    intercept_se = np.sqrt(cov_matrix[0, 0])

    # t-test
    t_stat = intercept / intercept_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    return {
        'intercept': intercept,
        'intercept_se': intercept_se,
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < alpha
    }
