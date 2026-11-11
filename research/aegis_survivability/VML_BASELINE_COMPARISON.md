# VML Baseline Comparison & Forensic Provenance Audit (Cycle 5)

**Program:** AEGIS-01 / Research Cycle 5  
**Document ID:** `AEGIS-VML-AUDIT-C5`  
**Related Registries:** `EXP-0074`, `HYP-0028`, `FND-0082`, `NEG-0072`, `DEC-0033`, `SRC-0125`  
**Primary Empirical Anchor:** Dziki et al. (2016). *An acellular biologic scaffold treatment for volumetric muscle loss: results of a 13-patient cohort study*. npj Regenerative Medicine 1:16008; DOI: 10.1038/npjregenmed.2016.8 (PMC5744714).

---

## 1. Executive Summary & Epistemic Pivot

In Cycle 4C, an initial forensic correction established that the synthetic 13-patient dataset utilized in Cycle 4B was completely fabricated. However, Cycle 4C introduced its own subtle methodological error: it reported Leave-One-Patient-Out Cross-Validation (LOPO-CV) metrics using freshly trained group means rather than evaluating the fixed coefficients of `MODEL-13`, and it conflated cohort-mean agreement with predictive utility for individual human patients.

This audit establishes three definitive scientific conclusions:
1. **Patient S01 Baseline Measurement:** Patient S01’s baseline force measurement was absent in the published study tables. Replacing this missing datum with a measured zero ($0.0\text{ lb}$) is mathematically and clinically impermissible, as $(0 - 0) / 0$ is an indeterminate operation ($\text{NaN}$), not a measured $0.0\%$ improvement.
2. **Failure Against Non-Physiological Baseline:** In rigorous out-of-sample LOPO-CV, the 3-tier physiological innervation predictor fails to outperform a simple featureless baseline:
   - Simple Cohort-Mean LOPO Baseline: $\text{MAE} = 38.89\text{ percentage points (pp)}$, $\text{RMSE} = \mathbf{46.44\text{ pp}}$.
   - Trained Group-Mean LOPO Predictor: $\text{MAE} = 36.21\text{ pp}$, $\text{RMSE} = \mathbf{48.94\text{ pp}}$.
   - **The complex physiological model produces a higher (worse) RMSE (+2.50 pp) than the zero-feature baseline.**
3. **Complete Case Disqualification:** When evaluating complete cases only (Policy A, $N=12$, excluding S01), the group predictor underperforms the baseline across **both** metrics ($\text{MAE}: 42.91\text{ vs } 39.59\text{ pp}$; $\text{RMSE}: 52.51\text{ vs } 47.11\text{ pp}$).
4. **Epistemic Classification:** Matching the cohort average ($+37.34\%$ vs $+37.3\%$) is a trivial property of any unbiased estimator; it constitutes **zero evidence** of predictive capability for individual patients. `MODEL-13` is formally designated as **`UNVALIDATED_FOR_INDIVIDUAL_PREDICTIONS`**.

---

## 2. Raw Clinical Data & Provenance Analysis (PMC5744714)

### 2.1 Provenance of Innervation Status (Table 4)
The three innervation categories (`DENERVATED`, `PARTIAL`, `INTACT`) were derived from clinical needle electromyography (EMG) and nerve conduction studies reported in Table 4 of Dziki et al. (2016):
- **S01 & S02 (`DENERVATED`):** Needle EMG of the anterior tibial compartment demonstrated complete denervation: fibrillations, positive sharp waves, and "no voluntary motor units recruited". Both patients presented with severe foot drop following peroneal nerve trauma.
- **S03, S04, S05, S06, S11 (`PARTIAL`):** Demonstrated discrete neurogenic recruitment patterns with reduced interference patterns, indicating incomplete motor axon continuity or collateral sprouting.
- **S07, S08, S09, S10, S12, S13 (`INTACT`):** Demonstrated normal voluntary motor unit action potentials (MUAPs) and full recruitment interference in adjacent preserved compartments.

*Critical Scientific Note:* The authors of Dziki et al. (2016) did not propose a 3-tier discrete categorical model ($0\%$, $32\%$, $65\%$). These thresholds were synthesized *post hoc* by the AEGIS modeling team.

### 2.2 Patient S01 Missing Data Audit
In Table 2 of PMC5744714, strength testing was performed using a Biodex System 4 dynamometer. 
- For Patient S01, the pre-operative torque was unrecordable because the patient had $0^\circ$ of voluntary dorsiflexion against gravity and could not register force against the dynamometer pad.
- In Cycle 4C, the data record assigned `baseline_forces_lb: [0.0]` and computed $(0.0 - 0.0) / 0.0 = 0.0\%$.
- Arithmetically, division by zero is undefined. If a patient produces $0\text{ N}$ pre-op and $1\text{ N}$ post-op, their percentage gain is $+\infty\%$. If they produce $0\text{ N}$ pre-op and $0\text{ N}$ post-op, percentage change cannot be computed.
- To resolve this without data fabrication, we define two explicit, reproducible policies:
  - **Policy A (Complete Case Analysis, $N=12$):** Exclude S01 from percentage change calculations, as baseline torque is absent.
  - **Policy B (Conservative Intent-to-Treat, $N=13$):** Retain S01 with baseline torque explicitly tagged as `MISSING` (`None`), assigning an outcome of $0.0\%$ change based on the physical reality that needle EMG at 24 weeks remained completely silent with zero force generation.

---

## 3. Four Comparative Model Architectures

To eliminate confounding between fixed heuristics and data-driven predictors, we evaluate four distinct models:

1. **Model 1: `MODEL-13` Fixed Categorical (Heuristic)**
   - Pre-specified fixed parameters:
     $$\hat{y}_i = \begin{cases} 0.0\% & \text{if DENERVATED} \\ 32.0\% & \text{if PARTIAL} \\ 65.0\% & \text{if INTACT} \end{cases}$$
   - Zero degrees of freedom fitted on the test data; represents the original model hypothesis.

2. **Model 2: Group-Mean LOPO-CV (Separately Trained)**
   - For each held-out patient $i$, the prediction is the empirical mean of their innervation category computed strictly over the remaining $N-1$ training patients:
     $$\hat{y}_i = \frac{1}{|S_{\text{cat}} \setminus \{i\}|} \sum_{j \in S_{\text{cat}} \setminus \{i\}} y_j$$
   - If an innervation category has no remaining training examples, it defaults to the training cohort mean.

3. **Model 3: Independent Baseline (LOPO Cohort-Mean, Zero Physiological Features)**
   - For each held-out patient $i$, the prediction is the unweighted mean of all other $N-1$ patients:
     $$\hat{y}_i = \frac{1}{N-1} \sum_{j \neq i} y_j$$
   - Uses zero anatomical, physiological, surgical, or electromyographic features.

4. **Model 4: Trivial Zero-Prediction Baseline**
   - Assumes acellular biological scaffolds have zero efficacy:
     $$\hat{y}_i = 0.0\% \quad \forall i$$

---

## 4. Patient-by-Patient Ledger & Residuals

The table below details all 13 authentic patients, their raw baseline measurements, observed 24-week outcomes, and predictions across all models under Policy B:

| ID | Anatomical Site | Innervation | Baseline (lb) | Observed $y_i$ (%) | Model 13 Pred (%) | Residual $e_{M13}$ | Group LOPO (%) | Residual $e_{\text{grp}}$ | Baseline LOPO (%) | Residual $e_{\text{base}}$ |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **S01** | Ant. tibial | DENERVATED | **MISSING** | $0.00\%$ | $0.0\%$ | $0.00$ | $0.00\%$ | $0.00$ | $40.45\%$ | $+40.45$ |
| **S02** | Ant. tibial | DENERVATED | $0.0$ | $0.00\%$ | $0.0\%$ | $0.00$ | $0.00\%$ | $0.00$ | $40.45\%$ | $+40.45$ |
| **S03** | Quadriceps | PARTIAL | $6.0$ | $20.00\%$ | $32.0\%$ | $+12.00$ | $46.31\%$ | $+26.31$ | $38.78\%$ | $+18.78$ |
| **S04** | Quadriceps | PARTIAL | $6.1$ | $136.10\%$ | $32.0\%$ | $-104.10$ | $17.28\%$ | $-118.82$ | $29.11\%$ | $-106.99$ |
| **S05** | Ant/lat tibial | PARTIAL | $3.6$ | $33.30\%$ | $32.0\%$ | $-1.30$ | $42.98\%$ | $+9.68$ | $37.67\%$ | $+4.37$ |
| **S06** | Brachialis | PARTIAL | $35.8$ | $-17.90\%$ | $32.0\%$ | $+49.90$ | $55.78\%$ | $+73.68$ | $41.94\%$ | $+59.84$ |
| **S07** | Biceps | INTACT | $40.1$ | $71.50\%$ | $65.0\%$ | $-6.50$ | $41.93\%$ | $-29.57$ | $34.49\%$ | $-37.01$ |
| **S08** | Quadriceps | INTACT | $10.3$ | $64.10\%$ | $65.0\%$ | $+0.90$ | $43.41\%$ | $-20.69$ | $35.11\%$ | $-28.99$ |
| **S09** | Quadriceps | INTACT | $33.3$ | $61.90\%$ | $65.0\%$ | $+3.10$ | $43.85\%$ | $-18.05$ | $35.29\%$ | $-26.61$ |
| **S10** | Rectus fem. | INTACT | $6.6$ | $86.40\%$ | $65.0\%$ | $-21.40$ | $38.95\%$ | $-47.45$ | $33.25\%$ | $-53.15$ |
| **S11** | Biceps/delt. | PARTIAL | $56.6$ | $33.72\%$ | $32.0\%$ | $-1.72$ | $42.88\%$ | $+9.16$ | $37.64\%$ | $+3.92$ |
| **S12** | Sartorius | INTACT | $80.1$ | $-2.30\%$ | $65.0\%$ | $+67.30$ | $56.69\%$ | $+58.99$ | $40.64\%$ | $+42.94$ |
| **S13** | Hamstring | INTACT | $76.4$ | $-1.45\%$ | $65.0\%$ | $+66.45$ | $56.52\%$ | $+57.97$ | $40.57\%$ | $+42.02$ |

---

## 5. Statistical Benchmark Results

### 5.1 Policy B: Full Cohort ($N=13$, S01 Base=Missing, $y=0.0\%$)
- **Observed Cohort Statistics:** $\mu = 37.34\%$, $\sigma = 44.62\%$, $\text{Range} = [-17.90\%, +136.10\%]$.

| Metric | Model 1: Fixed M-13 | Model 2: Group LOPO | Model 3: Baseline LOPO | Model 4: Zero Prediction | Superiority vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | $25.74\text{ pp}$ | $36.21\text{ pp}$ | $38.89\text{ pp}$ | $40.67\text{ pp}$ | Minor ($+2.68\text{ pp}$) |
| **Root Mean Squared Error (RMSE)**| $42.00\text{ pp}$ | $\mathbf{48.94\text{ pp}}$ | $\mathbf{46.44\text{ pp}}$ | $56.85\text{ pp}$ | **FAILS ($-2.50\text{ pp}$ worse)** |
| **Mean Bias Error (MBE)** | $+4.97\text{ pp}$ | $0.00\text{ pp}$ | $0.00\text{ pp}$ | $-37.34\text{ pp}$ | Tied |
| **Max Absolute Error** | $104.10\text{ pp}$ | $118.82\text{ pp}$ | $106.99\text{ pp}$ | $136.10\text{ pp}$ | FAILS ($+11.83\text{ pp}$ worse) |

### 5.2 Policy A: Complete Cases Only ($N=12$, S01 Excluded)
- **Observed Cohort Statistics:** $\mu = 40.45\%$, $\sigma = 45.11\%$, $\text{Range} = [-17.90\%, +136.10\%]$.

| Metric | Model 1: Fixed M-13 | Model 2: Group LOPO | Model 3: Baseline LOPO | Model 4: Zero Prediction | Superiority vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | $27.89\text{ pp}$ | $\mathbf{42.91\text{ pp}}$ | $\mathbf{39.59\text{ pp}}$ | $44.06\text{ pp}$ | **FAILS ($-3.32\text{ pp}$ worse)** |
| **Root Mean Squared Error (RMSE)**| $43.71\text{ pp}$ | $\mathbf{52.51\text{ pp}}$ | $\mathbf{47.11\text{ pp}}$ | $59.17\text{ pp}$ | **FAILS ($-5.40\text{ pp}$ worse)** |
| **Mean Bias Error (MBE)** | $+5.39\text{ pp}$ | $+3.68\text{ pp}$ | $-0.00\text{ pp}$ | $-40.45\text{ pp}$ | Worse bias |

---

## 6. Physiological Dissection: Why Did Group-Mean LOPO Fail?

The failure of the physiological innervation model to beat a featureless baseline on RMSE is rooted in profound clinical biology:

1. **Extreme Intragroup Variance in the `PARTIAL` Class:**
   - Patient S04 (IED blast to quadriceps, pre-op force $6.1\text{ lb}$) achieved $+136.1\%$ strength improvement due to extensive compensatory hypertrophy of surviving motor units.
   - Patient S06 (wakeboarding brachial trauma, pre-op force $35.8\text{ lb}$) suffered a $-17.9\%$ decline due to progressive neuropathic denervation and joint stiffness.
   - When S04 is held out, the remaining partial patients average only $+17.28\%$. The model predicts $+17.28\%$ for S04, generating an error of $|17.28 - 136.10| = 118.82\text{ pp}$. The simple cohort-mean baseline predicts $+29.11\%$, yielding a smaller error ($106.99\text{ pp}$). Because RMSE penalizes large errors quadratically, S04 massively inflates the group model's RMSE.

2. **The Intact Ceiling Effect in Patients S12 & S13:**
   - Both patients had intact motor nerve supply but suffered small injuries ($25-27\%$ deficit) in muscles with high baseline strength ($68-99\text{ lb}$). Both showed zero/negative recovery ($-2.30\%$ and $-1.45\%$).
   - The trained group model predicted $+56.69\%$ and $+56.52\%$ based on the other intact patients, producing massive $58-59\text{ pp}$ errors. The featureless baseline predicted $+40.6\%$, which was closer to the true outcome.

3. **Loss of Sample Support in Complete Case Analysis:**
   - In Policy A, when S01 is removed, Patient S02 is the sole remaining denervated patient. When S02 is held out, the training fold contains **zero** denervated patients, forcing fallback to the global mean and destroying group-specific predictive power.

---

## 7. Forensic Verification & Retraction Ledger

1. **Retraction of Predictive Utility Claims:** Previous claims that `MODEL-13` constitutes a validated individual predictive model for human volumetric muscle loss are formally retracted.
2. **Registration of Negative Finding:** Formally entered into `registry/negative_results.json` as `NEG-0072`.
3. **Mandatory Benchmarking Policy:** In all future AEGIS research cycles, no complex physiological or computational model may be claimed as useful unless it strictly surpasses an independent, featureless baseline on pre-registered holdout metrics (MAE and RMSE).
