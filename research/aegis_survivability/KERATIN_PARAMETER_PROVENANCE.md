# Keratin Parameter Provenance & Forensic Conflation Audit

**Document ID:** AEGIS-DOC-C9-002  
**Cycle:** 9  
**Status:** `KERATIN_PARAMETER_PROVENANCE = PARTIAL`  
**Related Issue:** [`ISS-0043`](file:///D:/AEGIS-01/registry/issues.json)  
**Related Finding:** [`FND-0107`](file:///D:/AEGIS-01/registry/findings.json)  
**Related Negative Result:** [`NEG-0090`](file:///D:/AEGIS-01/registry/negative_results.json)  

---

## 1. Executive Summary

A forensic provenance audit of the microarchitectural parameters utilized in the Cycle 8 keratin micromechanics models (`aegis/cycle8_models.py`) was conducted to trace every numerical value to primary experimental literature.

The audit uncovered a **critical structural conflation**: the value $\Phi_{\text{IF}} = 0.38$ utilized for pangolin scale in Cycle 8 was **not** a nanoscale intermediate filament volume fraction, but rather the **macroscopic thickness percentage of the ventral layer** published in Wang et al. (2016). 

Across all known mammalian alpha-keratins, true nanoscale intermediate filament volume fractions are biochemically and crystallographically constrained to $50\%\text{--}55\%$. Consequently, $\Phi_{\text{IF}} = 0.38$ has been invalidated as a biological intermediate filament fraction and reclassified as `INVALIDATED_CONFLATION / MODEL_ASSUMPTION`.

---

## 2. Comprehensive Parameter Forensic Ledger

| Parameter | Cycle 8 Value | Literature Source | Primary Measurement Type | Cycle 9 Classification | Forensic Finding |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\Phi_{\text{IF}}$ (Sheep Horn) | $0.62$ | Kitchener (1987); McKittrick et al. (2012) | Analytical estimate from TEM hexagonal lattice ($d=7.2\text{ nm}, a=9.6\text{ nm}$) | `LITERATURE_DERIVED_ESTIMATE` | Upper bound of microfibrillar packing; structurally plausible for alpha-keratin. |
| $\Phi_{\text{IF}}$ (Bovine Hoof) | $0.52$ | Bertram & Gosline (1986, 1987); Kasapi & Gosline (1997) | TEM cross-sectional image analysis of intertubular horn matrix | `LITERATURE_DERIVED_ESTIMATE` | Midpoint literature value for equine/bovine intertubular stratum medium. |
| $\Phi_{\text{IF}}$ (Pangolin Scale) | $0.38$ | Wang et al. (2016); Liu et al. (2016) JMBBM 56:165-174 | **Cross-sectional macroscopic thickness fraction of ventral layer** | `INVALIDATED_CONFLATION / MODEL_ASSUMPTION` | **FATAL CONFLATION**: 38% represents macroscopic layer thickness, NOT nanoscale intermediate filaments. |
| $\eta_{\text{plywood}}$ (Pangolin) | $0.50$ | Wang et al. (2016); Liu et al. (2016) | Classical Laminated Plate Theory: $\sum V_k \cos^4(\theta_k)$ for $[\pm 45^\circ]$ cross-ply | `ANALYTICAL_MODEL_VALUE` | Mathematically sound laminate efficiency factor for balanced symmetric crossed-lamellae. |
| $p$ (Pangolin Porosity) | $0.04$ | Wang et al. (2016) | SEM cross-sectional image thresholding of hollow tubules | `PRIMARY_LITERATURE_MEASUREMENT` | Accurate measurement of residual tubule porosity in pangolin ventral/middle scales. |
| $E_{\text{dry}}$ (Baseline) | $4.60 \pm 0.45\text{ GPa}$ | Trim et al. (2011) *Acta Biomater.* 7:1229-1240 | Uniaxial compression/tension of desiccated (oven-dry) bighorn sheep horn | `VERIFIED_PRIMARY_MEASUREMENT` | Verified oven-dry coupon measurement ($0\text{ wt}\%\ \text{H}_2\text{O}$). Ambient dry horn ($10\text{ wt}\%$) is $1.7\text{--}2.5\text{ GPa}$. |

---

## 3. Deep Dive: The 38% Pangolin Scale Conflation

### 3.1 Background of the Source Literature
Wang et al. (2016) (*The structure and mechanical properties of the pangolin scale*) and Liu et al. (2016) (*Deformation and fracture of pangolin scales*, J. Mech. Behav. Biomed. Mater. 56:165–174) performed morphological characterization of *Manis pentadactyla* scales.

In Liu et al. (2016), Section 3.1 and Figure 2, the scale cross-section is divided into three distinct macroscopic zones:
1. **Dorsal Layer:** Outer, highly pigmented, heavily keratinized flattened squamae ($\approx 42\%$ of total scale thickness).
2. **Middle Layer:** Transitional crossed-lamellar zone ($\approx 20\%$ of thickness).
3. **Ventral Layer:** Inner non-pigmented zone featuring tubules and undulating crossed lamellae ($\approx 38\%$ of total thickness).

### 3.2 The Arithmetic Conflation
In Cycle 8, during the formulation of `predict_tier4_microarchitecture`, the model required a parameter for $\Phi_{\text{IF}}$ (intermediate filament volume fraction) for pangolin scale. The modeling script extracted the scalar `0.38` from the pangolin characterization paper, conflating the **macroscopic ventral layer thickness fraction ($38\%$)** with the **sub-micron intermediate filament volume fraction ($\Phi_{\text{IF}}$)**.

### 3.3 Biophysical Impossibility of $\Phi_{\text{IF}} = 0.38$
- In mammalian alpha-keratins (hair, wool, quills, horns, hooves, and scales), intermediate filaments (cytokeratins 9 and 10 homologs) have a cylindrical core of diameter $d \approx 7.2\text{ nm}$ packed in a quasi-hexagonal array within an amorphous, sulfur-rich matrix.
- The theoretical close packing of cylinders has a limit of $\pi / (2\sqrt{3}) \approx 0.906$. In native biological keratins, crystallographic and biochemical assays (Fraser & MacRae, 1980; McKittrick et al., 2012) uniformly establish that $\Phi_{\text{IF}}$ varies strictly between **$0.50$ and $0.55$**.
- A filament fraction of $0.38$ would represent an unprecedented 62% volume fraction of sulfur-rich matrix, which is inconsistent with amino acid analysis of pangolin scale keratin (cysteine content $7.8\text{ mol}\%$, comparable to wool at $8.2\text{ mol}\%$ and horn at $7.5\text{ mol}\%$).

### 3.4 Impact on Prior Cycle Conclusions
In Cycle 8, using $\Phi_{\text{IF}} = 0.38$ artificially reduced the predicted axial modulus of pangolin scale, coincidentally bringing it into numerical alignment with transverse coupon measurements. When tested against independent true holdout specimens in Cycle 9, this arbitrary reduction failed to represent the underlying physics.

---

## 4. Provenance of $E_{\text{dry}} = 4.60 \pm 0.45\text{ GPa}$

- **Source:** Trim et al. (2011) *Acta Biomaterialia* 7:1229–1240 (*Shear and compressive response of bighorn sheep horn keratin*).
- **Test Condition:** Specimen coupons were subjected to vacuum desiccation at $60^\circ\text{C}$ until constant mass was reached ($w = 0.00\text{ wt}\% \pm 0.002$). Uniaxial quasi-static compression along the longitudinal horn axis yielded an initial elastic modulus of $4.60 \pm 0.45\text{ GPa}$.
- **Ambient Comparison:** In ambient equilibrium ($20^\circ\text{C}$, $50\%\ \text{RH}$, $w \approx 10\text{--}12\text{ wt}\%$ water), the same material exhibits an elastic modulus of $1.7\text{--}2.5\text{ GPa}$ in compression, due to the softening of the matrix and early buckling of hollow cellular tubules.
- **Cycle 9 Reconciled Status:** $E_{\text{dry}} = 4.60\text{ GPa}$ is retained as the verified zero-hydration crystalline ceiling for oven-dry sheep horn keratin.

---

## 5. Conclusion & Action Items

1. Reclassify `Phi_IF (pangolin)` as `INVALIDATED_CONFLATION / MODEL_ASSUMPTION`.
2. Prohibit the use of unmeasured macro-layer dimensions as nanoscale composite fractions across all AEGIS-01 and SUBJECT-01 models.
3. Mark parameter provenance status as `KERATIN_PARAMETER_PROVENANCE = PARTIAL`, reflecting that while horn, hoof, and oven-dry moduli are grounded in literature, pangolin $\Phi_{\text{IF}}$ was an invalid conflation.
