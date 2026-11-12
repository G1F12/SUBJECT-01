# EXPERIMENT E2-REGIONAL-STRAIN: IN VIVO TENDON LAYER MECHANICS
## Regional Strain Heterogeneity and Sliding Dynamics in Human Achilles Tendon

**Experiment ID:** `EXP-0052`  
**Document ID:** `research/cycle16/E2_REGIONAL_TENDON.md`  
**Date:** 2026-11-12  
**Dataset:** Bogaerts et al. (2017), PLoS ONE / PMC5519157 (DOI: `10.1371/journal.pone.0181364`)  
**Designation:** `E2-REGIONAL-STRAIN` (regional strain and displacement only)  
**Hypothesis Status:**
- `HYP-0010_REGIONAL_STRAIN_HETEROGENEITY`: **EMPIRICALLY CONFIRMED**
- `HYP-0010_FULL_VALIDATION (Stress & Load)`: **BLOCKED** (absent regional CSA)  
**Related Documents:**
- [E2_RESULTS.json](file:///D:/SUBJECT-01/research/cycle16/E2_RESULTS.json)
- [DATASET_VERIFICATION.md](file:///D:/SUBJECT-01/research/cycle16/DATASET_VERIFICATION.md)
- [CYCLE15_CORRECTIONS.md](file:///D:/SUBJECT-01/research/cycle16/CYCLE15_CORRECTIONS.md)

---

## 1. Scientific Context & Purpose

The human Achilles tendon is not a homogeneous cylindrical cord; it is composed of three twisted sub-tendons arising separately from the soleus, medial gastrocnemius, and lateral gastrocnemius muscle bellies. In classical biomechanical models, tendons are often modeled as uniform springs with a single elastic modulus and uniform cross-sectional strain.

In Cycle 15, `HYP-0010` posited that tendon internal layers experience non-uniform strain and shear deformation, which could localize micro-damage during high-force contractions. However, empirical verification on real human intra-tendinous tracking data was pending (`ISS-0023`).

In Cycle 16, we analyzed the complete open dataset of Bogaerts et al. (2017) containing high-frame-rate ultrasound speckle tracking across 10 healthy adults (bilateral, $N = 160$ total observations).

---

## 2. Experimental Data & Cohort Details

- **Participants:** 10 healthy human volunteers (5 females, 5 males; age $25.8 \pm 3.1$ years, body mass $69.0 \pm 15.6\text{ kg}$).
- **Tested Limbs:** Bilateral (Left and Right limbs evaluated independently).
- **Activation Modalities:**
  1. *Passive Ankle Motion (PAS):* Controlled passive rotation.
  2. *Isometric Plantarflexion (ISO):* Ramp-and-hold voluntary isometric contraction.
- **Layers Evaluated:**
  - **Superficial Layer:** Posterior/dorsal region (primarily soleus/lateral gastrocnemius sub-tendon).
  - **Middle Layer:** Central core region.
  - **Deep Layer:** Anterior/ventral region (closest to Kager's fat pad and medial gastrocnemius sub-tendon).
- **Time Points:** Baseline initial (Time 0) and Peak excursion (Time 1).

---

## 3. Empirical Results

### 3.1. Layer-Specific Displacement & Strain at Peak Excursion (Time 1)

| Activation Mode | Layer | Longitudinal Displacement (mm) | Longitudinal Strain (%) | Inter-Layer Displacement Difference |
| :--- | :--- | :--- | :--- | :--- |
| **Isometric (ISO)** | Superficial | $+2.44 \pm 1.59$ (median 2.24) | $+0.33 \pm 0.53$ | **Sup vs Mid:** $-0.29 \pm 0.20\text{ mm}$ ($p < 10^{-10}$) |
| | Middle | $+2.73 \pm 1.72$ (median 2.48) | $+0.32 \pm 0.54$ | **Mid vs Deep:** $-0.28 \pm 0.20\text{ mm}$ ($p < 10^{-10}$) |
| | Deep | **$+3.00 \pm 1.88$** (median 2.68) | $+0.32 \pm 0.56$ | **Sup vs Deep:** $-0.56 \pm 0.36\text{ mm}$ ($p < 10^{-12}$) |
| **Passive (PAS)** | Superficial | $-2.32 \pm 1.04$ (median -2.05) | $-0.48 \pm 0.52$ | **Sup vs Mid:** $+0.40 \pm 0.24\text{ mm}$ ($p < 10^{-11}$) |
| | Middle | $-2.72 \pm 1.13$ (median -2.34) | $-0.41 \pm 0.49$ | **Mid vs Deep:** $+0.38 \pm 0.21\text{ mm}$ ($p < 10^{-12}$) |
| | Deep | **$-3.10 \pm 1.24$** (median -2.80) | $-0.32 \pm 0.47$ | **Sup vs Deep:** $+0.79 \pm 0.41\text{ mm}$ ($p < 10^{-13}$) |

### 3.2. Statistical Tests of Layer Non-Uniformity
- **Isometric Displacement Non-Uniformity:**
  - Friedman Test across layers: $\chi^2 = 59.55$, **$p = 1.17 \times 10^{-13}$**.
  - Highly significant displacement gradient: the deep layer displaces **$23.1\%$ more** than the superficial layer during isometric plantarflexion.
- **Passive Displacement Non-Uniformity:**
  - Friedman Test across layers: $\chi^2 = 72.20$, **$p = 2.10 \times 10^{-16}$**.
  - In passive rotation, the deep layer also displaces **$33.6\%$ more** than the superficial layer.
- **Passive Strain Gradient:**
  - Friedman Test for passive strain across layers: $\chi^2 = 33.45$, **$p = 5.45 \times 10^{-8}$**.
  - Significant negative compressive strain gradient from superficial ($-0.48\%$) to deep ($-0.32\%$).
- **Correlation with Plantarflexion Torque (during ISO):**
  - Superficial displacement vs Torque: Pearson $r = 0.5816$, $p = 8.27 \times 10^{-5}$.
  - Deep displacement vs Torque: Pearson $r = 0.5901$, $p = 6.13 \times 10^{-5}$.
  - Both layers exhibit robust linear coupling with joint torque.

---

## 4. Methodological Barrier: Why `HYP-0010_FULL_VALIDATION` Is Blocked

While intra-tendinous strain and displacement non-uniformity are rigorously confirmed, **`HYP-0010` cannot be declared fully validated as a mechanical stress model**:
1. **Absence of Regional Cross-Sectional Area (CSA):** Bogaerts et al. utilized longitudinal sagittal ultrasound planes to track speckle patterns. Transverse axial scans were not captured, meaning the cross-sectional area of the individual sub-tendons (superficial, middle, deep) is unknown for each subject.
2. **Impossibility of Regional Stress Calculation:**
   $$\sigma_{\text{layer}} = \frac{F_{\text{layer}}}{\text{CSA}_{\text{layer}}}$$
   Without $\text{CSA}_{\text{layer}}$, regional engineering stress cannot be calculated. It is mathematically and physically impermissible to assume uniform CSA across twisted sub-tendons.
3. **Formal Classification:**
   - Experiment designated: **`E2-REGIONAL-STRAIN`**.
   - `HYP-0010_REGIONAL_STRAIN_HETEROGENEITY`: **CONFIRMED**.
   - `HYP-0010_FULL_VALIDATION`: **BLOCKED** pending datasets with simultaneous axial MRI/3D-ultrasound sub-tendon segmentation.

---

## 5. Precise Taxonomy of Tendon Failure Properties

To eliminate future ambiguity in SUBJECT-01 modeling, the biomechanical endpoints of tendon failure are strictly separated:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TENDON FAILURE ENDPOINT TAXONOMY                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Ultimate Tensile Strength (UTS):                                    │
│    Peak nominal stress before macroscopic rupture (MPa or N/mm^2).     │
│    Normative human Achilles: 70 - 100 MPa.                             │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Ultimate Failure Load:                                              │
│    Peak structural force sustained before complete rupture (N).        │
│    Normative human Achilles: 4000 - 8000 N. F_max = UTS * Total CSA.   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Failure Strain (epsilon_f):                                         │
│    Elongation at rupture (%). Normative human Achilles: 12 - 16%.      │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Work to Fracture / Toughness:                                       │
│    Volumetric strain energy density absorbed to failure (MJ/m^3).      │
│    Normative human Achilles: 3 - 7 MJ/m^3.                             │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Fatigue Life (N_f):                                                 │
│    Cycles to failure under repetitive sub-UTS cyclic stress (Basquin). │
│    N_f = C * (Delta_sigma)^(-m), m ~ 6 - 8.                            │
├────────────────────────────────────────────────────────────────────────┤
│ 6. Cross-link Density:                                                 │
│    Biochemical density of enzymatic trivalent LOX cross-links          │
│    (HP, LP) vs non-enzymatic glycation products (AGEs, pentosidine).  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Functional Implications for Human Enhancement

1. **Sub-Tendon Sliding is a Physiological Stress Relief Mechanism:** The $0.28\text{--}0.40\text{ mm}$ of inter-layer sliding observed between superficial and deep sub-tendons allows differential gastrocnemius vs. soleus motor unit firing without tearing the common tendon trunk.
2. **Interfascicular Matrix (IFM) Vulnerability:** Inter-layer shear strains place high mechanical demands on the non-collagenous IFM (rich in lubricin, decorin, and COMP). Enhancing muscle force without conditioning the IFM to withstand increased inter-fascicular shear represents the primary structural risk of localized tendinopathy.
