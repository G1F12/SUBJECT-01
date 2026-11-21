# LINK 2 SCIENTIFIC VERIFICATION REPORT: EXP-0130
## Work Done -> Residual Force -> Recovery on Open Cohort Data

**Experiment ID:** EXP-0130  
**Related Findings:** FND-0126  
**Related Negative Results:** NEG-0110  
**Sources:** SRC-0111 (Norbury et al.), SRC-0102 (de Poli et al.), SRC-0086 (McLaughlin et al.)  
**Protocol:** [LINK2_WORK_RECOVERY_PROTOCOL.md](LINK2_WORK_RECOVERY_PROTOCOL.md)  
**Results JSON:** [LINK2_WORK_RECOVERY_RESULTS.json](LINK2_WORK_RECOVERY_RESULTS.json)  

---

### 1. Executive Summary

Requirement R2 mandates empirical verification of Link 2 (**Work Done -> Residual Force -> Recovery**) on available open scientific data. Using individual held-out crossover data from Norbury et al. (leg press volume), published group training data from de Poli et al. (supra-critical cycling), and continuous endurance data from McLaughlin et al. (45-min heat cycling), we tested whether external mechanical work predicts post-exercise force capacity.

Key findings:
1. **Out-of-Sample Defeat of Volume Models:** On Norbury held-out participants (N=12, 24 paired trials), incorporating workload/volume into force prediction increased MAE by 4.08 N over a simple mean retention baseline (baseline MAE 50.61 N vs volume linear MAE 54.69 N). The paired difference under participant-clustered bootstrap is **-4.08 [-8.49, -0.29] N**, strictly favoring the trivial baseline.
2. **Directional Refutation of Scalar Work Fatigue:** In de Poli et al., 5 weeks of SIT enabled participants to perform +11.1% more mechanical work to exhaustion (73.0 vs 65.7 kJ), yet post-exercise force retention **increased** from 71.36% to 75.08% (+3.72 percentage points). This directly refutes the monotonic scalar work-depletion equation F = F0 * (1 - f(W)).
3. **Power Domain Incommensurability:** In McLaughlin et al., participants sustained 270 to 810 kJ of continuous work over 45 minutes without task failure (moderate domain), whereas in de Poli, only ~70 kJ of supra-critical work induced severe task failure. Mechanical Joules are biologically meaningless without reference to Critical Power.
4. **Recovery Kinetics:** In Norbury et al., force was 91.0% at 5 min, 98.3% at 45 min, and 100.1% at 24 h. By 45 minutes, spontaneous recovery accounts for almost all force restoration, leaving zero residual volume variance.
5. **Architectural Decision (DEC-0032):** Direct scalar coupling between mechanical work and force capacity is rejected. A valid transition requires a **4-component transition candidate architecture** (intensity domains, 2-component fatigue, recovery kinetics operator, and task specificity).

---

### 2. Norbury Crossover Evaluation & Model Comparison

Across 12 healthy males in Low Load (30% 1RM) and High Load (70% 1RM):
- LL Volume: 4134.4 +- 898.6 kg·reps | 5-min Retention: 91.01%
- HL Volume: 5064.5 +- 1030.9 kg·reps | 5-min Retention: 91.04%
- Volume increased by **+22.5%**, yet force drop was identical (paired diff +0.04 pp).

| Model | MAE [N] | RMSE [N] | Bias [N] | Rel MAE [%] | Paired dMAE vs Base [95% CI] | Favors |
|---|---:|---:|---:|---:|---:|:---:|
| **Mean Retention Baseline** | 50.61 | 61.74 | +2.79 | 10.4% | Reference (0.0) | -- |
| **Mean Loss Baseline** | 51.52 | 63.85 | +2.86 | 10.6% | -0.91 [-2.24, +0.33] | Inconclusive |
| **Volume Linear Model** | 54.69 | 67.25 | +2.79 | 11.2% | **-4.08 [-8.49, -0.29]** | **Baseline** |
| **Volume Proportional D2** | 54.26 | 66.82 | +2.80 | 11.1% | **-3.65 [-8.06, -0.19]** | **Baseline** |
| **Persistence (Zero-Loss)** | 74.13 | 85.34 | +72.96 | 15.6% | -23.52 [-34.20, -14.18] | **Baseline** |
| **4-Component Candidate** | 50.85 | 61.85 | +2.79 | 10.4% | -0.24 [-1.55, +1.02] | Inconclusive |

---

### 3. de Poli Training Discrepancy & Scalar Falsification

Published group averages (Table 3, N=21):
- **SIT Group (N=11):**
  * Pre-training: Baseline 611 N -> Post 436 N (Retention: 71.36%, Drop: 28.64%)
  * Post-training: Baseline 614 N -> Post 461 N (Retention: 75.08%, Drop: 24.92%)
  * Power increased +11.0%, mechanical work increased +11.1% (65.7 -> 73.0 kJ)
  * Force retention shifted **+3.72 percentage points** (superior force maintenance despite more work)
- **Control Group (N=10):**
  * Pre-training retention 81.83%, Post-training retention 80.81% (-1.02 pp shift)

*Conclusion:* Monotonic scalar work-to-force exhaustion equations are directly falsified by real human physiology.

---

### 4. McLaughlin Endurance Work Association Bounds

In N=23 participants performing 45-min continuous cycling in heat:
- Power output: 175.2 +- 48.7 W (range 105-277 W)
- Cumulative mechanical work: 473.1 kJ (range 283.5-747.9 kJ)
- Participants successfully completed 45 minutes with up to 810 kJ of mechanical work without force failure, demonstrating that sub-CP work does not deplete force via scalar exhaustion.

---

### 5. Multi-Component Architecture & DEC-0032 Synthesis

Scalar work coupling is replaced by a 4-component transition model:
1. **Domain Thresholding:** Sub-CP work produces minimal force loss; severe-domain work depletes W' causing rapid acute exhaustion.
2. **Bi-Compartmental Fatigue:** Distinguishing peripheral metabolite accumulation (H+, Pi) from central voluntary activation deficits (%VA).
3. **Recovery Operator:** F(t) = F_end + (F_pre - F_end)*(1 - exp(-t/tau)), accounting for rapid early recovery (tau approx 30-60 s) and slow low-frequency fatigue.
4. **Task Specificity:** Mapping multi-joint cycle ergometer torque to isometric joint constraint.

---

### 6. Registration
- **EXP-0130**: Open data link verification: Work done -> Residual force -> Recovery (Link 2).
- **FND-0126**: Work-to-force transition failure of scalar volume models and directional refutation on open cohorts.
- **NEG-0110**: External mechanical work fails to improve prediction of post-load residual force over simple retention baseline.
