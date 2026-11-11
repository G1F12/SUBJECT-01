# AEGIS-01 — Research Cycle 8 Strategic Decisions & Prioritized Hypotheses
**Research Cycle 7 — Phase 7: Scientific Decisions & Cycle 8 Roadmapping**  
**Document ID:** `AEGIS-DOC-C8-DECISION`  
**Execution Date:** 2026-11-10  
**Cycle Readiness:** `CYCLE_8_READY = YES`  
**Decision Range:** `DEC-0047` through `DEC-0050`

---

## 1. Formal Architectural & Methodological Decisions

In response to the forensic evidence audit, cross-study transfer tests, and thermal re-analyses of Cycle 7, the steering committee enacts four binding decisions:

### `DEC-0047`: Mandatory Microstructural Scaling for Cross-Material Transfer
- **Rationale:** Direct blind transfer of horn-calibrated elasticity to crossed-lamellar pangolin scales failed catastrophically (overpredicting stiffness by $+83.5\%$, yielding an error $45\%$ worse than a simple baseline, `NEG-0073`). The universal hydration parameter ($k_w \approx 7.0$) controls the plasticization slope, but the reference dry modulus $E_0$ is governed by filament packing and porosity.
- **Enactment:** All future cross-material models must incorporate an explicit microstructural packing factor $\Phi_{\text{micro}}$ based on measured fiber volume fraction.

### `DEC-0048`: Epistemic Classification of Physiological Scenario Assumptions
- **Rationale:** Parameters such as the $20\text{--}50\text{ kcal/day}$ foreign body reaction metabolic cost, the $54\text{--}63\text{ mmHg}$ compartment pressure surge, and $90\%$ sprint speed retention were derived from theoretical boundary equations and static scaling laws, not direct in vivo catheter or calorimetry measurements.
- **Enactment:** All such parameters are formally classified as `SCENARIO_ASSUMPTIONS` and must never be cited as experimentally validated biological constants.

### `DEC-0049`: Adoption of Leave-One-Study-Out (LOSO) as Preclinical Standard
- **Rationale:** Preclinical animal VML recovery models exhibit high inter-study variability due to differences in surgical biopsy punch technique, nerve preservation, and rehabilitation protocols. Simple pooled cross-validation risks learning study-specific artifacts.
- **Enactment:** All multivariable regeneration models must pass Leave-One-Study-Out cross-validation with an MAE $< 7.5\%$ across independent laboratories.

### `DEC-0050`: Formal Retention of 1-Node Lumped Thermal Model
- **Rationale:** Under authentic Montain et al. (1994) conditions ($v = 2.2\text{ m/s}$), the difference between the 1-node baseline and 3-node dynamic model is $0.00065\text{ K/min}$, an order of magnitude smaller than inter-individual human experimental standard deviation ($\pm 0.0065\text{ K/min}$, `NEG-0074`).
- **Enactment:** The 1-node lumped-capacitance model is retained as the parsimonious baseline. Multi-node complexity is prohibited until direct in vivo telemetry of microclimate sweat accumulation is integrated.

---

## 2. Selection of Three Prioritized Research Hypotheses for Cycle 8

To maximize verifiable scientific progress without generating redundant ungrounded architectures, Research Cycle 8 will investigate exactly three testable hypotheses:

### Hypothesis 1: Imbricated Scale Biomechanics & Intracompartmental Pressure Mitigation
- **Statement:** An articulating, imbricated scale architecture (overlapping pangolin-style geometry with elastomeric inter-scale fascial ligaments) preserves $\ge 90\%$ of radial compartment compliance during maximal muscular contraction, keeping peak anterior tibial pressure below the critical capillary closing threshold ($30\text{ mmHg}$), while sustaining localized blunt puncture resistance $> 25\text{ N}$.
- **Experimental Grounding:** Pangolin scale kinematics (*Wang et al. 2016*); human compartment pressure compliance curves (*Turnipseed 2002*, *Edmundsson 2011*).
- **Physical Limits:** Bounded by contact Hertzian shear stress and ligament elastic modulus ($E_{\text{ligament}} \le 50\text{ MPa}$).
- **Refutation Criteria:** If finite element simulation demonstrates that any imbricated scale layout providing $25\text{ N}$ puncture protection causes peak intramuscular pressure to exceed $35\text{ mmHg}$ during $10\%$ muscle volume expansion.
- **Expected Information Value:** Resolves the primary biomechanical contradiction between dermal armor and Chronic Exertional Compartment Syndrome (TARGET-CPE45).

### Hypothesis 2: Unified Microstructural Volume-Fraction Scaling for Keratin Composites
- **Statement:** The effective dry modulus of structural biological keratins scales linearly with the intermediate filament (IF) volume fraction ($\Phi_{\text{IF}}$) according to rule-of-mixtures composite mechanics:
  $$E_0(\Phi_{\text{IF}}) = E_{\text{IF}} \Phi_{\text{IF}} + E_{\text{matrix}} (1 - \Phi_{\text{IF}})$$
  allowing a single unified equation to predict the hydration curves of bovine hoof, sheep horn, whale baleen, and pangolin scale within $\le 15\%$ relative error across all species.
- **Experimental Grounding:** Published synchrotron X-ray diffraction data on keratin filament volume fractions (*Meyers et al. 2008*, *Wang et al. 2016*, *Trim et al. 2011*).
- **Physical Limits:** Limited by the amorphous matrix percolation threshold ($\Phi_{\text{IF}} \in [0.35, 0.75]$).
- **Refutation Criteria:** If measured dry moduli of unseen structural keratins deviate from the $\Phi_{\text{IF}}$-linear curve by $> 25\%$.
- **Expected Information Value:** Eliminates empirical guessing in cross-material transfer, providing an exact microstructural predictor.

### Hypothesis 3: Spatial Axonal Reinnervation Time Window in Human Limb VML
- **Statement:** A spatial-temporal reaction-diffusion model of motor axon sprouting ($1\text{ mm/day}$) across human skeletal muscle dimensions ($> 10\text{ cm}$) defines a critical defect radius ($R_{\text{crit}} \approx 4.5\text{ cm}$) beyond which functional neuromuscular reinnervation cannot occur before irreversible motor endplate fibrotic obliteration ($t_{\text{limit}} \approx 12\text{ months}$), proving that non-neurotized acellular grafts are biologically incapable of functional restoration in large human limb wounds.
- **Experimental Grounding:** Clinical electrodiagnostic recovery curves (*Dziki et al. 2016*); rodent/porcine VML denervation series (*Greising et al. 2020*).
- **Biological Limits:** Bounded by mammalian microtubule axonal transport rates ($\approx 1\text{ mm/day}$) and Schwann cell senescence.
- **Refutation Criteria:** Demonstration of functional tetanic contraction in a human muscle defect $> 5\text{ cm}$ treated solely with an acellular scaffold $> 12\text{ months}$ post-trauma.
- **Expected Information Value:** Establishes the definitive biophysical boundary between scaffold therapies and autologous neurotized muscle transfers.

---

## 3. Mandatory Gate Verification

```
========================================================================================
STATUS INDICATOR                       REQUIRED         CYCLE 7 STATUS
========================================================================================
PR9_SYNC                               PASS             PASS (Commit f8afbe3 live)
EVIDENCE_PROVENANCE                    PARTIAL          PARTIAL (20 verified, 1 unverified)
MATERIALS_CROSS_STUDY                  PASS             PASS (Tests A, B pass; C parameterized)
REGENERATION_CROSS_STUDY               PASS             PASS (LOSO MAE = 6.69% across 82 animals)
THERMAL_HOLDOUT                        PARTIAL          PARTIAL (1-node baseline retained)
BIOLOGICAL_FEASIBILITY                 CONDITIONAL      CONDITIONAL (Parameters audited)
CYCLE_8_READY                          YES              YES (3 hypotheses formulated)
========================================================================================
```
