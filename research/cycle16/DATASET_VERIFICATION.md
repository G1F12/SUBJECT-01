# DATASET VERIFICATION AND PROVENANCE REPORT
## Empirical Data Ingestion for Research Cycle 16

**Document ID:** `research/cycle16/DATASET_VERIFICATION.md`  
**Date:** 2026-11-12  
**Author:** SUBJECT-01 Autonomous Research Team  
**Status:** Verified and Complete  
**Related Documents:**
- [data_manifest.json](file:///D:/SUBJECT-01/research/cycle16/data_manifest.json)
- [CYCLE15_CORRECTIONS.md](file:///D:/SUBJECT-01/research/cycle16/CYCLE15_CORRECTIONS.md)
- [E1_ISOMETRIC_STRENGTH.md](file:///D:/SUBJECT-01/research/cycle16/E1_ISOMETRIC_STRENGTH.md)
- [E2_REGIONAL_TENDON.md](file:///D:/SUBJECT-01/research/cycle16/E2_REGIONAL_TENDON.md)
- [E5_OXFORD_MTJ.md](file:///D:/SUBJECT-01/research/cycle16/E5_OXFORD_MTJ.md)

---

## 1. Overview and Ingestion Principles

In accordance with the core directives of Research Cycle 16, no synthetic data is permitted to substitute for empirical human physiological measurements. Three external independent open-access datasets were targeted, verified, and ingested:

1. **Dataset A (Biomechanics & Neuromuscular Coordination):** DPValid Collection, University of Bologna.
2. **Dataset B (Tendon Material Heterogeneity & In Vivo Strain):** Bogaerts et al. (2017), KU Leuven / PLoS ONE.
3. **Dataset C (Tendon & MTJ Microanatomy Single-Cell Atlas):** Cohen et al. (2026), University of Oxford / AJP-Cell Physiol.

---

## 2. Dataset A: DPValid Collection (Knee Isometric Neuromechanics)

### 2.1. Dataset Metadata
- **Repository:** AMS Acta, Institutional Research Repository of the University of Bologna
- **Permanent URI:** `https://amsacta.unibo.it/id/eprint/7710/`
- **Archive URL:** `https://amsacta.unibo.it/7710/1/DPValid_v0.zip`
- **DOI:** `10.6092/unibo/amsacta/7710`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Archive File Size:** 2,159,384,103 bytes (2.01 GB)

### 2.2. Cohort Demographics and Protocol
- **Sample Size:** $N = 20$ healthy human adult volunteers (HA01 through HA20).
- **Sex Distribution:** 10 Females, 10 Males.
- **Age:** $31.0 \pm 6.1$ years (range: 21.6 – 40.7 years).
- **Body Mass:** $66.8 \pm 14.5\text{ kg}$ (range: 49.0 – 98.0 kg).
- **Height:** $1.68 \pm 0.08\text{ m}$ (range: 1.55 – 1.81 m).
- **Tested Limb:** Right lower limb (instrumented dynamometry and EMG).
- **Contraction Modality:** Maximum Voluntary Isometric Contractions (MVIC) for Knee Extension (EXT) and Knee Flexion (FLEX).
- **Joint Angles:** Evaluated at two fixed knee flexion angles: $75^\circ$ and $90^\circ$ ($0^\circ = \text{full extension}$).
- **Repetitions:** 3 to 4 maximal ramp-and-hold trials per condition with standardized rest intervals.

### 2.3. Measured Channels
- **Dynamometry:** Calibrated isokinetic dynamometer (Cybex / Biodex), delivering raw and zero-lag 4th order Butterworth filtered joint torque (in $\text{N}\cdot\text{m}$).
- **Surface Electromyography (sEMG):** Synchronous bipolar sEMG according to SENIAM recommendations:
  - *Knee Extensors (Agonists for Extension / Antagonists for Flexion):* Rectus Femoris (RF), Vastus Medialis (VM), Vastus Lateralis (VL).
  - *Knee Flexors (Agonists for Flexion / Antagonists for Extension):* Biceps Femoris long head (BF), Semitendinosus (ST).
  - *Ancillary/Stabilizers:* Gastrocnemius Lateralis (GL), Contralateral VL (VL_2), Contralateral BF (BF_2).

### 2.4. Ingestion and Integrity Verification
Due to the large size of `DPValid_v0.zip` (2.01 GB), HTTP Range Request streaming was utilized to read the Central Directory (`scripts/parse_central_dir.py`) and extract the peak dynamometer torque files (`*_torques_filt_max.csv`) and sEMG envelope maxima (`*_emg_env_max_r*.csv`) along with `Demographics.csv` without loss of data integrity.
- Extracted local records: 20 subjects, 280 valid isometric peak trials.
- Output file: `research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv`.

---

## 3. Dataset B: Bogaerts et al. 2017 (In Vivo Tendon Layer Strain)

### 3.1. Dataset Metadata
- **Citation:** Bogaerts A, De Wall M, Peers K, et al. (2017). *A method to investigate tissue displacement and strain in different regions of the human Achilles tendon using ultrasound speckle tracking*. PLoS ONE 12(7): e0181364.
- **PMID / PMCID:** PMID 28723914 / PMCID PMC5519157
- **DOI:** `10.1371/journal.pone.0181364`
- **Data Source:** Supporting Information File `S1 Table` (PMC5519157).
- **License:** Open Access (CC BY 4.0).

### 3.2. Cohort Demographics and Experimental Design
- **Sample Size:** $N = 10$ healthy adults (Patiënt 1 through 10).
- **Sex Distribution:** 5 Females, 5 Males.
- **Age:** $25.8 \pm 3.1$ years (range: 21 – 33 years).
- **Body Mass:** $69.0 \pm 15.6\text{ kg}$ (range: 49 – 102 kg).
- **Limbs Tested:** Bilateral assessment (Left leg `L` and Right leg `R`).
- **Activation Modes:**
  1. *Passive Ankle Motion (PAS):* Controlled passive dorsiflexion/plantarflexion.
  2. *Isometric Plantarflexion (ISO):* Submaximal voluntary isometric plantarflexion ramp.
- **Repetitions:** 2 repetitions per leg per activation condition.
- **Timepoints:** Time 0 (initial baseline unloaded) and Time 1 (peak loading/displacement).

### 3.3. Measured Variables and Ultrasound Speckle Tracking
High-frame-rate 2D B-mode ultrasound speckle tracking was applied to quantify longitudinal intra-tendinous displacement and strain across three distinct anatomical depth layers:
1. **Superficial Layer:** Dorsal aspect, predominantly occupied by the soleus and lateral gastrocnemius sub-tendons.
2. **Middle Layer:** Central core region.
3. **Deep Layer:** Ventral aspect, closest to Kager's fat pad and predominantly medial gastrocnemius sub-tendon.
- Displacement (mm): `disp_sup_mm`, `disp_mid_mm`, `disp_deep_mm`.
- Longitudinal Strain (%): `strain_sup_pct`, `strain_mid_pct`, `strain_deep_pct`.
- Inter-layer Shearing / Strain Differences: `strain_diff_sup_mid_pct`, `strain_diff_mid_deep_pct`.
- Plantarflexion Torque: Joint torque normalized to body mass ($\text{N}\cdot\text{m}/\text{kg}$).

### 3.4. Crucial Biomechanical Limitation: Absence of Regional CSA
A rigorous audit of `Bogaerts_S1_Table.pdf` confirms that **individual regional cross-sectional areas (CSA) of each layer were not measured**.
- The ultrasound imaging plane was sagittal longitudinal (used for speckle displacement tracking), which does not provide transverse cross-sectional slice areas of the three individual sub-tendon layers.
- Consequently, while intra-tendinous strain heterogeneity and inter-layer sliding can be evaluated, regional tensile stress ($\sigma = F / \text{CSA}_{\text{layer}}$) cannot be calculated.
- **Scientific Impact:** `HYP-0010_FULL_VALIDATION` remains **BLOCKED**. The experiment is designated strictly as `E2-REGIONAL-STRAIN`.

---

## 4. Dataset C: Cohen et al. 2026 (Oxford Human Achilles Single-Cell Atlas)

### 4.1. Dataset Metadata
- **Citation:** Cohen KE, et al. (2026). *Single-cell and spatial transcriptomics reveal microanatomical fibroblast specialization across human Achilles tendon*. American Journal of Physiology - Cell Physiology.
- **DOI:** `10.1152/ajpcell.00838.2025`
- **Institution:** Kennedy Institute of Rheumatology, University of Oxford.
- **Modality:** Droplet-based single-nucleus RNA sequencing (snRNA-seq, 10x Genomics Chromium) and spatial transcriptomics (10x Genomics Visium).

### 4.2. Anatomical Profiling and Microenvironmental Zones
The study mapped the human Achilles tendon organ across four microanatomical regions:
1. **Enthesis (Osteotendinous Junction):** Insertion into the calcaneus (mineralized/unmineralized fibrocartilage).
2. **Midbody:** Central dense regular collagenous core and interfascicular stroma.
3. **Myotendinous Junction (MTJ):** Proximal transitional zone interfacing with the triceps surae muscle bellies.
4. **Paratenon:** Thin vascularized loose connective tissue sheath enclosing the tendon.

### 4.3. Cell Type Demarcation and Replication Boundary
- **Target Cell Population:** The study specifically isolated and characterized **stromal cells, tenocytes, and fibroblasts**, resolving 6 transcriptionally distinct fibroblast states (e.g., *COL22A1+* junctional fibroblasts, *COMP+/THBS4+* midbody load-bearing tenocytes, and *POSTN+/TNC+* peritenon/sheath fibroblasts).
- **Myonuclear Exclusion:** During specimen preparation, non-tendinous skeletal muscle fibers were trimmed away to isolate tendon fibroblasts. Skeletal muscle myonuclei were not retained in the cell suspension.
- **Methodological Boundary for SUBJECT-01:** Karlsen et al. (2023) established `MTJCore` (COL22A1, ITGA7, ANKRD1, MYLK4, CHRNE) within *skeletal muscle myonuclei* residing at the terminal ends of myofibers. Because Cohen et al. profiled tendon stroma/fibroblasts rather than muscle myonuclei, direct replication of the myonuclear `MTJCore` program cannot be performed on Cohen et al. However, Cohen et al. independently confirms the regional enrichment of *COL22A1* and junctional ECM genes in MTJ-associated stroma.

---

## 5. Summary Data Manifest

| Dataset ID | Source Repository / DOI | Subjects | Observations | Experimental Role | Key Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset A** | AMS Acta `10.6092/unibo/amsacta/7710` | 20 humans (10F/10M) | 280 trials | `E1-ISO`: Isometric knee torque vs. agonist + antagonist sEMG | Isometric only; dynamic isokinetic trials require separate processing. |
| **Dataset B** | PMC5519157 / PLoS ONE `10.1371/journal.pone.0181364` | 10 humans (5F/5M) | 160 observations | `E2-REGIONAL-STRAIN`: Layer-specific strain & displacement | No regional CSA; cannot calculate layer-specific stress. |
| **Dataset C** | Oxford / AJP-Cell `10.1152/ajpcell.00838.2025` | Human Achilles donors | 6 fibroblast clusters | `E5-OXFORD-MTJ`: Spatial stromal specialization audit | Fibroblasts only; myonuclei excluded; cannot replicate myonuclear MTJCore. |
