# Code and Data Availability Statement

## For Inclusion in Manuscript

**Recommended text for manuscript:**

> **Code Availability:** All analysis code, simulation scripts, and dashboard implementation are freely available under the MIT License at: https://github.com/[username]/publication-bias-dashboard (DOI: 10.5281/zenodo.[ZENODO_ID]). The repository includes:
>
> - Complete Python implementation of all five methods
> - Interactive dashboard (Dash application)
> - Simulation study code (144,000 runs)
> - Validation scripts (R comparison)
> - Figure and table generation code
> - Reproducibility script (reproduce_paper_results.py)
> - Unit tests (89% coverage)
> - Example datasets and usage tutorials
>
> **Data Availability:** All simulation results, validation outputs, and real-world meta-analysis data used in this study are available in the same repository under `results/` and `data/` directories. Raw simulation data totals ~500 MB and is available upon request or via Zenodo.
>
> **Reproducibility:** Complete reproduction of all results can be achieved by running:
> ```bash
> pip install -r requirements.txt
> python reproduce_paper_results.py
> ```
> Expected runtime: 48-72 hours on a modern multi-core workstation. A quick mode (--quick flag) completes in 5-8 hours with abbreviated simulations.

---

## Publication Checklist

### Pre-Submission Steps

**1. Create GitHub Repository**

```bash
# Initialize if not already done
git init
git add .
git commit -m "Initial commit: Publication bias dashboard"

# Create GitHub repo (via web interface or CLI)
gh repo create publication-bias-dashboard --public

# Push code
git remote add origin https://github.com/[username]/publication-bias-dashboard.git
git push -u origin main
```

**2. Create Zenodo Archive**

Steps:
1. Go to https://zenodo.org/
2. Log in with GitHub account
3. Navigate to "GitHub" tab
4. Enable repository: `publication-bias-dashboard`
5. Create a GitHub release:
   ```bash
   git tag -a v1.0 -m "Publication version - Research Synthesis Methods"
   git push origin v1.0
   ```
6. Zenodo automatically creates archive and assigns DOI
7. Note the DOI: `10.5281/zenodo.[NUMBER]`
8. Update manuscript and README with DOI

**3. Add CITATION.cff File**

```yaml
# Already provided in repository root
cff-version: 1.2.0
message: "If you use this software, please cite both the software and the paper."
title: "Multi-Method Publication Bias Assessment Dashboard"
version: 1.0.0
date-released: 2025-11-16
url: "https://github.com/[username]/publication-bias-dashboard"
repository-code: "https://github.com/[username]/publication-bias-dashboard"
license: MIT
authors:
  - family-names: "[Last Name]"
    given-names: "[First Name]"
    orcid: "https://orcid.org/[ORCID]"
```

**4. Create comprehensive README.md**

Already created - includes:
- ✓ Installation instructions
- ✓ Quick start guide
- ✓ API documentation
- ✓ Citation information
- ✓ License
- ✓ Contributing guidelines

**5. Verify requirements.txt**

```bash
# Generate from current environment
pip freeze > requirements.txt

# Or use pinned versions for exact reproducibility
cat > requirements.txt << EOF
numpy==1.24.3
scipy==1.11.3
pandas==2.1.1
matplotlib==3.8.0
seaborn==0.13.0
plotly==5.17.0
dash==2.14.1
dash-bootstrap-components==1.5.0
statsmodels==0.14.0
tqdm==4.66.1
pytest==7.4.3
pytest-cov==4.1.0
EOF
```

**6. Add LICENSE File**

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text]
```

---

## Repository Structure for Publication

### Recommended Directory Layout

```
publication-bias-dashboard/
├── README.md                          # Main documentation
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation information
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package installation
├── reproduce_paper_results.py         # Master reproducibility script
│
├── src/                               # Core implementation
│   ├── methods/                       # Five validated methods
│   │   ├── egger_begg.py
│   │   ├── trim_fill.py
│   │   ├── pet_peese.py
│   │   ├── maive_improved.py
│   │   └── __init__.py
│   ├── utils/                         # Utilities
│   ├── visualization/                 # Plotting functions
│   └── dashboard/                     # Interactive app
│
├── simulations/                       # Simulation studies
│   └── simulation_study.py            # 144,000 runs
│
├── validation/                        # Validation against R
│   ├── validate_against_r.R           # R comparison script
│   └── MAIVE_VALIDATION_SUPPLEMENT.md # MAIVE validation doc
│
├── tests/                             # Unit tests (89% coverage)
│   ├── test_validation.py
│   └── test_methods.py
│
├── paper/                             # Publication materials
│   ├── research_paper_template.md
│   ├── complete_results_section.md
│   ├── figures_tables_code.py         # Generate all figures/tables
│   ├── figures/                       # Publication figures (PDF/PNG)
│   └── tables/                        # Publication tables (CSV/LaTeX)
│
├── docs/                              # Documentation
│   ├── METHOD_SELECTION_GUIDE.md      # 5000-word guide
│   ├── SELECTION_MODELS_JUSTIFICATION.md
│   └── PET_PEESE_JUSTIFICATION.md
│
├── examples/                          # Usage examples
│   ├── basic_usage.py
│   └── real_meta_analyses.py          # 5 datasets
│
├── data/                              # Example datasets
│   └── examples/
│       └── example_dataset.csv
│
└── results/                           # Outputs (may be large)
    ├── simulations/
    │   └── summary_statistics.csv     # ~500 MB
    └── real_world_applications.csv
```

### Large Files Handling

**For files > 100 MB (simulation results):**

Option 1: Host on Zenodo
- Upload simulation_results.csv to Zenodo
- Add download link to README:
  ```
  Large files available at: https://zenodo.org/record/[ZENODO_ID]/files/
  ```

Option 2: Git LFS (if using GitHub)
```bash
git lfs install
git lfs track "results/simulations/*.csv"
git add .gitattributes
git commit -m "Track large files with LFS"
```

Option 3: Regenerate on user's machine
- Provide script: `python reproduce_paper_results.py`
- Users generate their own results (48-72 hours)

**Recommendation:** Use Option 1 (Zenodo) for immediate availability

---

## Open Science Framework (OSF) Alternative

If Zenodo not preferred, use OSF:

1. Create project: https://osf.io/
2. Upload materials:
   - Preregistration (if applicable)
   - Data files
   - Analysis scripts
   - Supplementary materials
3. Link to GitHub repository
4. Generate DOI for OSF project
5. Add to manuscript:
   ```
   Materials available at: https://osf.io/[PROJECT_ID]/
   ```

---

## Version Control Best Practices

### Tagging Releases

```bash
# Tag the exact version used for manuscript
git tag -a v1.0-manuscript -m "Version submitted to Research Synthesis Methods"
git push origin v1.0-manuscript

# Tag when revisions complete
git tag -a v1.1-revision1 -m "Version after addressing reviewer comments"
git push origin v1.1-revision1

# Tag accepted version
git tag -a v1.2-accepted -m "Final accepted version"
git push origin v1.2-accepted
```

### Branches

```
main                 # Stable release
├── development      # Active development
├── paper-v1.0       # Frozen at submission
└── paper-v1.1       # Frozen at revision
```

---

## Data Sharing Policy

### What to Share

**Essential (must share):**
- ✓ Source code for all methods
- ✓ Simulation scripts
- ✓ Validation scripts
- ✓ Figure generation code
- ✓ Summary statistics (tables in paper)
- ✓ Example datasets

**Recommended (should share):**
- ✓ Full simulation results (if < 1 GB)
- ✓ Raw validation outputs
- ✓ Real meta-analysis data (if permitted by original authors)

**Optional (nice to have):**
- ✓ Intermediate analysis outputs
- ✓ Debugging logs
- ✓ Development history

### What NOT to Share

- ✗ Proprietary meta-analysis data (without permission)
- ✗ Patient-level data (privacy concerns)
- ✗ API keys or credentials (obviously)
- ✗ Very large temporary files (> 10 GB)

### Licensing

**Code:** MIT License (permissive)
- Allows commercial use
- Modification allowed
- Redistribution allowed
- Attribution required

**Data:** CC-BY 4.0 (Creative Commons)
- Attribution required
- Suitable for scientific data

**Documentation:** CC-BY 4.0
- Same as data

Add to repository root:
```bash
# LICENSE (for code)
MIT License text...

# LICENSE-DATA (for data)
Creative Commons Attribution 4.0 International...
```

---

## Journal-Specific Requirements

### Research Synthesis Methods

**Code/Data Policy:**
> Authors are encouraged to make code and data available in public repositories.

**Requirements:**
1. ✓ Code availability statement in manuscript
2. ✓ Data availability statement
3. ✓ Link to repository (GitHub + DOI)
4. ✓ License specified
5. ✓ Installation instructions
6. ✓ Reproducibility information

**Template for submission:**

> **Code Availability:** All code is available at https://github.com/[username]/publication-bias-dashboard with DOI 10.5281/zenodo.[ID].
>
> **Data Availability:** Simulation results and example datasets are included in the repository. Raw simulation data (500 MB) available upon request.
>
> **Reproducibility:** Full reproduction possible via `reproduce_paper_results.py` script (48-72 hours runtime).

### Other Journals

**PLOS ONE:**
- Requires data in Figshare or Dryad
- Code in GitHub/GitLab + Zenodo

**BMC Journals:**
- Accepts GitHub + DOI
- Prefers Open Science Framework

**Psychological Methods:**
- Requires code for simulations
- Recommends OSF

---

## Post-Publication Maintenance

### Issues and Bug Reports

Add to README:
```markdown
## Reporting Issues

Found a bug or have a question?

1. Check existing issues: https://github.com/[username]/publication-bias-dashboard/issues
2. Open new issue with:
   - Clear description
   - Minimal reproducible example
   - System information (Python version, OS)
   - Error messages

We aim to respond within 48-72 hours.
```

### Updates and Versioning

**Semantic versioning:**
- v1.0.0 - Initial publication release
- v1.1.0 - Minor improvements (bug fixes, documentation)
- v1.2.0 - New features (additional methods)
- v2.0.0 - Breaking changes (API modifications)

**Changelog:**
```markdown
## Changelog

### [1.0.0] - 2025-11-16
- Initial release accompanying RSM publication
- Five validated methods
- 144,000 simulation validation
- Interactive dashboard

### [1.1.0] - 2025-12-01 (planned)
- Bug fix: Heterogeneity estimator boundary condition
- Enhancement: Bootstrap B increased to 2000
- Documentation: Additional examples added
```

---

## Checklist Before Manuscript Submission

**GitHub Repository:**
- [ ] Repository is public
- [ ] README.md is comprehensive
- [ ] LICENSE file added
- [ ] CITATION.cff added
- [ ] requirements.txt with version pins
- [ ] .gitignore configured
- [ ] All tests passing
- [ ] Documentation complete

**Zenodo Archive:**
- [ ] GitHub-Zenodo integration enabled
- [ ] Release v1.0 created
- [ ] DOI obtained
- [ ] DOI added to README and manuscript

**Code Quality:**
- [ ] All code documented
- [ ] Unit tests > 80% coverage
- [ ] No hardcoded paths
- [ ] Reproducibility script tested
- [ ] Example data included

**Data Files:**
- [ ] Summary statistics < 100 MB in repo
- [ ] Large files on Zenodo or regenerable
- [ ] Example datasets included
- [ ] Data dictionaries provided

**Documentation:**
- [ ] Installation instructions clear
- [ ] Quick start guide provided
- [ ] API documentation complete
- [ ] Troubleshooting section included
- [ ] Citation information clear

**Manuscript:**
- [ ] Code availability statement written
- [ ] Data availability statement written
- [ ] Repository URL included
- [ ] DOI included
- [ ] License mentioned

---

## Contact for Code/Data Requests

Add to manuscript and README:

> **Corresponding Author for Code/Data:**
> [Name]
> Email: [email]
> GitHub: @[username]
> ORCID: [ORCID ID]
>
> Response time: Typically 48-72 hours for issues, longer for complex requests.

---

## Example Final Statements for Manuscript

### Minimal (meets requirements):

> **Availability of Data and Materials:** All code and data are available at https://github.com/[username]/publication-bias-dashboard (DOI: 10.5281/zenodo.[ID]).

### Recommended (comprehensive):

> **Availability of Data and Materials:** All analysis code, simulation scripts, validation tests, and example datasets are freely available under the MIT License in our GitHub repository (https://github.com/[username]/publication-bias-dashboard). A permanent archive with DOI 10.5281/zenodo.[ID] has been created for long-term preservation. Complete reproduction of results is possible using the provided `reproduce_paper_results.py` script (estimated runtime: 48-72 hours). The interactive dashboard can be launched locally or accessed online at [URL if hosted].

### With Restrictions (if applicable):

> **Availability of Data and Materials:** All code is freely available at [GitHub URL] under MIT License. Simulation results and synthetic datasets are included in the repository. Original meta-analysis data from published studies cannot be redistributed but sources are cited in Table [X]. Researchers seeking access to specific datasets should contact original study authors.

---

**Status:** Ready for implementation
**Last Updated:** 2025-11-16
**Version:** 1.0
