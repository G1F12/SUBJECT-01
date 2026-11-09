# SUBJECT-01 — Scientific Validation, Corrigendum & Freeze on Rehman et al. 2024 Real Data
**Document ID**: `VAL-REHMAN-2024-REAL-01-REV2`  
**Date**: 2026-11-09  
**Repository**: `G1F12/SUBJECT-01`  
**Cycle**: Cycle 9 (Evidence Gate V2 & Real Data Freeze — Corrigendum Revision)  
**Primary Source**: Rehman et al. 2024, *Data in Brief* 57:111114 (PMC11617988; Dryad DOI: `10.5061/dryad.08kprr59v`)  
**Raw Source File**: `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18,136 B; SHA256: `ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`)  
**Derived Extraction Artifact**: `rehman2024_extracted_timeseries.json` (SHA256: `af6a396b006a6cb791844742085701c6782b4eb706a8f768b1bd87dfa7e8de5b`)  
**Validation Artifact**: `rehman2024_validation_results.json`

---

## 1. Executive Summary & Corrigendum Log

Following primary raw data extraction from Dryad (`2024_829_Ergometer_Dryad_Raw_V3.xlsx`), this report provides the reconciled, fully audit-verified scientific validation and freeze of the Rehman et al. 2024 $^{31}\text{P}$-MRS benchmark. All numerical metrics are strictly reconciled with `rehman2024_validation_results.json` and verified by automated consistency tests.

### Corrigendum Log (Superseded Draft vs Verified Canonical Values):
1. **Raw PCr Amplitudes at 90s Stop**:
   - *Superseded Draft*: Trial 1 $= 1908$, Trial 2 $= 2027$, Trial 3 $= 1961$.
   - *Verified Canonical*: **Trial 1 $= 1920$**, **Trial 2 $= 1291$**, **Trial 3 $= 1277$**.
2. **Raw PCr Amplitudes at Observed Nadir**:
   - *Superseded Draft*: Trial 1 $= 1670$, Trial 2 $= 1916$, Trial 3 $= 1860$.
   - *Verified Canonical*: **Trial 1 $= 1670$**, **Trial 2 $= 1245$**, **Trial 3 $= 1231$**.
3. **In-Sample Fit Metrics**:
   - *M0 (Null Baseline Constant)*: Superseded reported RMSE $185.0 / 82.7 / 145.4$ with $R^2 = 0.000$. Verified canonical: **T1 RMSE $= 230.88$ ($R^2 = -0.553$)**, **T2 RMSE $= 120.21$ ($R^2 = -1.130$)**, **T3 RMSE $= 141.69$ ($R^2 = -0.962$)**. M0 $R^2$ is negative because predicting resting baseline yields higher residual variance than the mean of the recovery slice.
   - *M1 (Empirical 3-Parameter Monoexponential)*: Verified canonical **T1 RMSE $= 26.05$ ($R^2 = 0.9802$)**, **T2 RMSE $= 15.73$ ($R^2 = 0.9635$)**, **T3 RMSE $= 14.70$ ($R^2 = 0.9789$)**.
   - *M2 (Constrained Monoexponential Baseline)*: Reclassified from "physiological ODE" to `CONSTRAINED_MONOEXPONENTIAL_BASELINE`. Verified canonical: **T1 RMSE $= 31.72$ ($R^2 = 0.9707$)**, **T2 RMSE $= 37.67$ ($R^2 = 0.7909$)**, **T3 RMSE $= 32.80$ ($R^2 = 0.8948$)**.
4. **Intracellular pH Statement Retraction**:
   - *Superseded Claim*: "pH >= 6.86 throughout exercise and recovery".
   - *Formal Retraction*: The claim `pH >= 6.86 throughout` is formally **RETRACTED as superseded**. Calculated minimum pH reaches **$6.7932$** in Trial 1 ($6.8840$ in Trial 2, $6.8911$ in Trial 3).
5. **Model M2 Classification & Full Physiological ODE (M3)**:
   - M2 is strictly reclassified as `CONSTRAINED_MONOEXPONENTIAL_BASELINE` ($d\text{PCr}/dt = k \cdot (\text{PCr}_{\text{rest}} - \text{PCr})$). It does not validate energy balance, $O_2$ transport, active muscle volume, or motor control.
   - Full physiological ODE model is documented as `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS` because pedal power in Watts, muscle PCSA, cardiac output, and whole-body $\dot{V}\text{O}_2$ are absent in Rehman 2024.
6. **Transfer Distinction (Scenario A vs Scenario B)**:
   - *Scenario A* (`CONDITIONAL_TRAJECTORY_RECONSTRUCTION`): Evaluated with test nadir and baseline known. Achieves mean transfer $R^2 = 0.8566$ (M2) vs $0.8268$ (M1).
   - *Scenario B* (`PROSPECTIVE_PREDICTION`): Forward forecasting from $t = 90\text{ s}$ prior to observing the true nadir is classified as `PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS`.
7. **Protocol Timing Synchronization**:
   - Classified as `INFERRED_TIMING_ASSUMPTION` because exercise start/stop were auditory cues without synchronous hardware TTL event markers in the MRS stream. Retracted terms "ischemic" or "hyperemic" without independent perfusion measurements.

---

## 2. Stage 1 — Protocol Timing Reconstruction & Mismatch Analysis

Data were acquired with $TR = 6.0\text{ s}$ ($0.1\text{ min}$ per spectrum) over 74 usable spectra per trial.

### Reconciled Protocol Landmarks:
- **Baseline Control Period**: Spectra 2 through 8 ($t = 12.0\text{ s}$ to $48.0\text{ s}$).
  - Trial 1: $\text{PCr}_{\text{rest}} = 2481.43 \pm 78.41$.
  - Trial 2: $\text{PCr}_{\text{rest}} = 1678.86 \pm 41.51$.
  - Trial 3: $\text{PCr}_{\text{rest}} = 1675.57 \pm 38.65$.
- **Nominal Exercise Interval**: $t = 48.0\text{ s}$ to $90.0\text{ s}$ ($42\text{ s}$ dynamic knee kicking at 1 Hz).
  - Status: `INFERRED_TIMING_ASSUMPTION` (auditory cue; no TTL pulse in raw MRS).
- **Nominal Exercise Stop**: $t = 90.0\text{ s}$ (Spectrum 15).
- **Actual Biochemical Nadir**: Observed minimum PCr amplitude in spectral series.
  - Trial 1: $t = 144.0\text{ s}$ (Spectrum 24; $\text{PCr} = 1670$, depletion $= 32.70\%$, published $= 31.6\%$, lag $= +54.0\text{ s}$).
  - Trial 2: $t = 108.0\text{ s}$ (Spectrum 18; $\text{PCr} = 1245$, depletion $= 25.85\%$, published $= 25.2\%$, lag $= +18.0\text{ s}$).
  - Trial 3: $t = 108.0\text{ s}$ (Spectrum 18; $\text{PCr} = 1231$, depletion $= 26.53\%$, published $= 24.8\%$, lag $= +18.0\text{ s}$).

### Exact Reconciled Timing Table:

| Trial ID | Baseline PCr Mean | PCr at 90s Stop | Drop at 90s (%) | Actual Nadir Time | Nadir PCr | Drop at Nadir (%) | Published Drop (%) | Post-Stop Lag (s) | Timing Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Trial 1** | $2481.43 \pm 78.41$ | **$1920$** | $22.62\%$ | **$144.0\text{ s}$** (Spec 24) | **$1670$** | **$32.70\%$** | $31.6\%$ | $+54.0\text{ s}$ | `EXTENDED_DEPLETION_PHASE` |
| **Trial 2** | $1678.86 \pm 41.51$ | **$1291$** | $23.10\%$ | **$108.0\text{ s}$** (Spec 18) | **$1245$** | **$25.85\%$** | $25.2\%$ | $+18.0\text{ s}$ | `CONGRUENT_WITH_TABLE1` |
| **Trial 3** | $1675.57 \pm 38.65$ | **$1277$** | $23.79\%$ | **$108.0\text{ s}$** (Spec 18) | **$1231$** | **$26.53\%$** | $24.8\%$ | $+18.0\text{ s}$ | `CONGRUENT_WITH_TABLE1` |

### Timing Audit Rulings:
1. `timing_synchronization_status`: `INFERRED_TIMING_ASSUMPTION`.
2. `nadir_status`: `OBSERVED_SPECTRAL_MINIMUM_DISTINCT_FROM_MECHANICAL_STOP`.
3. `perfusion_disclaimer`: The post-90s decline represents an empirical lag in recovery onset. Speculating on "ischemic" or "hyperemic" causes is prohibited because neither Doppler blood flow nor arterial occlusion was recorded.
4. `governing_status`: `PROTOCOL_TIMING_DISCREPANCY_IDENTIFIED`.

---

## 3. Stage 2 — Recovery Kinetics Sensitivity & Systematic Uncertainty

To decouple systematic phase-selection uncertainty from statistical non-linear regression error, recovery curves were evaluated under shifts $\Delta t \in \{-18, -12, -6, 0, +6, +12, +18\}\text{ s}$ relative to the biochemical nadir.

### Exact Reconciled Sensitivity Evaluations:

#### Trial 1 (Nadir $= 144.0\text{ s}$, Published $k = 1.43\text{ min}^{-1}$):
- $\Delta t = -18\text{ s}$ ($126.0\text{ s}$): $k = 1.041\text{ min}^{-1}$, $\tau = 57.6\text{ s}$, $R^2 = 0.9664$, $\text{RMSE} = 42.25$.
- $\Delta t = -12\text{ s}$ ($132.0\text{ s}$): $k = 1.163\text{ min}^{-1}$, $\tau = 51.6\text{ s}$, $R^2 = 0.9751$, $\text{RMSE} = 34.43$.
- $\Delta t = -6\text{ s}$ ($138.0\text{ s}$): $k = 1.280\text{ min}^{-1}$, $\tau = 46.9\text{ s}$, $R^2 = 0.9792$, $\text{RMSE} = 29.23$.
- **$\Delta t = 0\text{ s}$ ($144.0\text{ s}$)**: **$k = 1.393\text{ min}^{-1}$**, $\tau = 43.1\text{ s}$, **$R^2 = 0.9802$**, $\text{RMSE} = 26.05$, $\text{CI}_{95} = \pm 0.129\text{ min}^{-1}$ (Diff vs Pub: $-2.58\%$).
- $\Delta t = +6\text{ s}$ ($150.0\text{ s}$): $k = 1.355\text{ min}^{-1}$, $\tau = 44.3\text{ s}$, $R^2 = 0.9739$, $\text{RMSE} = 26.02$.
- $\Delta t = +12\text{ s}$ ($156.0\text{ s}$): $k = 1.394\text{ min}^{-1}$, $\tau = 43.0\text{ s}$, $R^2 = 0.9670$, $\text{RMSE} = 26.06$.
- $\Delta t = +18\text{ s}$ ($162.0\text{ s}$): $k = 1.306\text{ min}^{-1}$, $\tau = 45.9\text{ s}$, $R^2 = 0.9574$, $\text{RMSE} = 25.44$.
- **Uncertainty Breakdown**: Statistical $\text{CI}_{95} = \pm 0.129\text{ min}^{-1}$; Systematic Phase Uncertainty $\Delta k_{\text{sys}} = \pm 0.044\text{ min}^{-1}$ (Ratio $= 0.34$).

#### Trial 2 (Nadir $= 108.0\text{ s}$, Published $k = 1.62\text{ min}^{-1}$):
- $\Delta t = -18\text{ s}$ ($90.0\text{ s}$, Nominal Stop): $k = 1.115\text{ min}^{-1}$, $\tau = 53.8\text{ s}$, $R^2 = 0.9394$, $\text{RMSE} = 25.09$.
- $\Delta t = -12\text{ s}$ ($96.0\text{ s}$): $k = 1.233\text{ min}^{-1}$, $\tau = 48.7\text{ s}$, $R^2 = 0.9408$, $\text{RMSE} = 23.29$.
- $\Delta t = -6\text{ s}$ ($102.0\text{ s}$): $k = 1.493\text{ min}^{-1}$, $\tau = 40.2\text{ s}$, $R^2 = 0.9635$, $\text{RMSE} = 17.40$.
- **$\Delta t = 0\text{ s}$ ($108.0\text{ s}$)**: **$k = 1.686\text{ min}^{-1}$**, $\tau = 35.6\text{ s}$, **$R^2 = 0.9635$**, $\text{RMSE} = 15.73$, $\text{CI}_{95} = \pm 0.187\text{ min}^{-1}$ (Diff vs Pub: $+4.09\%$).
- $\Delta t = +6\text{ s}$ ($114.0\text{ s}$): $k = 1.574\text{ min}^{-1}$, $\tau = 38.1\text{ s}$, $R^2 = 0.9497$, $\text{RMSE} = 15.48$.
- $\Delta t = +12\text{ s}$ ($120.0\text{ s}$): $k = 1.438\text{ min}^{-1}$, $\tau = 41.7\text{ s}$, $R^2 = 0.9324$, $\text{RMSE} = 15.13$.
- $\Delta t = +18\text{ s}$ ($126.0\text{ s}$): $k = 1.342\text{ min}^{-1}$, $\tau = 44.7\text{ s}$, $R^2 = 0.9101$, $\text{RMSE} = 15.05$.
- **Uncertainty Breakdown**: Statistical $\text{CI}_{95} = \pm 0.187\text{ min}^{-1}$; Systematic Phase Uncertainty $\Delta k_{\text{sys}} = \pm 0.172\text{ min}^{-1}$ (Ratio $= 0.92$).

#### Trial 3 (Nadir $= 108.0\text{ s}$, Published $k = 1.53\text{ min}^{-1}$):
- $\Delta t = -18\text{ s}$ ($90.0\text{ s}$, Nominal Stop): $k = 1.023\text{ min}^{-1}$, $\tau = 58.6\text{ s}$, $R^2 = 0.9398$, $\text{RMSE} = 29.53$.
- $\Delta t = -12\text{ s}$ ($96.0\text{ s}$): $k = 1.165\text{ min}^{-1}$, $\tau = 51.5\text{ s}$, $R^2 = 0.9573$, $\text{RMSE} = 23.89$.
- $\Delta t = -6\text{ s}$ ($102.0\text{ s}$): $k = 1.323\text{ min}^{-1}$, $\tau = 45.4\text{ s}$, $R^2 = 0.9712$, $\text{RMSE} = 18.55$.
- **$\Delta t = 0\text{ s}$ ($108.0\text{ s}$)**: **$k = 1.480\text{ min}^{-1}$**, $\tau = 40.5\text{ s}$, **$R^2 = 0.9789$**, $\text{RMSE} = 14.70$, $\text{CI}_{95} = \pm 0.137\text{ min}^{-1}$ (Diff vs Pub: $-3.24\%$).
- $\Delta t = +6\text{ s}$ ($114.0\text{ s}$): $k = 1.610\text{ min}^{-1}$, $\tau = 37.3\text{ s}$, $R^2 = 0.9797$, $\text{RMSE} = 12.95$.
- $\Delta t = +12\text{ s}$ ($120.0\text{ s}$): $k = 1.714\text{ min}^{-1}$, $\tau = 35.0\text{ s}$, $R^2 = 0.9764$, $\text{RMSE} = 12.30$.
- $\Delta t = +18\text{ s}$ ($126.0\text{ s}$): $k = 1.663\text{ min}^{-1}$, $\tau = 36.1\text{ s}$, $R^2 = 0.9668$, $\text{RMSE} = 12.29$.
- **Uncertainty Breakdown**: Statistical $\text{CI}_{95} = \pm 0.137\text{ min}^{-1}$; Systematic Phase Uncertainty $\Delta k_{\text{sys}} = \pm 0.117\text{ min}^{-1}$ (Ratio $= 0.85$).

Status: `PHASE_SELECTION_SENSITIVITY_QUANTIFIED`.

---

## 4. Stage 3 — Chemical Shift Referencing & pH Calibration Corrigendum

### Henderson-Hasselbalch Formulation:
$$\text{pH} = 6.75 + \log_{10}\left(\frac{\delta_o - 3.290}{5.805 - \delta_o}\right), \quad \delta_o = \delta_{\text{Pi}} - \delta_{\text{PCr}}$$

### Reconciled Metrics & Formal Retraction:
- **Systematic Offset**: Mean offset $\Delta\text{pH} = -0.0548 \pm 0.0098$ pH units below published Table 1.
- **Formal Retraction of Invariant**: The claim `pH >= 6.86 throughout` is formally **RETRACTED as superseded**.
- **Actual Computed pH Ranges**:
  - **Trial 1**: $\min = \mathbf{6.7932}$, $\max = 6.9778$, mean $= 6.9189$.
  - **Trial 2**: $\min = \mathbf{6.8840}$, $\max = 7.0077$, mean $= 6.9497$.
  - **Trial 3**: $\min = \mathbf{6.8911}$, $\max = 7.0228$, mean $= 6.9610$.
  - **Global Range**: $6.7932$ to $7.0228$.

### Scientific Rulings on pH:
1. `status`: `PH_CALIBRATION_PARTIAL`.
2. No arbitrary $+0.055$ fudge factor is applied.
3. Because minimum pH in Trial 1 reaches $6.7932$, asserting "purely oxidative kinetics with zero proton inhibition" is scientifically unjustified without independent blood lactate and acid-base measurements.

---

## 5. Stage 4 — Model Reclassification & Within-Subject Transfer

### Model Hierarchy:
1. **Model M0 (Null Baseline Constant)**:
   $$\hat{y}(t) = \text{PCr}_{\text{rest}}$$
2. **Model M1 (Empirical 3-Parameter Monoexponential)**:
   $$\hat{y}(t) = \text{PCr}_{\text{nadir}} + \Delta\text{PCr} \cdot (1 - e^{-k \cdot t})$$
3. **Model M2 (`CONSTRAINED_MONOEXPONENTIAL_BASELINE`)**:
   $$\frac{d\text{PCr}}{dt} = k \cdot (\text{PCr}_{\text{rest}} - \text{PCr}) \implies \hat{y}(t) = \text{PCr}_{\text{nadir}} + (\text{PCr}_{\text{rest}} - \text{PCr}_{\text{nadir}}) \cdot (1 - e^{-k \cdot t})$$
   *Classification*: Constrained monoexponential baseline with resting asymptote. It is NOT the full integrated SUBJECT-01 physiology.
4. **Model M3 (Full SUBJECT-01 Physiological ODE)**:
   *Classification*: `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS`. Mechanical pedal power (W), pedal torque, active quadriceps PCSA, cardiac output, and whole-body $\dot{V}\text{O}_2$ were not measured in Rehman 2024.

### In-Sample Fit Results (Strictly Labeled: `IN_SAMPLE_FIT_NOT_VALIDATION`):

| Trial ID | M0 RMSE | M0 MAE | M0 $R^2$ | M1 RMSE | M1 MAE | M1 $R^2$ | M1 $k$ ($\text{min}^{-1}$) | M2 RMSE | M2 MAE | M2 $R^2$ | M2 $k$ ($\text{min}^{-1}$) | M2 $\tau$ (s) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Trial 1** | **$230.88$** | $139.20$ | **$-0.553$** | **$26.05$** | $21.34$ | **$0.9802$** | $1.393$ | **$31.72$** | $25.70$ | **$0.9707$** | $1.298$ | $46.2$ |
| **Trial 2** | **$120.21$** | $87.55$ | **$-1.130$** | **$15.73$** | $12.63$ | **$0.9635$** | $1.686$ | **$37.67$** | $33.21$ | **$0.7909$** | $1.147$ | $52.3$ |
| **Trial 3** | **$141.69$** | $99.23$ | **$-0.962$** | **$14.70$** | $11.50$ | **$0.9789$** | $1.480$ | **$32.80$** | $28.70$ | **$0.8948$** | $0.970$ | $61.9$ |

*Note on M0 $R^2$*: $R^2 < 0.0$ because predicting $\text{PCr}_{\text{rest}}$ on recovery data yields larger squared error than predicting the slice mean $\bar{y}$.

---

### Within-Subject Cross-Trial Transfer:

#### Scenario A: `CONDITIONAL_TRAJECTORY_RECONSTRUCTION`
(Evaluated retrospectively with test nadir $\text{PCr}_{\text{min},j}$ and baseline $\text{PCr}_{\text{rest},j}$ known):

| Train Trial | Test Trial | Calibrated $k$ ($\text{min}^{-1}$) | M1 Trans RMSE | M1 Trans MAE | M1 Trans $R^2$ | M2 Trans RMSE | M2 Trans MAE | M2 Trans $R^2$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Trial 1** | **Trial 2** | $1.298$ | $39.75$ | $34.99$ | $0.7671$ | **$38.56$** | $33.70$ | **$0.7809$** |
| **Trial 1** | **Trial 3** | $1.298$ | $43.09$ | $40.31$ | $0.8185$ | **$39.97$** | $36.38$ | **$0.8439$** |
| **Trial 2** | **Trial 1** | $1.147$ | $48.20$ | $39.86$ | $0.9323$ | **$36.93$** | $28.58$ | **$0.9603$** |
| **Trial 2** | **Trial 3** | $1.147$ | $52.43$ | $49.84$ | $0.7313$ | **$35.47$** | $30.13$ | **$0.8770$** |
| **Trial 3** | **Trial 1** | $0.970$ | $36.91$ | $29.97$ | $0.9603$ | **$56.28$** | $42.43$ | **$0.9077$** |
| **Trial 3** | **Trial 2** | $0.970$ | $41.08$ | $36.54$ | $0.7512$ | **$39.54$** | $34.99$ | **$0.7696$** |
| **Mean** | — | — | **$43.58$** | $38.59$ | **$0.8268$** | **$41.13$** | $34.37$ | **$0.8566$** |

*Scenario A Verdict*: Confirms technical test-retest reproducibility of the recovery rate parameter. M2 constrained baseline outperforms M1 (mean $R^2 = 0.8566$ vs $0.8268$).

#### Scenario B: `PROSPECTIVE_PREDICTION`
- **Status**: `PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS`.
- **Forecast Origin**: $t = 90.0\text{ s}$ (nominal stop of mechanical exercise).
- **Blocking Reason**: At $t = 90.0\text{ s}$, PCr continues declining for an unobserved lag duration ($+18\text{ s}$ to $+54\text{ s}$) to an unobserved nadir depth. Forward forecasting prior to observing nadir without pedal power or blood flow data is mathematically undefined and cannot be claimed without leakage of future test points.

#### Prohibition of Cross-Subject LOSO:
Calling cross-subject leave-one-subject-out routines on $N=1$ cohort strictly raises `LosoProhibitedError`.

---

## 6. Stage 5 — Identifiability Matrix & Epistemic Freeze

```
                             RECONCILED IDENTIFIABILITY MATRIX
   ┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
   │         IDENTIFIABLE PARAMETERS              │           STRICLY UNIDENTIFIABLE             │
   ├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
   │ • tau_PCr_rec: 39.72 ± 3.81 s (CV = 9.9%)    │ • [PCr]_rest (mM): arbitrary MR gain         │
   │ • k_rec: 1.520 ± 0.151 min^-1                │ • V_active (L): single-coil scale symmetry   │
   │ • PCr Depletion Fraction: 28.36 ± 3.77%      │ • J_ATP (mol/s): volume/mM coupled           │
   │ • Conditional Reconstruction R²: 0.8566      │ • eta_loc: pedal torque unrecorded           │
   │ • Intracellular pH range: 6.7932 to 7.0228   │ • Q_max: submaximal linear regime (10% MVC)  │
   │                                              │ • TARGET-CPE45: NOT EXTERNALLY VALIDATED     │
   │                                              │ • Biological Interventions: NO_GO            │
   └──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 7. Stage 6 — Multi-Subject Dataset Acquisition Roadmap

Minimal external data required to test full model M3 on another human cohort ($N \ge 8$):
1. **Continuous Ergometer Power $P(t)$ (W)**: Synchronously recorded pedal torque and cadence.
2. **3D Dixon MRI Muscle Volumetry**: Individual quadriceps volume $V_{\text{anat}}$ (mL) and subcutaneous fat thickness.
3. **Calibrated $^{31}\text{P}$-MRS**: Water-referenced or phantom-calibrated absolute $[\text{PCr}]$ in mM.
4. **Breath-by-Breath CPET**: Pulmonary $\dot{V}\text{O}_2, \dot{V}\text{CO}_2$ to anchor systemic energy balance.

---

## 8. Summary of Reconciled Registries & Verification

- **`EXP-0042`**: Updated with exact canonical amplitudes ($1920/1670, 1291/1245, 1277/1231$), exact RMSEs ($230.88, 120.21, 141.69$ for M0; $26.05, 15.73, 14.70$ for M1; $31.72, 37.67, 32.80$ for M2), M2 reclassified as `CONSTRAINED_MONOEXPONENTIAL_BASELINE`, M3 as `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS`, transfer as `CONDITIONAL_TRAJECTORY_RECONSTRUCTION`, prospective prediction as `BLOCKED`.
- **`FND-0042`**: Updated to supersede draft values, record pH range $6.7932\dots 7.0228$, retract $pH \ge 6.86$, and document conditional transfer $R^2 = 0.8566$.
- **`NEG-0035`**: Documents prospective prediction blockage and M3 unexecutability.
- **`DEC-0016`**: Formally records scientific freeze and corrigendum rulings.
- **Automated Consistency Test**: `tests/test_rehman_model_validation.py::test_report_markdown_json_consistency` guarantees permanent 1:1 numerical alignment between markdown reports and canonical JSON.
