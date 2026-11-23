# PROTOCOL · EXP-0157 · Stage 2 Multi-Bout Intermittent Heat Stress (Locomotor Pacing + Core Temp + Technical Motor Accuracy) and 45/90-min Intermittent Heat Cognition

## Pre-Registered Decisive Criterion
Evaluate two brand-new primary human intermittent heat-stress datasets (plus explicitly document screening exclusion of `OSF 84fru`, `n = 8` valid recruits lacking external work/power and cognition):
1. **`SSGs_Heat` (`SRC-0202`, `PMC13249198`, `Zenodo 17418102`, 2026 PLOS ONE, `n = 16` paired × 3 controlled environmental heat-stress levels `<23.9°C`, `24–27.9°C`, `>28°C` × 2 intermittent formats `2v2` [4×2 min / 2 min rest = 840 s] and `4v4` [4×4 min / 4 min rest = 1680 s]):**
   - Test individual-level repeated-measures effects of **Environmental Heat (`>28°C` vs `<23.9°C`)**, **Bout Fatigue (`Late B3–B4` vs `Early B1–B2`)**, and **Heat × Bout interaction** on:
     - Post-session `Core Temp` (`°C`) and proportion exceeding `39.0°C` / `39.5°C` (`EXP-0149` thermal bounds)
     - Locomotor `Distance` (m) per bout and `Late/Early` pacing retention ratio
     - Cardiovascular load (`HR %max`) and `RPE`
     - Concurrent **technical motor-coordination accuracy** (`Pass Accuracy = SUCC_PASS / (SUCC_PASS + UNSUCC_PAS)`, `Shot Accuracy`, and `Lost Balls`)
2. **`Malcolm et al. (2024)` (`SRC-0203`, `PMC11369344`, *Eur J Sport Sci* 24:1287, `n = 12` men, `90-min` intermittent running in `33°C / 50% RH`):**
   - Audit the **native uncooled `CON` arm** (excluding external ice-slurry/ice-collar `COOL` as non-native under `GOVERNANCE.md`) at exact **`45-min (2700 s)` half-time** and **`90-min` full-time** across Complex Visual Search, Complex Stroop, Sternberg 1/3/5-item, and 5-min RVIP against `EXP-0149` working cognitive bounds.

## Hard Constraints & Statistical Discipline
- Canonical `research/targets/CPE45.json` remains unchanged (`success_thresholds: null`).
- Never treat `p > 0.05` as proof of zero heat/fatigue impairment; report exact 10,000-draw bootstrap 95% CIs and Wilcoxon signed-rank p-values alongside parametric `t`-tests.
- Deterministic seed (`20260421`), strict RFC-8259 JSON (`allow_nan=False`), `--check` exact replay.
