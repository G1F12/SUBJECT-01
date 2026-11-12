# E1: Independent Human Functional Strength Validation & Antagonist Co-Activation Transfer Audit

**Experiment ID:** EXP-0048  
**Negative Result Ref:** NEG-0045  
**Cycle:** 15  
**Date:** 2026-11-12  
**Working Branch:** `research/cycle15-independent-validation`  
**Status:** `DATA_BLOCKED`  
**Primary Endpoint:** Paired RMSE reduction in fractions of MVC relative to linear sEMG model across unseen human participants.  

---

## 1. Scientific Context and Motivation

In the development stages of SUBJECT-01 (EXP-0045, EXP-0046), mathematical models were developed to map non-invasive neuromuscular signals to active net joint moment during dynamic knee extension using the raw open-access dataset of Bird et al. (2026) ($N=6$ participants, 1,844 dynamic active contraction samples).

In EXP-0046 and the subsequent scientific consolidation (NEG-0044), an alarming failure of model generalization was uncovered when isolating active contraction trials:

| Model ID | Model Description | Mean LOSO $R^2$ (Active-Only Series) | Pooled $R^2$ |
|---|---|---|---|
| **$M_0$** | Constant training-fold mean baseline | $0.00000$ | $0.00000$ |
| **$M_1$ (sEMG)** | Linear agonist-only sEMG model | **$-0.05280$** | $+0.12450$ |
| **$M_2$ (M4)** | sEMG + knee angle + angular velocity | **$-0.11532$** | $+0.11890$ |
| **$M_3$ (Bridge)** | Non-linear physiological bridge with agonist-derived coactivation proxy ($\gamma_{\text{proxy}}$) | **$-0.11482$** | $+0.14120$ |

### The Critical Vulnerability in EXP-0046:
1. The Bridge model ($M_3$) had higher apparent complexity and incorporated pennation angle adaptation and co-activation penalties, yet **substantially underperformed the simplest single-variable sEMG model ($M_1$)** when transferred across unseen human participants (Mean fold $R^2 = -0.11482$ vs. $-0.05280$).
2. The negative $R^2$ demonstrates that cross-subject zero-shot prediction was worse than simply predicting the mean active torque of the training fold.
3. Crucially, the Bird et al. (2026) experimental setup recorded **only one single muscle channel (Vastus Lateralis)**. Antagonist co-activation ($\gamma$) was not measured; it was mathematically inferred as a non-linear monotonic proxy of the agonist activation itself:
   $$\gamma_{\text{proxy}} = \alpha \cdot \text{sEMG}_{\text{VL}}^{1.5}$$
4. True biological co-activation is an independent motor control phenomenon orchestrated by reciprocal inhibition circuits in the spinal cord, dynamic stability requirements, and individual movement habits. Proxying antagonist brake torque from agonist drive introduced severe cross-subject misspecification.

---

## 2. Pre-Registration Protocol (Locked Prior to Outcome Assessment)

To establish an unassailable evidentiary gate, the full experimental protocol was locked in code and documentation before analyzing external cohorts.

### 2.1 Hypotheses
- **Primary Hypothesis ($H_1$):** Directly measured surface EMG from antagonist muscle groups (biceps femoris long head, semitendinosus) provides independent neural drive information that significantly improves the generalization (LOSO transfer) of active knee extension joint moment models relative to a simple agonist-only sEMG model.
- **Null Hypothesis ($H_0$):** Adding measured antagonist sEMG yields no significant reduction in cross-subject RMSE ($\Delta \text{RMSE} < 0.02\text{ MVC}$ or $95\%\text{ CI}$ spanning zero).

### 2.2 Model Definitions

All models predict active net knee extension moment $\hat{\tau}_i(t)$ normalized to participant maximum voluntary contraction (MVC):

1. **Model $M_0$ (Baseline Mean):**
   $$\hat{\tau}_{M0}(t) = \frac{1}{N_{\text{train}}} \sum_{j \in \text{train}} \tau_j$$
2. **Model $M_1$ (Simple sEMG Linear Regression):**
   $$\hat{\tau}_{M1}(t) = \beta_0 + \beta_1 \cdot \tilde{e}_{\text{ag}}(t)$$
   where $\tilde{e}_{\text{ag}}$ is the rectified, envelope-filtered, MVC-normalized agonist EMG (Vastus Lateralis).
3. **Model $M_2$ (M4 Kinematic-sEMG Model):**
   $$\hat{\tau}_{M2}(t) = \beta_0 + \beta_1 \cdot \tilde{e}_{\text{ag}}(t) + \beta_2 \cdot \theta(t) + \beta_3 \cdot \dot{\theta}(t)$$
   incorporating joint angle $\theta$ and angular velocity $\dot{\theta}$.
4. **Model $M_3$ (EXP-0046 Bridge Proxy Model):**
   $$\hat{\tau}_{M3}(t) = \left[ F_0 \cdot \tilde{e}_{\text{ag}}(t) \cdot f_L(\theta) \cdot f_V(\dot{\theta}) \cos\alpha(\theta) - \gamma_{\text{proxy}}(\tilde{e}_{\text{ag}}) \right] \cdot r_{\text{pat}}(\theta)$$
5. **Model $M_4$ (Measured Antagonist Co-Activation Bridge Model):**
   $$\hat{\tau}_{M4}(t) = \left[ F_{\text{max,ext}} \cdot \tilde{e}_{\text{ext}}(t) \cdot f_{L,\text{ext}}(\theta) \cdot f_{V,\text{ext}}(\dot{\theta}) \cos\alpha(\theta) \cdot r_{\text{pat}}(\theta) \right] - \left[ F_{\text{max,flex}} \cdot \tilde{e}_{\text{flex}}(t) \cdot f_{L,\text{flex}}(\theta) \cdot f_{V,\text{flex}}(\dot{\theta}) \cdot r_{\text{ham}}(\theta) \right]$$
   where $\tilde{e}_{\text{flex}}(t)$ is directly measured, bandpass-filtered, MVC-normalized surface EMG from the knee flexors (Biceps Femoris long head / Semitendinosus), and $r_{\text{ham}}(\theta)$ is the flexor moment arm.

### 2.3 Methodological Separation of Calibration Regimes
To prevent statistical leakage and ensure absolute comparability, two distinct regimes were established:
- **Regime A: Completely Uncalibrated (Pure Zero-Shot LOSO).** All model parameters ($\beta$ coefficients, muscle specific tension constants) are fit strictly on $N-1$ participants and evaluated on the held-out participant without any participant-specific calibration.
- **Regime B: Pre-Defined Individual Calibration.** One single isometric MVC trial from the held-out participant is permitted to calibrate subject-specific maximum torque scaling ($F_{\text{max}}$), after which the model is evaluated on all dynamic isokinetic series.
- **Rule:** Results from Regime A and Regime B must NEVER be averaged, merged, or directly contrasted as equivalent.

### 2.4 Primary Endpoint and Decision Rule
- **Primary Metric:** Participant-level paired RMSE reduction in fractions of MVC relative to Model $M_1$:
  $$\Delta \text{RMSE}_k = \text{RMSE}_k(M_1) - \text{RMSE}_k(M_4)$$
  $$\overline{\Delta \text{RMSE}} = \frac{1}{K} \sum_{k=1}^K \Delta \text{RMSE}_k$$
- **Pre-Registered Practical Equivalence Threshold:**
  $$\overline{\Delta \text{RMSE}} \ge 0.02\text{ MVC}$$
  *Rationale:* In adult human knee extension, typical peak isometric MVC torque ranges between $200\text{ and }350\text{ N}\cdot\text{m}$. A threshold of $0.02\text{ MVC}$ corresponds to an absolute torque error reduction of $4.0\text{ to }7.0\text{ N}\cdot\text{m}$. Any improvement smaller than $2\%\text{ MVC}$ falls within the baseline electrical noise floor of surface EMG electrodes, skin-electrode motion artifact, and isokinetic dynamometer torque transducer calibration tolerance ($\pm 1.5\%\text{ FS}$).
- **Formal Decision Rule:**
  - **`GO`:** $\overline{\Delta \text{RMSE}} \ge 0.02\text{ MVC}$ AND $95\%\text{ bootstrap confidence interval} > 0$ across independent human participants in held-out LOSO cross-validation.
  - **`NO_GO`:** $\overline{\Delta \text{RMSE}} < 0.02\text{ MVC}$ OR $95\%\text{ CI}$ crosses zero.
  - **`DATA_BLOCKED`:** Absence of external cohorts providing the required synchronized variables.

---

## 3. Dataset Audit and Integrity Verification

An exhaustive systematic search of global open repositories was executed to find candidate human datasets containing the requisite variables.

### 3.1 Candidate Evaluations

1. **Bird et al. (2026) — Science Robotics / Dryad (10.5061/dryad.sbcc2frmh):**
   - Lacks antagonist EMG channels (only 1 EMG channel recorded: Vastus Lateralis).
   - Served as the discovery/development cohort in EXP-0045/EXP-0046.
   - Reusing Bird 2026 would violate the fundamental independence criterion.
   - **Verdict:** Disqualified.

2. **Wang et al. (2022) — Zenodo (10.5281/zenodo.6457662):**
   - High-quality multi-channel EMG (including VL, RF, VM, BF, SM).
   - However, movements are whole-body daily locomotion tasks (walking, running, squats, lunges, jumps).
   - Knee moments are estimated via multi-body inverse dynamics from ground reaction forces in OpenSim, with substantial estimation uncertainty ($r \approx 0.61$).
   - Completely lacks isolated isokinetic/isometric dynamometer active torque curves and knee extension MVC trials.
   - **Verdict:** Incompatible protocol.

3. **Sanchez & Sotelo (2014) — UCI Machine Learning Repository (ID 278):**
   - Features knee extension from a seated position with RF, VM, BF, ST surface EMG.
   - Includes knee angle via electrogoniometer.
   - **Completely lacks a joint torque transducer, load cell, or dynamometer.**
   - Computing torque prediction error without ground truth torque is physically impossible.
   - **Verdict:** Missing critical target outcome.

4. **Besier et al. (2009) — SimTK OpenSim:**
   - Walking and running gait only; moments derived via inverse dynamics.
   - **Verdict:** Incompatible task.

5. **KneE-PAD & Gait120 — Zenodo / Figshare:**
   - Clinical and gait locomotion datasets lacking dynamometer torque transducers.
   - **Verdict:** Incompatible.

---

## 4. Integrity and Scientific Governance Declaration

In strict compliance with SUBJECT-01 Core Invariants:
1. **No Synthetic Antagonists:** We categorically refused to generate synthetic or simulated antagonist EMG signals (e.g., perturbing agonist signals with Gaussian noise or inverted profiles) and market them as "independent empirical validation".
2. **No Circular Re-Testing:** We refused to re-run models on the Bird 2026 development dataset under altered hyperparameters to claim a positive result.
3. **No Surrogate Manipulation:** We refused to differentiate goniometer kinematics in the UCI dataset to compute inertial proxy moments ($I \ddot{\theta}$) as a substitute for true joint torque.
4. **Accuracy $\ne$ Augmentation:** Even if an EMG-torque model achieved an $R^2 > 0.90$, a better predictive model is a mathematical achievement in signal processing; it is **NOT evidence of biological enhancement or human strength augmentation**.

---

## 5. Formal Verdict

```text
E1_STATUS = DATA_BLOCKED
```

### Registered Result:
- **ID:** NEG-0045
- **Statement:** "In global open-access scientific repositories, there is currently no publicly accessible human dataset that simultaneously provides synchronized isokinetic/isometric dynamometer joint torque, joint kinematics, participant-specific MVC normalization, and simultaneous surface EMG from both knee extensors and knee flexors across independent human participants."
- **Status of Hypothesis HYP-0009:** Remains **`UNVERIFIED / MODEL_ONLY`**. The theoretical hypothesis that antagonist co-activation improves cross-subject active moment transfer cannot be empirically confirmed or refuted until suitable independent human dynamometry data is collected.

---

## 6. Detailed Requirements to Unblock E1

To resolve ISS-0022 and unblock Experiment E1 in subsequent research cycles, an empirical data collection must be executed with the following minimal specifications:

| Parameter | Specification | Purpose |
|---|---|---|
| **Dynamometer** | Biodex System 4 Pro or Humac Norm isokinetic dynamometer ($1000\text{ Hz}$) | Direct, calibrated measurement of external joint torque ($\text{N}\cdot\text{m}$) |
| **Kinematics** | Optical shaft encoder synchronized with dynamometer lever arm | Exact joint angle ($\theta$) and angular velocity ($\dot{\theta}$) |
| **Agonist EMG** | Vastus Lateralis, Rectus Femoris, Vastus Medialis ($1000\text{--}2000\text{ Hz}$, $20\text{--}450\text{ Hz}$ bandpass) | Neural excitation of extensor group |
| **Antagonist EMG** | Biceps Femoris (long head), Semitendinosus ($1000\text{--}2000\text{ Hz}$) | Directly measured antagonist co-contraction |
| **Normalization** | Minimum 3 isometric MVC trials (knee extension at $60^\circ$ and knee flexion at $60^\circ$) | Participant-level normalization of EMG amplitude and maximum joint torque |
| **Contraction Modes** | Concentric isokinetic extension at $60^\circ/\text{s}$ and $120^\circ/\text{s}$, eccentric extension at $60^\circ/\text{s}$, isometric ramps ($20\%, 40\%, 60\%, 80\%, 100\%\text{ MVC}$) | Robustness across dynamic contraction archetypes |
| **Sample Size** | $N \ge 12$ healthy human adults (balanced biological sex) | Sufficient degrees of freedom for robust LOSO bootstrap confidence intervals |
| **Data Licensing** | Unrestricted open deposit (CC-BY 4.0 or CC0) with raw `.mat` or `.h5` files and metadata | Fully reproducible independent validation |
