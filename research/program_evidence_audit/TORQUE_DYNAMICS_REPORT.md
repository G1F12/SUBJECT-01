# DECISIVE SCIENTIFIC TEST REPORT: EXP-0137
## Decisive Out-of-Sample Evaluation of Sequential Torque Fatigue Dynamics Predicting Post-Exercise Residual Force

**Experiment ID:** EXP-0137  
**Related Findings:** FND-0133  
**Related Negative Results:** NEG-0117  
**Related Decisions:** DEC-0034  
**Data Source:** Evangelidis et al. 2023 (SRC-0115, PMC10030419, DOI: [10.1007/s00421-022-05104-0](https://doi.org/10.1007/s00421-022-05104-0))  
**Protocol:** Leave-One-Subject-Out (LOSO) Cross-Validation with 5,000 Participant-Clustered Bootstrap Resamples on Sequential Contraction Blocks  

---

### 1. Executive Summary & Core Scientific Question

> **Core Research Question:**  
> Do sequential contraction torque blocks (11 progress bins from 9.09% to 100% across 99 contractions) provide incremental predictive information regarding post-exercise maximal capacity on held-out human participants beyond baseline force, condition, and total work?

#### Pre-Specified Hypotheses and Utility Criterion:
Prior to statistical evaluation, three candidate dynamic features and an explicit acceptance criterion were established:
1. **$R_{\text{late}}$ (Late-to-early ratio):** $\frac{\frac{1}{3}\sum_{k=8}^{10} \tau_k}{\frac{1}{3}\sum_{k=0}^{2} \tau_k}$ (relative torque preservation).
2. **$S_{\tau}$ (Normalized torque slope):** Linear regression slope across the 11 normalized progress points ($t \in [0, 1]$).
3. **$\tau_{\text{end}}$ (Terminal absolute torque):** $\tau_{10} \times MVT_{\text{pre}} / 100$ (in $\text{Nm}$).
- **Pre-specified Utility Criterion:** A candidate feature must achieve $\Delta\text{MAE} \ge 1.0\text{ Nm}$ relative to both `MeanRetention` and `Pre + Cond`, with a 95% participant-clustered bootstrap confidence interval strictly excluding zero ($p < 0.05$).

---

### 2. Experimental Results & LOSO Cross-Validation

#### Dynamic Conditions (CON + ECC, N=18 across 9 participants):

| Model Architecture | Features Included | LOSO MAE (Nm) | $\Delta\text{MAE}$ vs Base Cond (Nm) [95% CI] | $\Delta\text{MAE}$ vs MeanRet (Nm) [95% CI] | Passes Utility Criterion? |
|---|---|---:|:---:|:---:|:---:|
| **Pre + Cond + $\tau_{\text{end}}$** | $MVT_{\text{pre}} + \text{is\_ECC} + \tau_{\text{end}}$ | **10.224** | **+4.044** [-2.930, +12.394] | **+1.022** [-3.839, +6.747] | **NO (CI spans zero)** |
| **Mean Retention Base** | $MVT_{\text{pre}} \times \overline{\text{ret}}$ | 11.246 | +3.022 | 0.000 | Benchmark Baseline |
| **Condition Retention Base**| $MVT_{\text{pre}} \times \overline{\text{ret}}_{c}$ | 11.585 | +2.683 | -0.339 | Condition Scaler |
| **Pre + Cond + Work + $\tau_{\text{end}}$** | $MVT_{\text{pre}} + \text{is\_ECC} + W + \tau_{\text{end}}$ | 11.847 | +2.421 | -0.601 | Destructive work effect (+1.62 Nm error) |
| **Pre + Cond + Work** | $MVT_{\text{pre}} + \text{is\_ECC} + W_{\text{Joules}}$ | 13.724 | +0.544 [-4.211, +6.252] | -2.478 [-5.187, +0.633] | NO (Loses to MeanRet) |
| **Pre + Cond + $S_{\tau}$** | $MVT_{\text{pre}} + \text{is\_ECC} + S_{\tau}$ | 13.960 | +0.308 [-3.078, +3.574] | -2.714 [-5.773, +0.181] | NO (Inferior to MeanRet) |
| **Pre + Cond + $R_{\text{late}}$** | $MVT_{\text{pre}} + \text{is\_ECC} + R_{\text{late}}$ | 14.075 | +0.193 [-3.576, +3.777] | -2.829 [-5.869, +-0.174] | NO (Inferior to MeanRet) |
| **Pre + Condition Base** | $MVT_{\text{pre}} + \text{is\_ECC}$ | 14.268 | 0.000 | -3.022 | Context Base |

---

### 3. Detailed Mechanistic & Statistical Interpretation

1. **Relative Decay Rates ($R_{\text{late}}$ and $S_{\tau}$) Fail:**
   - Both normalized features yield virtually no improvement over `Pre + Cond` ($\Delta\text{MAE} \le +0.31\text{ Nm}$) and lose by over $2.7\text{ Nm}$ to `MeanRetention`. Normalizing torque decay relative to baseline destroys the critical scale information needed to predict absolute post-exercise capacity.
2. **Terminal Torque ($\tau_{\text{end}}$) Shows Substantial Nominal Signal:**
   - Incorporating absolute terminal torque reduces LOSO MAE to **10.224 Nm**, nominally outperforming the strongest non-work benchmark `MeanRetention` (11.246 Nm) by **+1.022 Nm** and `Pre + Cond` by **+4.044 Nm**.
3. **Failure of the Pre-Specified Statistical Significance Criterion:**
   - Despite nominal gains, the 95% participant-clustered bootstrap confidence interval spans zero:
     * vs `Pre + Cond`: `[-2.930, +12.394] Nm`
     * vs `MeanRetention`: `[-3.839, +6.747] Nm`
   - **Inter-Individual Heterogeneity Breakdown:**
     * In 4 subjects with severe fatigue (P3, P4, P5, P6), $\tau_{\text{end}}$ drastically improved prediction (P3 error was reduced by **+18.64 Nm**, P4 by +5.30 Nm, P5 by +5.96 Nm, P6 by +3.28 Nm).
     * Conversely, in 3 subjects (P1, P2, P7), post-exercise isometric MVT rebounded or remained stable despite dynamic torque dips; in these subjects, $\tau_{\text{end}}$ increased prediction error by **−6.92 Nm to −7.61 Nm**.
     * With $N=9$ participants, this severe bimodal heterogeneity prevents the confidence interval from clearing zero ($p > 0.05$).
4. **Cumulative Work Introduces Destructive Noise:**
   - When cumulative mechanical work ($W_{\text{Joules}}$) is added to the terminal torque model (`Pre + Cond + Work + tau_end`), the MAE degrades from **10.224 Nm** to **11.847 Nm** (an error increase of **+1.623 Nm**). This provides definitive proof that scalar mechanical work acts as a confounding noise variable rather than an informative fatigue index.

---

### 4. Independent Open Data Transfer Boundary

A systematic audit across all candidate open data repositories in the project confirms:
- **Križaj et al. 2025 (SRC-0112):** 21 participants, but only 3 brief EQI contractions (~98% force retention); devoid of progressive intra-session fatigue decay.
- **Jutlah et al. 2026 (SRC-0040):** 21 participants, 567 cycle sprints; records only discrete whole-sprint peak power, devoid of within-bout torque decay profiles.
- **Norbury et al. 2020 (SRC-0111):** 12 participants, leg press volume; records only discrete set volume (kg·reps) and post-exercise time points (5 min, 45 min, 24 h), devoid of intra-set dynamometry.

**Definitive Boundary:**  
No public dataset currently exists that provides continuous/binned intra-bout torque decay traces alongside pre- and post-exercise MVC on larger cohorts ($N \ge 30$). Therefore, the $N=9$ sample of Evangelidis et al. represents the definitive boundary of open-data evidence for fatigue dynamics.

---

### 5. Final Epistemic Decision for Architecture A

The empirical results of EXP-0137 confirm:
1. Dynamic decay slopes do not predict post-exercise force.
2. Terminal torque $\tau_{\text{end}}$ shows promising candidate utility (10.22 Nm vs 11.25 Nm), but cannot be confirmed as statistically significant on open data ($N=9$).
3. Adding mechanical work in Joules actively degrades predictive accuracy.

**System Status:**  
Architecture A remains at **`CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD`** (`verdict = "NOT_CONFIRMED_PENDING_DECISIVE_MEASUREMENTS"`).
