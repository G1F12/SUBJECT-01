# AEGIS-01 — CYCLE 10B FORENSIC AUDIT REPORT
## Epistemic Re-evaluation, Primary Data Reconstruction & Pre-Registration Integrity

**Document ID:** `AEGIS-REP-C10B-001`  
**Cycle:** 10B (Forensic Rectification & Epistemic Audit)  
**Date:** November 2026  
**Auditor:** AEGIS-01 Autonomous Verification Engine  
**Repositories:** `D:\AEGIS-01` & `D:\SUBJECT-01`  
**PR #9 Status:** Open (Sync Repaired; Zero Automatic Merge)  
**Primary Verdicts:**
- `PR9_SYNC = PASS` (Commit pushed, files verified on GitHub remote)
- `LI2010_HOLDOUT = PARTIAL` (MAE 0.27833 GPa; 8% moisture overpredicted outside $1\sigma$)
- `TOMBOLATO2010_HOLDOUT = NOT_VERIFIED` (Figure digitization; wrong DOI; post-hoc mode factor)
- `PRE_REGISTRATION = UNVERIFIED` (Hash reproducible, but chronological priority unverified)
- `REGENERATION_LOSO = PARTIAL` (Preclinically stable; single cluster; denervation prior dependent)
- `TARGET-CPE45 = NOT_EXTERNALLY_VALIDATED` (Mass-energy consistent; threshold demarcated)

---

## 1. Executive Summary: What Went Wrong in Cycle 10

Cycle 10 achieved important methodological steps by identifying synthetic data rows in Cycle 9 and acknowledging the post-hoc calibration of Zhang et al. (2018). However, an independent forensic re-examination revealed four severe vulnerabilities:

```
+===================================================================================================+
| Vulnerability                        | Discovered Defect                 | Corrected Status in 10B        |
+===================================================================================================+
| 1. Git Publication Failure           | Commit 84d00db never pushed;      | Remote synced via worktree;    |
|                                      | PR #9 remained at 57337f4         | full remote SHA confirmed      |
| 2. Li et al. (2010) Data Drift       | Claimed [2.30, 1.65, 0.85] GPa;   | Reconstructed exact primary    |
|                                      | True is [2.34, 1.56, 0.85] GPa    | [2.34, 1.56, 0.85] GPa         |
| 3. Tombolato et al. (2010) Evidence  | Wrong DOI (Lozano bioceramics);   | Rectified to 10.1016/j.actbio  |
|                                      | Bending curves lack tables        | .2009.06.033; NOT_VERIFIED     |
| 4. Pre-Registration Conflation       | Hash matched code string, but was | Demarcated 4-tier taxonomy;    |
|                                      | co-committed with results         | PRE_REGISTRATION_UNVERIFIED    |
+===================================================================================================+
```

---

## 2. Phase 0: Git Integrity & Remote Synchronization Audit

### 2.1 The Missing Commit 84d00db
- **Claimed in Cycle 10:** Integration commit `84d00db` unified AEGIS-01 and SUBJECT-01.
- **Forensic Ground Truth:** Commit `84d00db` existed **strictly locally** on `feature/aegis-survivability-research` in `D:\SUBJECT-01`. Because `git push` was never executed (due to a silent Git Credential Manager hang on Windows caused by an invalid `gh.exe` credential helper path), the remote PR #9 branch on GitHub remained frozen at `57337f42a262aae47a989d548e52376e2bcc6602`.
- **Impact:** Reviewers inspecting GitHub PR #9 saw no `CYCLE_10_RESEARCH_REPORT.md` or Cycle 10 model files.
- **Remediation:**
  1. Credential helper was re-routed through `wincred` and verified with GitHub API token.
  2. Worktree `D:\SUBJECT-01-wt-pr9` was created to isolate the PR #9 integration branch.
  3. All test suites in both repositories passed (AEGIS-01: 149/149; SUBJECT-01: 120/120).
  4. Remote push was executed and verified via GitHub REST API.

---

## 3. Phase 1: Forensic Audit of Li et al. (2010) Bovine Horn Sheath

### 3.1 Primary Source Ground Truth
- **Citation:** Bing-Wei Li, H.-P. Zhao, Xi-Qiao Feng, W.-W. Guo, Sicong Shan (2010). *Experimental study on the mechanical properties of the horn sheaths from cattle*. **Journal of Experimental Biology**, 213(3): 479–486. DOI: [10.1242/jeb.035428](https://doi.org/10.1242/jeb.035428).
- **True Measured Tensile Moduli (Mean $\pm$ SD, $n=6$ per group, $N=18$ specimens total):**
  - Desiccated ($0\%$ moisture): **$2.34 \pm 0.12\text{ GPa}$**
  - Ambient equilibrium ($8\%$ moisture): **$1.56 \pm 0.06\text{ GPa}$**
  - Fully hydrated ($19\%$ moisture): **$0.85 \pm 0.09\text{ GPa}$**
- **Cycle 10 Model Predictions:** $[2.189, 2.022, 1.072]\text{ GPa}$.

### 3.2 Exact Quantitative Error Recalculation

```
+---------------------------------------------------------------------------------------------------+
| Moisture | Obs (Mean +- SD) | Cycle 10 Pred | Signed Error | Abs Error | 1-Sigma Band | Violation |
+---------------------------------------------------------------------------------------------------+
| 0%       | 2.34 +- 0.12 GPa | 2.189 GPa     | -0.151 GPa   | 0.151 GPa | [2.22, 2.46] | 0.031 GPa |
| 8%       | 1.56 +- 0.06 GPa | 2.022 GPa     | +0.462 GPa   | 0.462 GPa | [1.50, 1.62] | 0.402 GPa |
| 19%      | 0.85 +- 0.09 GPa | 1.072 GPa     | +0.222 GPa   | 0.222 GPa | [0.76, 0.94] | 0.132 GPa |
+---------------------------------------------------------------------------------------------------+
| SUMMARY  | Mean: 1.5833 GPa | Mean: 1.761 G | Bias: +0.178 | MAE: 0.27833 GPa | RMSE: 0.30851 GPa |
+---------------------------------------------------------------------------------------------------+
```

- **Corrected Model MAE:** **$0.27833\text{ GPa}$** (Cycle 10 claimed $0.235\text{ GPa}$ using corrupted inputs).
- **Corrected Model RMSE:** **$0.30851\text{ GPa}$**.
- **Model Bias:** **$+0.17767\text{ GPa}$** (systematic overprediction).
- **Uncertainty Analysis:** At $8\%$ moisture, the model overpredicts by $+0.462\text{ GPa}$, which is **$6.7$ standard deviations** above the empirical mean, violating the $1\sigma$ margin by $0.402\text{ GPa}$.

### 3.3 Dual Baselines: Retrospective vs Prospective
1. **Retrospective Test-Mean Baseline:**
   - $\bar{E}_{\text{test}} = (2.34 + 1.56 + 0.85)/3 = 1.58333\text{ GPa}$.
   - $\text{MAE}_{\text{test\_mean}} = \mathbf{0.50444\text{ GPa}}$.
   - Error reduction: **$+44.82\%$** (Cycle 10 claimed $+52.95\%$).
   - *Limitation:* Uses target test set information; not a prospective prediction.
2. **Prospective Training-All Baseline (Zhang 2018 All 28 Rows):**
   - $\bar{E}_{\text{train\_all}} = 0.868214\text{ GPa}$.
   - $\text{MAE}_{\text{train\_all}} = \mathbf{0.72726\text{ GPa}}$.
   - Error reduction: **$+61.73\%$**.
3. **Prospective Training-Tension Baseline (Zhang 2018 Table 3 Dry Tension):**
   - $\bar{E}_{\text{train\_tens}} = 1.83500\text{ GPa}$.
   - $\text{MAE}_{\text{train\_tens}} = \mathbf{0.58833\text{ GPa}}$.
   - Error reduction: **$+52.69\%$**.

### 3.4 Verdict: PARTIAL
While the model outperforms all three baselines by $44\%\text{--}61\%$, the sample size consists of only $N=3$ aggregate group means ($df=2$), and the severe overprediction at $8\%$ moisture indicates that the Hill-type plasticization threshold ($w_c = 0.18$) delays softening compared to cattle horn keratin. Status is downgraded from `PASS` to `PARTIAL`.

---

## 4. Phase 2: Forensic Audit of Tombolato et al. (2010)

### 4.1 Erroneous Citation & DOI Discrepancy
Cycle 10 cited Tombolato et al. with DOI `10.1016/j.actbio.2009.08.033`.
- **True Paper at 08.033:** Lozano D. et al., *Osteostatin-loaded bioceramics stimulate osteoblastic growth and differentiation*, Acta Biomater. (2010).
- **True DOI of Tombolato et al.:** **`10.1016/j.actbio.2009.06.033`** (*Microstructure, elastic properties and deformation mechanisms of horn keratin*, Acta Biomater. 6(2): 319–330).

### 4.2 Mode Conflation & Data Extraction Audit
1. **Table 1 Reports Compression, Not Bending:**
   In the authentic publication, Table 1 provides numerical data exclusively for **ambient dry compression** tests (Longitudinal $1.8\text{--}2.4\text{ GPa}$, Radial $1.1\text{--}1.3\text{ GPa}$, Transverse $1.0\text{--}1.2\text{ GPa}$).
2. **Bending Coupouns Are Graphical Only:**
   Three-point bending tests are presented in Figure 8 and Figure 9 as qualitative stress-strain curves. **No numerical table of flexural Young's moduli exists in the paper.**
3. **Post-Hoc Parameter Injection:**
   Cycle 10 introduced `mode_factor = 0.90` for bending. In Cycles 8 and 9, only tension ($0.75$) and compression ($1.00$) were defined. Introducing $0.90$ specifically to match digitized bending curves is post-hoc calibration, not an independent test.
4. **Hydration Discrepancy:**
   Cycle 10 evaluated wet bending at $w = 0.40$, whereas Tombolato et al. reported rehydration moisture at $\sim 35\%$ ($w \approx 0.35$).
5. **Verdict:** **`TOMBOLATO2010_HOLDOUT = NOT_VERIFIED`**.

---

## 5. Phase 3: Cryptographic Pre-Registration & Independence Audit

### 5.1 Four-Tier Epistemic Taxonomy
To eliminate ambiguity, AEGIS-01 enforces a strict four-tier taxonomy:

```
+---------------------------------------------------------------------------------------------------+
| Classification Tier              | Formal Definition                     | Cycle 10 Status        |
+---------------------------------------------------------------------------------------------------+
| 1. REPRODUCIBLE_HASH             | Deterministic SHA-256 digest of exact | VERIFIED               |
|                                  | string FROZEN_MODEL_CODE              | (225d6994d5b9... valid)|
| 2. CHRONOLOGICALLY_PRE_REGISTERED| Locked & timestamped BEFORE exposure  | UNVERIFIED             |
|                                  | to the target dataset in Git ledger   | (Co-committed)         |
| 3. INDEPENDENT_TEST_SET          | Different authors, lab, and specimens | VERIFIED (Li 2010)     |
| 4. TRUE_BLIND_HOLDOUT            | Target values completely hidden from  | UNVERIFIED (Literature |
|                                  | modelers and LLM context              | published in 2010)     |
+---------------------------------------------------------------------------------------------------+
```

- **Hash Audit:** The hash `225d6994d5b97539f52c1ef5968ee8ac5f96a8b4da37c1e057e983b5f2faea25` belongs strictly to the in-memory string variable `FROZEN_MODEL_CODE.strip()`, not to any standalone file on disk.
- **Chronological Audit:** Both the hash declaration and the test evaluations were introduced in commit `0f627c84899dc502ea6f123f68013e60f9002384`. There is no prior commit or public registration proving temporal precedence.
- **Verdict:** **`PRE_REGISTRATION = UNVERIFIED`**.

---

## 6. Summary of Downgraded Statuses in Cycle 10B

```
====================================================================================================
METRIC / TARGET             | CYCLE 10 CLAIM          | CYCLE 10B CORRECTED AUDIT | RATIONALE
====================================================================================================
PR9 Synchronization         | PASS (Unverified)       | PASS (Verified via API)   | Commit pushed to GitHub
Li et al. (2010) Holdout    | VALIDATED PASS (+52.9%) | PARTIAL (+44.8% to +61.7%)| 8% overprediction; N=3
Tombolato et al. (2010)     | VALIDATED PASS (+88.1%) | NOT_VERIFIED              | Figure digitization; 0.90
Pre-Registration Integrity  | VERIFIED (SHA-256)      | UNVERIFIED                | Co-committed with results
Regeneration LOSO           | VALIDATED (MAE 6.02%)   | PARTIAL                   | Single lab; alpha=0.25
TARGET-CPE45                | NOT_EXTERNALLY_VALIDATED| NOT_EXTERNALLY_VALIDATED  | Consistent 270,450 J/K
====================================================================================================
```
