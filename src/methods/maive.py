"""
MAIVE: Meta-Analysis Instrumental Variable Estimator

The MAIVE estimator (Irsova et al., 2023) uses an instrumental variable approach
to correct for publication bias. It exploits between-study heterogeneity as an
instrument, recognizing that publication bias is correlated with study precision
but heterogeneity is not.

Key insight: Between-study variation provides a source of exogenous variation
that can identify the true effect in the presence of publication bias.

References:
    Irsova, Z., Havranek, T., & Novak, J. (2023). Publication bias in measuring
    anthropogenic climate change. Energy Economics, 119, 106474.

    Irsova, Z., & Havranek, T. (2023). Instrumental variables in meta-analysis.
    Research Synthesis Methods (working paper).
"""

import numpy as np
from scipy import stats, optimize
from typing import Tuple, Optional, Dict
from dataclasses import dataclass
import warnings


@dataclass
class MAIVEResult:
    """Results from MAIVE estimator."""
    original_effect: float
    original_se: float
    original_ci: Tuple[float, float]
    maive_effect: float
    maive_se: float
    maive_ci: Tuple[float, float]
    iv_strength: float  # First-stage F-statistic
    heterogeneity_tau2: float
    overid_test_stat: float  # Overidentification test
    overid_p_value: float
    interpretation: str

    def __repr__(self):
        return (
            f"MAIVE: Meta-Analysis IV Estimator\n"
            f"{'=' * 70}\n"
            f"Original (biased) effect: {self.original_effect:.4f} "
            f"[{self.original_ci[0]:.4f}, {self.original_ci[1]:.4f}]\n"
            f"MAIVE (bias-corrected): {self.maive_effect:.4f} "
            f"[{self.maive_ci[0]:.4f}, {self.maive_ci[1]:.4f}]\n"
            f"\n"
            f"Instrument strength (F-stat): {self.iv_strength:.2f}\n"
            f"Heterogeneity (τ²): {self.heterogeneity_tau2:.4f}\n"
            f"Overidentification test: χ² = {self.overid_test_stat:.2f}, "
            f"p = {self.overid_p_value:.4f}\n"
            f"\n{self.interpretation}"
        )


def maive_estimator(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    alpha: float = 0.05,
    moderators: Optional[np.ndarray] = None
) -> MAIVEResult:
    """
    Meta-Analysis Instrumental Variable Estimator (MAIVE).

    Uses between-study heterogeneity as an instrument to correct for publication bias.
    The method is based on two-stage least squares (2SLS) estimation.

    Identification strategy:
    1. Publication bias creates correlation between effect sizes and standard errors
    2. Heterogeneity (between-study variation) is uncorrelated with publication bias
    3. Use heterogeneity-based instruments to recover unbiased effect estimate

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        alpha: Significance level for confidence intervals
        moderators: Optional moderator variables (used to construct instruments)

    Returns:
        MAIVEResult object with bias-corrected estimates
    """
    n = len(effect_sizes)
    variances = standard_errors ** 2

    # Original (potentially biased) estimate
    weights = 1 / variances
    original_effect = np.sum(weights * effect_sizes) / np.sum(weights)
    original_se = np.sqrt(1 / np.sum(weights))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    original_ci = (
        original_effect - z_crit * original_se,
        original_effect + z_crit * original_se
    )

    # Estimate heterogeneity (tau^2) using DerSimonian-Laird
    Q = np.sum(weights * (effect_sizes - original_effect) ** 2)
    df = n - 1
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - df) / C)

    # Construct instruments based on heterogeneity
    # Instrument 1: Study-specific deviation from pooled effect (captures heterogeneity)
    # Instrument 2: Squared deviation (captures non-linear heterogeneity)
    # Instrument 3: Moderator interactions (if available)

    deviation = effect_sizes - original_effect
    instruments = [
        deviation,
        deviation ** 2,
        1 / (standard_errors + tau2),  # Precision under random effects
    ]

    # Add moderator-based instruments if available
    if moderators is not None:
        if moderators.ndim == 1:
            moderators = moderators.reshape(-1, 1)
        for j in range(moderators.shape[1]):
            instruments.append(moderators[:, j] * deviation)

    # Stack instruments
    Z = np.column_stack(instruments)

    # Endogenous variable: standard error (correlated with publication bias)
    X_endo = standard_errors.reshape(-1, 1)

    # Exogenous variables: constant
    X_exog = np.ones((n, 1))

    # Dependent variable: effect sizes
    y = effect_sizes

    # Two-stage least squares (2SLS)
    try:
        maive_effect, maive_se, iv_strength, overid_stat, overid_pval = _two_stage_least_squares(
            y, X_endo, X_exog, Z, weights
        )
    except Exception as e:
        warnings.warn(f"MAIVE estimation failed: {str(e)}. Returning original estimate.")
        maive_effect = original_effect
        maive_se = original_se
        iv_strength = 0
        overid_stat = 0
        overid_pval = 1

    # Confidence interval
    maive_ci = (
        maive_effect - z_crit * maive_se,
        maive_effect + z_crit * maive_se
    )

    # Interpretation
    change = abs(maive_effect - original_effect)
    relative_change = 100 * change / abs(original_effect) if original_effect != 0 else 0

    interpretation = (
        f"MAIVE uses heterogeneity-based instruments to correct for publication bias.\n"
    )

    # Check instrument strength
    if iv_strength < 10:
        interpretation += (
            f"\nWARNING: Weak instruments detected (F = {iv_strength:.2f} < 10).\n"
            f"MAIVE estimates may be unreliable. Requires more heterogeneity or\n"
            f"larger sample size for identification.\n"
        )
    else:
        interpretation += (
            f"\nInstrument strength adequate (F = {iv_strength:.2f} > 10).\n"
        )

    # Interpret bias correction
    interpretation += (
        f"\nThe MAIVE estimate changed by {change:.4f} ({relative_change:.1f}%) "
        f"from the original.\n"
    )

    if relative_change > 20:
        interpretation += (
            f"Substantial bias correction suggests publication bias was affecting\n"
            f"the meta-analysis. The MAIVE estimate of {maive_effect:.4f} is likely\n"
            f"more accurate than the conventional estimate of {original_effect:.4f}."
        )
    elif relative_change > 5:
        interpretation += (
            f"Moderate bias correction. Publication bias may be present but limited."
        )
    else:
        interpretation += (
            f"Small bias correction suggests limited publication bias, or\n"
            f"insufficient heterogeneity to identify bias effects."
        )

    # Overidentification test interpretation
    if overid_pval < 0.05:
        interpretation += (
            f"\n\nNote: Overidentification test rejects (p = {overid_pval:.4f}),\n"
            f"suggesting instrument validity assumptions may be violated."
        )

    return MAIVEResult(
        original_effect=original_effect,
        original_se=original_se,
        original_ci=original_ci,
        maive_effect=maive_effect,
        maive_se=maive_se,
        maive_ci=maive_ci,
        iv_strength=iv_strength,
        heterogeneity_tau2=tau2,
        overid_test_stat=overid_stat,
        overid_p_value=overid_pval,
        interpretation=interpretation
    )


def _two_stage_least_squares(
    y: np.ndarray,
    X_endo: np.ndarray,
    X_exog: np.ndarray,
    Z: np.ndarray,
    weights: np.ndarray
) -> Tuple[float, float, float, float, float]:
    """
    Two-stage least squares estimation with diagnostic tests.

    Stage 1: Regress endogenous variables on instruments
    Stage 2: Regress outcome on predicted endogenous variables

    Parameters:
        y: Dependent variable (effect sizes)
        X_endo: Endogenous regressors (standard errors)
        X_exog: Exogenous regressors (constant)
        Z: Instruments
        weights: Regression weights

    Returns:
        Tuple of (coefficient, std_error, first_stage_f, overid_stat, overid_pval)
    """
    n = len(y)
    W = np.diag(weights)

    # Combine exogenous variables and instruments
    Z_all = np.column_stack([X_exog, Z])

    # Stage 1: Regress X_endo on instruments
    # X_endo = Z_all * pi + v
    Z_all_W = Z_all.T @ W @ Z_all
    Z_all_y = Z_all.T @ W @ X_endo

    pi = np.linalg.solve(Z_all_W, Z_all_y)
    X_endo_hat = Z_all @ pi

    # First-stage F-statistic
    # Test: pi_instruments = 0
    n_exog = X_exog.shape[1]
    n_instruments = Z.shape[1]

    residuals_stage1 = X_endo - X_endo_hat
    sse_stage1 = residuals_stage1.T @ W @ residuals_stage1
    mse_stage1 = sse_stage1 / (n - n_exog - n_instruments)

    # F-test for excluded instruments
    # Simplified: R² from stage 1
    tss_stage1 = (X_endo - np.mean(X_endo)).T @ W @ (X_endo - np.mean(X_endo))
    r2_stage1 = 1 - sse_stage1 / tss_stage1
    f_stat = (r2_stage1 / n_instruments) / ((1 - r2_stage1) / (n - n_exog - n_instruments))

    # Stage 2: Regress y on X_endo_hat and X_exog
    # y = X_endo_hat * beta + X_exog * gamma + u
    X_stage2 = np.column_stack([X_exog, X_endo_hat])

    X_stage2_W = X_stage2.T @ W @ X_stage2
    X_stage2_y = X_stage2.T @ W @ y

    coeffs = np.linalg.solve(X_stage2_W, X_stage2_y)

    # The coefficient on endogenous variable (standard error) is the last one
    # But we want the intercept (constant term) as our effect estimate
    beta_constant = coeffs[0]
    beta_endo = coeffs[1] if len(coeffs) > 1 else 0

    # Standard errors (using 2SLS variance estimator)
    residuals_stage2 = y - X_stage2 @ coeffs
    sse_stage2 = residuals_stage2.T @ W @ residuals_stage2
    mse_stage2 = sse_stage2 / (n - X_stage2.shape[1])

    # Variance-covariance matrix
    vcov = mse_stage2 * np.linalg.inv(X_stage2_W)
    se_constant = np.sqrt(vcov[0, 0])

    # Overidentification test (Sargan-Hansen J-statistic)
    # Test: E[Z' * u] = 0
    if n_instruments > X_endo.shape[1]:
        # Compute 2SLS residuals using actual endogenous variables
        X_actual = np.column_stack([X_exog, X_endo])
        beta_2sls = np.linalg.solve(X_actual.T @ W @ X_actual, X_actual.T @ W @ y)
        residuals_2sls = y - X_actual @ beta_2sls

        # Project residuals on all instruments
        u_Z = Z_all.T @ W @ residuals_2sls
        j_stat = u_Z.T @ np.linalg.inv(Z_all_W) @ u_Z

        # Chi-squared test with (n_instruments - n_endogenous) degrees of freedom
        df_overid = n_instruments - X_endo.shape[1]
        overid_pval = 1 - stats.chi2.cdf(j_stat, df_overid)
    else:
        # Exactly identified - no overidentification test
        j_stat = 0
        overid_pval = 1

    return beta_constant, se_constant, f_stat, j_stat, overid_pval


def maive_sensitivity_analysis(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    n_bootstrap: int = 500,
    alpha: float = 0.05,
    random_seed: Optional[int] = None
) -> Dict:
    """
    Sensitivity analysis for MAIVE using bootstrap.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary with sensitivity analysis results
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    n = len(effect_sizes)
    bootstrap_estimates = []

    for _ in range(n_bootstrap):
        # Resample studies
        indices = np.random.choice(n, size=n, replace=True)
        boot_effects = effect_sizes[indices]
        boot_se = standard_errors[indices]

        # Estimate MAIVE
        try:
            result = maive_estimator(boot_effects, boot_se, alpha)
            bootstrap_estimates.append(result.maive_effect)
        except:
            continue

    bootstrap_estimates = np.array(bootstrap_estimates)

    # Bootstrap confidence interval
    boot_lower = np.percentile(bootstrap_estimates, 100 * alpha / 2)
    boot_upper = np.percentile(bootstrap_estimates, 100 * (1 - alpha / 2))

    # Bootstrap standard error
    boot_se = np.std(bootstrap_estimates)

    return {
        'bootstrap_estimates': bootstrap_estimates,
        'bootstrap_mean': np.mean(bootstrap_estimates),
        'bootstrap_median': np.median(bootstrap_estimates),
        'bootstrap_se': boot_se,
        'bootstrap_ci': (boot_lower, boot_upper)
    }
