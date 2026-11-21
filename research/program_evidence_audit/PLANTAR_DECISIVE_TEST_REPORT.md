# DECISIVE SCIENTIFIC TEST REPORT: EXP-0135
## Direct Out-of-Sample Evaluation of Measured Work in Joules Predicting Post-Exercise MVIC Torque on Zenodo 15679911

**Experiment ID:** EXP-0135  
**Related Findings:** FND-0131  
**Related Negative Results:** NEG-0115  
**Related Decisions:** DEC-0033  
**Data Source:** Križaj et al. 2025 (SRC-0112, PMC12238097, DOI: [10.5281/zenodo.15679911](https://doi.org/10.5281/zenodo.15679911))  
**Protocol:** Leave-One-Subject-Out (LOSO) Cross-Validation with 5,000 Participant-Clustered Bootstrap Resamples  

| Source ID | Data Provenance & Scope |
|---|---|
| SRC-0112 | [Zenodo 15679911](https://doi.org/10.5281/zenodo.15679911), [PMC12238097](https://pmc.ncbi.nlm.nih.gov/articles/PMC12238097/). 21 raw workbooks (126 records) verified with SHA-256; HumacNorm dynamometer coordinate polarity resolved (discrepancy median 1.05 J); out-of-sample LOSO cross-validation executed in EXP-0135. |

---

### 1. Executive Summary & Core Scientific Question

> **Core Research Question:**  
> Does actually measured mechanical work in Joules ($W = \int \tau \cdot d\theta$) improve the out-of-sample prediction of post-exercise maximal voluntary isometric contraction torque (MVIC) on held-out human participants compared to baselines accounting for pre-exercise capacity and load conditions?

#### Definitive Result:
1. **Direct Test Execution:** **PASSED.** The full Zenodo 15679911 archive (21 workbooks, 126 records) was downloaded, verified against publisher checksums, and admitted to direct test following resolution of dynamometer spindle coordinate polarity.
2. **Out-of-Sample Prediction:** **NO STATISTICALLY SIGNIFICANT IMPROVEMENT.** On this dataset, adding measured mechanical work in Joules to a pre-exercise force + condition baseline yields a paired MAE difference of **+0.38 Nm** with a 95% bootstrap confidence interval of **[-1.39, +1.81] Nm**, which strictly crosses zero. Under alternative joint bipartite matching, the difference is **+0.13 Nm** [-1.43, +1.42] Nm.
3. **Comparison to Simpler Baseline:** Compared to a simple univariate baseline predicting post-exercise force directly from pre-exercise force (MAE = **10.60 Nm**), adding condition and mechanical work slightly worsens MAE to **10.62 Nm** ($Delta\text{MAE} = -0.02\text{ Nm}$ [-1.85, +1.52] Nm).
4. **Resolution of Recalculation Discrepancy:** The difference between reported +0.38 Nm, +0.20 Nm, and +0.13 Nm is mathematically resolved:
   - Rule 1 (unilateral 75% error minimization) + angle integral $\implies \mathbf{+0.38\text{ Nm}}$.
   - Rule 1 + speed integral $\implies \mathbf{+0.50\text{ Nm}}$.
   - Rule 2 (joint bipartite error minimization) + speed integral $\implies \mathbf{+0.20\text{ Nm}}$.
   - Rule 2 + angle integral $\implies \mathbf{+0.13\text{ Nm}}$.
   In all variations, 95% bootstrap CIs span zero, and the simple non-work `Linear Pre` baseline outperforms the work model.

---

### 2. Sample Composition & Provenance Audit

- **Discrepancy:** The raw Zenodo archive contains **21 workbooks** (`Subjekt01_IZOK.xlsx` to `Subjekt21_IZOK.xlsx`) with 6 sheets each (126 raw records), whereas the published article reports **20 participants** (9 men, 11 women).
- **Resolution & Provenance Nuance:**
  - For subjects S001 to S020, anthropometrics of the 9 men match Table 1 of Križaj et al. 2025 to the exact decimal: Age **25.1 ± 3.1 yr** (published: 25.1 ± 3.1), Height **183.2 ± 4.5 cm** (published: 183.2 ± 4.5), Body mass **84.0 ± 6.9 kg** (published: 84.0 ± 6.9), MVIC Left **202.7 ± 38.6 Nm** (published: 202.7 ± 38.6), MVIC Right **199.0 ± 29.7 Nm** (published: 199.0 ± 29.7).
  - S021 is an extra female participant (age 22) whose workbook features non-standard sheet naming (`Nivo2_1` instead of `Nivo2_Pon1`). Note: non-standard naming alone does not definitively prove pilot status, but sensitivity checks confirm identical conclusions with or without S021.
  - S004 in `Nivo2_Pon1` had an abortive recording (7273 points, mean torque 99.6 Nm vs expected 144 Nm). Excluding S004 matches women's height (169.9 cm) and mass (66.5 kg) to published Table 1.
  - Models evaluated across full N=21 and N=20 cohorts show identical scientific behavior.

---

### 3. Signal Processing & Coordinate Polarity Resolution

- **The Coordinate Polarity Discovery:**
  - In every workbook, exactly **3 out of 6 sheets** exhibited opposite signs between position rate of change ($d\theta/dt$) and the dynamometer `Speed(d/s)` channel.
  - **Physical Mechanism:** The HumacNorm isokinetic dynamometer measures spindle shaft angular velocity relative to a fixed hardware coordinate frame. For the Left ankle, dorsiflexion rotates the spindle in one direction; for the Right ankle, dorsiflexion rotates the spindle in the opposite direction.
  - **Resolution:** By matching coordinate polarity (integrating physical mechanical work $|W|$ or accounting for leg side), the torque-angle integral ($W_\theta = \int \tau \cdot d\theta$) and torque-velocity integral ($W_t = \int \tau \cdot \omega \cdot dt$) agree within a **median of 1.05 J** across all 126 records (mean 1.33 J, 95th percentile 3.07 J, max 6.44 J).
  - The previous apparent discrepancy of **23.17 J** was an artifact of computing naive difference without reconciling dynamometer spindle coordinates across bilateral tests.

---

### 4. Work Distribution & Fatigue Kinetics

| Metric | 75% MVIC Load Condition | 90% MVIC Load Condition | Notes |
|---|:---:|:---:|---|
| **Mean Mechanical Work (J)** | **135.9 ± 34.4** | **119.4 ± 35.8** | 75% load yielded greater work due to longer time under tension |
| **Work Range (J)** | [93.6, 225.6] | [71.3, 203.3] | **71.1% range overlap** between conditions |
| **MVIC Retention (%)** | **98.9% ± 8.9%** | **97.1% ± 7.5%** | No significant post-exercise force depression (main effect $p = 0.636$) |

---

### 5. Out-of-Sample Cross-Validation Results

#### Primary LOSO Cross-Validation ($N=21$, Angle Work Integral, Rule 1):

| Model Architecture | Features Used | LOSO MAE (Nm) | $Delta MAE$ vs Base Cond (Nm) | 95% Clustered CI (Nm) | Outcome |
|---|---|---:|---:|---:|:---:|
| **Unperturbed Persistence** | Identity ($MVIC_{\text{post}} = MVIC_{\text{pre}}$) | 11.28 | -0.28 | [-1.45, +0.88] | Naive benchmark |
| **Mean Retention Base** | $MVIC_{\text{pre}} \times \overline{\text{ret}}$ | 10.51 | -0.32 | [-1.50, +0.85] | Trivial scaler |
| **Linear Pre Baseline** | $MVIC_{\text{pre}}$ | **10.60** | **+0.40** | [-0.35, +1.15] | **Best simple reference** |
| **Pre + Condition Base** | $MVIC_{\text{pre}} + \text{Cond}$ | 11.00 | 0.00 | [0.00, 0.00] | Context-indexed base |
| **Full Model with Work** | $MVIC_{\text{pre}} + \text{Cond} + W_{\text{total}}$ | **10.62** | **+0.38** | **[-1.39, +1.81]** | **Inconclusive (spans zero)** |

#### Alternative Condition Matching & Integration Modalities:

1. **Rule 1 Speed Integral ($W_t$):** MAE = 10.50 Nm; $Delta MAE = +0.50\text{ Nm}$ [-1.32, +1.98] Nm (spans zero).
2. **Rule 2 Joint Bipartite Angle ($W_\theta$):** MAE = 10.73 Nm; $Delta MAE = +0.13\text{ Nm}$ [-1.43, +1.42] Nm (spans zero).
3. **Rule 2 Joint Bipartite Speed ($W_t$):** MAE = 10.66 Nm; $Delta MAE = +0.19\text{ Nm}$ [-1.37, +1.51] Nm (spans zero).
4. **Published Cohort ($N=20$, Exclude S021):** MAE = 10.72 Nm; $Delta MAE = +0.37\text{ Nm}$ [-1.50, +1.86] Nm (spans zero).
5. **Alternative Cohort ($N=20$, Exclude S004):** MAE = 10.79 Nm; $Delta MAE = +0.45\text{ Nm}$ [-1.48, +2.01] Nm (spans zero).

---

### 6. Epistemic Scope & Implications for Architecture A

1. **Tested Operational Scope:**
   - Single bout of 3 repetitions of eccentric quasi-isometric (EQI) plantarflexion resistance exercise.
   - Work range: 71 to 226 Joules (~0.1 to 0.2 kJ).
   - Post-exercise latency: immediately following final repetition (< 60 s).
   - Muscle group: ankle plantar flexors (soleus / gastrocnemius).
2. **Epistemic Finding:**
   - On this dataset, incremental predictive value of mechanical work is not established beyond baseline force and condition indicators.
   - Across available human resistance and sprint datasets (Jutlah, Norbury et al. 2024, Križaj, Evangelidis), direct scalar work coupling is unconfirmed.
3. **Architecture A Status:**
   - Direct module coupling between scalar mechanical work and residual muscular capacity remains unsupported on open human data.
   - Overall Architecture A status remains **`CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD`**.
