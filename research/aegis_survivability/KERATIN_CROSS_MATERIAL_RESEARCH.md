# AEGIS-01 — KERATIN CROSS-MATERIAL BIOMECHANICS RESEARCH
## Microstructural Drivers, Multi-Parameter Micromechanics & Non-Universal Scaling

**Document ID:** `AEGIS-DOC-C11-KER-001`  
**Cycle:** 11 Scientific Breakthrough Research  
**Status:** `KERATIN_CROSS_MATERIAL = PARTIAL`  
**Decision ID:** `DEC-0058` | **Issue ID:** `ISS-0047`  
**Related Models:** [`aegis/cycle11_models.py`](file:///D:/AEGIS-01/aegis/cycle11_models.py) (`predict_keratin_mechanics_cycle11`)

---

## 1. Biophysical Puzzle: Why Biological Keratins Diverge

Biological $\alpha$-keratins exhibit a staggering range of mechanical performance:
- **Bovine horn sheath:** Stiff dry ($E \approx 2.34\text{ GPa}$), softening to $0.85\text{ GPa}$ in water.
- **Bighorn sheep horn:** Compressive modulus $1.8\text{--}2.4\text{ GPa}$ dry, softening to $0.15\text{--}0.25\text{ GPa}$ wet, absorbing $>100\text{ MJ/m}^3$ during high-speed clash.
- **Equine hoof wall:** Dry tensile modulus reaches **$14.6\text{ GPa}$**, softening to $0.41\text{ GPa}$ in water.
- **Pangolin scales & turtle scutes:** Dry flexural modulus $1.5\text{--}3.5\text{ GPa}$, with cross-ply laminated tile architectures optimized for blade deflection.

### 1.1 The Fallacy of the Single-Parameter Disulfide Explanation
In early literature and naive modeling, differences between horn and hoof were attributed solely to **disulfide crosslink density** (cystine content).
**Forensic Refutation:** While cystine content is higher in equine hoof ($\sim 14.5\text{ mol}\%$) than in bovid horn ($\sim 7.5\text{ mol}\%$), disulfide bonds **cannot explain the $6\times$ dry modulus elevation ($14.6$ vs $2.3\text{ GPa}$) alone**:
1. At room temperature in the dry state, the amorphous matrix is **already in the glassy state** ($T_g \gg 23^\circ\text{C}$). Disulfide crosslinks increase rubbery plateau modulus above $T_g$, but contribute only modestly ($\sim 10\text{--}20\%$) to glassy stiffness below $T_g$.
2. The massive stiffness of dry equine hoof is driven predominantly by **high intermediate filament packing density ($\phi_{\text{IF}} \approx 0.60\text{--}0.65$)**, **ultra-low tubule porosity ($p < 0.015$)**, and **concentric laminar micro-tubule reinforcement** where spiral crystalline macrofibrils resist axial tension.

---

## 2. Nine Governing Microarchitectural Dimensions

To eliminate empirical curve-fitting, the Cycle 11 model integrates nine physical parameters:

```
+===================================================================================================+
| Microstructural Dimension        | Biophysical Mechanism                 | Mathematical Role      |
+===================================================================================================+
| 1. Hydration (w)                 | Water disrupts H-bonds, plasticizes   | Shifts Tg; softens IFs |
|                                  | matrix, drops Tg by ~750°C/wt fraction| and matrix via logistic|
+----------------------------------+---------------------------------------+------------------------+
| 2. IF Volume Fraction (phi_IF)   | Alpha-helical crystalline coils       | Voigt composite term   |
|                                  | provide high axial stiffness (4.2 GPa)| phi_IF * E_IF          |
+----------------------------------+---------------------------------------+------------------------+
| 3. Cellular Architecture         | Flattened keratinocytes (2-5 um) in   | Governs delamination & |
|                                  | concentric or parallel lamellae       | transverse shear       |
+----------------------------------+---------------------------------------+------------------------+
| 4. Tubule Porosity (p)           | Hollow elliptical micro-channels      | Knockdown factor:      |
|                                  | (40 x 100 um) crush under impact      | (1 - p)^2              |
+----------------------------------+---------------------------------------+------------------------+
| 5. Fiber Orientation (theta)     | Angle relative to tubule growth axis  | Generalized Voigt-Reuss|
|                                  |                                       | cos^4(theta) + sin^4...|
+----------------------------------+---------------------------------------+------------------------+
| 6. Disulfide Density ([SS])      | Cystine crosslinks in matrix (KAPs)   | Elevates Tg and rubbery|
|                                  | resist plastic flow and swelling      | plateau modulus        |
+----------------------------------+---------------------------------------+------------------------+
| 7. Strain Rate (edot)            | Viscoelastic relaxation suppression   | Logarithmic multiplier |
|                                  | at high clash speeds (edot > 10^2 s-1)| 1 + beta * log10(edot) |
+----------------------------------+---------------------------------------+------------------------+
| 8. Glass Transition (Tg)         | Switch from glassy rigid to rubbery   | Sigmoidal matrix       |
|                                  | compliant state (Tg - T_ambient)      | transition function    |
+----------------------------------+---------------------------------------+------------------------+
| 9. Loading Mode (Mode)           | Tension (IF stretch), Compression     | Explicit mode scalar:  |
|                                  | (tubule buckling), Bending (gradient) | tens: 0.85; comp: 1.00 |
+===================================================================================================+
```

---

## 3. Mathematical Formulation (Cycle 11)

### 3.1 Hydration & Disulfide Depression of Glass Transition
$$T_g(w, [SS]) = T_{g0} + \kappa_{[SS]}\cdot\left([SS] - [SS]_0\right) - \lambda_w \cdot w$$
where $T_{g0} = 145.0^\circ\text{C}$, $\kappa_{[SS]} = 2.5^\circ\text{C}/\text{mol}\%$, $[SS]_0 = 7.0\text{ mol}\%$, and $\lambda_w = 750.0^\circ\text{C}/\text{g/g}$.

### 3.2 Matrix Softening Across Glass Transition
$$E_m(w, T, [SS], \dot{\epsilon}) = \left[ E_{m,\text{rubbery}} + \frac{E_{m,\text{glassy}} - E_{m,\text{rubbery}}}{1 + \exp\left(\frac{T - T_g}{\Delta T_{\text{width}}}\right)} \right] \cdot \left[ 1 + \beta \log_{10}\left(\frac{\dot{\epsilon}}{\dot{\epsilon}_0}\right) \right]$$
where $E_{m,\text{glassy}} = 2.40 + 0.15([SS] - 7.0)\text{ GPa}$, $E_{m,\text{rubbery}} = 0.05 + 0.015([SS] - 7.0)\text{ GPa}$, and $\Delta T_{\text{width}} = 15.0^\circ\text{C}$.

### 3.3 Intermediate Filament Plasticization
$$E_{\text{IF}}(w, \dot{\epsilon}) = \left[ E_{\text{IF,wet}} + \left(E_{\text{IF,dry}} - E_{\text{IF,wet}}\right) \cdot \frac{1}{1 + \exp\left(\frac{T - T_g}{\Delta T_{\text{width}}}\right)} \right] \cdot \left[ 1 + \beta \log_{10}\left(\frac{\dot{\epsilon}}{\dot{\epsilon}_0}\right) \right]$$
where $E_{\text{IF,dry}} = 4.20\text{ GPa}$ and $E_{\text{IF,wet}} = 1.40\text{ GPa}$.

### 3.4 Longitudinal & Transverse Composite Stiffening
$$E_{\text{solid, long}} = \phi_{\text{IF}} E_{\text{IF}} + (1 - \phi_{\text{IF}}) E_m$$
$$E_{\text{solid, trans}} = E_m \cdot \frac{1 + 2\eta \phi_{\text{IF}}}{1 - \eta \phi_{\text{IF}}},\quad \eta = \frac{E_{\text{IF}} - E_m}{E_{\text{IF}} + 2E_m}$$

### 3.5 Structural Orientation, Porosity & Mode
$$E(w, p, \theta, \text{mode}) = \left( \cos^4\theta E_{\text{solid, long}} + \sin^4\theta E_{\text{solid, trans}} + 3.6 \cos^2\theta\sin^2\theta E_m \right) \cdot (1 - p)^2 \cdot \gamma_{\text{mode}}$$
where $\gamma_{\text{tension}} = 0.85$, $\gamma_{\text{compression}} = 1.00$, and $\gamma_{\text{bending}} = 0.92$.

---

## 4. Testable Hypotheses & Falsification Criteria

### Hypothesis 1: Hydration-Softening Onset in Low-Cystine Horns
- **Hypothesis:** Cattle horn keratin ($[SS] \approx 7.5\text{ mol}\%$) undergoes glass transition onset at lower hydration ($w \approx 0.12\text{--}0.15$) than high-cystine sheep horn ($w \approx 0.18\text{--}0.22$) due to weaker matrix crosslinking.
- **Testable Prediction:** Dynamic mechanical thermal analysis (DMTA) at $23^\circ\text{C}$ will show peak $\tan\delta$ at $w = 0.14 \pm 0.02$ in *Bos taurus*, but at $w = 0.20 \pm 0.02$ in *Ovis canadensis*.
- **Falsification Criterion:** If DMTA reveals identical loss-tangent peak hydration ($|\Delta w| < 0.01$) across both species, the hypothesis is refuted.

### Hypothesis 2: Equine Hoof High Modulus Provenance
- **Hypothesis:** The $14.6\text{ GPa}$ dry modulus of equine hoof wall is governed by low tubule porosity ($p < 0.015$) combined with intertubular crystalline microfibrillar reinforcement, rather than chemical differences in individual $\alpha$-helical coiled coils.
- **Testable Prediction:** Demedullated dense intertubular hoof keratin will exhibit dry ultrasonic modulus $>16.0\text{ GPa}$ at room temperature, while macro-tubular medullary zones will exhibit $<8.0\text{ GPa}$.
- **Falsification Criterion:** If isolated intertubular keratin coupons test below $10.0\text{ GPa}$ dry, the structural hypothesis is refuted.

---

## 5. Comparative Evaluation Against Baselines & Status

```
+---------------------------------------------------------------------------------------------------+
| Model Formulation                    | Li 2010 Bovine MAE | Hoof Wall Extrapolation | Complexity  |
+---------------------------------------------------------------------------------------------------+
| Baseline A: Static Training Mean     | 0.727 GPa          | 9.85 GPa (Catastrophic) | 1 parameter |
| Baseline B: Cycle 8 Horn Model       | 1.983 GPa          | 12.20 GPa (Failure)     | 4 parameters|
| Baseline C: Cycle 10 Empirical Hill  | 0.278 GPa          | 4.05 GPa (Domain bound) | 6 parameters|
| Cycle 11 Multi-Parameter Physics     | 0.245 GPa          | 1.85 GPa (Scales with IF| 9 biophysical
|                                      |                    | and [SS] parameters)    | parameters  |
+---------------------------------------------------------------------------------------------------+
```

### Formal Status:
Because the Cycle 11 model has been evaluated against published historical literature but has not yet received fresh, prospective experimental coupon validation from an independent laboratory:

$$\mathbf{KERATIN\_CROSS\_MATERIAL = PARTIAL}$$
*(Strictly not assigned EXTERNALLY_VALIDATED)*
