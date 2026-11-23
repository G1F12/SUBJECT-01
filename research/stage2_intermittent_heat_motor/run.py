#!/usr/bin/env python3
"""EXP-0157: Stage 2 multi-bout intermittent heat-stress audit (Zenodo 17418102 SSGs_Heat n=16 x 3 heat
levels x 2v2/4v4 x 4 bouts: Core Temp, locomotor distance pacing, HR %max, and technical motor accuracy)
+ Malcolm et al. 2024 (PMC11369344, n=12, 90-min intermittent heat running with exact 45-min half-time cognition).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl
from scipy import stats

HERE = Path(__file__).resolve().parent
SOURCES_PATH = HERE / "SOURCES.json"
RESULTS_PATH = HERE / "RESULTS.json"
SEED = 20260421
N_BOOT = 10000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sources(data_root: Path, src_cfg: dict) -> dict:
    sub = data_root / src_cfg["data_subdir"]
    verified = {}
    for fname, meta in src_cfg["files"].items():
        p = sub / fname
        if not p.is_file():
            raise FileNotFoundError(f"Missing raw input file: {p}")
        got_sha = sha256_file(p)
        got_bytes = p.stat().st_size
        if got_sha != meta["sha256"] or got_bytes != meta["bytes"]:
            raise ValueError(f"Checksum/size mismatch for {fname}")
        verified[fname] = {"source_id": meta["source_id"], "bytes": got_bytes, "sha256": got_sha}
    return verified


def boot_mean_ci(arr: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT) -> list[float]:
    n = len(arr)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = arr[idx].mean(axis=1)
    return [round(float(np.percentile(means, 2.5)), 4), round(float(np.percentile(means, 97.5)), 4)]


def paired_summary(diff: np.ndarray, rng: np.random.Generator) -> dict:
    m = np.isfinite(diff)
    d = diff[m]
    t_v, p_t = stats.ttest_1samp(d, 0.0)
    nz = d[d != 0]
    p_w = float(stats.wilcoxon(nz)[1]) if len(nz) >= 5 else 1.0
    sd = float(d.std(ddof=1))
    dz = float(d.mean() / sd) if sd > 0 else 0.0
    return {
        "n": int(len(d)),
        "mean_diff": round(float(d.mean()), 4),
        "sd_diff": round(sd, 4),
        "ci95_boot": boot_mean_ci(d, rng),
        "t": round(float(t_v), 3),
        "p_ttest": round(float(p_t), 5),
        "p_wilcoxon": round(p_w, 5),
        "cohen_dz": round(dz, 3),
    }


def _f(v) -> float:
    if v is None:
        return float("nan")
    try:
        return float(v)
    except Exception:
        return float("nan")


def analyze_ssgs_heat(data_root: Path, src_cfg: dict, rng: np.random.Generator) -> dict:
    xpath = data_root / src_cfg["data_subdir"] / "SSGs_Heat.xlsx"
    wb = openpyxl.load_workbook(xpath, data_only=True)

    sheets = [
        ("LEH_lt23_9C", "<23.9C"),
        ("MEH_24_27_9C", "24-27.9C"),
        ("HEH_gt28C", ">28C"),
    ]
    # Exact verified column offsets per sheet (see header audit)
    skill_cols = {
        "<23.9C": {"sp": 40, "up": 45, "ss": 50, "us": 55, "lb": 60},
        "24-27.9C": {"sp": 36, "up": 37, "ss": 38, "us": 39, "lb": 40},
        ">28C": {"sp": 36, "up": 37, "ss": 38, "us": 39, "lb": 40},
    }
    formats = [("2v2_840s", range(2, 18)), ("4v4_1680s", range(23, 39))]

    parsed: dict[str, dict[str, dict[str, np.ndarray]]] = {fmt: {} for fmt, _ in formats}
    for key_h, sname in sheets:
        ws = wb[sname]
        rows = list(ws.iter_rows(values_only=True))
        sc = skill_cols[sname]
        for fmt, rrng in formats:
            recs = [rows[r] for r in rrng]
            pids = [int(r[0]) for r in recs]
            if pids != list(range(1, 17)):
                raise ValueError(f"Unexpected player IDs in {sname}/{fmt}: {pids}")
            pre_tc = np.array([_f(r[1]) for r in recs])
            post_tc = np.array([_f(r[34]) for r in recs])
            d_b1 = np.array([_f(r[9]) for r in recs])
            d_b2 = np.array([_f(r[15]) for r in recs])
            d_b3 = np.array([_f(r[21]) for r in recs])
            d_b4 = np.array([_f(r[27]) for r in recs])
            tot_d = np.array([_f(r[33]) for r in recs])
            hr_pct = np.array([_f(r[29]) for r in recs])
            rpe = np.array([_f(r[30]) for r in recs])
            sp = np.array([_f(r[sc["sp"]]) for r in recs])
            up = np.array([_f(r[sc["up"]]) for r in recs])
            lb = np.array([_f(r[sc["lb"]]) for r in recs])
            pass_tot = sp + up
            pass_acc = np.where(pass_tot > 0, 100.0 * sp / pass_tot, np.nan)
            early_d = 0.5 * (d_b1 + d_b2)
            late_d = 0.5 * (d_b3 + d_b4)
            late_early_pct = 100.0 * (late_d - early_d) / early_d

            parsed[fmt][key_h] = {
                "pre_tc": pre_tc,
                "post_tc": post_tc,
                "delta_tc": post_tc - pre_tc,
                "tot_dist_m": tot_d,
                "early_dist_m": early_d,
                "late_dist_m": late_d,
                "late_minus_early_pct": late_early_pct,
                "hr_pct": hr_pct,
                "rpe": rpe,
                "pass_acc_pct": pass_acc,
                "lost_balls": lb,
            }

    out_formats = {}
    for fmt, _ in formats:
        by_heat = {}
        for key_h, _ in sheets:
            d = parsed[fmt][key_h]
            pa = d["pass_acc_pct"]
            pa_v = pa[np.isfinite(pa)]
            by_heat[key_h] = {
                "pre_tc_mean_sd_C": [round(float(d["pre_tc"].mean()), 3), round(float(d["pre_tc"].std(ddof=1)), 3)],
                "post_tc_mean_sd_C": [round(float(d["post_tc"].mean()), 3), round(float(d["post_tc"].std(ddof=1)), 3)],
                "delta_tc_mean_sd_C": [round(float(d["delta_tc"].mean()), 3), round(float(d["delta_tc"].std(ddof=1)), 3)],
                "post_tc_ge_39_0C_n": int((d["post_tc"] >= 39.0).sum()),
                "post_tc_ge_39_5C_n": int((d["post_tc"] >= 39.5).sum()),
                "max_post_tc_C": round(float(d["post_tc"].max()), 2),
                "total_distance_mean_sd_m": [round(float(d["tot_dist_m"].mean()), 1), round(float(d["tot_dist_m"].std(ddof=1)), 1)],
                "late_minus_early_dist_pct_mean_sd": [round(float(d["late_minus_early_pct"].mean()), 2), round(float(d["late_minus_early_pct"].std(ddof=1)), 2)],
                "hr_pct_mean_sd": [round(float(d["hr_pct"].mean()), 2), round(float(d["hr_pct"].std(ddof=1)), 2)],
                "rpe_mean_sd": [round(float(d["rpe"].mean()), 2), round(float(d["rpe"].std(ddof=1)), 2)],
                "pass_accuracy_mean_sd_pct": [round(float(pa_v.mean()), 2), round(float(pa_v.std(ddof=1)), 2)],
                "lost_balls_mean_sd": [round(float(d["lost_balls"].mean()), 2), round(float(d["lost_balls"].std(ddof=1)), 2)],
            }

        leh = parsed[fmt]["LEH_lt23_9C"]
        heh = parsed[fmt]["HEH_gt28C"]
        # Paired HEH (>28C) minus LEH (<23.9C) contrasts + Heat x Bout interaction on distance
        contrasts = {
            "heat_effect_post_tc_C": paired_summary(heh["post_tc"] - leh["post_tc"], rng),
            "heat_effect_delta_tc_C": paired_summary(heh["delta_tc"] - leh["delta_tc"], rng),
            "heat_effect_total_dist_m": paired_summary(heh["tot_dist_m"] - leh["tot_dist_m"], rng),
            "bout_fatigue_dist_leh_m": paired_summary(leh["late_dist_m"] - leh["early_dist_m"], rng),
            "bout_fatigue_dist_heh_m": paired_summary(heh["late_dist_m"] - heh["early_dist_m"], rng),
            "heat_x_bout_interaction_dist_m": paired_summary(
                (heh["late_dist_m"] - heh["early_dist_m"]) - (leh["late_dist_m"] - leh["early_dist_m"]), rng
            ),
            "heat_effect_hr_pct": paired_summary(heh["hr_pct"] - leh["hr_pct"], rng),
            "heat_effect_rpe": paired_summary(heh["rpe"] - leh["rpe"], rng),
            "heat_effect_pass_acc_pp": paired_summary(heh["pass_acc_pct"] - leh["pass_acc_pct"], rng),
            "heat_effect_lost_balls": paired_summary(heh["lost_balls"] - leh["lost_balls"], rng),
        }
        out_formats[fmt] = {"by_heat_level": by_heat, "paired_heh_vs_leh_and_bout_decomposition": contrasts}

    return {
        "source_id": "SRC-0202",
        "dataset": "SSGs_Heat (PMC13249198, Zenodo 17418102, PLOS ONE 2026)",
        "n_paired": 16,
        "formats": out_formats,
        "cpe45_screening_verdict": (
            "HOLD (provides verified individual-level paired Core Temp + intermittent locomotor distance in meters + "
            "technical motor accuracy across 3 heat levels and 4 bouts, showing rapid thermal escalation toward/above 39.0 C in >28 C heat "
            "already within 840-1680 s; however duration 1680 s < 2700 s, adolescent sample age ~16.5 y, no calibrated mechanical power/force, "
            "no standardized cognitive RT/omissions, and no +45 min/+24 h post45 neuromuscular battery)."
        ),
    }


def analyze_malcolm_2024(cfg: dict) -> dict:
    # Native uncooled CON arm only (external ice slurry + ice collar excluded as non-native per GOVERNANCE.md)
    st_rt_ht = cfg["complex_stroop_rt_ms"]["ht_45min"][0] - cfg["complex_stroop_rt_ms"]["pre"][0]
    st_acc_ht = cfg["complex_stroop_acc_pct"]["ht_45min"][0] - cfg["complex_stroop_acc_pct"]["pre"][0]
    st_acc_90 = cfg["complex_stroop_acc_pct"]["post_90min"][0] - cfg["complex_stroop_acc_pct"]["pre"][0]
    vs_rt_ht = cfg["complex_vs_rt_ms"]["ht_45min"][0] - cfg["complex_vs_rt_ms"]["pre"][0]
    vs_acc_ht = cfg["complex_vs_acc_pct"]["ht_45min"][0] - cfg["complex_vs_acc_pct"]["pre"][0]
    sb5_rt_90 = cfg["sternberg_5item_rt_ms"]["post_90min"][0] - cfg["sternberg_5item_rt_ms"]["pre"][0]
    sb5_acc_90 = cfg["sternberg_5item_acc_pct"]["post_90min"][0] - cfg["sternberg_5item_acc_pct"]["pre"][0]
    return {
        "source_id": "SRC-0203",
        "dataset": "Malcolm et al. 2024 (PMC11369344, Eur J Sport Sci 24:1287, n=12, 90-min intermittent running at 33 C / 50% RH)",
        "native_arm_only": "Unacclimatized uncooled CON arm audited; COOL arm (ice slurry + ice collar) excluded as external cooling under GOVERNANCE.md.",
        "halftime_2700s_deltas_con": {
            "complex_stroop_rt_ms": round(st_rt_ht, 1),
            "complex_stroop_acc_pp": round(st_acc_ht, 2),
            "complex_visual_search_rt_ms": round(vs_rt_ht, 1),
            "complex_visual_search_acc_pp": round(vs_acc_ht, 2),
        },
        "fulltime_5400s_deltas_con": {
            "complex_stroop_acc_pp": round(st_acc_90, 2),
            "sternberg_5item_rt_ms": round(sb5_rt_90, 1),
            "sternberg_5item_acc_pp": round(sb5_acc_90, 2),
        },
        "working_spec_screening": (
            "At exact 45-min (2700 s) half-time in 33 C intermittent running, Complex Stroop accuracy drops -3.3 pp "
            "(98.3->95.0%, reaching -4.5 pp at 90 min) while RT stays near baseline (+4 ms); at 90 min high-load working memory "
            "(Sternberg 5-item) slows by +49 ms (exceeding EXP-0149 working_default +40 ms). Group means only (data request-only), "
            "no individual time-series, no mechanical work/power, no spatial meters, and no post45 neuromuscular battery."
        ),
    }


def run_experiment(data_root: Path) -> dict:
    src_cfg = json.loads(SOURCES_PATH.read_text("utf-8"))
    verified = verify_sources(data_root, src_cfg)
    rng = np.random.default_rng(SEED)

    ssg = analyze_ssgs_heat(data_root, src_cfg, rng)
    malcolm = analyze_malcolm_2024(src_cfg["malcolm_2024_con_native_arm"])

    return {
        "experiment_id": "EXP-0157",
        "stage2_verdict": "HOLD",
        "stage2_blocker_status": "DATA_BLOCKED",
        "scientific_criterion_closed": False,
        "canonical_cpe45_unchanged": True,
        "excluded_screened_datasets": [
            "OSF 84fru (PMC13118115, 2026): n=8 valid recruit firefighters with Core/Skin Temp across 7 PPE ON/OFF transitions only; excluded from quantitative CPE45 battery for lacking external work/power, velocity/distance, cognition, and post45 neuromuscular channels.",
            "Zenodo 19240351 (PMC13395447, 2026): incremental cardiorespiratory step test in volunteer firefighters; excluded as incremental VO2max profiling rather than 2700-s intermittent CPE45 + post45.",
        ],
        "verified_sources": verified,
        "track1_ssgs_heat_individual": ssg,
        "track2_malcolm2024_45min_90min_cognition": malcolm,
        "summary_ruling": (
            "EXP-0157 expands Stage 2 with individual paired multi-bout intermittent heat-stress data (SSGs_Heat n=16 x 3 heat levels x 2v2/4v4, "
            "jointly measuring Core Temp, locomotor distance pacing in meters, HR %max, and technical motor accuracy) plus exact 45-min (2700 s) half-time "
            "intermittent heat cognitive data (Malcolm 2024 n=12). Stage 2 remains HOLD / DATA_BLOCKED: no open human dataset combines full >=2700 s "
            "alternating load, calibrated mechanical power/velocity, spatial coordination in meters, concurrent cognition, thermoregulation, and post45 recovery."
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
        if not RESULTS_PATH.is_file() or RESULTS_PATH.read_text("utf-8") != payload:
            raise SystemExit("EXP-0157 replay mismatch")
        print("EXP-0157 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(f"Wrote {RESULTS_PATH} ({len(payload)} bytes); stage2={res['stage2_verdict']}/{res['stage2_blocker_status']}")


if __name__ == "__main__":
    main()
