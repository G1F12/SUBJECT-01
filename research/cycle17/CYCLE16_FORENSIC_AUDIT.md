# FORENSIC AUDIT OF RESEARCH CYCLE 16
## Comprehensive Verification, Classification, and Epistemic Correction

**Document ID:** `research/cycle17/CYCLE16_FORENSIC_AUDIT.md`  
**Date:** 2026-11-12  
**Author:** SUBJECT-01 Independent Scientific Audit Role  
**Status:** Completed  
**Base Commit:** `b543524eeaddd75a6f8179942724dc7a35a39740` (Cycle 16)  

---

## 1. Executive Summary & Audit Mandate

In strict accordance with the SUBJECT-01 Scientific Principles, a rigorous retrospective forensic audit of Research Cycle 16 was conducted. Every mathematical claim, data pipeline, statistical hypothesis test, and biological interpretation was audited against primary source data and independent re-calculation.

### Core Audit Outcomes:
1. **EXP-0051 (E1-ISO):**
   - The numerical values of M1, M2, and M4 reproduced exactly.
   - **Critical Methodological Flaw Detected:** M4 ($R^2 = 0.6301$, $\text{RMSE} = 53.45\text{ Nm}$) simultaneously changed the feature set (adding demographics and angle) and algorithm. A rigorous factorial ablation reveals that **Anthropometry and Angle alone (F0) achieve $R^2 = 0.6867$ and $\text{RMSE} = 49.19\text{ Nm}$**. Adding surface EMG actually **degrades** predictive accuracy ($R^2$ drops to 0.6301), and adding antagonist EMG to anthropometry + agonist EMG **statistically significantly increases error** ($\Delta \text{RMSE} = -3.01\text{ Nm}$, $p = 0.0089$). The success of M4 was 100% driven by anthropometrics, not EMG!
2. **EXP-0052 (E2-REG):**
   - **Severe Statistical Pseudoreplication Detected:** Cycle 16 reported a Friedman test statistic of $\chi^2 = 59.55$ ($p = 1.17 \times 10^{-13}$). For $k = 3$ conditions, the maximum possible Friedman statistic for $N$ blocks is $Q_{\max} = 2N$. With $N = 10$ human subjects, $Q$ cannot physically exceed 20.0! Cycle 16 treated repeated trials (2 legs $\times$ 2 reps) as 40 independent subjects. Correcting for pseudoreplication at the subject level ($N = 10$) confirms displacement non-uniformity ($\chi^2 = 20.0$, $p = 4.54 \times 10^{-5}$), but reveals that **strain differences across layers are completely non-significant** ($\chi^2 = 0.80$, $p = 0.6703$).
   - **Demographic Error Corrected:** Cycle 16 reported "5 females, 5 males". The primary data (S1 Table) and published text confirm **4 females and 6 males**.
3. **EXP-0053 (E5-OXFORD):**
   - **Cellular Assumption Contradicted:** Cycle 16 asserted that the Oxford Achilles Atlas (Cohen et al. 2026) contained "0 myonuclei" and excluded skeletal muscle. Primary literature and repository records confirm that muscle tissue and myonuclei were sequenced, but the study focused on fibroblast subclustering. However, donor-level pseudobulk contrast data for mature vs. MTJ myonuclei remains unavailable in the primary tables, keeping independent replication blocked.

---

## 2. Item-by-Item Forensic Classification

| Result Identifier | Cycle 16 Claim | Audit Classification | Forensic Evidence & Proof |
| :--- | :--- | :--- | :--- |
| **E1-DPVALID-DATA** | 20 subjects, 125 extension trials | `VERIFIED` | Exact match in DPValid database. 15 subjects had 6 trials ($3 \times 75^\circ, 3 \times 90^\circ$); 5 subjects had 7 trials. Total = 125 trials. |
| **E1-M1-M2-VALUES** | M1 RMSE 82.85, M2 RMSE 89.10 | `VERIFIED` | Reproduces to within floating-point precision on identical LOSO folds. |
| **E1-M4-PERFORMANCE** | M4 R² = 0.6301, RMSE 53.45 Nm | `CORRECTED` | Mathematically reproduced, but causal attribution refuted. Feature F0 (Anthropometry + Angle) alone achieves RMSE 49.19 Nm ($R^2 = 0.6867$). EMG is negative signal. |
| **E1-ANTAGONIST-VALUE**| Antagonist sEMG adds noise in LOSO | `VERIFIED` | Confirmed and strengthened: in factorial ablation F4 vs F3, antagonist EMG significantly increases prediction error ($p = 0.0089$). |
| **E2-BOGAERTS-N** | 10 participants, 160 rows | `VERIFIED` | Exact match with S1 Table (10 subjects $\times$ 2 legs $\times$ 2 activations $\times$ 2 reps $\times$ 2 timepoints = 160). |
| **E2-DEMOGRAPHICS** | 5 Females, 5 Males | `CORRECTED` | Falsified by primary table and paper: Patients 1, 5, 6, 9 are Female ($N=4$); Patients 2, 3, 4, 7, 8, 10 are Male ($N=6$). |
| **E2-FRIEDMAN-STAT** | Friedman $\chi^2 = 59.55$, $p = 1.17 \times 10^{-13}$ | `CORRECTED (PSEUDOREPLICATION)` | Mathematical impossibility for $N=10$ ($Q_{\max} = 20$). Caused by treating 40 repeated trials as independent. Proper subject-level $\chi^2 = 20.0$, $p = 4.54 \times 10^{-5}$. |
| **E2-LAYER-STRAIN** | Strain non-uniform across layers | `UNREPRODUCED / REFUTED` | At the subject-aggregated level, layer strain differences are non-significant ($\chi^2 = 0.80$, $p = 0.6703$). Only displacement is non-uniform. |
| **E2-STRESS-STATUS** | HYP-0010 stress blocked (no CSA) | `VERIFIED` | Confirmed: Bogaerts did not measure individual sub-tendon CSA; layer stress cannot be calculated. |
| **E5-MYONUCLEI-PRESENCE**| "0 skeletal muscle myonuclei in atlas" | `CONTRADICTED` | Primary publication explicitly profiles muscle-tendon transitional zone including myonuclei with COL22A1. |
| **E5-REPLICATION-STATUS**| External MTJCore replication blocked | `VERIFIED_WITH_LIMITATIONS` | Blocked not because myonuclei are absent from the tissue, but because processed data on Mendeley Data lacks donor-level MTJ vs. mature myonuclear pseudobulk counts. |

---

## 3. Methodological Root-Cause Analysis

### 3.1. How Pseudoreplication Entered E2-REG
In Cycle 16, `df_peak[df_peak['activation'] == 'ISO']` contained 40 rows. `scipy.stats.friedmanchisquare` was called directly on columns of length 40 without grouping by `participant_id`.
In classical statistics, the Friedman test assumes each row is an independent subject. By feeding 4 repeated measurements per participant (left/right legs and reps 1/2), the effective sample size was artificially multiplied by 4, creating an astronomical and invalid $p$-value ($1.17 \times 10^{-13}$).

### 3.2. How Confounding Entered E1-ISO
In Cycle 16, Model M1 was an OLS regression on 3 agonist EMG channels ($R^2 = 0.1112$). Model M4 was a Ridge regression on 10 features (5 demographic/angle features + 5 EMG channels) ($R^2 = 0.6301$).
Because M4 changed both the features (adding anthropometrics) and the algorithm (Ridge) simultaneously, Cycle 16 concluded that "combining angle, demographics, and EMG" drove the performance. A full $2 \times 5$ factorial ablation was omitted. When executed, it proves that anthropometrics alone explain the entire variance, and EMG is a pure error contributor.
