# DECISIVE SCIENTIFIC TEST REPORT: EXP-0133
## Empirical Evaluation of Mechanical Work, Load Intensity, and Recovery Latency in Predicting Residual Capacity vs Simple Baselines

**Experiment ID:** EXP-0133  
**Related Findings:** FND-0129  
**Related Negative Results:** NEG-0113  
**Related Decisions:** DEC-0033  
**Protocol:** Pre-registered participant-paired LOSO cross-validation with clustered bootstrap  
**Data Sources:** Jutlah et al. 2026 (SRC-0040, OSF db3sk); Norbury et al. 2020 (SRC-0111, PMC4037563)  

---

### 1. Primary Research Question & Pre-Registered Criteria

> **Core Research Question:**  
> Does actually performed mechanical work predict residual muscular capacity (force or power) in the same individuals better than a simple empirical baseline?

#### Pre-Registered Decision Criteria:
- **Primary Metric:** Out-of-sample Mean Absolute Error (MAE) evaluated via Leave-One-Subject-Out (LOSO) cross-validation.
- **Statistical Contrast:** Paired MAE difference (\Delta \text{MAE} = \text{MAE}_{\text{baseline}} - \text{MAE}_{\text{model}}) with 95% participant-clustered bootstrap confidence interval (10,000 resamples).
- **Decision Rule:** A work-based model is confirmed superior only if the lower bound of the 95% CI is strictly positive ($> 0$). If the upper bound is negative ($< 0$), the baseline is superior. If the interval includes zero, the finding is inconclusive.

---

### 2. Dataset 1: Jutlah et al. 2026 (Measured Work in Joules on Repeated Sprints)

- **Cohort:** 21 active males performing 10 x 6s repeated all-out cycling sprints across 3 inter-sprint rest conditions (12 s, 18 s, 24 s rest).
- **Total Post-Fresh Observations:** 567 trials.
- **Workload Metric:** Actual external mechanical work per sprint in Joules ($TW$, mean = 3661.6 J; mean cumulative work = 18702.8 J).
- **Capacity Metric:** Sprint Peak Power output in Watts.

#### Cross-Validation Model Comparison:

| Model / Baseline | Input Features | Out-of-Sample MAE, W | \Delta \text{MAE} vs Retention Base, W | 95% Bootstrap CI, W | Outcome |
|---|---|---:|---:|---:|:---:|
| **Unperturbed Persistence** | None ($P_k = P_1$) | 114.64 | -25.41 | [-34.20, -17.50] | Fails (fatigue exists) |
| **Mean Retention Baseline** | Sprint index $k$ only | **89.23** | **0.00** | **[0.00, 0.00]** | **Best Simple Reference** |
| **Cumulative Work Linear Model** | Cumulative work $W_{\text{cum}}$ (J) | 88.70 | +0.53 | [-2.96, +4.29] | Inconclusive (crosses zero) |
| **Work + Recovery Duration Model** | $W_{\text{cum}}$ (J) + Rest (s) | 89.48 | -0.25 | [-3.87, +3.70] | Inconclusive (crosses zero) |
| **Proportional D2 Depletion** | Proportional $1 - k \cdot W_{\text{cum}}$ | 105.96 | -16.73 | [-26.40, -8.10] | Strictly Refuted |

**Key Finding:** Even when mechanical work is directly and accurately measured in Joules, adding cumulative work improves out-of-sample prediction by only **+0.53 W**, and the 95% CI **[-2.96, +4.29] W** includes zero. Adding recovery duration does not improve prediction (\Delta \text{MAE} = -0.25 W).

---

### 3. Dataset 2: Norbury et al. 2020 (Multi-Time-Point Isometric Force Recovery)

- **Cohort:** 12 active males performing unilateral leg press to failure under Low Load (30% 1RM) and High Load (70% 1RM).
- **Total Workload Contrast:** Volume = 4134.4 kg·reps (LL) vs 5064.5 kg·reps (HL) (+22.5% volume difference).
- **Capacity Metric:** Knee extensor MVIC force in Newtons measured at 5 min, 45 min, and 24 h post-load.

#### Multi-Delay Cross-Validation Comparison:

| Recovery Delay | Persistence MAE, N | Mean Retention Base MAE, N | Workload Volume Model MAE, N | \Delta \text{MAE} (Base - Vol), N | 95% Bootstrap CI, N | Verdict |
|---|---:|---:|---:|---:|---:|:---:|
| **5 minutes (300 s)** | 74.12 | **50.61** | 54.69 | **-4.08** | **[-8.49, -0.29]** | **Base Superior (Vol Fails)** |
| **45 minutes (2700 s)** | 61.42 | **46.49** | 50.86 | **-4.38** | **[-7.61, -1.91]** | **Base Superior (Vol Fails)** |
| **24 hours (86400 s)** | **39.96** | 40.96 | 42.35 | -1.39 | [-3.45, +0.24] | Inconclusive |

**Key Finding:** Across the entire acute and intermediate recovery timeline (5 min and 45 min), adding workload volume statistically significantly **worsens** out-of-sample prediction by -4.08 N and -4.38 N relative to a simple empirical retention baseline. Similarly, relative load intensity (% 1RM) offers no advantage.

---

### 4. Definitive Scientific Answer & Architecture A Integration Verdict

1. **Answer to Primary Question:**  
   **NO.** Actually performed mechanical work (whether in Joules or in kg·repetitions) does **NOT** predict residual muscular force or power on held-out individuals significantly better than a simple empirical time-dependent retention baseline.
2. **Mechanism:**  
   Scalar accumulation of mechanical work ($W = \int P \, dt$ or $\sum m \cdot \text{reps}$) neglects intensity domain boundaries (sub-CP vs. supra-CP), differential neuromuscular vs. metabolic fatigue contributions, and non-linear recovery kinetics. Fitting work-to-force coefficients on training cohorts overfits idiosyncratic fatigue susceptibility without generalizing to new individuals.
3. **Implication for Architecture A:**  
   Direct coupling between the bioenergetic work module and the muscular force module via a scalar depletion equation ($F = F_0(1 - f(W))$) remains **REJECTED (NO-GO)**. Architecture A cannot use performed mechanical work as a surrogate for residual maximal strength. The 4-component candidate transition framework remains an unvalidated hypothesis.
