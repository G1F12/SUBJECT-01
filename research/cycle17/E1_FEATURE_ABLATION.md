# EXPERIMENT E1-ISO REANALYSIS: FACTORIAL FEATURE ABLATION
## Disentangling Anthropometric Dominance and Surface EMG Noise in Human Torque Prediction

**Document ID:** `research/cycle17/E1_FEATURE_ABLATION.md`  
**Date:** 2026-11-12  
**Dataset:** DPValid Collection (AMS Acta 7710, DOI: `10.6092/unibo/amsacta/7710`)  
**Cohort:** 20 healthy adults (10 Females, 10 Males; 125 knee extension trials)  
**Evaluation Protocol:** Strict Leave-One-Subject-Out (LOSO) Cross-Validation ($N = 20$ folds)  
**Status:** Completed  
**Related Documents:**
- [E1_RESULTS.json](file:///D:/SUBJECT-01/research/cycle17/E1_RESULTS.json)
- [CYCLE16_FORENSIC_AUDIT.md](file:///D:/SUBJECT-01/research/cycle17/CYCLE16_FORENSIC_AUDIT.md)

---

## 1. Scientific Aim & The Confounding Problem in Cycle 16

In Cycle 16, Model M4 achieved an out-of-sample pooled $R^2$ of **0.6301** (RMSE = 53.45 Nm), compared to Model M1 ($R^2 = 0.1112$, RMSE = 82.85 Nm). Cycle 16 concluded that "combining joint angle, demographics, and multichannel EMG" provided a synergistic predictive model.

However, Model M4 differed from M1 in two major dimensions simultaneously:
1. It added 5 demographic/kinematic variables (knee angle, body mass, height, age, biological sex).
2. It added 2 antagonist EMG channels (BF, ST).
3. It switched from Ordinary Least Squares (OLS) to regularized Ridge regression.

To resolve whether surface EMG contributed any genuine predictive signal, or whether the performance was driven entirely by anthropometrics, a complete $2 \times 5$ factorial ablation was executed under identical LOSO cross-validation folds.

---

## 2. Factorial Experimental Design

### 2.1. Feature Sets
- **F0 (Kinematics & Anthropometry):** `angle_deg`, `mass`, `height`, `age`, `sex_code` (0 EMG channels).
- **F1 (Agonist sEMG only):** `emg_RF`, `emg_VM`, `emg_VL` (3 channels).
- **F2 (Agonist + Antagonist sEMG):** `emg_RF`, `emg_VM`, `emg_VL`, `emg_BF`, `emg_ST` (5 channels).
- **F3 (Anthropometry + Agonist sEMG):** F0 + F1 (8 features).
- **F4 (Anthropometry + All sEMG):** F0 + F2 (10 features, equivalent to Cycle 16 M4).

### 2.2. Algorithmic Control
Every feature set was evaluated using both:
- **Ordinary Least Squares (OLS)**.
- **L2 Regularized Ridge Regression (RidgeCV)** with internal nested validation ($\alpha \in [10^{-2}, 10^3]$) fitted exclusively on training folds.
- Standard scaling (mean zero, unit variance) fitted strictly on the 19 training subjects in each fold.

---

## 3. Empirical Results: Full Factorial Matrix

### 3.1. Generalization Performance Across All 20 Subjects (125 Trials)

| Feature Set | Features Description | Algorithm | Pooled RMSE (Nm) | 95% Bootstrap CI | Pooled MAE (Nm) | Pooled $R^2$ | Mean Subject RMSE (Nm) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F0** | Angle + Anthropometry | **OLS** | **49.56** | [41.2, 57.8] | **37.54** | **0.6820** | **42.54** |
| **F0** | Angle + Anthropometry | **Ridge** | **49.19** | [41.0, 57.3] | **37.39** | **0.6867** | **42.38** |
| **F1** | Agonist EMG only | OLS | 82.85 | [66.5, 99.8] | 58.49 | 0.1112 | 66.57 |
| **F1** | Agonist EMG only | Ridge | 81.90 | [66.0, 98.4] | 59.08 | 0.1316 | 67.01 |
| **F2** | Agonist + Antagonist EMG | OLS | 89.10 | [71.5, 106.4] | 62.47 | -0.0280 | 70.52 |
| **F2** | Agonist + Antagonist EMG | Ridge | 82.39 | [69.3, 95.7] | 60.45 | 0.1211 | 68.13 |
| **F3** | Anthropometry + Agonist | OLS | 52.29 | [43.8, 60.7] | 39.25 | 0.6460 | 43.87 |
| **F3** | Anthropometry + Agonist | Ridge | 51.28 | [43.1, 59.3] | 38.35 | 0.6596 | 42.82 |
| **F4** | Anthropometry + All EMG | OLS | 54.20 | [45.8, 62.6] | 42.05 | 0.6196 | 46.86 |
| **F4** | Anthropometry + All EMG | Ridge | 53.45 | [45.3, 61.2] | 41.31 | 0.6301 | 45.83 |

---

## 4. Formal Hypothesis Testing on Planned Contrasts

### 4.1. Primary Contrast 1: Does Antagonist EMG Add Value Over Agonist + Anthropometry? (`F4 vs. F3`)
- **Metric:** Subject-paired $\Delta \text{RMSE} = \text{RMSE}_i(F3) - \text{RMSE}_i(F4)$ (positive = F4 improves).
- **Observed Mean Difference:** $\Delta \text{RMSE} = \mathbf{-3.01 \pm 4.67\text{ Nm}}$.
- **Paired Student's t-test:** $t = -2.879$, **$p = 0.0089$**.
- **Wilcoxon Signed-Rank Test:** $W = 34.0$, **$p = 0.0121$**.
- **Scientific Verdict:** Adding antagonist surface EMG **statistically significantly degrades** out-of-sample torque prediction ($p < 0.01$). Antagonist EMG acts as a pure noise injector in cross-subject models.

### 4.2. Planned Contrast 2: Does Agonist EMG Add Value Over Anthropometry Alone? (`F3 vs. F0`)
- **Metric:** Subject-paired $\Delta \text{RMSE} = \text{RMSE}_i(F0) - \text{RMSE}_i(F3)$ (positive = F3 improves).
- **Observed Mean Difference:** $\Delta \text{RMSE} = \mathbf{-0.44 \pm 2.27\text{ Nm}}$.
- **Paired Student's t-test:** $t = -0.865$, **$p = 0.9337$** (one-tailed for improvement).
- **Wilcoxon Signed-Rank Test:** $W = 91.0$, **$p = 0.7562$**.
- **Scientific Verdict:** Agonist surface EMG provides **zero statistically significant incremental benefit** over anthropometry and joint angle alone. Adding agonist EMG increases RMSE from 49.19 Nm to 51.28 Nm.

### 4.3. Planned Contrast 3: Does All EMG Add Value Over Anthropometry Alone? (`F4 vs. F0`)
- **Metric:** Subject-paired $\Delta \text{RMSE} = \text{RMSE}_i(F0) - \text{RMSE}_i(F4)$.
- **Observed Mean Difference:** $\Delta \text{RMSE} = \mathbf{-3.45 \pm 5.12\text{ Nm}}$.
- **Paired Student's t-test:** $t = -3.014$, **$p = 0.0071$**.
- **Scientific Verdict:** Combining all surface EMG with anthropometry significantly worsens prediction accuracy compared to anthropometry alone.

---

## 5. Sex-Stratified Sensitivity Analysis

To test whether anthropometry was merely serving as a proxy for biological sex, models were re-evaluated within single-sex cohorts ($N = 10$ males, $N = 10$ females):

| Cohort | Feature Set | Pooled RMSE (Nm) | Pooled $R^2$ |
| :--- | :--- | :--- | :--- |
| **Males ($N = 10$)** | F0 (Angle, Mass, Height, Age) | **56.78** | **0.4675** |
| | F4 (F0 + All 5 EMG channels) | **104.68** | **-0.8102** |
| **Females ($N = 10$)** | F0 (Angle, Mass, Height, Age) | **40.52** | **-0.1673** |
| | F4 (F0 + All 5 EMG channels) | **48.68** | **-0.6848** |

### Critical Finding:
When evaluated strictly within males, adding surface EMG **doubled the out-of-sample RMSE** (from 56.78 Nm to 104.68 Nm) and collapsed $R^2$ from $+0.4675$ to $-0.8102$! This definitively demonstrates the severe overfitting risk of raw multichannel surface EMG in unseen individuals.

---

## 6. Physiological & Methodological Discussion

1. **Why Does Raw sEMG Fail Across Subjects?**
   Surface EMG measures potential differences at the skin surface, which are heavily filtered by the subcutaneous adipose tissue layer. The tissue transfer function varies by orders of magnitude between individuals. An uncalibrated 0.3 mV envelope in a lean individual reflects a different neural drive than a 0.3 mV envelope in an individual with thicker subcutaneous fat.
2. **Why Is Anthropometry Dominant?**
   Maximum isometric torque is governed by:
   $$\tau = F_{\text{muscle}} \cdot r_{\text{moment\_arm}}(\theta) = (\text{PCSA} \cdot \sigma_{\text{spec}}) \cdot r(\theta)$$
   Physiological cross-sectional area (PCSA) scales with body mass and height. Specific tension ($\sigma_{\text{spec}}$) differs by biological sex. Knee angle ($\theta$) governs both fiber length along the force-length curve and the patellar tendon moment arm. These physical invariants explain over 68% of torque variance across humans.
3. **The Role of Antagonist Co-activation:**
   While hamstrings co-activation physically generates an opposing flexor torque, its amplitude during isometric extension is small (~8–11% of agonist amplitude). Inter-individual variance in sensor placement and skin impedance on the posterior thigh introduces more noise than signal. Population models attempting to fit antagonist sEMG across subjects inevitably overfit this noise.

---

## 7. Conclusions for SUBJECT-01

- **Cycle 16 Correction:** The claim that M4 succeeded because of EMG synergy is **refuted**. Anthropometrics and kinematics alone (F0) achieve the superior result (RMSE = 49.19 Nm, $R^2 = 0.6867$).
- **Status of EMG in Population Models:** Raw surface EMG cannot be used for cross-subject torque prediction without subject-specific calibration (e.g., individual MVIC normalization).
- **Status of Human Enhancement:** High predictive accuracy of torque from body mass and angle ($R^2 = 0.69$) represents morphological physics, **not biological human strength enhancement**.
