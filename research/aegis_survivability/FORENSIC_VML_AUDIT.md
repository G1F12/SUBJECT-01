# Forensic Clinical Audit: Volumetric Muscle Loss (VML)
## Verification of Dziki et al. (2016) Individual Participant Data & Error Metrics
**Program:** AEGIS-01 / Research Cycle 4C  
**Author:** AEGIS Survivability Systems Engineering  
**Primary Source:** Dziki, J. L., et al. (2016). *An acellular biologic scaffold treatment for volumetric muscle loss: results of a 13-patient cohort study.* npj Regenerative Medicine, 1:16008. DOI: `10.1038/npjregenmed.2016.8` (PMC5744714).  
**Date:** 2026-11-09  
**Status:** Canonical Clinical Forensic Audit  

---

## 1. Executive Summary

This forensic audit investigates the clinical validity of the Volumetric Muscle Loss (VML) external validation claim asserted in Cycle 4B.

### Key Forensic Findings:
1. **The Cohort Data in Cycle 4B Was Completely Synthetic:** The `DZIKI_2016_COHORT` array utilized in Cycle 4B was an artificial dataset. Patient injury sites, baseline forces, innervation categories, and 6-month force changes were fabricated to produce an artificial mean of $37.29\%$ and an artificial validation set $\text{MAE} = 5.92\%$.
2. **Patient S12 Falsification:** In Cycle 4B, Patient S12 was declared to have experienced a **$+112.4\%$** strength gain and was labeled an "intact innervation holdout outlier". Direct extraction of PMC5744714 Table 2 proves that **Patient 12 never achieved $+112.4\%$**. In reality, Patient 12 (39-year-old male, sartorius electrocution) exhibited **$-3.5\%$** (hip flexion) and **$-1.1\%$** (knee extension) at 24–28 weeks (mean: **$-2.30\%$**). The number $+112.4\%$ does not appear anywhere in the primary publication.
3. **The 6/4/3 Split Was Fictitious:** The calibration ($N=6$), validation ($N=4$), and holdout ($N=3$) partition was an arbitrary split of synthetic numbers designed to yield a low validation error.
4. **Authentic Performance on Primary Data ($N=13$):** On the actual clinical data from Table 1 and Table 2 of Dziki et al. (2016), the cohort mean improvement is indeed $+37.34\%$, but the standard deviation across patients is **$\pm 44.62\%$** (ranging from $-17.90\%$ to $+136.10\%$).
5. **Real Error Metrics:** When evaluated against authentic clinical outcomes:
   - `MODEL-13` Categorical Innervation Predictor: **$\text{MAE} = 25.74\%$**, **$\text{RMSE} = 42.00\%$**, **$\text{MBE} = +4.97\%$**.
   - Leave-One-Patient-Out Cross-Validation (LOPO-CV): **$\text{MAE} = 36.21\%$**, **$\text{RMSE} = 48.94\%$**, **$\text{MBE} = 0.00\%$**.
6. **Verdict:** **`VALIDATION_VML = PARTIAL`**. The prior unconditional validation claim (`PASS` / $\text{MAE} = 5.92\%$) is **formally revoked (`INV-0017`, `NEG-0056`)**.

---

## 2. Extraction of Primary Clinical Data (PMC5744714)

The primary publication Dziki et al. (2016) was directly retrieved via the NCBI Entrez API from PMC5744714. The cohort consists of 13 patients with chronic VML (mean chronicity: 55.1 months, mean prior surgeries: 10.0, mean initial tissue deficit: $66.2\%$).

### 2.1 Table 1: Patient Demographics and Deficit Characteristics
- Total patients: 13 (11 males, 2 females; mean age $35.8 \pm 10.2$ years).
- Etiologies: IED blast ($n=3$), Motor vehicle accident ($n=3$), Sports/skiing/wakeboarding ($n=4$), Exercise-induced compartment syndrome ($n=1$), Tendon rupture ($n=1$), Electrocution ($n=1$).
- Devices: Acell Matristem (porcine urinary bladder matrix, $n=6$), Cook Biodesign (porcine small intestinal submucosa, $n=5$), Bard XenMatrix (porcine dermal ECM, $n=2$).

### 2.2 Table 2: Force Production Measurements
Strength was evaluated using an isokinetic/isometric dynamometer (Biodex System 4) as percent change from pre-operative maximum isometric torque following ECM implantation and 6 months of physical therapy.

Patients with multi-compartment or multi-axis muscle trauma were tested across **multiple distinct muscle activities**:
- Subject 7: Wrist supination ($+126.2\%$), Biceps flexion ($+16.8\%$) $\to$ Mean: **$+71.50\%$**.
- Subject 11: Shoulder abduction ($+20.1\%$), Shoulder flexion ($+104.1\%$), Shoulder extension ($+46.8\%$), Elbow flexion ($-4.0\%$), Elbow extension ($+1.6\%$) $\to$ Mean: **$+33.72\%$**.
- Subject 12: Hip flexion ($-3.5\%$), Knee extension ($-1.1\%$) $\to$ Mean: **$-2.30\%$**.
- Subject 13: Knee flexion ($-3.4\%$), Knee extension ($+0.5\%$) $\to$ Mean: **$-1.45\%$**.

When each patient's activities are averaged, the 13 individual patient outcomes are:
$$0.0\%,\ 0.0\%,\ 20.0\%,\ 136.1\%,\ 33.3\%,\ -17.9\%,\ 71.5\%,\ 64.1\%,\ 61.9\%,\ 86.4\%,\ 33.72\%,\ -2.3\%,\ -1.45\%$$
The cohort mean across these 13 patients is:
$$\mu = \frac{485.37}{13} = \mathbf{37.34\%} \approx 37.3\%$$
This matches the published average of $37.3\%$ in Table 2 ($P < 0.05$).

---

## 3. Dissection of the Synthetic Data & Origin of +112.4%

### 3.1 Side-by-Side Comparison: Cycle 4B Synthetic vs. Authentic PMC5744714

| Patient | Cycle 4B Fabricated Site | Cycle 4B Synthetic Force | Actual PMC5744714 Anatomical Site | Actual Tested Activity | Actual 24–28w Change (%) | Discrepancy Description |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| **S01** | Anterior Compartment | $-5.2\%$ | Anterior tibial compartment (left) | Dorsiflexion | **$0.0\%$** | Completely denervated; zero contraction |
| **S02** | Anterior Compartment | $+4.1\%$ | Anterior tibial compartment (left) | Dorsiflexion | **$0.0\%$** | Completely denervated; zero contraction |
| **S03** | Anterior Compartment | $+32.5\%$ | Quadriceps (left) | Knee extension | **$+20.0\%$** | Wrong site; synthetic number |
| **S04** | Quadriceps | $+48.0\%$ | Quadriceps (right) | Knee extension | **$+136.1\%$** | Massively understated ($+48\%$ vs $+136.1\%$) |
| **S05** | Quadriceps | $+56.2\%$ | Ant/lat tibial compartment (left) | Dorsiflexion | **$+33.3\%$** | Wrong site; synthetic number |
| **S06** | Hamstrings | $+28.4\%$ | Brachialis (left) | Biceps flexion | **$-17.9\%$** | Wrong site; patient declined in reality |
| **S07** | Hamstrings | $+35.1\%$ | Biceps (right) | Wrist supination / Biceps flex | **$+71.50\%$** | Wrong site; actual mean $+71.5\%$ |
| **S08** | Anterior Compartment | $+42.0\%$ | Quadriceps (left) | Knee extension | **$+64.1\%$** | Wrong site; synthetic number |
| **S09** | Gastrocnemius | $+18.7\%$ | Quadriceps (right) | Knee extension | **$+61.9\%$** | Wrong site; synthetic number |
| **S10** | Gastrocnemius | $+24.3\%$ | Rectus femoris (right) | Knee extension | **$+86.4\%$** | Wrong site; actual gain was $+86.4\%$ |
| **S11** | Brachialis / Biceps | $+68.5\%$ | Biceps/deltoid (left) | 5 shoulder/elbow motions | **$+33.72\%$** | Synthetic aggregate number |
| **S12** | Quadriceps | **$+112.4\%$** | **Sartorius (left)** | **Hip flex / Knee ext** | **$-2.30\%$** | **CATASTROPHIC FABRICATION** |
| **S13** | Hamstrings | $+19.8\%$ | Hamstring (left) | Knee flex / Knee ext | **$-1.45\%$** | Synthetic $+19.8\%$ vs actual $-1.45\%$ |

### 3.2 Where Did "+112.4%" Originate?
1. In the text and tables of PMC5744714, the string `112.4` does not appear anywhere.
2. The maximum values in Table 2 are:
   - Subject 4: $+149.2\%$ at 10–12w, $+136.1\%$ at 24–28w.
   - Subject 7: $+126.2\%$ at 24–28w (wrist supination).
   - Subject 11: $+104.1\%$ at 24–28w (shoulder flexion).
3. The value $+112.4\%$ was a purely synthetic number hallucinated during Cycle 4B when generating an artificial 13-patient vector whose average matched $37.29\%$. The agent assigned this number to Patient 12 and rationalized it as "a young athlete outlier who had intact innervation and did intense physical therapy".
4. In reality, Patient 12 was a 39-year-old male with an electrocution injury to the sartorius who had already undergone 11 previous surgeries. His baseline force was high ($68.1\text{ lb}$ hip flexion, $92.0\text{ lb}$ knee extension), and at 6 months he showed **no functional improvement ($-3.5\%$ and $-1.1\%$)**.

---

## 4. Authentic Model Evaluation & Leave-One-Patient-Out Cross-Validation (LOPO-CV)

Using the authentic data from PMC5744714, we evaluated `MODEL-13`:
- Categorical innervation heuristic:
  - `DENERVATED` $\to 0.0\%$
  - `PARTIAL` $\to 32.0\%$
  - `INTACT` $\to 65.0\%$

### 4.1 Detailed Patient-by-Patient Ledger

| ID | Age / Sex | Anatomical Site | Etiology | Deficit | Innervation | Observed 24w (%) | Model 13 Pred (%) | Residual ($e_i$) | LOPO-CV Pred (%) | LOPO Residual |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **S01** | 34 / M | Anterior tibial (left) | Exercise | $58\%$ | DENERVATED | $0.00\%$ | $0.0\%$ | $0.00\%$ | $0.00\%$ | $0.00\%$ |
| **S02** | 37 / M | Anterior tibial (left) | Skiing | $67\%$ | DENERVATED | $0.00\%$ | $0.0\%$ | $0.00\%$ | $0.00\%$ | $0.00\%$ |
| **S03** | 28 / M | Quadriceps (left) | IED blast | $68\%$ | PARTIAL | $20.00\%$ | $32.0\%$ | $+12.00\%$ | $46.31\%$ | $+26.31\%$ |
| **S04** | 27 / M | Quadriceps (right) | IED blast | $83\%$ | PARTIAL | $136.10\%$ | $32.0\%$ | $-104.10\%$ | $17.28\%$ | $-118.82\%$ |
| **S05** | 32 / M | Ant/lat tibial (left) | Skiing | $90\%$ | PARTIAL | $33.30\%$ | $32.0\%$ | $-1.30\%$ | $42.98\%$ | $+9.68\%$ |
| **S06** | 31 / M | Brachialis (left) | Wakeboard | $90\%$ | PARTIAL | $-17.90\%$ | $32.0\%$ | $+49.90\%$ | $55.78\%$ | $+73.68\%$ |
| **S07** | 31 / M | Biceps (right) | IED blast | $33\%$ | INTACT | $71.50\%$ | $65.0\%$ | $-6.50\%$ | $41.93\%$ | $-29.57\%$ |
| **S08** | 66 / F | Quadriceps (left) | MVA | $50\%$ | INTACT | $64.10\%$ | $65.0\%$ | $+0.90\%$ | $43.41\%$ | $-20.69\%$ |
| **S09** | 35 / M | Quadriceps (right) | MVA | $80\%$ | INTACT | $61.90\%$ | $65.0\%$ | $+3.10\%$ | $43.85\%$ | $-18.05\%$ |
| **S10** | 44 / F | Rectus femoris (right) | Tendon | $52\%$ | INTACT | $86.40\%$ | $65.0\%$ | $-21.40\%$ | $38.95\%$ | $-47.45\%$ |
| **S11** | 31 / M | Biceps/deltoid (left) | MVA | $50\%$ | PARTIAL | $33.72\%$ | $32.0\%$ | $-1.72\%$ | $42.88\%$ | $+9.16\%$ |
| **S12** | 39 / M | Sartorius (left) | Electric | $25\%$ | INTACT | $-2.30\%$ | $65.0\%$ | $+67.30\%$ | $56.69\%$ | $+58.99\%$ |
| **S13** | 30 / M | Hamstring (left) | Sports | $27\%$ | INTACT | $-1.45\%$ | $65.0\%$ | $+66.45\%$ | $56.52\%$ | $+57.97\%$ |

### 4.2 Comprehensive Statistical Ledger

$$\text{MAE} = \frac{1}{N}\sum_{i=1}^N |\hat{y}_i - y_i|, \quad \text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (\hat{y}_i - y_i)^2}, \quad \text{MBE} = \frac{1}{N}\sum_{i=1}^N (\hat{y}_i - y_i)$$

| Metric | Cycle 4B Claimed (Synthetic) | Authentic Primary Data (Model 13) | Authentic Primary Data (LOPO-CV) | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Cohort Sample Size ($N$)** | 13 | 13 | 13 | Full clinical cohort |
| **Cohort Mean Observed** | $37.29\%$ | $\mathbf{37.34\%}$ | $\mathbf{37.34\%}$ | Mean matches published $37.3\%$ |
| **Cohort Standard Deviation** | $\approx 28.5\%$ | $\mathbf{44.62\%}$ | $\mathbf{44.62\%}$ | Huge individual patient variance |
| **Mean Absolute Error (MAE)** | **$10.42\%$** | **$25.74\%$** | **$36.21\%$** | **Actual error is $2.5\times$ to $3.5\times$ higher** |
| **Root Mean Squared Error (RMSE)**| **$15.55\%$** | **$42.00\%$** | **$48.94\%$** | Heavily penalized by S04, S12, S13 |
| **Mean Bias Error (MBE)** | $-2.60\%$ | $+4.97\%$ | $0.00\%$ | Slight overprediction in categorical model |
| **Validation Set MAE** | **$5.92\%$** | **N/A (Fictitious split)** | **$36.21\%$ (LOPO)** | Real generalizability error is $36.21\%$ |

---

## 5. Physiological Insights Revealed by Authentic Data

1. **Denervated Muscle Beds Yield Zero Functional Restoration:**
   - Both Patient S01 and Patient S02 had complete denervation of the anterior compartment on needle EMG (Table 4: "No unit recruited"). Both showed exactly **$0.0\%$ force production change** at 24–28 weeks.
   - This firmly corroborates the physiological principle that acellular ECM scaffolds cannot reconstitute voluntary contractile force without viable host motor axon re-innervation.
2. **The Ceiling Effect in Pre-Existing High-Strength Muscles:**
   - Patients S12 (sartorius, electrocution) and S13 (hamstring, tear) had intact nerve supply, but small volumetric deficits ($25\%$ and $27\%$) and high baseline strength ($68-99\text{ lb}$).
   - Both showed negligible or slightly negative changes ($-2.30\%$ and $-1.45\%$).
   - `MODEL-13` falsely assumed that intact innervation automatically leads to $+65\%$ strength gain. In reality, large percentage gains occur only in severely compromised muscles where physical therapy and neuroplastic reorganization produce compensatory hypertrophy.
3. **Extreme Outlier S04:**
   - Patient S04 (IED blast to quadriceps, $83\%$ deficit, baseline force only $6.1\text{ lb}$) achieved $+136.1\%$ improvement. This massive gain was possible because the baseline was near zero ($6.1\text{ lb} \to 14.4\text{ lb}$).

---

## 6. Regulatory & Epistemic Corrective Actions

1. **`INV-0017` Enacted:** The synthetic dataset `DZIKI_2016_COHORT`, the fabricated $+112.4\%$ value for S12, and the fictitious $6/4/3$ split are permanently invalidated.
2. **`NEG-0056` Recorded:** Formally logged in `registry/negative_results.json`.
3. **Model 13 Update:** `DZIKI_2016_AUTHENTIC_COHORT` in `aegis/external_validation.py` now embeds the exact, immutable data from PMC5744714 Tables 1 and 2.
4. **Validation Status Reclassification:**
   $$\mathbf{VALIDATION\_VML = PARTIAL}$$
   The model correctly predicts the cohort mean ($+37.3\%$) and correctly predicts failure in denervated beds ($0.0\%$), but exhibits $\text{MAE} = 25.74\%$ and $\text{LOPO-CV MAE} = 36.21\%$ across individuals.
