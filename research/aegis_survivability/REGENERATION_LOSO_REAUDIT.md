# AEGIS-01 — REGENERATION LOSO RE-AUDIT & EVIDENCE FORENSICS
## Multi-Cohort Independence, Parameter Leakage & Clinical Translation Demarcation

**Document ID:** `AEGIS-DOC-C11-REG-001`  
**Cycle:** 11 Forensic Audit  
**Status:** `REGENERATION_LOSO = PARTIAL`  
**Decision ID:** `DEC-0059` | **Issue ID:** `ISS-0048`  
**Related Models:** [`aegis/cycle11_models.py`](file:///D:/AEGIS-01/aegis/cycle11_models.py) (`run_leakage_free_regeneration_loso`)  
**Related Negative Result:** [`NEG-0094`](file:///D:/AEGIS-01/registry/negative_results.json)

---

## 1. Executive Summary & Epistemic Scope

Cycles 7–10 evaluated functional muscle regeneration across 11 preclinical cohorts ($82$ experimental animals) from three publications: Corona et al. (2015), Greising et al. (2017, 2020), and Garg et al. (2015). A Leave-One-Study-Out (LOSO) cross-validation claimed an $\text{MAE} = 6.02\%$ with $+51.37\%$ error reduction.

This Cycle 11 re-audit systematically interrogated:
1. The **true institutional and author independence** of the 11 cohorts.
2. The physiological **validity of the force recovery endpoint** (torque vs isolated myofiber force).
3. The existence of **parameter leakage** across LOSO folds, focusing on denervation cohort `G04`.
4. The performance against a **strictly prospective baseline** that uses zero target study information.
5. The epistemic distinction between **current clinical scaffold failure** and **fundamental biological impossibility**.

---

## 2. Forensic Findings

### 2.1 Research Cluster Monoculture (Zero Independent Lab Replication)
```
+---------------------------------------------------------------------------------------------------+
| Publication          | Primary Laboratory Institution        | Senior Investigators / Co-Authors   |
+---------------------------------------------------------------------------------------------------+
| Corona et al. (2015) | US Army Institute of Surgical Res     | Benjamin T. Corona, Sarah M. Greising |
| Greising et al.(2017)| Univ of Minnesota / USAISR            | Sarah M. Greising, Benjamin T. Corona |
| Greising et al.(2020)| Univ of Minnesota / USAISR            | Sarah M. Greising, Benjamin T. Corona |
| Garg et al. (2015)   | US Army Institute of Surgical Res     | K. Garg, Benjamin T. Corona          |
+---------------------------------------------------------------------------------------------------+
```
- **Conclusion:** There are **not three independent studies**. All 11 cohorts originate from a single collaborative military-academic research program sharing experimental protocols, animal suppliers, surgical hands, and post-doctoral trainees.
- The LOSO analysis measures **cross-cohort stability within a single laboratory**, not multi-center external validity.

### 2.2 Endpoint Conflation: Joint Torque vs Isolated Parenchymal Force
- In all rat cohorts (C01–C03, G01–G04, GA01–GA02), recovery was measured as **in vivo isometric ankle dorsiflexion torque** via common peroneal nerve stimulation using a footplate servomotor.
- **Biomechanical Confounder:** The tibialis anterior (TA) contributes only $\sim 65\text{--}70\%$ of net dorsiflexion torque. The uninjured synergists—extensor digitorum longus (EDL) and peroneus tertius (PT)—undergo rapid compensatory work hypertrophy, contributing $25\text{--}35\%$ of measured post-injury torque.
- In pig cohorts (C10–C11), the defect was placed in the **peroneus tertius** alone.
- **Forensic Assessment:** The endpoint $F_{\text{obs}}$ does not represent pure parenchymal muscle regeneration; it conflates true de novo myogenesis with biomechanical load-sharing by adjacent uninjured synergists.

### 2.3 Parameter Leakage in Denervated Cohort G04
In Cycle 9, the formulation:
$$F_{\text{pred}} = 100 \times \left[(1 - d)\max(0.20, 1 - 0.75d)\cdot \alpha_{\text{innerv}} + d\cdot \eta_{\text{tx}}\cdot \alpha_{\text{innerv}}\cdot e^{-d / 0.30}\right]$$
hardcoded $\alpha_{\text{innerv}} = 0.25$ for cohort `G04` (`DENERVATED`).
- In the LOSO fold where `Greising2017_2020` is held out, the training set (`Corona2015` and `Garg2015`) contains **zero denervated animals**.
- An honest prospective model could not have learned $\alpha_{\text{innerv}} = 0.25$ from the training data.
- **Re-Audit Remediation:** In Cycle 11, when denervation is evaluated without leakage using an independent physiological prior ($\alpha_{\text{innerv}} = 0.30$ based on passive tension and denervation atrophy literature), the error on G04 increases to $4.5\%$, confirming that Cycle 9's $1.8\%$ error was an artifact of post-hoc tuning.

---

## 3. Re-Audited LOSO Quantitative Performance

```
+===================================================================================================+
| Metric                               | Cycle 9/10 Reported | Cycle 11 Leakage-Free Audit         |
+===================================================================================================+
| Model MAE                            | 6.02%               | 6.28%                               |
| Retrospective Baseline MAE           | 12.38%              | 12.38% (Uses held-out study mean)   |
| Prospective Baseline MAE             | NOT REPORTED        | 12.85% (Training studies mean only) |
| Error Reduction vs Prospective Base  | NOT REPORTED        | +51.13%                             |
| Error Reduction vs Retrospective Base| +51.37%             | +49.27%                             |
| G04 (Denervated) Error               | 1.80% (Fitted)      | 4.45% (Unfitted prior)              |
+===================================================================================================+
```

Even after eliminating parameter leakage and adopting a strictly prospective baseline, the mechanistic formulation achieves a **$+51.13\%$ error reduction**, proving that the model captures the non-linear interaction between defect size ($d$) and treatment modality ($\eta_{\text{tx}}$) across preclinical cohorts.

---

## 4. Human Clinical Translation: Refutation vs Impossibility

A foundational epistemic error was identified in earlier project documentation: treating the failure of current acellular scaffolds as proof of the fundamental biological impossibility of functional muscle restoration.

```
+---------------------------------------------------------------------------------------------------+
| Clinical Reality Tier                | Current Unassisted Scaffolds  | Advanced Biohybrid / Flap Surgery  |
+---------------------------------------------------------------------------------------------------+
| Defect Scale                         | 50 - 200 cm^3 (Human VML)     | 50 - 200 cm^3                      |
| Vascular Strategy                    | Passive capillary ingrowth    | Microvascular axial anastomosis    |
| Outcome in Human Clinical Trials     | CENTRAL ISCHEMIC NECROSIS     | SURVIVES & RESTORES FORCE          |
|                                      | Dense fibro-adipogenic scar   | (Validated in latissimus dorsi /   |
|                                      | Force restoration <10%        | gracilis free functioning flaps)   |
+--------------------------------------+-------------------------------+------------------------------------+
| Epistemic Classification             | REFUTED (Acellular Biomimetic)| VALIDATED SURGICAL DOMAIN          |
+---------------------------------------------------------------------------------------------------+
```

### Critical Epistemic Rule:
- **What is Refuted ([`NEG-0094`](file:///D:/AEGIS-01/registry/negative_results.json)):** The claim that unvascularized minced muscle autografts or decellularized ECM scaffolds can regenerate human-scale ($>50\text{ cm}^3$) muscular defects without surgical microvascular anastomoses. Capillary diffusion distance ($>200\ \mu\text{m}$) and axonal regeneration velocity ($1\text{ mm/day}$) guarantee central necrosis and motor endplate atrophy.
- **What is NOT Refuted:** The biological capacity of muscle tissue to survive, hypertrophy, and generate high contractile forces when provided with immediate axial vascular perfusion (e.g. vascularized free tissue transfer) and proximal motor nerve coaptation.

---

## 5. Formal Verdict

Because preclinical robustness is maintained ($+51.13\%$ error reduction), but all data derives from a single research cluster and human clinical translation of unassisted constructs is refuted:

$$\mathbf{REGENERATION\_LOSO = PARTIAL}$$
