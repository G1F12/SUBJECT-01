# PRE-REGISTRATION PROTOCOL: EXP-0129 — Link 1 (Force → Motion → Tissue Limits)

## 1. Scientific Objective & Target Link
- **Target Link**: Link 1 (Force → Motion → Tissue Limits).
- **Core Scientific Inquiry**: Can a closed-chain multi-joint biomechanical model (Strategy 2) accurately predict external footplate force and ensure tendon tissue safety factors ($SF \ge 1.50$) across varying postures, and does it demonstrate statistically significant predictive superiority over naive/simple baselines on held-out human cohort data?
- **Hypothesis**: The multi-joint closed-chain model with physiological specific tension and posture-dependent moment arms explains individual force variation better than naive mean baselines and guarantees connective tissue integrity under target loads.

---

## 2. Cohort Provenance, Data Hygiene & Admission Gates

### 2.1 Audited Datasets
1. **Santos et al. 2024 (`SRC-0090`)**:
   - Source: Open repository (`tmp/data_repository_santos.xlsx`, SHA-256: `8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe`).
   - Task: Bilateral isometric horizontal leg press at nominal knee flexion $\sim 110^\circ$, 11 untrained males at baseline W0, 10 completing 4 longitudinal visits (W0, W2, W4, POS).
   - Reused status: Diagnostic re-evaluation cohort.
2. **DPValid Collection (`SRC-0081`)**:
   - Source: Open CSV repository (`research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv`, SHA-256: `80dc705d5bf3c5a60d65a657ae0753054e3a797a3aa95f537c4f9f9b366772dd`).
   - Task: Single-joint isometric knee extension across multiple joint angles ($30^\circ$, $60^\circ$, $70^\circ$, $90^\circ$), 20 healthy subjects, 125 trials.
   - Status: Single-joint reference benchmark (protocol shift relative to closed-chain leg press).
3. **Scherpereel et al. 2023 (`SRC-0089`)**:
   - Source: Georgia Tech DSpace / Nature Scientific Data (`research/program_evidence_audit/SQUAT_TRANSFER_RESULTS.json`).
   - Task: Multi-activity dynamic squats at 0 lb and 25 lb load, 12 healthy subjects, inverse dynamics joint moments and angles at 20 Hz.
   - Status: Dynamic multi-joint transfer check, governed by unit ambiguity issue `ISS-0028`.
4. **Zöger et al. 2025 (`SRC-0085`, PMC11776222)**:
   - Task: Bilateral isometric leg extension on IsoMed2000 at $100^\circ$ and $140^\circ$.
   - Availability: Data available only upon author request; strictly prohibited from external requests under GOVERNANCE.md.
   - Status: Programmatically classified as `REQUEST_ONLY_BLOCKED`.

---

## 3. Naive & Candidate Models

### 3.1 Force Prediction Models (Santos Cohort)
1. **Baseline 0a (LOSO Mean)**:
   $$\hat{F}_i = \frac{1}{N-1} \sum_{j \neq i} F_j$$
2. **Baseline 0b (Grand Mean)**:
   $$\hat{F}_i = \bar{F}_{\text{cohort}} = 2513.6\text{ N}$$
3. **Baseline 0c (Constant Fixed Force)**:
   $$\hat{F}_i = 2500.0\text{ N}$$
4. **Biomechanical Model (EXP-0061 Corrected)**:
   - Configured at $100^\circ$: $\hat{F} = 2567.0\text{ N}$
   - Configured at $110^\circ$: $\hat{F} = 2976.8\text{ N}$
   - Configured at $140^\circ$: $\hat{F} = 3804.5\text{ N}$
5. **Strategy 2 Model (+21.93% Closed-Chain Target)**:
   - Configured at $100^\circ$: $\hat{F} = 3130.0\text{ N}$
   - Configured at $110^\circ$: $\hat{F} = 3629.6\text{ N}$
   - Configured at $140^\circ$: $\hat{F} = 4632.6\text{ N}$

### 3.2 Tissue Safety Factor Model
- Patellar tendon force: $F_{\text{PT}}(\theta) = \tau_{\text{knee}} / r_{\text{pat}}(\theta)$, where $r_{\text{pat}}(\theta)$ is the Buford/Herzog moment arm.
- Safety factor: $SF(t) = F_{\text{ult}}(t) / F_{\text{PT}}(t)$.
- Invariant threshold: $SF(t) \ge 1.50$ (native biological reserve $SF_0 \ge 1.78$).

---

## 4. Evaluation Metrics & Success Criteria
- Primary Error Metric: Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and Mean Signed Bias (Bias).
- Paired Error Difference: $\Delta\text{MAE} = \text{MAE}_{\text{baseline}} - \text{MAE}_{\text{model}}$ (positive favors model).
- Inferential Test: Participant-clustered bootstrap ($B = 10,000$ resamples, seed 20261121).
- Decision Rules:
  * `MODEL_SUPERIOR`: $\Delta\text{MAE} > 50\text{ N}$ and 95% CI strictly $> 0$.
  * `INCONCLUSIVE`: 95% CI contains 0.
  * `BASELINE_SUPERIOR`: 95% CI strictly $< 0$ (model rejected in favor of trivial baseline).
- Angular Sensitivity: Gradient $dF/d\theta$ evaluated across $100^\circ \to 110^\circ$ and $110^\circ \to 140^\circ$.

---

## 5. Cross-Validation & Partitioning Scheme
- Santos: Leave-One-Subject-Out CV across 11 baseline males; ANOVA partitioning on 10 complete 4-visit participants.
- DPValid: Leave-One-Subject-Out CV across 20 subjects (125 trials) with subject-cluster bootstrap on condition means.
- Scherpereel: Leave-One-Subject-Out CV across 12 subjects on 0 lb and 25 lb squat conditions.
