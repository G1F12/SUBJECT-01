# PROTOCOL · EXP-0155 (v2 — Independent Statistical Audit & Corrigendum)

## Goal
Advance **Stage 2 (`CPE45`)** and run a rigorously audited **within-person Stage 3 empirical compatibility probe** on three open individual-level human datasets, incorporating full statistical robustness checks (2×2 repeated-measures decomposition, baseline-adjusted ANCOVA, outlier/influence diagnostics, multicollinearity/VIF, covariate sensitivity, Huber robust regression, LOOCV overfitting audit, and explicit non-zero-harm 95% confidence bounds):

1. **Spatial coordination & maneuver anchor in meters (`DUO-GAIT`, Zhou et al. 2023, `SRC-0195`, `n = 16` paired × 4 conditions):**
   - Decompose the 2×2 repeated-measures structure into **Fatigue main effect**, **Dual-Task main effect**, and **Fatigue × Dual-Task interaction** (`t`-test, Wilcoxon signed-rank, 10,000-draw bootstrap 95% CI, `dz`, `η_p²`), plus explicit outlier/log sensitivity for `clearances_min_CV` (`sub_18` = `11.81` in `ST-Fat`).
2. **Single-cohort 4-channel physiological + cognitive + neuromuscular heat-stress trial (`Goepp et al. 2026`, `SRC-0196`, `OSF ekvcg`, `n = 20`: `10 BFR HA` vs `10 SHAM HA`, plus `CTRL n = 25` SART test-retest):**
   - Separate **pure `SHAM HA` time effect** (`n = 10`) and pooled HA effect (`n = 20`) from **incremental `BFR vs SHAM` effect** via baseline-adjusted ANCOVA (`Post ~ BFR + Pre_centered`), quantify test-retest familiarization in `CTRL` (`n = 25`), and explicitly avoid interpreting underpowered `p > 0.05` as proof of zero BFR effect.
3. **Within-person Stage 3 compatibility probe (`Agostinelli et al. 2025`, `SRC-0197`, `Figshare 28768673`, `n = 33` adults, `35°C / 50% RH`, `~1124 s`):**
   - Audit bivariate correlations (Pearson & Spearman), predictor collinearity (`VIF` for `M1` and `M2 + PBF`), outlier influence (`Cook's D > 4/n` and trimmed refit), Huber-IRLS robust regression, covariate sensitivity (`M0`..`M4` including within-sex strata), and out-of-sample generalization (`R²_LOOCV` and `MAE_LOOCV` vs null).
   - **Strict inference rule:** never treat `p > 0.05` as proof of absence of thermal or cognitive harm; report explicit 95% confidence harm bounds per `+1 kg/kg` `RelStr`.

## Hard Constraints & Stop Rules
- Canonical `research/targets/CPE45.json` remains untouched (`success_thresholds: null`, `historical_experiments_cpe45_status: "not_assessed"`).
- Stage 2 closes **only** if a single verified human cohort sustains full `2700 s` alternating load with all required channels (`power`, `velocity`, `spatial coordination in meters`, `concurrent cognitive control`, `thermoregulation`, and `post45` recovery).
- Stage 3 closes **only** after Stage 1 and Stage 2 are closed on a unified internal biological system.
- Deterministic seed (`20260420`), 10,000-draw bootstrap, strict RFC-8259 JSON (`allow_nan=False`), and `--check` exact replay.
