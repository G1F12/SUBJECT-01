# Remaining Barriers Matrix & Model M3 Epistemic Identifiability

**Date**: 2026-11-09  
**Cycle**: 10  
**Repository**: `G1F12/SUBJECT-01`  
**Governing Standard**: SUBJECT-01 Evidence Gate V2

---

## 1. Executive Scientific Stance

The acquisition and successful Leave-One-Subject-Out (LOSO) cross-validation of the **PhysioNet ACTES Cycloergometer Dataset** (`SRC-0073`, $N=18$) represents a major breakthrough:
It provides the **first true multi-subject empirical validation of macroscopic cardiorespiratory bioenergetic coupling** ($\dot{E}_{\text{met}} = P_{\text{mech}} / \eta_{\text{gross}}$, $R^2_{\text{LOSO}} = 0.7371 \pm 0.1770$).

**However, the core scientific stance of SUBJECT-01 remains uncompromisingly rigorous:**
> **Successful multi-subject validation of whole-body pulmonary $\dot{V}\text{O}_2$ does NOT validate the full physiological model (M3), does NOT validate localized intramuscular phosphate dynamics, does NOT validate the 45-minute survival target (`TARGET-CPE45`), and does NOT authorize any biological intervention.**

---

## 2. Comprehensive Model M3 Parameter Identifiability Matrix

The table below exhaustively maps every parameter domain of the full integrated SUBJECT-01 physiological model (M3) against empirical datasets acquired through Cycle 10.

| Model M3 Parameter / Domain | Mathematical Symbol | Acquired Dataset Coverage | Observability Status | Epistemic Barrier & Mechanism of Unobservability | Required Future Measurement to Unblock |
|:---|:---:|:---|:---:|:---|:---|
| **Incremental Delta Aerobic Efficiency** | $\eta_{\text{delta}}$ | **ACTES (SRC-0073)**<br>$N = 18$ | **IDENTIFIED & VALIDATED** | Linear regression slope $\beta_1 = \Delta \dot{V}\text{O}_2 / \Delta P$ yields $\eta_{\text{delta}} = 1 / (\beta_1 \cdot 348.33) \approx 22.5\%\dots 26.5\%$; generalizes across 18 independent subjects. | Resolved for cycle ergometry incremental work. |
| **Macroscopic Gross Efficiency** | $\eta_{\text{gross}}(t)$ | **ACTES (SRC-0073)**<br>$N = 18$ | **RECLASSIFIED: WORKLOAD-DEPENDENT** | $\eta_{\text{gross}} = P_{\text{mech}} / \dot{E}_{\text{met}}$ starts at 0% at rest and rises non-linearly to $20\dots 24\%$ at peak workload. Cannot be treated as a single constant regression slope. | Workload-resolved instantaneous ratio tracking. |
| **Cardiorespiratory Response Delay** | $\tau_{\dot{V}\text{O}_2}$ | **ACTES (SRC-0073)**<br>$N = 18$ | **IDENTIFIED VIA NESTED CV** | Phase II kinetics delay verified at $\tau \approx 35\text{ s}$ using nested subject-level cross-validation (zero test leakage), reducing prediction RMSE by $>30\%$. | Resolved for systemic pulmonary kinetics. |
| **Allometric Mass Scaling Exponent** | $M^{\gamma}$ | **ACTES (SRC-0073)**<br>$N = 18$ | **CONSTRAINED LINEAR ($\gamma=1.0$)** | Linear scaling improves cohort-average $R^2$ to $0.7371$, but degrades RMSE in 7/18 subjects (light and heavy participants), indicating non-linear or multi-compartment allometry. | Multi-exponential / non-linear body composition modeling (fat-free mass). |
| **Intracellular Phosphocreatine** | $[\text{PCr}](t)$ | Rehman 2024 (`SRC-0069`)<br>$N = 1$ (3 trials) | **LOCAL TECHNICAL REPEATABILITY ONLY ($N=1$)** | Unobservable from systemic $\dot{V}\text{O}_2$ and crank torque. Local depletion fraction ($26\%\dots 33\%$) and recovery ($k \approx 1.52\text{ min}^{-1}$) observed in only one human subject. | Simultaneous multi-subject $^{31}\text{P}$-MRS + CPET cohort ($N \ge 10$). |
| **Intramuscular Cytosolic pH** | $\text{pH}_i(t)$ | Rehman 2024 (`SRC-0069`)<br>$N = 1$ (3 trials) | **PARTIALLY CALIBRATED ($N=1$)** | Chemical shift titration ($\delta\text{Pi} - \delta\text{PCr}$) depends on temperature, ionic strength, and AMARES fitting; range $6.7932\dots 7.0228$. Unobserved in ACTES. | Calibrated $^{31}\text{P}$-MRS chemical shift standards with temperature correction across multiple subjects. |
| **Motor Unit Discharge Rates & Recruitment** | $f_{\text{MU}}, \theta_{\text{rec}}$ | Hug 2021 (`SRC-0068`)<br>$N = 15$ participants | **LITERATURE ANCHORED (NO DIRECT TIME-SERIES)** | Raw HD-sEMG decomp files blocked by CDN challenge. Mean rates ($8.1\dots 17.9\text{ Hz}$) provide envelope bounds, but cannot be paired beat-to-beat with dynamic cycling power. | Synchronized HD-sEMG during dynamic cycling with open decomposed motor unit spike trains. |
| **Anatomical Muscle Belly Volume** | $V_{\text{anat}}$ | Franke 2020 (`SRC-0063`)<br>$N = 1$ (Subject 01) | **SINGLE-SUBJECT ANCHOR ($N=1$)** | 3D MRI segmentation gives GM volume ($379.89\text{ mL}$), but cohort distributions (Zenodo 10077847, Figshare 5971480) were retracted as unverified. | Open multi-subject lower-limb 3D MRI segmentation cohort ($N \ge 20$). |
| **Local Actomyosin Efficiency** | $\eta_{\text{loc}}$ | Unmeasured | **COMPLETELY UNIDENTIFIABLE** | Cross-bridge ATP turnover efficiency is entangled inside macroscopic $\eta_{\text{gross}} = \eta_{\text{loc}} \cdot \eta_{\text{trans}} \cdot \eta_{\text{mech}}$. | Single muscle fiber in-vitro mechanics or concurrent localized 31P-MRS + optical myography. |
| **Active Muscle Volume** | $V_{\text{active}}(t)$ | Unmeasured | **COMPLETELY UNIDENTIFIABLE** | Fractional recruitment of quadriceps vs gluteus vs gastrocnemius varies with cadence, posture, and fatigue. | Multi-muscle functional MRI (T2-mapping) or localized near-infrared spectroscopy (NIRS). |
| **Extreme 45-Min Target** | `TARGET-CPE45` | Unmeasured in all datasets | **NOT EXTERNALLY VALIDATED** | Graded incremental CPET tests exhaustion in $10\dots 15\text{ minutes}$. Rehman tests $42\text{ seconds}$. Neither tests continuous 45-minute survivability. | Dedicated 45-minute constant-load endurance trial at critical power boundary. |
| **Biological Interventions** | Interventions | None | **STRICTLY PROHIBITED (`NO_GO`)** | Incomplete model identifiability prohibits simulating or recommending pharmacological, dietary, or extreme physiological interventions. | Complete identifiability, animal pre-validation, and institutional ethics approval. |

---

## 3. Epistemic Analysis: Why Macroscopic Validation $\ne$ Microscopic Validation

### 3.1 The Entanglement Fallacy
A common error in computational physiology is assuming that if a model accurately predicts pulmonary $\dot{V}\text{O}_2$ ($R^2 > 0.85$), the underlying intracellular ODE state variables ($[\text{PCr}]$, $[\text{Pi}]$, $[\text{ADP}]$, $\text{pH}_i$) must also be correct.

This deduction is mathematically false due to **many-to-one mapping (non-uniqueness)**:
$$\dot{V}\text{O}_2(t) = \int_{\text{body}} q_{\text{O}_2}(\mathbf{x}, t) \, d\mathbf{x} + \Delta\dot{V}\text{O}_{2,\text{cardiopulmonary}}$$
An infinite combination of localized phosphate depletion profiles, localized blood flows, and recruitment patterns can sum to the exact same whole-body oxygen consumption rate $\dot{V}\text{O}_2$.

### 3.2 The Protocol Domain Gap
- **ACTES Protocol**: Graded incremental ramp protocol ($50\text{ W} \to 140\dots 335\text{ W}$, 15–20 minutes to exhaustion).
- **Rehman 2024 Protocol**: Intermittent repeated square-wave bouts (42 s load at ~3 kg, separated by 300 s recovery).
- **`TARGET-CPE45` Protocol**: Continuous constant-load endurance at or near critical power ($CP$) for 45 minutes under extreme heat or survivability constraints.

Extrapolating a model validated on a 15-minute incremental ramp to a 45-minute continuous extreme survivability regime is an unvalidated out-of-domain projection.

---

## 4. Required Evidence Roadmap to Unblock Remaining Barriers

To progressively unblock the remaining barriers, subsequent research cycles must target:

1. **Simultaneous Multimodal Benchmark (Level 1 Unblock)**:
   A public dataset providing concurrent beat-to-beat mechanical power, breath-by-breath CPET, AND continuous quadriceps near-infrared spectroscopy (NIRS) or dynamic $^{31}\text{P}$-MRS across $N \ge 10$ subjects.
2. **Volumetric Cohort Segmentation (Level 2 Unblock)**:
   An open repository of segmented lower-limb MRI volumes across a representative athletic cohort to replace the single Franke 2020 anchor.
3. **Dedicated Critical Power Endurance Trial (Level 3 Unblock)**:
   Open-source continuous endurance trials (>30–45 minutes) at fixed sub-maximal and supra-maximal workloads to empirically test the long-term depletion and thermal limits of `TARGET-CPE45`.

Until these empirical anchors are downloaded, cryptographically verified, and evaluated through Evidence Gate V2, `TARGET-CPE45` remains **`NOT EXTERNALLY VALIDATED`** and biological interventions remain **`NO_GO`**.
