"""
Statistical utilities for meta-analysis.

Core statistical functions for effect size estimation and inference.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional


def random_effects_model(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    method: str = 'DL'
) -> Tuple[float, float, float, float]:
    """
    Fit random-effects meta-analysis model.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of within-study variances
        method: Method for estimating tau^2 ('DL', 'REML', 'PM', 'ML')
            - DL: DerSimonian-Laird
            - REML: Restricted maximum likelihood
            - PM: Paule-Mandel
            - ML: Maximum likelihood

    Returns:
        Tuple of (pooled_effect, pooled_se, tau2, I2)
    """
    weights = 1 / variances
    pooled_effect_FE = np.sum(weights * effect_sizes) / np.sum(weights)

    # Q statistic
    Q = np.sum(weights * (effect_sizes - pooled_effect_FE) ** 2)
    df = len(effect_sizes) - 1

    # Estimate tau^2 (between-study variance)
    if method == 'DL':
        # DerSimonian-Laird estimator
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, (Q - df) / C)
    elif method == 'PM':
        # Paule-Mandel estimator
        tau2 = _paule_mandel_tau2(effect_sizes, variances, Q, df)
    elif method in ['REML', 'ML']:
        # Iterative REML/ML
        tau2 = _reml_tau2(effect_sizes, variances, method == 'REML')
    else:
        raise ValueError(f"Unknown method: {method}")

    # Random-effects pooled estimate
    weights_RE = 1 / (variances + tau2)
    pooled_effect = np.sum(weights_RE * effect_sizes) / np.sum(weights_RE)
    pooled_se = np.sqrt(1 / np.sum(weights_RE))

    # I^2 statistic (heterogeneity)
    I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0

    return pooled_effect, pooled_se, tau2, I2


def _paule_mandel_tau2(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    Q: float,
    df: int,
    max_iter: int = 100,
    tol: float = 1e-8
) -> float:
    """Iterative Paule-Mandel estimator for tau^2."""
    tau2 = max(0, (Q - df) / np.sum(1 / variances))

    for _ in range(max_iter):
        weights = 1 / (variances + tau2)
        pooled = np.sum(weights * effect_sizes) / np.sum(weights)
        Q_new = np.sum(weights * (effect_sizes - pooled) ** 2)

        if abs(Q_new - df) < tol:
            break

        # Update tau2
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, tau2 + (Q_new - df) / C)

    return tau2


def _reml_tau2(
    effect_sizes: np.ndarray,
    variances: np.ndarray,
    restricted: bool = True,
    max_iter: int = 100,
    tol: float = 1e-8
) -> float:
    """REML/ML estimator for tau^2."""
    tau2 = max(0, np.var(effect_sizes) - np.mean(variances))

    for _ in range(max_iter):
        tau2_old = tau2

        weights = 1 / (variances + tau2)
        W = np.sum(weights)
        pooled = np.sum(weights * effect_sizes) / W

        # Score and information
        residuals = effect_sizes - pooled
        score = -0.5 * np.sum(weights ** 2 * (residuals ** 2 - variances - tau2))

        if restricted:
            info = 0.5 * np.sum(weights ** 2) - 0.5 * (np.sum(weights) ** 2) / W
        else:
            info = 0.5 * np.sum(weights ** 2)

        # Newton-Raphson update
        tau2 = max(0, tau2 + score / info)

        if abs(tau2 - tau2_old) < tol:
            break

    return tau2


def fixed_effects_model(
    effect_sizes: np.ndarray,
    variances: np.ndarray
) -> Tuple[float, float]:
    """
    Fit fixed-effects meta-analysis model.

    Parameters:
        effect_sizes: Array of effect sizes
        variances: Array of within-study variances

    Returns:
        Tuple of (pooled_effect, pooled_se)
    """
    weights = 1 / variances
    pooled_effect = np.sum(weights * effect_sizes) / np.sum(weights)
    pooled_se = np.sqrt(1 / np.sum(weights))

    return pooled_effect, pooled_se


def calculate_ci(
    estimate: float,
    se: float,
    alpha: float = 0.05
) -> Tuple[float, float]:
    """
    Calculate confidence interval.

    Parameters:
        estimate: Point estimate
        se: Standard error
        alpha: Significance level (default: 0.05 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    z = stats.norm.ppf(1 - alpha / 2)
    return estimate - z * se, estimate + z * se


def bootstrap_ci(
    data: np.ndarray,
    statistic_func: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    random_seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval.

    Parameters:
        data: Data array or tuple of arrays
        statistic_func: Function to calculate statistic from data
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    bootstrap_stats = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        if isinstance(data, tuple):
            n = len(data[0])
            indices = np.random.choice(n, size=n, replace=True)
            sample = tuple(d[indices] for d in data)
        else:
            n = len(data)
            indices = np.random.choice(n, size=n, replace=True)
            sample = data[indices]

        # Calculate statistic
        stat = statistic_func(sample)
        bootstrap_stats.append(stat)

    # Percentile method
    lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
    upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))

    return lower, upper


def kendall_tau(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """
    Calculate Kendall's tau rank correlation coefficient.

    Parameters:
        x: First variable
        y: Second variable

    Returns:
        Tuple of (tau, p_value)
    """
    return stats.kendalltau(x, y)


def weighted_least_squares(
    X: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Weighted least squares regression.

    Parameters:
        X: Design matrix (n_samples, n_features)
        y: Response vector (n_samples,)
        weights: Weight vector (n_samples,)

    Returns:
        Tuple of (coefficients, standard_errors, fitted_values)
    """
    # Weight matrix
    W = np.diag(weights)

    # Weighted least squares solution
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ y

    # Coefficients
    beta = np.linalg.solve(XtWX, XtWy)

    # Fitted values
    fitted = X @ beta

    # Residuals and variance
    residuals = y - fitted
    n, p = X.shape
    sigma2 = np.sum(weights * residuals ** 2) / (n - p)

    # Standard errors
    cov_matrix = sigma2 * np.linalg.inv(XtWX)
    se = np.sqrt(np.diag(cov_matrix))

    return beta, se, fitted
