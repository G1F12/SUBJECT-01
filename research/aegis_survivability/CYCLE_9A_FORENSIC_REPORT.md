# AEGIS-01 — CYCLE 9A FORENSIC AUDIT REPORT
## Critical Evidence Forensic Repair, Provenance Audit & Model Reclassification

**Document ID:** AEGIS-REP-C9A-001  
**Cycle:** 9A (Forensic Audit & Correction)  
**Date:** November 2026  
**Auditor:** AEGIS-01 Autonomous Verification Engine  
**Target Repository:** `D:\AEGIS-01` & `D:\SUBJECT-01`  
**Related Pull Request:** PR #9 (G1F12/SUBJECT-01)  
**Registered Source:** [`SRC-0149`](file:///D:/AEGIS-01/registry/sources.json) (Rectified)  
**Related Issues:** [`ISS-0044`](file:///D:/AEGIS-01/registry/issues.json)  
**Related Decisions:** [`DEC-0055`](file:///D:/AEGIS-01/registry/decisions.json)  

---

## 1. Executive Summary

A comprehensive forensic audit of the **Cycle 9** research deliverables, code implementations, and published validation tables was conducted. The audit revealed five critical structural and epistemic failures that compromised the scientific integrity of the reported results:

1. **Erroneous Bibliographic Citation & Fabricated Author String:** Cycle 9 cited the primary holdout study as `Huang et al. (2018), JRSI 15:20180217`, with co-authors erroneously copied from unrelated literature. The authentic publication is **Zhang Y., Huang W., Hayashi C., Gatesy J., McKittrick J. (2018). *Microstructure and mechanical properties of different keratinous horns*, J. R. Soc. Interface 15:20180093 (PMCID: PMC6030630; DOI: 10.1098/rsif.2018.0093)**.
2. **Fabricated Dynamic Coupon Observations (H25–H28):** The table published in [`INDEPENDENT_KERATIN_HOLDOUT.md`](file:///D:/AEGIS-01/INDEPENDENT_KERATIN_HOLDOUT.md) contained four observations claiming to be hydrated Young's modulus tests at high strain rate ($1000\text{ s}^{-1}$). The primary article by Zhang et al. (2018) contains **zero** high-strain-rate Young's modulus measurements. The drop-weight tests in the paper were exclusively qualitative indentation and energy-absorption tests conducted on domestic and bighorn sheep only.
3. **Severe Arithmetic Decoupling Between Markdown and Executable Code:** The 28-row table in `INDEPENDENT_KERATIN_HOLDOUT.md` was decoupled from the data structure executed in `aegis/cycle9_models.py`. The markdown table yielded a Mean $E = 0.715714\text{ GPa}$, Baseline $\text{MAE} = 0.481429\text{ GPa}$, Cycle 8 $\text{MAE} = 0.868250\text{ GPa}$, and Cycle 9 $\text{MAE} = 0.134571\text{ GPa}$. In stark contrast, the executable code operated on a different 28-item matrix (Mean $E = 0.868214\text{ GPa}$, Baseline $\text{MAE} = 0.606327\text{ GPa}$, Cycle 8 $\text{MAE} = 1.307906\text{ GPa}$, Cycle 9 $\text{MAE} = 0.396863\text{ GPa}$).
4. **Epistemic Holdout Invalidation & Circular Data Leakage:** In Cycle 8, the predictive composite model failed catastrophically on the Zhang 2018 dataset ($\text{MAE} = 1.308\text{ GPa}$ vs Baseline $0.606\text{ GPa}$, $-115.71\%$ error reduction). The Cycle 9 micromechanics model was subsequently engineered and tuned *specifically* against these data. Evaluating Cycle 9 on the identical dataset was therefore a **development/calibration fit**, not an independent holdout validation.
5. **Cohort Conflation & Non-Independent Replication in VML Regeneration:** The 11 VML cohorts from Corona, Greising, and Garg originated from a single collaborative research cluster with shared surgical protocols. Furthermore, leave-one-study-out (LOSO) cross-validation contained hard-coded parameters (`innerv = 0.25`) that leaked information across folds.

This report establishes the forensic truth, ratifies canonical datasets, reconciles all numerical divergence, and reclassifies all evidentiary statuses.

---

## 2. Bibliographic Rectification

### 2.1 Cycle 9 Erroneous Record
In Cycle 9, [`registry/sources.json`](file:///D:/AEGIS-01/registry/sources.json) and markdown files recorded:
```json
{
  "id": "SRC-0149",
  "citation": "Huang W, Zaheri A, Jung JY, Suvannasara V, Naleway SE, Frank NJ, McKittrick J, Espinosa HD (2018). Microstructure and mechanical properties of different keratinous horns. Journal of the Royal Society Interface 15:20180217. DOI: 10.1098/rsif.2018.0217. PMC6030630.",
  "cycle": "Cycle 9"
}
```
**Forensic Findings:**
- The first author is **Yuchen Zhang**, not Wei Huang (Wei Huang is co-first author / second author).
- The author string `Zaheri A, Jung JY, Suvannasara V, Naleway SE, Frank NJ, McKittrick J, Espinosa HD` was imported from an entirely unrelated publication on biological materials (Espinosa lab, Northwestern University).
- The Royal Society Interface article ID was incorrectly cited as `20180217` (which corresponds to an unrelated paper on plant biomechanics) instead of `20180093`.
- The PMCID `PMC6030630` was correct and pointed to the authentic publication.

### 2.2 Rectified Canonical Record
All source registries, models, and test assertions are updated to:
```json
{
  "id": "SRC-0149",
  "citation": "Zhang Y, Huang W, Hayashi C, Gatesy J, McKittrick J (2018). Microstructure and mechanical properties of different keratinous horns. Journal of the Royal Society Interface 15(143):20180093. DOI: 10.1098/rsif.2018.0093. PMCID: PMC6030630.",
  "cycle": "Cycle 9A Forensic Repair",
  "status": "RECTIFIED_PRIMARY_SOURCE"
}
```

---

## 3. Forensic Reconstruction of the Primary Keratin Matrix

### 3.1 Primary Article Experimental Architecture
Inspection of the full text and data tables of Zhang et al. (2018) confirms:
- **Quasi-static Uniaxial Compression Tests:**
  - Standard strain rate: $\dot{\varepsilon} = 1.0 \times 10^{-3}\text{ s}^{-1}$ (crosshead speed $6 \times 10^{-3}\text{ mm/s}$).
  - Specimen dimensions: $6 \times 6 \times 6\text{ mm}$ cubes cut from central horn sheath.
  - Sample size: $n = 5$ independent specimens per experimental group.
  - Groups: 4 species $\times$ 3 orientations (Longitudinal, Radial, Transverse) $\times$ 2 hydration states (Ambient Dry, Fully Hydrated) = **24 compression experimental groups** ($120$ physical specimens tested).
- **Quasi-static Longitudinal Tension Tests:**
  - Standard strain rate: $\dot{\varepsilon} = 1.0 \times 10^{-3}\text{ s}^{-1}$ (crosshead speed $0.001\text{ mm/s}$).
  - Specimen dimensions: $15 \times 3 \times 0.3\text{ mm}$ dogbone coupons, gauge length $10\text{ mm}$.
  - Testing condition: Ambient dry only, longitudinal orientation only.
  - Sample size: $n = 7$ independent specimens per species.
  - Groups: 4 species $\times$ 1 orientation $\times$ 1 hydration = **4 tension experimental groups** ($28$ physical specimens tested).
- **Total Primary Mechanical Groups:** $24 + 4 = \mathbf{28\text{ published group means}}$ representing $148$ individual coupon tests.
- **Drop-Weight Dynamic Tests:**
  - Laboratory apparatus with 1:5 scale of ASTM D7136. Impactor mass $1.2\text{ kg}$, drop height $0\text{--}0.74\text{ m}$.
  - Conducted **only** on domestic sheep and bighorn sheep (pronghorn and mountain goat were excluded due to horn curvature and wall thickness constraints).
  - Measured endpoints: Normalized impact energy ($E_n$), damage modes (dimple, split, delamination, puncture).
  - **No Young's modulus was measured or reported for drop-weight tests.**

### 3.2 Audit of Discrepancies in `INDEPENDENT_KERATIN_HOLDOUT.md`

| Item | Value in `INDEPENDENT_KERATIN_HOLDOUT.md` | Authentic Primary Value in Zhang et al. (2018) | Forensic Assessment |
| :--- | :--- | :--- | :--- |
| **H01 (Mtn Goat Long Dry E)** | $1.83\text{ GPa}$ | $2.10 \pm 0.60\text{ GPa}$ (Table 1) | **CORRUPTED:** Rough estimate or miscopy. |
| **Pronghorn Wet Hydration** | $35\text{ wt}\%$ | $52\text{ wt}\%$ (Table 2) | **CORRUPTED:** Understated water absorption capacity. |
| **Bighorn Wet Hydration** | $52\text{ wt}\%$ | $40\text{ wt}\%$ (Table 2) | **CORRUPTED:** Swapped or misattributed. |
| **Mtn Goat Wet Long E** | $0.35\text{ GPa}$ | $0.50 \pm 0.23\text{ GPa}$ (Table 2) | **CORRUPTED:** Arithmetic discrepancy. |
| **Rows H25–H28** | $1000\text{ s}^{-1}$ Hydrated Young's Modulus | **ABSENT FROM PAPER** (ASTM D7136 drop-weight only) | **FABRICATED / SYNTHETIC:** High-rate modulus was never measured. |
| **Sample Definition** | "28 independent individual specimens" | 28 group means from $148$ physical specimens ($24 \times 5 + 4 \times 7$) | **MISLABELED:** Group averages reported with $\pm \text{SD}$. |

### 3.3 Canonical Reconstruction File
To permanently prevent manual copy-paste errors, the canonical dataset has been compiled into:
[`KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv`](file:///D:/AEGIS-01/KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv)

Every row contains:
- Unique canonical row ID (`ZHANG2018-C01` through `C24` for compression, `T01` through `T04` for tension).
- Common and scientific species names.
- Tubule porosity ($p$) and hydration weight fraction ($w$).
- Loading mode and orientation angle ($\theta$).
- Sample count per group ($n$).
- Measured Young's modulus mean and standard deviation.
- Yield strength and toughness means with standard deviations.
- Explicit source table from Zhang et al. (2018).

---

## 4. Root Cause of Arithmetic Discrepancy

### 4.1 Quantitative Comparison of Reported Metrics

```
+---------------------------------------------------------------------------------------+
| Metric                 | Published Markdown Table | Executable Code (cycle9_models.py)|
+---------------------------------------------------------------------------------------+
| Observed Mean Modulus  | 0.715714 GPa             | 0.868214 GPa                      |
| Baseline MAE (Mean)    | 0.481429 GPa             | 0.606327 GPa                      |
| Cycle 8 Model MAE      | 0.868250 GPa             | 1.307906 GPa                      |
| Cycle 9 Model MAE      | 0.134571 GPa             | 0.396863 GPa                      |
| Cycle 9 Error Reduc.   | +72.05%                  | +34.55%                           |
+---------------------------------------------------------------------------------------+
```

### 4.2 Forensic Diagnosis
The cause of this divergence is **complete dissociation between documentation and code**:
1. The developer wrote a draft markdown table featuring 24 compression rows with hand-entered values plus 4 fabricated dynamic rows (H25–H28).
2. Later, when authoring `aegis/cycle9_models.py`, the developer realized Zhang 2018 had 24 compression groups + 4 tension groups, and entered the exact numbers from Tables 1, 2, and 3 into `HUANG_2018_HOLDOUT_SET`.
3. The executable code was run on `HUANG_2018_HOLDOUT_SET`, producing the values: Mean $0.868\text{ GPa}$, Baseline MAE $0.606\text{ GPa}$, Cycle 8 MAE $1.308\text{ GPa}$, Cycle 9 MAE $0.397\text{ GPa}$.
4. The author copied the summary numbers from the code into Section 3 and Section 4 of `INDEPENDENT_KERATIN_HOLDOUT.md`, **without updating the markdown table in Section 2**.
5. As a consequence, any mathematical audit checking the table in Section 2 derived the erroneous numbers ($0.716\text{ GPa}$, $0.481\text{ GPa}$, $0.135\text{ GPa}$), revealing the mismatch.

---

## 5. Epistemic Reclassification of the Zhang 2018 Dataset

### 5.1 Post-Hoc Parameter Leakage Audit
In Cycle 8, the Voigt rule-of-mixtures composite model was evaluated against the Zhang 2018 dataset and failed catastrophically:
$$\text{MAE}_{\text{Cycle 8}} = 1.308\text{ GPa vs Baseline } 0.606\text{ GPa}\quad (-115.71\%\text{ error reduction})$$

In response, the Cycle 9 model replaced the linear Voigt formulation with a Hill-type sigmoidal softening function:
$$E_{\text{solid}}(w) = E_{\text{solid, wet}} + \frac{E_{\text{solid, dry}} - E_{\text{solid, wet}}}{1 + (w / w_c)^{p_{\text{Hill}}}}$$

The six governing parameters of this model were chosen as follows:
- $E_{\text{solid, dry}} = 3.20\text{ GPa}$: Calibrated directly to match mountain goat dry longitudinal compression ($2.10\text{ GPa}$) and tensile strength ($1.54\text{ GPa}$).
- $E_{\text{solid, wet}} = 0.18\text{ GPa}$: Calibrated directly to match mountain goat wet radial/transverse modulus ($0.14\text{--}0.23\text{ GPa}$).
- $w_c = 0.18$: Positioned at the inflection point of the hydration curve observed across the 4 species in Table 2 ($22\%\text{--}52\%$).
- $p_{\text{Hill}} = 3.0$: Fitted to capture the steepness of the glass-to-rubber transition in horn keratin.
- $\text{Orientation factor} = 0.65$: Calibrated to match the radial-to-longitudinal ratio in Table 1 ($1.50 / 2.10 = 0.71$; $0.90 / 1.80 = 0.50$; mean $\approx 0.65$).
- $\text{Tension factor} = 0.75$: Calibrated to match the dry longitudinal tension-to-compression ratio ($1.54 / 2.10 = 0.73$; $1.06 / 1.80 = 0.59$; $1.33 / 2.00 = 0.66$; $1.15 / 1.70 = 0.68$; mean $\approx 0.67\text{--}0.75$).

### 5.2 Ratification of Evidentiary Status
Because all six parameters were calibrated *after* observing the Zhang 2018 experimental matrix:
- **`CYCLE8_ZHANG2018` = `FAILED_HOLDOUT`**
- **`CYCLE9_ZHANG2018` = `DEVELOPMENT_SET` (Calibration Set)**
- **All parameters are classified as `POST_HOC_CALIBRATED`**
- **The claim `MATERIALS_TRUE_HOLDOUT = PASS` on Zhang 2018 is REVOKED.**
- **True holdout validation requires an untouched, uncalibrated dataset.**

---

## 6. Regeneration Evidence Forensic Audit

### 6.1 Audit of 11 Cohorts
The 11 VML cohorts in `VML_COHORTS_C9` were re-examined:
- **Corona et al. (2015):** 5 cohorts (3 rat TA, 2 pig peroneus tertius; total 36 animals).
- **Greising et al. (2017, 2020):** 4 cohorts (4 rat TA; total 30 animals).
- **Garg et al. (2015):** 2 cohorts (2 rat TA; total 16 animals).
- **Total Animals:** $82$ subjects ($70$ rats, $12$ pigs).

### 6.2 Forensic Vulnerabilities Identified
1. **Cluster Interdependence:** Benjamin Corona and Sarah Greising are frequent co-authors from the same military biomedical research group (US Army ISR). The experimental paradigms, surgical ablations, and torque dynamometers were identical across studies, meaning these do not constitute fully independent international replication.
2. **Dynamic LOSO Leakage:** When leaving out `Greising2017_2020`, cohort G04 is denervated (`innerv = "DENERVATED"`). The training set (`Corona2015` and `Garg2015`) contains no denervated cohorts. The parameter `innerv = 0.25` was hard-coded into the prediction function rather than fitted dynamically from training data.
3. **Preclinical-to-Clinical Translation Barrier:** The rodent ($0.1\text{ cm}^3$) and porcine ($3\text{ cm}^3$) defects cannot be linearly extrapolated to human clinical VML ($50\text{--}100\text{ cm}^3$) due to capillary diffusion distance limits, rapid fibro-adipogenic fibrosis, and human axon regeneration limits ($1\text{ mm/day}$).
- **Status:** Ratified as `PRECLINICAL_REPRODUCED_ONLY`; clinical extrapolation is `REFUTED_WITHOUT_HUMAN_TRIALS`.

---

## 7. Action Items Completed in Cycle 9A

1. Canonical CSV generated: [`KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv`](file:///D:/AEGIS-01/KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv).
2. Erroneous citation `Huang et al. 2018 JRSI 15:20180217` corrected to `Zhang et al. 2018 JRSI 15:20180093` across all registries, source codes, and documentation.
3. Numerical reconciliation completed: Table and executable code aligned on the canonical 28 group means.
4. Epistemic status of Zhang 2018 converted from `TRUE_INDEPENDENT_HOLDOUT` to `DEVELOPMENT_SET`.
5. Pre-registration of an authentic independent holdout dataset (Li et al. 2010 Bovine Horn Sheath) established in Phase 3.
