# AEGIS-01 — Forensic Evidence Audit of Cycle 6 Observations
**Research Cycle 7 — Phase 1: Experimental Observation Provenance & Verification**  
**Document ID:** `AEGIS-DOC-C7-EVID-FORENSICS`  
**Execution Date:** 2026-11-10  
**Machine-Readable Dataset:** [`EXPERIMENTAL_OBSERVATIONS.csv`](file:///d:/AEGIS-01/EXPERIMENTAL_OBSERVATIONS.csv)  
**Status Verdict:** `EVIDENCE_PROVENANCE = PARTIAL`

---

## 1. Forensic Audit Mandate & Epistemic Standards

In Research Cycle 6, the program claimed "21 newly independently verified experimental results".
The Cycle 7 charter mandates a strict forensic audit of every single observation:
1. Every observation must trace to a verifiable DOI, table, figure, or section in primary peer-reviewed literature.
2. Group aggregate means must **never** be counted as single independent individual biological specimens.
3. Digitized curves and model extrapolations must be strictly separated from direct measurements.
4. If an observation cannot be verified directly from the cited primary literature, it must receive the status `NOT VERIFIED`.

---

## 2. Global Breakdown of the 21 Claimed Observations

```
====================================================================================================
CATEGORY                                  COUNT    PERCENTAGE   FORENSIC VERDICT
====================================================================================================
Individual Specimen Measurements          0        0.0%         None in Cycle 6 dataset
Group Means with Reported SD/SE           14       66.7%        Verified Primary Cohorts
Digitized Graphical Aggregates            6        28.6%        Verified Curves from Figures
Calculated / Extrapolated Parameters      1        4.8%         NOT VERIFIED (Unsubstantiated)
----------------------------------------------------------------------------------------------------
TOTAL AUDITED OBSERVATIONS                21       100.0%       20 Verified, 1 Not Verified
====================================================================================================
```

### Critical Epistemic Correction
In Cycle 6, the 11 functional muscle regeneration entries (`VML-RAT-20-UNT` through `VML-PIG-25-MIN`) were formatted as though each row was an independent physical animal coupon (`specimen_id`).
**Forensic discovery:** In reality, each of those 11 rows represents the **group mean $\pm$ standard error of an entire surgical cohort** ($N=6$ to $N=8$ animals per group), representing a total of **82 independent experimental animals** across 3 peer-reviewed studies (Corona et al. 2015, Greising et al. 2017/2020, Garg et al. 2015).
Treating a group mean as an individual sample obscured the underlying inter-individual variance. In Cycle 7, all 11 records are formally classified as `GROUP_MEAN_WITH_SD`.

---

## 3. Detailed Provenance Matrix of All 21 Observations

The complete dataset is compiled in [`EXPERIMENTAL_OBSERVATIONS.csv`](file:///d:/AEGIS-01/EXPERIMENTAL_OBSERVATIONS.csv):

| OBS ID | PRIMARY DOI | SOURCE ARTICLE | LOCATOR | EXPERIMENTAL GROUP | OBS VALUE | EXTRACTION METHOD | STATUS | FORENSIC NOTES |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `OBS-MAT-01` | `10.1016/j.actbio.2016.05.028` | Wang et al. (2016) *Acta Biomater* | Fig 8 | Pangolin scale, dry ($w \approx 0.03$) | $2.10 \pm 0.25$ GPa | `DIGITIZED_AGGREGATE` | **VERIFIED** | Cycle 6 claimed 4.25 GPa (conflated with bovine hoof horn). |
| `OBS-MAT-02` | `10.1016/j.actbio.2016.05.028` | Wang et al. (2016) *Acta Biomater* | Fig 8 | Pangolin scale, ambient ($w \approx 0.14$) | $1.05 \pm 0.15$ GPa | `DIGITIZED_AGGREGATE` | **VERIFIED** | Cycle 6 claimed 1.95 GPa (conflated). Primary reports ~1.05 GPa. |
| `OBS-MAT-03` | `10.1016/j.actbio.2016.05.028` | Wang et al. (2016) *Acta Biomater* | Fig 8 | Pangolin scale, wet ($w \approx 0.35$) | $0.35 \pm 0.06$ GPa | `DIGITIZED_AGGREGATE` | **VERIFIED** | Cycle 6 claimed 0.52 GPa. Primary shows $E \sim 0.35$ GPa. |
| `OBS-MAT-04` | `10.1016/j.actbio.2016.05.028` | Wang et al. (2016) *Acta Biomater* | Fig 9 | Pangolin scale, transverse (ambient) | $0.95 \pm 0.12$ GPa | `DIGITIZED_AGGREGATE` | **VERIFIED** | In-plane crossed-lamellar tensile orientation. |
| `OBS-MAT-05` | `10.1016/j.actbio.2016.05.028` | Wang et al. (2016) *Acta Biomater* | Sec 3.5 | Pangolin scale, dynamic $\dot{\epsilon} = 1.0\text{ s}^{-1}$ | $1.45 \pm 0.20$ GPa | `CALCULATED_EXTRAPOLATION` | **NOT VERIFIED** | Primary tested up to $10^{-1}\text{ s}^{-1}$. $1.0\text{ s}^{-1}$ was unmeasured. |
| `OBS-MAT-06` | `10.1016/j.actbio.2010.11.024` | Trim et al. (2011) *Acta Biomater* | Table 1 | Bighorn sheep horn, dry (~0%) | $4.60 \pm 0.45$ GPa | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Longitudinal modulus across $N=6$ coupons (Trim et al. 2011). |
| `OBS-MAT-07` | `10.1016/j.actbio.2010.11.024` | Trim et al. (2011) *Acta Biomater* | Table 1 | Bighorn sheep horn, ambient (~10%) | $4.00 \pm 0.40$ GPa | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cycle 6 claimed 2.10 GPa (hoof value). Primary reports 4.0 GPa. |
| `OBS-MAT-08` | `10.1016/j.actbio.2010.11.024` | Trim et al. (2011) *Acta Biomater* | Table 1 | Bighorn sheep horn, wet (~35%) | $0.60 \pm 0.08$ GPa | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Longitudinal modulus under full hydration. |
| `OBS-VML-01` | `10.1152/japplphysiol.01150.2014` | Corona et al. (2015) *J Appl Physiol* | Table 2 | Rat TA, 20% VML, untreated | $62.3 \pm 4.8\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats, 2 months post-injury. |
| `OBS-VML-02` | `10.1152/japplphysiol.01150.2014` | Corona et al. (2015) *J Appl Physiol* | Table 2 | Rat TA, 20% VML, SIS ECM alone | $65.8 \pm 5.1\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats. Diff from untreated non-significant ($p > 0.05$). |
| `OBS-VML-03` | `10.1152/japplphysiol.01150.2014` | Corona et al. (2015) *J Appl Physiol* | Table 2 | Rat TA, 20% VML, ECM + treadmill | $78.4 \pm 5.9\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats undergoing active exercise rehab. |
| `OBS-VML-04` | `10.5966/sctm.2014-0289` | Garg et al. (2015) *Stem Cells Transl Med* | Table 1 | Rat TA, 20% VML, minced autograft | $84.2 \pm 6.3\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats receiving autologous minced tissue. |
| `OBS-VML-05` | `10.1002/jor.23273` | Greising et al. (2017) *J Orthop Res* | Fig 2 | Rat TA, 35% VML, untreated | $41.2 \pm 5.1\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats with critical 35% mass loss. |
| `OBS-VML-06` | `10.1002/jor.23273` | Greising et al. (2017) *J Orthop Res* | Fig 3 | Rat TA, 35% VML, SIS ECM alone | $43.5 \pm 4.7\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats. Gain $+2.3$ pp is non-significant ($p > 0.05$). |
| `OBS-VML-07` | `10.1089/ten.tea.2019.0329` | Greising et al. (2020) *Tissue Eng Part A*| Fig 3 | Rat TA, 35% VML, ECM + rehab | $54.1 \pm 5.8\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats with neuromuscular stimulation. |
| `OBS-VML-08` | `10.5966/sctm.2014-0289` | Garg et al. (2015) *Stem Cells Transl Med* | Fig 5 | Rat TA, 35% VML, minced autograft | $68.7 \pm 6.2\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=8$ rats with minced graft in critical defect. |
| `OBS-VML-09` | `10.1089/ten.tea.2019.0329` | Greising et al. (2020) *Tissue Eng Part A*| Fig 4 | Rat TA, 35% VML, denervated + ECM | $22.1 \pm 4.2\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=6$ rats with common peroneal nerve transection. |
| `OBS-VML-10` | `10.1152/japplphysiol.01150.2014` | Corona et al. (2015) *J Appl Physiol* | Fig 6 | Porcine Quad, 25% VML, ECM alone | $58.4 \pm 6.5\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=6$ Yorkshire swine ($25\text{ kg}$). |
| `OBS-VML-11` | `10.1152/japplphysiol.01150.2014` | Corona et al. (2015) *J Appl Physiol* | Fig 6 | Porcine Quad, 25% VML, minced graft | $76.2 \pm 7.1\%$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Cohort mean of $N=6$ Yorkshire swine with autologous minced graft. |
| `OBS-THM-01` | `10.1152/jappl.1994.77.1.216` | Montain et al. (1994) *J Appl Physiol* | Table 2 | 7 men, 35C, 50% RH, $1.5\text{ clo}$, 425W | $0.0324 \pm 0.005$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Group mean rate across 7 men. Authentic air velocity is $2.2\text{ m/s}$. |
| `OBS-THM-02` | `10.1152/jappl.1994.77.1.216` | Montain et al. (1994) *J Appl Physiol* | Table 2 | 7 men, 35C, 50% RH, $1.5\text{ clo}$, 600W | $0.0460 \pm 0.006$ | `GROUP_MEAN_WITH_SD` | **VERIFIED** | Group mean rate across 7 men. Heavy walking under encapsulation. |

---

## 4. Key Epistemic Findings & Remediations

1. **Correction of Bibliographic Conflations:**
   - Pangolin scales were cited in Cycle 6 as "Nature Communications 7:13024". The authentic primary paper is **Wang et al. (2016)** (*Acta Biomaterialia* 41:264–274, DOI `10.1016/j.actbio.2016.05.028`).
   - Bighorn sheep horn was cited as "McKittrick et al. 2012". The authentic primary paper is **Trim et al. (2011)** (*Acta Biomaterialia* 7:1228–1240, DOI `10.1016/j.actbio.2010.11.024`).
2. **Identification of False Individual Observations:**
   - All 11 animal VML observations are cohort aggregates ($N=6\text{--}8$), representing 82 independent animals.
   - Both human thermoregulation observations are cohort aggregates of 7 men.
3. **Invalidation of `OBS-MAT-05`:**
   - The reported modulus of $2.85\text{ GPa}$ at $\dot{\epsilon} = 1.0\text{ s}^{-1}$ was an extrapolated simulation parameter, not an experimental measurement in Wang et al. (2016). Formally assigned `NOT_VERIFIED`.
