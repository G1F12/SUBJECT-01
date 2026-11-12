# EXPERIMENT E1-ISO: INDEPENDENT HUMAN ISOMETRIC STRENGTH VALIDATION
## Neuromuscular EMG Torque Prediction and Antagonist Co-activation Analysis

**Experiment ID:** `EXP-0051`  
**Document ID:** `research/cycle16/E1_ISOMETRIC_STRENGTH.md`  
**Date:** 2026-11-12  
**Dataset:** DPValid Collection, University of Bologna (AMS Acta 7710, DOI: `10.6092/unibo/amsacta/7710`)  
**Cross-Validation Protocol:** Participant-Level Leave-One-Subject-Out (LOSO) Cross-Validation ($N = 20$ folds)  
**Status:** Completed  
**Related Documents:**
- [E1_MODEL_COMPARISON.json](file:///D:/SUBJECT-01/research/cycle16/E1_MODEL_COMPARISON.json)
- [E1_REPRODUCIBILITY.md](file:///D:/SUBJECT-01/research/cycle16/E1_REPRODUCIBILITY.md)
- [DATASET_VERIFICATION.md](file:///D:/SUBJECT-01/research/cycle16/DATASET_VERIFICATION.md)

---

## 1. Scientific Aim & Hypothesis

A central claim in neuromusculoskeletal modeling is that measuring antagonist muscle co-activation (e.g., hamstrings during knee extension, or quadriceps during knee flexion) substantially refines joint torque estimation by accounting for joint flexion/extension counter-torques:

$$\tau_{\text{net}} = \tau_{\text{agonist}} - \tau_{\text{antagonist}}$$

In Research Cycle 15, issue `ISS-0022` noted that antagonist co-activation effects had not been evaluated on real, independent human dynamometry datasets with synchronous multichannel sEMG under strict out-of-sample cross-validation.

### Core Hypothesis Tested:
- **$H_0$:** Incorporating directly measured antagonist surface EMG into a linear/regularized model does not improve out-of-sample joint torque prediction over an agonist-only model in unseen human subjects ($\Delta \text{RMSE} = \text{RMSE}(M_1) - \text{RMSE}(M_2) \le 0$).
- **$H_1$:** Antagonist surface EMG inclusion significantly reduces prediction error on held-out subjects ($\Delta \text{RMSE} > 0$, $p < 0.05$).

---

## 2. Experimental Data & Cohort

- **Cohort:** 20 healthy human participants (10 females, 10 males; age $31.0 \pm 6.1$ years, body mass $66.8 \pm 14.5\text{ kg}$, height $1.68 \pm 0.08\text{ m}$).
- **Tested Movements:**
  1. Maximum Voluntary Isometric Knee Extension (EXT) at $75^\circ$ and $90^\circ$ of knee flexion ($N = 125$ valid trials).
  2. Maximum Voluntary Isometric Knee Flexion (FLEX) at $75^\circ$ and $90^\circ$ of knee flexion ($N = 122$ total trials, $N = 121$ clean trials after removing one single dynamometer sensor saturation artifact of 717.9 Nm in HA16 r3).
- **EMG Envelopes:**
  - *Extension Agonists:* Rectus Femoris (RF), Vastus Medialis (VM), Vastus Lateralis (VL).
  - *Extension Antagonists:* Biceps Femoris long head (BF), Semitendinosus (ST).
  - *Flexion Agonists:* Biceps Femoris (BF), Semitendinosus (ST).
  - *Flexion Antagonists:* Rectus Femoris (RF), Vastus Medialis (VM), Vastus Lateralis (VL).

---

## 3. Model Architecture & Formulations

Five nested models were constructed and evaluated on identical folds:

1. **M0 (Baseline Mean):** Predicts the training-fold sample mean torque:
   $$\hat{y}_i = \bar{y}_{\text{train}}$$
2. **M1 (Agonist-Only OLS):** Ordinary least-squares regression trained exclusively on agonist muscle sEMG envelopes:
   $$\hat{y}_i = \beta_0 + \sum_{j \in \text{agonists}} \beta_j X_{ij}$$
3. **M2 (Agonist + Antagonist OLS):** Ordinary least-squares regression including both agonist and antagonist sEMG envelopes:
   $$\hat{y}_i = \beta_0 + \sum_{j \in \text{agonists}} \beta_j X_{ij} + \sum_{k \in \text{antagonists}} \beta_k X_{ik}$$
4. **M3 (Regularized Ridge Regression):** Ridge regression on all EMG channels (agonist + antagonist) with internal nested cross-validation for penalty parameter $\alpha \in [10^{-2}, 10^{3}]$:
   $$\min_{\beta} \|y - X\beta\|_2^2 + \alpha \|\beta\|_2^2$$
5. **M4 (Full Biomechanical Control):** Ridge regression incorporating joint angle ($75^\circ$ vs $90^\circ$), anthropometrics (body mass, height, age, biological sex), and all sEMG channels.

---

## 4. Empirical Results

### 4.1. Knee Extension Performance ($N = 125$ trials, 20 folds)

| Model ID | Features Included | Pooled RMSE (Nm) | 95% Bootstrap CI | Pooled MAE (Nm) | Pooled $R^2$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M0** | Training Mean Baseline | 91.30 | [80.2, 103.8] | 73.42 | -0.0793 |
| **M1** | Agonists (RF, VM, VL) | 82.85 | [66.5, 99.8] | 58.49 | 0.1112 |
| **M2** | Agonists + Antagonists (OLS) | 89.10 | [71.5, 106.4] | 62.47 | -0.0280 |
| **M3** | Agonists + Antagonists (Ridge) | 82.39 | [69.3, 95.7] | 60.45 | 0.1211 |
| **M4** | Angle + Demographics + EMG | **53.45** | **[45.3, 61.2]** | **41.31** | **0.6301** |

#### Hypothesis Test for Extension (M1 vs M2):
- Mean paired subject difference: $\Delta \text{RMSE} = -3.94 \pm 11.7\text{ Nm}$ (unregularized M2 performed worse than M1).
- Paired Student's t-test: $t = -1.530$, $p = 0.1426$.
- Wilcoxon signed-rank test: $W = 75.0$, $p = 0.2863$.
- **Outcome:** The null hypothesis $H_0$ cannot be rejected. Adding unregularized antagonist EMG to an OLS model does *not* significantly improve generalizable torque estimation across unseen individuals.

### 4.2. Knee Flexion Performance ($N = 121$ clean trials, 20 folds)

| Model ID | Features Included | Pooled RMSE (Nm) | 95% Bootstrap CI | Pooled MAE (Nm) | Pooled $R^2$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M0** | Training Mean Baseline | 27.26 | [24.5, 30.1] | 22.28 | -0.0873 |
| **M1** | Agonists (BF, ST) | 29.80 | [26.9, 32.9] | 24.42 | -0.2999 |
| **M2** | Agonists + Antagonists (OLS) | 30.63 | [27.7, 33.7] | 25.90 | -0.3731 |
| **M3** | Agonists + Antagonists (Ridge) | 30.43 | [27.5, 33.4] | 25.76 | -0.3554 |
| **M4** | Angle + Demographics + EMG | **19.61** | **[16.2, 23.1]** | **14.67** | **0.4371** |

#### Hypothesis Test for Flexion (M1 vs M2):
- Mean paired subject difference: $\Delta \text{RMSE} = -2.05 \pm 7.5\text{ Nm}$.
- Paired Student's t-test: $t = -1.216$, $p = 0.2388$.
- Wilcoxon signed-rank test: $W = 70.0$, $p = 0.2045$.
- **Outcome:** Null hypothesis $H_0$ retained.

---

## 5. Critical Biomechanical & Neuromuscular Findings

1. **Failure of Raw sEMG for Cross-Subject Generalization:**
   - Raw surface EMG envelopes without subject-specific calibration show weak generalizability across unseen humans ($R^2 = 0.11$ for extension, $R^2 < 0$ for flexion).
   - This limitation stems from individual differences in subcutaneous adipose tissue layer thickness, electrode impedance, skin conductivity, and motor unit spatial recruitment profiles.
2. **The Antagonist Overfitting Phenomenon (M2 vs M1):**
   - Unregularized inclusion of antagonist channels (M2) consistently increased generalization error ($\Delta \text{RMSE} = -3.94\text{ Nm}$ in extension).
   - Because antagonist co-activation is low in magnitude (~8–11% of agonist amplitude) and varies considerably across subjects, an unregularized cross-subject OLS model fits spurious inter-individual co-activation noise, leading to worse predictions on new subjects.
   - When L2 regularization is applied (M3 Ridge), the model shrinks antagonist coefficients, recovering an RMSE of 82.39 Nm ($R^2 = 0.1211$), essentially on par with M1.
3. **Dominance of Anthropometrics and Joint Kinematics (M4):**
   - Incorporating joint angle ($75^\circ$ vs $90^\circ$), body mass, height, age, and sex (M4) produces a dramatic improvement:
     - Extension RMSE drops from 82.85 Nm to **53.45 Nm** ($R^2$ jumps from 0.11 to **0.6301**).
     - Flexion RMSE drops from 29.80 Nm to **19.61 Nm** ($R^2$ jumps to **0.4371**).
   - Biomechanical explanation: Peak joint torque is primarily dictated by muscular cross-sectional area (scaled with body mass and height), sex-specific specific tension, and the non-linear force-length and moment-arm curves of the patellar tendon across knee angles.

---

## 6. Resolution of Issue ISS-0022

- **Issue ISS-0022 Status:** **RESOLVED FOR ISOMETRIC REGIMES**.
- **Conclusion:** While antagonist co-activation is physiologically real and modulates net joint stiffness, measuring surface antagonist EMG without subject-specific calibration does *not* enhance generalizable isometric joint torque predictions in cross-subject models.
- **Guidance for SUBJECT-01:** Models predicting functional human strength capacity must prioritize anthropometric scaling and kinematic moment-arm functions. Pure sEMG-driven torque estimation requires subject-level calibration (e.g., individual MVIC normalization) rather than uncalibrated population regressors.
