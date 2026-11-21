# LINK 1 SCIENTIFIC VERIFICATION REPORT: EXP-0129
## Force -> Motion -> Tissue Limits on Open Cohort Data

**Experiment ID:** EXP-0129  
**Related Findings:** FND-0125  
**Related Negative Results:** NEG-0109  
**Sources:** SRC-0090 (Santos et al.), SRC-0081 (DPValid), SRC-0089 (Scherpereel et al.), SRC-0085 (Zoger et al.)  
**Protocol:** [LINK1_FORCE_TISSUE_PROTOCOL.md](LINK1_FORCE_TISSUE_PROTOCOL.md)  
**Results JSON:** [LINK1_FORCE_TISSUE_RESULTS.json](LINK1_FORCE_TISSUE_RESULTS.json)  

---

### 1. Executive Summary

Requirement R2 mandates empirical verification of Link 1 (**Force -> Motion -> Tissue Limits**) on available open scientific data. We evaluated candidate cohort datasets, tested closed-chain multi-joint models against naive baselines on the Santos holdout cohort, quantified postural angle sensitivity gradients, partitioned longitudinal training progression from test-retest noise, audited single-joint reference transfer on DPValid, evaluated dynamic transfer on Scherpereel squats, and established tendon tissue safety factor bounds.

Key findings:
1. **Candidate Cohort Admission:** External open cohorts for bilateral isometric leg press remain blocked. Zoger et al. 2025 (`SRC-0085`, PMC11776222) is classified as `REQUEST_ONLY_BLOCKED` under project governance.
2. **Santos Holdout Evaluation:** At the actual task angle (~110 deg), the multi-joint model predicts 2976.8 N, exhibiting a large positive bias of +463.2 N (MAE 613.6 N), being outperformed by a trivial constant baseline F0 = 2500 N (MAE 458.8 N, bias -13.6 N).
3. **Postural Angle Sensitivity:** The angular sensitivity gradient is 40.98 N/deg (100 deg -> 110 deg) and 27.59 N/deg (110 deg -> 140 deg). A 10 deg mismatch generates a ~410 N artifact (16.3% of baseline), comparable to the entire +20% target effect size.
4. **Variance Separation (ANOVA):** Across 10 complete participants over 4 visits, two-way ANOVA separates systematic multi-week training progression (SS = 1.60e6) from residual test-retest error (SS = 2.87e6, detrended Sw = 309.08 N, CV = 10.80% vs naive Sw = 385.70 N).
5. **Single-Joint Reference (DPValid):** PCSA model M2 yields Delta R2 = +0.0735 (95% CI [+0.0259, +0.1428]), falling below the pre-registered superiority threshold Delta_min = 0.08 (INCONCLUSIVE).
6. **Dynamic Squat Blocker (ISS-0028):** Adding velocity to joint angle regression fails to improve moment prediction on Scherpereel data (0.27046 vs 0.27077 at 0 lb); unresolved unit ambiguity (N*m vs N*m/kg in Plot_3x3_plots.m) blocks coupling into tissue force gates.
7. **Tissue Safety Margins:** Strategy 2 preserves SF = 2.05 >= 1.50 under quasi-static loading, but explosive ballistic recruitment (dF/dt = 20,000 N/s) drops local enthesis SF to 1.31 < 1.50, establishing a strict rate-limiting requirement.

---

### 2. Candidate Cohort Admission Audit

| Cohort | Source | Open Data Available | Task | Admission Decision |
|---|---|:---:|---|---|
| **Zoger et al. 2025** | SRC-0085 / PMC11776222 | No | Bilateral isometric leg press | **REQUEST_ONLY_BLOCKED** |
| **OpenCap (Uhlrich 2023)** | SimTK | Yes | Dynamic gait, squats, jumps | **PROTOCOL_MISMATCH_REJECTED** |
| **Zushi et al. 2024** | Figshare / PLOS ONE | Yes | Unilateral isometric leg press | **PROTOCOL_MISMATCH_REJECTED** |
| **Zenodo 6503956** | Zenodo | Yes | Dynamic 1RM leg press (elderly) | **PROTOCOL_MISMATCH_REJECTED** |

---

### 3. Santos Holdout Model Evaluation (Visit W0)

Cohort baseline force: 2513.6 +- 577.7 N (range 1678.0-3647.1 N across N=11 males).

| Model | Pred [N] | MAE [N] | RMSE [N] | Bias [N] | Rel MAE [%] | Paired dMAE vs LOSO [95% CI] | Favors |
|---|---:|---:|---:|---:|---:|---:|:---:|
| **LOSO Mean Baseline** | 2513.6 | 465.3 | 557.4 | 0.0 | 19.3% | Reference (0.0) | -- |
| **Grand Mean Baseline** | 2513.6 | 447.1 | 550.9 | 0.0 | 18.5% | +18.2 [-0.6, +38.6] | Inconclusive |
| **Fixed Constant 2500 N** | 2500.0 | 458.8 | 551.1 | -13.6 | 19.0% | +6.6 [-11.7, +26.6] | Inconclusive |
| **Corrected Model 100 deg** | 2567.0 | 477.1 | 554.5 | +53.4 | 19.9% | -11.8 [-65.5, +32.4] | Inconclusive |
| **Corrected Model 110 deg** | 2976.8 | 613.6 | 722.9 | +463.2 | 27.2% | -148.3 [-344.7, +31.3] | Inconclusive |
| **Corrected Model 140 deg** | 3804.5 | 1290.9 | 1408.8 | +1290.9 | 56.4% | -825.6 [-1184.2, -493.5] | **Baseline** |
| **Strategy 2 Target 110 deg** | 3629.6 | 1121.7 | 1247.7 | +1116.0 | 48.7% | -656.4 [-993.4, -345.9] | **Baseline** |

---

### 4. Postural Angular Sensitivity & Artifact Magnitude

- Gradient 100 deg -> 110 deg: **40.98 N/deg**
- Gradient 110 deg -> 140 deg: **27.59 N/deg**
- Artifact from 10 deg mismatch: **409.8 N (16.3% of baseline)**

*Implication:* Without subject-specific segment geometry and postural angle calibration, biomechanical model transfer errors exceed the entire +20% target margin.

---

### 5. Multi-Week Progression vs Within-Session Repeatability (ANOVA)

Across 10 complete participants over 4 visits:
- Grand Mean: 2862.35 N
- Naive Within-Subject SD (Sw): 385.70 N (CV = 13.47%)
- Detrended Within-Subject SD (Sw): 309.08 N (CV = 10.80%)
- ICC(3,1) Consistency: 0.7871 | Agreement: 0.7251
- ANOVA Partitioning:
  * SS Progression = 1596999.4
  * SS Residual Error = 2865965.2 (SD = 325.80 N)

---

### 6. Transfer Boundaries & Tissue Safety Bounds

1. **In Vivo Human Validation Gap:** No open dataset contains simultaneous calibrated multi-joint footplate forces and high-speed in vivo patellar tendon ultrasound strain during maximal leg press.
2. **Squat Unit Ambiguity (ISS-0028):** Published CSV moments in Scherpereel et al. are scaled ambiguously between N*m and N*m/kg, preventing direct coupling into tissue force gates.
3. **Quasi-Static vs Ballistic Tissue Margins:**
   - Under quasi-static isometric leg press at 4800 N target (2400 N/limb), Case 2C remodeling preserves SF = 2.05 >= 1.50.
   - Under explosive ballistic 100% MVC (dF/dt = 20,000 N/s), viscoelastic shear stress concentrations drop local enthesis safety factor to SF = 1.31 < 1.50, demanding rate-limiting control.

---

### 7. Registration
- **EXP-0129**: Open data link verification: Force -> Motion -> Tissue limits (Link 1).
- **FND-0125**: Biomechanical model out-of-sample bias, angular sensitivity, and tissue hazard bounds on open cohorts.
- **NEG-0109**: Biomechanical closed-chain model fails to outperform trivial constant baseline at matched task posture without individual joint geometry.
