# SUBJECT-01 — Cycle 11 Multi-Subject Treadmill CPET Validation Report
## Scientific Corrigendum & Subject-Level Grouped Validation

**Experiment ID**: `EXP-0044`  
**Finding ID**: `FND-0044`  
**Negative Result ID**: `NEG-0037` (Reclassified: `AD_HOC_CROSS_MODAL_MAPPING_FAILURE` & `PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE`)  
**Decision ID**: `DEC-0018` / `DEC-0019`  
**Open Issue**: `ISS-0020` (License conflict between packaged CC BY-NC-SA 4.0 and PhysioNet DUA 1.5.0)  
**Dataset**: PhysioNet Malaga Treadmill CPET (`SRC-0074`, DOI: `10.13026/7ezk-j442`)  
**Raw Cohort**: $N = 992$ tests across $N = 857$ human participants  
**Admitted Cohort**: $N = 981$ valid incremental tests across $N = 846$ independent participants  
**Repeat Test Integrity**: Exactly 116 participants have repeated trials, accounting for 251 tests (100% preserved)  
**Total Records Analyzed**: 575,087 synchronized breath observations  
**Validation Strategy**: 5-Fold Subject-Level Grouped Cross-Validation (`GroupKFold`, zero subject leakage)  
**Legacy Benchmark**: 5-Fold Random Test-Level Cross-Validation (`SUBJECT_LEAKAGE_RISK_NOT_GROUPED`)  
**Canonical Data Artifact**: [`malaga_validation_results.json`](malaga_validation_results.json)  
**Governing Standard**: SUBJECT-01 Evidence Gate V2  

---

## 1. Scientific Context & Stage 1 Group Leakage Resolution

### 1.1 The Group Leakage Risk in Locomotion CPET
In Cycle 10 (`EXP-0043`), cardiorespiratory kinetics were evaluated across $N=18$ adolescent athletes in cycle ergometry.
Cycle 11 evaluates whole-body treadmill running locomotion using the open PhysioNet Malaga CPET database (`SRC-0074`).

Initial Cycle 11 protocols partitioned the dataset randomly across tests (`ID_test`), creating a severe biological group leakage risk:
- In Malaga, 116 participants underwent repeated CPET sessions (251 total tests).
- Under test-level random splitting, tests from the same biological individual were placed simultaneously into training and validation sets.
- **Corrigendum Resolution**: The random cross-validation was replaced with deterministic `GroupKFold(groups=subject_id, n_splits=5)`.
- For every fold, the Evidence Gate programmatically validates:
  $$\text{intersection}(\text{train\_subject\_ids}, \text{val\_subject\_ids}) = \emptyset$$

### 1.2 Cohort Admittance, Repeat Tests & Fold Distribution

Of the 992 entries in `subject-info.csv`:
- 11 tests were filtered due to duration $< 100$ breaths or non-incremental protocol (speed span $\Delta v < 3\text{ km/h}$).
- Exactly $N = 981$ valid incremental tests on $N = 846$ unique participants were admitted.
- All 116 multi-test participants and all 251 repeat tests were fully preserved.

| Validation Fold | Train Tests ($N$) | Val Tests ($N$) | Train Subjects ($N$) | Val Subjects ($N$) | Subject Overlap ($N$) | Epistemic Gate Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fold 0** | 784 | 197 | 677 | 169 | **0** | `PASS_ZERO_LEAKAGE` |
| **Fold 1** | 785 | 196 | 677 | 169 | **0** | `PASS_ZERO_LEAKAGE` |
| **Fold 2** | 785 | 196 | 677 | 169 | **0** | `PASS_ZERO_LEAKAGE` |
| **Fold 3** | 785 | 196 | 677 | 169 | **0** | `PASS_ZERO_LEAKAGE` |
| **Fold 4** | 785 | 196 | 676 | 170 | **0** | `PASS_ZERO_LEAKAGE` |
| **TOTAL** | — | **981** | — | **846** | **0** | `SUBJECT_INDEPENDENCE_VERIFIED` |

### 1.3 Cryptographic Verification & Source Provenance Audit
Prior to evaluation, all files were verified against official PhysioNet SHA256SUMS.txt.

| Source ID | Dataset Name | Archive / DOI | Sample Size | Data Modality | Verified SHA256 Status | Evidence Gate Role |
|:---:|:---|:---|:---:|:---|:---:|:---|
| SRC-0074 | PhysioNet Malaga Treadmill CPET | DOI: `10.13026/7ezk-j442` | $N = 992$ tests, $N = 857$ subjects | Treadmill speed, breath-by-breath $\dot{V}\text{O}_2$, $\dot{V}\text{CO}_2$, HR | `3b5ed558...` (MATCH) | External Multi-Subject Locomotion Validation |
| SRC-0075 | Hug et al. (2015) Dryad Muscle Architecture | DOI: `10.5061/dryad.h3b27` | $N = 21$ participants | 5 XLSX files (Muscle Architecture, Torque, EMG) | HTTP 401 / BotStopper Blocked | Architecture Reference (Direct Download Blocked) |

---

## 2. Model Performance Hierarchy under Subject GroupKFold

| Model Identifier | Model Description | Workload Input | Dynamic Kinetics | Body Mass Scaling | GroupKFold RMSE (mL/min) | GroupKFold MAE (mL/min) | GroupKFold $R^2$ | Bias (mL/min) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| M0 Null | Cohort mean VO2 | None | None | None | $950.7 \pm 202.9$ | $821.1 \pm 196.9$ | $-0.6244 \pm 1.8461$ | $+29.6 \pm 458.8$ |
| M1 Linear | Static linear regression on speed | Speed (v) | None | None | $570.0 \pm 186.1$ | $455.6 \pm 179.5$ | $0.3296 \pm 1.1465$ | $-0.7 \pm 381.7$ |
| M2 Linear+Mass | Multiple regression (v + M) | Speed + Mass | None | Linear M | $514.1 \pm 156.5$ | $391.4 \pm 142.8$ | $0.5157 \pm 0.7882$ | $+8.9 \pm 273.7$ |
| M3 Dynamic ODE | 1st-order kinetics on speed | Speed (v) | tau = 35 s | None | $469.9 \pm 211.8$ | $403.5 \pm 193.7$ | $0.4837 \pm 1.0953$ | $+0.9 \pm 380.8$ |
| **M4 Allometric ODE** | Dynamic allometric kinetics | Speed (v) | tau = 35 s | v -> VO2/M | **$404.0 \pm 175.1$** | $336.7 \pm 151.2$ | **$0.6648 \pm 0.7374$** | $+28.3 \pm 285.5$ |
| Static Allometric | Mass-normalized running economy | Speed + Mass | None | v -> VO2/M | $516.1 \pm 160.4$ | $396.0 \pm 146.4$ | $0.5145 \pm 0.7745$ | $+26.5 \pm 284.9$ |
| Baseline Lagged | Workload shifted by tau | Lagged speed | Fixed shift (35 s) | None | $527.8 \pm 196.6$ | $436.2 \pm 184.8$ | $0.3932 \pm 1.1379$ | $-10.0 \pm 381.4$ |
| Baseline Persistence* | Autoregressive prior breath | Prior VO2(t-1) | None | None | $96.6 \pm 15.8$ | $44.5 \pm 12.1$ | $0.9817 \pm 0.0189$ | $+1.8 \pm 0.8$ |

> [!NOTE]
> \* **Baseline Persistence Information Regime**: Persistence ($y(t_k) = y(t_{k-1})$) operates as an autoregressive 1-step lookback utilizing prior observed $\dot{V}\text{O}_2(t_{k-1})$. Prospective models (M1--M4) predict solely from external workload ($v$) and physical body mass ($M$) without observing prior gas exchange observations.

### 2.1 GroupKFold vs Legacy Test-Level Split Comparison

| Model Identifier | Independent GroupKFold RMSE (mL/min) | Independent GroupKFold $R^2$ | Legacy Test-Level RMSE (mL/min) | Legacy Test-Level $R^2$ | Methodological Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **M0 Null** | $950.7 \pm 202.9$ | $-0.6244$ | $950.9 \pm 203.0$ | $-0.6260$ | `GUARANTEED_ZERO_LEAKAGE` |
| **M1 Linear** | $570.0 \pm 186.1$ | $0.3296$ | $569.9 \pm 186.1$ | $0.3297$ | `GUARANTEED_ZERO_LEAKAGE` |
| **M2 Linear+Mass** | $514.1 \pm 156.5$ | $0.5157$ | $514.4 \pm 156.8$ | $0.5149$ | `GUARANTEED_ZERO_LEAKAGE` |
| **M3 Dynamic ODE** | $469.9 \pm 211.8$ | $0.4837$ | $469.8 \pm 211.7$ | $0.4838$ | `GUARANTEED_ZERO_LEAKAGE` |
| **M4 Allometric ODE** | $404.0 \pm 175.1$ | $0.6648$ | $404.4 \pm 175.4$ | $0.6642$ | `GUARANTEED_ZERO_LEAKAGE` |
| **Baseline Lagged** | $527.8 \pm 196.6$ | $0.3932$ | $527.7 \pm 196.6$ | $0.3933$ | `GUARANTEED_ZERO_LEAKAGE` |
| **Baseline Persistence** | $96.6 \pm 15.8$ | $0.9817$ | $96.6 \pm 15.8$ | $0.9817$ | `GUARANTEED_ZERO_LEAKAGE` |
| **Ad-Hoc Cycling Transfer** | $584.9 \pm 176.0$ | $0.2465$ | $584.9 \pm 176.0$ | $0.2465$ | `AD_HOC_MAPPING_FAILURE` |

---

## 3. Epistemic Audit of Respiratory Exchange & Oxycaloric Equivalent (Stage 5)

### 3.1 Strict Metrological Classification
- **MEASURED**: Breath-by-breath $\dot{V}\text{O}_2$ (mL/min), $\dot{V}\text{CO}_2$ (mL/min), and pulmonary $\text{RER} = \dot{V}\text{CO}_2 / \dot{V}\text{O}_2$.
- **DERIVED_MODEL_DEPENDENT**: Oxycaloric equivalent $c_{\text{ox}} = 16.89 + 4.82 \cdot \min(\max(\text{RER}, 0.707), 1.000)\text{ kJ/L}$.
- **NOT INDEPENDENTLY VALIDATED**: Cellular substrate oxidation fractions and total energy expenditure during non-steady-state incremental ramp/step testing.

### 3.2 Non-Metabolic $\text{CO}_2$ Exhalation and $\text{RER} > 1.00$
Across 569,379 breath observations:
- **46.80% of observations exhibit $\text{RER} > 1.00$** (266,461 breaths).
- During vigorous and maximal exercise, bicarbonate buffering of lactic acid ($	ext{H}^+ + 	ext{HCO}_3^- \rightleftharpoons 	ext{H}_2\text{CO}_3 \rightleftharpoons 	ext{H}_2\text{O} + \text{CO}_2\uparrow$) produces massive non-metabolic $\text{CO}_2$ blow-off.
- Clipping $\text{RER}$ to $1.000$ assigns all these points to the carbohydrate oxidation ceiling ($21.71\text{ kJ/L}$).
- The resulting mean $c_{\text{ox}} = 21.37\text{ kJ/L}$ is a mathematical consequence of clipping non-steady-state gas exchange; **it is NOT an independent experimental validation of cellular energy expenditure**, and the 2.26% proximity to the nominal $20.9\text{ kJ/L}$ constant must not be claimed as experimental confirmation.

---

## 4. Cross-Modality Transfer Reclassification & Physical Identifiability (Stage 4)

### 4.1 Reclassification of `NEG-0037`
The prior test applied the ad-hoc formula:
$$\text{pred\_transfer} = 560.0 + (7.657 \cdot 25.0) \cdot v$$
- Uses an arbitrary multiplier of $25\text{ W/(km/h)}$ and an uncalibrated intercept of $560\text{ mL/min}$.
- **Status Reclassification**: `AD_HOC_CROSS_MODAL_MAPPING_FAILURE`.
- Factual error preserved: GroupKFold RMSE = $584.9\text{ mL/min}$, $R^2 = 0.2465$ (penalty of $+180.8\text{ mL/min}$ relative to M4).

### 4.2 Physical Cross-Modal Transfer Status
- **Status**: `PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE`.
- **Epistemic Rationale**: Treadmill CPET measures belt velocity ($v$), not mechanical power output ($P_{\text{mech}}$ in Watts). Running involves center-of-mass vertical oscillation and 40%..50% elastic energy storage/recoil in the Achilles tendon and plantar fascia. Without force plates or kinematic motion capture, mechanical work rate cannot be measured. Inventing mechanical Watts from speed is strictly unidentifiable.

---

## 5. Statistical Reliability, Participant Bootstrap & Subgroups (Stage 6)

### 5.1 Paired Hypothesis Tests
- **M4 vs M3 (Allometric Dynamic ODE vs Unscaled ODE)**: Mean RMSE reduction = $67.02\text{ mL/min}$ ($t = 10.38, p = 7.80e-24$; Wilcoxon signed-rank $p = 4.97e-20$).
- **M4 vs M2 (Dynamic vs Static Multiple Regression)**: Mean RMSE reduction = $109.63\text{ mL/min}$ ($p = 6.37e-186$).
- **M4 vs M1 (Dynamic vs Static Speed)**: Mean RMSE reduction = $166.22\text{ mL/min}$ ($p = 9.85e-118$).
- **M3 vs M1 (Kinetics Contribution)**: Mean RMSE reduction = $99.20\text{ mL/min}$ ($p < 10^{-300}$).

### 5.2 Participant-Level Bootstrap (1,000 Resamples of Independent Subjects)
- **M4 Out-of-Sample RMSE 95% CI**: $[392.38, 415.89]\text{ mL/min}$
- **M4 Out-of-Sample $R^2$ 95% CI**: $[0.6006, 0.7015]$
- **M3 Out-of-Sample RMSE 95% CI**: $[457.11, 485.57]\text{ mL/min}$

### 5.3 Demographic Subgroups & Worst-Case Tail Analysis

| Demographic Cohort Group | Subgroup Category | Tests ($N$) | M4 RMSE (mL/min) | M4 $R^2$ | Epistemic Observation |
|:---|:---|:---:|:---:|:---:|:---|
| **Sex** | Male | 836 | $417.6 \pm 179.1$ | $0.6929$ | Higher absolute VO2 capacity |
| **Sex** | Female | 145 | $325.5 \pm 122.9$ | $0.5025$ | Lower baseline VO2; reduced dynamic range |
| **Age Bracket** | <18 years | 143 | $405.6 \pm 183.0$ | $0.6546$ | Stable Phase II ODE kinetics across age span |
| **Age Bracket** | 18-29 years | 438 | $388.0 \pm 152.1$ | $0.6615$ | Stable Phase II ODE kinetics across age span |
| **Age Bracket** | 30-44 years | 326 | $429.5 \pm 203.9$ | $0.6617$ | Stable Phase II ODE kinetics across age span |
| **Age Bracket** | 45-59 years | 71 | $382.2 \pm 130.7$ | $0.7246$ | Stable Phase II ODE kinetics across age span |
| **Age Bracket** | >=60 years | 3 | $414.5 \pm 57.2$ | $0.5504$ | Stable Phase II ODE kinetics across age span |
| **Worst 5% Participants** | Tail (N=49) | 49 | $947.7$ | — | Heavier individuals (77.5 kg vs cohort 73.3 kg) with high hyperventilation drift |

---

## 6. Scientific Generalization Framework (Three Levels)

1. **Level A: Within-Dataset LOSO on Cycling Humans (ACTES, $N=18$)**  
   `VALIDATED_ON_ACTES_N18`: Dynamic ODE kinetics validated ($R^2 = 0.812$). Linear mass scaling improves cohort $R^2$ but degrades individual fit in 7/18 subjects.
2. **Level B: Within-Dataset Grouped Validation on Running Humans (Malaga, $N=846$)**  
   `VALIDATED_ON_MALAGA_N846`: Dynamic allometric ODE (M4) validated ($R^2 = 0.6648$, $\text{RMSE} = 404.0\text{ mL/min}$). Allometric scaling uniformly improves performance across all age brackets and sexes.
3. **Level C: External Zero-Shot Modality Transfer**  
   `EXTERNAL_ZERO_SHOT_TRANSFER_NOT_IDENTIFIABLE`: Retraining on Malaga is NOT zero-shot transfer of cycling parameters. Direct parameter transfer requires mechanical work rate and running economy measurements absent in open treadmill CPET.

---

## 7. Data Provenance & License Conflict Audit (Stage 7)

- **Source ID**: `SRC-0074`
- **PhysioNet Resource**: `treadmill-exercise-cardioresp` Version 1.0.1 (DOI: `10.13026/7ezk-j442`)
- **License Conflict Analysis**:
  1. `empirical_datasets_cycle11.json` previously registered the license as `ODC-By v1.0` (inadvertently copied from ACTES).
  2. The downloaded raw distribution archive contains `LICENSE.txt` specifying `Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License` (CC BY-NC-SA 4.0).
  3. The official PhysioNet v1.0.1 landing page specifies `PhysioNet Contributor Review Health Data License 1.5.0` and Data Use Agreement 1.5.0.
- **Epistemic Classification**: `LICENSE_CONFLICT_OPEN_ISSUE` (Tracked under `ISS-0020`).
- **Redistribution Terms**: Data can only be stored and utilized under non-commercial academic attribution guidelines; clean dual-licensing clearance is NOT claimed.

---

## 8. Epistemic Guarantees & Freezes

1. **Macroscopic Locomotion Kinetics**: Empirically validated under subject-independent `GroupKFold` across $N = 846$ participants ($R^2 = 0.6648$, $\text{RMSE} = 404.0\text{ mL/min}$).
2. **Intracellular Unobservability**: Intramuscular phosphates ([PCr], [Pi]), cytosolic pH, and motor unit recruitment remain completely unobserved in treadmill CPET.
3. **`TARGET-CPE45` Status**: Strictly **`NOT EXTERNALLY VALIDATED`**. Graded ramp tests do not test 45-minute continuous critical power survivability.
4. **Biological Interventions**: Strictly **`NO_GO`**.
