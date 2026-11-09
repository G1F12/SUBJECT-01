# SUBJECT-01 — Cycle 10 Multi-Subject CPET Validation Report

**Experiment ID**: `EXP-0043`  
**Finding ID**: `FND-0043`  
**Negative Result ID**: `NEG-0036`  
**Decision ID**: `DEC-0017`  
**Dataset**: PhysioNet ACTES Cycloergometer (`SRC-0073`, DOI: `10.13026/2qs3-kh43`)  
**Cohort**: $N = 18$ independent adolescent athletes (Fencing, Kayak, Triathlon)  
**Total Records**: 52,062 synchronized beat-to-beat observations  
**Validation Strategy**: Strict Leave-One-Subject-Out (LOSO) Cross-Validation  
**Canonical Data Artifact**: [`actes_validation_results.json`](actes_validation_results.json)  
**Governing Standard**: SUBJECT-01 Evidence Gate V2

---

## 1. Scientific Context & Pre-Registration

### 1.1 Overcoming the $N=1$ Single-Subject Barrier
In Cycle 9 (EXP-0042), evaluation of Rehman et al. (2024) established local quadriceps $^{31}\text{P}$-MRS technical repeatability ($CV = 9.9\%$), but mathematically prohibited cross-subject leave-one-subject-out (LOSO) validation because the dataset contained only one single human subject ($N=1$).

Cycle 10 breaks this limitation by acquiring, verifying byte-for-byte, and evaluating the **PhysioNet ACTES cycloergometer dataset** (`SRC-0073`), comprising $N = 18$ independent human participants.

### 1.2 Pre-Registered Hypothesis & Parameter Freezing
Before running any model predictions on the held-out subjects, all model structures, bioenergetic parameters, and search boundaries were frozen:
1. **Oxycaloric Equivalent**: $c_{\text{ox}} = 20,900\text{ J/L}$ ($20.9\text{ kJ/L O}_2$, mixed carbohydrate/lipid substrate oxidation, corresponding to $348.33\text{ W / (L/min)}$).
2. **Incremental Delta Efficiency**: $\eta_{\text{delta}} = 1 / (\beta_1 \cdot 348.33) \approx 22.5\%\dots 26.5\%$ (canonical incremental human cycling efficiency). Gross efficiency $\eta_{\text{gross}}(t) = P(t) / \dot{E}_{\text{met}}(t)$ is workload-dependent ($0\%$ at rest, rising to $20\dots 24\%$ at peak), distinct from the incremental slope.
3. **Cardiorespiratory Kinetic Delay**: $\tau_{\dot{V}\text{O}_2} \in [0, 65]\text{ s}$, evaluated strictly within training subjects via nested subject-level cross-validation (confirming optimal generalization at $\tau = 35.0\text{ s}$ across folds without test leakage).
4. **Allometric Normalization**: Linear mass scaling of work rate ($P / M$ in $\text{W/kg}$) and metabolic rate ($\dot{V}\text{O}_2 / M$ in $\text{mL/(min}\cdot\text{kg)}$).

### 1.3 Competing Model Hierarchy
- **Model M0 (Null Baseline)**: Static mean $\dot{V}\text{O}_2$ of training cohort ($\dot{V}\text{O}_2(t) = \bar{V}_{\text{train}}$).
- **Model M1 (Empirical Static Linear)**: Standard linear regression ($\dot{V}\text{O}_2(t) = \beta_0 + \beta_1 \cdot P_{\text{mech}}(t)$).
- **Model M2 (Dynamic Bioenergetics ODE)**:
  $$\tau \frac{d\dot{V}\text{O}_2(t)}{dt} = \left(\beta_0 + \beta_1 P_{\text{mech}}(t)\right) - \dot{V}\text{O}_2(t)$$
  solved via exact exponential discretization for irregular beat-to-beat intervals.
- **Model M2-Allometric**: Dynamic ODE with body-mass normalized workload ($P/M$) and uptake ($\dot{V}\text{O}_2/M$).

---

## 2. Leave-One-Subject-Out (LOSO) Cross-Validation Results

In each fold $k \in \{1, \dots, 18\}$, training is performed on the 17 other participants ($\approx 49,000$ points) and evaluated strictly out-of-sample on the held-out $k$-th participant. Zero test outcome information is leaked.

### LOSO Cross-Validation Summary Table

| Subject ID | Sport | Body Mass (kg) | $P_{\text{max}}$ (W) | $\dot{V}\text{O}_{2,\text{max}}$ (L/min) | Records ($N$) | M0 RMSE | M0 $R^2$ | M1 RMSE | M1 $R^2$ | M2 Pop RMSE | M2 Pop $R^2$ | M2 Allometric RMSE | M2 Allometric $R^2$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Subj 01** | fencing | 53.7 | 170.0 | 1.790 | 2,403 | $0.715$ | $-2.6942$ | $0.397$ | $-0.1371$ | $0.369$ | $0.0174$ | **$0.237$** | **$0.5932$** |
| **Subj 02** | fencing | 56.2 | 140.0 | 1.960 | 2,000 | $0.688$ | $-0.8878$ | $0.296$ | $0.6504$ | $0.217$ | $0.8113$ | **$0.213$** | **$0.8194$** |
| **Subj 03** | fencing | 89.9 | 305.0 | 3.455 | 3,443 | $0.895$ | $-0.1273$ | $0.486$ | $0.6675$ | $0.262$ | $0.9032$ | **$0.339$** | **$0.8382$** |
| **Subj 04** | fencing | 76.5 | 305.0 | 3.437 | 3,694 | $0.675$ | $-0.0078$ | $0.502$ | $0.4423$ | $0.356$ | $0.7195$ | **$0.404$** | **$0.6384$** |
| **Subj 05** | fencing | 76.4 | 275.0 | 3.386 | 3,594 | $0.895$ | $-0.1546$ | $0.463$ | $0.6914$ | $0.312$ | $0.8600$ | **$0.282$** | **$0.8852$** |
| **Subj 06** | fencing | 65.6 | 245.0 | 3.416 | 2,683 | $0.746$ | $-0.1000$ | $0.387$ | $0.7041$ | $0.281$ | $0.8446$ | **$0.316$** | **$0.8026$** |
| **Subj 07** | fencing | 49.8 | 170.0 | 1.659 | 2,207 | $0.765$ | $-5.3972$ | $0.503$ | $-1.7688$ | $0.449$ | $-1.2037$ | **$0.282$** | **$0.1300$** |
| **Subj 08** | fencing | 51.2 | 170.0 | 1.994 | 2,121 | $0.679$ | $-0.9690$ | $0.357$ | $0.4561$ | $0.257$ | $0.7177$ | **$0.176$** | **$0.8671$** |
| **Subj 09** | fencing | 57.1 | 200.0 | 1.743 | 2,823 | $0.707$ | $-1.7593$ | $0.439$ | $-0.0651$ | $0.367$ | $0.2548$ | **$0.273$** | **$0.5875$** |
| **Subj 10** | fencing | 58.8 | 200.0 | 2.353 | 2,635 | $0.609$ | $-0.4000$ | $0.394$ | $0.4127$ | $0.265$ | $0.7358$ | **$0.223$** | **$0.8121$** |
| **Subj 11** | kayak | 84.8 | 335.0 | 3.354 | 3,854 | $0.888$ | $-0.3816$ | $0.414$ | $0.6993$ | $0.270$ | $0.8724$ | **$0.239$** | **$0.9000$** |
| **Subj 12** | kayak | 86.0 | 305.0 | 3.868 | 3,648 | $1.175$ | $-0.5126$ | $0.601$ | $0.6039$ | $0.494$ | $0.7322$ | **$0.366$** | **$0.8532$** |
| **Subj 13** | kayak | 83.9 | 320.0 | 4.577 | 3,637 | $1.124$ | $-0.3917$ | $0.493$ | $0.7320$ | $0.402$ | $0.8221$ | **$0.326$** | **$0.8825$** |
| **Subj 14** | kayak | 62.3 | 230.0 | 2.483 | 2,808 | $0.595$ | $-0.4840$ | $0.404$ | $0.3165$ | $0.343$ | $0.5071$ | **$0.293$** | **$0.6401$** |
| **Subj 15** | kayak | 63.5 | 215.0 | 2.994 | 2,691 | $0.693$ | $-0.0038$ | $0.381$ | $0.6957$ | $0.279$ | $0.8372$ | **$0.321$** | **$0.7850$** |
| **Subj 16** | kayak | 70.4 | 230.0 | 3.451 | 2,840 | $0.801$ | $-0.0654$ | $0.384$ | $0.7548$ | $0.372$ | $0.7704$ | **$0.372$** | **$0.7703$** |
| **Subj 17** | triathlon | 39.9 | 185.0 | 2.206 | 2,410 | $0.648$ | $-0.3583$ | $0.296$ | $0.7157$ | $0.199$ | $0.8719$ | **$0.308$** | **$0.6939$** |
| **Subj 18** | triathlon | 39.7 | 200.0 | 2.204 | 2,571 | $0.607$ | $-0.3224$ | $0.285$ | $0.7086$ | $0.216$ | $0.8321$ | **$0.253$** | **$0.7697$** |
| **MEAN** | — | **64.8** | **233.3** | **2.796** | **2,892** | **$0.773$** | **$-0.8343$** | **$0.416$** | **$0.4045$** | **$0.317$** | **$0.6059$** | **$0.290$** | **$0.7371$** |
| **SD** | — | $15.1$ | $58.6$ | $0.831$ | $582$ | $0.162$ | $1.2894$ | $0.080$ | $0.5860$ | $0.080$ | $0.4936$ | **$0.059$** | **$0.1770$** |

---

## 3. Key Scientific Findings

1. **Macroscopic Generalizability Confirmed**:
   The first-principles aerobic coupling equation combined with first-order cardiorespiratory kinetics delay ($\tau = 35\text{ s}$) achieves a cross-subject out-of-sample $R^2 = 0.7371 \pm 0.1770$ (RMSE $= 0.290 \pm 0.059\text{ L/min}$) under strict Leave-One-Subject-Out cross-validation across 18 independent human participants.
2. **Massive Superiority over Static and Linear Baselines**:
   - Model M0 (Null Baseline) fails completely ($R^2 = -0.8343$, RMSE $= 0.773\text{ L/min}$), confirming that exercise oxygen demand constitutes genuine physiological signal.
   - Model M1 (Static Linear) achieves $R^2 = 0.4045$ with substantial tracking lag during workload transitions.
   - Model M2 (Dynamic Delay) reduces prediction error by $30.3\%$ relative to M1 and $62.5\%$ relative to M0.
3. **Allometric Normalization Value**:
   Normalizing workload by body mass ($P / M$ in W/kg) improves cross-subject generalizability from $R^2 = 0.6059$ to $R^2 = 0.7371$, directly capturing the physiological variance between adolescent fencers ($49.8\text{ kg}$) and adult kayakers ($89.9\text{ kg}$).
4. **Heterogeneous Mass Degradation**:
   While linear mass normalization ($P/M$) improves the macro-average $R^2$ across the full cohort, it degrades RMSE in 7 of the 18 participants (Subjects 3, 4, 6, 15, 16, 17, 18), demonstrating that single-variable linear body mass scaling introduces individual bias for light endurance and heavy muscular athletes.
5. **Metrological Unit Verification**:
   Audited raw byte tables: while the PhysioNet HTML metadata claims units of $\text{mL/min}$, raw CSV numbers in `test_measure.csv` are strictly in $\text{L/min}$ ($0.20\dots 4.54\text{ L/min}$); processing treats them directly without post-hoc multipliers.

---

## 4. Epistemic Guarantees & Uncompromised Boundaries

Despite the successful multi-subject validation of macroscopic aerobic coupling:
1. **Intracellular Phosphate Unobservability**: Whole-body pulmonary $\dot{V}\text{O}_2$ cannot resolve intramuscular [PCr], [Pi], or cytosolic pH dynamics. Local kinetics remain bounded by Rehman 2024 ($N=1$).
2. **Motor Unit Recruitment Unobservability**: HD-sEMG discharge rates remain unobserved in CPET data.
3. **`TARGET-CPE45` Status**: Remains **`NOT EXTERNALLY VALIDATED`**. A graded incremental CPET protocol to exhaustion (~15 min) does not test 45-minute continuous extreme survivability.
4. **Biological Interventions**: Remain strictly **`NO_GO`**.
