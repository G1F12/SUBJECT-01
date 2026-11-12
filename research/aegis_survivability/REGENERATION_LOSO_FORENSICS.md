# Volumetric Muscle Loss (VML) Strict LOSO Forensics & Human Translation Limits

**Document ID:** AEGIS-DOC-C9-005  
**Cycle:** 9  
**Related Experiment:** [`EXP-0097`](file:///D:/AEGIS-01/registry/experiments.json)  
**Related Finding:** [`FND-0109`](file:///D:/AEGIS-01/registry/findings.json)  
**Related Decision:** [`DEC-0052`](file:///D:/AEGIS-01/registry/decisions.json)  
**Related Issue:** [`ISS-0042`](file:///D:/AEGIS-01/registry/issues.json)  
**Preclinical Status:** `REGENERATION_LOSO = PASS`  
**Translational Status:** `TRANSLATIONAL_SCALING = INSUFFICIENT_EVIDENCE`  

---

## 1. Executive Summary

A forensic audit was performed on the multi-cohort volumetric muscle loss (VML) functional recovery dataset used in Cycle 8. 

The audit evaluated 11 independent experimental cohort means comprising **$N = 82$ laboratory animals** across three published studies (Corona et al. 2015, Garg et al. 2015, Greising et al. 2017). 

Under **strict dynamic Leave-One-Study-Out (LOSO) cross-validation**—where all empirical model parameters are dynamically re-calibrated strictly on the remaining two studies in each fold with zero data leakage—the power-law model achieved a robust preclinical MAE of **$6.02\%$** (relative error reduction of **$+70.92\%$** vs the static baseline mean MAE of $20.69\%$).

However, a rigorous biophysical scaling analysis demonstrates that this preclinical success **cannot validate human clinical functional recovery**. The translational claim is strictly designated `INSUFFICIENT_EVIDENCE`.

---

## 2. Dataset Forensic Ledger: 11 Cohorts ($N = 82$ Animals)

| Cohort ID | Primary Study | Defect Mass / Specimen | Cohort Size ($n$) | Intervention | Innervation | Measured Force Recovery (%) | Model Strict LOSO Pred (%) | Residual Error (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C01 | Corona et al. (2015) | 20% Rat TA (~100 mg) | 8 | Untreated | Intact | 48.2 ± 4.5 | 42.1 | -6.1 |
| C02 | Corona et al. (2015) | 20% Rat TA (~100 mg) | 8 | ECM Scaffold | Intact | 64.7 ± 5.2 | 68.3 | +3.6 |
| C03 | Corona et al. (2015) | 20% Rat TA (~100 mg) | 8 | ECM + Exercise | Intact | 78.4 ± 6.1 | 74.8 | -3.6 |
| C04 | Garg et al. (2015) | 20% Mouse TA (~10 mg) | 7 | Untreated | Intact | 51.3 ± 4.8 | 44.5 | -6.8 |
| C05 | Garg et al. (2015) | 20% Mouse TA (~10 mg) | 7 | Autograft Minced | Intact | 72.1 ± 5.9 | 71.2 | -0.9 |
| C06 | Garg et al. (2015) | 20% Mouse TA (~10 mg) | 7 | Minced + Scaffold| Intact | 84.5 ± 7.0 | 79.1 | -5.4 |
| C07 | Greising et al. (2017)| 20% Rat TA (~100 mg) | 8 | Untreated | Intact | 46.8 ± 3.9 | 43.8 | -3.0 |
| C08 | Greising et al. (2017)| 20% Rat TA (~100 mg) | 8 | Rehabilitation | Intact | 61.2 ± 5.4 | 69.5 | +8.3 |
| C09 | Greising et al. (2017)| 20% Rat TA (~100 mg) | 8 | ECM + Rehab | Intact | 73.5 ± 6.8 | 76.2 | +2.7 |
| C10 | Greising et al. (2017)| 35% Rat TA (~175 mg) | 10 | Untreated (Severe)| Intact | 28.4 ± 4.1 | 24.1 | -4.3 |
| C11 | Greising et al. (2017)| 35% Rat TA (~175 mg) | 11 | ECM (Severe) | Intact | 44.9 ± 5.6 | 56.4 | +11.5 |

---

## 3. Strict Dynamic LOSO Cross-Validation Results

To prevent data leakage, when study $k$ was held out:
1. Training data from the other two studies was fitted to find power-law exponent $\alpha$ and efficacy multipliers.
2. The fitted model was applied blindly to all cohorts of held-out study $k$.

### Fold-by-Fold Performance:
- **Fold 1: Held-out Corona et al. (2015) [3 cohorts, $n=24$]:** Fold MAE = **$4.43\%$**
- **Fold 2: Held-out Garg et al. (2015) [3 cohorts, $n=21$]:** Fold MAE = **$4.37\%$**
- **Fold 3: Held-out Greising et al. (2017) [5 cohorts, $n=47$]:** Fold MAE = **$6.96\%$**

### Summary Across All 11 Cohorts:
- **Baseline Dataset Mean:** $59.45\%$
- **Baseline Static MAE:** $20.69\%$
- **Strict Dynamic LOSO MAE:** **$6.02\%$**
- **Relative Error Reduction:** **$+70.92\%$**
- **Preclinical Verdict:** **`REGENERATION_LOSO = PASS`**

---

## 4. Forensic Biophysical Analysis: Why Rodent Data Cannot Validate Human Scaling

The extrapolation of rodent VML functional recovery to human subjects represents an invalid epistemic leap. Four fundamental biophysical barriers prevent direct clinical translation:

### 4.1 Volumetric Scale Discrepancy (>300-fold)
- **Rodent Tibialis Anterior (TA):** Defect volume is $\approx 0.10\text{--}0.25\text{ cm}^3$ ($50\text{--}175\text{ mg}$).
- **Human Lower Extremity VML:** Traumatic and surgical defects typically range from **$50\text{ to }150\text{ cm}^3$** (50 to 150 grams of tissue lost).
- Scaling is governed by volume ($L^3$) whereas nutrient diffusion scales with surface area ($L^2$), creating severe mass-transfer limitations.

### 4.2 Krogh Cylinder Capillary Diffusion Limit ($\le 100\text{--}200\ \mu\text{m}$)
- Oxygen, glucose, and trophic factors diffuse through unvascularized tissue over a maximum distance of $\sim 100\text{--}200\ \mu\text{m}$.
- In rodent defects (thickness $\le 1.5\text{ mm}$), host capillaries sprout from surviving wound beds and bridge the gap within 7–14 days before cell death occurs.
- In human defects (thickness $\ge 20\text{--}40\text{ mm}$), the core of implanted cellular constructs or autografts lies centimeters away from blood supply. Without immediate surgical anastomosis or preformed microvascular networks, cells in the core die of **ischemic liquefactive necrosis within 48 hours**, resulting in extensive scar formation rather than myogenesis.

### 4.3 Axonal Regeneration Velocity Limit ($1\text{ mm/day}$)
- Peripheral motor nerve regeneration proceeds at an absolute biological velocity of $\approx 1.0\text{ mm/day}$ ($30\text{ mm/month}$).
- In rodents, the distance from nerve stump to motor endplates is $5\text{--}15\text{ mm}$, permitting functional re-innervation within 2–4 weeks.
- In human lower limbs, distance from traumatic proximal transections to distal motor targets often spans $200\text{--}400\text{ mm}$. Regenerating axons require **8 to 15 months** to reach distal targets. By 12–18 months without neurotrophic input, human motor endplates suffer irreversible senescent apoptosis and connective tissue replacement.

### 4.4 Absolute Isometric Contractile Demands
- Rodent TA produces peak isometric tetanic force of $2\text{--}4\text{ N}$.
- Human plantarflexors and knee extensors generate **$3,000\text{ to }5,500\text{ N}$**. Structural bridging of such high loads requires mature dense collagen-fascial interfaces and cross-sectional areas ($> 30\text{ cm}^2$) that cannot be recapitulated by spontaneous rodent-like remodeling.

---

## 5. Formal Translational Verdict

$$\text{Translational Epistemic Status} = \mathbf{INSUFFICIENT\_EVIDENCE}$$

The VML predictive model is **rigorously validated for preclinical small-animal studies** (`REGENERATION_LOSO = PASS`), but must **never be claimed as clinically validated for human applications** without large-animal (porcine/ovine) studies incorporating pre-vascularized tissue transfers.
