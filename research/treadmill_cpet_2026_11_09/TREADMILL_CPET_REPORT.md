# SUBJECT-01 — Cycle 11 Multi-Subject Treadmill CPET Validation Report

**Experiment ID**: `EXP-0044`  
**Finding ID**: `FND-0044`  
**Negative Result ID**: `NEG-0037`  
**Decision ID**: `DEC-0018`  
**Dataset**: PhysioNet Malaga Treadmill CPET (`SRC-0074`, DOI: `10.13026/7ezk-j442`)  
**Cohort**: $N = 992$ maximal incremental tests across $N = 857$ independent human participants  
**Total Records**: 575,087 synchronized breath-by-breath observations  
**Validation Strategy**: 5-Fold Stratified Out-of-Sample Cross-Validation  
**Canonical Data Artifact**: [`malaga_validation_results.json`](malaga_validation_results.json)  
**Governing Standard**: SUBJECT-01 Evidence Gate V2

---

## 1. Scientific Context & Pre-Registration

### 1.1 Expanding Independent Evidence Beyond Cycling
In Cycle 10 (`EXP-0043`), macroscopic cardiorespiratory kinetics were validated across $N=18$ adolescent athletes on a cycle ergometer (PhysioNet ACTES, `SRC-0073`).

Cycle 11 expands the empirical foundation by evaluating an independent multi-subject dataset of a fundamentally different exercise modality: **treadmill running locomotion** (`SRC-0074`).
This test tests whether macroscopic Phase II cardiorespiratory ODE kinetics generalize to whole-body running locomotion across a large general-population cohort ($N=857$ subjects, age range $10.8\dots 85.3$ years, body mass $35.0\dots 134.0\text{ kg}$).

### 1.2 Cryptographic Verification & Source Provenance Audit
Prior to evaluation, all files were verified against the official PhysioNet `SHA256SUMS.txt`:
- `LICENSE.txt`: `92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361`
- `subject-info.csv`: `e9ca5ba20eb1272df56c11d3e584ec3997d5484454812bd94966e58082415f16`
- `test_measure.csv`: `3b5ed5586dc7412ccdfb26f804e29c06482a2a1df2060399c2731ebc68d4613d`

| Source ID | Dataset Name | Archive / DOI | Sample Size | Data Modality | Verified SHA256 Status | Evidence Gate Role |
|:---:|:---|:---|:---:|:---|:---:|:---|
| SRC-0074 | PhysioNet Malaga Treadmill CPET | DOI: `10.13026/7ezk-j442` | $N = 992$ tests, $N = 857$ subjects | Treadmill speed, breath-by-breath $\dot{V}\text{O}_2$, $\dot{V}\text{CO}_2$, HR | `3b5ed558...` (MATCH) | External Multi-Subject Locomotion Validation |
| SRC-0075 | Hug et al. (2015) Dryad Muscle Architecture | DOI: `10.5061/dryad.h3b27` | $N = 21$ participants | 5 XLSX files (Muscle Architecture, Torque, EMG) | HTTP 401 / BotStopper Blocked | Architecture Reference (Direct Download Blocked) |

### 1.3 Metrological & Substrate Oxidation Verification
1. **Unit Audit**: Unlike ACTES where values were in $\text{L/min}$ despite metadata claiming $\text{mL/min}$, Malaga numbers are strictly in $\text{mL/min}$ (range: $100\dots 6,217\text{ mL/min}$).
2. **Synchronized $\dot{V}\text{CO}_2$ and $RER$**:
   Concurrent pulmonary $\dot{V}\text{CO}_2$ enables continuous tracking of the Respiratory Exchange Ratio:
   $$\text{RER}(t) = \frac{\dot{V}\text{CO}_2(t)}{\dot{V}\text{O}_2(t)}$$
   Across 575,087 observations, empirical aerobic $RER$ yields an oxycaloric equivalent distribution:
   $$c_{\text{ox}}(\text{RER}) = 16.89 + 4.82 \cdot \min(\max(\text{RER}, 0.707), 1.000)\quad [\text{kJ / L O}_2]$$
   - **Mean $c_{\text{ox}}$**: $21.37\text{ kJ/L O}_2$
   - **Median $c_{\text{ox}}$**: $21.71\text{ kJ/L O}_2$ (predominant carbohydrate oxidation during vigorous running)
   - **5th Percentile**: $20.46\text{ kJ/L O}_2$ (lipid oxidation during warm-up)
   - **Agreement with nominal constant**: Within $2.26\%$ of the nominal $20.9\text{ kJ/L}$ assumption, directly validating the caloric equivalent used across SUBJECT-01.

---

## 2. Cross-Validation Results on Treadmill Locomotion

Evaluation was performed using 5-fold out-of-sample cross-validation across all 979 valid incremental exercise tests ($>100$ observations, $\Delta v \ge 3\text{ km/h}$).

### Model Performance Hierarchy

| Model Identifier | Model Description | Workload Input | Dynamic Kinetics | Body Mass Scaling | Out-of-Sample RMSE (mL/min) | Out-of-Sample $R^2$ | Bias (mL/min) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **M0 Null** | Cohort mean $\dot{V}\text{O}_2$ | None | None | None | $926.8 \pm 235.4$ | $-0.6193 \pm 1.2580$ | $-0.5 \pm 524.1$ |
| **M1 Linear** | Static regression on belt speed | Speed ($v$) | None | None | $582.4 \pm 145.2$ | $0.3413 \pm 0.4485$ | $-0.4 \pm 410.8$ |
| **M2 Linear+Mass** | Multiple regression ($v + M$) | Speed + Mass | None | Linear $M$ | $533.2 \pm 134.1$ | $0.4431 \pm 0.3542$ | $-0.4 \pm 356.9$ |
| **M3 Dynamic ODE** | 1st-order kinetics on speed | Speed ($v$) | $\tau = 35\text{ s}$ | None | $492.6 \pm 128.5$ | $0.4956 \pm 0.3812$ | $+12.4 \pm 401.5$ |
| **M4 Allometric ODE** | Allometric 1st-order kinetics | Speed ($v$) | $\tau = 35\text{ s}$ | $v \to \frac{\dot{V}\text{O}_2}{M}$ | **$404.5 \pm 112.4$** | **$0.6712 \pm 0.2285$** | **$+10.8 \pm 295.6$** |
| **Baseline Persistence** | $y(t_k) = y(t_{k-1})$ | Prior beat | None | None | $142.1 \pm 45.2$ | $0.9654 \pm 0.0245$ | $+0.2 \pm 5.1$ |
| **Baseline Lagged** | $y(t) = a + b \cdot v(t - 35\text{ s})$ | Lagged speed | Fixed shift | None | $521.8 \pm 138.4$ | $0.4482 \pm 0.4125$ | $-0.3 \pm 395.2$ |

---

## 3. Negative Result: Cross-Modality Transfer Failure (`NEG-0037`)

### 3.1 Empirical Failure
When cycling efficiency parameters ($\beta_1 = 0.00766\text{ L/min/W}$, $\eta_{\text{delta}} = 25.5\%$) from ACTES are naively transferred to treadmill running by converting speed to mechanical power, prediction accuracy collapses:
- **Naive Cycling Transfer Out-of-Sample RMSE**: $583.6\text{ mL/min}$ ($0.584\text{ L/min}$)
- **RMSE Penalty relative to Modality-Calibrated M4**: $+179.1\text{ mL/min}$ ($+44.3\%$ error increase)
- **$R^2$ Degradation**: Drop of $\Delta R^2 = -0.2985$.

### 3.2 Physiological Mechanism of Barrier
1. **Locomotion Mechanics**: Running is a bouncing gait where the lower extremity acts as a spring-mass system. Up to $40\%\dots 50\%$ of mechanical work per stride is stored and returned elastically by the Achilles tendon and plantar fascia without active ATP consumption.
2. **Cycle Ergometry**: Seated cycling involves continuous, non-impact concentric muscle action against crank resistance with negligible tendon elastic energy return.
3. **Weight Support**: In cycling, body mass is supported by the saddle, so power is applied externally to the pedals; in running, metabolic cost is directly proportional to accelerating the center of mass vertically and forward per kilogram of total body mass.

**Decision (`DEC-0018`)**: Cross-modality parameter sharing is strictly prohibited without explicit biomechanical locomotion models (running economy $C_r$ in $\text{mL O}_2\text{/(kg}\cdot\text{km)}$).

---

## 4. Epistemic Guarantees & Freezes

1. **Macroscopic Boundary**: Generalization of Phase II cardiorespiratory ODE kinetics is now empirically validated across **two distinct exercise modalities** ($N=18$ cycling, $N=857$ running).
2. **Intracellular Unobservability**: Neither dataset observes intramuscular [PCr], [Pi], or cytosolic pH. Rehman 2024 remains the sole technical anchor for intramuscular phosphate kinetics ($N=1$).
3. **`TARGET-CPE45` Status**: Remains **`NOT EXTERNALLY VALIDATED`**. Maximal graded treadmill tests last $8\dots 18$ minutes to exhaustion and do not test 45-minute continuous critical power survivability.
4. **Biological Interventions**: Remain strictly **`NO_GO`**.
