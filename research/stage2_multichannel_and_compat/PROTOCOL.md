# PROTOCOL · EXP-0155 · Multi-Channel CPE45 Empirical Expansion (Spatial Coordination in Meters + 4-Channel Heat Dual-Task) & Within-Person Stage 3 Compatibility Probe

## Goal
Advance **Stage 2 (`CPE45`)** and run a genuine **within-person Stage 3 empirical compatibility probe** using three brand-new open individual-level human datasets (zero synthetic inputs, zero canonical threshold changes):

1. **Spatial coordination & maneuver anchor in meters (`DUO-GAIT`, Zhou et al. 2023, `SRC-0195`, `n = 16` paired × 4 conditions):**
   - Replace the previously `UNASSESSED_NO_HUMAN_ANCHOR` coordination/spatial-control cell in `CPE45` working assumptions with exact paired human fatigue + cognitive dual-task trajectories in meters (`stride_lengths_avg`, `clearances_min_avg`, `speed_avg`) and spatial/temporal dispersion (`clearances_min_CV`, `stride_lengths_CV`, `stride_times_CV`, `clearances_max_SI`).
2. **Single-cohort 4-channel physiological + cognitive + neuromuscular heat-stress trial (`Goepp et al. 2026`, `SRC-0196`, `OSF ekvcg`, `n = 20`: `10 BFR HA` vs `10 SHAM HA`, `40°C / 40% RH`, `21 min = 1260 s`):**
   - Test an internal biological adaptation (8-day Heat Acclimation ± BFR) across **4 jointly measured human channels** (`%PO`, `T_re`, concurrent `SART` RT/ACC/GS across blocks B2→B3, and pre/post `MVC` + `VA`), checking both pooled adaptation and `BFR` vs `SHAM` superiority, and screening against `EXP-0149` provisional `WORKING_SPEC.json` bounds.
3. **Within-person Stage 3 compatibility probe (`Agostinelli et al. 2025`, `SRC-0197`, `Figshare 28768673`, `n = 33` adults, `35°C / 50% RH`, 4-round loaded work + concurrent cognition, `~18.7 min`):**
   - Test directly within the same individuals whether higher mass-normalized maximal functional strength (`RelStr = (Squat + Deadlift + Bench) / Weight`) and explosive power (`VJ_max`) improve or impair loaded work speed (`TotalTime`), core thermal ceiling (`maxCT`), metabolic acidosis (`IMP_BLC`), and cognitive accuracy (`Total_errors`), both bivariately and in **multiple OLS regression controlling for `VO2max` and `Sex`**.

## Hard Constraints & Stop Rules
- Canonical `research/targets/CPE45.json` remains untouched (`success_thresholds: null`, `historical_experiments_cpe45_status: "not_assessed"`).
- Stage 2 closes **only** if a single verified human cohort sustains full `2700 s` alternating load with all required channels (`power`, `velocity`, `spatial coordination in meters`, `concurrent cognitive control`, `thermoregulation`, and `post45` recovery) passing `EXP-0149` working bounds.
- Stage 3 closes **only** after Stage 1 and Stage 2 are both closed on a unified internal biological system; `Agostinelli 2025` is cross-sectional (`~1124 s`, no longitudinal adaptation or tendon capacity) and therefore can provide **empirical compatibility constraints** only, not scientific closure of Stage 3.
- Deterministic seed (`20260420`), 10,000-draw participant-clustered bootstrap, strict RFC-8259 JSON (`allow_nan=False`), and `--check` exact replay.
