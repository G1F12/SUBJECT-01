# PUBLICATION POTENTIAL AND DISSEMINATION PLAN
## Peer-Reviewed Publication Outlines from Cycle 16 Findings

**Document ID:** `research/cycle16/PUBLICATION_POTENTIAL.md`  
**Date:** 2026-11-12  
**Author:** SUBJECT-01 Autonomous Research Team  
**Status:** Completed  
**Related Documents:**
- [E1_ISOMETRIC_STRENGTH.md](file:///D:/SUBJECT-01/research/cycle16/E1_ISOMETRIC_STRENGTH.md)
- [E2_REGIONAL_TENDON.md](file:///D:/SUBJECT-01/research/cycle16/E2_REGIONAL_TENDON.md)
- [E5_OXFORD_MTJ.md](file:///D:/SUBJECT-01/research/cycle16/E5_OXFORD_MTJ.md)
- [SCIENTIFIC_NOVELTY.md](file:///D:/SUBJECT-01/research/cycle16/SCIENTIFIC_NOVELTY.md)

---

## 1. Overview

The computational and empirical breakthroughs of Research Cycle 16 provide rigorous foundation for three distinct peer-reviewed scientific manuscripts:

1. **Manuscript 1 (Neuromechanics / Biomedical Engineering):** Focuses on the empirical failure of uncalibrated antagonist sEMG in cross-subject generalization.
2. **Manuscript 2 (Orthopaedic Biomechanics / Ultrasound):** Focuses on in vivo sub-tendon sliding and displacement gradients in human Achilles tendon.
3. **Manuscript 3 (Molecular Muscle Physiology / Transcriptomics):** Focuses on the anatomical provenance and cell-type boundaries for myotendinous junction signature replication.

---

## 2. Manuscript 1: Neuromuscular Torque Modeling

### 2.1. Title & Target Journal
- **Proposed Title:** *Pitfalls of Uncalibrated Antagonist Surface EMG in Cross-Subject Joint Torque Prediction: A Rigorous Benchmark on the DPValid Collection*
- **Target Journals:**
  - *Journal of Biomechanics* (Elsevier, IF: 2.8, Quartile Q2)
  - *IEEE Transactions on Biomedical Engineering* (IEEE, IF: 4.6, Quartile Q1)
  - *Journal of Applied Physiology* (APS, IF: 3.3, Quartile Q1)

### 2.2. Abstract Draft
> **Abstract:** Surface electromyography (sEMG) is widely used to predict joint torque in biomechanical models, with antagonist co-activation frequently hypothesized to improve prediction accuracy by accounting for counter-torques. However, the generalizability of uncalibrated antagonist sEMG across unseen human subjects remains poorly quantified. Using the open-access DPValid collection (20 healthy adults, 125 knee extension and 121 knee flexion trials at 75° and 90°), we evaluated five nested regression architectures under strict Leave-One-Subject-Out (LOSO) cross-validation. While an agonist-only linear model achieved an out-of-sample RMSE of 82.85 Nm (R² = 0.1112) in knee extension, the unregularized addition of antagonist hamstrings sEMG increased prediction error to 89.10 Nm (R² = -0.0280; paired t-test p = 0.1426), acting as a noise contributor. L2 Ridge shrinkage attenuated this penalty (RMSE = 82.39 Nm, R² = 0.1211). In contrast, incorporating joint angle and anthropometrics (body mass, height, biological sex) dramatically reduced RMSE by 41% to 53.45 Nm (R² = 0.6301). Our findings demonstrate that uncalibrated surface antagonist EMG does not enhance cross-subject torque prediction in healthy adults due to inter-individual impedance and co-activation variance. Neuromusculoskeletal models must incorporate subject-specific calibration or prioritize anthropometric and kinematic constraints over raw population sEMG regressors.

---

## 3. Manuscript 2: Tendon Intra-Structure Biomechanics

### 3.1. Title & Target Journal
- **Proposed Title:** *In Vivo Sub-Tendon Sliding and Displacement Non-Uniformity in the Human Achilles Tendon During Passive Rotation and Isometric Plantarflexion*
- **Target Journals:**
  - *Scandinavian Journal of Medicine & Science in Sports* (Wiley, IF: 3.9, Quartile Q1)
  - *Annals of Biomedical Engineering* (Springer, IF: 3.8, Quartile Q1)
  - *Frontiers in Bioengineering and Biotechnology* (Frontiers, IF: 5.7, Quartile Q1)

### 3.2. Abstract Draft
> **Abstract:** The human Achilles tendon comprises twisted sub-tendons arising from the soleus and gastrocnemius muscles. While macroscopic models treat the tendon as a uniform elastic element, local tissue shearing is hypothesized to facilitate differential muscle action. We re-analyzed high-frame-rate ultrasound speckle tracking data across superficial, middle, and deep layers in 10 healthy adults (bilateral, 160 observations) under passive ankle rotation and isometric plantarflexion. During isometric contractions, the deep layer underwent significantly greater longitudinal displacement than the superficial layer (3.00 ± 1.88 mm vs. 2.44 ± 1.59 mm; Friedman p = 1.17e-13), producing an inter-layer sliding displacement of 0.28 to 0.40 mm between adjacent layers. In passive rotation, a parallel displacement gradient was observed (-3.10 ± 1.24 mm deep vs. -2.32 ± 1.04 mm superficial; p = 2.10e-16). Both superficial and deep displacements correlated strongly with external torque (r = 0.582, p = 8.27e-5 and r = 0.590, p = 6.13e-5). These findings confirm that intra-tendinous sliding is an intrinsic physiological mechanism accommodating non-uniform muscular contractions. Furthermore, because layer-specific cross-sectional areas were not quantified, we highlight the methodological distinction between tissue strain tracking and true mechanical stress determination.

---

## 4. Manuscript 3: Myotendinous Junction Transcriptomics

### 4.1. Title & Target Journal
- **Proposed Title:** *Anatomical Lineage and Cell-Type Boundaries in the Single-Cell Replication of Human Myotendinous Junction Signatures*
- **Target Journals:**
  - *Skeletal Muscle* (BMC, IF: 3.5, Quartile Q1)
  - *American Journal of Physiology - Cell Physiology* (APS, IF: 3.7, Quartile Q2)
  - *Matrix Biology Plus* (Elsevier, IF: 3.2, Quartile Q2)

### 4.2. Core Message
- Rigorous clarification of why E-MTAB-15400 failed replication in Cycle 15 (needle biopsy from vastus lateralis mid-belly lacking junctional tissue).
- Evaluation of the Oxford Achilles single-cell atlas (Cohen et al. 2026), demonstrating that *COL22A1* and *COMP* are synthesized by junctional stromal fibroblasts, while myonuclei were physically excluded.
- Formulates guidelines for future experimental protocols to capture true intact human MTJ interfaces.

---

## 5. Submission Readiness Checklist

| Item | Manuscript 1 (EMG/Torque) | Manuscript 2 (Tendon Shearing) | Manuscript 3 (MTJ Provenance) |
| :--- | :--- | :--- | :--- |
| **Raw Data Integrity** | Ingested & Verified (`dpvalid_isometric_trials.csv`) | Ingested & Verified (`bogaerts_2017_data.csv`) | Documented & Audited |
| **Cross-Validation** | 20-fold LOSO + 2000 Bootstrap CI | Friedman & Paired RM-ANOVA | Provenance Matrix |
| **Figures & Tables** | Complete in `E1_ISOMETRIC_STRENGTH.md` | Complete in `E2_REGIONAL_TENDON.md` | Complete in `E5_OXFORD_MTJ.md` |
| **Code Reproducibility** | Python script verified (`run_e1_iso.py`) | Python script verified (`run_e2_regional.py`) | Audited in `run_e5_mtj_audit.py` |
| **Status** | **Ready for Drafting** | **Ready for Drafting** | **Ready for Drafting** |
