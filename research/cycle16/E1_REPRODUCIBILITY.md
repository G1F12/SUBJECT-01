# REPRODUCIBILITY GUIDE: EXPERIMENT E1-ISO
## Step-by-Step Computational Instructions

**Document ID:** `research/cycle16/E1_REPRODUCIBILITY.md`  
**Date:** 2026-11-12  
**Experiment ID:** `EXP-0051`  

---

## 1. Environment & Prerequisites

- **Python Version:** 3.12+ (tested on Windows 11 PowerShell)
- **Key Dependencies:**
  ```text
  numpy >= 1.26.0
  scipy >= 1.13.0
  pandas >= 2.2.0
  scikit-learn >= 1.4.0
  ```
- No proprietary toolboxes or specialized GPU accelerators are required.

---

## 2. Data Acquisition

The dataset is ingested directly from the University of Bologna institutional repository AMS Acta (`https://amsacta.unibo.it/7710/`, DOI: `10.6092/unibo/amsacta/7710`).

To download and extract the required peak dynamometry torque and sEMG envelopes for all 20 subjects without downloading the full 2 GB archive:

```powershell
python D:\SUBJECT-01\research\cycle16\scripts\fetch_dpvalid_data.py
```

This generates:
`D:\SUBJECT-01\research\cycle16\data\dpvalid\dpvalid_isometric_trials.csv` (247 rows, 14 columns).

---

## 3. Running Model Training and Cross-Validation

Execute the Leave-One-Subject-Out (LOSO) modeling script:

```powershell
python D:\SUBJECT-01\research\cycle16\scripts\run_e1_iso.py
```

This runs:
- 20 distinct LOSO folds for Knee Extension ($N = 125$ trials).
- 20 distinct LOSO folds for Knee Flexion ($N = 121$ clean trials).
- 2000 bootstrap iterations per model to establish 95% confidence intervals.
- Generates `D:\SUBJECT-01\research\cycle16\E1_MODEL_COMPARISON.json`.

---

## 4. Expected Output Values (Verification Benchmark)

### Knee Extension:
- **M0 (Mean Baseline):** RMSE = $91.30 \pm 11.8\text{ Nm}$, $R^2 = -0.0793$
- **M1 (Agonist-only RF+VM+VL):** RMSE = $82.85 \pm 16.6\text{ Nm}$, $R^2 = 0.1112$
- **M2 (Agonist + Antagonist OLS):** RMSE = $89.10 \pm 17.5\text{ Nm}$, $R^2 = -0.0280$
- **M3 (Agonist + Antagonist Ridge):** RMSE = $82.39 \pm 13.2\text{ Nm}$, $R^2 = 0.1211$
- **M4 (Demographics + Kinematics + EMG):** RMSE = $53.45 \pm 7.9\text{ Nm}$, $R^2 = 0.6301$
- **Paired $\Delta \text{RMSE}$ (M1 - M2):** $-3.94\text{ Nm}$, paired t-test $p = 0.1426$ ($H_0$ not rejected).

### Knee Flexion (Clean):
- **M0 (Mean Baseline):** RMSE = $27.26\text{ Nm}$, $R^2 = -0.0873$
- **M1 (Agonist-only BF+ST):** RMSE = $29.80\text{ Nm}$, $R^2 = -0.2999$
- **M2 (Agonist + Antagonist OLS):** RMSE = $30.63\text{ Nm}$, $R^2 = -0.3731$
- **M3 (Agonist + Antagonist Ridge):** RMSE = $30.43\text{ Nm}$, $R^2 = -0.3554$
- **M4 (Demographics + Kinematics + EMG):** RMSE = $19.61\text{ Nm}$, $R^2 = 0.4371$
- **Paired $\Delta \text{RMSE}$ (M1 - M2):** $-2.05\text{ Nm}$, paired t-test $p = 0.2388$ ($H_0$ not rejected).
