# AEGIS-01 — TOMBOLATO ET AL. (2010) VALIDATION AUDIT
## Primary Provenance Verification, Mode Conflation Analysis & Parameter Leakage Audit

**Document ID:** `AEGIS-DOC-C10B-TOM-001`  
**Cycle:** 10B Forensic Audit  
**Status:** `TOMBOLATO2010_HOLDOUT = NOT_VERIFIED`  
**Decision ID:** `DEC-0056` | **Issue ID:** `ISS-0045`  
**Primary Source Citation:** Luca Tombolato, Ekaterina E. Novitskaya, Po-Yu Chen, Fred A. Sheppard, Joanna McKittrick (2010). *Microstructure, elastic properties and deformation mechanisms of horn keratin*. **Acta Biomaterialia**, 6(2): 319–330. DOI: [10.1016/j.actbio.2009.06.033](https://doi.org/10.1016/j.actbio.2009.06.033).

---

## 1. Primary Source Rectification & DOI Audit

In Cycle 10, the secondary holdout dataset was cited under DOI `10.1016/j.actbio.2009.08.033`.
A cross-reference audit against Crossref and ScienceDirect revealed:
- **`10.1016/j.actbio.2009.08.033`:** Daniel Lozano et al., *Osteostatin-loaded bioceramics stimulate osteoblastic growth and differentiation*, Acta Biomater. 6(2): 797–803 (2010).
- **`10.1016/j.actbio.2009.06.033`:** The authentic DOI for Tombolato et al. (2010).

This typographical error in the DOI has been permanently corrected in [`registry/sources.json`](file:///D:/AEGIS-01/registry/sources.json) under `SRC-0151`.

---

## 2. Quantitative Mode-by-Mode Forensic Audit

Cycle 10 evaluated four experimental conditions attributed to Tombolato et al. (2010). Below is the comprehensive forensic reconstruction of each mode:

```
+-----------------------------------------------------------------------------------------------------------------------+
| Specimen ID   | TOM2010-DL                                                                                           |
| Mode Name     | Dry Longitudinal                                                                                      |
| Direction     | Longitudinal (0 deg, parallel to horn tubule and growth axis)                                         |
| Hydration     | Ambient dry (~10% moisture content)                                                                   |
| Measured E    | 2.15 +- 0.30 GPa (Reported in Cycle 10)                                                               |
| Model Pred    | 1.953 GPa                                                                                             |
| Model Error   | 0.197 GPa (Abs Error: 9.16%)                                                                          |
| Paper Source  | Figure 8 / Figure 9 (Representative flexural stress-strain curves)                                    |
| Extr. Method  | Visual slope digitization from non-tabular graphical curve                                            |
| Verification  | NOT VERIFIED IN AUTHOR TABLES. No discrete tabular numerical value of 2.15 GPa exists.                |
+---------------+-------------------------------------------------------------------------------------------------------+
| Specimen ID   | TOM2010-DT                                                                                           |
| Mode Name     | Dry Transverse                                                                                        |
| Direction     | Transverse (90 deg, perpendicular to tubule axis)                                                     |
| Hydration     | Ambient dry (~10% moisture content)                                                                   |
| Measured E    | 1.25 +- 0.20 GPa (Reported in Cycle 10)                                                               |
| Model Pred    | 1.269 GPa                                                                                             |
| Model Error   | 0.019 GPa (Abs Error: 1.52%)                                                                          |
| Paper Source  | Figure 8 / Figure 9 (Representative flexural stress-strain curves)                                    |
| Extr. Method  | Visual slope digitization from non-tabular graphical curve                                            |
| Verification  | NOT VERIFIED IN AUTHOR TABLES. Apparent 0.019 GPa agreement relies on post-hoc mode_factor=0.90.       |
+---------------+-------------------------------------------------------------------------------------------------------+
| Specimen ID   | TOM2010-WL                                                                                           |
| Mode Name     | Wet Longitudinal                                                                                      |
| Direction     | Longitudinal (0 deg, parallel to tubule axis)                                                         |
| Hydration     | Rehydrated (Tombolato paper reports ~35% water content; Cycle 10 model entered w=0.40)                 |
| Measured E    | 0.22 +- 0.06 GPa (Reported in Cycle 10)                                                               |
| Model Pred    | 0.306 GPa                                                                                             |
| Model Error   | 0.086 GPa (Abs Error: 39.09%)                                                                         |
| Paper Source  | Figure 8 / Figure 9 (Representative flexural stress-strain curves)                                    |
| Extr. Method  | Visual slope digitization from low-slope tail                                                         |
| Verification  | NOT VERIFIED IN AUTHOR TABLES. Hydration parameter mismatch (w=0.40 vs ~0.35).                         |
+---------------+-------------------------------------------------------------------------------------------------------+
| Specimen ID   | TOM2010-WT                                                                                           |
| Mode Name     | Wet Transverse                                                                                        |
| Direction     | Transverse (90 deg, perpendicular to tubule axis)                                                     |
| Hydration     | Rehydrated (Tombolato paper reports ~35% water content; Cycle 10 model entered w=0.40)                 |
| Measured E    | 0.14 +- 0.04 GPa (Reported in Cycle 10)                                                               |
| Model Pred    | 0.199 GPa                                                                                             |
| Model Error   | 0.059 GPa (Abs Error: 42.14%)                                                                         |
| Paper Source  | Figure 8 / Figure 9 (Representative flexural stress-strain curves)                                    |
| Extr. Method  | Visual slope digitization from low-slope tail                                                         |
| Verification  | NOT VERIFIED IN AUTHOR TABLES. No discrete tabular numerical value exists.                            |
+-----------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Conflation of Loading Modes: Compression vs Bending vs Tension

The paper by Tombolato et al. (2010) contains two separate mechanical testing programs:
1. **Quasi-Static Compression Testing (Table 1):**
   - Conducted on cubic specimens along Longitudinal, Radial, and Transverse directions.
   - Ambient dry Young's modulus:
     - Longitudinal: **$1.8\text{--}2.4\text{ GPa}$**
     - Radial: **$1.1\text{--}1.3\text{ GPa}$**
     - Transverse: **$1.0\text{--}1.2\text{ GPa}$**
2. **Three-Point Flexural Bending Testing (Figures 8 and 9):**
   - Conducted on rectangular beam coupons to investigate crack deflection, delamination, and ligament bridging.
   - The authors presented stress-strain curves to illustrate fracture energy and plastic deformability, but **did not compile a summary table of bending Young's moduli**.
3. **Tensile Testing:**
   - Tombolato et al. (2010) **did not perform tensile testing** on bighorn sheep horn coupons. (Tensile data was obtained in Zhang et al. 2018 and Li et al. 2010).

**Forensic Finding:** In Cycle 10, the four bending values were described as "bending coupons", but their values ($2.15$ and $1.25\text{ GPa}$) closely mirror the compressive moduli from Table 1 ($1.8\text{--}2.4$ and $1.0\text{--}1.2\text{ GPa}$). This creates severe ambiguity as to whether digitized bending slopes were subconsciously influenced by Table 1 compressive values.

---

## 4. Parameter Leakage & Post-Hoc Model Adaptation

In `predict_keratin_modulus()` (Cycle 10):
```python
mode_factor = 0.75 if mode == "tension" else (1.0 if mode == "compression" else 0.90)
```
- In Cycle 8 and Cycle 9, the model only handled tension ($0.75$) and compression ($1.00$).
- The scalar $\gamma_{\text{bending}} = 0.90$ was introduced in Cycle 10 **at the exact same time that Tombolato bending coupons were introduced**.
- Without $\gamma_{\text{bending}} = 0.90$, the longitudinal dry prediction would be $2.17\text{ GPa}$ (if treated as compression) or $1.63\text{ GPa}$ (if treated as tension).
- Setting $\gamma_{\text{bending}} = 0.90$ post-hoc to optimize the fit to the digitized bending curves invalidates the claim of a blind, prospective holdout.

---

## 5. Final Evidentiary Classification

Because:
1. No author-published tabular ground truth exists for three-point bending elastic moduli in Tombolato et al. (2010);
2. Values were extracted by graphical slope estimation from non-numerical figures;
3. Hydration was approximated as $w=0.40$ instead of the reported $w \approx 0.35$;
4. The bending mode factor ($0.90$) was post-hoc calibrated;

The formal validation status of Tombolato et al. (2010) is declared:

$$\mathbf{TOMBOLATO2010\_HOLDOUT = NOT\_VERIFIED}$$
