# Multi-Method Publication Bias Assessment Dashboard

A comprehensive Python-based dashboard for detecting and correcting publication bias in meta-analyses using multiple state-of-the-art methods.

## Features

### Publication Bias Detection Methods

1. **Visual Methods**
   - Enhanced funnel plots with contour regions
   - Galbraith plots
   - P-curve analysis

2. **Statistical Tests**
   - Egger's regression test
   - Begg's rank correlation test
   - Harbord's test (for binary outcomes)

3. **Correction Methods**
   - Trim-and-fill (Duval & Tweedie, 2000)
   - PET-PEESE with bootstrapped confidence intervals (Stanley & Doucouliagos, 2014)
   - Selection models:
     - Copas sensitivity analysis
     - Vevea & Hedges step function model

4. **Advanced Methods**
   - **MAIVE** (Meta-Analysis Instrumental Variable Estimator, Irsova et al., 2023)
     - Novel instrumental variable approach
     - Addresses both publication bias and researcher degrees of freedom
     - Based on between-study heterogeneity

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.dashboard import PublicationBiasDashboard
import pandas as pd

# Load your meta-analysis data
data = pd.read_csv('your_data.csv')

# Launch dashboard
dashboard = PublicationBiasDashboard(data)
dashboard.run()
```

## Project Structure

```
.
├── src/
│   ├── methods/           # Individual bias detection methods
│   ├── visualization/     # Plotting functions
│   ├── dashboard/         # Interactive dashboard
│   └── utils/            # Utility functions
├── data/                 # Example datasets
├── notebooks/            # Analysis notebooks
├── tests/               # Unit tests
├── paper/               # Research paper materials
└── docs/                # Documentation
```

## Citation

If you use this dashboard in your research, please cite:

```bibtex
@article{publicationbias2025,
  title={A Comprehensive Multi-Method Approach to Publication Bias Assessment in Meta-Analysis},
  author={[Your Name]},
  journal={[Target Journal]},
  year={2025}
}
```

## References

- Duval, S., & Tweedie, R. (2000). Trim and fill: A simple funnel‐plot–based method
- Stanley, T. D., & Doucouliagos, H. (2014). Meta‐regression approximations to reduce publication selection bias
- Irsova, Z., Meta-analysis instrumental variable estimator (MAIVE), 2023
- Copas, J. B., & Shi, J. Q. (2000). Meta-analysis, funnel plots and sensitivity analysis
- Vevea, J. L., & Hedges, L. V. (1995). A general linear model for estimating effect size

## License

MIT License
