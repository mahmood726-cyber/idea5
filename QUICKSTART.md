# Quick Start Guide

Get started with the Publication Bias Assessment Dashboard in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/publication-bias-dashboard.git
cd publication-bias-dashboard

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## Launch the Dashboard

```bash
python run_dashboard.py
```

Then open your browser to `http://localhost:8050`

## Quick Example

### 1. Using the Dashboard

1. **Generate Demo Data**
   - Select "Simulate Data" tab
   - Set parameters (e.g., 50 studies, moderate bias)
   - Click "Generate Data"

2. **Run Analyses**
   - Check methods you want to run
   - Click "Run Selected Methods"

3. **View Results**
   - Explore tabs: Summary, Funnel Plots, Comparisons
   - Export results

### 2. Using the API

```python
from src.utils.data_utils import simulate_publication_bias_data
from src.methods import egger_test, trim_and_fill, maive_estimator
from src.visualization import contour_enhanced_funnel_plot

# Simulate data
data = simulate_publication_bias_data(
    n_studies=40,
    true_effect=0.3,
    bias_severity='moderate'
)

# Run Egger's test
egger_result = egger_test(data.effect_sizes, data.standard_errors)
print(egger_result)

# Run trim-and-fill
tf_result = trim_and_fill(data.effect_sizes, data.variances)
print(tf_result)

# Run MAIVE
maive_result = maive_estimator(data.effect_sizes, data.standard_errors)
print(maive_result)

# Create funnel plot
fig = contour_enhanced_funnel_plot(
    data.effect_sizes,
    data.standard_errors,
    pooled_effect=0.3
)
fig.show()
```

### 3. Load Your Own Data

```python
from src.utils.data_utils import load_meta_analysis_data

# CSV format: study, effect_size, se, n
data = load_meta_analysis_data(
    'your_data.csv',
    effect_col='effect_size',
    se_col='se',
    study_col='study'
)

# Now run any analysis...
```

## Example Workflow

```python
import numpy as np
from src.utils.data_utils import load_meta_analysis_data
from src.methods import (
    egger_test, trim_and_fill,
    pet_peese_combined, maive_estimator
)
from src.utils.statistics import random_effects_model

# 1. Load data
data = load_meta_analysis_data('data/examples/example_dataset.csv')

# 2. Basic meta-analysis
pooled, se, tau2, I2 = random_effects_model(
    data.effect_sizes,
    data.variances
)
print(f"Pooled effect: {pooled:.3f} ± {se:.3f}")
print(f"I²: {I2:.1f}%")

# 3. Test for bias
egger = egger_test(data.effect_sizes, data.standard_errors)
if egger.significant:
    print("⚠ Publication bias detected!")

    # 4. Apply corrections
    tf = trim_and_fill(data.effect_sizes, data.variances)
    pp = pet_peese_combined(data.effect_sizes, data.standard_errors)
    maive = maive_estimator(data.effect_sizes, data.standard_errors)

    print(f"Trim-Fill adjusted: {tf.adjusted_effect:.3f}")
    print(f"PET-PEESE adjusted: {pp.selected_estimate:.3f}")
    print(f"MAIVE adjusted: {maive.maive_effect:.3f}")
```

## Key Features

### ✓ Multiple Methods
- **Detection**: Egger's, Begg's tests
- **Correction**: Trim-fill, PET-PEESE, MAIVE
- **Selection Models**: Copas, Vevea-Hedges

### ✓ Enhanced Visualizations
- Contour-enhanced funnel plots
- Side-by-side method comparisons
- Interactive plots with Plotly

### ✓ Publication-Ready
- Export results tables
- High-quality figures
- Comprehensive reporting

### ✓ Novel Methods
- **MAIVE**: Instrumental variable approach
- Bootstrap confidence intervals
- Sensitivity analyses

## Common Use Cases

### Case 1: Quick Bias Check
```python
from src.methods import egger_test
result = egger_test(effects, se)
print(f"Bias detected: {result.significant}")
```

### Case 2: Comprehensive Assessment
Run all methods and compare:
```python
# Use the dashboard for comprehensive side-by-side comparison
python run_dashboard.py
```

### Case 3: Simulation Study
```python
from src.utils.data_utils import simulate_publication_bias_data

# Test your methods
for bias in ['none', 'mild', 'moderate', 'severe']:
    data = simulate_publication_bias_data(
        n_studies=50,
        true_effect=0.3,
        bias_severity=bias
    )
    # Run analyses...
```

## Troubleshooting

**Q: Dashboard won't start?**
- Check all dependencies installed: `pip install -r requirements.txt`
- Try different port: `python run_dashboard.py --port 8051`

**Q: MAIVE fails with "weak instruments"?**
- Needs heterogeneity (I² > 25%)
- Try with larger sample

**Q: All methods show different results?**
- Expected! Compare and report all
- Check simulation studies in paper

## Next Steps

- 📖 Read full documentation in `docs/`
- 📊 Try example analyses in `examples/`
- 📝 See research paper template in `paper/`
- 🎓 Learn method details in implementation files

## Getting Help

- 📧 Email: [your email]
- 💬 Issues: [GitHub issues URL]
- 📚 Docs: [Documentation URL]

## Citation

If you use this dashboard in your research:

```bibtex
@software{publicationbias2025,
  title={Multi-Method Publication Bias Assessment Dashboard},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/publication-bias-dashboard}
}
```
