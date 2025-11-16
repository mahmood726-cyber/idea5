# Publication Bias Method Selection Guide

## Overview

This guide helps researchers select appropriate publication bias methods based on their meta-analysis characteristics. **No single method is universally best** - the optimal approach depends on sample size, heterogeneity, and bias severity.

---

## Quick Decision Tree

```
START: Do you suspect publication bias?
│
├─ k < 10 studies?
│  └─ **Limited options**
│     • Funnel plot inspection (visual only)
│     • Report this limitation
│     • DO NOT use: Egger's, Begg's, Trim-fill (insufficient power)
│
├─ 10 ≤ k < 20 studies?
│  └─ **Moderate options**
│     • Egger's test (but interpret cautiously - low power)
│     • PET-PEESE (if heterogeneity low, I² < 50%)
│     • Trim-and-fill (descriptive, not inferential)
│     • DO NOT use: Selection models, MAIVE (need more studies)
│
├─ 20 ≤ k < 50 studies?
│  ├─ Low heterogeneity (I² < 25%)?
│  │  └─ • Egger's test ✓
│  │     • Begg's test (low power, use as secondary)
│  │     • PET-PEESE ✓✓ (recommended)
│  │     • Trim-and-fill ✓
│  │
│  └─ Moderate-high heterogeneity (I² ≥ 25%)?
│     └─ • Egger's test (but confounded by heterogeneity)
│        • PET-PEESE (may overcorrect)
│        • Trim-and-fill ✓
│        • MAIVE ✓✓ (if I² > 50%, recommended)
│
└─ k ≥ 50 studies?
   └─ **All methods available**
      • Run comprehensive battery
      • Selection models (Copas, Vevea-Hedges) now feasible
      • Compare across methods
      • Trust convergent evidence
```

---

## Method-Specific Guidance

### 1. Egger's Regression Test

**When to use:**
- ✓ k ≥ 10 studies
- ✓ Low to moderate heterogeneity (I² < 50%)
- ✓ Continuous outcomes or log-transformed ratios

**When NOT to use:**
- ✗ k < 10 (very low power)
- ✗ High heterogeneity (I² > 75%) - confounded
- ✗ Binary outcomes without transformation - use Harbord's test instead

**Performance characteristics:**
- **Power:** Low with k < 20, moderate with k ≥ 20
- **Type I error:** Generally maintains nominal level
- **Bias correction:** No - detection only

**Interpretation:**
- p < 0.05: Evidence of funnel plot asymmetry
- p ≥ 0.05: No evidence (but absence of evidence ≠ evidence of absence)
- **Caution:** Asymmetry may reflect heterogeneity, not bias

---

### 2. Begg's Rank Correlation Test

**When to use:**
- ✓ k ≥ 15 studies (preferably 20+)
- ✓ Robust to outliers
- ✓ Non-parametric preference

**When NOT to use:**
- ✗ k < 15 (extremely low power)
- ✗ As primary test (use as confirmatory)

**Performance characteristics:**
- **Power:** Very low (often < 30% even with k = 50)
- **Type I error:** Conservative (maintains under α)
- **Bias correction:** No - detection only

**Recommendation:**
Use as **secondary confirmation** of Egger's test. If both significant, stronger evidence of bias.

---

### 3. Trim-and-Fill

**When to use:**
- ✓ k ≥ 15 studies
- ✓ Want visual representation of bias
- ✓ Exploratory/descriptive analysis

**When NOT to use:**
- ✗ Asymmetric bias (one-tailed selection)
- ✗ As definitive bias correction (use PET-PEESE or MAIVE instead)

**Performance characteristics:**
- **Assumptions:** Symmetric bias (often violated)
- **Bias correction:** Can over- or under-correct
- **Coverage:** Often undercoverage (CIs too narrow)

**Recommendation:**
Use for **visualization and exploration**. Do not rely solely on trim-fill adjusted estimate - compare with other methods.

---

### 4. PET-PEESE

**When to use:**
- ✓ k ≥ 15 studies (preferably 20+)
- ✓ Low to moderate heterogeneity (I² < 50%)
- ✓ Want bias-corrected estimate

**When NOT to use:**
- ✗ High heterogeneity (I² > 75%) - may overcorrect
- ✗ k < 15 (unstable estimates)

**Performance characteristics:**
- **Power:** Good for bias detection
- **Bias correction:** Effective with moderate bias
- **Issue:** Type I error inflation if no true effect

**Selection heuristic:**
1. Run PET: If intercept not significant → use PET estimate
2. If PET intercept significant → use PEESE estimate

**Recommendation:**
**First choice** for low-heterogeneity meta-analyses with k ≥ 20. Use bootstrapped confidence intervals (1000+ iterations) for better coverage.

---

### 5. Selection Models (Copas, Vevea-Hedges)

**When to use:**
- ✓ k ≥ 50 studies (preferably 100+)
- ✓ Want to model publication process explicitly
- ✓ Sensitivity analysis

**When NOT to use:**
- ✗ k < 50 (unstable, non-convergence)
- ✗ Computational constraints (slow estimation)

**Performance characteristics:**
- **Assumptions:** Strong (parametric selection function)
- **Estimation:** Complex (EM algorithm)
- **Uncertainty:** High with small k

**Recommendation:**
Use for **sensitivity analysis** in large meta-analyses. Compare results across different selection assumptions. Do not rely solely on these methods.

---

### 6. MAIVE (Meta-Analysis IV Estimator)

**When to use:**
- ✓ k ≥ 20 studies (preferably 30+)
- ✓ **Substantial heterogeneity (I² > 50%)** - CRITICAL
- ✓ Want unbiased estimate without modeling selection

**When NOT to use:**
- ✗ Low heterogeneity (I² < 25%) - weak instruments
- ✗ k < 20 (IV estimation unreliable)
- ✗ First-stage F < 10 (weak instruments)

**Performance characteristics:**
- **Novel approach:** Uses heterogeneity constructively
- **Assumptions:** Weaker than selection models
- **Diagnostics:** F-statistic, overidentification test

**Critical diagnostic checks:**
1. **Heterogeneity:** I² > 50% (higher is better)
2. **F-statistic:** F > 10 (minimum), F > 20 (good)
3. **Stock-Yogo test:** F > critical value
4. **Overidentification:** p > 0.05

**Recommendation:**
**First choice** for high-heterogeneity meta-analyses. Novel and promising, but newer method - validate with other approaches.

---

## Recommended Workflows

### Workflow A: Standard Meta-Analysis (k = 20-50)

**Step 1: Initial Assessment**
```
1. Create contour-enhanced funnel plot
2. Run Egger's test
3. Run Begg's test (confirmation)
4. Estimate I² statistic
```

**Step 2: Method Selection**
```
IF I² < 50%:
  • Primary: PET-PEESE with bootstrap CIs
  • Secondary: Trim-and-fill
  • Validation: Egger's test

IF I² ≥ 50%:
  • Primary: MAIVE (check diagnostics!)
  • Secondary: Trim-and-fill
  • Validation: Egger's test (noting heterogeneity confounding)
```

**Step 3: Reporting**
```
• Report ALL methods tested
• Present original AND corrected estimates
• Discuss convergence or divergence
• Acknowledge limitations
```

---

### Workflow B: Large Meta-Analysis (k ≥ 50)

**Comprehensive Battery:**
```
1. Funnel plots (basic and contour-enhanced)
2. Egger's test
3. Begg's test
4. Trim-and-fill
5. PET-PEESE
6. MAIVE (if heterogeneity present)
7. Selection models (Copas, Vevea-Hedges) - sensitivity analysis
```

**Triangulation:**
- Methods agree → Strong confidence
- Methods diverge → Uncertainty, report range
- One outlier → Investigate assumptions

---

### Workflow C: Small Meta-Analysis (k < 20)

**Limited Options:**
```
1. Funnel plot with confidence contours
2. Report visual inspection
3. If k ≥ 10: Run Egger's test (acknowledge low power)
4. Do NOT claim "no bias" based on p > 0.05
5. Discuss bias as potential limitation
```

**Recommendation:**
With small k, **acknowledge uncertainty**. Conduct pre-specified sensitivity analyses removing outliers or influential studies.

---

## Common Scenarios

### Scenario 1: All methods detect bias

**Example:** Egger's p = 0.001, Begg's p = 0.02, Trim-fill estimates 5 missing studies

**Action:**
- Strong evidence of publication bias
- Report multiple bias-corrected estimates
- Choose most appropriate method based on characteristics:
  - Low I²: Use PET-PEESE
  - High I²: Use MAIVE
- Report both original and corrected in paper

---

### Scenario 2: Egger's significant, but Begg's not

**Example:** Egger's p = 0.03, Begg's p = 0.15

**Action:**
- Common pattern (Begg's low power)
- Consider Egger's result as primary
- Apply bias correction methods
- Note: "Egger's test suggests bias (p=0.03), though Begg's test was non-significant (p=0.15), likely due to low power"

---

### Scenario 3: No bias detected, but visual asymmetry

**Example:** Egger's p = 0.12, but funnel plot looks asymmetric

**Action:**
- Tests have low power with small k
- Asymmetry may be real but not statistically detected
- Consider:
  - Trim-and-fill exploratory analysis
  - Sensitivity analysis removing outliers
  - Report both "no statistical evidence" but "visual suggestion"
- Do NOT conclude "no bias exists"

---

### Scenario 4: High heterogeneity (I² = 80%)

**Action:**
- Egger's test unreliable (confounded by heterogeneity)
- PET-PEESE may overcorrect
- **Recommended:**
  1. MAIVE (if F > 10 and k ≥ 20)
  2. Investigate sources of heterogeneity (meta-regression)
  3. Subgroup analyses if possible
- Interpret bias tests cautiously

---

### Scenario 5: MAIVE shows weak instruments (F = 6)

**Action:**
- Do NOT trust MAIVE estimate
- Fall back to alternative methods:
  - If I² moderate: Try PET-PEESE
  - If I² low: Use Egger's + Trim-fill
- Consider increasing k by adding more studies
- Report: "Insufficient heterogeneity for MAIVE (F = 6 < 10)"

---

## Reporting Checklist

### Minimal Reporting

- [ ] Funnel plot presented
- [ ] At least one statistical test (Egger's or Begg's)
- [ ] I² and τ² reported
- [ ] Original pooled estimate
- [ ] Discussion of bias implications

### Comprehensive Reporting (Recommended)

- [ ] Contour-enhanced funnel plot
- [ ] Egger's test results
- [ ] Begg's test results (if k ≥ 15)
- [ ] Heterogeneity statistics (I², τ², Q)
- [ ] At least one correction method (PET-PEESE or MAIVE)
- [ ] Original AND corrected estimates side-by-side
- [ ] Method selection justification
- [ ] Sensitivity analyses
- [ ] Limitations acknowledged

### Example Results Paragraph

> "We assessed publication bias using multiple complementary methods. Visual inspection of the contour-enhanced funnel plot revealed slight asymmetry, with smaller studies showing larger effect sizes. Egger's regression test was statistically significant (intercept = 0.42, p = 0.03), providing evidence of small-study effects. Given substantial heterogeneity (I² = 65%), we applied the MAIVE estimator, which showed adequate instrument strength (F = 15.3 > 10). The MAIVE-corrected estimate (d = 0.28, 95% CI [0.15, 0.41]) was moderately attenuated compared to the random-effects estimate (d = 0.38, 95% CI [0.28, 0.48]), suggesting publication bias may have inflated the observed effect by approximately 26%. We also applied trim-and-fill as a sensitivity analysis, which estimated 3 missing studies and yielded a similar corrected estimate (d = 0.30)."

---

## Special Considerations

### Binary Outcomes

- Use **Harbord's test** instead of Egger's for odds ratios
- Arcsine transformation for risk differences
- Peters' test for small studies

### Rare Events

- Publication bias methods assume large-sample approximations
- May be unreliable with event rates < 1%
- Consider exact methods or Bayesian approaches

### Network Meta-Analysis

- Standard methods designed for pairwise comparisons
- Extension methods exist (Chaimani et al., 2012)
- Beyond scope of current dashboard

### Individual Participant Data (IPD)

- Publication bias operates at study level, not participant level
- Apply methods to study-level estimates
- IPD helps investigate sources of heterogeneity

---

## Method Comparison Table

| Method | Min k | Power | Assumptions | Correction | Best When |
|--------|-------|-------|-------------|------------|-----------|
| **Egger's** | 10 | Low-Mod | Linear bias | No | Low I², continuous outcomes |
| **Begg's** | 15 | Very Low | Rank-based | No | Confirmation only |
| **Trim-Fill** | 15 | N/A | Symmetric | Yes | Visualization, exploration |
| **PET-PEESE** | 15 | Good | SE correlation | Yes | Low I², k ≥ 20 |
| **Copas** | 50 | Varies | Latent threshold | Yes | Large k, sensitivity |
| **Vevea-Hedges** | 50 | Varies | p-value steps | Yes | Large k, known selection |
| **MAIVE** | 20 | Good | Heterogeneity IV | Yes | **High I² (>50%), k ≥ 20** |

---

## References

Egger, M., et al. (1997). Bias in meta-analysis detected by a simple, graphical test. *BMJ*, 315, 629-634.

Stanley, T. D., & Doucouliagos, H. (2014). Meta-regression approximations to reduce publication selection bias. *Research Synthesis Methods*, 5, 60-78.

Irsova, Z., et al. (2023). Publication bias in measuring anthropogenic climate change. *Energy Economics*, 119, 106474.

Sterne, J. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry. *BMJ*, 343, d4002.

---

## Contact

For questions or to report issues with this guide:
- GitHub Issues: [repository URL]
- Email: [contact email]

**Last updated:** 2025-11-16
