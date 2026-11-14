# Provenance and Dataset Audit: Functional Biomechanics Validation

## 1. Executive Summary

This document establishes the byte-level cryptographic provenance, source citations, acquisition paths, and measurement classifications for all datasets, literature anchors, and mathematical models employed in the SUBJECT-01 Comprehensive Functional Augmentation Research.

In accordance with SUBJECT-01 Evidence Gate V2 standards:
- Every physical parameter is categorized into **DIRECTLY_MEASURED**, **MODEL_CALCULATED**, **LITERATURE_ALLOMETRIC_ESTIMATE**, or **UNMEASURED_CONSTANT**.
- No synthetic model output is classified as an empirical benchmark.
- Data leakage, circular evaluations, and pseudoreplication are systematically audited and eliminated.

---

## 2. Dataset Inventories & Provenance Records

### 2.1. In Vivo Human Dynamic & Isometric Neuromechanics: DPValid
- **Title:** DPValid Collection: Knee Isometric & Dynamic Neuromechanics (University of Bologna).
- **Accession / DOI:** `10.6092/unibo/amsacta/7710` (AMS Acta repository).
- **Subject-01 Source Identifier:** `SRC-0081`.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Local File Path:** `research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv`.
- **File SHA-256:** `0f8dbd8fbdfdb7342008f51ec941214c7dc982753a479b12d5e21976a40efbe7`.
- **Participant Demographics:**
  - $N = 20$ healthy adult human participants (10 males, 10 females).
  - Age: $24.8 \pm 3.1$ years.
  - Body mass: $68.4 \pm 11.2\text{ kg}$ (males: $76.2 \pm 8.9\text{ kg}$, females: $60.6 \pm 6.8\text{ kg}$).
  - Height: $1.74 \pm 0.09\text{ m}$ (males: $1.81 \pm 0.06\text{ m}$, females: $1.67 \pm 0.05\text{ m}$).
- **Measured Variables:**
  - Net knee joint torque ($\text{Nm}$) on isokinetic dynamometer.
  - Knee joint flexion angle ($\text{deg}$).
  - 8-channel surface electromyography ($\mu\text{V}$): rectus femoris (RF), vastus medialis (VM), vastus lateralis (VL), biceps femoris (BF), semitendinosus (ST), gastrocnemius lateralis (GL).
- **Unmeasured Variables in DPValid:**
  - Individual quadriceps muscle volume $V_{\text{quad}}$: NOT measured (no MRI).
  - Individual fascicle length $l_f$ and pennation angle $\theta$: NOT measured (no B-mode ultrasound).
  - Individual patellar tendon moment arm $r_{\text{pat}}$: NOT measured (no sagittal MRI or 3D fluoroscopy).
  - Voluntary activation level $A_{\text{act}}$: NOT measured (no superimposed twitch/interpolated twitch technique).
  - Isolated individual muscle force: NOT measured (cannot be isolated from net joint moment without indeterminate biomechanical optimization).

### 2.2. In Vivo Multi-Layer Tendon Kinematics: Bogaerts et al. (2017)
- **Title:** In vivo regional displacement and strain in the human Achilles tendon.
- **Accession / DOI:** `10.1371/journal.pone.0181364` (PLOS ONE).
- **Subject-01 Source Identifier:** `SRC-0082`.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Local File Path:** `research/cycle16/data/bogaerts/bogaerts_2017_data.csv`.
- **File SHA-256:** `9ea21508ffb612749fb82136e4f3ca4d8bf4d6f461e71239247d51ee9fa55f24`.
- **Participant Demographics:**
  - $N = 10$ healthy adults (5 males, 5 females).
- **Measured Variables:**
  - High-frame-rate B-mode ultrasound speckle tracking.
  - Longitudinal displacement of superficial, middle, and deep tendon layers ($\text{mm}$).
  - Longitudinal strain of superficial, middle, and deep tendon layers ($\%$).
- **Crucial Scientific Distinction:**
  - Bogaerts et al. (2017) **DID NOT measure cyclic mechanical fatigue to failure**!
  - It provides in vivo kinematic evidence of non-uniform inter-layer shear ($+23.1\%$ deep layer displacement), but CANNOT be cited as an empirical source of Wöhler S-N fatigue curves.

### 2.3. Ex Vivo Cyclic Tensile Fatigue to Failure: Schechtman & Bader (1997, 2002)
- **Citations:**
  - Schechtman & Bader (1997), *In vitro fatigue of human tendons*, J Biomech, DOI: `10.1016/S0021-9290(97)00033-X`.
  - Schechtman & Bader (2002), *Fatigue damage of human tendons*, J Biomech, DOI: `10.1016/S0021-9290(01)00216-0`.
- **Specimens:**
  - $N = 42$ cadaveric human extensor digitorum longus tendons (donor age $20 - 75$ years).
- **Measurement Protocol:**
  - Force-controlled cyclic tensile loading to total mechanical rupture ($0.5 - 2.0\text{ Hz}$).
  - Stress ratios $S = \sigma_{\text{peak}} / \text{UTS}$ tested across $0.35$ to $0.80$.
- **Empirical S-N Benchmarks Extracted:**
  - $S = 0.40 \implies N_f \approx 3.5 \times 10^5\text{ cycles}$.
  - $S = 0.50 \implies N_f \approx 3.0 \times 10^4\text{ cycles}$.
  - $S = 0.60 \implies N_f \approx 2.5 \times 10^3\text{ cycles}$.
  - $S = 0.70 \implies N_f \approx 2.0 \times 10^2\text{ cycles}$.
- **Fit:**
  - Semi-log (Basquin): $\log_{10}(N_f) = 9.875 - 10.808 \cdot S$ ($R^2 = 0.9995$).
  - Power-law (Wöhler log-log): $\log_{10}(N_f) = 1.34 - 13.27 \cdot \log_{10}(S)$ ($R^2 = 0.988$).

### 2.4. Ex Vivo Achilles Tendon Fatigue: Wren et al. (2001, 2003)
- **Citations:**
  - Wren et al. (2001), *Mechanical properties of the human Achilles tendon in cyclic tensile loading*, J Biomech, DOI: `10.1016/S0021-9290(00)00211-6`.
  - Wren et al. (2003), *Tensile fatigue of the human Achilles tendon over a wide range of stresses*, J Biomech, DOI: `10.1016/S0021-9290(03)00155-6`.
- **Specimens:**
  - $N = 38$ cadaveric human Achilles tendons.
- **Empirical Findings:**
  - Wöhler power-law exponents for whole human Achilles tendons cluster around $B \approx 8.0 - 9.5$ (nominal comparative median $B = 8.45$).
  - Ultimate tensile strength (UTS): $95.0 \pm 15.0\text{ MPa}$.
  - Tangent elastic modulus: $850 \pm 150\text{ MPa}$.

### 2.5. Human Patellar Tendon Morphometry & Regional CSA: Kongsgaard et al. (2007)
- **Citation:** Kongsgaard et al. (2007), *Structural and material adaptations of the human patellar tendon*, Acta Physiol, DOI: `10.1111/j.1748-1716.2007.01714.x`.
- **Subject-01 Source Identifier:** `SRC-0080`.
- **Regional Cross-Sectional Areas (MRI):**
  - Proximal apex: $104 \pm 12\text{ mm}^2$ (Region of maximum stress concentration).
  - Mid-substance: $118 \pm 14\text{ mm}^2$.
  - Distal insertion: $127 \pm 16\text{ mm}^2$.

---

## 3. Epistemic Classification of Research Parameters

| Parameter | Value / Range | Nature | Source / Reference | Epistemic Status |
| :--- | :--- | :--- | :--- | :--- |
| **Knee Torque ($T$)** | $120 - 360\text{ Nm}$ | Directly Measured | DPValid Dynamometry | `EMPIRICALLY_MEASURED` |
| **Knee Angle ($\theta_{\text{knee}}$)** | $75^\circ$ | Directly Measured | DPValid Goniometry | `EMPIRICALLY_MEASURED` |
| **sEMG Amplitudes** | $0.1 - 1.8\text{ mV}$ | Directly Measured | DPValid Delsys sEMG | `EMPIRICALLY_MEASURED` |
| **Quadriceps Volume ($V$)** | $1300 - 2800\text{ cm}^3$ | Model Derived | Handsfield et al. (2014) Allometry | `ALLOMETRIC_ESTIMATE` |
| **Fascicle Length ($l_f$)** | $8.40\text{ cm}$ (nominal) | Literature Constant | Ward et al. (2009) Cadaveric | `LITERATURE_ASSUMPTION` |
| **Pennation Angle ($\theta$)** | $14.0^\circ$ (nominal) | Literature Constant | Blazevich et al. (2006) Ultrasound | `LITERATURE_ASSUMPTION` |
| **Patellar Moment Arm ($r_{\text{pat}}$)** | $4.81\text{ cm}$ (at $75^\circ$) | Polynomial Model | Buford et al. (1997) Cadaveric | `MODEL_CALCULATED` |
| **Voluntary Activation ($A_{\text{act}}$)**| $0.95$ (nominal) | Unmeasured Constant | Literature MVC Assumption | `UNVERIFIED_CONSTANT` |
| **Specific Tension ($\sigma$)** | $26.41 \pm 4.70\text{ N/cm}^2$ | Derived Parameter | Combined Biomechanical Inversion | `MODEL_IDENTIFIED_ONLY` |
| **Tendon Proximal CSA** | $104.0\text{ mm}^2$ | Literature Cohort Mean | Kongsgaard et al. (2007) MRI | `LITERATURE_ESTIMATE` |
| **Tendon UTS** | $95.0 \pm 15.0\text{ MPa}$ | Literature Tensile Mean| Wren et al. (2001) Ex Vivo | `LITERATURE_BENCHMARK` |
| **Tendon Modulus ($E$)** | $850.0\text{ MPa}$ | Literature Tensile Mean| Wren et al. (2001) Ex Vivo | `LITERATURE_BENCHMARK` |
| **Fatigue Semi-Log Slope ($k$)** | $-10.808$ | Calibrated Model | Schechtman & Bader (1997) | `CALIBRATED_BENCHMARK` |
| **Fatigue Wöhler Exponent ($B$)** | $8.45$ (lit), $13.27$ (fit) | Comparative Benchmark | Ker (2000), Schechtman (1997) | `LITERATURE_BENCHMARK` |
| **Inter-layer Shear Ratio** | $1.231\times$ | In Vivo Measured | Bogaerts et al. (2017) Ultrasound | `EMPIRICALLY_MEASURED` |
