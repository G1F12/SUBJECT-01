# EXPERIMENT E2 REANALYSIS: STATISTICAL CORRECTION & PSEUDOREPLICATION AUDIT
## Subject-Level Verification of Intra-Tendinous Sliding in Human Achilles Tendon

**Document ID:** `research/cycle17/E2_STATISTICAL_CORRECTION.md`  
**Date:** 2026-11-12  
**Dataset:** Bogaerts et al. (2017), PLoS ONE / PMC5519157 (DOI: `10.1371/journal.pone.0181364`)  
**Cohort:** 10 healthy adults (4 Females, 6 Males; bilateral assessment, 160 observations)  
**Status:** Completed (Methodological Correction)  
**Scientific Classification:** `REPRODUCTION_AND_CORRECTION_ONLY`  
**Related Documents:**
- [E2_RESULTS.json](file:///D:/SUBJECT-01/research/cycle17/E2_RESULTS.json)
- [CYCLE16_FORENSIC_AUDIT.md](file:///D:/SUBJECT-01/research/cycle17/CYCLE16_FORENSIC_AUDIT.md)

---

## 1. Executive Summary of Corrections

A rigorous statistical audit of Experiment E2-REG from Cycle 16 identified two fundamental errors:

1. **Severe Statistical Pseudoreplication in the Friedman Test:**
   - In Cycle 16, the Friedman test was computed on 40 rows representing multiple repetitions and both limbs from the same 10 individuals, yielding $\chi^2 = 59.55$ ($p = 1.17 \times 10^{-13}$).
   - In a Friedman test with $k = 3$ repeated conditions, the theoretical maximum test statistic for $N$ independent blocks is $Q_{\max} = 2N$. For $N = 10$ biological participants, $\chi^2$ cannot mathematically exceed 20.0! The reported value of 59.55 was a mathematical proof of 4-fold pseudoreplication.
   - When properly aggregated to the independent biological participant level ($N = 10$), the non-uniform displacement effect **remains statistically confirmed** ($\chi^2 = 20.0$, $p = 4.54 \times 10^{-5}$, with all 10 subjects showing deep > middle > superficial displacement).
   - Crucially, however, **layer strain differences are completely non-significant** at the subject level ($\chi^2 = 0.80$, **$p = 0.6703$**).
2. **Demographic Misstatement Corrected:**
   - Cycle 16 reported the cohort as "5 females, 5 males".
   - The primary data (S1 Table) and original publication confirm the true composition is **4 females and 6 males** (Patients 1, 5, 6, 9 Female; Patients 2, 3, 4, 7, 8, 10 Male).
3. **Scientific Novelty Demarcation:**
   - Bogaerts et al. (2017) originally established displacement non-uniformity across layers. Our re-analysis provides necessary statistical correction for pseudoreplication, but does **not** constitute a novel primary discovery. It is classified strictly as `REPRODUCTION_AND_CORRECTION_ONLY`.

---

## 2. Mathematical Audit of the Friedman Test

The Friedman test statistic for $N$ blocks and $k$ treatments is:

$$Q = \frac{12 N}{k(k+1)} \sum_{j=1}^k \bar{R}_j^2 - 3 N (k+1)$$

For $k = 3$ layers (superficial, middle, deep):
$$Q_{\max} = \frac{12 N}{12} (1^2 + 2^2 + 3^2) - 3 N (4) = 14 N - 12 N = 2 N$$

- **Cycle 16 Error:** Cycle 16 fed 40 rows (10 participants $\times$ 2 legs $\times$ 2 reps) directly into the test. $N_{\text{flawed}} = 40 \implies Q_{\max} = 80.0$. The observed $\chi^2 = 59.55$ reflected this inflated sample size.
- **Cycle 17 Correction:** The independent biological unit is the individual participant ($N = 10$). $Q_{\max} = 2 \times 10 = 20.0$.
- **Observed Subject-Level Ranks:** For all 10 participants, superficial displacement was the smallest (rank 1), middle displacement was intermediate (rank 2), and deep displacement was the largest (rank 3). Consequently, the subject-level test statistic is:
  $$Q = 20.0, \quad p = 4.54 \times 10^{-5}$$

---

## 3. Empirical Comparison: Flawed vs. Corrected Analysis

### 3.1. Isometric Plantarflexion (ISO)

| Metric | Cycle 16 Flawed ($N=40$ pseudoreplicated) | Cycle 17 Corrected ($N=10$ subject-aggregated) | Scientific Interpretation |
| :--- | :--- | :--- | :--- |
| **Superficial Disp (mm)** | $2.44 \pm 1.59$ | $2.44 \pm 1.25$ | Basal layer displacement |
| **Middle Disp (mm)** | $2.73 \pm 1.72$ | $2.73 \pm 1.39$ | Core tendon displacement |
| **Deep Disp (mm)** | $3.00 \pm 1.88$ | $3.00 \pm 1.52$ | Ventral layer displacement |
| **Deep - Sup Difference** | $+0.56\text{ mm}$ (unpaired CI) | **$+0.564\text{ mm}$ [95% CI: 0.245, 0.884]** | $+23.1\%$ relative increase |
| **Displacement Omnibus Test** | $\chi^2 = 59.55, p = 1.17 \times 10^{-13}$ | **$\chi^2 = 20.0, p = 4.54 \times 10^{-5}$** | **VERIFIED at subject level** |
| **Paired Student's t-test** | Not reported at subject level | **$t = 3.993, p = 0.0031$** | Significant subject-level effect |
| **Strain Omnibus Test** | $\chi^2 = 4.05, p = 0.132$ | **$\chi^2 = 0.80, p = 0.6703$** | **REFUTED / NON-SIGNIFICANT** |

### 3.2. Passive Motion (PAS)

| Metric | Flawed ($N=40$) | Corrected ($N=10$) | Interpretation |
| :--- | :--- | :--- | :--- |
| **Superficial Disp (mm)** | $-2.32 \pm 1.04$ | $-2.32 \pm 0.77$ | Passive stretch |
| **Deep Disp (mm)** | $-3.10 \pm 1.24$ | $-3.10 \pm 0.99$ | Deep layer displaces 33.6% more |
| **Displacement Omnibus Test** | $\chi^2 = 72.20, p = 2.10 \times 10^{-16}$ | **$\chi^2 = 20.0, p = 4.54 \times 10^{-5}$** | **VERIFIED at subject level** |
| **Strain Omnibus Test** | $\chi^2 = 33.45, p = 5.45 \times 10^{-8}$ | **$\chi^2 = 9.80, p = 0.0074$** | Passive strain gradient retained |

---

## 4. Sensitivity & Bilateral Dependency

1. **Jackknife Stability:**
   Iteratively excluding each of the 10 subjects yielded mean paired displacement differences ranging from **$+0.505\text{ mm}$ to $+0.613\text{ mm}$** (all $> 0$). The effect is robust and not driven by any single outlier participant.
2. **Between-Limb Correlation:**
   Within subjects, the Pearson correlation between left and right limb deep layer displacement was $r = 0.355$ ($p = 0.3137$). While bilateral variation exists, limbs from the same subject share systemic genetic, age, and morphological covariates, confirming that limbs cannot be treated as independent biological units.

---

## 5. Summary Verdict for SUBJECT-01

1. **Displacement Non-Uniformity:** Confirmed on real human subjects ($p = 0.0031$, $Q = 20.0$). The deep layer of the Achilles tendon displaces $23.1\%$ ($0.56\text{ mm}$) more than the superficial layer during isometric plantarflexion.
2. **Strain Non-Uniformity:** Falsified at the subject level during active contraction ($p = 0.6703$). While speckle tracking shows high local variance, systematic layer-dependent strain differences are not statistically detectable at this sample size.
3. **Mechanical Stress:** Remains **BLOCKED**. Without individual sub-tendon cross-sectional areas, mechanical stress ($\sigma = F/\text{CSA}$) cannot be determined.
