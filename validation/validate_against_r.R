# Validation of Python implementations against R metafor package
#
# This script runs the same analyses in R to compare with Python results.
# Run this script and compare output with Python validation tests.

library(metafor)

cat("================================================================================\n")
cat("R VALIDATION SCRIPT: Publication Bias Methods\n")
cat("================================================================================\n\n")

# -----------------------------------------------------------------------------
# BCG Vaccine Dataset
# -----------------------------------------------------------------------------

cat("BCG Vaccine Dataset\n")
cat("--------------------------------------------------------------------------------\n")

# Load BCG data
data(dat.bcg)

# Calculate log odds ratios
dat <- escalc(measure="OR", ai=tpos, bi=tneg, ci=cpos, di=cneg, data=dat.bcg)

# Random-effects model
res <- rma(yi, vi, data=dat)
cat("\nRandom-Effects Model:\n")
cat(sprintf("  Estimate: %.4f\n", res$beta))
cat(sprintf("  SE: %.4f\n", res$se))
cat(sprintf("  tau^2: %.4f\n", res$tau2))
cat(sprintf("  I^2: %.2f%%\n", res$I2))

# Egger's regression test
cat("\nEgger's Regression Test:\n")
reg <- regtest(res, model="lm")
cat(sprintf("  z-value: %.4f\n", reg$zval))
cat(sprintf("  p-value: %.4f\n", reg$pval))

# Begg's rank correlation test
cat("\nBegg's Rank Correlation Test:\n")
rank <- ranktest(res)
cat(sprintf("  tau: %.4f\n", rank$tau))
cat(sprintf("  p-value: %.4f\n", rank$pval))

# Trim-and-fill
cat("\nTrim-and-Fill Analysis:\n")
taf <- trimfill(res)
cat(sprintf("  Estimated missing studies: %d (%s side)\n", taf$k0, taf$side))
cat(sprintf("  Original estimate: %.4f\n", res$beta))
cat(sprintf("  Adjusted estimate: %.4f\n", taf$beta))
cat(sprintf("  Adjusted SE: %.4f\n", taf$se))

cat("\n================================================================================\n\n")

# -----------------------------------------------------------------------------
# Small Example Dataset
# -----------------------------------------------------------------------------

cat("Small Example Dataset\n")
cat("--------------------------------------------------------------------------------\n")

# Create small example
yi <- c(0.5, 0.4, 0.6, 0.3, 0.7)
vi <- c(0.2, 0.18, 0.22, 0.25, 0.19)^2

res2 <- rma(yi, vi)
cat("\nRandom-Effects Model:\n")
cat(sprintf("  Estimate: %.4f\n", res2$beta))
cat(sprintf("  SE: %.4f\n", res2$se))

cat("\nEgger's Test:\n")
reg2 <- regtest(res2)
cat(sprintf("  z-value: %.4f\n", reg2$zval))
cat(sprintf("  p-value: %.4f\n", reg2$pval))

cat("\nBegg's Test:\n")
rank2 <- ranktest(res2)
cat(sprintf("  tau: %.4f\n", rank2$tau))
cat(sprintf("  p-value: %.4f\n", rank2$pval))

cat("\nTrim-and-Fill:\n")
taf2 <- trimfill(res2)
cat(sprintf("  Estimated missing studies: %d\n", taf2$k0))
cat(sprintf("  Adjusted estimate: %.4f\n", taf2$beta))

cat("\n================================================================================\n\n")

# -----------------------------------------------------------------------------
# PET-PEESE (using metafor)
# -----------------------------------------------------------------------------

cat("PET-PEESE Analysis (BCG Data)\n")
cat("--------------------------------------------------------------------------------\n")

# PET: regress effect on SE
pet <- lm(dat$yi ~ dat$vi^0.5, weights=1/dat$vi)
cat("\nPET (Precision-Effect Test):\n")
cat(sprintf("  Intercept: %.4f\n", coef(pet)[1]))
cat(sprintf("  Slope: %.4f\n", coef(pet)[2]))
cat(sprintf("  p-value (slope): %.4f\n", summary(pet)$coefficients[2,4]))

# PEESE: regress effect on variance
peese <- lm(dat$yi ~ dat$vi, weights=1/dat$vi)
cat("\nPEESE (Precision-Effect Estimate with SE):\n")
cat(sprintf("  Intercept: %.4f\n", coef(peese)[1]))
cat(sprintf("  Slope: %.4f\n", coef(peese)[2]))

# Selection criterion
if (summary(pet)$coefficients[1,4] < 0.05) {
  cat("\nPET intercept significant -> Use PEESE\n")
  cat(sprintf("  Selected estimate: %.4f\n", coef(peese)[1]))
} else {
  cat("\nPET intercept not significant -> Use PET\n")
  cat(sprintf("  Selected estimate: %.4f\n", coef(pet)[1]))
}

cat("\n================================================================================\n\n")

# -----------------------------------------------------------------------------
# Expected Output Summary for Python Validation
# -----------------------------------------------------------------------------

cat("VALIDATION CHECKLIST\n")
cat("================================================================================\n")
cat("Python implementations should match R results within tolerance:\n")
cat("  - Test statistics: ±0.05\n")
cat("  - P-values: ±0.01\n")
cat("  - Effect estimates: ±0.02\n")
cat("  - Standard errors: ±0.01\n\n")

cat("Key values to check:\n")
cat("1. Egger's test p-value on BCG data: ~0.01\n")
cat("2. Trim-fill should estimate missing studies\n")
cat("3. PET-PEESE should select appropriate method\n")
cat("\nRun: python tests/test_validation.py\n")
cat("Compare outputs from Python and R\n")
cat("================================================================================\n")
