# PROTOCOL · EXP-0156 · Stage 1 New Internal Biological Mechanism: Collagen-Peptide & Strain-Targeted Tendon Remodeling RCTs

## Pre-Registered Decisive Criterion
Test whether an **internal biological intervention specifically targeting tendon collagen synthesis and matrix remodeling** — **hydrolysed/bioactive collagen peptides + heavy resistance training (`COL/CP + RT`) vs active placebo-controlled resistance training (`PLA + RT`)** on the **patellar tendon** (the exact tendon where the non-destructive safety criterion `ε_max < 9.0%` is prospectively validated, `SRC-0183`), plus **high-loading strain-targeted Achilles tendon exercise** — can simultaneously clear:
1. **`ADAPT25`:** lower 95% CI of `(r_I − 1.25 × r_C) > 0` with positive active control rate `r_C > 0`, **OR** **`FORCE20`:** control-adjusted maximal functional strength gain lower 95% CI `≥ +20 pp` at comparable body mass; **AND**
2. **Validated tendon safety:** loaded tendon strain `< 9.0%` (patellar) or positive CSA/stiffness adaptation without structural/clinical degradation at the new post-training maximum.

## New Cohorts Audited (Zero Overlap with Prior Registry, `N = 120` Total)
1. **`Balshaw et al. (2025)` (`SRC-0198`, Figshare `28715441`, `n = 39` completers: `19 CP` vs `20 PLA`, 15 wk lower-body RT):** 3T MRI patellar tendon CSA + VL aponeurosis + ultrasound stiffness/modulus/strain (`80% pre-MVT`) + KE & KF MVT.
2. **`Lee et al. (2025)` (`SRC-0199`, `PMC11917387`, `n = 20`: `9 COL` vs `11 PLA`, 12 wk RT, middle-aged adults):** KE MVT, 10-RM, pRTD, CMJ power + patellar tendon stiffness, Young's modulus, CSA, and maximal strain.
3. **`Lee et al. (2023)` (`SRC-0200`, `PMC9910607`, `n = 17`: `8 COL` vs `9 PLA`, 10 wk in-season RT, female soccer players):** Iso/Con KE MVC, Iso KF MVC + patellar tendon CSA, stiffness, and maximal strain.
4. **`Radovanović et al. (2022)` (`SRC-0201`, `PMC9768072`, `n = 44`: 15 High-Load vs 15 Alfredson vs 14 Passive Therapy, 12 wk Achilles tendinopathy RCT):** Plantar flexor MVC, CMJ/DJ, Achilles CSA, stiffness, and maximal strain.

## Statistical Discipline
- Never interpret `p > 0.05` as proof of exact zero effect; report exact `G × T` p-values alongside `ADAPT25` rate contrasts and 95% confidence bounds across `r = 0.50` and `r = 0.90` pre-post correlation sensitivity (plus exact published `Δ ± SD` where available, e.g. `Balshaw 2025`, `Lee 2023`, `Radovanović 2022`).
- Deterministic `--check` exact replay, strict RFC-8259 JSON (`allow_nan=False`).
