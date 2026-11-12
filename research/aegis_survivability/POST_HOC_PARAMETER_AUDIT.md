# AEGIS-01 — POST-HOC PARAMETER AUDIT & DATA LEAKAGE ANALYSIS
## Reclassification of Cycle 9 Keratin Micromechanics Parameters

**Document ID:** AEGIS-DOC-C9-AUD-002  
**Cycle:** 9A Forensic Audit  
**Auditor:** AEGIS-01 Autonomous Verification Engine  
**Related Code:** [`aegis/cycle9_models.py`](file:///D:/AEGIS-01/aegis/cycle9_models.py) (`predict_cycle9_reconciled`)  
**Canonical Status:** `DATA_LEAKAGE_RESOLVED` / `PARAMETERS_POST_HOC_CALIBRATED`  

---

## 1. Overview of the Epistemic Failure

In scientific machine learning and computational mechanics, an evaluation dataset can be classified as a **True Independent Holdout** only if:
1. No parameter in the model was calibrated, adjusted, or optimized using the dataset.
2. The functional form of the model was not altered as a consequence of inspecting the dataset.
3. The evaluation code and hypothesis were pre-registered before test data exposure.

In Cycle 8 and Cycle 9, this protocol was violated:
- **Cycle 8:** The unmodified Tier 4 composite model (Voigt rule-of-mixtures) was evaluated on the 28-group dataset of Zhang et al. (2018). It produced an $\text{MAE} = 1.308\text{ GPa}$, which was **worse than the naive sample mean baseline** ($\text{MAE} = 0.606\text{ GPa}$), representing an error reduction of **$-115.71\%$**.
- **Cycle 9:** The model architecture was completely restructured from linear Voigt composite theory to a nonlinear sigmoidal Hill microbuckling softening function. Six specific numeric parameters were introduced and fitted directly to minimize residuals on the Zhang 2018 data.
- **The Consequence:** Evaluating Cycle 9 on Zhang 2018 yielded an $\text{MAE} = 0.397\text{ GPa}$ ($+34.55\%$ error reduction). Cycle 9 reported this as `MATERIALS_TRUE_HOLDOUT = PASS`. This was epistemically invalid: the dataset was no longer a holdout, but the **development/training set** used to derive the model.

---

## 2. Parameter-by-Parameter Forensic Provenance

| Parameter Name | Cycle 9 Value | Calibrated Against | Mechanism of Leakage / Fitting | Forensic Epistemic Classification |
| :--- | :---: | :--- | :--- | :--- |
| **$w_c$ (Critical Hydration)** | $0.18$ | Zhang 2018 Table 2 (water contents $22\%\text{--}52\%$) | Chosen at the inflection point where compressive modulus collapses by $>85\%$. Not derived from independent calorimetry or DSC glass transition data. | `POST_HOC_CALIBRATED` |
| **$p_{\text{Hill}}$ (Hill Exponent)** | $3.0$ | Zhang 2018 Table 1 vs Table 2 transition slope | Tuned to fit the steep drop between ambient dry ($10\%\text{--}12\%$) and hydrated ($22\%\text{--}52\%$) horn stiffness. | `POST_HOC_CALIBRATED` |
| **$E_{\text{solid, dry}}$** | $3.20\text{ GPa}$ | Zhang 2018 Mountain Goat dry longitudinal compression ($2.10\text{ GPa}$) & tension ($1.54\text{ GPa}$) | Solved to match the unporous ($p=0$) dry mountain goat horn sheath modulus. | `POST_HOC_CALIBRATED` |
| **$E_{\text{solid, wet}}$** | $0.18\text{ GPa}$ | Zhang 2018 Mountain Goat wet transverse/radial modulus ($0.14\text{--}0.23\text{ GPa}$) | Solved to match the asymptotic plateau of fully softened mountain goat keratin. | `POST_HOC_CALIBRATED` |
| **$\text{Orientation Factor}$** | $0.65$ | Zhang 2018 Table 1 Radial/Transverse vs Longitudinal ratios | Calculated directly from the ratio: $\frac{E_{\text{rad}} + E_{\text{trans}}}{2 E_{\text{long}}} \approx 0.65$ across dry horns. | `POST_HOC_CALIBRATED` |
| **$\text{Tension Factor}$** | $0.75$ | Zhang 2018 Table 3 Tensile vs Table 1 Compressive longitudinal modulus | Calculated directly from the ratio: $\frac{E_{\text{tensile}}}{E_{\text{comp}}} \approx \frac{1.54}{2.10} = 0.73$ (Goat), $\frac{1.33}{2.00} = 0.66$ (Sheep), $\frac{1.15}{1.70} = 0.68$ (Bighorn). Set to $0.75$. | `POST_HOC_CALIBRATED` |

---

## 3. Epistemic Ratification Matrix

To restore scientific integrity, the evidentiary ledger is formally updated:

```
+---------------------------------------------------------------------------------------+
| Experiment / Evaluation           | Previous Claim (C9)    | Rectified Status (C9A/C10)|
+---------------------------------------------------------------------------------------+
| CYCLE8_ZHANG2018                  | TRUE_HOLDOUT_FAIL      | FAILED_HOLDOUT (Confirmed)|
| CYCLE9_ZHANG2018                  | TRUE_HOLDOUT_PASS      | DEVELOPMENT_SET_FIT       |
| MATERIALS_TRUE_HOLDOUT (General)  | PASS                   | PENDING_NEW_DATASET       |
| Parameter Classification (All 6)  | THEORETICAL_DERIVATION | POST_HOC_CALIBRATED       |
+---------------------------------------------------------------------------------------+
```

### Formal Decision Statement
1. The status `MATERIALS_TRUE_HOLDOUT = PASS` is **REVOKED**.
2. Zhang et al. (2018) is reclassified as a **development and parameter calibration dataset**.
3. A true holdout evaluation is required, using an independent published experimental dataset that was completely unseen during both Cycle 8 and Cycle 9 parameter tuning.
