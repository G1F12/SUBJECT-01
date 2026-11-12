# STAGE 0: Dataset Discovery and Scientific Accessibility Audit
## SUBJECT-01 — Research Cycle 15: Independent Validation

**Date:** 2026-11-12  
**Working Branch:** `research/cycle15-independent-validation`  
**Base Commit:** `113dbad16f2920ede49e679596a24b53fdf4af2e` (Cycle 14 Scientific Consolidation handoff)  
**Auditor:** SUBJECT-01 Autonomous Research Team  

---

## 1. Executive Summary

Prior to initiating mathematical modeling or statistical inference for Cycle 15, an exhaustive audit of global open-access scientific data repositories was conducted across the target domains:
- **E1:** Independent Functional Strength Validation (Agonist + Antagonist sEMG, Joint Torque, Angle, Velocity, MVC).
- **E2:** Regional Tendon Mechanics (Participant-Specific Regional CSA, Local Segmental Strain, Applied Force).
- **E5:** Third Independent MTJ Cohort Replication (Human Adult Musculotendinous Junction Transcriptomics, snRNA-seq, MTJ vs. Mature Muscle Contrast).

Repositories systematically queried:
- **Zenodo** (`zenodo.org`)
- **Dryad Digital Repository** (`datadryad.org`)
- **Figshare** (`figshare.com`)
- **PhysioNet** (`physionet.org`)
- **OpenSim / SimTK** (`simtk.org`)
- **AddBiomechanics** (`addbiomechanics.org`)
- **ArrayExpress / BioStudies** (`ebi.ac.uk/biostudies/arrayexpress`)
- **NCBI Gene Expression Omnibus (GEO)** (`ncbi.nlm.nih.gov/geo`)
- **CELLxGENE** (`cellxgene.cziscience.com`)
- **PRIDE Proteomics Archive** (`ebi.ac.uk/pride`)
- **UCI Machine Learning Repository** (`archive.ics.uci.edu`)

### Status Matrix

| Experiment | Target Outcome | Open Candidate Datasets Audited | Fully Qualified Independent Datasets Found | Status | Root Blocker |
|---|---|---|---|---|---|
| **E1** | In vivo knee extension active torque prediction with agonist + antagonist EMG | 6 candidates | 0 qualified | **DATA_BLOCKED** | Absence of open datasets containing synchronized dynamometer torque, MVC, and simultaneous antagonist (hamstring) EMG across independent human participants |
| **E2** | Regional patellar/Achilles tendon strain prediction via segmented CSA | 4 candidates | 0 qualified | **DATA_BLOCKED** | Absence of participant-specific regional CSA paired with local segmental strain measurements (literature means cannot be substituted) |
| **E5** | Replication of frozen MTJCore myonuclear program in human adult MTJ | 5 candidates | 0 qualified | **DATA_BLOCKED** | All public human adult MTJ transcriptomic cohorts originate from the single discovery laboratory (Institute of Sports Medicine Copenhagen); other candidates are non-MTJ belly muscle or controlled-access |

---

## 2. Systematic Audit of Candidates for E1 (Functional Strength Validation)

### Candidate E1-1: Bird et al. (2026) — Science Robotics / Dryad
1. **Official Name:** Data for: Ultra-wideband radar to measure in vivo muscle forces
2. **DOI / Deposit URL:** [10.5061/dryad.sbcc2frmh](https://doi.org/10.5061/dryad.sbcc2frmh) / arXiv:2510.20866
3. **Authors & Publication:** Christopher S. Bird, Antonio P. L. Bo, Wei Lu, Taylor J. M. Dick. *Science Robotics* (2026).
4. **License:** Creative Commons Zero v1.0 Universal (CC0-1.0).
5. **Sample Size:** 16 participants tested; 6 participants with complete dynamic knee extension series (`DATA_Dynamic_Knee.mat`).
6. **Unit of Independence:** Individual human participant (LOSO cross-validation across 6 individuals).
7. **Presence of Required Outcomes:**
   - Agonist EMG (Vastus Lateralis): **YES** (`total_emg`, 1 channel)
   - Antagonist EMG (Biceps Femoris / Semitendinosus): **NO** (0 channels; not recorded)
   - Measured Joint Torque: **YES** (`total_torque`)
   - Joint Angle: **YES** (`total_angle`)
   - Angular Velocity: **YES** (`total_vel`)
   - MVC Normalization: **YES** (isometric ramp MVCs)
   - Active Contraction Metadata: **YES**
8. **Primary File Availability:** Direct download from Dryad (`DATA_Dynamic_Knee.mat`, 5.21 MB).
9. **Local Reproduction Feasibility:** High (files already verified and digested in repository under `research/muscle_force_biomechanics_2026_11_10/raw_data/`).
10. **Previously Used in SUBJECT-01:** **YES** (Core development cohort in EXP-0045, EXP-0046, EXP-0047; NEG-0040, NEG-0044).
11. **Possible Overlaps:** 100% overlap with previous development cycle.
12. **Protocol Compatibility:** High for dynamometer mechanics, but **FAILS INDEPENDENCE CRITERION** (used as development set) and **FAILS ANTAGONIST MEASUREMENT CRITERION** (antagonist was never recorded; proxying $\gamma$ from VL was already proven inferior to sEMG in NEG-0044).
- **Verdict for E1:** **DISQUALIFIED**. Cannot be used for independent validation; lacks measured antagonist.

---

### Candidate E1-2: Wang et al. (2022) — Zenodo
1. **Official Name:** Comprehensive Kinetic and EMG Dataset of Daily Locomotion with 6 types of Sensors
2. **DOI / Deposit URL:** [10.5281/zenodo.6457662](https://doi.org/10.5281/zenodo.6457662) / [10.5281/zenodo.6644593](https://doi.org/10.5281/zenodo.6644593)
3. **Authors & Publication:** Huawei Wang, Akash Basu, Guillaume Durandau, Massimo Sartori. University of Twente (2022).
4. **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
5. **Sample Size:** 12 healthy young adults (7 males, 5 females).
6. **Unit of Independence:** Individual participant.
7. **Presence of Required Outcomes:**
   - Agonist EMG (Rectus Femoris, Vastus Lateralis, Vastus Medialis): **YES**
   - Antagonist EMG (Biceps Femoris Long Head, Semimembranosus): **YES**
   - Measured Joint Torque: **NO** (Joint moments are computed via multi-body inverse dynamics using ground reaction forces and motion capture markers in OpenSim; no dynamometer load-cell torque)
   - Joint Angle & Angular Velocity: **YES** (Optical motion capture / IMUs)
   - Isolated Dynamometer Knee Extension Task: **NO** (Locomotion tasks: walking, running, vertical jumps, squats, lunges)
   - Individual Isometric Knee Extension MVC: **NO**
8. **Primary File Availability:** Deposited on Zenodo, but requires API access or bulk multi-gigabyte download.
9. **Local Reproduction Feasibility:** Medium.
10. **Previously Used in SUBJECT-01:** NO.
11. **Possible Overlaps:** None.
12. **Protocol Compatibility:** Incompatible task. Whole-body closed-chain locomotion introduces ground reaction force distribution uncertainty and inverse-dynamics errors ($r \approx 0.61$ correlation to portable estimators). It does not provide isolated knee extensor/flexor active torque curves.
- **Verdict for E1:** **REJECTED FOR E1 DYNAMOMETRY BENCHMARK**. Suitable for multi-joint locomotion tasks, but violates the requirement for isolated dynamometer active torque and MVC calibration.

---

### Candidate E1-3: Sanchez & Sotelo (2014) — UCI Machine Learning Repository
1. **Official Name:** EMG dataset in Lower Limb
2. **Repository ID / URL:** UCI ML Repository ID 278 / [archive.ics.uci.edu/dataset/278](https://archive.ics.uci.edu/dataset/278/emg+dataset+in+lower+limb)
3. **Authors & Publication:** O. Sanchez, J. Sotelo (2014).
4. **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
5. **Sample Size:** 22 participants (11 healthy, 11 knee pathology).
6. **Unit of Independence:** Individual participant.
7. **Presence of Required Outcomes:**
   - Agonist EMG: **YES** (Rectus Femoris, Vastus Medialis)
   - Antagonist EMG: **YES** (Biceps Femoris, Semitendinosus)
   - Knee Goniometer Angle: **YES** (Biometrics electrogoniometer FX)
   - Measured Joint Torque: **NO** (No load cell, no torque transducer, no dynamometer; only kinematic goniometer output)
   - Angular Velocity: Derived via differentiation of goniometer.
   - MVC Normalization: **NO** (Uncalibrated microvolts).
8. **Primary File Availability:** Direct download (`SEMG_DB1.rar`).
9. **Local Reproduction Feasibility:** High.
10. **Previously Used in SUBJECT-01:** NO.
11. **Possible Overlaps:** None.
12. **Protocol Compatibility:** Severely incomplete. Without measured joint torque, computing RMSE of torque prediction in fractions of MVC or assessing $R^2$ is mathematically impossible without substituting an arbitrary inertial surrogate ($\tau = I \ddot{\theta}$), which violates the fundamental prohibition against synthetic/surrogate outcomes.
- **Verdict for E1:** **REJECTED**. Critical missing endpoint: measured joint torque.

---

### Candidate E1-4: Besier et al. — SimTK / OpenSim
1. **Official Name:** Knee muscle forces during walking and running estimated from an EMG-driven model
2. **Repository URL:** [simtk.org/projects/emg_knee_model](https://simtk.org/projects/emg_knee_model)
3. **Authors & Publication:** Thor F. Besier, David G. Lloyd, et al. *Journal of Biomechanics* (2009).
4. **License:** OpenSim Academic / Research License.
5. **Sample Size:** 45 participants.
6. **Unit of Independence:** Individual human participant.
7. **Presence of Required Outcomes:**
   - Agonist EMG: **YES**
   - Antagonist EMG: **YES**
   - Measured Joint Torque: **NO** (Net knee moments are derived from inverse dynamics during gait).
   - Dynamometer Knee Extension: **NO** (Gait / running only).
- **Verdict for E1:** **REJECTED**. Task mismatch; lack of isolated isokinetic/isometric dynamometer torque.

---

### Candidate E1-5: KneE-PAD (2021) — Zenodo
1. **Official Name:** Knee Rehabilitation Exercises for Postural Assessment Dataset
2. **DOI / Deposit URL:** [10.5281/zenodo.5554625](https://doi.org/10.5281/zenodo.5554625)
3. **Authors:** Research team, Zenodo deposit (2021).
4. **Sample Size:** 31 patients.
5. **Presence of Required Outcomes:** Multi-channel sEMG and IMUs; **NO direct torque sensor**.
- **Verdict for E1:** **REJECTED**. Target outcome (joint moment) missing.

---

### Candidate E1-6: Gait120 — Figshare
1. **Official Name:** Comprehensive Human Locomotion and Electromyography Dataset
2. **DOI / Deposit URL:** [10.6084/m9.figshare.19702213](https://doi.org/10.6084/m9.figshare.19702213)
3. **Sample Size:** 120 healthy adults.
4. **Presence of Required Outcomes:** EMG during gait; **NO dynamometer knee torque**.
- **Verdict for E1:** **REJECTED**. Locomotion only, no isolated active joint torque.

---

## 3. Systematic Audit of Candidates for E2 (Tendon Regional Mechanics)

### Candidate E2-1: Kongsgaard et al. (2007) — Literature Reference
1. **Official Name:** Regional differences in patellar tendon cross-sectional area and mechanical properties
2. **Publication Reference:** *Journal of Applied Physiology* 102: 1752–1759 (2007). DOI: 10.1152/japplphysiol.00849.2006.
3. **Authors:** M. Kongsgaard, V. Reitelsperger, P. Aagaard, M. Kjær, et al.
4. **License:** Traditional journal copyright (no open data deposit).
5. **Sample Size:** 10 healthy male participants.
6. **Unit of Independence:** Individual participant (in published paper).
7. **Presence of Required Outcomes:**
   - Regional CSA reported in text/tables: Proximal: 104 ± 4 mm², Mid: 118 ± 5 mm², Distal: 127 ± 6 mm².
   - Raw individual participant CSA values: **NO** (Only group aggregate means and standard errors published; raw tabular participant data was never deposited in Dryad, Zenodo, or Figshare).
   - Local regional strain per participant: **NO** (Global elongation and average strain published).
   - Direct Synchronized Time-Series: **NO**.
8. **Primary File Availability:** **UNAVAILABLE**. No digital data repository deposit exists for this 2007 publication.
9. **Scientific Boundary Check:** Substituting published cohort means as individual participant data across a synthetic cohort is **STRICTLY PROHIBITED** by SUBJECT-01 governance. It eliminates between-subject variance, fabricates artificial statistical power, and creates a pseudo-validation artifact.
- **Verdict for E2:** **DATA_BLOCKED**. Raw individual measurements are inaccessible in public repositories.

---

### Candidate E2-2: Specimen-Specific Models of Healthy Knee — SimTK
1. **Official Name:** Mechanical Testing and Specimen-Specific Models of Natural Human Knee Biomechanics
2. **Repository URL:** [simtk.org/projects/specimenkneemod](https://simtk.org/projects/specimenkneemod)
3. **Authors & Institution:** University of Denver Center for Orthopaedic Biomechanics.
4. **License:** OpenSim / Academic Free.
5. **Sample Size:** Cadaveric knee specimens.
6. **Presence of Required Outcomes:**
   - In vivo participant regional tendon CSA: **NO** (Cadaveric specimens).
   - Local regional strain during voluntary isometric contraction: **NO**.
- **Verdict for E2:** **REJECTED**. Cadaveric tissue; no in vivo neuromuscular active loading.

---

### Candidate E2-3: Open Knee(s) — SimTK / Zenodo
1. **Official Name:** Open Knee: Open Source Models of the Knee Joint
2. **Repository URL:** [simtk.org/projects/openknee](https://simtk.org/projects/openknee)
3. **License:** CC BY-NC-SA.
4. **Presence of Required Outcomes:** Finite element tetrahedral meshes and segmented geometry; **NO live in vivo synchronized regional strain tracking across human cohorts**.
- **Verdict for E2:** **REJECTED**. Computational geometry only, no experimental strain-force time series.

---

### Candidate E2-4: Tendon Ultrasonography Aggregates (Dryad / Figshare)
Systematic search across Dryad and Figshare for keywords: `"patellar tendon" AND "cross-sectional area" AND "strain"` yielded 7 publications (e.g., Couppé et al., Magnusson et al.).
- **Audit Findings:** Every identified deposit either:
  1. Contains only aggregate summary spreadsheets (mean CSA and maximum force) without local regional strain time series, OR
  2. Measures single-point mid-substance CSA without proximal and distal tracking, OR
  3. Measures total tendon elongation via distal tuberosity tracking without resolving intra-tendinous segmental strain.
- **Verdict for E2:** **DATA_BLOCKED**.

---

## 4. Systematic Audit of Candidates for E5 (Third MTJ Cohort Replication)

### Candidate E5-1: Karlsen et al. (2023) — ArrayExpress E-MTAB-12529
1. **Official Name:** Distinct myofibre domains of the human myotendinous junction revealed by single-nucleus RNA sequencing
2. **Accession / URL:** [E-MTAB-12529](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-12529)
3. **Authors & Institution:** Karlsen et al., Institute of Sports Medicine Copenhagen.
4. **Sample Size:** 3 adult human donors (semitendinosus MTJ vs. muscle belly).
5. **Role in SUBJECT-01:** **Discovery cohort and Stage 5 validation set** (EXP-0047, FND-0047).
6. **Critical Limitation:** Donor 1 contributed 51.2% of all myonuclei in discovery.
- **Verdict for E5:** **EXPLICITLY FORBIDDEN TO REUSE**. Using discovery data as a third independent validation is fraudulent circular reasoning.

---

### Candidate E5-2: Møbjerg et al. (2025) — ArrayExpress E-MTAB-15400
1. **Official Name:** Early transcriptional response of human myotendinous junction and muscle compartments to acute resistance exercise
2. **Accession / URL:** [E-MTAB-15400](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-15400)
3. **Authors & Institution:** Møbjerg et al., Institute of Sports Medicine Copenhagen.
4. **Sample Size:** 8 human participants (vastus lateralis MTJ biopsies, acute exercise vs. rest).
5. **Role in SUBJECT-01:** **Stage 6 loading-context test set** (EXP-0047, NEG-0041).
6. **Outcome in EXP-0047:** Achieved concordant direction fraction of **0.5818**, failing the pre-registered 0.60 threshold. Sex was heavily confounded with loading condition.
- **Verdict for E5:** **EXPLICITLY FORBIDDEN TO RE-ANALYZE AS "NEW"**. Stage 6 was already completed and failed; re-labeling E-MTAB-15400 as a "successful third replication" would directly violate scientific integrity.

---

### Candidate E5-3: Karlsen et al. (2023) — ArrayExpress E-MTAB-12530
1. **Official Name:** Spatial transcriptomics of the human myotendinous junction (10x Visium)
2. **Accession / URL:** [E-MTAB-12530](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-12530)
3. **Authors & Institution:** Karlsen et al., Institute of Sports Medicine Copenhagen.
4. **Sample Size:** Sections from the exact same human donors as E-MTAB-12529.
5. **Unit of Independence:** Violates donor independence (identical biological individuals).
- **Verdict for E5:** **DISQUALIFIED**. Lacks independent human donors.

---

### Candidate E5-4: Zhao et al. (2022) — GSA-Human HRA002803
1. **Official Name:** Discovery of Muscle-Tendon Progenitor Subpopulation in Human Myotendinous Junction at Single-Cell Resolution
2. **Publication Reference:** *Research* (2022), DOI: 10.34133/2022/9760390.
3. **Repository & Accession:** Genome Sequence Archive in National Genomics Data Center (NGDC), China. Accession: **HRA002803**.
4. **Data Type:** Single-cell RNA sequencing of human MTJ tissue.
5. **Data Access Model:** **Controlled Access (DAC Approval Required)**.
6. **Local Reproduction Feasibility:** Infeasible for autonomous computing. Access requires institutional formal review, institutional ethical clearance transfer, and secure repository credentials. Raw FASTQ and count matrices cannot be fetched via open HTTP/FTP.
- **Verdict for E5:** **ACCESS_BLOCKED / CONTROLLED_ACCESS**. Cannot be accessed autonomously without external institutional authorization.

---

### Candidate E5-5: Jakobsen et al. (2021) — AJP-Cell Physiology
1. **Official Name:** RNA sequencing and immunofluorescence of the myotendinous junction of mature horses and humans
2. **Publication Reference:** *Am J Physiol Cell Physiol* 321: C742–C757 (2021). DOI: 10.1152/ajpcell.00218.2021.
3. **Authors:** Jens R. Jakobsen, Peter Schjerling, Michael Kjær, Abigail L. Mackey.
4. **Institution:** Institute of Sports Medicine Copenhagen (same research group as Karlsen and Møbjerg).
5. **Public Accession:** No open public accession number in GEO or ArrayExpress. Primary RNA-seq data was distributed in article supplementary PDF tables and upon request.
- **Verdict for E5:** **DISQUALIFIED / SAME LABORATORY**.

---

## 5. Summary of Experiment Gate Decisions

| ID | Planned Experiment | Gate Decision | Detailed Scientific Rationale |
|---|---|---|---|
| **E1** | Functional Strength Independent Validation | **DATA_BLOCKED** | All open human knee extension dynamometer datasets with joint torque lack measured antagonist (hamstring) sEMG. Datasets with antagonist EMG lack direct joint torque measurements. No open cohort fulfills all required endpoints. |
| **E2** | Tendon Regional Mechanics Validation | **DATA_BLOCKED** | No public dataset provides synchronized participant-specific regional CSA (proximal, mid, distal) paired with local strain tracking and applied force across $\ge 6$ individuals. Literature means cannot be substituted. |
| **E5** | Third MTJ Cohort Replication | **DATA_BLOCKED** | No independent open-access human adult MTJ transcriptomic dataset exists outside the Copenhagen group. E-MTAB-12529 is discovery; E-MTAB-15400 is Stage 6 (already failed); HRA002803 is controlled access. |

---

## 6. Concrete Missing Measurements Required to Unblock Future Cycles

To enable future execution of E1, E2, and E5, the scientific community or future experimental campaigns must deposit datasets meeting the following explicit criteria:

### Requirements to Unblock E1 (Functional Strength):
1. **Dynamometry:** Calibrated isokinetic and isometric knee extension and flexion joint torque (N·m) recorded on a Biodex System 4 or equivalent at $1000\text{ Hz}$.
2. **Kinematics:** Synchronous optical or rotary encoder knee joint angle ($\text{deg}$) and angular velocity ($\text{deg/s}$).
3. **Multi-Channel sEMG:**
   - Agonists: Vastus Lateralis (VL), Rectus Femoris (RF), Vastus Medialis (VM).
   - Antagonists: Biceps Femoris long head (BF), Semitendinosus (ST).
   - Bandwidth: Raw signals sampled at $\ge 1000\text{ Hz}$, bandpass filtered $20\text{--}450\text{ Hz}$.
4. **Normalization:** Isolated maximum voluntary isometric contractions (MVIC) for both knee extension and knee flexion per participant.
5. **Cohort Size:** Minimum $N = 10$ healthy adult human participants with complete metadata (mass, height, age, sex).

### Requirements to Unblock E2 (Tendon Mechanics):
1. **Morphometry:** 3T MRI or high-resolution B-mode ultrasound axial scans measuring cross-sectional area ($\text{mm}^2$) at $\ge 3$ distinct anatomical levels (proximal insertion, mid-substance, distal insertion) for each individual participant.
2. **Local Deformation:** Synchronous ultrasound tissue Doppler imaging, speckle tracking, or cine-PC MRI tracking regional displacement and computing local strain ($\Delta L / L_0$) across the three corresponding segments during loading.
3. **Loading:** Continuous force transducer or dynamometer recording patellar tendon tensile force during controlled isometric ramp contractions ($0\text{ to }100\%\text{ MVC}$).
4. **Cohort Size:** Minimum $N = 10$ independent individuals.

### Requirements to Unblock E5 (MTJ Replication):
1. **Tissue:** Human adult skeletal muscle biopsy capturing intact musculotendinous junction (interface between muscle fibers and dense tendon).
2. **Assay:** Single-nucleus RNA sequencing (10x Genomics 3' or 5' gene expression) with sequencing depth $\ge 30,000$ reads/nucleus.
3. **Cohort Independence:** Minimum $N = 4$ human donors collected by an independent clinical institution completely separate from the Copenhagen/Bispebjerg cohorts.
4. **Contrast:** Paired samples of MTJ interface vs. adjacent muscle belly from the same donors to enable donor-paired differential expression.
5. **Public Access:** Unrestricted open-access raw count matrix and metadata deposited in GEO or ArrayExpress.
