"""
Basic usage examples for the Publication Bias Assessment toolkit.

This script demonstrates how to use individual methods and the dashboard.
"""

import numpy as np
import sys
sys.path.insert(0, '..')

from src.utils.data_utils import simulate_publication_bias_data, load_meta_analysis_data
from src.methods import (
    egger_test, begg_test, trim_and_fill, pet_peese_combined,
    maive_estimator
)
from src.visualization import contour_enhanced_funnel_plot
from src.utils.statistics import random_effects_model


def example_1_simulate_and_test():
    """Example 1: Simulate data and run basic tests."""
    print("=" * 70)
    print("Example 1: Simulate Data and Run Basic Tests")
    print("=" * 70)

    # Simulate data with moderate publication bias
    data = simulate_publication_bias_data(
        n_studies=40,
        true_effect=0.3,
        heterogeneity=0.15,
        bias_severity='moderate',
        random_seed=123
    )

    print(f"\nSimulated {data.n_studies} studies")
    print(f"True effect: 0.3")
    print(f"Bias severity: moderate")

    # Random-effects pooled estimate
    pooled, se, tau2, I2 = random_effects_model(
        data.effect_sizes,
        data.variances
    )

    print(f"\nRandom-Effects Model:")
    print(f"  Pooled effect: {pooled:.4f} (SE: {se:.4f})")
    print(f"  τ² (heterogeneity): {tau2:.4f}")
    print(f"  I² (% variation due to heterogeneity): {I2:.1f}%")

    # Egger's test
    print("\n" + "-" * 70)
    egger_result = egger_test(data.effect_sizes, data.standard_errors)
    print(egger_result)

    # Begg's test
    print("\n" + "-" * 70)
    begg_result = begg_test(data.effect_sizes, data.variances)
    print(begg_result)


def example_2_correction_methods():
    """Example 2: Apply correction methods."""
    print("\n" + "=" * 70)
    print("Example 2: Publication Bias Correction Methods")
    print("=" * 70)

    # Simulate data with severe publication bias
    data = simulate_publication_bias_data(
        n_studies=50,
        true_effect=0.25,
        heterogeneity=0.1,
        bias_severity='severe',
        random_seed=456
    )

    # Original estimate
    pooled, se, _, _ = random_effects_model(
        data.effect_sizes,
        data.variances
    )
    print(f"\nOriginal pooled effect: {pooled:.4f} (SE: {se:.4f})")

    # Trim-and-fill
    print("\n" + "-" * 70)
    tf_result = trim_and_fill(data.effect_sizes, data.variances)
    print(tf_result)

    # PET-PEESE
    print("\n" + "-" * 70)
    pp_result = pet_peese_combined(
        data.effect_sizes,
        data.standard_errors,
        bootstrap=True,
        n_bootstrap=500,
        random_seed=789
    )
    print(pp_result)


def example_3_maive():
    """Example 3: MAIVE estimator with heterogeneity."""
    print("\n" + "=" * 70)
    print("Example 3: MAIVE Estimator")
    print("=" * 70)

    # Simulate data with high heterogeneity
    data = simulate_publication_bias_data(
        n_studies=60,
        true_effect=0.4,
        heterogeneity=0.25,  # High heterogeneity
        bias_severity='moderate',
        random_seed=101
    )

    # Original estimate
    pooled, se, tau2, _ = random_effects_model(
        data.effect_sizes,
        data.variances
    )
    print(f"\nOriginal pooled effect: {pooled:.4f} (SE: {se:.4f})")
    print(f"Heterogeneity (τ²): {tau2:.4f}")

    # MAIVE estimator
    print("\n" + "-" * 70)
    maive_result = maive_estimator(data.effect_sizes, data.standard_errors)
    print(maive_result)


def example_4_load_real_data():
    """Example 4: Load and analyze real data."""
    print("\n" + "=" * 70)
    print("Example 4: Load and Analyze Real Data")
    print("=" * 70)

    try:
        # Load example dataset
        data = load_meta_analysis_data(
            '../data/examples/example_dataset.csv',
            effect_col='effect_size',
            se_col='se',
            n_col='n',
            study_col='study'
        )

        print(f"\nLoaded {data.n_studies} studies from CSV")

        # Run comprehensive analysis
        pooled, se, tau2, I2 = random_effects_model(
            data.effect_sizes,
            data.variances
        )

        print(f"\nRandom-Effects Model:")
        print(f"  Pooled effect: {pooled:.4f} (SE: {se:.4f})")
        print(f"  I²: {I2:.1f}%")

        # Quick test battery
        egger = egger_test(data.effect_sizes, data.standard_errors)
        begg = begg_test(data.effect_sizes, data.variances)

        print(f"\nPublication Bias Tests:")
        print(f"  Egger's test p-value: {egger.p_value:.4f}")
        print(f"  Begg's test p-value: {begg.p_value:.4f}")

        if egger.significant or begg.significant:
            print("\n⚠ Warning: Publication bias detected!")
            print("Consider using correction methods (PET-PEESE, MAIVE, etc.)")
        else:
            print("\n✓ No significant publication bias detected.")

    except FileNotFoundError:
        print("\nExample dataset not found. Please ensure the file exists.")


def example_5_visualization():
    """Example 5: Create publication bias visualizations."""
    print("\n" + "=" * 70)
    print("Example 5: Funnel Plot Visualization")
    print("=" * 70)

    data = simulate_publication_bias_data(
        n_studies=35,
        true_effect=0.35,
        heterogeneity=0.12,
        bias_severity='moderate',
        random_seed=202
    )

    pooled, _, _, _ = random_effects_model(
        data.effect_sizes,
        data.variances
    )

    print("\nGenerating contour-enhanced funnel plot...")
    print("(Opening in browser...)")

    fig = contour_enhanced_funnel_plot(
        data.effect_sizes,
        data.standard_errors,
        data.study_names,
        pooled,
        interactive=True
    )

    # Save to HTML
    fig.write_html('../figures/funnel_plot_example.html')
    print("✓ Saved to figures/funnel_plot_example.html")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "PUBLICATION BIAS ASSESSMENT EXAMPLES" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")

    # Run examples
    example_1_simulate_and_test()
    example_2_correction_methods()
    example_3_maive()
    example_4_load_real_data()
    example_5_visualization()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("\nTo launch the interactive dashboard, run:")
    print("  python ../run_dashboard.py")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
