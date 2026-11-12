# E2: Tendon Regional Mechanics Validation & Segmental Morphometry Audit

**Experiment ID:** EXP-0049  
**Negative Result Ref:** NEG-0046  
**Cycle:** 15  
**Date:** 2026-11-12  
**Working Branch:** `research/cycle15-independent-validation`  
**Status:** `DATA_BLOCKED`  
**Hypothesis:** HYP-0010  
**Primary Endpoint:** RMSE reduction of local tendon strain prediction ($\ge 10\%$) using regional cross-sectional area (CSA) versus a single uniform CSA.  

---

## 1. Scientific Foundation and Problem Formulation

In human skeletal muscle force transmission, the tendon is not an idealized rigid tether or a uniform cylindrical spring. In vivo anatomical investigations (notably Kongsgaard et al., 2007) demonstrate pronounced morphological heterogeneity along the longitudinal axis of human tendons.

For the patellar tendon, Kongsgaard et al. (*J Appl Physiol*, 2007) documented characteristic cross-sectional areas:
- **Proximal Region (near patellar apex):** $\sim 104 \pm 4\text{ mm}^2$
- **Mid-Substance Region:** $\sim 118 \pm 5\text{ mm}^2$
- **Distal Region (near tibial tuberosity):** $\sim 127 \pm 6\text{ mm}^2$

### The Crucial Methodological Warning:
These published values are **cohort-level population means from a specific demographic group** (healthy young males), with substantial between-subject standard deviations. They are **NOT universal constants** and **CANNOT be substituted as individual participant data** in computational models. Substituting literature means for individual measurements creates an artificial cohort with zero inter-individual geometric covariance, generating spurious statistical significance and invalidating cross-validation.

---

## 2. Hypothesis Formulation (HYP-0010)

- **Statement:** At an identical applied or inferred tendon tensile force $F(t)$, a biomechanical model incorporating participant-specific regional cross-sectional areas ($\text{CSA}_{\text{prox}}$, $\text{CSA}_{\text{mid}}$, $\text{CSA}_{\text{dist}}$) will reduce the held-out root mean square error (RMSE) of local segmental strain predictions by at least $10\%$ relative to a standard baseline model employing a single mean cross-sectional area ($\overline{\text{CSA}}$), under an otherwise strictly identical constitutive material law.
- **Null Hypothesis ($H_0$):** Regional CSA segmentation reduces local strain prediction RMSE by less than $10\%$ ($\Delta \text{RMSE} < 0.10$), or the difference is statistically indistinguishable from zero across participants.

---

## 3. Mathematical Models for E2 Comparison

To isolate the specific mechanical contribution of regional geometry without confounding variables, all other parameters are held strictly invariant between the two models:

### 3.1 Constitutive Material Law (Strictly Invariant)
A 1D linear elastic material law is assigned to the collagen fascicle matrix in the physiological linear region:
$$\sigma_r(t) = E \cdot \epsilon_r(t)$$
where:
- $\sigma_r(t)$ is the normal tensile stress in region $r \in \{\text{proximal}, \text{mid}, \text{distal}\}$ (MPa).
- $\epsilon_r(t) = \frac{\Delta L_r(t)}{L_{0,r}}$ is the local segmental engineering strain (dimensionless).
- $E$ is the material Young's modulus (MPa).

### 3.2 Distinction Between Material Modulus and Structural Stiffness
A fundamental error in previous biomechanical literature is the conflation of material and structural properties:
- **Material Modulus ($E$, MPa or $\text{N/mm}^2$):** Intrinsic material stiffness of the extracellular matrix, determined by collagen fibril density, crosslink maturity, and proteoglycan ground substance.
- **Structural Stiffness ($k$, N/mm):** Extrinsic resistance of the whole organ to deformation, governed by both material modulus and macro-geometry:
  $$k = \frac{E \cdot \text{CSA}}{L_0}$$
In our comparative evaluation, $E$ is identical between Model A and Model B. Only the cross-sectional area representation varies.

### 3.3 Model A (Single Uniform CSA Baseline)
Model A assigns the participant's mean cross-sectional area uniformly across all regions:
$$\overline{\text{CSA}} = \frac{1}{3} \left( \text{CSA}_{\text{prox}} + \text{CSA}_{\text{mid}} + \text{CSA}_{\text{dist}} \right)$$
Predicted local tensile stress and strain for all regions $r \in \{\text{prox}, \text{mid}, \text{dist}\}$:
$$\sigma_{A,r}(t) = \frac{F(t)}{\overline{\text{CSA}}}$$
$$\hat{\epsilon}_{A,r}(t) = \frac{\sigma_{A,r}(t)}{E} = \frac{F(t)}{E \cdot \overline{\text{CSA}}}$$
*Limitation of Model A:* Predicts uniform strain across the entire tendon length, ignoring local stress concentrations at the narrower proximal insertion.

### 3.4 Model B (Regional Segmental CSA Model)
Model B calculates regional tensile stress based on the participant-specific measured CSA of each segment:
$$\sigma_{B,r}(t) = \frac{F(t)}{\text{CSA}_r}, \quad r \in \{\text{prox}, \text{mid}, \text{dist}\}$$
$$\hat{\epsilon}_{B,r}(t) = \frac{\sigma_{B,r}(t)}{E} = \frac{F(t)}{E \cdot \text{CSA}_r}$$
*Expectation of Model B:* Correctly predicts elevated strain in the proximal region ($\text{CSA}_{\text{prox}} \approx 104\text{ mm}^2 \implies \text{higher stress}$) and lower strain in the distal region ($\text{CSA}_{\text{dist}} \approx 127\text{ mm}^2 \implies \text{lower stress}$).

---

## 4. Pre-Registration Protocol (Locked Prior to Outcome Assessment)

### 4.1 Required Primary Measurements
To test HYP-0010 without surrogates, an external dataset must simultaneously provide:
1. **Regional CSA:** Individual participant B-mode ultrasound axial scans or 3T MRI axial slices calibrated at $\ge 3$ verified anatomical landmarks (patellar apex, mid-distance, tibial insertion).
2. **Local Segmental Strain:** In vivo dynamic displacement tracking (via ultrasound speckle tracking, tissue Doppler, or tagged cine-MRI) measuring $\Delta L_{\text{prox}}$, $\Delta L_{\text{mid}}$, $\Delta L_{\text{dist}}$ under progressive voluntary isometric loading.
3. **Tendon Force:** External force or dynamometer joint torque converted to patellar tendon force via participant-specific patellar tendon moment arm:
   $$F_{\text{tendon}}(t) = \frac{\tau_{\text{knee}}(t)}{r_{\text{pat}}(\theta)}$$
4. **Sample Size:** $N \ge 6$ independent human participants.

### 4.2 Error Metric
Local strain RMSE computed per participant $i$ across all observed time points $T_i$ and regions $r$:
$$\text{RMSE}_{i}(M) = \sqrt{\frac{1}{3 T_i} \sum_{r \in \{\text{prox}, \text{mid}, \text{dist}\}} \sum_{t=1}^{T_i} \left( \hat{\epsilon}_{M,r,i}(t) - \epsilon_{r,i}^{\text{obs}}(t) \right)^2 }$$
Relative RMSE reduction:
$$\Delta \text{RMSE}_{\text{rel}, i} = \frac{\text{RMSE}_i(\text{Model A}) - \text{RMSE}_i(\text{Model B})}{\text{RMSE}_i(\text{Model A})}$$

### 4.3 Decision Criteria
- **`GO`:** $\Delta \text{RMSE}_{\text{rel}, i} \ge 0.10$ sustained in $> 50\%$ of independent participants, with a 95% bootstrap confidence interval strictly excluding zero.
- **`NO_GO`:** $\Delta \text{RMSE}_{\text{rel}} < 0.10$ or confidence interval crossing zero.
- **`DATA_BLOCKED`:** Absence of public repository datasets providing synchronized participant-level regional CSA and local strain.

### 4.4 Sensitivity Analysis
To account for ultrasound/MRI segmentation error, regional CSA must be perturbed by $\pm 10\%$:
$$\text{CSA}_r^{\text{perturbed}} = \text{CSA}_r \cdot (1 \pm 0.10)$$
The model must demonstrate whether the advantage of Model B persists across the entire $\pm 10\%$ measurement error bound.

---

## 5. Separate Analysis of Tendon Strength and Mechanical Limits

When evaluating tendon structural safety under augmented muscular loading (e.g., the $+20\%$ force scenario), biomechanical models must not simplify tendon failure into a single scalar "density index". 

In accordance with fundamental soft tissue biomechanics, the following ex vivo mechanical testing endpoints must be analyzed **strictly as separate, independent mechanical properties**:

1. **Ultimate Tensile Stress (UTS, $\sigma_{\text{uts}}$, MPa):** Peak tensile stress sustained prior to macroscopic fascicle rupture. Typically $80\text{--}120\text{ MPa}$ in healthy human patellar tendon.
2. **Ultimate Tensile Load ($F_{\text{fail}}$, N):** Total force at catastrophic failure ($F_{\text{fail}} = \sigma_{\text{uts}} \cdot \text{CSA}_{\text{min}}$).
3. **Strain at Failure ($\epsilon_{\text{fail}}$, %):** Engineering strain at the point of rupture (typically $12\text{--}16\%$).
4. **Energy to Failure (Work of Fracture / Modulus of Resilience, $\text{MJ/m}^3$ or J):** Area under the stress-strain or force-displacement curve up to failure.
5. **Fatigue Life ($N_f$, Cycles to Failure):** Number of submaximal loading cycles sustained at cyclic stress amplitudes $\Delta \sigma$ ($S\text{-}N$ Wöhler curve: $\Delta \sigma = \sigma_0 - b \log_{10} N_f$).
6. **Enzymatic & Non-Enzymatic Collagen Crosslinks (mol/mol collagen):**
   - Enzymatic trivalent crosslinks: Hydroxylysyl-pyridinoline (HP) and lysyl-pyridinoline (LP), mediated by Lysyl Oxidase (LOX).
   - Non-enzymatic Advanced Glycation End-products (AGEs): Pentosidine.

### Critical Integrity Warnings:
- **PROHIBITION 1: No Scalar "Density Index".** Combining tensile strength, stiffness, and crosslink density into an arbitrary composite "tendon density score" is mathematically and biologically invalid. A tissue may have high enzymatic crosslinking yet lower ultimate load due to smaller cross-sectional area.
- **PROHIBITION 2: Elastic Modulus $\ne$ Fatigue Life.** An increase in Young's modulus ($E$) reflects tissue stiffening, NOT increased fatigue resistance. Highly stiffened, over-crosslinked tendons (e.g., in advanced glycation or hyper-physiological chemical crosslinking) exhibit increased brittleness, reduced strain to failure, and accelerated microdamage accumulation under high-cycle cyclic loading.

---

## 6. Dataset Audit Findings

An exhaustive systematic search was conducted across PhysioNet, Zenodo, Figshare, Dryad, OpenSim/SimTK, UMUD, and AddBiomechanics.

### Key Audit Outcomes:
1. **Kongsgaard et al. (2007):** Literature values exist only as aggregate published means ($\pm \text{SD}$). Raw individual participant tables were never deposited. Substituting group means as individual data is prohibited.
2. **SimTK Specimen-Specific Models:** Tested cadaveric specimens under artificial rig loading; no live human neuromuscular contractions.
3. **Tendon Ultrasound Databases (Dryad/Figshare):** Publicly available ultrasound studies (e.g., Couppé et al., Magnusson et al.) measure either global tendon elongation or single-level CSA. None provide the synchronous pairing of 3-region CSA with 3-region local strain time series under calibrated dynamometer load.

---

## 7. Formal Verdict

```text
E2_STATUS = DATA_BLOCKED
```

### Registered Result:
- **ID:** NEG-0046
- **Statement:** "In global scientific repositories, there is currently no open-access human dataset providing synchronized participant-specific regional tendon cross-sectional areas (proximal, mid, distal) paired with local regional strain measurements and applied tendon load across independent individuals."
- **Status of Hypothesis HYP-0010:** Remains **`UNVERIFIED / MODEL_ONLY`**. The hypothesis is biologically grounded by literature evidence of regional CSA heterogeneity, but cannot be empirically validated until individual-level multi-region imaging datasets are acquired.
