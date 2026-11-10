# AEGIS-01 — Negative Results Registry & Falsification Ledger
**Research Cycle 6 — Scientific Audit & Hypothesis Falsification**  
**Document ID:** `AEGIS-DOC-C6-NEG-RESULTS`  
**Execution Date:** 2026-11-10  
**Registry Range:** `NEG-0069` through `NEG-0072`

---

## 1. Epistemic Principles of Negative Results in AEGIS-01

In accordance with advanced scientific integrity standards:
- Negative results, model refutations, and failed predictions are permanently recorded in the canonical registry.
- A model is never declared "validated" if it fails to substantially outperform a simple non-physiological baseline.
- Theoretical convenience is never substituted for physical reality.

---

## 2. Cycle 6 Canonical Negative Results Ledger

### 2.1 `NEG-0069`: Failure of 3-Node Dynamic Thermal Model Under Encapsulation
- **Associated Experiment:** `EXP-0073`
- **Falsified Hypothesis:** `HYP-0037` ("A 3-node dynamic thermal model significantly reduces rectal temperature prediction error relative to a 1-node lumped baseline under matched Montain 1994 conditions")
- **Quantitative Finding:**
  - 1-Node Lumped Baseline MAE: $0.02025^\circ\text{C/min}$
  - 3-Node Dynamic Model MAE: $0.01899^\circ\text{C/min}$
  - Error Reduction: **6.2%** (Statistically insignificant relative to observational variance)
- **Scientific Root Cause:** In uncompensable heat stress where sweat evaporation is blocked by protective encapsulation ($I_{\text{cl}} = 1.5\text{ clo}$), the whole body acts as an integrated thermal capacitance. Dynamic blood flow shifts between active muscle and core alter transient core temperature minimally compared to the dominant physical bottleneck of heat dissipation to the environment. Furthermore, clinical rectal thermistor placement introduces a $10\text{--}15\text{ minute}$ response lag that completely obscures fine-grained nodal temperature dynamics.
- **Decision:** In accordance with parsimony principles, the 1-node model is retained as the baseline, and the hypothesis of multi-node superiority under encapsulation without sweat pooling dynamics is rejected.

---

### 2.2 `NEG-0070`: Inability of Acellular ECM Scaffolds Alone to Restore Contractile Force
- **Associated Experiment:** `EXP-0072`
- **Source Evidences:** Greising et al. (2017) (*J Orthop Res* 35:106–114); Corona et al. (2015) (*J Appl Physiol* 118:1115–1126)
- **Quantitative Finding:**
  - Rat Tibialis Anterior, 35% Critical Defect, Untreated: $41.2 \pm 5.1\%$ force recovery
  - Rat Tibialis Anterior, 35% Critical Defect, SIS ECM Scaffold Alone: $43.5 \pm 4.7\%$ force recovery
  - Functional Contractile Difference: **$+2.3\text{ percentage points}$ ($p > 0.05$, statistically indistinguishable)**
- **Scientific Root Cause:** Decellularized porcine extracellular matrix scaffolds lack viable myogenic progenitor cells. In the absence of viable satellite cells and active neuromuscular stimulation, host fibro-adipogenic progenitors (FAPs) infiltrate the scaffold, depositing disordered, non-contractile collagenous scar tissue. The scaffold acts merely as a passive mechanical spacer.
- **Decision:** Permanent revocation of claims that acellular ECM scaffolds alone regenerate functional contractile muscle tissue in critical-size VML defects.

---

### 2.3 `NEG-0071`: Refutation of Zero Metabolic Cost for Biohybrid Armor
- **Associated Experiment:** `EXP-0074`
- **Falsified Hypothesis:** `HYP-0038` ("Indwelling synthetic armor implants operate with zero ongoing metabolic energy or immune maintenance cost")
- **Quantitative Finding:** Obligate continuous metabolic overhead of **$20\text{--}50\text{ kcal/day}$** in humans.
- **Scientific Root Cause:** Host macrophages, dendritic cells, and foreign body giant cells (FBGC) persistently adhere to synthetic abiotic surfaces (titanium, PEEK, UHMWPE). The body maintains a continuous dynamic collagen turnover in the surrounding dense fibrous capsule, secreting inflammatory cytokines ($IL-6$, $TNF-\alpha$). This chronic biological maintenance incurs continuous ATP expenditure and localized vascular remodeling costs.
- **Decision:** All bio-hybrid architecture calculations must include an explicit physiological maintenance tax ($\ge 35\text{ kcal/day}$).

---

### 2.4 `NEG-0072`: Inability to Predict Whole-Body Kinematics Deterministically
- **Associated Experiment:** `EXP-0075`
- **Quantitative Finding:** Deterministic point predictions of running velocity (+14.2%) and acceleration (+18.5%) exhibit uncalibrated residual errors exceeding $\pm 25\%$.
- **Scientific Root Cause:** Locomotion is an emergent property of multi-segment skeletal kinematics, non-linear tendon stretch-shortening dynamics, and motor cortex recruitment patterns. Isolated improvements in muscle isometric torque do not translate linearly into running speed due to limb inertia and stance-time constraints.
- **Decision:** Deterministic kinematic point claims are permanently replaced by bounded interval estimates.

---

## 3. Summary of Hypothesis Falsification in Cycle 6

```
========================================================================================
HYPOTHESIS ID | STATEMENT TITLE                           | VERDICT  | REGISTERED NEGATIVE
========================================================================================
HYP-0034      | Satellite Hayflick Replicative Limit      | DOWNGRADED | Context-dependent
HYP-0037      | Thermal 3-Node Nodal Superiority          | REFUTED  | NEG-0069
HYP-0038      | Zero Metabolic Overhead of Biohybrids     | REFUTED  | NEG-0071
--            | Acellular ECM Alone Restores VML Force    | REFUTED  | NEG-0070
--            | Deterministic Kinematic Point Predictions | REFUTED  | NEG-0072
========================================================================================
```
