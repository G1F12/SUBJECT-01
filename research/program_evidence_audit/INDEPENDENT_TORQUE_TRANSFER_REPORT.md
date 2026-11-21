# EXP-0138: Decisive Independent Out-of-Sample Evaluation of Terminal Torque and Dynamic Predictors
## Plantar Flexion (Križaj et al. 2025, Zenodo 15679911) & Resistance Recovery (Norbury et al. 2024, DOI 10.1113/EP091705)

- **Experiment ID:** EXP-0138
- **Findings:** FND-0134
- **Negative Results:** NEG-0118
- **Decisions:** DEC-0035
- **Sources Audited:**
  - Križaj et al. 2025 (`SRC-0112`, Zenodo 15679911, $N=21$ adults, 42 bilateral observations)
  - Evangelidis et al. 2023 (`SRC-0115`, PMC10030419, $N=9$ men, 27 observations)
  - Norbury et al. 2024 (`SRC-0111`, DOI 10.1113/EP091705, PMC7444855, $N=12$ men, 24 observations, 4 sets to failure)

---

### 1. Executive Summary & Audit Resolution

Following `EXP-0137`, which observed an unconfirmed nominal gain of terminal contraction torque ($\tau_{\text{end}}$) over baseline in the Evangelidis hamstrings dataset, this experiment pre-specified and executed an independent transfer and cross-validation evaluation across two open human datasets:
1. **Križaj et al. (2025):** Bilateral plantar flexion contractions at 75% and 90% EQI ($N=21$ adults, 42 observations with same-leg pre/post MVIC).
2. **Norbury et al. (2024):** Unilateral leg press to failure (4 sets) at Low Load (30% 1RM) and High Load (70% 1RM) with recovery measured at 5 min and 45 min ($N=12$ men, 24 observations).

#### Resolution of Numerical Discrepancies
- **Norbury Index Alignment:** The previous report indicated an error increase from 76.99 N to 84.24 N. Audit identified that `y_true` was sorted by condition while predictions were grouped by participant. When predictions and actual values are strictly aligned by participant and condition:
  * 5-min recovery: `PreAlone` MAE = **49.50 N**, `Pre + Vol4` MAE = **47.58 N** ($\Delta\text{MAE} = +1.93\text{ N}$, 95% bootstrap CI `[-6.13, +10.31] N`).
  * 45-min recovery: `PreAlone` MAE = **34.38 N**, `Pre + Vol4` MAE = **32.94 N** ($\Delta\text{MAE} = +1.44\text{ N}$, 95% bootstrap CI `[-4.22, +6.87] N`).
  * Both 95% bootstrap CIs span zero ($p > 0.05$), failing the pre-specified utility criterion ($\Delta\text{MAE} \ge 1.0\text{ N}$ with CI strictly $> 0$).
- **Križaj Same-Leg Matching:** The previous code duplicated a single leg across both conditions. Proper bilateral same-leg pairing across the full archive ($N=21$) yields a baseline `PreAlone` MAE of identically **10.60 N·m** (10.6032 N·m). Permuting condition order within participant preserves this 10.60 N·m exactly. Adding $\tau_{\text{end}}$ yields **10.71 N·m** (Rule 2) or **10.79 N·m** (Rule 1), worsening error by -0.10 to -0.18 N·m.

---

### 2. Discrepancy Reconciliation Table: Old vs Corrected Metrics

| Dataset / Analysis | Old Flawed Value | Corrected Value | Discrepancy Cause | Epistemic Impact |
|---|---|---|---|---|
| **Norbury 5m PreAlone MAE** | 76.99 N | **49.50 N** | Index misalignment (`y_true` ordered by cond, preds by pid) | Baseline accuracy properly restored |
| **Norbury 5m Pre + Vol4 MAE** | 84.24 N | **47.58 N** | Index misalignment in prediction gathering | Nominal error is lower, not higher |
| **Norbury 5m $\Delta\text{MAE}$ (95% CI)** | -7.25 N `[-22.1, +3.8]` | **+1.93 N `[-6.13, +10.31]`** | Subtraction between mismatched participants | CI crosses zero: non-significant gain |
| **Norbury 45m PreAlone MAE** | 63.35 N | **34.38 N** | Index misalignment | Baseline accuracy properly restored |
| **Norbury 45m Pre + Vol4 MAE** | 66.65 N | **32.94 N** | Index misalignment | Nominal error is lower, not higher |
| **Norbury 45m $\Delta\text{MAE}$ (95% CI)** | -3.31 N `[-10.4, +2.9]` | **+1.44 N `[-4.22, +6.87]`** | Subtraction between mismatched participants | CI crosses zero: non-significant gain |
| **Križaj PreAlone Baseline MAE** | 9.63 N·m | **10.60 N·m** | Single leg duplicated for both conditions | Reflects genuine bilateral 42-leg variance |
| **Križaj Pre + $\tau_{\text{end}}$ MAE** | 9.70 N·m | **10.71 N·m (R2) / 10.79 N·m (R1)** | Single leg duplication | Worsens out-of-sample error vs baseline |
| **Križaj Condition Invariance** | Not assessed | **10.60 N·m (invariant)** | Permuted condition order test | Robust mathematical property of OLS |

---

### 3. Direct Model Transfer Evaluation (Evangelidis -> Križaj)

| Model Specification | MAE (N·m) | Bias (N·m) | Status vs Fixed Source Baseline | Status vs Target Local Benchmark |
|---|---|---|---|---|
| **Local Target Benchmark (Križaj PreAlone)** | **10.60** | +0.00 | -- | **Target Optimal Baseline** |
| **Local Target Naive MeanRetention Baseline** | **10.51** | -0.19 | -- | Target Simple Baseline |
| Fixed Evangelidis Retention Baseline ($0.7236 \times \text{pre}$) | 44.97 | -44.97 | **Source Reference Baseline** | Catastrophic Underestimation |
| Fixed Evangelidis PreAlone Baseline ($39.42 + 0.3563 \times \text{pre}$) | 70.22 | -70.22 | Severe Underestimation | Catastrophic Underestimation |
| Fixed Evangelidis $\tau_{\text{end}}$ Model (Overall 42 obs) | **72.51** | +72.51 | **Worsens by -27.54 N·m** | Catastrophic Overestimation |
| Fixed Evangelidis $\tau_{\text{end}}$ Model (75% Condition) | 47.77 | +47.45 | Worsens by -2.80 N·m | Severe Overestimation |
| Fixed Evangelidis $\tau_{\text{end}}$ Model (90% Condition) | 97.24 | +97.24 | Worsens by -52.27 N·m | Severe Overestimation |

#### Protocol Divergence Limiting Direct Transfer
1. **Fatigue Depth:** Evangelidis et al. applied 99 maximal voluntary contractions in 3 blocks, inducing severe hamstring fatigue (mean force retention 72.36%, drop of -27.64%). In contrast, Križaj et al. administered 3 brief submaximal contractions (75% or 90% EQI), causing negligible fatigue (mean force retention 97.32%, drop of -2.68%).
2. **Muscle Groups:** Hamstrings (knee flexors, multi-articular, susceptible to eccentric strain) vs Plantar flexors (triceps surae, high tendon stiffness, isometric/isokinetic ankle plantar flexion).
3. **Transfer Conclusion:** The fixed dynamic model transfers with catastrophic error ($> 72\text{ N·m}$), performing substantially worse than the simple fixed source retention baseline (44.97 N·m). Cross-study transfer without calibration is invalid.

---

### 4. Križaj et al. 2025 LOSO Cross-Validation & Sensitivity Matrix ($N=21$, 42 Obs)

#### Sensitivity Across Justified Matching Rules
| Matching Rule | Evaluated Leg Mapping | PreAlone MAE (N·m) | Pre + $\tau_{\text{end}}$ MAE (N·m) | Pre + Cond + $\tau_{\text{end}}$ MAE (N·m) | $\Delta\text{MAE}$ (Pre - $\tau$) (95% CI) | Utility Outcome |
|---|---|---|---|---|---|---|
| **Rule 2 (Joint Bipartite Error, Recommended)** | $\min(|T_{75}-0.75P_1| + |T_{90}-0.90P_2|)$ | **10.60** | 10.71 | 10.96 | **-0.10 `[-0.75, +0.50]`** | **FAILS (Worsens error)** |
| **Rule 1 (Unilateral 75% Error)** | $\min(|T_{75}-0.75P|)$, contralateral 90% | **10.60** | 10.79 | 10.50 | **-0.18 `[-0.42, +0.03]`** | **FAILS (Worsens error)** |
| **Rule 3 (Joint Relative Error)** | $\min(|T_{75}/P_1-0.75| + |T_{90}/P_2-0.90|)$ | **10.60** | 10.71 | 10.96 | **-0.10 `[-0.75, +0.50]`** | **FAILS (Worsens error)** |
| **Fixed Leg Condition (L75 / R90)** | Constant Left 75%, Right 90% | **10.60** | 10.84 | 11.24 | **-0.24 `[-0.92, +0.44]`** | **FAILS (Worsens error)** |
| **Fixed Leg Condition (R75 / L90)** | Constant Right 75%, Left 90% | **10.60** | 11.03 | 10.83 | **-0.43 `[-1.15, +0.29]`** | **FAILS (Worsens error)** |

*Observation:* Across all 5 matching rules, baseline `PreAlone` MAE is rigorously invariant at **10.60 N·m**. Adding terminal torque ($	au_{\text{end}}$) spans 10.50 to 11.03 N·m, offering zero statistically valid predictive gain over baseline capacity.

#### Participant-Level Breakdown for Križaj (Rule 2)
| Subject | Leg | Condition | Pre (N·m) | Rep 3 $\tau_{\text{end}}$ (N·m) | Post MVIC (N·m) | PreAlone Pred (Err) | Pre + $\tau_{\text{end}}$ Pred (Err) |
|---|---|---|---|---|---|---|---|
| S001 | L | 75% | 244.0 | 188.9 | 226.7 | 236.9 (10.2) | 235.4 (8.7) |
| S001 | R | 90% | 217.3 | 198.5 | 234.6 | 211.4 (23.3) | 212.8 (21.8) |
| S002 | R | 75% | 247.7 | 186.0 | 243.6 | 241.4 (2.2) | 236.7 (6.9) |
| S002 | L | 90% | 206.7 | 187.4 | 193.3 | 202.0 (8.7) | 204.6 (11.3) |
| S003 | L | 75% | 135.2 | 103.9 | 113.9 | 134.4 (20.5) | 133.1 (19.2) |
| S003 | R | 90% | 140.5 | 123.4 | 138.1 | 139.3 (1.2) | 140.1 (2.0) |
| S004 | R | 75% | 162.4 | 122.1 | 151.9 | 159.7 (7.8) | 157.4 (5.6) |
| S004 | L | 90% | 159.4 | 147.9 | 151.1 | 156.8 (5.7) | 159.1 (8.0) |
| S005 | L | 75% | 181.9 | 137.1 | 163.7 | 178.5 (14.7) | 176.3 (12.6) |
| S005 | R | 90% | 170.4 | 153.1 | 162.2 | 167.4 (5.2) | 168.8 (6.6) |
| S006 | R | 75% | 120.9 | 95.1 | 136.3 | 117.3 (18.9) | 116.4 (19.9) |
| S006 | L | 90% | 145.1 | 133.3 | 151.8 | 141.1 (10.7) | 143.0 (8.8) |
| S007 | R | 75% | 145.9 | 110.0 | 131.9 | 143.5 (11.6) | 141.9 (10.0) |
| S007 | L | 90% | 122.6 | 110.4 | 128.3 | 121.1 (7.2) | 122.2 (6.2) |
| S008 | R | 75% | 160.2 | 124.5 | 164.8 | 157.3 (7.6) | 155.4 (9.4) |
| S008 | L | 90% | 163.0 | 147.7 | 146.2 | 160.0 (13.9) | 162.2 (16.0) |
| S009 | L | 75% | 149.1 | 112.6 | 135.7 | 146.9 (11.2) | 145.1 (9.4) |
| S009 | R | 90% | 175.5 | 159.5 | 172.4 | 172.1 (0.3) | 173.9 (1.5) |
| S010 | R | 75% | 175.8 | 133.5 | 167.3 | 172.5 (5.2) | 170.1 (2.8) |
| S010 | L | 90% | 177.6 | 163.9 | 165.0 | 174.1 (9.2) | 176.8 (11.8) |
| S011 | R | 75% | 170.2 | 130.7 | 172.8 | 166.6 (6.2) | 164.6 (8.2) |
| S011 | L | 90% | 211.3 | 185.4 | 207.8 | 205.9 (1.8) | 207.4 (0.4) |
| S012 | L | 75% | 155.7 | 122.4 | 167.9 | 153.2 (14.7) | 151.3 (16.5) |
| S012 | R | 90% | 176.7 | 159.5 | 140.9 | 173.4 (32.5) | 176.1 (35.1) |
| S013 | L | 75% | 141.8 | 109.4 | 142.0 | 139.6 (2.4) | 138.0 (4.0) |
| S013 | R | 90% | 163.4 | 146.6 | 153.2 | 160.3 (7.1) | 162.0 (8.8) |
| S014 | R | 75% | 148.0 | 110.3 | 163.0 | 144.7 (18.3) | 142.0 (21.0) |
| S014 | L | 90% | 160.7 | 146.5 | 158.4 | 157.0 (1.4) | 159.3 (0.9) |
| S015 | R | 75% | 159.8 | 128.9 | 149.7 | 155.8 (6.1) | 155.2 (5.6) |
| S015 | L | 90% | 165.4 | 146.6 | 205.7 | 161.1 (44.6) | 162.0 (43.8) |
| S016 | L | 75% | 203.4 | 153.9 | 210.3 | 197.6 (12.8) | 195.2 (15.1) |
| S016 | R | 90% | 172.0 | 161.9 | 189.7 | 167.7 (22.0) | 170.2 (19.4) |
| S017 | L | 75% | 201.4 | 149.9 | 190.2 | 196.8 (6.6) | 194.0 (3.8) |
| S017 | R | 90% | 208.6 | 190.6 | 205.4 | 203.8 (1.6) | 206.1 (0.7) |
| S018 | R | 75% | 198.4 | 151.6 | 187.8 | 194.2 (6.4) | 191.8 (4.1) |
| S018 | L | 90% | 213.5 | 196.0 | 204.9 | 208.7 (3.8) | 211.5 (6.7) |
| S019 | R | 75% | 242.2 | 183.4 | 229.5 | 233.9 (4.4) | 231.7 (2.2) |
| S019 | L | 90% | 268.7 | 242.5 | 276.0 | 258.7 (17.4) | 260.7 (15.3) |
| S020 | L | 75% | 205.6 | 164.3 | 187.7 | 201.0 (13.3) | 200.0 (12.3) |
| S020 | R | 90% | 185.6 | 177.5 | 189.5 | 181.7 (7.8) | 184.6 (4.9) |
| S021 | R | 75% | 118.8 | 87.8 | 121.8 | 118.3 (3.5) | 116.2 (5.7) |
| S021 | L | 90% | 122.4 | 110.1 | 106.3 | 121.7 (15.4) | 123.1 (16.7) |

---

### 5. Norbury et al. 2024 Recovery Force Evaluation ($N=12$ Men, 24 Obs, 4 Sets to Failure)

*Citation: Norbury et al., 2024, Exp Physiol 109: 1335-1348, DOI 10.1113/EP091705, PMC7444855 (SRC-0111).*

| Recovery Delay | Metric / Model | Baseline PreAlone MAE (N) | Pre + Vol4 MAE (N) | $\Delta\text{MAE}$ (PreAlone - Vol4) | 95% Bootstrap CI (N) | Pre-Specified Utility |
|---|---|---|---|---|---|---|
| **5 minutes post** | Force Recovery (91.01%) | **49.50 N** | 47.58 N | +1.93 N | `[-6.13, +10.31]` | **FAILS (CI crosses zero)** |
| **5 minutes post** | Total Volume (TotVol) | **49.50 N** | 50.07 N | -0.56 N | `[-8.51, +7.68]` | **FAILS (CI crosses zero)** |
| **45 minutes post** | Force Recovery (93.34%) | **34.38 N** | 32.94 N | +1.44 N | `[-4.22, +6.87]` | **FAILS (CI crosses zero)** |
| **45 minutes post** | Total Volume (TotVol) | **34.38 N** | 33.66 N | +0.72 N | `[-4.54, +5.88]` | **FAILS (CI crosses zero)** |

#### Participant-Level Breakdown for Norbury
| Participant | Condition | Pre MVC (N) | Vol 4 (kg·reps) | Post 5m Act | Post 5m PreAlone | Post 5m Pre+Vol4 | Post 45m Act | Post 45m PreAlone | Post 45m Pre+Vol4 |
|---|---|---|---|---|---|---|---|---|---|
| P01 | LL | 827.0 | 990.0 | 818.0 | 729.1 | 727.6 | 787.0 | 747.0 | 745.8 |
| P01 | HL | 820.0 | 1540.0 | 829.0 | 724.9 | 749.6 | 823.0 | 743.1 | 761.7 |
| P02 | LL | 685.0 | 697.5 | 681.0 | 643.9 | 622.4 | 696.0 | 669.6 | 653.0 |
| P02 | HL | 653.0 | 1085.0 | 622.0 | 622.7 | 631.5 | 643.0 | 650.9 | 657.7 |
| P03 | LL | 717.0 | 765.0 | 640.0 | 675.2 | 658.6 | 618.0 | 697.7 | 686.8 |
| P03 | HL | 725.0 | 1190.0 | 599.0 | 680.1 | 694.6 | 654.0 | 702.0 | 711.6 |
| P04 | LL | 690.0 | 652.5 | 596.0 | 662.5 | 641.6 | 723.0 | 669.5 | 647.4 |
| P04 | HL | 641.0 | 1015.0 | 578.0 | 634.5 | 636.8 | 639.0 | 640.0 | 642.4 |
| P05 | LL | 947.0 | 675.0 | 783.0 | 829.3 | 794.6 | 857.0 | 818.8 | 781.1 |
| P05 | HL | 899.0 | 1050.0 | 760.0 | 795.5 | 787.6 | 767.0 | 792.0 | 783.4 |
| P06 | LL | 666.0 | 562.5 | 642.0 | 630.4 | 593.9 | 632.0 | 665.6 | 643.0 |
| P06 | HL | 662.0 | 875.0 | 656.0 | 627.8 | 615.7 | 650.0 | 663.4 | 655.9 |
| P07 | LL | 919.0 | 753.8 | 840.0 | 790.1 | 758.8 | 795.0 | 811.0 | 790.3 |
| P07 | HL | 879.0 | 1172.5 | 778.0 | 765.9 | 770.9 | 761.0 | 787.0 | 790.2 |
| P08 | LL | 781.0 | 753.8 | 614.0 | 711.4 | 697.4 | 659.0 | 728.4 | 717.2 |
| P08 | HL | 781.0 | 1172.5 | 756.0 | 711.4 | 718.8 | 753.0 | 728.4 | 734.3 |
| P09 | LL | 743.0 | 1125.0 | 700.0 | 680.2 | 689.5 | 713.0 | 700.8 | 706.8 |
| P09 | HL | 751.0 | 1750.0 | 756.0 | 685.5 | 728.5 | 771.0 | 705.5 | 733.5 |
| P10 | LL | 775.0 | 900.0 | 713.0 | 702.3 | 695.9 | 745.0 | 720.4 | 715.2 |
| P10 | HL | 843.0 | 1400.0 | 811.0 | 744.8 | 766.1 | 799.0 | 758.9 | 776.5 |
| P11 | LL | 834.0 | 990.0 | 778.0 | 744.4 | 740.5 | 747.0 | 757.5 | 754.8 |
| P11 | HL | 841.0 | 1232.0 | 697.0 | 749.0 | 762.7 | 763.0 | 761.6 | 771.1 |
| P12 | LL | 820.0 | 1057.5 | 734.0 | 743.4 | 744.8 | 742.0 | 754.6 | 755.7 |
| P12 | HL | 920.0 | 1151.5 | 687.0 | 817.1 | 821.7 | 742.0 | 817.8 | 821.2 |

---

### 6. Program Governance & Architecture A Verdict

1. **Separation of Evidence Channels:**
   - **Norbury Volume:** Resistance exercise volume (load × reps) reflects peripheral neuromuscular fatigue during 4 multi-joint sets. While nominal MAE drops slightly (49.50 -> 47.58 N at 5m; 34.38 -> 32.94 N at 45m), the 95% bootstrap CIs span zero in both cases, failing pre-specified utility.
   - **Torque Transfer:** Dynamic single-joint torque ($	au_{\text{end}}$) fails both cross-study transfer (MAE = 72.51 N·m vs local 10.60 N·m) and local retraining (10.60 -> 10.71 N·m).
2. **Whole-System Implication:**
   The empirical coupling between mechanical work/dynamics and residual muscular force remains unvalidated across independent cohorts. Architecture A's bioenergetic bridge cannot substitute for in vivo measurements.
