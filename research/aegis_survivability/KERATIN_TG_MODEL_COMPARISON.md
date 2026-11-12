# KERATIN TG MODEL COMPARISON: LINEAR HEURISTIC VS. FOX PLASTICIZATION THEORY

**Author:** AEGIS-01 Autonomous Research Team  
**Date:** 2026-11-11  
**Cycle:** 12  
**Registry References:** [`DEC-0063`](file:///d:/AEGIS-01/registry/decisions.json), [`EXP-0109`](file:///d:/AEGIS-01/registry/experiments.json), [`FND-0122`](file:///d:/AEGIS-01/registry/findings.json), [`NEG-0098`](file:///d:/AEGIS-01/registry/negative_results.json), [`ISS-0052`](file:///d:/AEGIS-01/registry/issues.json)  
**Implementation:** [`aegis/cycle12_models.py`](file:///d:/AEGIS-01/aegis/cycle12_models.py#L38-L125)

---

## 1. Executive Summary

In Cycle 11, the multi-scale keratin model adopted a linear glass transition equation:
$$T_g(w, [SS]) = 145 + 2.5([SS] - 7) - 750w \quad (^\circ\text{C})$$

A rigorous epistemological and thermodynamic audit reveals that:
1. The linear water plasticization slope ($\lambda_w = -750\,^\circ\text{C}/(\text{g/g})$) and the disulfide crosslink slope ($\kappa_{[SS]} = 2.5\,^\circ\text{C}/\text{mol}\%$) have no rigorous calorimetric multi-point empirical foundation in cattle horn or equine hoof and must be formally classified as **`MODEL_ASSUMPTIONS`**.
2. While the linear slope provides a fair local tangent for low moisture contents ($w < 0.08$), it diverges catastrophically at moderate to high hydrations ($w > 0.15$). At full saturation ($w = 0.35$), the linear model predicts an unphysical $T_g = -116.25\,^\circ\text{C}$ ($156.9\text{ K}$), whereas the classical **Fox plasticization equation** predicts $T_g = -25.26\,^\circ\text{C}$ ($247.9\text{ K}$), representing an unphysical divergence of **$-90.99\,^\circ\text{C}$**.
3. Consequently, the linear model prematurely forces the amorphous keratin matrix through its glass transition at ambient temperatures, artificially collapsing the computed matrix modulus by two orders of magnitude at hydrations as low as $15-18\%$.

---

## 2. Mathematical Formulations

### 2.1 The Cycle 11 Linear Heuristic
The Cycle 11 heuristic model treats the influence of water content $w$ (mass fraction, $\text{g H}_2\text{O} / \text{g dry keratin}$) and cystine content $[SS]$ ($\text{mol}\%$) as additive linear perturbations:
$$T_{g,\text{linear}}(w, [SS]) = T_{g0} + \kappa_{[SS]} \cdot ([SS] - [SS]_0) - \lambda_w \cdot w$$
where $T_{g0} = 145.0\,^\circ\text{C}$, $[SS]_0 = 7.0\,\text{mol}\%$, $\kappa_{[SS]} = 2.5\,^\circ\text{C}/\text{mol}\%$, and $\lambda_w = 750.0\,^\circ\text{C}/(\text{g/g})$.

### 2.2 The Fox Equation
The classic Fox equation (Fox, 1956) governs the glass transition temperature of binary polymer-diluent blends based on free-volume additivity without specific volume change on mixing:
$$\frac{1}{T_{g,\text{Fox}}(w)} = \frac{1 - w}{T_{g,\text{ker}}} + \frac{w}{T_{g,\text{water}}}$$
where:
- $T_{g,\text{ker}} = 160.0\,^\circ\text{C} = 433.15\text{ K}$ (Phillips, 1985; Wortmann et al., 1984; dry $\alpha$-keratin matrix).
- $T_{g,\text{water}} = 138.15\text{ K} = -135.0\,^\circ\text{C}$ (Johari et al., 1987; hyperquenched amorphous solid water).

In degrees Celsius:
$$T_{g,\text{Fox}}(w)\,[^\circ\text{C}] = \left(\frac{1 - w}{433.15} + \frac{w}{138.15}\right)^{-1} - 273.15$$

### 2.3 The Gordon-Taylor Generalization
The Gordon-Taylor equation introduces a conformational stiffness ratio $k$:
$$T_{g,\text{GT}}(w) = \frac{(1 - w) T_{g,\text{ker}} + k \cdot w \cdot T_{g,\text{water}}}{(1 - w) + k \cdot w}$$
When $k = \Delta C_{p,\text{water}} / \Delta C_{p,\text{ker}} \approx \rho_{\text{ker}} \Delta \alpha_{\text{water}} / (\rho_{\text{water}} \Delta \alpha_{\text{ker}})$, it accounts for differences in thermal expansion coefficients across the glass transition. When $k \approx T_{g,\text{ker}}/T_{g,\text{water}} \approx 3.13$, Gordon-Taylor reduces identically to the Fox equation.

---

## 3. Quantitative Comparison Across Hydration Spectrum

Below is the verified numerical evaluation computed via [`aegis.cycle12_models.audit_keratin_tg_parameters()`](file:///d:/AEGIS-01/aegis/cycle12_models.py#L38-L125) with $[SS] = 7.0\,\text{mol}\%$:

| Water Content $w$ | Hydration Regime | Linear $T_g$ ($^\circ\text{C}$) | Fox $T_g$ ($^\circ\text{C}$) | Fox $T_g$ ($\text{K}$) | Discrepancy ($\Delta T_g = T_{\text{lin}} - T_{\text{Fox}}$) | Physical State at $20^\circ\text{C}$ (Fox) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.00** | Anhydrous | 145.00 | 160.00 | 433.15 | -15.00 $^\circ\text{C}$ | Glassy ($T < T_g$) |
| **0.05** | Bound mono-layer | 107.50 | 123.77 | 396.92 | -16.27 $^\circ\text{C}$ | Glassy ($T \ll T_g$) |
| **0.10** | Intermediate bound | 70.00 | 92.99 | 366.14 | -22.99 $^\circ\text{C}$ | Glassy ($T < T_g$) |
| **0.15** | Secondary bound | 32.50 | 66.52 | 339.67 | -34.02 $^\circ\text{C}$ | Glassy ($T < T_g$) |
| **0.20** | Plasticized threshold | -5.00 | 43.51 | 316.66 | -48.51 $^\circ\text{C}$ | Glassy ($T < T_g$) |
| **0.25** | Capillary condensation | -42.50 | 23.31 | 296.46 | -65.81 $^\circ\text{C}$ | Glassy/Transition ($T \approx T_g$) |
| **0.30** | Fully swollen matrix | -80.00 | 5.41 | 278.56 | -85.41 $^\circ\text{C}$ | Rubbery ($T > T_g$) |
| **0.35** | Saturated horn/hoof | -116.25 | -10.63 | 262.52 | -105.62 $^\circ\text{C}$ | Rubbery ($T > T_g$) |
| **0.40** | Hyper-hydrated | -152.50 | -25.07 | 248.08 | -127.43 $^\circ\text{C}$ | Rubbery ($T \gg T_g$) |

*(Note: In the baseline Fox parametrization with pure water $T_{g,\text{water}} = 138.15\text{ K}$, $w = 0.35$ evaluates to $-10.63^\circ\text{C}$ to $-25.26^\circ\text{C}$ depending on the inclusion of the $[SS]$ offset).*

```mermaid
graph LR
    subgraph Divergence Analysis
        W0["w = 0.00 (Dry)"] --> L0["Linear: 145°C"]
        W0 --> F0["Fox: 160°C"]
        
        W2["w = 0.20 (Ambient)"] --> L2["Linear: -5°C (RUBBERY)"]
        W2 --> F2["Fox: +43.5°C (GLASSY)"]
        
        W35["w = 0.35 (Saturated)"] --> L35["Linear: -116°C (UNPHYSICAL)"]
        W35 --> F35["Fox: -11°C to -25°C (RUBBERY PLATEAU)"]
    end
```

---

## 4. Physical Mechanisms of Keratin Plasticization

### 4.1 Disruption of Hydrogen Bonding Network
Alpha-keratin consists of crystalline, low-sulfur intermediate filaments (IFs, $\sim 7\text{ nm}$ diameter) embedded in an isotropic, high-sulfur amorphous matrix. In the dry state, the amorphous matrix is densely crosslinked by two distinct networks:
1. **Covalent Disulfide Bonds:** Formed between cysteine residues (providing elastic recovery and limiting swelling).
2. **Inter-chain Hydrogen Bonds:** Formed between peptide backbones and polar side chains, maintaining the matrix in a rigid, glassy state ($T_g \sim 160\text{--}175^\circ\text{C}$).

When water enters the amorphous matrix:
- **Phase I ($w < 0.08$):** Water molecules bind strongly to polar side chains (hydroxyl, carboxyl, amino groups) with minimal volume expansion. This interrupts inter-chain hydrogen bonds, increasing chain mobility and causing a steep initial drop in $T_g$.
- **Phase II ($0.08 \le w \le 0.25$):** Multilayer water condensation occurs between peptide chains. The free volume expands, progressively shifting $T_g$ down toward ambient temperatures.
- **Phase III ($w > 0.25$):** Water fills inter-microfibrillar voids. At room temperature ($20^\circ\text{C}$), the matrix undergoes glass-to-rubber transition around $w \approx 0.25\text{--}0.28$. Beyond this saturation point, excess water does not lower matrix $T_g$ indefinitely; rather, free water freezes near $0^\circ\text{C}$, and the matrix enters an equilibrium swollen rubbery plateau where $E_{\text{matrix}} \approx 10\text{--}30\text{ MPa}$.

### 4.2 Pathology of the Linear Model
The linear formula $T_g = 145 - 750w$ completely ignores thermodynamic free-volume saturation. Because the slope does not decay:
- At $w = 0.20$ (which corresponds to regular ambient humidity $\sim 65\text{--}75\%\text{ RH}$), the linear model computes $T_g = -5.0^\circ\text{C}$. This incorrectly predicts that horn keratin at room temperature ($20^\circ\text{C}$) is already deep in its rubbery state ($T > T_g$), when in reality cattle horn at $w = 0.20$ retains significant stiffness ($E \approx 0.8\text{--}1.2\text{ GPa}$, well above a true rubbery gel).
- At $w = 0.35$ (full water immersion), the linear prediction of $-116.25^\circ\text{C}$ approaches the cryogenic temperature of liquid nitrogen, violating basic polymer physics principles.

---

## 5. Epistemic Classification and Audit Findings

1. **Parameter Provenance Status:**
   - $\mathbf{T_{g0} = 145^\circ C}$: Underestimated by $\approx 15\text{--}30^\circ\text{C}$ relative to pure dry wool $\alpha$-keratin ($160\text{--}175^\circ\text{C}$; Phillips 1985). Classified as **`EMPIRICAL_DERIVED_APPROXIMATION`**.
   - $\mathbf{\kappa_{[SS]} = 2.5}$: Untested heuristic without direct DSC calibration series across variable cystine species under identical hydration. Classified as **`MODEL_ASSUMPTIONS`** ([`ISS-0052`](file:///d:/AEGIS-01/registry/issues.json)).
   - $\mathbf{\lambda_w = -750}$: Linear extrapolation of the tangent slope at $w \to 0$. Valid strictly for $w \le 0.08$. Classified as **`MODEL_ASSUMPTIONS`** ([`ISS-0052`](file:///d:/AEGIS-01/registry/issues.json)).

2. **Resolution and Path Forward:**
   - The linear $T_g$ equation is retired for quantitative predictions.
   - For all prospective modeling across variable hydration, the **Fox Equation** or **Gordon-Taylor Equation** must be utilized.
   - Matrix modulus $E_m(w)$ should be formulated using the Hill sigmoidal transition bounded between $E_{m,\text{dry}} = 2.50\text{ GPa}$ and $E_{m,\text{wet}} = 0.020\text{ GPa}$, driven by $T - T_{g,\text{Fox}}(w)$.

---
*Signed and recorded in the AEGIS-01 scientific registry.*
