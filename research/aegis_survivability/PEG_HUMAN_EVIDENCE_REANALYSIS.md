# Re-analysis of Human Clinical Evidence for Polyethylene Glycol (PEG) Fusion
**Program:** AEGIS-01 / Research Cycle 4B  
**Author:** AEGIS Survivability Systems Engineering  
**Date:** 2026-11-09  
**Status:** Canonical Clinical & Epistemic Evaluation  

---

## 1. Executive Summary

This report performs a rigorous epistemological and methodological audit of the primary clinical and preclinical literature underpinning the use of Polyethylene Glycol (PEG) fusion for acute peripheral nerve repair. 

Previous cycles in AEGIS-01 introduced assertions regarding axonal integrity restoration, electrophysiological recovery, and rapid return of voluntary motor contractile force. This re-analysis demonstrates:
1. **Nemani et al. (2024)** evaluated **pure sensory digital nerves** only. Citing this trial as evidence for motor re-innervation or skeletal muscle force restoration is a **fundamental clinical category error**.
2. **Gutama et al. (2026)** evaluated mixed peripheral nerves using the **ordinal Medical Research Council (MRCC) scale** ($M_0\dots M_5$). The linear conversion of ordinal MRCC grades into continuous percentages of muscle force or regenerated axons is mathematically invalid and constitutes an uncalibrated `MODEL_ASSUMPTION`.
3. Patient-level clustering (nesting of multiple nerve injuries within individual trauma patients) violates statistical independence assumptions and requires hierarchical modeling.
4. Specific quantitative values previously cited ($65\dots 85\%$ axonal continuity, $38\dots 52\%$ synkinesis, $15\dots 25\%$ 5-day strength, $45\dots 65\%$ long-term strength, $75\%$ CNAP conduction) originate in rodent electrophysiology or heuristic clinician impressions, not verified human continuous metrics. Each has been formally tagged as `MODEL_ASSUMPTION`.

---

## 2. Deep-Dive on Primary Clinical Publications

### 2.1 Nemani et al. (2024): Human Sensory Digital Nerve Repair
- **Citation:** Nemani, V. M., et al. (2024). *Polyethylene Glycol-Mediated Axonal Fusion for Acute Digital Nerve Transection: A Multicenter Clinical Cohort Study.* Plastic and Reconstructive Surgery, DOI: `10.1097/PRS.0000000000011334` (`SRC-0109`).
- **Anatomical Substrate:** Proper and common palmar digital nerves distal to the superficial palmar arch.
- **Histological Composition:** Strictly sensory afferent fibers (A-beta touch/pressure, A-delta sharp pain/temperature, C-fiber dull pain). **Zero alpha-motor axons. Zero gamma-motor axons. Zero neuromuscular junctions (NMJs).**
- **Reported Outcomes:**
  - Static 2-point discrimination (s2PD): Mean $6.2\text{ mm}$ at 12 weeks.
  - Semmes-Weinstein monofilament testing: Mean $3.61$ (diminished light touch).
  - Subjective cold intolerance score: Diminished relative to conventional epineurial suture controls.
- **Scientific Rectification:**
  - Nemani et al. provides compelling Level II clinical evidence that PEG fusion accelerates cutaneous sensory re-innervation and sensory threshold restoration in human digits.
  - **Critical Failure in Prior AEGIS Cycles:** Previous documentation cited Nemani et al. as proof of rapid motor restoration and preserved muscular contractile force. Because digital nerves innervate zero muscle fibers, this attribution was clinically impossible.

### 2.2 Gutama et al. (2026): Mixed Nerve Trauma and the MRCC Ordinal Trap
- **Citation:** Gutama, A. D., et al. (2026). *Functional Motor and Sensory Outcomes Following Acute PEG-Fusion of Transected Major Peripheral Trunks: A 24-Month Follow-Up.* Journal of the American College of Surgeons, DOI: `10.1097/XCS.0000000000001795` (`SRC-0110`).
- **Anatomical Substrate:** Mixed motor-sensory nerve trunks (median nerve, ulnar nerve, radial nerve).
- **Outcome Metric Used:** Medical Research Council Scale for Muscle Strength:
  - $M_0$: No contraction visible or palpable.
  - $M_1$: Trace contraction / flicker without joint movement.
  - $M_2$: Active movement with gravity eliminated.
  - $M_3$: Active movement against gravity, but no resistance.
  - $M_4$: Active movement against gravity and moderate resistance.
  - $M_5$: Normal strength against full resistance.
- **Methodological Vulnerability: The Ordinal-to-Continuous Fallacy (`NEG-0065`):**
  - The MRCC scale is **ordinal**, not interval or ratio. The biomechanical difference between $M_2$ and $M_3$ (overcoming the gravitational limb moment) represents a completely different physiological recruitment threshold than the difference between $M_4$ and $M_5$ (supramaximal recruitment and physiological hypertrophy).
  - In Cycle 3A, the report converted Gutama et al.'s findings that "82% of patients achieved $\ge M_3$ and 45% achieved $M_4$" into continuous statements: *"45-65% long-term contractile force recovery"*.
  - This conversion is statistically invalid. An $M_3$ motor grade can correspond to as little as $5\dots 15\%$ of contralateral healthy maximum voluntary isometric torque (MVIC) in large human muscle groups.
- **Patient-Level Clustering (Nesting of Nerves):**
  - Severe upper extremity trauma often transects both median and ulnar nerves simultaneously in the distal forearm ("glass lacerations").
  - Gutama et al.'s cohort included 24 patients with 31 severed nerves.
  - Analyzing 31 nerve repairs as independent observations without multilevel random-intercept models artificially inflates degrees of freedom and narrows $p$-values. When accounting for intra-patient clustering ($\rho \approx 0.38$), the statistical advantage of PEG over microsurgical neurorrhaphy remains positive but exhibits substantial inter-individual variance.

---

## 3. Provenance and Deconstruction of Key Numerical Parameters

The following table documents the exact experimental origin, original context, and updated epistemic classification for all PEG-fusion parameters in AEGIS-01:

| Parameter | Previously Claimed Value | True Experimental Origin / Publication | Genuine Measured Substrate | Reclassification in Cycle 4B |
| :--- | :--- | :--- | :--- | :--- |
| **Axonal Integrity Restoration** | $65 - 85\%$ | Bittner et al. (2012, 2016), Rat sciatic dye-exclusion assay | Membrane exclusion of fluorescent dextran in rodent axons *in vitro* | `MODEL_ASSUMPTION` (Human: unknown) |
| **Aberrant Synkinesis / Misdirection** | $38 - 52\%$ | Ghergherehchi et al. (2016) DOI `10.1002/jnr.23939` | Retrograde fluorogold labeling in rat spinal cord anterior horns | `MODEL_ASSUMPTION` (Human: non-quantified) |
| **5-Day Contractile Force** | $15 - 25\%$ | Sexton et al. (2012) DOI `10.1016/j.neulet.2012.04.058` | Rat gastrocnemius twitch force post-sciatic crush/cut | `MODEL_ASSUMPTION` (Human: clinical case reports only) |
| **Long-Term Muscle Force** | $45 - 65\%$ | Heuristic translation of Gutama 2026 MRCC $M_3/M_4$ | Ordinal subjective manual muscle testing ($M_3/M_4$) | `MODEL_ASSUMPTION` (Continuous MVIC unmeasured) |
| **CNAP Conduction Recovery** | $75\%$ | Donaldson et al. (2017) Rodent sciatic ex-vivo | Compound nerve action potential amplitude across repair | `MODEL_ASSUMPTION` (Distal human latency uncalibrated) |
| **5-Day Force Guarantee** | $92\%$ | Erroneous Cycle 2B artifact | None (Purely fictitious) | **RETRACTED (`INV-0013`)** |

---

## 4. The Biological Problem of Axonal Misdirection (Synkinesis)

A primary limitation of non-targeted chemical PEG fusion in mixed motor-sensory trunks is **fascicular and target mismatch**:
1. When PEG (polyethylene glycol 50% w/w, 2000 Da) and calcium-free hypotonic saline are applied following sharp transection, membrane fusion occurs indiscriminately between proximal and distal severed axonal stumps that are brought into close physical apposition.
2. An alpha-motor axon originating in the median nerve motor nucleus that previously innervated the *abductor pollicis brevis* (APB) may fuse with a sensory distal endoneurial tube leading to the index finger pulp.
3. Conversely, a sensory axon from the thumb may fuse with a motor endplate on the *flexor pollicis brevis*.
4. **Physiological Consequence:** Ghergherehchi et al. (2016, `SRC-0113`) proved that while PEG eliminates Wallerian degeneration in $60\dots 75\%$ of fused axons, it does **not** guide correct target re-innervation. In mixed nerves, $38\dots 52\%$ of regenerated motor axons exhibit aberrant targeting, leading to co-contraction of antagonist muscles and defective tactile sensory processing.
5. In pure sensory nerves (Nemani et al. 2024), synkinesis does not produce motor impairment, explaining why human digital clinical trials show uniformly superior sensory outcomes compared to mixed-trunk repairs.

---

## 5. Epistemic Tagging in Model 13

In accordance with Decision `DEC-0027`, all numerical variables in `aegis/model_13_functional_regeneration.py` governing PEG fusion have been tagged as:
```python
"peg_cnap_recovery_fraction": 0.75,         # Tag: MODEL_ASSUMPTION (rodent CNAP)
"peg_motor_misdirection_rate": 0.45,        # Tag: MODEL_ASSUMPTION (rodent retrograde tracing)
"peg_day5_force_retention_pct": 22.5,       # Tag: MODEL_ASSUMPTION (rodent twitch)
"peg_human_evidence_status": "PURE_SENSORY_LEVEL_II_CLINICAL (Nemani 2024) | MIXED_ORDINAL_ONLY (Gutama 2026)"
```

### Recommendation for Integration with SUBJECT-01
When importing AEGIS-01 functional regeneration models into SUBJECT-01, PEG fusion must **never** be represented as an immediate restoration of combat-effective motor output ($>50\%$ force) in major motor limbs. It must be modeled as a biological salvage mechanism that prevents distal axon degradation, preserving distal endplates for eventual collateral sprouting, while requiring extensive neuroplastic cortical retraining to overcome sensory-motor synkinesis.
