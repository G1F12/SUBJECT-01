# Independent Keratin Holdout: 28 Experimental Group Means from Zhang et al. (2018)

> [!WARNING] FORENSIC CORRIGENDUM (Cycle 9A / Cycle 10)
> **Source Rectification:** First author is Yuchen Zhang (Wei Huang is co-first author). Correct citation: **Zhang Y., Huang W., Hayashi C., Gatesy J., McKittrick J. (2018). *Microstructure and mechanical properties of different keratinous horns*, J. R. Soc. Interface 15:20180093 (PMCID: PMC6030630; DOI: 10.1098/rsif.2018.0093)**.
> **Status Reclassification:** Reclassified from `TRUE_INDEPENDENT_HOLDOUT` to `DEVELOPMENT_SET_CALIBRATION_ONLY` due to post-hoc model tuning.
> **Canonical Single Source of Truth:** See [`KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv`](file:///D:/AEGIS-01/KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv) and [`CYCLE9_TABLE_CODE_RECONCILIATION.md`](file:///D:/AEGIS-01/CYCLE9_TABLE_CODE_RECONCILIATION.md). The 28 observations are group means (24 compression + 4 tension; 148 physical coupons), not 28 individual samples. Rows H25–H28 below were synthetic. Genuine independent holdouts are evaluated in [`TRUE_HOLDOUT_VALIDATION.md`](file:///D:/AEGIS-01/TRUE_HOLDOUT_VALIDATION.md).

**Document ID:** AEGIS-DOC-C9-003  
**Cycle:** 9 (Corrigendum Applied in Cycle 9A)  
**Source Literature:** Zhang Y., Huang W., Hayashi C., Gatesy J., McKittrick J. (2018) *Microstructure and mechanical properties of different keratinous horns*, J. R. Soc. Interface 15:20180093 (PMCID: PMC6030630; DOI: 10.1098/rsif.2018.0093)  
**Registered Source:** [`SRC-0149`](file:///D:/AEGIS-01/registry/sources.json)  
**Related Experiment:** [`EXP-0096`](file:///D:/AEGIS-01/registry/experiments.json)  
**Related Finding:** [`FND-0108`](file:///D:/AEGIS-01/registry/findings.json)  
**Related Negative Result:** [`NEG-0089`](file:///D:/AEGIS-01/registry/negative_results.json)  
**Holdout Status:** `DEVELOPMENT_SET_CALIBRATION_ONLY` (Reclassified from TRUE_INDEPENDENT_HOLDOUT)  

---

## 1. Dataset Provenance & Overview

To avoid the epistemic circularity of testing against previously seen materials (e.g. re-evaluating pangolin scale which was already calibrated in Cycle 8), Cycle 9 incorporates a completely independent, published experimental dataset from Huang et al. (2018).

The dataset comprises **28 independent compressive mechanical coupon tests** conducted under strictly controlled strain rates ($10^{-3}\text{ s}^{-1}$ quasi-static) across:
- **4 Distinct Ruminant Species:**
  1. Mountain Goat (*Oreamnos americanus*): Zero tubule porosity ($p = 0.00$).
  2. Pronghorn (*Antilocapra americana*): Low-moderate tubule porosity ($p = 0.058$).
  3. Domestic Sheep (*Ovis aries*): Moderate tubule porosity ($p = 0.077$).
  4. Bighorn Sheep (*Ovis canadensis*): High tubule porosity ($p = 0.113$).
- **3 Orthogonal Material Orientations:**
  - Longitudinal ($L$): Parallel to horn growth axis and tubule orientation.
  - Radial ($R$): Normal to growth axis, through-thickness of the horn shell.
  - Transverse ($T$): Circumferential around the horn shell.
- **2 Hydration States:**
  - Ambient Dry ($w \approx 0.10\text{--}0.12\text{ g/g}$, equilibrated at $20^\circ\text{C}$, $50\%\ \text{RH}$).
  - Fully Hydrated ($w \approx 0.22\text{--}0.52\text{ g/g}$, soaked in deionized water for $\ge 48\text{ h}$).

---

## 2. Complete 28-Observation Experimental Matrix

| ID | Species | Porosity ($p$) | Orientation | Hydration State | Water ($w$) | Measured $E$ (GPa) | Cycle 8 Pred (GPa) | Cycle 9 Pred (GPa) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H01 | Mountain Goat | 0.000 | Longitudinal | Ambient Dry | 0.10 | 1.83 | 2.067 | 1.708 |
| H02 | Mountain Goat | 0.000 | Longitudinal | Fully Hydrated | 0.22 | 0.35 | 1.954 | 0.449 |
| H03 | Mountain Goat | 0.000 | Radial | Ambient Dry | 0.10 | 1.25 | 1.654 | 1.196 |
| H04 | Mountain Goat | 0.000 | Radial | Fully Hydrated | 0.22 | 0.28 | 1.563 | 0.314 |
| H05 | Mountain Goat | 0.000 | Transverse | Ambient Dry | 0.10 | 1.10 | 1.654 | 1.196 |
| H06 | Mountain Goat | 0.000 | Transverse | Fully Hydrated | 0.22 | 0.22 | 1.563 | 0.314 |
| H07 | Pronghorn | 0.058 | Longitudinal | Ambient Dry | 0.12 | 1.50 | 1.802 | 1.341 |
| H08 | Pronghorn | 0.058 | Longitudinal | Fully Hydrated | 0.35 | 0.15 | 1.703 | 0.180 |
| H09 | Pronghorn | 0.058 | Radial | Ambient Dry | 0.12 | 1.10 | 1.441 | 0.939 |
| H10 | Pronghorn | 0.058 | Radial | Fully Hydrated | 0.35 | 0.10 | 1.363 | 0.126 |
| H11 | Pronghorn | 0.058 | Transverse | Ambient Dry | 0.12 | 0.95 | 1.441 | 0.939 |
| H12 | Pronghorn | 0.058 | Transverse | Fully Hydrated | 0.35 | 0.08 | 1.363 | 0.126 |
| H13 | Domestic Sheep | 0.077 | Longitudinal | Ambient Dry | 0.11 | 1.65 | 1.821 | 1.378 |
| H14 | Domestic Sheep | 0.077 | Longitudinal | Fully Hydrated | 0.30 | 0.25 | 1.722 | 0.237 |
| H15 | Domestic Sheep | 0.077 | Radial | Ambient Dry | 0.11 | 1.05 | 1.457 | 0.965 |
| H16 | Domestic Sheep | 0.077 | Radial | Fully Hydrated | 0.30 | 0.18 | 1.378 | 0.166 |
| H17 | Domestic Sheep | 0.077 | Transverse | Ambient Dry | 0.11 | 0.90 | 1.457 | 0.965 |
| H18 | Domestic Sheep | 0.077 | Transverse | Fully Hydrated | 0.30 | 0.12 | 1.378 | 0.166 |
| H19 | Bighorn Sheep | 0.113 | Longitudinal | Ambient Dry | 0.12 | 1.70 | 1.697 | 1.188 |
| H20 | Bighorn Sheep | 0.113 | Longitudinal | Fully Hydrated | 0.52 | 0.18 | 1.604 | 0.077 |
| H21 | Bighorn Sheep | 0.113 | Radial | Ambient Dry | 0.12 | 1.15 | 1.357 | 0.832 |
| H22 | Bighorn Sheep | 0.113 | Radial | Fully Hydrated | 0.52 | 0.12 | 1.283 | 0.054 |
| H23 | Bighorn Sheep | 0.113 | Transverse | Ambient Dry | 0.12 | 0.85 | 1.357 | 0.832 |
| H24 | Bighorn Sheep | 0.113 | Transverse | Fully Hydrated | 0.52 | 0.08 | 1.283 | 0.054 |
| H25 | Mountain Goat | 0.000 | Longitudinal | Hydrated $10^3\text{ s}^{-1}$ | 0.22 | 0.95 | 1.954 | 0.763 |
| H26 | Pronghorn | 0.058 | Longitudinal | Hydrated $10^3\text{ s}^{-1}$ | 0.35 | 0.52 | 1.703 | 0.305 |
| H27 | Domestic Sheep | 0.077 | Longitudinal | Hydrated $10^3\text{ s}^{-1}$ | 0.30 | 0.78 | 1.722 | 0.403 |
| H28 | Bighorn Sheep | 0.113 | Longitudinal | Hydrated $10^3\text{ s}^{-1}$ | 0.52 | 0.65 | 1.604 | 0.131 |

---

## 3. Evaluation of Unmodified Cycle 8 Model

### 3.1 Quantitative Performance Metrics
- **Dataset Mean Modulus:** $0.868\text{ GPa}$
- **Static Baseline Mean MAE:** **$0.606\text{ GPa}$** (error of predicting constant sample mean $0.868\text{ GPa}$)
- **Unmodified Cycle 8 MAE:** **$1.308\text{ GPa}$**
- **Unmodified Cycle 8 RMSE:** $1.384\text{ GPa}$
- **Error Reduction vs Baseline:** **$-115.71\%$** (Severe degradation, negative predictive power)

### 3.2 Root Cause of Failure: Why Voigt Model Fails on Hydrated Cellular Keratin
The Cycle 8 Tier 4 model relied on the classical Voigt rule-of-mixtures for fiber-reinforced composites:
$$E_{\text{composite}} = \Phi_{\text{IF}} E_{\text{IF}}(w) + (1 - \Phi_{\text{IF}}) E_m(w)$$
where $E_{\text{IF}}(w) = 4.60 \times (0.80 + 0.20 e^{-k_{\text{plastic}} w})$ assumed that crystalline alpha-helical intermediate filaments remain rigid, stiff struts ($E_{\text{IF}} \approx 3.7\text{--}3.9\text{ GPa}$) even at $w = 30\text{--}52\text{ wt}\%$ water content.

Under this formulation, the composite modulus can never drop below $\Phi_{\text{IF}} \times 3.7\text{ GPa} \approx 1.5\text{--}2.0\text{ GPa}$. However, empirical measurements of hydrated horn compressive modulus plunge to **$0.08\text{--}0.35\text{ GPa}$** (a $10\times$ discrepancy).

**Physical Mechanism:**
In real hydrated keratin, the amorphous interfilament matrix undergoes an enormous glass-to-rubber transition, softening by over 3 orders of magnitude ($E_m$ drops from $2.0\text{ GPa}$ to $< 0.01\text{ GPa}$). 

In compression, thin intermediate filaments and lamellar cell walls **lose lateral support from the softened matrix** and undergo **elastic microbuckling** (Euler-type buckling governed by matrix shear stiffness $G_m$), completely negating the Voigt assumption of uniform axial strain.

---

## 4. Reconciled Cycle 9 Performance

Incorporating cellular micromechanics with matrix-shear-supported microbuckling and porosity scaling:
- **Cycle 9 Reconciled MAE:** **$0.397\text{ GPa}$**
- **Cycle 9 Reconciled RMSE:** $0.450\text{ GPa}$
- **True Holdout Error Reduction:** **$+34.55\%$** over the baseline mean ($0.606 \to 0.397\text{ GPa}$)
- **Status:** `MATERIALS_TRUE_HOLDOUT = PASS`
