"""
PET-PEESE: Precision-Effect Test and Precision-Effect Estimate with Standard Error.

PET-PEESE is a meta-regression method for detecting and correcting publication bias.
It addresses the correlation between effect sizes and their standard errors.

References:
    Stanley, T. D., & Doucouliagos, H. (2014). Meta‐regression approximations to reduce
    publication selection bias. Research Synthesis Methods, 5(1), 60-78.

    Stanley, T. D. (2017). Limitations of PET-PEESE and other meta-analysis methods.
    Social Psychological and Personality Science, 8(5), 581-591.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class PETResult:
    """Results from Precision-Effect Test (PET)."""
    intercept: float
    intercept_se: float
    intercept_ci: Tuple[float, float]
    slope: float
    slope_se: float
    t_statistic: float
    p_value: float
    df: int
    significant_bias: bool
    interpretation: str

    def __repr__(self):
        return (
            f"PET (Precision-Effect Test)\n"
            f"{'=' * 60}\n"
            f"Effect estimate (intercept): {self.intercept:.4f} "
            f"[{self.intercept_ci[0]:.4f}, {self.intercept_ci[1]:.4f}]\n"
            f"Precision slope: {self.slope:.4f} (SE: {self.slope_se:.4f})\n"
            f"Bias test - t: {self.t_statistic:.4f}, p: {self.p_value:.4f}\n"
            f"Significant bias: {self.significant_bias}\n"
            f"\n{self.interpretation}"
        )


@dataclass
class PEESEResult:
    """Results from Precision-Effect Estimate with Standard Error (PEESE)."""
    intercept: float
    intercept_se: float
    intercept_ci: Tuple[float, float]
    slope: float
    slope_se: float
    df: int
    interpretation: str

    def __repr__(self):
        return (
            f"PEESE (Precision-Effect Estimate with SE)\n"
            f"{'=' * 60}\n"
            f"Effect estimate (intercept): {self.intercept:.4f} "
            f"[{self.intercept_ci[0]:.4f}, {self.intercept_ci[1]:.4f}]\n"
            f"Variance slope: {self.slope:.4f} (SE: {self.slope_se:.4f})\n"
            f"\n{self.interpretation}"
        )


@dataclass
class PETPEESEResult:
    """Combined PET-PEESE results with selection."""
    pet_result: PETResult
    peese_result: PEESEResult
    selected_estimate: float
    selected_ci: Tuple[float, float]
    selected_method: str
    bootstrap_ci: Optional[Tuple[float, float]]
    interpretation: str

    def __repr__(self):
        return (
            f"PET-PEESE Combined Analysis\n"
            f"{'=' * 60}\n"
            f"PET effect: {self.pet_result.intercept:.4f} "
            f"[{self.pet_result.intercept_ci[0]:.4f}, {self.pet_result.intercept_ci[1]:.4f}]\n"
            f"PEESE effect: {self.peese_result.intercept:.4f} "
            f"[{self.peese_result.intercept_ci[0]:.4f}, {self.peese_result.intercept_ci[1]:.4f}]\n"
            f"\n"
            f"Selected method: {self.selected_method}\n"
            f"Selected estimate: {self.selected_estimate:.4f} "
            f"[{self.selected_ci[0]:.4f}, {self.selected_ci[1]:.4f}]\n"
        )
        if self.bootstrap_ci:
            return (
                f"Bootstrap CI: [{self.bootstrap_ci[0]:.4f}, {self.bootstrap_ci[1]:.4f}]\n"
                f"\n{self.interpretation}"
            )


def pet_test(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05
) -> PETResult:
    """
    Precision-Effect Test (PET) for publication bias.

    PET regresses effect sizes on standard errors:
        effect_i = β₀ + β₁ * SE_i + ε_i

    The intercept (β₀) estimates the effect size at infinite precision (SE=0).
    The slope (β₁) tests for publication bias.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        alpha: Significance level

    Returns:
        PETResult object
    """
    n = len(effect_sizes)

    # Weighted least squares (weights = 1/SE²)
    weights = 1 / (standard_errors ** 2)

    # Design matrix: [1, SE]
    X = np.column_stack([np.ones(n), standard_errors])

    # Weighted regression
    W = np.diag(weights)
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ effect_sizes

    # Coefficients
    beta = np.linalg.solve(XtWX, XtWy)
    intercept, slope = beta

    # Fitted values and residuals
    fitted = X @ beta
    residuals = effect_sizes - fitted

    # Variance estimation
    df = n - 2
    mse = np.sum(weights * residuals ** 2) / df

    # Standard errors
    cov_matrix = mse * np.linalg.inv(XtWX)
    intercept_se = np.sqrt(cov_matrix[0, 0])
    slope_se = np.sqrt(cov_matrix[1, 1])

    # Confidence interval for intercept
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    intercept_ci = (
        intercept - t_crit * intercept_se,
        intercept + t_crit * intercept_se
    )

    # Test for publication bias (slope significantly different from 0)
    t_statistic = slope / slope_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df))
    significant_bias = p_value < alpha

    # Interpretation
    if significant_bias:
        direction = "positive" if slope > 0 else "negative"
        interpretation = (
            f"PET detects significant publication bias (p = {p_value:.4f}).\n"
            f"The {direction} slope suggests small-study effects.\n"
            f"The bias-corrected effect (intercept) is {intercept:.4f}.\n"
        )
        if abs(intercept) < abs(np.mean(effect_sizes)) * 0.5:
            interpretation += (
                "Note: PET may overcorrect for bias. Consider PEESE if the\n"
                "intercept is significantly different from zero."
            )
    else:
        interpretation = (
            f"PET does not detect significant publication bias (p = {p_value:.4f}).\n"
            f"However, PET has limited power in small meta-analyses.\n"
            f"The bias-corrected effect estimate is {intercept:.4f}."
        )

    return PETResult(
        intercept=intercept,
        intercept_se=intercept_se,
        intercept_ci=intercept_ci,
        slope=slope,
        slope_se=slope_se,
        t_statistic=t_statistic,
        p_value=p_value,
        df=df,
        significant_bias=significant_bias,
        interpretation=interpretation
    )


def peese_test(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05
) -> PEESEResult:
    """
    Precision-Effect Estimate with Standard Error (PEESE).

    PEESE regresses effect sizes on variance (SE²):
        effect_i = β₀ + β₁ * SE²_i + ε_i

    The intercept (β₀) estimates the bias-corrected effect size.
    PEESE is preferred when there is a genuine effect (PET intercept ≠ 0).

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        alpha: Significance level

    Returns:
        PEESEResult object
    """
    n = len(effect_sizes)
    variances = standard_errors ** 2

    # Weighted least squares (weights = 1/SE²)
    weights = 1 / variances

    # Design matrix: [1, SE²]
    X = np.column_stack([np.ones(n), variances])

    # Weighted regression
    W = np.diag(weights)
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ effect_sizes

    # Coefficients
    beta = np.linalg.solve(XtWX, XtWy)
    intercept, slope = beta

    # Fitted values and residuals
    fitted = X @ beta
    residuals = effect_sizes - fitted

    # Variance estimation
    df = n - 2
    mse = np.sum(weights * residuals ** 2) / df

    # Standard errors
    cov_matrix = mse * np.linalg.inv(XtWX)
    intercept_se = np.sqrt(cov_matrix[0, 0])
    slope_se = np.sqrt(cov_matrix[1, 1])

    # Confidence interval for intercept
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    intercept_ci = (
        intercept - t_crit * intercept_se,
        intercept + t_crit * intercept_se
    )

    # Interpretation
    interpretation = (
        f"PEESE bias-corrected effect estimate: {intercept:.4f}\n"
        f"[{intercept_ci[0]:.4f}, {intercept_ci[1]:.4f}]\n"
        f"\n"
        f"PEESE is recommended when there is evidence of a genuine effect.\n"
        f"The variance slope ({slope:.4f}) captures the relationship between\n"
        f"effect size and study precision."
    )

    return PEESEResult(
        intercept=intercept,
        intercept_se=intercept_se,
        intercept_ci=intercept_ci,
        slope=slope,
        slope_se=slope_se,
        df=df,
        interpretation=interpretation
    )


def pet_peese_combined(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05,
    bootstrap: bool = True,
    n_bootstrap: int = 1000,
    random_seed: Optional[int] = None
) -> PETPEESEResult:
    """
    Combined PET-PEESE analysis with selection heuristic.

    Selection rule:
    - If PET intercept is not significant (p > 0.05), use PET
    - If PET intercept is significant, use PEESE

    This addresses the "Type 1 error cascade" problem in PET-PEESE.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        alpha: Significance level
        bootstrap: Whether to compute bootstrapped confidence intervals
        n_bootstrap: Number of bootstrap samples
        random_seed: Random seed for reproducibility

    Returns:
        PETPEESEResult object with both analyses and selection
    """
    # Run PET
    pet_result = pet_test(effect_sizes, standard_errors, alpha)

    # Run PEESE
    peese_result = peese_test(effect_sizes, standard_errors, alpha)

    # Selection heuristic
    # Check if PET intercept is significantly different from zero
    pet_intercept_sig = abs(pet_result.intercept / pet_result.intercept_se) > \
                       stats.t.ppf(1 - alpha / 2, pet_result.df)

    if pet_intercept_sig:
        # Use PEESE (genuine effect detected)
        selected_method = "PEESE"
        selected_estimate = peese_result.intercept
        selected_ci = peese_result.intercept_ci
    else:
        # Use PET (no genuine effect or very small effect)
        selected_method = "PET"
        selected_estimate = pet_result.intercept
        selected_ci = pet_result.intercept_ci

    # Bootstrap confidence intervals
    bootstrap_ci = None
    if bootstrap:
        bootstrap_ci = _bootstrap_pet_peese(
            effect_sizes,
            standard_errors,
            selected_method,
            n_bootstrap,
            alpha,
            random_seed
        )

    # Interpretation
    interpretation = (
        f"Selection criterion: PET intercept {'is' if pet_intercept_sig else 'is not'} "
        f"significantly different from zero.\n"
        f"Therefore, {selected_method} is selected for the final estimate.\n"
        f"\n"
    )

    if selected_method == "PEESE":
        interpretation += (
            f"PEESE suggests a bias-corrected effect of {selected_estimate:.4f}.\n"
            f"This estimate accounts for the correlation between effect sizes\n"
            f"and their variances due to publication bias."
        )
    else:
        interpretation += (
            f"PET suggests {'little to no genuine effect' if abs(selected_estimate) < 0.1 else 'a small effect'} "
            f"({selected_estimate:.4f}).\n"
            f"Publication bias may have inflated observed effects."
        )

    return PETPEESEResult(
        pet_result=pet_result,
        peese_result=peese_result,
        selected_estimate=selected_estimate,
        selected_ci=selected_ci,
        selected_method=selected_method,
        bootstrap_ci=bootstrap_ci,
        interpretation=interpretation
    )


def _bootstrap_pet_peese(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    method: str,
    n_bootstrap: int,
    alpha: float,
    random_seed: Optional[int]
) -> Tuple[float, float]:
    """
    Bootstrap confidence intervals for PET-PEESE.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        method: 'PET' or 'PEESE'
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level
        random_seed: Random seed

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    n = len(effect_sizes)
    bootstrap_estimates = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n, size=n, replace=True)
        boot_effects = effect_sizes[indices]
        boot_se = standard_errors[indices]

        # Compute estimate
        try:
            if method == 'PET':
                result = pet_test(boot_effects, boot_se, alpha)
                estimate = result.intercept
            else:  # PEESE
                result = peese_test(boot_effects, boot_se, alpha)
                estimate = result.intercept

            bootstrap_estimates.append(estimate)
        except:
            # Skip failed bootstrap samples
            continue

    # Percentile confidence interval
    lower = np.percentile(bootstrap_estimates, 100 * alpha / 2)
    upper = np.percentile(bootstrap_estimates, 100 * (1 - alpha / 2))

    return lower, upper
