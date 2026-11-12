# E5: Third Independent Human MTJ Cohort Replication & Myonuclear Program Audit

**Experiment ID:** EXP-0050  
**Negative Result Ref:** NEG-0047  
**Cycle:** 15  
**Date:** 2026-11-12  
**Working Branch:** `research/cycle15-independent-validation`  
**Status:** `DATA_BLOCKED`  
**Primary Endpoint:** Directional concordance fraction ($S_{\text{rep}} \ge 0.60$) of the frozen 1,176-gene MTJCore myonuclear transcriptional program against an independent external human cohort.  

---

## 1. Scientific Context and Prior Replication Audit

The musculotendinous junction (MTJ) represents the specialized anatomical transition zone mediating tensile force transfer from intracellular sarcomeric actin-myosin complexes across the sarcolemma to the collagenous extracellular matrix of the tendon. 

Within the SUBJECT-01 research program, the **MTJCore** initiative investigated whether human MTJ-associated myonuclei possess a stable, evolutionarily conserved transcriptional program that could be targeted for tissue reinforcement.

### 1.1 Critical Audit of Prior Stages (Stages 5, 6, 7)
It is a violation of scientific truth to claim that MTJCore has undergone "three successful independent replications". A rigorous re-examination of the evidence demonstrates:

| Evaluation Stage | Accession / Cohort | Empirical Outcome | Evidentiary Status | Key Scientific Vulnerability |
|---|---|---|---|---|
| **Stage 5** | ArrayExpress E-MTAB-12529 (Karlsen et al., 2023) | 1,083 / 1,176 concordant directions (**92.09%**), $S_{\text{rep}} = 3.434$, CAMERA $p < 0.01$ | Validated in Discovery Data | **Donor Dominance:** Donor 1 contributed **51.2%** of all myonuclei in the dataset. Cross-donor leave-one-donor-out (LODO) showed vulnerability to single-donor dropout. |
| **Stage 6** | ArrayExpress E-MTAB-15400 (Møbjerg et al., 2025) | Concordance fraction **0.5818** against fixed 0.60 threshold | **FAILED REPLICATION (NEG-0041)** | **Criterion Failure:** 0.5818 failed the pre-registered 0.60 directional threshold. Result: `NO_CLEAR_CONDITION_ASSOCIATION`. Furthermore, biological sex was confounded with training condition. |
| **Stage 7** | PRIDE PXD029307 & PXD072245 | Myonuclear protein enrichment $p \approx 0.00047$; **50 / 216** concordant protein directions | Partial Protein Support | **Modality Dissociation:** Only 50 of 216 quantified proteins matched transcriptional directions. Fibroblast stromal component was completely unconfirmed in 3D bioprinted constructs (NEG-0042). |

**Summary of Evidence:** The frozen program demonstrated high within-study concordance in Stage 5, but **failed its pre-registered replication threshold in Stage 6** ($0.5818 < 0.60$) and demonstrated substantial transcriptional-translational discordance in Stage 7. Therefore, a genuine, third, external independent human cohort is an absolute scientific requirement.

---

## 2. Pre-Registration Protocol (Locked Prior to Outcome Assessment)

To prevent post-hoc hypothesis trimming or threshold inflation, the complete statistical analysis plan was locked prior to candidate screening.

### 2.1 Frozen Gene Panel
- **Source:** MTJCore Stage 5 frozen panel derived from human semitendinosus snRNA-seq.
- **Size:** Exactly 1,176 genes.
- **Anchor Genes:** *COL22A1, ABI3BP, ABLIM1, SPARC, TNC, ITGB1, LAMB2, COL6A1, COL6A2, COL6A3, VCL, PXN, TLN1*.
- **Direction Assignment:** 
  - `+1` (MTJ-enriched): Over-expressed in myonuclei at the tendon insertion relative to muscle belly.
  - `-1` (Belly-enriched): Under-expressed at the insertion relative to muscle belly.
- **Marker Guard:** Pre-registered exclusion of the top 6 unsupervised clustering marker genes to eliminate circular annotation bias.

### 2.2 Gene Inclusion and Quality Filtering Criteria
1. **Expression Floor:** A gene must have $\ge 10$ raw counts in $\ge 2$ independent donors in the validation dataset.
2. **Missing Marker Handling:** Genes absent from the validation dataset platform are excluded from the test denominator ($N_{\text{tested}}$).
3. **Adequacy Guard:** If the validation dataset provides $< 50\%$ coverage of the 1,176 frozen genes ($N_{\text{tested}} < 588$), the experiment must be formally declared **`INCONCLUSIVE`** due to platform insufficiency.

### 2.3 Donor Independence Strategy
- The unit of biological independence is the **human donor**.
- Single-cell and single-nucleus observations must be aggregated by donor using a **pseudobulk generalized linear model** (edgeR quasi-likelihood F-test or DESeq2 with donor blocking factors):
  $$\log_2 (\mu_{g, d, c}) = \alpha_g + \beta_{g, d} + \gamma_g \cdot \text{Condition}_c$$
  where $\beta_{g, d}$ blocks for donor $d$, and $\gamma_g$ estimates the MTJ-vs-mature log-fold-change.
- Treating individual nuclei from the same donor as independent statistical samples is strictly forbidden (inflates degrees of freedom by $1000\times$).

### 2.4 Correlation-Aware Null Distribution
- Because co-regulated genes share biological pathways, assuming an independent Bernoulli coin-toss null ($p = 0.5$) generates drastically deflated false-positive $p$-values.
- The null distribution must be generated via **correlation-preserving gene label permutations** (or the CAMERA procedure), estimating inter-gene correlation ($\rho$) directly from donor residuals.

### 2.5 Primary Endpoint and Decision Criteria
- **Primary Endpoint:** Directional concordance fraction:
  $$S_{\text{rep}} = \frac{N_{\text{concordant}}}{N_{\text{tested}}}$$
- **Fixed Pre-Registered Decision Threshold:**
  - **`REPLICATED`:** $S_{\text{rep}} \ge 0.60$ AND permutation $p < 0.05$ across $\ge 3$ independent donors.
  - **`NOT_REPLICATED`:** $S_{\text{rep}} < 0.60$ OR permutation $p \ge 0.05$.
  - **`INCONCLUSIVE`:** Panel coverage $< 50\%$ or donor count $N < 3$.
  - **`DATA_BLOCKED`:** Absence of public independent human MTJ transcriptomic datasets.

---

## 3. Global Systematic Search for Candidate Cohorts

An exhaustive audit of NCBI GEO, EBI ArrayExpress/BioStudies, PRIDE, CELLxGENE, and GSA-Human was executed.

### 3.1 Candidate Evaluations

1. **Karlsen et al. (2023) — ArrayExpress E-MTAB-12529:**
   - The discovery cohort of MTJCore Stage 5.
   - **Verdict:** **EXPLICITLY FORBIDDEN TO REUSE**. Testing a hypothesis on its own discovery data is circular.

2. **Møbjerg et al. (2025) — ArrayExpress E-MTAB-15400:**
   - Already evaluated in Stage 6 (EXP-0047, NEG-0041).
   - Produced $S_{\text{rep}} = 0.5818$, which failed the 0.60 threshold.
   - **Verdict:** **EXPLICITLY FORBIDDEN TO RE-TEST AS "NEW"**. Re-packaging an existing failed experiment as a new replication violates scientific integrity.

3. **Karlsen et al. (2023) 10x Visium — ArrayExpress E-MTAB-12530:**
   - Spatial transcriptomics sections obtained from the **exact same 3 human donors** as E-MTAB-12529.
   - **Verdict:** **DISQUALIFIED**. Lacks donor biological independence.

4. **Zhao et al. (2022) — GSA-Human HRA002803 (*Research*, 2022):**
   - Single-cell RNA sequencing of human MTJ progenitor subpopulations ($N=4$ donors).
   - Deposited in GSA-Human (China National Center for Bioinformation).
   - **Access Model:** **Controlled Access (DAC Approval Required)**.
   - Access requires formal institutional Data Access Committee submission, inter-institutional ethical agreement, and credentials. Files cannot be openly fetched via public API or download.
   - **Verdict:** **DATA_BLOCKED / CONTROLLED_ACCESS**. Inaccessible to autonomous computational pipelines.

5. **Jakobsen et al. (2021) — *AJP-Cell Physiol*:**
   - Bulk RNA-seq of horse and human MTJ tissue.
   - Same Copenhagen laboratory (Mackey/Kjær).
   - Raw sequencing counts were not deposited under an open repository accession number.
   - **Verdict:** **DISQUALIFIED**. Same research group; lacks open public accession.

6. **General Skeletal Muscle Databases (GTEx, CELLxGENE):**
   - Hundreds of human muscle RNA-seq samples exist (e.g., GTEx vastus lateralis, gastrocnemius).
   - However, all GTEx and general human muscle atlas samples were harvested strictly from the **muscle belly** (mid-substance).
   - **None contain the anatomical musculotendinous junction interface.**
   - Belly-only tissue cannot evaluate the MTJ-versus-mature contrast.
   - **Verdict:** Anatomically unqualified.

---

## 4. Separation of Biological and Translational Dimensions

To prevent unwarranted extrapolation, the SUBJECT-01 framework formally separates six biological dimensions that must never be conflated:

1. **RNA Direction Replication:** Demonstrating that a set of mRNAs are co-expressed at the MTJ interface.
2. **Donor Robustness:** Demonstrating that the signal is consistent across diverse human ages, sexes, and genetic backgrounds without single-donor dominance.
3. **Cell-Type Specificity:** Distinguishing myonuclear transcription from tenocyte, fibroblast, endothelial, and macrophage contributions.
4. **Load Adaptation:** Demonstrating that mechanical loading or resistance training dynamically alters MTJ transcription (which failed in Stage 6).
5. **Protein Translation Support:** Demonstrating that mRNA abundance translates into stable structural junctional protein complexes (only 23% concordant in Stage 7).
6. **Mechanical Function & Failure Resistance:** Demonstrating that the molecular junction withstands higher peak tensile stress without avulsion or micro-tearing.

### Core Scientific Conclusion:
**A positive RNA direction concordance in a sequencing assay does NOT prove enhanced tendon strength, does NOT prove improved force transmission, and does NOT justify biological interventions.**

---

## 5. Formal Verdict

```text
E5_STATUS = DATA_BLOCKED
```

### Registered Result:
- **ID:** NEG-0047
- **Statement:** "In global open-access scientific repositories, there is currently no third independent, publicly accessible human adult musculotendinous junction transcriptomic dataset outside the Copenhagen research group (E-MTAB-12529 and E-MTAB-15400). Other identified candidate datasets are either controlled-access (HRA002803), identical donors (E-MTAB-12530), or anatomically restricted to mid-belly muscle (GTEx)."
- **Evidentiary State of MTJCore:** Remains unvalidated on a third cohort. Stage 5 showed 92.09% concordance in discovery data; Stage 6 failed (0.5818 vs. 0.60, NEG-0041); Stage 7 showed weak proteomic concordance (50/216).

---

## 6. Requirements to Unblock E5

To unblock MTJCore Stage 8 and execute E5 in future cycles, an external dataset must be deposited that meets the following criteria:

1. **Sample Cohort:** Human adult skeletal muscle biopsies capturing intact musculotendinous junction with paired muscle belly control from $\ge 4$ independent individuals.
2. **Institutional Independence:** Collected by an independent clinical/academic institution outside the University of Copenhagen / Bispebjerg Hospital network.
3. **Sequencing Platform:** Single-nucleus RNA sequencing (10x Genomics Chromium) with $\ge 30,000$ reads/nucleus and comprehensive nuclear isolation protocols.
4. **Data Access:** Unrestricted open-access count matrices and donor metadata deposited in NCBI GEO or ArrayExpress.
