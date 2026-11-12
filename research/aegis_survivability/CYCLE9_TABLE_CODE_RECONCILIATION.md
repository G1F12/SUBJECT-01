# AEGIS-01 — CYCLE 9 TABLE & CODE RECONCILIATION
## Forensic Discrepancy Resolution Between Published Markdown and Executable Code

**Document ID:** AEGIS-DOC-C9-REC-001  
**Cycle:** 9A Reconciliation  
**Auditor:** AEGIS-01 Autonomous Verification Engine  
**Canonical Reference Dataset:** [`KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv`](file:///D:/AEGIS-01/KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv)  
**Related Script:** [`aegis/cycle9_models.py`](file:///D:/AEGIS-01/aegis/cycle9_models.py)  

---

## 1. Problem Statement

A major discrepancy was detected between the numbers presented in the summary text of [`INDEPENDENT_KERATIN_HOLDOUT.md`](file:///D:/AEGIS-01/INDEPENDENT_KERATIN_HOLDOUT.md) and the actual numbers derived if one evaluates the 28-row table printed in Section 2 of that document.

### Observed Arithmetic Values:
- **Evaluated from Section 2 Markdown Table:**
  - Mean Observed Modulus: $0.715714\text{ GPa}$
  - Baseline MAE (Mean): $0.481429\text{ GPa}$
  - Cycle 8 Model MAE: $0.868250\text{ GPa}$
  - Cycle 9 Model MAE: $0.134571\text{ GPa}$
- **Evaluated from Executable Code (`aegis/cycle9_models.py`):**
  - Mean Observed Modulus: $0.868214\text{ GPa}$
  - Baseline MAE (Mean): $0.606327\text{ GPa}$
  - Cycle 8 Model MAE: $1.307906\text{ GPa}$
  - Cycle 9 Model MAE: $0.396863\text{ GPa}$

This document establishes the exact row-by-row origin of every divergence, proves how the code was populated, unmasks the synthetic dynamic rows, and enforces automated pipeline reconciliation.

---

## 2. Row-by-Row Comparison & Provenance

The 28 observations in the markdown table (H01–H28) are mapped directly against the 28 objects in `cycle9_models.py` (`HUANG_2018_HOLDOUT_SET`) and the authentic data from **Zhang et al. (2018)** (Tables 1, 2, 3):

| Index | MD ID | MD Species | MD State / Orientation | MD Water ($w$) | MD Obs $E$ | Code Specimen ID | Code State / Mode | Code Water ($w$) | Code Obs $E$ | Primary Paper Authentic Value (Zhang 2018) | Forensic Discrepancy Status |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **00** | H01 | Mtn Goat | Long / Ambient Dry | 0.10 | 1.83 | `GOAT-DRY-LC` | Long / Comp / Dry | 0.10 | 2.10 | $2.10 \pm 0.60\text{ GPa}$ (Table 1) | **CORRUPTED IN MD:** Table 1 is 2.10 GPa; MD wrote 1.83. |
| **01** | H02 | Mtn Goat | Long / Fully Hydrated | 0.22 | 0.35 | `GOAT-DRY-RC` | Radial / Comp / Dry | 0.10 | 1.50 | $1.50 \pm 0.20\text{ GPa}$ (Table 1) | **MISMATCH:** MD placed wet coupon; Code had Dry Radial! |
| **02** | H03 | Mtn Goat | Radial / Ambient Dry | 0.10 | 1.25 | `GOAT-DRY-TC` | Trans / Comp / Dry | 0.10 | 1.40 | $1.40 \pm 0.40\text{ GPa}$ (Table 1) | **MISMATCH:** MD wrote 1.25 GPa; Code had 1.40 GPa. |
| **03** | H04 | Mtn Goat | Radial / Fully Hydrated | 0.22 | 0.28 | `GOAT-DRY-LT` | Long / Tens / Dry | 0.10 | 1.54 | $1.54 \pm 0.20\text{ GPa}$ (Table 3) | **MISMATCH:** MD had wet radial; Code had dry tension! |
| **04** | H05 | Mtn Goat | Trans / Ambient Dry | 0.10 | 1.10 | `GOAT-WET-LC` | Long / Comp / Wet | 0.22 | 0.50 | $0.50 \pm 0.23\text{ GPa}$ (Table 2) | **MISMATCH:** MD dry transverse vs Code wet long. |
| **05** | H06 | Mtn Goat | Trans / Fully Hydrated | 0.22 | 0.22 | `GOAT-WET-RC` | Radial / Comp / Wet | 0.22 | 0.14 | $0.14 \pm 0.03\text{ GPa}$ (Table 2) | **MISMATCH:** MD 0.22 vs Code 0.14 GPa. |
| **06** | H07 | Pronghorn | Long / Ambient Dry | 0.12 | 1.50 | `GOAT-WET-TC` | Trans / Comp / Wet | 0.22 | 0.23 | $0.23 \pm 0.14\text{ GPa}$ (Table 2) | **MISMATCH:** MD pronghorn vs Code goat wet trans. |
| **07** | H08 | Pronghorn | Long / Fully Hydrated | **0.35** | 0.15 | `PRONG-DRY-LC` | Long / Comp / Dry | 0.10 | 1.80 | $1.80 \pm 0.20\text{ GPa}$ (Table 1) | **MISMATCH & HYDRATION ERROR:** MD wrote 35% (Paper is 52%). |
| **08** | H09 | Pronghorn | Radial / Ambient Dry | 0.12 | 1.10 | `PRONG-DRY-RC` | Radial / Comp / Dry | 0.10 | 0.90 | $0.90 \pm 0.30\text{ GPa}$ (Table 1) | **MISMATCH:** MD 1.10 vs Code 0.90 GPa. |
| **09** | H10 | Pronghorn | Radial / Fully Hydrated | **0.35** | 0.10 | `PRONG-DRY-TC` | Trans / Comp / Dry | 0.10 | 1.20 | $1.20 \pm 0.20\text{ GPa}$ (Table 1) | **MISMATCH:** MD wet radial vs Code dry trans. |
| **10** | H11 | Pronghorn | Trans / Ambient Dry | 0.12 | 0.95 | `PRONG-DRY-LT` | Long / Tens / Dry | 0.10 | 1.06 | $1.06 \pm 0.20\text{ GPa}$ (Table 3) | **MISMATCH:** MD dry trans vs Code dry tension. |
| **11** | H12 | Pronghorn | Trans / Fully Hydrated | **0.35** | 0.08 | `PRONG-WET-LC` | Long / Comp / Wet | **0.52** | 0.11 | $0.11 \pm 0.04\text{ GPa}$ (Table 2) | **MISMATCH:** MD w=0.35, E=0.08 vs Code w=0.52, E=0.11. |
| **12** | H13 | Dom Sheep | Long / Ambient Dry | 0.11 | 1.65 | `PRONG-WET-RC` | Radial / Comp / Wet | **0.52** | 0.02 | $0.02 \pm 0.007\text{ GPa}$ (Table 2) | **MISMATCH:** MD sheep vs Code pronghorn wet radial. |
| **13** | H14 | Dom Sheep | Long / Fully Hydrated | 0.30 | 0.25 | `PRONG-WET-TC` | Trans / Comp / Wet | **0.52** | 0.02 | $0.02 \pm 0.003\text{ GPa}$ (Table 2) | **MISMATCH:** MD sheep vs Code pronghorn wet trans. |
| **14** | H15 | Dom Sheep | Radial / Ambient Dry | 0.11 | 1.05 | `DSHEEP-DRY-LC`| Long / Comp / Dry | 0.10 | 2.00 | $2.00 \pm 0.20\text{ GPa}$ (Table 1) | **MISMATCH:** MD radial vs Code long dry sheep. |
| **15** | H16 | Dom Sheep | Radial / Fully Hydrated | 0.30 | 0.18 | `DSHEEP-DRY-RC`| Radial / Comp / Dry | 0.10 | 1.30 | $1.30 \pm 0.50\text{ GPa}$ (Table 1) | **MISMATCH:** MD wet radial vs Code dry radial. |
| **16** | H17 | Dom Sheep | Trans / Ambient Dry | 0.11 | 0.90 | `DSHEEP-DRY-TC`| Trans / Comp / Dry | 0.10 | 0.90 | $0.90 \pm 0.30\text{ GPa}$ (Table 1) | Coincidental numerical match on different condition. |
| **17** | H18 | Dom Sheep | Trans / Fully Hydrated | 0.30 | 0.12 | `DSHEEP-DRY-LT`| Long / Tens / Dry | 0.10 | 1.33 | $1.33 \pm 0.10\text{ GPa}$ (Table 3) | **MISMATCH:** MD wet trans vs Code dry tension. |
| **18** | H19 | Bighorn | Long / Ambient Dry | 0.12 | 1.70 | `DSHEEP-WET-LC`| Long / Comp / Wet | 0.29 | 0.26 | $0.26 \pm 0.13\text{ GPa}$ (Table 2) | **MISMATCH:** MD bighorn dry vs Code sheep wet long. |
| **19** | H20 | Bighorn | Long / Fully Hydrated | **0.52** | 0.18 | `DSHEEP-WET-RC`| Radial / Comp / Wet | 0.29 | 0.11 | $0.11 \pm 0.03\text{ GPa}$ (Table 2) | **MISMATCH:** MD bighorn w=0.52 vs Code sheep w=0.29. |
| **20** | H21 | Bighorn | Radial / Ambient Dry | 0.12 | 1.15 | `DSHEEP-WET-TC`| Trans / Comp / Wet | 0.29 | 0.15 | $0.15 \pm 0.06\text{ GPa}$ (Table 2) | **MISMATCH:** MD dry radial vs Code wet trans sheep. |
| **21** | H22 | Bighorn | Radial / Fully Hydrated | **0.52** | 0.12 | `BSHEEP-DRY-LC`| Long / Comp / Dry | 0.10 | 1.70 | $1.70 \pm 0.50\text{ GPa}$ (Table 1) | **MISMATCH:** MD wet radial vs Code dry long bighorn. |
| **22** | H23 | Bighorn | Trans / Ambient Dry | 0.12 | 0.85 | `BSHEEP-DRY-RC`| Radial / Comp / Dry | 0.10 | 1.20 | $1.20 \pm 0.20\text{ GPa}$ (Table 1) | **MISMATCH:** MD dry trans vs Code dry radial bighorn. |
| **23** | H24 | Bighorn | Trans / Fully Hydrated | **0.52** | 0.08 | `BSHEEP-DRY-TC`| Trans / Comp / Dry | 0.10 | 1.30 | $1.30 \pm 0.60\text{ GPa}$ (Table 1) | **MISMATCH:** MD wet trans vs Code dry trans bighorn. |
| **24** | H25 | Mtn Goat | Long / Hydrated $10^3\text{ s}^{-1}$ | 0.22 | **0.95** | `BSHEEP-DRY-LT`| Long / Tens / Dry | 0.10 | 1.15 | $1.15 \pm 0.10\text{ GPa}$ (Table 3) | **FABRICATED IN MD:** No 1000 s^-1 Young's modulus test in paper. |
| **25** | H26 | Pronghorn | Long / Hydrated $10^3\text{ s}^{-1}$ | 0.35 | **0.52** | `BSHEEP-WET-LC`| Long / Comp / Wet | **0.40** | 0.14 | $0.14 \pm 0.08\text{ GPa}$ (Table 2) | **FABRICATED IN MD:** No 1000 s^-1 test; Code has authentic bighorn wet. |
| **26** | H27 | Dom Sheep | Long / Hydrated $10^3\text{ s}^{-1}$ | 0.30 | **0.78** | `BSHEEP-WET-RC`| Radial / Comp / Wet | **0.40** | 0.09 | $0.09 \pm 0.04\text{ GPa}$ (Table 2) | **FABRICATED IN MD:** No 1000 s^-1 test; Code has authentic bighorn wet. |
| **27** | H28 | Bighorn | Long / Hydrated $10^3\text{ s}^{-1}$ | 0.52 | **0.65** | `BSHEEP-WET-TC`| Trans / Comp / Wet | **0.40** | 0.16 | $0.16 \pm 0.05\text{ GPa}$ (Table 2) | **FABRICATED IN MD:** No 1000 s^-1 test; Code has authentic bighorn wet. |

---

## 3. The Structure of the Code Matrix

Look at the structure in `aegis/cycle9_models.py` (`HUANG_2018_HOLDOUT_SET`):
The code grouped 7 observations per species:
1. Dry Longitudinal Compression (Table 1)
2. Dry Radial Compression (Table 1)
3. Dry Transverse Compression (Table 1)
4. Dry Longitudinal Tension (Table 3)
5. Wet Longitudinal Compression (Table 2)
6. Wet Radial Compression (Table 2)
7. Wet Transverse Compression (Table 2)

Across 4 species ($4 \times 7 = 28$), this encompasses:
- 12 dry compression group means
- 4 dry tension group means
- 12 wet compression group means
Total: **28 authentic group means from Zhang et al. (2018).**

### Why the Markdown Table Was Different:
The markdown author organized the table differently:
- 6 compression rows per species (3 dry, 3 wet) $\times$ 4 species = 24 rows.
- But wanting 28 rows, the author arbitrarily appended 4 dynamic rows H25–H28 labeled "Hydrated $10^3\text{ s}^{-1}$" with synthetic values ($0.95, 0.52, 0.78, 0.65\text{ GPa}$).
- Additionally, the author corrupted hydration values (Pronghorn: 35% vs 52%; Bighorn: 52% vs 40%).
- Finally, the summary text in Section 3 and 4 of `INDEPENDENT_KERATIN_HOLDOUT.md` was copied from the terminal output of `cycle9_models.py`, creating a direct contradiction with the table printed above it!

---

## 4. Remedial Actions and Permanent Policy

1. **Table Deprecation:** The table in `INDEPENDENT_KERATIN_HOLDOUT.md` is deprecated and annotated with this forensic corrigendum.
2. **Canonical Single Source of Truth:** All downstream scripts and tests must load directly from:
   [`KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv`](file:///D:/AEGIS-01/KERATIN_PRIMARY_DATA_RECONSTRUCTION.csv)
3. **No Manual Numerical Tables:** No markdown report may contain manually typed data tables. All tables must be generated programmatically from verified CSV or JSON canonical files.
4. **Automated Continuous Parity Testing:** A regression test [`tests/test_cycle10_models.py`](file:///D:/AEGIS-01/tests/test_cycle10_models.py) validates that the canonical CSV, models, and validation matrix agree to zero tolerance.
