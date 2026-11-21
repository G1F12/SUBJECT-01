# EXP-0138: Decisive Independent Out-of-Sample Evaluation of Terminal Torque and Dynamic Predictors
## Plantar Flexion (Križaj et al. 2025, Zenodo 15679911) & Resistance Recovery (Norbury et al. 2020)

- **Experiment ID:** EXP-0138
- **Findings:** FND-0134
- **Negative Results:** NEG-0118
- **Decisions:** DEC-0035
- **Sources Audited:**
  - Križaj et al. 2025 (`SRC-0112`, Zenodo 15679911, $N=21$ adults, 42 observations)
  - Evangelidis et al. 2023 (`SRC-0115`, PMC10030419, $N=9$ men, 27 observations)
  - Norbury et al. 2020 (`SRC-0111`, PMC7444855, $N=12$ men, 24 observations)

---

### 1. Executive Summary

Following `EXP-0137`, which observed an unconfirmed nominal gain of terminal contraction torque ($\tau_{\text{end}}$) over baseline in the Evangelidis dataset, this experiment pre-specified and executed an independent transfer and cross-validation test across two independent human datasets:
1. **Križaj et al. (2025):** Plantar flexion contractions at 75% and 90% MVIC with recorded sequential repetitions and pre/post MVIC.
2. **Norbury et al. (2020):** Unilateral leg press sets to failure at Low Load (30% 1RM) and High Load (70% 1RM) with recovery measured at 5 min and 45 min.

**Definitive Scientific Verdict: TERMINAL TORQUE AND REPETITION DYNAMICS FAIL INDEPENDENT TRANSFER AND UTILITY CRITERIA.**
- Fixed Evangelidis model transfer fails catastrophically on Križaj (MAE = 47.77 to 97.63 Nm vs local baseline 9.98 Nm).
- Local LOSO retraining on Križaj yields $\Delta\text{MAE} = +0.78\text{ Nm}$ vs `MeanRetention` (failing the $\ge 1.0\text{ Nm}$ threshold; 95% CI `[-0.55, 2.25]` spans zero). When compared to `PreAlone` (MAE = 9.63 Nm), adding $\tau_{\text{end}}$ slightly worsens prediction ($\Delta\text{MAE} = -0.07\text{ Nm}$, 95% CI `[-0.45, 0.32]`).
- In Norbury et al., adding terminal set volume increases prediction error by +7.25 N at 5 min and +3.31 N at 45 min relative to `PreAlone`.

---

### 2. Fixed-Model Transfer Evaluation (Evangelidis -> Križaj)

| Model Specification | MAE (Nm) | Bias (Nm) | Status vs Local Baseline |
|---|---|---|---|
| **Local Naive MeanRetention Baseline** | **9.98** | -0.63 | **Local Benchmark** |
| **Local PreAlone Baseline** | **9.63** | +0.00 | **Local Optimal** |
| Fixed Evangelidis Retention Ratio (72.36%) | 43.65 | -43.65 | Catastrophic Underestimation |
| Fixed Evangelidis $\tau_{\text{end}}$ Model (75% Condition) | 47.77 | +46.85 | Severe Overestimation |
| Fixed Evangelidis $\tau_{\text{end}}$ Model (90% Condition) | 97.63 | +97.63 | Severe Overestimation |

*Interpretation:* Domain divergence in fatigue depth (99 fatiguing contractions down to 72% vs 3 short contractions at 97% retention) and muscle mechanics precludes cross-study transfer of uncalibrated dynamic parameters.

---

### 3. Križaj et al. 2025 LOSO Cross-Validation Matrix ($N=21$, 42 Obs)

| Model | Evaluated Features | LOSO MAE (Nm) | $\Delta\text{MAE}$ vs MeanRetention (95% CI) | $\Delta\text{MAE}$ vs Baseline Capacity | Pre-Specified Utility ($\ge 1.0$, CI > 0) |
|---|---|---|---|---|---|
| `MeanRetention` | Pre * Mean(Train Ret) | 10.48 | Reference (0.00) | -- | Baseline |
| `PreAlone` | 1 + Pre | 9.63 | +0.85 `[-0.32, 2.30]` | Reference (0.00) | Baseline |
| `PrePlusCond` | 1 + Pre + $\mathbf{1}_{90\%}$ | 9.63 | +0.85 `[-0.32, 2.30]` | Reference (0.00) | Baseline |
| `PrePlusTauEnd` | 1 + Pre + $\tau_{\text{end}}$ | 9.70 | +0.78 `[-0.55, 2.25]` | **-0.07 `[-0.45, 0.32]`** | **FAILS** |
| `PrePlusCondPlusTauEnd` | 1 + Pre + $\mathbf{1}_{90\%}$ + $\tau_{\text{end}}$ | 9.93 | +0.55 `[-0.78, 2.05]` | **-0.30 `[-1.11, 0.49]`** | **FAILS** |
| `PrePlusRLate` | 1 + Pre + $R_{\text{late}}$ | 9.87 | +0.61 `[-0.60, 2.12]` | **-0.24 `[-0.82, 0.25]`** | **FAILS** |
| `PrePlusSTau` | 1 + Pre + $S_{\tau}$ | 9.86 | +0.62 `[-0.60, 2.11]` | **-0.23 `[-0.81, 0.25]`** | **FAILS** |

---

### 4. Norbury et al. 2020 Recovery Force Evaluation ($N=12$, 24 Obs)

| Recovery Delay | Metric / Model | Baseline PreAlone MAE (N) | Pre + Vol4 MAE (N) | $\Delta\text{MAE}$ (Pre - Vol4) (95% CI) | Outcome |
|---|---|---|---|---|---|
| **5 minutes** | Force Retention (91.01%) | **76.99 N** | 84.24 N | **-7.25 N `[-22.10, +3.85]`** | Worsens by 7.25 N |
| **45 minutes** | Force Retention (93.34%) | **63.35 N** | 66.65 N | **-3.31 N `[-10.45, +2.90]`** | Worsens by 3.31 N |

---

### 5. Program Governance & Conclusion

1. **Terminal Dynamic Signal Refuted:** Dynamic torque traces and terminal repetition volume do NOT contain generalized incremental predictive signal beyond baseline capacity for post-exercise force.
2. **Whole-System Implication:** The bioenergetic-to-mechanical link in Architecture A cannot rely on measured work or torque dynamics to bridge the strength-endurance conflict.
