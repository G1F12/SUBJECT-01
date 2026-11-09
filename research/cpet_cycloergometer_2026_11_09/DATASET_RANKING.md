# Cycle 10 Empirical Dataset Acquisition & Systematic Ranking

**Date**: 2026-11-09  
**Cycle**: 10  
**Repository**: `G1F12/SUBJECT-01`  
**Governing Standard**: SUBJECT-01 Evidence Gate V2 (`tools/verify_data_provenance.py`)

---

## 1. Executive Summary & Objective

The primary scientific bottleneck identified at the conclusion of Cycle 9 (EXP-0042) was the **single-subject limitation** ($N=1$) of Rehman et al. (2024). Under Evidence Gate V2 rules (`process_rehman_xlsx.py::validate_cross_subject_loso_applicability`), leave-one-subject-out (LOSO) cross-validation is mathematically prohibited on $N=1$, restricting evaluations to technical repeatability and within-subject cross-trial transfer.

To overcome this epistemic barrier without relaxing rigor or inventing synthetic proxies, Cycle 10 systematically searched and ranked open human experimental datasets from global archives (PhysioNet, Dryad, Figshare, Zenodo, OSF, PMC).

The objective is to identify, download, cryptographically anchor (SHA-256), and evaluate an independent multi-subject cohort with simultaneous mechanical workload and metabolic or physiological observations.

---

## 2. Systematic Evaluation Matrix of Candidate Repositories

| Source ID | Rank | Dataset / Source Identifier | Archive & Access | Unique Human Subjects ($N$) | Synchronous Measurements | Experimental Protocol | Files & Formats | Open Redistribution License | Download & Hash Audit | Observable M3 Parameters | Unidentifiable M3 Parameters | Validation Role |
|:---:|:---:|:---|:---|:---:|:---|:---|:---|:---|:---|:---|:---|:---|
| SRC-0073 | **1 (SELECTED)** | **PhysioNet ACTES Cycloergometer**<br>DOI: `10.13026/2qs3-kh43` | PhysioNet / AWS S3 Open Bucket<br>[Link](https://physionet.org/content/actes-cycloergometer-exercise/1.0.0/) | **$N = 18$** (Adolescent athletes: fencing, kayak, triathlon) | Beat-to-beat mechanical power ($P_{\text{mech}}$ in W), pulmonary $\dot{V}\text{O}_2$ (L/min), cardiac $RR$ interval (ms), ventilatory thresholds ($P_{\text{vt1}}, P_{\text{vt2}}$). 52,062 total records. | Graded incremental cycloergometer exercise to exhaustion preceded by resting baseline. | `test_measure.csv` (1.58 MB), `subject-info.csv` (590 B), `SHA256SUMS.txt` | Open Data Commons Attribution (ODC-By v1.0) | Direct HTTPS download, byte-verified SHA256 (`14a9df02...`, `5ac7cdd4...`). | Macroscopic mechanical-to-aerobic coupling ($\dot{E}_{\text{met}} = P / \eta$), gross mechanical efficiency ($\eta_{\text{gross}}$), cardiorespiratory $\dot{V}\text{O}_2$ response kinetics ($\tau_{\dot{V}\text{O}_2}$). | Intracellular phosphates ([PCr], [ATP], [Pi]), cytosolic pH, localized muscle recruitment per motor unit, individual muscle PCSA. | **Primary External Cross-Subject Benchmark (LOSO on $N=18$)** |
| SRC-0069 | **2** | **Rehman et al. 2024**<br>DOI: `10.1016/j.dib.2024.111114`<br>Dryad: `10.5061/dryad.08kprr59v` | Dryad Data Repository<br>[Link](https://datadryad.org/stash/dataset/doi:10.5061/dryad.08kprr59v) | $N = 1$ (Healthy adult male, 3 repeated trials) | In-bore dynamic $^{31}\text{P}$-MRS: PCr amplitude, Pi amplitude, chemical shifts ($\delta\text{pcr}, \delta\text{pi}$). 222 spectra at 6 s temporal resolution. | 3 bouts of 42 s knee extension exercise (0.5 Hz, 3 kg resistance) separated by recovery. | `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18.1 KB) | Creative Commons Zero (CC0 1.0) | Acquired and extracted to canonical JSON (`rehman2024_extracted_timeseries.json`, SHA256: `af6a396b...`). | Local intramuscular PCr recovery kinetics ($k_{\text{rec}}, \tau_{\text{rec}}$), cytosolic pH via chemical shift equation. | Mechanical power output ($P_{\text{mech}}$ in W), pedal torque, quadriceps active volume, pulmonary $\dot{V}\text{O}_2$, cardiac output. | Local High-Energy Phosphate Kinetics & Repeatability Benchmark ($N=1$) |
| SRC-0074 | **3** | **Hug et al. 2015**<br>Proc R Soc B / Dryad: `10.5061/dryad.h3b27`<br>DOI: `10.1098/rspb.2015.1908` | Dryad Data Repository<br>[Link](https://doi.org/10.5061/dryad.h3b27) | **$N = 21$** (Healthy human adults) | Multi-slice MRI quadriceps volume ($V_{\text{active}}$, $\text{cm}^3$), 3D ultrasound fascicle length, calculated PCSA, isometric knee extension torque, surface EMG. | Submaximal (20%, 50% MVC) and maximal voluntary isometric knee extensions. | `Muscle_Architecture.xlsx` (47.7 KB), `Demographics.xlsx` (46.8 KB), `Torque_and_VA.xlsx` (41.5 KB), `Neural_Drive.xlsx` (43.7 KB) | Creative Commons Zero (CC0 1.0) | Verified metadata and Dryad API record; direct browser download available. | Active quadriceps volume ($V_{\text{active}}$), individual muscle PCSA, voluntary torque, neural drive. | Dynamic high-energy phosphate kinetics ($^{31}\text{P}$-MRS absent), whole-body gas exchange ($\dot{V}\text{O}_2$ absent). | Quadriceps Morphology & Muscle Architecture Cohort Anchor ($N=21$) |
| — | **4** | **PhysioNet Malaga Treadmill CPET**<br>DOI: `10.13026/7ezk-j442` | PhysioNet<br>[Link](https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/) | $N = 992$ (Athletes and clinical cohort) | Breath-by-breath $\dot{V}\text{O}_2, \dot{V}\text{CO}_2, \dot{V}_E$, heart rate, treadmill speed and slope. | Bruce or modified Bruce treadmill graded protocol. | Multi-file text and WFDB records (>500 MB) | PhysioNet Open Access License | Accessible via PhysioNet, large population reference. | Population-scale cardiorespiratory coupling, allometric scaling of $\dot{V}\text{O}_{2,\text{max}}$. | Direct mechanical work rate in Watts (running gait efficiency variance), local muscle compartment parameters. | Secondary Population Reference for Gas Exchange |
| — | **5** | **Edwards & Kemp 2013 (InSight Trial)**<br>DOI: `10.1038/srep01182` | Scientific Reports / Institutional Access | $N = 100+$ (Mixed cohort) | Resting $^{31}\text{P}$-MRS, PCr recovery kinetics, whole-body $\dot{V}\text{O}_{2,\text{max}}$, delta efficiency. | Cycle ergometry and knee extension $^{31}\text{P}$-MRS. | Published figures and summary tables; raw data requires institutional data sharing application. | Non-open (restricted institutional access) | Data restricted to formal author application; not directly downloadable. | Macro-micro efficiency linkage between resting [PCr] and mechanical efficiency. | Raw continuous individual time-series unavailable for automated reproduction. | Theoretical Cross-Scale Coupling Benchmark |

---

## 3. Justification for Selection of PhysioNet ACTES (`SRC-0073`)

PhysioNet ACTES is selected as the **primary empirical dataset for Cycle 10** for the following rigorous scientific and technical reasons:

1. **Independent Human Cohort ($N = 18$)**: Breaks the single-subject bottleneck. With 18 distinct human participants (adolescent athletes across 3 sports: fencing, kayaking, triathlon), it enables genuine **Leave-One-Subject-Out (LOSO)** cross-validation without statistical overfitting or data leakage.
2. **Simultaneous External Mechanical Workload and Whole-Body Metabolism**: Contains beat-to-beat mechanical power output ($P_{\text{mech}}$ in Watts) recorded by an electronically braked cycloergometer, paired synchronously with breath-by-breath pulmonary oxygen consumption ($\dot{V}\text{O}_2$ in L/min) and cardiac $RR$ interval across 52,062 valid observation rows.
3. **Pristine Data Provenance**: Published on PhysioNet with an Open Data Commons Attribution (ODC-By v1.0) license and hosted on an open AWS S3 mirror. SHA-256 byte checksums match official `SHA256SUMS.txt` exactly:
   - `test_measure.csv`: `14a9df027caf00ee1dc39f1493e708c27a7da88794ff69a59442326ef7aa0516` (1,588,131 bytes)
   - `subject-info.csv`: `5ac7cdd41d9112c48121998f19927318bd6dc2241ead97a6baa5e9ae8b60c203` (590 bytes)
4. **Direct Relevance to SUBJECT-01 Model Hierarchy**: Allows direct, frozen testing of the **macroscopic aerobic coupling equation**:
   $$\dot{E}_{\text{met}} = \frac{P_{\text{mech}}}{\eta_{\text{gross}}}, \quad \dot{V}\text{O}_2(t) = \dot{V}\text{O}_{2,\text{base}} + \frac{P_{\text{mech}}(t)}{\eta_{\text{gross}} \cdot c_{\text{ox}}}$$
   against baseline null (M0) and purely empirical linear (M1) models.
5. **Clear Epistemic Boundary**: ACTES provides macro-scale metabolic coupling data, but lacks localized $^{31}\text{P}$-MRS and localized muscle MRI. This allows rigorous delineation between observable macroscopic parameters and strictly unidentifiable micro-compartment states, which is formalized in the `REMAINING_BARRIERS_MATRIX`.
