# Independent Verification and Forensic Reproducibility Report

## 1. Executive Summary

This document certifies the independent verification and mathematical replication of all findings in the SUBJECT-01 Functional Mechanics Validation study.

Every quantitative claim, statistical test, and simulation model was executed via dedicated, isolated Python verification scripts (`scripts/run_independent_verification.py`, `scripts/audit_and_recalculate_muscle.py`, `scripts/audit_and_recalculate_tendon.py`) directly from raw bytes and first-principles formulations.

---

## 2. Verification Protocol & Results Matrix

| Check Identifier | Tested Proposition / Calculation | Primary Script Verification | Test Status | Output Value Verified |
| :--- | :--- | :--- | :--- | :--- |
| **VERIF-01** | Equivalence of PCSA Convention A and Convention B | `audit_and_recalculate_muscle.py` | **PASS** | $\sigma_A \equiv \sigma_B$ ($26.41\text{ N/cm}^2$) |
| **VERIF-02** | Cycle 19 double-cosine artifact ratio | `run_independent_verification.py`| **PASS** | $1 / \cos(14^\circ) = 1.03061$ ($27.22 \to 26.41\text{ N/cm}^2$) |
| **VERIF-03** | TOST sex equivalence at multiple margins | `audit_and_recalculate_muscle.py` | **PASS** | $p_{10\%} = 0.1449$, $p_{15\%} = 0.0535$, $p_{20\%} = 0.0169$ |
| **VERIF-04** | Fold-specific M2 PCSA out-of-sample prediction | `audit_and_recalculate_muscle.py` | **PASS** | Strict LOSO $R^2 = 0.6945$, RMSE = $48.58\text{ Nm}$ |
| **VERIF-05** | Planar constant-thickness isomass force gain | `run_independent_verification.py`| **PASS** | $\sin(36^\circ)/\sin(28^\circ) = 1.25198 \implies +25.20\%$ |
| **VERIF-06** | Isomass maximum shortening velocity loss | `run_independent_verification.py`| **PASS** | $1 - \sin(14^\circ)/\sin(18^\circ) = 21.71\%$ ($l_f: 8.40 \to 6.58\text{ cm}$) |
| **VERIF-07** | Isomass Hill peak mechanical power penalty | `run_independent_verification.py`| **PASS** | $1.2520 \times (1 - 0.2171) - 1 = -1.98\%$ |
| **VERIF-08** | Power-law fatigue retention at $B = 8.45$ | `run_independent_verification.py`| **PASS** | $1.20^{-8.45} = 0.2142 \implies -78.58\%$ loss |
| **VERIF-09** | Semi-log Basquin fatigue retention at $k = -10.808$| `run_independent_verification.py`| **PASS** | $10^{-10.808 \times 0.0810} = 0.1333 \implies -86.67\%$ loss |
| **VERIF-10** | Case 2C adapted tensile stress arithmetic | `run_independent_verification.py`| **PASS** | $4800\text{ N} / 119.6\text{ mm}^2 = \mathbf{40.1338\text{ MPa}}$ |
| **VERIF-11** | Forensic origin of Cycle 19 $34.78\text{ MPa}$ error | `run_independent_verification.py`| **PASS** | $4000\text{ N} / 115.0\text{ mm}^2 = 34.7826\text{ MPa}$ |
| **VERIF-12** | Iso-durability conservation product | `run_independent_verification.py`| **PASS** | $(1 + \Delta_{\text{CSA}}) \cdot (1 + \Delta_{\text{UTS}}) \ge 1.20$ (Case 2C: $1.265 \ge 1.20$) |

---

## 3. Cryptographic and Test Suite Status

1. **Repository Consistency Check (`tools/validate_repository.py`):**
   ```text
   PASS: registries hypotheses=11, experiments=60, findings=61, negative_results=57, decisions=24, issues=26, sources=83
   PASS: 13 imported file checksums match; references/files consistent
   PASS: data provenance and evidence gate invariants satisfied
   ```
2. **Automated Unit Tests (`pytest tests/`):**
   - All 157 unit tests in the repository pass with zero errors (100% PASS in 4.30s).
   - Test suite includes strict checks on physiological specific tension bounds, M1/M2 performance parity, S1 fatigue loss, and Case 2C compensatory durability.

---

## 4. Scientific Epistemic Certification

The number of passing software tests confirms algorithmic correctness and syntactic consistency. It does NOT independently validate in vivo biological efficacy.

The findings of this report are classified strictly as **CALIBRATED_BIOMECHANICAL_SIMULATIONS** grounded on published empirical observations. Unattended biological interventions remain strictly **NO_GO**.
