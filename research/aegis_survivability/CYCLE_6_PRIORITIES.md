# Research Priorities & Operational Directives for Cycle 6

**Program:** AEGIS-01 / Research Cycle 6  
**Document ID:** `AEGIS-PRIORITIES-C6`  
**Preceding Deliverable:** `CYCLE_5_REPORT.md`  
**Target Repositories:** `D:\AEGIS-01`, `D:\SUBJECT-01`

---

## 1. Executive Mission for Cycle 6

Research Cycle 5 successfully dismantled multiple layers of circular reasoning, synthetic dataset reliance, and invalid environmental conflations. Cycle 6 must build directly upon these rectified foundations:

> **Core Mandate:** Transition from forensic error rectification to constructive physical and biological modeling, focusing strictly on verifiable mechanisms that resolve the primary bottlenecks identified in Cycle 5: **neuromuscular transmission failure, osteodermal vascular stress concentration, and uncompensable thermal storage.**

---

## 2. Six Primary Research Priorities for Cycle 6

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CYCLE 6 RESEARCH ROADMAP                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Multi-Compartment Transient Core-Shell Thermal Dynamics (Lag Modeling)   │
│ 2. Bi-Phasic Micro-CT FEA of Living Osteoderms Under Dynamic Impact         │
│ 3. Targeted Neurotization & Agrin-MuSK Neuromuscular Safety Factor Engine   │
│ 4. Anti-Fibrotic Temporal Gating (FAP Apoptosis & Costamere Transmission)   │
│ 5. Multi-Subject Holdout VML Validation on Additional Clinical Cohorts      │
│ 6. Formal SUBJECT-01 PR #9 Re-Migration & Integration Completion           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Priority 1: Multi-Compartment Transient Core-Shell Thermal Modeling
- **Context:** In Cycle 5, the lumped-parameter thermodynamic model predicted a warming rate of $0.1120\text{ K/min}$ under Montain's Heavy Tropical protocol ($600\text{ W}$, $50\%$ RH), whereas observed human rectal warming was $0.065 \pm 0.015\text{ K/min}$.
- **Cycle 6 Objective:** Construct a multi-node transient bioheat model (Gagge two-node / Fiala model) separating:
  - Deep core (viscera, brain).
  - Muscle active core (primary heat generation site).
  - Peripheral cutaneous shell (dermis, subcutaneous fat).
  - Sweating wet-clothing latent enthalpy pool.
- **Key Deliverable:** Eliminate the lumped-parameter discrepancy by explicitly modeling the $12 - 15\text{ minute}$ convective circulatory delay between contracting muscle and rectal temperature monitoring.

---

### Priority 2: Bi-Phasic Microstructural FEA of Living Osteoderms Under Dynamic Impact
- **Context:** Cycle 5 proved that living osteoderm compressive strength is capped at $\approx 175\text{ MPa}$ due to vascular canals occupying $22 - 38\%$ of bone volume.
- **Cycle 6 Objective:** Implement high-resolution 3D finite element analysis (FEA) based on micro-CT scans of hydrated xenarthran and crocodilian osteoderms:
  - Evaluate dynamic crack propagation at strain rates $\dot{\epsilon} = 10^1 - 10^3\text{ s}^{-1}$.
  - Test whether oriented elliptical or sinusoidal canal geometries can reduce peak circumferential stress concentrations ($\sigma_{\theta\theta}$) by $> 40\%$.
- **Success Metric:** Determine the theoretical upper physical bound of compressive yield strength achievable by living, perfusable bone.

---

### Priority 3: Targeted Neurotization & Agrin-MuSK NMJ Safety Factor Engine
- **Context:** Cycle 5 demonstrated that acellular scaffolds fail to restore voluntary strength because the neuromuscular transmission Safety Factor collapses below 1.0 ($SF < 1.0$).
- **Cycle 6 Objective:** Develop a quantitative computational model of acetylcholine release, post-synaptic receptor clustering, and MuSK kinase phosphorylation:
  - Model how targeted local slow-release Agrin-mimetic hydrogels affect quantal content $m$ and endplate potential ($\text{EPP}$) amplitude.
  - Evaluate whether autologous motor nerve transfers (e.g. transfer of an expendable motor branch from the tibial or obturator nerve) can shorten re-innervation distance below $30\text{ mm}$, preventing irreversible endplate atrophy.

---

### Priority 4: Anti-Fibrotic Temporal Gating (FAP Apoptosis & Costamere Transmission)
- **Context:** Chronic TGF-$\beta 1$ / Smad3 signaling prevents Fibro-Adipogenic Progenitor (FAP) apoptosis, converting them into myofibroblasts that deposit dense non-contractile collagen, increasing passive muscle stiffness by $400\%$.
- **Cycle 6 Objective:** Model the temporal kinetics of localized anti-fibrotic intervention:
  - Formulate a 2-compartment myogenic-fibrogenic kinetic differential equation model.
  - Test the hypothesis that localized delivery of an anti-Smad3 morpholino or decorin nanoparticle specifically during days 5 to 10 post-injury eliminates fibrotic accumulation without inhibiting early satellite cell activation.
  - Quantify the recovery of lateral force transmission through the costameric dystrophin-glycoprotein complex.

---

### Priority 5: Independent Holdout Validation on Additional Clinical Cohorts
- **Context:** Model 13 was evaluated on the 13-patient Dziki 2016 cohort and failed against a featureless baseline on out-of-sample RMSE.
- **Cycle 6 Objective:** Acquire and benchmark additional published human clinical trial datasets:
  - Sicari et al. (2014) 5-patient cohort.
  - Gentile et al. (2019) human muscle defect series.
  - Standardize pre-registration of evaluation metrics before unblinding external data.

---

### Priority 6: Canonical SUBJECT-01 PR #9 Re-Migration & Integration Completion
- **Context:** PR #9 is currently open at `G1F12/SUBJECT-01/pull/9`. The 15 namespace collisions with upstream Cycle 10 & 11 were shifted in AEGIS-01.
- **Cycle 6 Objective:** 
  - Update `research/aegis_survivability/` on the integration branch with the Cycle 5 shifted registries and forensic deliverables.
  - Verify that SUBJECT-01's CI pipeline runs and passes cleanly with zero namespace collisions.
  - Prepare PR #9 for formal review and canonical merge.

---

## 3. Strict Prohibitions & Quality Gates for Cycle 6

1. **NO Fictitious Dates:** Do not project speculative technology arrival years.
2. **NO Synthetic Datasets:** No simulated or fabricated patient records may ever be substituted for authentic clinical trials.
3. **MANDATORY Baseline Comparison:** No complex model may be announced as useful unless it beats an independent featureless baseline in pre-registered out-of-sample metrics.
4. **NO Identity Masquerading:** Verification of mathematical identities (e.g. LEFM equations) must never be reported as independent empirical holdout predictions.
5. **ZERO Clashing IDs:** Strict maintenance of zero namespace collisions with `D:\SUBJECT-01`.
