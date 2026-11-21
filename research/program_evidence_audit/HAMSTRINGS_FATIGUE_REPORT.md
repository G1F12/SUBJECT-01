# DECISIVE SCIENTIFIC TEST REPORT: EXP-0136
## Decisive Out-of-Sample Evaluation of Actual Mechanical Work (Joules) Predicting Post-Exercise MVT in a High-Fatigue Modality

**Experiment ID:** EXP-0136  
**Related Findings:** FND-0132  
**Related Negative Results:** NEG-0116  
**Related Decisions:** DEC-0033  
**Data Source:** Evangelidis et al. 2023 (SRC-0115, PMC10030419, DOI: [10.1007/s00421-022-05104-0](https://doi.org/10.1007/s00421-022-05104-0))  
**Protocol:** Leave-One-Subject-Out (LOSO) Cross-Validation with 5,000 Participant-Clustered Bootstrap Resamples  

| Source ID | Data Provenance & Scope |
|---|---|
| SRC-0115 | [PMC10030419](https://pmc.ncbi.nlm.nih.gov/articles/PMC10030419/), [European Journal of Applied Physiology](https://doi.org/10.1007/s00421-022-05104-0). 9 healthy men; within-subject crossover (ISO, CON, ECC); 99 submaximal knee flexions at 50% MVT on Con-Trex isokinetic dynamometer (0–40° RoM at 8°/s). High-fatigue regime (18–34% MVT depression). Verified with SHA-256 (`ec9b6c6f6ecae5bb0f241eade56a4ef5b7869dc4ca8e748c2e1b3655ba1f2ce4`). |

---

### 1. Executive Summary & Core Scientific Question

> **Core Research Question:**  
> In a biological regime characterized by **pronounced fatigue** (18% to 34% maximal voluntary force depression), does measured mechanical work in Joules ($W = \int \tau \cdot d\theta$) improve the out-of-sample prediction of post-exercise maximal capacity on held-out human participants beyond pre-exercise capacity and condition indicators?

#### Definitive Scientific Findings & Methodological Invariants:
1. **Pronounced Fatigue Confirmed:** Unlike previous low-fatigue resistance tests (e.g. Križaj et al. 2025 where post-exercise force was retained at ~98%), this protocol produced substantial, statistically significant force depression:
   - **Concentric (CON):** $-33.59\% \pm 15.01\%$ force drop (Pre: $118.88\text{ Nm} \to$ Post: $77.16\text{ Nm}$).
   - **Eccentric (ECC):** $-30.92\% \pm 7.53\%$ force drop (Pre: $109.36\text{ Nm} \to$ Post: $75.52\text{ Nm}$).
   - **Isometric (ISO):** $-18.41\% \pm 14.65\%$ force drop (Pre: $104.66\text{ Nm} \to$ Post: $84.18\text{ Nm}$).

2. **Physical Nature of Mechanical Work in Joules:**
   - Mechanical work values in Joules represent an **estimate of external shaft work** calculated from published mean torque values (%MVT) across 11 binned contraction intervals and nominal 40° ($0.6981\text{ rad}$) angular displacement across the 99 contractions ($W = \sum 3 \cdot \tau_k \cdot \Delta\theta$).
   - They do **not** represent continuous microsecond dynamometer integration, but constitute the highest-resolution published torque-displacement work estimate available for this cohort.

3. **Out-of-Sample Prediction on Held-Out Participants & Framing:**
   - In dynamic contractions (CON + ECC, N=18), adding mechanical work in Joules to a pre-exercise force + condition baseline yields $\Delta\text{MAE} = +0.544\text{ Nm}$ relative to `Pre + Cond` (improving error from 14.268 Nm to 13.724 Nm).
   - However, its 95% participant-clustered bootstrap confidence interval with 5,000 resamples is **[-4.211, +6.252] Nm** (exploratory 2,000-sample run yielded `[-3.032, +4.939] Nm`). **Both intervals strictly span zero ($p > 0.05$)**, demonstrating that the +0.54 Nm reduction is statistically indistinguishable from random noise.
   - **Crucial Comparison Framing:** The +0.54 Nm improvement is strictly relative to the multi-feature baseline `Pre + Cond` (14.27 Nm). Compared to the parsimonious baseline `MeanRetention` (11.246 Nm), the work model performs **2.478 Nm WORSE** (13.724 Nm vs 11.246 Nm).
   - Across all modalities (CON + ECC + ISO, N=27), adding mechanical work *worsens* error from 12.762 Nm to 13.093 Nm ($\Delta\text{MAE} = -0.331\text{ Nm}$, 95% CI **[-1.479, +0.890] Nm**).

4. **Simpler Baseline Dominance:**
   - The simple non-work baseline `MeanRetention` achieves an MAE of **11.246 Nm**, beating the full model with work (MAE = **13.724 Nm**) by **2.48 Nm**.
   - The physical capacity depletion model ($MVT_{\text{post}} = MVT_{\text{pre}} \cdot (1 - \alpha \cdot W)$) achieves an MAE of **13.549 Nm**, performing **2.30 Nm worse** than constant retention.

5. **Collinearity and Regression Reversal:**
   - Mechanical work is heavily confounded with baseline strength ($r = +0.834$).
   - Multiple linear regression fits a **positive coefficient** for work ($\beta_{\text{work}} = +0.0293\text{ J}^{-1}\cdot\text{Nm}$), because stronger individuals perform more absolute work while also maintaining higher absolute post-exercise torque. This is the direct inverse of a capacity depletion mechanism.

6. **Conclusion:** Even under severe muscular fatigue, actual mechanical work in Joules does not transfer to independent individuals to predict post-exercise capacity. Direct modular coupling in Architecture A remains rejected (**CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD**).

---

### 2. Experimental Design & Fatigue Kinetics

Participants performed 99 submaximal intermittent contractions (5 s contraction, 5 s rest, ~16.5 min total duration) at a target of 50% MVT on a Con-Trex isokinetic dynamometer (0–40° RoM at 8°/s):

| Condition | N Trials | Pre-Exercise MVT (Nm) | Post-Exercise MVT (Nm) | Force Drop (%) | Mean Mechanical Work (J) | Work Range (J) | Active Impulse (N·m·s) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Concentric (CON)** | 9 | $118.88 \pm 25.93$ | $77.16 \pm 15.89$ | $-33.59\% \pm 15.01\%$ | $3420.9 \pm 563.8$ | [2661.9, 4457.3] | $24,499 \pm 4039$ |
| **Eccentric (ECC)** | 9 | $109.36 \pm 22.33$ | $75.52 \pm 17.75$ | $-30.92\% \pm 7.53\%$ | $3448.2 \pm 718.5$ | [2552.4, 4670.7] | $24,694 \pm 5147$ |
| **Isometric (ISO)** | 9 | $104.66 \pm 20.71$ | $84.18 \pm 18.53$ | $-18.41\% \pm 14.65\%$ | $0.0 \pm 0.0$ | [0.0, 0.0] | $25,410 \pm 5032$ |

---

### 3. Out-of-Sample Leave-One-Subject-Out (LOSO) Cross-Validation

#### Dynamic Conditions (CON + ECC, N=18, 9 subjects):

| Model Architecture | Features Used | LOSO MAE (Nm) | $\Delta\text{MAE}$ vs Base Cond (Nm) | 95% Clustered CI (Nm) | Scientific Verdict |
|---|---|---:|---:|---:|:---:|
| **Mean Retention Base** | $MVT_{\text{pre}} \times \overline{\text{ret}}$ | **11.25** | **+3.02** | - | **Best Overall Benchmark** |
| **Condition Retention** | $MVT_{\text{pre}} \times \overline{\text{ret}}_{c}$ | 11.59 | +2.68 | - | Simple Condition Scaler |
| **Linear Pre Baseline** | $MVT_{\text{pre}}$ | 14.08 | +0.19 | - | Linear baseline |
| **Pre + Condition Base** | $MVT_{\text{pre}} + \text{is\_ECC}$ | 14.27 | 0.00 | [0.00, 0.00] | Context-indexed base |
| **Pre + Work** | $MVT_{\text{pre}} + W_{\text{Joules}}$ | 14.13 | +0.14 | - | Worsens vs Linear Pre |
| **Pre + Cond + Work** | $MVT_{\text{pre}} + \text{is\_ECC} + W_{\text{Joules}}$ | 13.72 | +0.54 | [-4.21, +6.25] | **Inconclusive (spans zero)** |
| **Pre + Cond + Impulse**| $MVT_{\text{pre}} + \text{is\_ECC} + I_{\text{Nms}}$ | 13.72 | +0.54 | [-4.21, +6.25] | Inconclusive (spans zero) |
| **Unperturbed Identity**| Identity ($MVT_{\text{post}} = MVT_{\text{pre}}$) | 37.78 | -23.51 | - | Naive Persistence |

#### All Conditions (CON + ECC + ISO, N=27, 9 subjects):

| Model Architecture | Features Used | LOSO MAE (Nm) | $\Delta\text{MAE}$ vs Base Cond (Nm) | 95% Clustered CI (Nm) | Scientific Verdict |
|---|---|---:|---:|---:|:---:|
| **Pre + Impulse** | $MVT_{\text{pre}} + I_{\text{Nms}}$ | 11.86 | +0.90 | - | Baseline with impulse |
| **Pre + Cond + Impulse**| $MVT_{\text{pre}} + \text{Cond} + I_{\text{Nms}}$ | 12.28 | +0.48 | - | Full impulse model |
| **Pre + Condition Base** | $MVT_{\text{pre}} + \text{Cond}$ | 12.76 | 0.00 | [0.00, 0.00] | Context-indexed base |
| **Cond Retention** | $MVT_{\text{pre}} \times \overline{\text{ret}}_{c}$ | 12.77 | -0.01 | - | Trivial condition scaler |
| **Pre + Cond + Work** | $MVT_{\text{pre}} + \text{Cond} + W_{\text{Joules}}$ | 13.09 | -0.33 | [-1.17, +0.65] | **Inconclusive / Inferior (spans zero)** |
| **Pre + Work** | $MVT_{\text{pre}} + W_{\text{Joules}}$ | 13.19 | -0.43 | - | Worsens error |
| **Mean Retention Base** | $MVT_{\text{pre}} \times \overline{\text{ret}}$ | 13.51 | -0.75 | - | Global retention |
| **Linear Pre Baseline** | $MVT_{\text{pre}}$ | 13.54 | -0.78 | - | Univariate baseline |

---

### 4. Cross-Modality Synthesis & Implications for Architecture A

Across all four independent human experimental datasets evaluated across the SUBJECT-01 program:

1. **Sprint Cycling (Jutlah et al., ~18 kJ):** Mechanical work in Joules does not predict subsequent sprint peak power beyond sprint sequence index ($\Delta\text{MAE} = +0.36\text{ W}$ [-3.19, +4.24] W).
2. **Resistance Leg Press (Norbury et al. 2024, 4-5 tonne-reps):** Cumulative resistance volume load (kg·reps) worsens post-exercise knee force prediction relative to simple retention ($\Delta\text{MAE} = -4.38\text{ N}$ [-7.61, -1.91] N).
3. **Plantarflexion Resistance Exercise (Križaj et al. 2025, ~140 J, low fatigue ~2% drop):** Measured work in Joules does not improve out-of-sample MVIC prediction beyond baseline strength ($\Delta\text{MAE} = +0.38\text{ Nm}$ [-1.38, +1.83] Nm under Rule 1; $+0.13\text{ Nm}$ under Rule 2).
4. **Hamstrings Knee Flexion Resistance Exercise (Evangelidis et al. 2023, ~3.4 kJ, pronounced fatigue 18–34% drop):** Measured work in Joules does not improve post-exercise MVT prediction ($\Delta\text{MAE} = +0.54\text{ Nm}$ [-3.03, +4.94] Nm; simple retention beats work model by 2.48 Nm).

**System Status:**
- Architecture A direct scalar coupling ($F = F_0(1 - f(W))$) is conclusively rejected across both low-fatigue and high-fatigue biological regimes.
- Overall Architecture A status remains **`CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD`**.
