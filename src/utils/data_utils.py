"""
Data utilities for meta-analysis

Handles data loading, validation, and preprocessing for publication bias analyses.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class MetaAnalysisData:
    """
    Container for meta-analysis data.

    Attributes:
        effect_sizes: Array of effect sizes (e.g., Cohen's d, log odds ratios)
        standard_errors: Array of standard errors
        variances: Array of variances (optional, computed from SE if not provided)
        sample_sizes: Array of sample sizes (optional)
        study_names: List of study identifiers (optional)
        moderators: DataFrame of moderator variables (optional)
    """
    effect_sizes: np.ndarray
    standard_errors: np.ndarray
    variances: Optional[np.ndarray] = None
    sample_sizes: Optional[np.ndarray] = None
    study_names: Optional[list] = None
    moderators: Optional[pd.DataFrame] = None

    def __post_init__(self):
        """Validate and process data after initialization."""
        self.effect_sizes = np.asarray(self.effect_sizes)
        self.standard_errors = np.asarray(self.standard_errors)

        if self.variances is None:
            self.variances = self.standard_errors ** 2
        else:
            self.variances = np.asarray(self.variances)

        # Validation
        n = len(self.effect_sizes)
        if len(self.standard_errors) != n:
            raise ValueError("Effect sizes and standard errors must have same length")
        if len(self.variances) != n:
            raise ValueError("Variances must match length of effect sizes")

        if self.sample_sizes is not None:
            self.sample_sizes = np.asarray(self.sample_sizes)
            if len(self.sample_sizes) != n:
                raise ValueError("Sample sizes must match length of effect sizes")

        if self.study_names is None:
            self.study_names = [f"Study_{i+1}" for i in range(n)]
        elif len(self.study_names) != n:
            raise ValueError("Study names must match length of effect sizes")

    @property
    def n_studies(self) -> int:
        """Return number of studies."""
        return len(self.effect_sizes)

    @property
    def weights(self) -> np.ndarray:
        """Return inverse-variance weights."""
        return 1 / self.variances

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        df = pd.DataFrame({
            'study': self.study_names,
            'effect_size': self.effect_sizes,
            'se': self.standard_errors,
            'variance': self.variances
        })

        if self.sample_sizes is not None:
            df['n'] = self.sample_sizes

        if self.moderators is not None:
            df = pd.concat([df, self.moderators], axis=1)

        return df


def load_meta_analysis_data(
    data: Union[str, pd.DataFrame],
    effect_col: str = 'effect_size',
    se_col: str = 'se',
    var_col: Optional[str] = None,
    n_col: Optional[str] = None,
    study_col: Optional[str] = None,
    moderator_cols: Optional[list] = None
) -> MetaAnalysisData:
    """
    Load meta-analysis data from file or DataFrame.

    Parameters:
        data: Path to CSV file or pandas DataFrame
        effect_col: Name of effect size column
        se_col: Name of standard error column
        var_col: Name of variance column (optional)
        n_col: Name of sample size column (optional)
        study_col: Name of study identifier column (optional)
        moderator_cols: List of moderator variable columns (optional)

    Returns:
        MetaAnalysisData object
    """
    if isinstance(data, str):
        df = pd.read_csv(data)
    else:
        df = data.copy()

    # Extract required columns
    effect_sizes = df[effect_col].values
    standard_errors = df[se_col].values

    # Extract optional columns
    variances = df[var_col].values if var_col and var_col in df.columns else None
    sample_sizes = df[n_col].values if n_col and n_col in df.columns else None
    study_names = df[study_col].tolist() if study_col and study_col in df.columns else None

    moderators = None
    if moderator_cols:
        available_mods = [col for col in moderator_cols if col in df.columns]
        if available_mods:
            moderators = df[available_mods]

    return MetaAnalysisData(
        effect_sizes=effect_sizes,
        standard_errors=standard_errors,
        variances=variances,
        sample_sizes=sample_sizes,
        study_names=study_names,
        moderators=moderators
    )


def simulate_publication_bias_data(
    n_studies: int = 50,
    true_effect: float = 0.3,
    heterogeneity: float = 0.1,
    bias_severity: str = 'moderate',
    random_seed: Optional[int] = None
) -> MetaAnalysisData:
    """
    Simulate meta-analysis data with publication bias.

    Parameters:
        n_studies: Number of studies to simulate
        true_effect: True underlying effect size
        heterogeneity: Between-study heterogeneity (tau)
        bias_severity: 'none', 'mild', 'moderate', or 'severe'
        random_seed: Random seed for reproducibility

    Returns:
        MetaAnalysisData object with simulated data
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Simulate sample sizes (log-normal distribution)
    sample_sizes = np.exp(np.random.normal(4.5, 0.8, n_studies)).astype(int)
    sample_sizes = np.clip(sample_sizes, 20, 1000)

    # Simulate true effects with heterogeneity
    true_effects = np.random.normal(true_effect, heterogeneity, n_studies)

    # Simulate standard errors (decreasing with sample size)
    standard_errors = np.sqrt(4 / sample_sizes)

    # Simulate observed effects
    observed_effects = np.random.normal(true_effects, standard_errors)

    # Apply publication bias
    bias_params = {
        'none': 0.0,
        'mild': 0.1,
        'moderate': 0.3,
        'severe': 0.5
    }

    bias_strength = bias_params.get(bias_severity, 0.3)

    if bias_strength > 0:
        # Publication probability decreases with p-value
        z_scores = observed_effects / standard_errors
        p_values = 2 * (1 - scipy.stats.norm.cdf(np.abs(z_scores)))

        # Probability of publication
        pub_prob = 1 - bias_strength * p_values
        pub_prob = np.clip(pub_prob, 0.1, 1.0)

        # Select published studies
        published = np.random.binomial(1, pub_prob).astype(bool)

        # Keep only published studies
        observed_effects = observed_effects[published]
        standard_errors = standard_errors[published]
        sample_sizes = sample_sizes[published]

    return MetaAnalysisData(
        effect_sizes=observed_effects,
        standard_errors=standard_errors,
        sample_sizes=sample_sizes
    )


# Import scipy for simulations
import scipy.stats
