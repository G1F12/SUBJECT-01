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
1. **Oxycaloric Equivalent**: $c_{\text{ox}} = 20,900\text{ J/L}$ ($20.9\text{ kJ/L O}_2$, mixed carbohydrate/lipid substrate oxidation).
2. **Gross Mechanical Efficiency**: $\eta_{\text{gross}} \in [0.18, 0.28]$ (canonical human cycling efficiency range).
3. **Cardiorespiratory Kinetic Delay**: $\tau_{\dot{V}\text{O}_2} = 35.0\text{ s}$ (standard Phase II pulmonary gas exchange time constant).
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
| **Subj 01** | fencing | 53.7 | 170.0 | 1.790 | 2,403 | $0.627$ | $-1.8315$ | $0.370$ | $0.0152$ | $0.239$ | $0.5898$ | **$0.231$** | **$0.6151$** |
| **Subj 02** | fencing | 56.2 | 140.0 | 1.960 | 2,000 | $0.686$ | $-1.3853$ | $0.354$ | $0.3644$ | $0.231$ | $0.7290$ | **$0.230$** | **$0.7303$** |
| **Subj 03** | fencing | 89.9 | 305.0 | 3.455 | 3,443 | $0.941$ | $-0.2452$ | $0.449$ | $0.7163$ | $0.342$ | $0.8354$ | **$0.334$** | **$0.8427$** |
| **Subj 04** | fencing | 76.5 | 305.0 | 3.437 | 3,694 | $0.722$ | $-0.0384$ | $0.468$ | $0.5630$ | $0.370$ | $0.7268$ | **$0.347$** | **$0.7594$** |
| **Subj 05** | fencing | 76.4 | 275.0 | 3.386 | 3,594 | $0.893$ | $-0.2198$ | $0.435$ | $0.7107$ | $0.320$ | $0.8436$ | **$0.311$** | **$0.8520$** |
| **Subj 06** | fencing | 65.6 | 245.0 | 3.416 | 2,683 | $0.884$ | $-0.3298$ | $0.374$ | $0.7618$ | $0.264$ | $0.8809$ | **$0.238$** | **$0.9038$** |
| **Subj 07** | fencing | 49.8 | 170.0 | 1.659 | 2,207 | $0.640$ | $-4.6186$ | $0.466$ | $-1.9804$ | $0.419$ | $-1.4087$ | **$0.325$** | **$-0.4507$** |
| **Subj 08** | fencing | 51.2 | 170.0 | 1.994 | 2,121 | $0.669$ | $-1.8617$ | $0.370$ | $0.1245$ | $0.222$ | $0.6862$ | **$0.213$** | **$0.7118$** |
| **Subj 09** | fencing | 57.1 | 200.0 | 1.743 | 2,823 | $0.605$ | $-1.7042$ | $0.435$ | $-0.4002$ | $0.334$ | $0.1746$ | **$0.288$** | **$0.3887$** |
| **Subj 10** | fencing | 58.8 | 200.0 | 2.353 | 2,635 | $0.799$ | $-0.9026$ | $0.309$ | $0.7153$ | $0.197$ | $0.8839$ | **$0.196$** | **$0.8859$** |
| **Subj 11** | kayak | 84.8 | 335.0 | 3.354 | 3,854 | $0.803$ | $-0.3749$ | $0.548$ | $0.3582$ | $0.469$ | $0.5310$ | **$0.401$** | **$0.6570$** |
| **Subj 12** | kayak | 86.0 | 305.0 | 3.868 | 3,648 | $1.066$ | $-0.0934$ | $0.437$ | $0.8166$ | $0.347$ | $0.8841$ | **$0.330$** | **$0.8953$** |
| **Subj 13** | kayak | 83.9 | 320.0 | 4.577 | 3,637 | $1.157$ | $0.1118$ | $0.482$ | $0.8454$ | $0.395$ | $0.8963$ | **$0.357$** | **$0.9152$** |
| **Subj 14** | kayak | 62.3 | 230.0 | 2.483 | 2,808 | $0.655$ | $-0.7490$ | $0.400$ | $0.3463$ | $0.315$ | $0.5936$ | **$0.283$** | **$0.6720$** |
| **Subj 15** | kayak | 63.5 | 215.0 | 2.994 | 2,691 | $0.864$ | $-0.6277$ | $0.305$ | $0.7972$ | $0.215$ | $0.8996$ | **$0.222$** | **$0.8929$** |
| **Subj 16** | kayak | 70.4 | 230.0 | 3.451 | 2,840 | $0.918$ | $-0.2638$ | $0.345$ | $0.8220$ | $0.259$ | $0.8998$ | **$0.284$** | **$0.8795$** |
| **Subj 17** | triathlon | 39.9 | 185.0 | 2.206 | 2,410 | $0.598$ | $-0.5518$ | $0.393$ | $0.3308$ | $0.315$ | $0.5699$ | **$0.245$** | **$0.7405$** |
| **Subj 18** | triathlon | 39.7 | 200.0 | 2.204 | 2,571 | $0.601$ | $-0.4611$ | $0.380$ | $0.4144$ | $0.297$ | $0.6402$ | **$0.229$** | **$0.7788$** |
| **MEAN** | — | **65.6** | **235.8** | **2.888** | **2,892** | **$0.773$** | **$-0.8343$** | **$0.416$** | **$0.4045$** | **$0.317$** | **$0.6059$** | **$0.290$** | **$0.7371$** |
| **SD** | — | $15.5$ | $61.0$ | $0.835$ | $599$ | $0.162$ | $1.2894$ | $0.080$ | $0.5860$ | $0.080$ | $0.4936$ | **$0.059$** | **$0.1770$** |

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

---

## 4. Epistemic Guarantees & Uncompromised Boundaries

Despite the successful multi-subject validation of macroscopic aerobic coupling:
1. **Intracellular Phosphate Unobservability**: Whole-body pulmonary $\dot{V}\text{O}_2$ cannot resolve intramuscular [PCr], [Pi], or cytosolic pH dynamics. Local kinetics remain bounded by Rehman 2024 ($N=1$).
2. **Motor Unit Recruitment Unobservability**: HD-sEMG discharge rates remain unobserved in CPET data.
3. **`TARGET-CPE45` Status**: Remains **`NOT EXTERNALLY VALIDATED`**. A graded incremental CPET protocol to exhaustion (~15 min) does not test 45-minute continuous extreme survivability.
4. **Biological Interventions**: Remain strictly **`NO_GO`**.
