"""
Comprehensive Monte Carlo simulation study for publication bias methods.

This module runs the full simulation study comparing all 7 methods across
multiple conditions to evaluate bias, RMSE, coverage, power, and Type I error.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from tqdm import tqdm
import pickle
import os
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import warnings

import sys
sys.path.insert(0, '..')

from src.utils.data_utils import simulate_publication_bias_data
from src.utils.statistics import random_effects_model
from src.methods import (
    egger_test, begg_test, trim_and_fill,
    pet_peese_combined, maive_estimator
)


@dataclass
class SimulationCondition:
    """Parameters for a simulation condition."""
    true_effect: float
    heterogeneity: float  # tau
    bias_severity: str  # 'none', 'mild', 'moderate', 'severe'
    n_studies: int
    condition_id: str


@dataclass
class SimulationResult:
    """Results from a single simulation replication."""
    condition_id: str
    replication: int

    # True parameters
    true_effect: float

    # Original (biased) estimate
    original_effect: float
    original_se: float
    original_ci_lower: float
    original_ci_upper: float

    # Detection methods
    egger_p: float
    egger_detected: bool
    begg_p: float
    begg_detected: bool

    # Correction methods
    trimfill_effect: float
    trimfill_se: float
    trimfill_n_missing: int

    petpeese_effect: float
    petpeese_method: str

    maive_effect: float
    maive_se: float
    maive_f_stat: float
    maive_valid: bool  # F > 10

    # Performance metrics (computed later)
    original_bias: float
    trimfill_bias: float
    petpeese_bias: float
    maive_bias: float

    original_coverage: bool
    trimfill_coverage: bool
    maive_coverage: bool


def generate_conditions() -> List[SimulationCondition]:
    """
    Generate all simulation conditions.

    Returns:
        List of SimulationCondition objects
    """
    conditions = []
    condition_id = 0

    # Parameter grid
    true_effects = [0.0, 0.2, 0.4]
    heterogeneities = [0.0, 0.1, 0.2, 0.3]  # tau
    bias_severities = ['none', 'mild', 'moderate', 'severe']
    n_studies_list = [20, 50, 100]

    for true_effect in true_effects:
        for tau in heterogeneities:
            for bias in bias_severities:
                for k in n_studies_list:
                    conditions.append(SimulationCondition(
                        true_effect=true_effect,
                        heterogeneity=tau,
                        bias_severity=bias,
                        n_studies=k,
                        condition_id=f"cond_{condition_id:03d}"
                    ))
                    condition_id += 1

    return conditions


def run_single_replication(
    condition: SimulationCondition,
    rep: int,
    random_seed: int
) -> SimulationResult:
    """
    Run a single simulation replication.

    Parameters:
        condition: Simulation condition parameters
        rep: Replication number
        random_seed: Random seed for this replication

    Returns:
        SimulationResult object
    """
    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')

    try:
        # Generate data
        data = simulate_publication_bias_data(
            n_studies=condition.n_studies,
            true_effect=condition.true_effect,
            heterogeneity=condition.heterogeneity,
            bias_severity=condition.bias_severity,
            random_seed=random_seed
        )

        # Original pooled estimate
        pooled, se, tau2, I2 = random_effects_model(
            data.effect_sizes,
            data.variances,
            method='REML'  # Use REML as recommended
        )

        # 95% CI
        z_crit = 1.96
        ci_lower = pooled - z_crit * se
        ci_upper = pooled + z_crit * se

        # Detection methods
        try:
            egger_result = egger_test(data.effect_sizes, data.standard_errors)
            egger_p = egger_result.p_value
            egger_detected = egger_result.significant
        except:
            egger_p = np.nan
            egger_detected = False

        try:
            begg_result = begg_test(data.effect_sizes, data.variances)
            begg_p = begg_result.p_value
            begg_detected = begg_result.significant
        except:
            begg_p = np.nan
            begg_detected = False

        # Trim-and-fill
        try:
            tf_result = trim_and_fill(data.effect_sizes, data.variances)
            trimfill_effect = tf_result.adjusted_effect
            trimfill_se = tf_result.adjusted_se
            trimfill_n_missing = tf_result.n_missing
        except:
            trimfill_effect = np.nan
            trimfill_se = np.nan
            trimfill_n_missing = 0

        # PET-PEESE
        try:
            pp_result = pet_peese_combined(
                data.effect_sizes,
                data.standard_errors,
                bootstrap=False  # Too slow for simulations
            )
            petpeese_effect = pp_result.selected_estimate
            petpeese_method = pp_result.selected_method
        except:
            petpeese_effect = np.nan
            petpeese_method = 'failed'

        # MAIVE
        try:
            maive_result = maive_estimator(data.effect_sizes, data.standard_errors)
            maive_effect = maive_result.maive_effect
            maive_se = maive_result.maive_se
            maive_f = maive_result.iv_strength
            maive_valid = maive_f > 10
        except:
            maive_effect = np.nan
            maive_se = np.nan
            maive_f = 0
            maive_valid = False

        # Compute biases
        original_bias = pooled - condition.true_effect
        trimfill_bias = trimfill_effect - condition.true_effect if not np.isnan(trimfill_effect) else np.nan
        petpeese_bias = petpeese_effect - condition.true_effect if not np.isnan(petpeese_effect) else np.nan
        maive_bias = maive_effect - condition.true_effect if not np.isnan(maive_effect) else np.nan

        # Coverage
        original_coverage = (ci_lower <= condition.true_effect <= ci_upper)

        if not np.isnan(trimfill_effect):
            tf_ci_lower = trimfill_effect - z_crit * trimfill_se
            tf_ci_upper = trimfill_effect + z_crit * trimfill_se
            trimfill_coverage = (tf_ci_lower <= condition.true_effect <= tf_ci_upper)
        else:
            trimfill_coverage = False

        if not np.isnan(maive_effect) and maive_valid:
            maive_ci_lower = maive_effect - z_crit * maive_se
            maive_ci_upper = maive_effect + z_crit * maive_se
            maive_coverage = (maive_ci_lower <= condition.true_effect <= maive_ci_upper)
        else:
            maive_coverage = False

        return SimulationResult(
            condition_id=condition.condition_id,
            replication=rep,
            true_effect=condition.true_effect,
            original_effect=pooled,
            original_se=se,
            original_ci_lower=ci_lower,
            original_ci_upper=ci_upper,
            egger_p=egger_p,
            egger_detected=egger_detected,
            begg_p=begg_p,
            begg_detected=begg_detected,
            trimfill_effect=trimfill_effect,
            trimfill_se=trimfill_se,
            trimfill_n_missing=trimfill_n_missing,
            petpeese_effect=petpeese_effect,
            petpeese_method=petpeese_method,
            maive_effect=maive_effect,
            maive_se=maive_se,
            maive_f_stat=maive_f,
            maive_valid=maive_valid,
            original_bias=original_bias,
            trimfill_bias=trimfill_bias,
            petpeese_bias=petpeese_bias,
            maive_bias=maive_bias,
            original_coverage=original_coverage,
            trimfill_coverage=trimfill_coverage,
            maive_coverage=maive_coverage
        )

    except Exception as e:
        # Return NaN result if replication fails completely
        return SimulationResult(
            condition_id=condition.condition_id,
            replication=rep,
            true_effect=condition.true_effect,
            original_effect=np.nan,
            original_se=np.nan,
            original_ci_lower=np.nan,
            original_ci_upper=np.nan,
            egger_p=np.nan,
            egger_detected=False,
            begg_p=np.nan,
            begg_detected=False,
            trimfill_effect=np.nan,
            trimfill_se=np.nan,
            trimfill_n_missing=0,
            petpeese_effect=np.nan,
            petpeese_method='failed',
            maive_effect=np.nan,
            maive_se=np.nan,
            maive_f_stat=0,
            maive_valid=False,
            original_bias=np.nan,
            trimfill_bias=np.nan,
            petpeese_bias=np.nan,
            maive_bias=np.nan,
            original_coverage=False,
            trimfill_coverage=False,
            maive_coverage=False
        )


def run_condition(
    condition: SimulationCondition,
    n_replications: int = 1000,
    n_jobs: int = 4
) -> List[SimulationResult]:
    """
    Run all replications for a single condition.

    Parameters:
        condition: Simulation condition
        n_replications: Number of replications per condition
        n_jobs: Number of parallel processes

    Returns:
        List of SimulationResult objects
    """
    print(f"\nRunning condition: {condition.condition_id}")
    print(f"  k={condition.n_studies}, δ={condition.true_effect}, "
          f"τ={condition.heterogeneity}, bias={condition.bias_severity}")

    # Generate seeds for reproducibility
    base_seed = hash(condition.condition_id) % (2**31)
    seeds = [base_seed + i for i in range(n_replications)]

    results = []

    # Run replications with progress bar
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        futures = [
            executor.submit(run_single_replication, condition, i, seeds[i])
            for i in range(n_replications)
        ]

        for future in tqdm(futures, desc=f"  Replications", total=n_replications):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                print(f"    Replication failed: {e}")

    return results


def summarize_condition_results(
    results: List[SimulationResult],
    condition: SimulationCondition
) -> Dict:
    """
    Summarize results for a single condition.

    Parameters:
        results: List of SimulationResult objects
        condition: Simulation condition

    Returns:
        Dictionary with summary statistics
    """
    # Convert to arrays, removing NaN values where appropriate
    def clean_array(values):
        arr = np.array(values)
        return arr[~np.isnan(arr)]

    # Biases
    original_biases = clean_array([r.original_bias for r in results])
    trimfill_biases = clean_array([r.trimfill_bias for r in results])
    petpeese_biases = clean_array([r.petpeese_bias for r in results])
    maive_biases = clean_array([r.maive_bias for r in results if r.maive_valid])

    # Detection
    egger_detections = [r.egger_detected for r in results if not np.isnan(r.egger_p)]
    begg_detections = [r.begg_detected for r in results if not np.isnan(r.begg_p)]

    # Coverage
    original_coverage = [r.original_coverage for r in results]
    trimfill_coverage = [r.trimfill_coverage for r in results]
    maive_coverage = [r.maive_coverage for r in results if r.maive_valid]

    # MAIVE validity
    maive_valid_rate = np.mean([r.maive_valid for r in results])

    summary = {
        'condition_id': condition.condition_id,
        'true_effect': condition.true_effect,
        'heterogeneity': condition.heterogeneity,
        'bias_severity': condition.bias_severity,
        'n_studies': condition.n_studies,
        'n_replications': len(results),

        # Bias
        'original_bias_mean': np.mean(original_biases) if len(original_biases) > 0 else np.nan,
        'original_bias_sd': np.std(original_biases) if len(original_biases) > 0 else np.nan,
        'trimfill_bias_mean': np.mean(trimfill_biases) if len(trimfill_biases) > 0 else np.nan,
        'trimfill_bias_sd': np.std(trimfill_biases) if len(trimfill_biases) > 0 else np.nan,
        'petpeese_bias_mean': np.mean(petpeese_biases) if len(petpeese_biases) > 0 else np.nan,
        'petpeese_bias_sd': np.std(petpeese_biases) if len(petpeese_biases) > 0 else np.nan,
        'maive_bias_mean': np.mean(maive_biases) if len(maive_biases) > 0 else np.nan,
        'maive_bias_sd': np.std(maive_biases) if len(maive_biases) > 0 else np.nan,

        # RMSE
        'original_rmse': np.sqrt(np.mean(original_biases**2)) if len(original_biases) > 0 else np.nan,
        'trimfill_rmse': np.sqrt(np.mean(trimfill_biases**2)) if len(trimfill_biases) > 0 else np.nan,
        'petpeese_rmse': np.sqrt(np.mean(petpeese_biases**2)) if len(petpeese_biases) > 0 else np.nan,
        'maive_rmse': np.sqrt(np.mean(maive_biases**2)) if len(maive_biases) > 0 else np.nan,

        # Coverage
        'original_coverage': np.mean(original_coverage),
        'trimfill_coverage': np.mean(trimfill_coverage),
        'maive_coverage': np.mean(maive_coverage) if len(maive_coverage) > 0 else np.nan,

        # Power/Type I error
        'egger_detection_rate': np.mean(egger_detections) if len(egger_detections) > 0 else np.nan,
        'begg_detection_rate': np.mean(begg_detections) if len(begg_detections) > 0 else np.nan,

        # MAIVE specific
        'maive_valid_rate': maive_valid_rate,
    }

    return summary


def run_full_simulation_study(
    n_replications: int = 1000,
    n_jobs: int = 4,
    save_dir: str = 'results'
):
    """
    Run the complete simulation study.

    Parameters:
        n_replications: Number of replications per condition
        n_jobs: Number of parallel processes
        save_dir: Directory to save results
    """
    print("=" * 80)
    print("COMPREHENSIVE PUBLICATION BIAS SIMULATION STUDY")
    print("=" * 80)

    # Generate conditions
    conditions = generate_conditions()
    print(f"\nTotal conditions: {len(conditions)}")
    print(f"Replications per condition: {n_replications}")
    print(f"Total replications: {len(conditions) * n_replications:,}")
    print(f"Parallel processes: {n_jobs}")

    # Create save directory
    os.makedirs(save_dir, exist_ok=True)

    all_results = []
    summaries = []

    # Run each condition
    for i, condition in enumerate(conditions):
        print(f"\n[{i+1}/{len(conditions)}] ", end="")

        # Run replications
        results = run_condition(condition, n_replications, n_jobs)
        all_results.extend(results)

        # Summarize
        summary = summarize_condition_results(results, condition)
        summaries.append(summary)

        # Save intermediate results
        if (i + 1) % 10 == 0:
            print(f"\n  Saving intermediate results...")
            pd.DataFrame(summaries).to_csv(
                f'{save_dir}/summaries_checkpoint_{i+1}.csv',
                index=False
            )

    # Save final results
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)

    # Summary statistics
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(f'{save_dir}/summary_statistics.csv', index=False)
    print(f"✓ Saved: {save_dir}/summary_statistics.csv")

    # Individual results (for detailed analysis)
    results_data = []
    for r in all_results:
        results_data.append({
            'condition_id': r.condition_id,
            'replication': r.replication,
            'true_effect': r.true_effect,
            'original_effect': r.original_effect,
            'trimfill_effect': r.trimfill_effect,
            'petpeese_effect': r.petpeese_effect,
            'maive_effect': r.maive_effect,
            'egger_p': r.egger_p,
            'begg_p': r.begg_p,
            'maive_f_stat': r.maive_f_stat,
        })

    results_df = pd.DataFrame(results_data)
    results_df.to_csv(f'{save_dir}/individual_results.csv', index=False)
    print(f"✓ Saved: {save_dir}/individual_results.csv")

    # Pickle raw results for detailed analysis
    with open(f'{save_dir}/raw_results.pkl', 'wb') as f:
        pickle.dump({'conditions': conditions, 'results': all_results}, f)
    print(f"✓ Saved: {save_dir}/raw_results.pkl")

    print("\n" + "=" * 80)
    print("SIMULATION STUDY COMPLETE")
    print("=" * 80)

    return summary_df


if __name__ == '__main__':
    # Run with reduced replications for testing
    # For full paper, use n_replications=1000
    summary_df = run_full_simulation_study(
        n_replications=100,  # Change to 1000 for final paper
        n_jobs=4,
        save_dir='../results/simulations'
    )

    print("\nSample results:")
    print(summary_df.head(10))
