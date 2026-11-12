# AEGIS-01 — TRUE INDEPENDENT HOLDOUT VALIDATION
## Pre-Registered Independent Evaluation of Keratin Micromechanics Across Unseen Datasets

**Document ID:** AEGIS-DOC-C10-VAL-001  
**Cycle:** 10 Independent Research  
**Validation Status:** `TRUE_HOLDOUT_VALIDATED = PASS` (Bovid Horn Domain)  
**Negative Boundary Status:** `CROSS_DOMAIN_HOOF_EXTRAPOLATION = REFUTED`  
**Primary Holdout Source:** Li et al. (2010) *J. Exp. Biol.* 213:479–486 ([`SRC-0150`](file:///D:/AEGIS-01/registry/sources.json))  
**Secondary Holdout Source:** Tombolato et al. (2010) *Acta Biomater.* 6:319–330 ([`SRC-0151`](file:///D:/AEGIS-01/registry/sources.json))  
**Domain Boundary Source:** Bertram & Gosline (1987) *J. Exp. Biol.* 130:121–136 ([`SRC-0152`](file:///D:/AEGIS-01/registry/sources.json))  
**Related Experiment:** [`EXP-0099`](file:///D:/AEGIS-01/registry/experiments.json)  
**Related Findings:** [`FND-0111`](file:///D:/AEGIS-01/registry/findings.json), [`FND-0112`](file:///D:/AEGIS-01/registry/findings.json)  
**Related Negative Result:** [`NEG-0091`](file:///D:/AEGIS-01/registry/negative_results.json)  

---

## 1. Pre-Registration Protocol (Frozen Prior to Evaluation)

To ensure zero post-hoc data leakage, the evaluation protocol, model formulation, parameters, and success criteria were frozen and hashed **before** evaluating unseen datasets.

### 1.1 Frozen Mathematical Formulation
The model predicts Young's modulus ($E$) as a function of hydration weight fraction ($w$), tubule porosity ($p$), orientation angle ($\theta$ in degrees relative to the growth/tubule axis), and mechanical loading mode:
$$E(w, p, \theta, \text{mode}) = E_{\text{solid}}(w) \times (1 - p)^2 \times \left(\cos^4\theta + 0.65\sin^4\theta\right) \times \gamma_{\text{mode}}$$
where:
$$E_{\text{solid}}(w) = E_{\text{solid, wet}} + \frac{E_{\text{solid, dry}} - E_{\text{solid, wet}}}{1 + (w / w_c)^{p_{\text{Hill}}}}$$
and $\gamma_{\text{mode}} = 0.75$ for uniaxial tension, $1.00$ for uniaxial compression, and $0.90$ for flexural bending.

### 1.2 Frozen Parameter Set
- $w_c = 0.18\text{ g/g}$
- $p_{\text{Hill}} = 3.0$
- $E_{\text{solid, dry}} = 3.20\text{ GPa}$
- $E_{\text{solid, wet}} = 0.18\text{ GPa}$
- $\text{Orientation factor} = 0.65$
- $\text{Tension factor} = 0.75$

### 1.3 Cryptographic Integrity Hash
- **Frozen Python Implementation SHA-256 Digest:**
  ```
  225d6994d5b97539f52c1ef5968ee8ac5f96a8b4da37c1e057e983b5f2faea25
  ```

### 1.4 Pre-Registered Evaluation Metric & Success Criterion
- **Metric:** Mean Absolute Error ($\text{MAE}$) and Root Mean Square Error ($\text{RMSE}$) compared to a static naive sample-mean baseline:
  $$\text{MAE}_{\text{baseline}} = \frac{1}{N}\sum_{i=1}^N \left|E_{\text{obs}, i} - \bar{E}_{\text{obs}}\right|$$
  $$\text{Error Reduction} = \frac{\text{MAE}_{\text{baseline}} - \text{MAE}_{\text{model}}}{\text{MAE}_{\text{baseline}}} \times 100\%$$
- **Pre-Registered Success Criterion:**
  $$\text{Error Reduction} > 0\%\quad (\text{Model strictly outperforms naive baseline})$$

---

## 2. Primary True Holdout: Li et al. (2010) Bovine Horn Sheath

### 2.1 Dataset Provenance & Metadata
- **Citation:** Bing-Wei Li, H.-P. Zhao, Xi-Qiao Feng, W.-W. Guo, Sicong Shan (2010). *Experimental study on the mechanical properties of the horn sheaths from cattle*. **Journal of Experimental Biology**, 213(3): 479–486. DOI: [10.1242/jeb.036079](https://doi.org/10.1242/jeb.036079).
- **Species:** Domestic Cattle (*Bos taurus*), Family Bovidae.
- **Microarchitecture:** Layered $\alpha$-keratin lamellae with flattened tubules aligned longitudinally; tubule porosity $p \approx 0.045$.
- **Prior Exposure:** **Zero.** This study was never present in Cycle 1 through Cycle 9.

### 2.2 Blind Quantitative Evaluation

| Specimen ID | Hydration Condition | Water Content ($w$) | Orientation | Mode | Observed $E$ (GPa) | Frozen Model Pred (GPa) | Absolute Error (GPa) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `LI2010-01` | Desiccated / Dry | $0.00$ | Longitudinal ($0^\circ$) | Tension | $2.30 \pm 0.25$ | $2.189$ | $0.111$ |
| `LI2010-02` | Ambient Equilibrium | $0.08$ | Longitudinal ($0^\circ$) | Tension | $1.65 \pm 0.20$ | $2.022$ | $0.372$ |
| `LI2010-03` | Fully Hydrated | $0.19$ | Longitudinal ($0^\circ$) | Tension | $0.85 \pm 0.12$ | $1.072$ | $0.222$ |

### 2.3 Statistical Performance
- **Sample Mean Observed $E$:** $1.600\text{ GPa}$
- **Static Baseline MAE:** **$0.500\text{ GPa}$** (Baseline RMSE: $0.593\text{ GPa}$)
- **Unmodified Cycle 8 Model MAE:** **$1.983\text{ GPa}$** ($-296.6\%$ error reduction; catastrophic failure)
- **Frozen Cycle 9/10 Model MAE:** **$0.235\text{ GPa}$**
- **Frozen Cycle 9/10 Model RMSE:** **$0.258\text{ GPa}$**
- **Error Reduction vs Baseline:** **$+52.95\%$**
- **Holdout Outcome:** **PASS.** The pre-registered model accurately predicted the hydration-dependent softening of bovine horn without any tuning on *Bos taurus*.

---

## 3. Secondary Cross-Study Holdout: Tombolato et al. (2010) Bending Coupons

### 3.1 Dataset Metadata
- **Citation:** Luca Tombolato, Ekaterina E. Novitskaya, Po-Yu Chen, Fred A. Sheppard, Joanna McKittrick (2010). *Microstructure, elastic properties and deformation mechanisms of horn keratin*. **Acta Biomaterialia**, 6(2): 319–330. DOI: [10.1016/j.actbio.2009.08.033](https://doi.org/10.1016/j.actbio.2009.08.033).
- **Species:** Desert Bighorn Sheep (*Ovis canadensis*).
- **Test Type:** Three-point flexural bending coupons (unseen experimental coupon set distinct from Zhang 2018).

### 3.2 Evaluation Results

| Specimen ID | Condition | Water ($w$) | Orientation ($\theta$) | Mode | Observed $E$ (GPa) | Model Pred (GPa) | Absolute Error (GPa) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `TOM2010-DL` | Ambient Dry | $0.10$ | Longitudinal ($0^\circ$) | Bending | $2.15 \pm 0.30$ | $1.953$ | $0.197$ |
| `TOM2010-DT` | Ambient Dry | $0.10$ | Transverse ($90^\circ$) | Bending | $1.25 \pm 0.20$ | $1.269$ | $0.019$ |
| `TOM2010-WL` | Fully Hydrated | $0.40$ | Longitudinal ($0^\circ$) | Bending | $0.22 \pm 0.06$ | $0.306$ | $0.086$ |
| `TOM2010-WT` | Fully Hydrated | $0.40$ | Transverse ($90^\circ$) | Bending | $0.14 \pm 0.04$ | $0.199$ | $0.059$ |

### 3.3 Statistical Performance
- **Sample Mean Observed $E$:** $0.940\text{ GPa}$
- **Static Baseline MAE:** **$0.760\text{ GPa}$**
- **Frozen Model MAE:** **$0.090\text{ GPa}$**
- **Frozen Model RMSE:** **$0.114\text{ GPa}$**
- **Error Reduction vs Baseline:** **$+88.11\%$**
- **Outcome:** **PASS.** Excellent generalizability across independent bending coupon geometries.

---

## 4. Negative Result: Refutation of Equine Hoof Extrapolation

### 4.1 Boundary Evaluation: Bertram & Gosline (1987) Equine Hoof Wall
- **Citation:** J. E. A. Bertram and J. M. Gosline (1987). *Functional design of horse hoof keratin: the modulation of mechanical properties through hydration effects*. **Journal of Experimental Biology**, 130: 121–136.
- **Observed Behavior:**
  - $0\%\text{ RH}$ (Dry): $E_{\text{obs}} \approx 14.6\text{ GPa}$
  - $50\%\text{ RH}$ ($w \approx 0.12$): $E_{\text{obs}} \approx 4.8\text{ GPa}$
  - $75\%\text{ RH}$ ($w \approx 0.18$): $E_{\text{obs}} \approx 2.2\text{ GPa}$
  - $100\%\text{ RH}$ ($w \approx 0.35$): $E_{\text{obs}} \approx 0.41\text{ GPa}$
- **Frozen Horn Model Predictions:**
  - $w = 0.00$: $E_{\text{pred}} \approx 2.40\text{ GPa}$ ($\text{Error} = 12.20\text{ GPa}$, underprediction by $84\%$)
  - $w = 0.12$: $E_{\text{pred}} \approx 1.95\text{ GPa}$ ($\text{Error} = 2.85\text{ GPa}$)
  - $w = 0.18$: $E_{\text{pred}} \approx 1.30\text{ GPa}$ ($\text{Error} = 0.90\text{ GPa}$)
  - $w = 0.35$: $E_{\text{pred}} \approx 0.16\text{ GPa}$ ($\text{Error} = 0.25\text{ GPa}$)
- **Statistical Metric:**
  - $\text{MAE}_{\text{model}} = 4.05\text{ GPa}$ vs $\text{MAE}_{\text{baseline}} = 4.55\text{ GPa}$ (Error Reduction only $+11.0\%$; extreme absolute error in dry state).

### 4.2 Biophysical Mechanism of Failure
Equine hoof wall is not a simple horn sheath:
1. **Higher Solid Packing Density:** Equine hoof wall contains macro-tubules surrounded by specialized dense intertubular keratin with high disulfide crosslink density ($14.6\text{ GPa}$ dry vs $2.3\text{--}3.2\text{ GPa}$ in bovid horn).
2. **Distinct Microfibrillar Architecture:** Horn keratin intermediate filaments are oriented predominantly parallel to the horn curvature, whereas hoof wall keratin exhibits a complex 3D ply where medullary and cortical tubule layers resist ground-reaction impact loads.
- **Formal Negative Result ([`NEG-0091`](file:///D:/AEGIS-01/registry/negative_results.json)):** The bovid horn micromechanics model cannot be transferred to ungulate hoof wall without an explicit recalibration of $E_{\text{solid, dry}}$ to account for tissue-specific macromolecular disulfide crosslink density.

---

## 5. Summary Verdict

```
+-------------------------------------------------------------------------------------------------+
| Dataset & Scope                        | Type                   | Error Reduc. | Final Verdict  |
+-------------------------------------------------------------------------------------------------+
| Li et al. (2010) Bovine Horn Sheath    | True Independent       | +52.95%      | VALIDATED PASS |
| Tombolato et al. (2010) Bighorn Bending| Independent Geometry   | +88.11%      | VALIDATED PASS |
| Bertram & Gosline (1987) Equine Hoof   | Cross-Tissue Domain    | +11.0% (Poor)| REFUTED (NEG)  |
+-------------------------------------------------------------------------------------------------+
```
The Cycle 10 model achieves genuine, pre-registered independent validation across the **bovid horn family**, while establishing a clear, physically grounded domain boundary that excludes equine hoof wall.
