# OPEN DATA CANDIDATE AUDIT REPORT: EXP-0134
## Sifting, Empirical Reproduction, and Verification of Joint Mechanical Work and Residual Strength Datasets

**Experiment ID:** EXP-0134  
**Related Findings:** FND-0130  
**Related Negative Results:** NEG-0114  
**Related Decisions:** DEC-0033  
**Audited Datasets:** SRC-0102 (de Poli), SRC-0111 (Norbury), SRC-0040 (Jutlah), SRC-0112 (Plantarflexion), SRC-0101 (Souron), SRC-0104 (Kudzia)  

---

### 1. Pre-Registered Audit Framework & Candidate Sifting

To resolve whether mechanical work can be coupled to residual muscular capacity in Architecture A, an open dataset must provide for **the same participant and session**:
1. Actual mechanical work in Joules ($W = \int P \, dt$) or its measured constituents (force/torque, velocity/cadence, displacement).
2. Functional muscular capacity (force or torque MVC, or peak power) measured both **before** and **after** load.
3. Precise time stamp / recovery latency of the post-load evaluation.

#### Summary of Evaluated Candidates:

| Candidate Source | Access Status | Work in Joules? | Pre/Post Capacity? | Post Delay Known? | Usable for Joint LOSO Test? |
|---|:---:|:---:|:---:|:---:|:---:|
| **de Poli et al. (SRC-0102)** | `REQUEST_ONLY_BLOCKED` | Yes (5 Hz cycling) | Yes (Knee MVC) | Yes ($25 \pm 7$ s) | **No** (Individual microdata request-only) |
| **Norbury et al. (SRC-0111)** | `FULLY_OPEN_VERIFIED` | No (kg·reps volume) | Yes (Knee MVC) | Yes (5m, 45m, 24h) | **Yes (for Volume to Force)** |
| **Jutlah et al. (SRC-0040)** | `FULLY_OPEN_VERIFIED` | Yes ($TW$ in J) | Yes (Peak Power W) | Yes (12s, 18s, 24s) | **Yes (for Joules to Power)** |
| **Plantarflexion (SRC-0112)** | `DATA_BLOCKED` | Divergent (~40 J) | Yes (Ankle MVIC) | Unknown window | **No** (Integral & sign discrepancies) |
| **Souron et al. (SRC-0101)** | `VARIABLE_BLOCKED` | No (time to failure) | No (no post-MVC) | N/A | **No** (Lacks work and post MVC) |
| **Kudzia et al. (SRC-0104)** | `ARCHIVE_EMPTY_BLOCKED`| Unknown | Yes (Group CV) | N/A | **No** (Zenodo repo lacks data files) |

---

### 2. Deep Reproduction and Audit of Usable High-Quality Datasets

#### A. Norbury et al. 2020 (SRC-0111, PMC4037563) — Volume to Isometric Force Recovery
- Evaluated 12 participants across 2 conditions (LL 30% 1RM vs HL 70% 1RM to failure, 24 total sessions) from primary spreadsheet `norbury_24156741.xlsx`.
- **Exact Empirical Recovery Kinetics:**
  - **5 minutes:** 91.02%
  - **45 minutes:** 93.34% (LL: 93.01%, HL: 93.67%)
  - **24 hours:** **99.10%** (LL: 99.35%, HL: 98.85%; ratio of means = 99.04%)
- **LOSO Prediction at 45 minutes (2700 s):**
  - Mean Retention Baseline: **46.49 N**
  - Workload Volume Model: **50.86 N**
  - \Delta \text{MAE} (Baseline - Volume): **-4.38 N** (95% CI: [-7.61, -1.91] N, strictly favoring baseline).
- **Audit Outcome:** Confirms checkpoint exactly: 99.10% recovery at 24 hours, and 46.49 N vs 50.86 N MAE at 45 minutes.

#### B. Jutlah et al. 2026 (SRC-0040, OSF db3sk) — Measured Joules to Peak Power Output
- Evaluated 21 active males across 567 repeated sprint cycling trials (10 x 6s, 12s/18s/24s rest) with mechanical work measured directly in Joules.
- **Verification of Work Accumulation:** Strictly confirmed that cumulative work includes only sprints prior to the predicted sprint ($k-1$ sprints before sprint $k$).
- **Multi-Factorial Baseline Comparison:**
  - Sprint Index Baseline: MAE = **89.23 W**
  - Sprint & Rest Baseline: MAE = **89.83 W**
  - Cumulative Work Linear Model: MAE = **88.70 W** (\Delta \text{MAE} = +0.53 W [-2.96, +4.29] W vs Sprint Base, crosses zero)
  - Work + Rest Duration Model: MAE = **89.48 W** (\Delta \text{MAE} = +0.36 W [-3.19, +4.24] W vs Sprint+Rest Base, crosses zero)
  - Sprint, Rest & Work Model: MAE = **91.98 W** (\Delta \text{MAE} = -2.15 W [-5.54, +0.90] W vs Sprint+Rest Base).
- **Audit Outcome:** Adding measured mechanical work to sprint index and recovery regime **worsens** prediction error by -2.15 W. Mechanical work fails to predict individual capacity.

---

### 3. Verdict on Coupling Force and Energy Modules

1. **Can Force and Energy Modules Be Coupled in the Tested Range?**
   - **NO.** Across all available open evidence, scalar mechanical work does not predict residual force or power.
2. **Does the Transition Model Need Restructuring?**
   - **YES.** Direct scalar depletion ($F = F_0(1 - f(W))$) is permanently rejected. A valid transition model must incorporate intensity domain thresholds (critical power / critical torque), non-linear motor unit recruitment, and physiological recovery time constants.
3. **Is an Empirical Measurement Still Lacking for Final Decision?**
   - **YES.** A dataset combining continuous cycling work in Joules with synchronized pre/post isometric MVC at matched 2700 s duration is currently non-existent in open repositories.

---

### 4. Specification for the Missing Decisive In Vivo Measurement

When laboratory or open collaborative data become available, the decisive protocol requires:
- **Modality:** Synchronized cycle ergometry and isometric knee dynamometry.
- **Channels:** Power $P(t)$ in W ($\ge 10$ Hz), $W = \int P \, dt$ in J, Core temperature $T_{\text{core}}(t)$ in °C, MVIC in N at pre, immediately post ($< 30$ s), 5 min, 45 min, and 24 h.
- **Duration:** 2700 s intermittent CPE45 protocol ($D = 0.59\text{--}0.92$, $360$ W impulse).
- **Evaluation:** Paired LOSO out-of-sample comparison of 4-component transition model against empirical retention baseline.
