# EXPERIMENT E5-OXFORD-MTJ: HUMAN MTJ REPLICATION AUDIT
## Evaluation of Oxford Achilles Single-Cell Atlas for MTJCore Verification

**Experiment ID:** `EXP-0053`  
**Document ID:** `research/cycle16/E5_OXFORD_MTJ.md`  
**Date:** 2026-11-12  
**Dataset:** Cohen et al. (2026), Oxford Achilles Single-Cell Atlas (DOI: `10.1152/ajpcell.00838.2025`)  
**Status:** Completed (Anatomical & Cellular Boundary Formally Defined)  
**Related Documents:**
- [E5_RESULTS.json](file:///D:/SUBJECT-01/research/cycle16/E5_RESULTS.json)
- [CYCLE15_CORRECTIONS.md](file:///D:/SUBJECT-01/research/cycle16/CYCLE15_CORRECTIONS.md)
- [DATASET_VERIFICATION.md](file:///D:/SUBJECT-01/research/cycle16/DATASET_VERIFICATION.md)

---

## 1. Scientific Aim & Background

In Research Cycle 15, replication of the human `MTJCore` gene program (COL22A1, ITGA7, ANKRD1, MYLK4, CHRNE) was attempted using post-exercise vastus lateralis biopsies from Møbjerg et al. (E-MTAB-15400). The replication failed to reach the acceptance threshold (Stage 6 cross-validation score 0.5818 < 0.60, recorded as `NEG-0044`).

With the recent publication of the Oxford Human Achilles Single-Cell and Spatial Atlas (Cohen et al., 2026, Kennedy Institute of Rheumatology), our goal was to assess whether this new spatial dataset could provide independent biological replication of the human myotendinous junction program.

---

## 2. Dataset Architecture & Cell Population Audit

Cohen et al. (2026) applied single-nucleus RNA sequencing (snRNA-seq, 10x Chromium) and spatial transcriptomics (10x Visium) to human Achilles tendon specimens partitioned into four distinct microanatomical regions:
1. **Enthesis:** Osteotendinous insertion into calcaneus.
2. **Midbody:** Central force-transmitting tendon core.
3. **Myotendinous Junction (MTJ):** Proximal transitional zone bordering calf muscle bellies.
4. **Paratenon:** Surrounding vascular sheath.

### 2.1. Critical Cell Type Audit
- **Tendon Isolation Protocol:** In Cohen et al., surgical dissections deliberately removed adjacent skeletal muscle tissue to enrich for connective tissue fibroblasts. Specimen digestion protocols were optimized for stromal dissociation.
- **Myonuclear Capture:** **0 skeletal muscle myonuclei were captured or sequenced**. The resulting dataset comprises 6 distinct sub-populations of tenocytes and fibroblasts (e.g., *COL1A1+*, *COL3A1+*, *COMP+*, *POSTN+*, *THBS4+*), alongside minor vascular endothelial and immune cell fractions.

---

## 3. Replication Feasibility Assessment

### 3.1. Why Direct `MTJCore` Replication Cannot Proceed
Karlsen et al. (2023) (*Nat Commun*, E-MTAB-12529) established the `MTJCore` program specifically in **junctional myonuclei**—the specialized multinucleated syncytial nuclei of skeletal muscle fibers physically anchored to tendon collagen through alpha-7 integrin and collagen XXII:
- These myonuclei simultaneously express high levels of skeletal muscle contractile transcripts (TTN, MYH1, MYH2, ACTA1) AND specialized junctional attachment genes (COL22A1, ITGA7, ANKRD1).
- Because Cohen et al. (2026) isolated tendon fibroblasts and excluded skeletal muscle myofibers, there are **zero myonuclei** in the dataset.
- Attempting to evaluate myonuclear signature correlation in a pure fibroblast dataset represents a fundamental cell-type error.

### 3.2. Biological Confirmation of Stromal MTJ Specialization
While myonuclei are absent, Cohen et al. provides independent validation of **junctional stroma**:
- Fibroblasts situated in the proximal MTJ zone exhibit robust transcriptional specialization, showing marked upregulation of *COL22A1*, *POSTN* (periostin), *TNC* (tenascin C), and *COMP*.
- This demonstrates that collagen XXII is not merely synthesized by junctional myonuclei; adjacent junctional tenocytes/fibroblasts actively participate in building the non-fibrillar anchoring matrix at the interface.

---

## 4. Lineage Resolution of MTJ Datasets

The resolution of the three core MTJ datasets in SUBJECT-01 is summarized below:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     SUBJECT-01 MTJ COHORT LINEAGE                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. E-MTAB-12529 (Karlsen et al. 2023, Nat Commun):                     │
│    True human semitendinosus MTJ biopsy (junction vs belly vs tendon). │
│    Discovered MTJCore myonuclei. STATUS: VALID DISCOVERY COHORT.      │
├────────────────────────────────────────────────────────────────────────┤
│ 2. E-MTAB-15400 (Møbjerg et al. 2025):                                 │
│    Vastus lateralis mid-belly needle biopsy (post-exercise).           │
│    Failed replication (NEG-0044). CAUSE: Anatomical mismatch           │
│    (mid-belly muscle biopsy has no MTJ tissue).                        │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Cohen et al. 2026 (Oxford Human Achilles Atlas):                    │
│    Achilles microanatomical zones (Enthesis, Midbody, MTJ, Paratenon). │
│    Enriched for fibroblasts/tenocytes; myonuclei excluded.            │
│    STATUS: Replicates MTJ stromal niche; myonuclear replication BLOCKED│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Conclusion & Action Items

- **Replication Status:** External independent replication of the myonuclear `MTJCore` signature remains **BLOCKED** due to the absence of independent single-cell datasets containing intact human muscle-tendon junction myofibers.
- **Future Requirement:** True replication will require single-nucleus profiling of surgical specimens where both muscle fibers and tendon collagen are co-harvested (e.g., hamstring graft harvests or tendon transfer procedures).
- **Tissue Engineering Insight:** Cellular models of human MTJ enhancement must culture both myotubes and junctional fibroblasts in co-culture, as both compartments express reciprocal elements of the *COL22A1*-integrin attachment apparatus.
