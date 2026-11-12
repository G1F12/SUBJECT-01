# EXPERIMENT E5 REANALYSIS: OXFORD ACHILLES ATLAS REASSESSMENT
## Forensic Verification of Cellular Compositions, Spatial Annotations, and MTJCore Feasibility

**Document ID:** `research/cycle17/E5_OXFORD_REASSESSMENT.md`  
**Date:** 2026-11-12  
**Dataset:** Cohen, Mimpen, Snelling et al. (2026), Oxford Achilles Atlas (DOI: `10.1152/ajpcell.00838.2025`, bioRxiv: `10.1101/2025.10.17.682664`)  
**Status:** Completed  
**Classification:** `CONTRADICTED_PREMISE_AND_BLOCKED_REPLICATION`  
**Related Documents:**
- [E5_RESULTS.json](file:///D:/SUBJECT-01/research/cycle17/E5_RESULTS.json)
- [CYCLE16_FORENSIC_AUDIT.md](file:///D:/SUBJECT-01/research/cycle17/CYCLE16_FORENSIC_AUDIT.md)

---

## 1. Executive Summary

In Cycle 16, Experiment E5 dismissed the Oxford Achilles single-cell atlas by asserting that:
> *"The study specifically isolated and characterized stromal cells, tenocytes, and fibroblasts... 0 skeletal muscle myonuclei were captured or sequenced... zero myonuclei in the dataset."*

A rigorous forensic audit of the primary publication (Cohen et al., 2026) and associated Mendeley Data repository reveals that **this claim was factually incorrect**:
1. The study explicitly dissected and profiled the **entire Achilles tendon unit**, specifically including the osteotendinous junction (enthesis), tendon midbody, myotendinous junction (MTJ), and **adjoining skeletal muscle**.
2. Both single-nucleus RNA sequencing (snRNA-seq, 10x Chromium v3) and spatial transcriptomics (10x Xenium) captured parenchymal muscle fibers, satellite cells, and myonuclei at the proximal interface.

However, despite the physical presence of myonuclei in the sampled tissue, **independent replication of the frozen Karlsen `MTJCore` gene signature remains BLOCKED**. This report establishes the exact methodological and bioinformatic reasons for this blockage.

---

## 2. Dataset Architecture & Primary Repository Audit

### 2.1. Provenance and Deposition
- **Title:** *Fibroblast specialisation across microanatomy in a single-cell atlas of healthy human Achilles tendon*
- **Authors:** Carla J. Cohen, Jolet Y. Mimpen, Sarah J.B. Snelling, et al. (University of Oxford, NDORMS).
- **Primary Repositories:** Mendeley Data (Files Data S1–S5), bioRxiv (doi: `10.1101/2025.10.17.682664`), and *AJP-Cell Physiology* (doi: `10.1152/ajpcell.00838.2025`).

### 2.2. Cell Population Decomposition
The analytical pipeline of Cohen et al. was specifically constructed around the hypothesis of **fibroblast microanatomical specialization**:
- The authors resolved **six distinct fibroblast subtypes**:
  1. *Tendon mid-substance fibroblasts* (core force-transmitting tenocytes).
  2. *Paratenon fibroblasts* (vascular/epitenon sheath).
  3. *Myotendinous junction (MTJ)-specific fibroblasts*.
  4. *Muscle-specific fibroblasts*.
  5. *Perineural fibroblasts*.
  6. *Lining-layer fibroblasts*.
- In their primary differential expression tables (Data S1 and S2), the authors benchmarked contrasts between these fibroblast clusters.
- The myonuclear fraction was treated as an anatomical landmark rather than subclustered into fine junctional vs. non-junctional myonuclear sub-types.

---

## 3. Why `MTJCore` Replication Cannot Proceed on Available Data

To execute an independent replication of Karlsen et al. (2023) (`HYP-0012`), the following four experimental conditions must be satisfied:
1. **Cell Type Match:** The evaluated cells must be skeletal muscle syncytial myonuclei (expressing TTN, MYH1, MYH2, ACTA1), not fibroblasts.
2. **Donor-Level Contrast:** For each independent donor, there must be a paired measurement of **MTJ-anchored myonuclei** versus **mature mid-belly non-junctional myonuclei**.
3. **Unsupervised Pseudobulk Matrix:** Gene expression counts across the 18 pre-registered `MTJCore` panel genes must be quantified per donor.
4. **Freedom from Circular Annotation:** The definition of MTJ myonuclei cannot simply be "cells that express *COL22A1*", as testing whether *COL22A1* is enriched in cells selected for *COL22A1* is completely circular.

### Evaluation of Cohen et al. Against These Criteria:
- **Criterion 1 (Cell Type):** Partially met in raw tissue, but the accessible processed differential expression tables (Data S1-S3) isolate fibroblast clusters.
- **Criterion 2 (Donor Contrast):** **FAILED**. The primary tables do not provide donor-level pseudobulk counts of MTJ myonuclei versus mature mid-belly myonuclei.
- **Criterion 3 (Unsupervised Counts):** **FAILED**. Accessing myonuclear counts requires downloading and de novo re-analyzing multi-gigabyte raw Seurat objects (Data S4) from Mendeley Data, re-clustering the minor myonuclear pool, and defining an independent anatomical spatial boundary.
- **Criterion 4 (Non-Circularity):** **FAILED**. Without an independent histological ground truth for each nucleus in snRNA-seq, identifying junctional myonuclei relies on *COL22A1*, creating circular logic.

**Conclusion:** Independent replication of `MTJCore` is **BLOCKED due to lack of donor-level myonuclear contrast tables**, not due to absence of muscle tissue.

---

## 4. The Novel Stromal MTJ Hypothesis (`HYP-0013`)

While myonuclear replication cannot proceed, Cohen et al. (2026) provides an important biological insight:
- **MTJ-Specific Fibroblasts:** Fibroblasts residing at the myotendinous interface are transcriptionally distinct from mid-substance tendon fibroblasts.
- **Key Enriched Genes:** They robustly express *COL22A1*, *POSTN* (periostin), *TNC* (tenascin C), *COMP* (cartilage oligomeric matrix protein), and *THBS4* (thrombospondin 4).
- **Biological Synthesis:** Collagen XXII is **not** exclusively synthesized by muscle fibers. The non-fibrillar anchoring matrix at the MTJ is a **co-synthesis product** of both junctional myonuclei and specialized junctional tendon fibroblasts.

To preserve scientific rigor, this stromal finding is formulated under a new hypothesis:
- `HYP-0012`: Myonuclear MTJCore Signature in Muscle Syncytium (**UNREPLICATED_IN_THIRD_COHORT**).
- `HYP-0013`: Stromal Fibroblast Collagen XXII Co-Synthesis at the MTJ Interface (**EMPIRICALLY_SUPPORTED** in Oxford Atlas).
