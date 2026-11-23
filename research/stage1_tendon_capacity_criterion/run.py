#!/usr/bin/env python3
"""EXP-0153: Lower bound of Achilles load-bearing capacity and validated non-destructive criteria audit (Stage 1)."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES_PATH = HERE / "SOURCES.json"
RESULTS_PATH = HERE / "RESULTS.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs(data_root: Path, src: dict) -> tuple[dict, dict, str]:
    subdir = data_root / src["data_subdir"]
    checked = {}
    for fname, meta in src["files"].items():
        fp = subdir / fname
        if not fp.is_file():
            raise FileNotFoundError(f"Missing raw source file: {fp}")
        digest = sha256_file(fp)
        if digest != meta["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {fname}: got {digest}, expected {meta['sha256']}")
        checked[fname] = {"bytes": fp.stat().st_size, "sha256": digest, "source_id": meta["source_id"]}

    exp152_path = ROOT / src["reused_experiment"]["results_path"]
    if not exp152_path.is_file():
        raise FileNotFoundError(f"Missing reused EXP-0152 output: {exp152_path}")
    exp152_sha = sha256_file(exp152_path)
    exp152 = json.loads(exp152_path.read_text("utf-8"))
    return checked, exp152, exp152_sha


def lower_bounds(mean: float, sd: float, n: int) -> dict:
    """Compute normal 5th percentile (P05) and small-sample one-sided 95% lower prediction bound (LPB95)."""
    z05 = float(stats.norm.ppf(0.95))
    t05 = float(stats.t.ppf(0.95, df=n - 1))
    p05 = mean - z05 * sd
    lpb95 = mean - t05 * math.sqrt(1.0 + 1.0 / n) * sd
    return {
        "mean": round(mean, 2),
        "sd": round(sd, 2),
        "n": n,
        "normal_p05": round(p05, 2),
        "one_sided_lpb95": round(lpb95, 2),
    }


def run_experiment(data_root: Path) -> dict:
    src = json.loads(SOURCES_PATH.read_text("utf-8"))
    checked, exp152, exp152_sha = verify_inputs(data_root, src)

    ta = src["track_a_ex_vivo_human_achilles_benchmarks"]
    tb = src["track_b_non_destructive_criteria"]
    t3_152 = exp152["task3_safety_margin_and_decision"]
    s10_full = t3_152["target_pose_10deg_pf_safety_margin"]["total_torque_fTS_1.000"]
    s10_pcsa = t3_152["target_pose_10deg_pf_safety_margin"]["pcsa_share_fTS_0.873"]
    gate = 1.50

    # --- TRACK A: Site-specific human capacity lower bounds vs EXP-0152 loads ---
    nag = ta["nagelli_2022_healthy_adults_0deg"]
    wren = ta["wren_2001_fresh_human_achilles"]

    avul_lb = lower_bounds(nag["avulsion_load_n"][0], nag["avulsion_load_n"][1], nag["avulsion_n"])
    mid_lb = lower_bounds(nag["midsubstance_load_n"][0], nag["midsubstance_load_n"][1], nag["midsubstance_n"])
    wren_slow_lb = lower_bounds(wren["slow_1pct_s_uts_mpa"][0], wren["slow_1pct_s_uts_mpa"][1], wren["slow_1pct_s_n"])
    wren_fast_lb = lower_bounds(wren["fast_10pct_s_uts_mpa"][0], wren["fast_10pct_s_uts_mpa"][1], wren["fast_10pct_s_n"])

    def sf_range(cap_val: float, load_range: list[float], load_med: float) -> dict:
        lo_load, hi_load = load_range
        sf_min = cap_val / hi_load
        sf_max = cap_val / lo_load
        sf_med = cap_val / load_med
        return {
            "sf_range": [round(sf_min, 3), round(sf_max, 3)],
            "sf_median_ma": round(sf_med, 3),
            "all_models_ge_1_50": bool(sf_min >= gate),
            "all_models_below_1_50": bool(sf_max < gate),
        }

    force_100 = s10_full["force_vs_nagelli_2022_avulsion_4217n"]
    force_873 = s10_pcsa["force_vs_nagelli_2022_avulsion_4217n"]
    ent_ramp_100 = s10_full["ramp_enthesis_vs_wren_71mpa"]
    ent_ramp_873 = s10_pcsa["ramp_enthesis_vs_wren_71mpa"]
    ent_bal_100 = s10_full["ballistic_enthesis_vs_wren_86mpa"]
    ent_bal_873 = s10_pcsa["ballistic_enthesis_vs_wren_86mpa"]

    capacity_vs_10pf = {
        "calcaneal_avulsion_nagelli2022_n5": {
            "capacity_n": avul_lb,
            "fTS_1_000_vs_p05": sf_range(avul_lb["normal_p05"], force_100["force_cohort_n_range"], force_100["force_cohort_n_median"]),
            "fTS_1_000_vs_lpb95": sf_range(avul_lb["one_sided_lpb95"], force_100["force_cohort_n_range"], force_100["force_cohort_n_median"]),
            "fTS_0_873_vs_p05": sf_range(avul_lb["normal_p05"], force_873["force_cohort_n_range"], force_873["force_cohort_n_median"]),
            "fTS_0_873_vs_lpb95": sf_range(avul_lb["one_sided_lpb95"], force_873["force_cohort_n_range"], force_873["force_cohort_n_median"]),
        },
        "midsubstance_rupture_nagelli2022_n5": {
            "capacity_n": mid_lb,
            "fTS_1_000_vs_p05": sf_range(mid_lb["normal_p05"], force_100["force_cohort_n_range"], force_100["force_cohort_n_median"]),
            "fTS_1_000_vs_lpb95": sf_range(mid_lb["one_sided_lpb95"], force_100["force_cohort_n_range"], force_100["force_cohort_n_median"]),
            "fTS_0_873_vs_p05": sf_range(mid_lb["normal_p05"], force_873["force_cohort_n_range"], force_873["force_cohort_n_median"]),
            "fTS_0_873_vs_lpb95": sf_range(mid_lb["one_sided_lpb95"], force_873["force_cohort_n_range"], force_873["force_cohort_n_median"]),
        },
        "wren2001_slow_1pct_s_vs_ramp_enthesis": {
            "capacity_mpa": wren_slow_lb,
            "fTS_1_000_vs_p05": sf_range(wren_slow_lb["normal_p05"], ent_ramp_100["effective_stress_cohort_mpa_range"], ent_ramp_100["effective_stress_cohort_mpa_median"]),
            "fTS_1_000_vs_lpb95": sf_range(wren_slow_lb["one_sided_lpb95"], ent_ramp_100["effective_stress_cohort_mpa_range"], ent_ramp_100["effective_stress_cohort_mpa_median"]),
            "fTS_0_873_vs_p05": sf_range(wren_slow_lb["normal_p05"], ent_ramp_873["effective_stress_cohort_mpa_range"], ent_ramp_873["effective_stress_cohort_mpa_median"]),
            "fTS_0_873_vs_lpb95": sf_range(wren_slow_lb["one_sided_lpb95"], ent_ramp_873["effective_stress_cohort_mpa_range"], ent_ramp_873["effective_stress_cohort_mpa_median"]),
        },
        "wren2001_fast_10pct_s_vs_ballistic_enthesis": {
            "capacity_mpa": wren_fast_lb,
            "fTS_1_000_vs_p05": sf_range(wren_fast_lb["normal_p05"], ent_bal_100["effective_stress_cohort_mpa_range"], ent_bal_100["effective_stress_cohort_mpa_median"]),
            "fTS_1_000_vs_lpb95": sf_range(wren_fast_lb["one_sided_lpb95"], ent_bal_100["effective_stress_cohort_mpa_range"], ent_bal_100["effective_stress_cohort_mpa_median"]),
            "fTS_0_873_vs_p05": sf_range(wren_fast_lb["normal_p05"], ent_bal_873["effective_stress_cohort_mpa_range"], ent_bal_873["effective_stress_cohort_mpa_median"]),
            "fTS_0_873_vs_lpb95": sf_range(wren_fast_lb["one_sided_lpb95"], ent_bal_873["effective_stress_cohort_mpa_range"], ent_bal_873["effective_stress_cohort_mpa_median"]),
        },
    }

    # Regional narrowest mCSA sensitivity relative to Kubo lateral-malleolus CSA (66.0 mm^2)
    mcsa_sensitivity = {}
    for frac in ta["regional_mcsa_discount_sensitivity"]:
        sig_lo = ent_ramp_100["effective_stress_cohort_mpa_range"][0] / frac
        sig_hi = ent_ramp_100["effective_stress_cohort_mpa_range"][1] / frac
        sig_med = ent_ramp_100["effective_stress_cohort_mpa_median"] / frac
        mcsa_sensitivity[f"mCSA_ratio_{frac:.2f}"] = {
            "implied_mcsa_mm2": round(66.0 * frac, 2),
            "enthesis_stress_10pf_mpa_range": [round(sig_lo, 2), round(sig_hi, 2)],
            "sf_vs_wren_mean_71mpa_range": [round(71.0 / sig_hi, 3), round(71.0 / sig_lo, 3)],
            "sf_vs_wren_p05_43mpa_range": [round(wren_slow_lb["normal_p05"] / sig_hi, 3), round(wren_slow_lb["normal_p05"] / sig_lo, 3)],
            "sf_vs_exp0062_85mpa_range": [round(85.0 / sig_hi, 3), round(85.0 / sig_lo, 3)],
            "passes_sf_1_50_vs_mean_71": bool(71.0 / sig_hi >= gate),
        }

    # --- TRACK B: Non-destructive criterion audit & provisional strain mapping for Kubo-Ishigaki ---
    km = tb["kubo_ishigaki_provisional_strain_mapping"]
    lmax_mean, lmax_sd = km["iso_post_0deg_ramp_elongation_mm"]
    bal_mean, bal_sd = km["iso_post_0deg_ballistic_elongation_mm"]
    f_ratio_ym = t3_152["pose_transfer_force_ratio_10pf_to_0"]["young_male_mean_ratio"]
    f_ratio_lo, f_ratio_hi = t3_152["pose_transfer_force_ratio_10pf_to_0"]["empirical_envelope_10pf_to_0"]
    strain_gate = tb["mersmann_2023_patellar_strain_threshold"]["threshold_pct"]

    def strain_band(dl_mm: float, dl_sd_mm: float, l0_range: list[float], scale_lo: float, scale_mean: float, scale_hi: float) -> dict:
        l0_min, l0_max = l0_range
        l0_mid = 0.5 * (l0_min + l0_max)
        eps_min = (dl_mm * scale_lo) / l0_max * 100.0
        eps_mid = (dl_mm * scale_mean) / l0_mid * 100.0
        eps_max = (dl_mm * scale_hi) / l0_min * 100.0
        eps_plus1sd_max = ((dl_mm + dl_sd_mm) * scale_hi) / l0_min * 100.0
        return {
            "strain_cohort_mean_range_pct": [round(eps_min, 2), round(eps_max, 2)],
            "strain_midpoint_pct": round(eps_mid, 2),
            "strain_plus1sd_upper_pct": round(eps_plus1sd_max, 2),
            "upper_bound_below_9pct": bool(eps_max < strain_gate),
            "plus1sd_below_9pct": bool(eps_plus1sd_max < strain_gate),
        }

    provisional_strain = {
        "caveat": "Mersmann 2023 >=9.0% risk threshold (RR=2.3 [1.1; 4.9]) is prospectively validated ONLY on the patellar tendon in adolescents, NOT on the adult human Achilles tendon; moreover Kubo-Ishigaki measured compound tendon+aponeurosis 2D displacement without resting L_0 or isolated free Achilles tendon strain.",
        "kharazi_2021_in_vivo_reference": {
            "mvc_elongation_mm": ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["mvc_elongation_mm"],
            "implied_mvc_strain_pct": round(ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["running_3_5_ms_strain_pct"][0] / (ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["running_pct_of_mvc_strain"] / 100.0), 2),
            "implied_l0_mm": round(ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["mvc_elongation_mm"][0] / (ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["running_3_5_ms_strain_pct"][0] / ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["running_pct_of_mvc_strain"]), 1),
        },
        "if_l0_calcaneus_mg_mtj_177_215mm": {
            "at_0deg_ramp_mvc": strain_band(lmax_mean, lmax_sd, km["calcaneus_mg_mtj_l0_range_mm"], 1.0, 1.0, 1.0),
            "transferred_10deg_pf_linear_bound": strain_band(lmax_mean, lmax_sd, km["calcaneus_mg_mtj_l0_range_mm"], f_ratio_lo, f_ratio_ym, f_ratio_hi),
            "at_0deg_ballistic_mvc": strain_band(bal_mean, bal_sd, km["calcaneus_mg_mtj_l0_range_mm"], 1.0, 1.0, 1.0),
        },
        "if_l0_compound_fascicle_insertion_230_300mm": {
            "at_0deg_ramp_mvc": strain_band(lmax_mean, lmax_sd, km["compound_fascicle_insertion_l0_range_mm"], 1.0, 1.0, 1.0),
            "transferred_10deg_pf_linear_bound": strain_band(lmax_mean, lmax_sd, km["compound_fascicle_insertion_l0_range_mm"], f_ratio_lo, f_ratio_ym, f_ratio_hi),
        },
    }

    # Check if ANY Track A lower bound passes SF >= 1.50
    any_track_a_pass = any(
        blk[k]["all_models_ge_1_50"]
        for blk in capacity_vs_10pf.values()
        for k in ("fTS_1_000_vs_p05", "fTS_1_000_vs_lpb95", "fTS_0_873_vs_p05", "fTS_0_873_vs_lpb95")
    )

    return {
        "experiment_id": "EXP-0153",
        "stage1_verdict": "HOLD",
        "stage1_blocker_status": "DATA_BLOCKED",
        "scientific_criterion_closed": False,
        "computational_work_on_existing_data_complete": True,
        "reused_exp0152": {
            "path": src["reused_experiment"]["results_path"],
            "sha256": exp152_sha,
            "stage1_verdict_inherited": exp152["stage1_verdict"],
            "adapt25_strength_preserved": exp152["kubo_ishigaki_adapt25_strength_preserved_from_exp0147"],
        },
        "verified_new_source_files": checked,
        "track_a_lower_bound_capacity": {
            "young_adult_ex_vivo_10pf_dataset_exists": False,
            "any_published_lower_bound_passes_sf_1_50": any_track_a_pass,
            "capacity_lower_bounds_vs_10pf": capacity_vs_10pf,
            "regional_mcsa_sensitivity_fTS_1_000": mcsa_sensitivity,
            "deng_2026_morphology_mechanics_limits": ta["deng_2026_3d_mri_free_at"],
            "in_vivo_survival_not_lower_bound": {
                "kharazi_2021_0deg_mvc_force_n": ta["kharazi_2021_in_vivo_survival_0deg_mvc"]["mvc_peak_force_n"],
                "ruling": "In vivo non-rupture peak (5523 +- 552 N in a separate cohort) is an upper survival observation, not a lower failure bound or SF >= 1.50 guarantee for Kubo-Ishigaki's cohort or enthesis fatigue durability.",
            },
        },
        "track_b_non_destructive_criteria_audit": {
            "independently_validated_adult_achilles_criterion_exists": False,
            "patellar_strain_criterion_mersmann2023": tb["mersmann_2023_patellar_strain_threshold"],
            "adult_patellar_prescription_weidlich2024": tb["weidlich_2024_adult_patellar_prescription"],
            "strength_stiffness_meta_pang2026": tb["pang_2026_strength_stiffness_meta"],
            "imaging_2d_vs_3d_error_deng2025": tb["deng_2025_2d_vs_3d_free_at_strain"],
            "achilles_tendinopathy_sr_weerkamp2026": tb["weerkamp_2026_bmj_achilles_tendinopathy_sr"],
            "provisional_kubo_strain_test": provisional_strain,
        },
        "stage1_paths_summary": {
            "ADAPT25": "STRENGTH_PASS_EXP0147 / TISSUE_DATA_BLOCKED_EXP0152_EXP0153 (Kubo-Ishigaki 2017 is the sole cohort clearing strength rate; fails both Track A capacity lower bounds and Track B non-destructive criteria/measurement identifiability, plus missing weeks 4 & 8 visits).",
            "FORCE20": "STRENGTH_AND_TISSUE_HOLD_EXP0140_TO_EXP0152 (0 open human cohorts clear controlled lower 95% CI >= +20 pp at matched mass with pose-matched loaded tissue reserve).",
        },
        "decisive_missing_indicator": (
            "1) Either a prospectively validated non-destructive adult human Achilles tendon safety criterion (linking individual 3D free-tendon strain epsilon_free and/or regional enthesis loading to clinical injury/structural failure incidence with calibrated sensitivity/specificity) measured longitudinally in the target pose (+10 deg PF and 0 deg) at weeks 0, 4, 8, and 12 alongside individual MRI/3D-US MA(theta), resting L_0, narrowest mCSA, and exposure-matched active control; "
            "2) OR site- and age-matched human free Achilles tendon & calcaneal enthesis mechanical capacity lower bounds combined with individual MA(theta), regional mCSA, and intermediate-visit trajectories in the same participants."
        ),
        "resumption_condition": (
            "Resume Stage 1 computational adjudication immediately upon receipt of either (a) participant-level longitudinal records with pose-matched strength, individual MA(theta), 3D free-tendon resting L_0 & maximal strain, regional mCSA, and weeks 0/4/8/12 visits under active control, OR (b) an externally validated prospective adult Achilles non-destructive criterion paired with raw Kubo-Ishigaki (or equivalent ADAPT25/FORCE20) participant-level measurements."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("tmp"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    res = run_experiment(args.data_root)
    payload = json.dumps(res, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.check:
        if not RESULTS_PATH.is_file():
            raise SystemExit("RESULTS.json missing")
        if RESULTS_PATH.read_text("utf-8") != payload:
            raise SystemExit("EXP-0153 replay mismatch against RESULTS.json")
        print("EXP-0153 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(f"Wrote {RESULTS_PATH} ({len(payload)} bytes); stage1={res['stage1_verdict']}/{res['stage1_blocker_status']}")


if __name__ == "__main__":
    main()
