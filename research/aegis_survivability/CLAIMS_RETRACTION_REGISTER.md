# Master Register of Claims Retraction and Epistemic Rectification
**Program:** AEGIS-01 / Research Cycle 4C  
**Author:** AEGIS Survivability Systems Engineering  
**Date:** 2026-11-09  
**Status:** Canonical Scientific Retraction Register  

---

## 1. Regulatory Framework

In accordance with strict scientific integrity and forensic verification standards, no invalid, falsified, circular, or synthetic claim is silently deleted or quietly replaced. 

Every retracted claim is permanently documented in this register, assigned a canonical identifier (`INV-XXXX`), mapped to an entry in the negative results registry (`registry/negative_results.json`), and paired with its forensic cause and scientific replacement.

---

## 2. Cycle 4C Forensic Retractions (Active Review)

### INV-0017: Synthetic Dziki Cohort, Fabricated +112.4% S12 Value, and Fictitious 6/4/3 Split
- **Original Claim (Cycle 4B):** *"Model 13 achieved external validation against Dziki et al. (2016) with MAE = 5.92% on a 4-patient validation split and MAE = 10.42% overall. Patient P12 achieved a +112.4% strength gain and is a holdout outlier."*
- **Forensic Discovery:** Direct retrieval of primary paper PMC5744714 (Tables 1 & 2) proved that the `DZIKI_2016_COHORT` array used in Cycle 4B was an artificial fabrication. Patient 12 (39-year-old male, sartorius electrocution) actually showed **$-3.5\%$** (hip flexion) and **$-1.1\%$** (knee extension) at 24–28 weeks (mean **$-2.30\%$**). The value $+112.4\%$ does not exist in the primary publication.
- **Root Cause:** LLM generation of synthetic records with target mean $37.29\%$ rather than authentic data extraction.
- **Scientific Replacement:** Authentic 13-patient IPD from PMC5744714 with true mean $+37.34 \pm 44.62\%$. Actual `MODEL-13` error is $\text{MAE} = 25.74\%$, $\text{RMSE} = 42.00\%$, and Leave-One-Patient-Out Cross-Validation (LOPO-CV) $\text{MAE} = 36.21\%$.
- **Negative Result ID:** `NEG-0066`.
- **Status:** **PERMANENTLY RETRACTED & FALSIFIED**.

---

### INV-0018: Circular Evaluation of 12 Biomaterials Properties with 0.50% Error
- **Original Claim (Cycle 4B):** *"Model 12 is independently externally validated across 12 mechanical properties with a mean relative error of 0.50% (all 12 within 1-sigma)."*
- **Forensic Discovery:** Code audit revealed that 11 of the 12 properties were hardcoded input constants copied directly into `MODEL-12` dictionaries. The model was evaluated against its own inputs, producing artificial $0.00\%$ error. The claimed $0.50\%$ error was produced by dividing the single real error ($5.96\%$) by 12.
- **Root Cause:** Data leakage (tautology / zero degrees of freedom) masquerading as external validation.
- **Scientific Replacement:** Clean demarcation separating the 11 input constants (`CALIBRATION_VALUE`) from genuine physical predictions. Across 3 genuine derived mechanical predictions (dermis puncture, keratin $K_{1c}$, scalpel incision), real mean relative error is **$9.15\%$** (all within $1\sigma$).
- **Negative Result ID:** `NEG-0067`.
- **Status:** **PERMANENTLY RETRACTED & RECLASSIFIED TO PARTIAL**.

---

### INV-0019: Automatic Assignment of EXTERNALLY_VALIDATED to ISO 7933:2023 Agreement
- **Original Claim (Cycle 4B):** *"Model 14 is EXTERNALLY_VALIDATED against ISO 7933:2023 Predicted Heat Strain with 0.005 K/min warming error."*
- **Forensic Discovery:** ISO 7933:2023 is a normative analytical model, not primary raw human subject data. Concordance between two computer models demonstrates `REFERENCE_MODEL_AGREEMENT`, not biological empirical validation.
- **Root Cause:** Epistemic category error conflating normative engineering model agreement with biological empirical validation.
- **Scientific Replacement:** Implementation of the Three-Tier Framework: Tier 1 (Energy Conservation: residual $< 10^{-12}\text{ W}$), Tier 2 (ISO 7933 Reference Model Agreement: error $0.005\text{ K/min}$), and Tier 3 (Independent Human Validation against Montain et al. 1994 uncompensable heat trials: error $0.0108\text{ K/min}$). Status downgraded to **`PARTIAL`**.
- **Negative Result ID:** Logged under `DEC-0029`.
- **Status:** **SUPERSEDED & DOWNGRADED TO PARTIAL**.

---

### INV-0020: Assertion of Clinical Proof for ARCH-HYBRID as an Integrated Protective System
- **Original Claim (Cycle 4B):** *"ARCH-HYBRID is already clinically proven as an operational protective architecture... High (proven clinically)... ARCH-BIO is eliminated."*
- **Forensic Discovery:** Clinical trials have proven *only* localized dental/orthopedic osseointegration and small-defect ECM patching. Whole-body multi-site biohybrid armor integration has never been tested in vivo. Chronic fatigue, foreign body giant-cell reactions, osteolysis, and ballistic shock transmission remain unquantified.
- **Root Cause:** Over-extrapolation of localized medical implants to systemic whole-body armor architectures.
- **Scientific Replacement:** ARCH-BIO and ARCH-HYBRID are maintained as parallel, active research avenues. ARCH-HYBRID is reclassified as a promising bioengineering hypothesis with **`CONDITIONAL`** feasibility.
- **Negative Result ID:** `NEG-0068`.
- **Status:** **PERMANENTLY RETRACTED (ARCH-HYBRID IS NOT PROVEN)**.

---

## 3. Prior Cycle Retractions (Consolidated Reference)

| Invalidation ID | Original Claim | Forensic Reason for Revocation | Scientific Replacement | Registry Reference |
| :--- | :--- | :--- | :--- | :--- |
| **INV-0013** | 92% force recovery guaranteed in 5 days post-PEG | Completely fictitious; unsupported by any literature | Model assumption: 15–25% rodent twitch force | `NEG-0061` |
| **INV-0014** | V50 analytical formulas prove weapon protection | Recht-Ipson plugging ignores BABT and blunt rupture | Analytical V50 is `EXPLORATORY_UNVALIDATED` | `NEG-0063`, `DEC-0026` |
| **INV-0015** | 78.4% volumetric fill in Dziki 2016 human VML | Never measured in primary publication | Confirmed: $+37.3\%$ force improvement over pre-op | `NEG-0064` |
| **INV-0016** | Arbitrary $\times 0.20$ multiplier in Atkins draw slicing | Ad-hoc fudge factor masking knife vs scalpel geometry | Macro knife wedge ($164.9\text{ N}$) vs razor scalpel ($30.4\text{ N}$) | `FND-0075` |
| **INV-0006** | 91.2% wave attenuation protects from trauma | Acoustic mismatch reflects spallation shock wave | Momentum transfer is conserved; internal organ BABT | `NEG-0036` |
| **INV-0005** | Cancer probability 99.6% vs 6.1% with TP53 copies | False precision derived from uncalibrated power law | Peto's paradox is qualitative biological trend | `NEG-0035` |
| **INV-0003** | Ferguson & O'Kane mathematical scarless index $\ge 2.5$| Formula never existed in original paper | TGF-$\beta 3 / \beta 1$ ratio is qualitative biological regulator | `NEG-0037` |
| **INV-0001** | Kragl et al. (2009) axon regeneration $1-2.2\text{ mm/day}$ | Paper examined axolotl blastema, not axon velocity | Nerve elongation confirmed via Sunderland (1947) | `NEG-0048` |

---

## 4. Summary of Epistemic Status Following Forensic Audit

```
+-----------------------------------------------------------------------------------------+
|                              FINAL VALIDATION STATUS SUMMARY                            |
+-----------------------------------------------------------------------------------------+
| VALIDATION_VML:                     PARTIAL  (Mean confirmed, individual MAE = 25.74%) |
| VALIDATION_MATERIALS:               PARTIAL  (Inputs separated, genuine error = 9.15%) |
| VALIDATION_THERMAL:                 PARTIAL  (Conservation PASS, ISO PASS, Human Lit OK)|
| ARCHITECTURE_BIOLOGICAL_FEASIBILITY: CONDITIONAL (Both BIO and HYBRID active tracks)   |
| CYCLE_5_READY:                      YES      (Forensic foundation established)          |
+-----------------------------------------------------------------------------------------+
```
