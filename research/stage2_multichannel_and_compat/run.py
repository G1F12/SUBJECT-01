#!/usr/bin/env python3
"""EXP-0155: Multi-channel Stage 2 (CPE45) empirical expansion (DUO-GAIT spatial anchor in meters +
Goepp 2026 4-channel heat-stress dual-task) and within-person Stage 3 compatibility probe (Agostinelli 2025).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import openpyxl
from scipy import stats

HERE = Path(__file__).resolve().parent
SOURCES_PATH = HERE / "SOURCES.json"
RESULTS_PATH = HERE / "RESULTS.json"
SEED = 20260420
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
            raise ValueError(
                f"Checksum/size mismatch for {fname}: got ({got_bytes}, {got_sha}), "
                f"expected ({meta['bytes']}, {meta['sha256']})"
            )
        verified[fname] = {
            "source_id": meta["source_id"],
            "bytes": got_bytes,
            "sha256": got_sha,
        }
    return verified


def boot_mean_ci(arr: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT) -> list[float]:
    n = len(arr)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = arr[idx].mean(axis=1)
    return [round(float(np.percentile(means, 2.5)), 4), round(float(np.percentile(means, 97.5)), 4)]


def boot_diff_ind_ci(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT) -> list[float]:
    ia = rng.integers(0, len(a), size=(n_boot, len(a)))
    ib = rng.integers(0, len(b), size=(n_boot, len(b)))
    diffs = a[ia].mean(axis=1) - b[ib].mean(axis=1)
    return [round(float(np.percentile(diffs, 2.5)), 4), round(float(np.percentile(diffs, 97.5)), 4)]


def boot_corr_ci(x: np.ndarray, y: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT) -> list[float]:
    n = len(x)
    rs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xs, ys = x[idx], y[idx]
        if np.std(xs) > 0 and np.std(ys) > 0:
            rs.append(float(np.corrcoef(xs, ys)[0, 1]))
    return [round(float(np.percentile(rs, 2.5)), 3), round(float(np.percentile(rs, 97.5)), 3)]


def analyze_duogait(data_root: Path, src_cfg: dict, rng: np.random.Generator) -> dict:
    zpath = data_root / src_cfg["data_subdir"] / "duogait_processed.zip"
    conds = ["OG_st_control", "OG_st_fatigue", "OG_dt_control", "OG_dt_fatigue"]
    metrics = [
        ("speed_avg", "m/s"),
        ("stride_lengths_avg", "m"),
        ("clearances_min_avg", "m"),
        ("clearances_min_CV", "ratio"),
        ("stride_lengths_CV", "ratio"),
        ("stride_times_CV", "ratio"),
        ("clearances_max_SI", "pct"),
    ]
    data: dict[str, dict[str, dict[str, float]]] = {c: {} for c in conds}
    with zipfile.ZipFile(zpath) as zf:
        for name in zf.namelist():
            parts = name.split("/")
            if len(parts) == 4 and parts[0] == "processed" and parts[1] in data and parts[3] == "aggregate_params.csv":
                cond, sub = parts[1], parts[2]
                txt = zf.read(name).decode("utf-8")
                rows = list(csv.DictReader(io.StringIO(txt)))
                if rows:
                    data[cond][sub] = {k: float(rows[0][k]) for k, _ in metrics}

    common_subs = sorted(set.intersection(*(set(data[c].keys()) for c in conds)))
    n = len(common_subs)
    out_metrics = {}
    for key, unit in metrics:
        arrs = {c: np.array([data[c][s][key] for s in common_subs], dtype=float) for c in conds}
        st_con = arrs["OG_st_control"]
        dt_fat = arrs["OG_dt_fatigue"]
        st_fat = arrs["OG_st_fatigue"]
        dt_con = arrs["OG_dt_control"]

        diff_comb = dt_fat - st_con
        pct_comb = 100.0 * (dt_fat.mean() - st_con.mean()) / st_con.mean()
        indiv_pct = 100.0 * (dt_fat - st_con) / st_con
        t_comb, p_comb = stats.ttest_rel(dt_fat, st_con)
        _, p_fat = stats.ttest_rel(st_fat, st_con)
        _, p_dt = stats.ttest_rel(dt_con, st_con)

        out_metrics[key] = {
            "unit": unit,
            "st_control_mean_sd": [round(float(st_con.mean()), 5), round(float(st_con.std(ddof=1)), 5)],
            "st_fatigue_mean_sd": [round(float(st_fat.mean()), 5), round(float(st_fat.std(ddof=1)), 5)],
            "dt_control_mean_sd": [round(float(dt_con.mean()), 5), round(float(dt_con.std(ddof=1)), 5)],
            "dt_fatigue_mean_sd": [round(float(dt_fat.mean()), 5), round(float(dt_fat.std(ddof=1)), 5)],
            "dt_fat_minus_st_con_mean": round(float(diff_comb.mean()), 5),
            "dt_fat_minus_st_con_ci95": boot_mean_ci(diff_comb, rng),
            "dt_fat_minus_st_con_pct_of_mean": round(float(pct_comb), 2),
            "indiv_pct_change_q25_q50_q75": [
                round(float(np.percentile(indiv_pct, 25)), 2),
                round(float(np.percentile(indiv_pct, 50)), 2),
                round(float(np.percentile(indiv_pct, 75)), 2),
            ],
            "paired_t_dt_fat_vs_st_con": round(float(t_comb), 3),
            "paired_p_dt_fat_vs_st_con": round(float(p_comb), 5),
            "paired_p_st_fat_vs_st_con": round(float(p_fat), 5),
            "paired_p_dt_con_vs_st_con": round(float(p_dt), 5),
        }

    return {
        "source_id": "SRC-0195",
        "dataset": "DUO-GAIT (Zhou et al. 2023, Zenodo 8244887, Sci Data 10:543)",
        "n_paired_all_4_conditions": n,
        "participants": common_subs,
        "protocol_duration_s_approx": 360,
        "metrics": out_metrics,
        "cpe45_spatial_anchor_verdict": (
            "REPLACES UNASSESSED_NO_HUMAN_ANCHOR WITH PARTIAL HUMAN EMPIRICAL ANCHOR IN METERS: "
            "combined physical fatigue + cognitive dual-task degrades gait speed (-11.8%), stride length (-7.8%), "
            "minimum foot clearance (-27.7%, -2.6 mm), spatial clearance CV (+57.2%), and clearance asymmetry (+68.4%). "
            "Still NOT full CPE45 closure (duration ~360 s << 2700 s, no heavy resistance alternation, no core temp, no post45)."
        ),
    }


def _read_osf_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    lines = [ln for ln in path.read_text("utf-8-sig").splitlines() if ln.strip()]
    reader = list(csv.reader(lines, delimiter=";"))
    header = [c.strip() for c in reader[0]]
    rows = [r for r in reader[1:] if r and r[0].strip() in ("BFR", "SHAM")]
    return header, rows


def _f(val: str) -> float:
    s = val.strip().replace(",", ".")
    return float("nan") if not s else float(s)


def analyze_goepp_2026(data_root: Path, src_cfg: dict, rng: np.random.Generator) -> dict:
    sub = data_root / src_cfg["data_subdir"]
    _, demo_rows = _read_osf_rows(sub / "osf_ekvcg_DEMOGRAPHIC.csv")
    _, perf_rows = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_PERFORMANCE.csv")
    _, hrtc_rows = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_HR_TC.csv")
    _, sart_rows = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_SART.csv")
    _, nm_rows = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_NEUROMUSCULAR_FUNCTION.csv")

    n = len(demo_rows)
    if not (n == len(perf_rows) == len(hrtc_rows) == len(sart_rows) == len(nm_rows) == 20):
        raise ValueError(f"Unexpected OSF row counts: {n}, {len(perf_rows)}, {len(hrtc_rows)}, {len(sart_rows)}, {len(nm_rows)}")
    groups = [r[0].strip() for r in demo_rows]
    for other in (perf_rows, hrtc_rows, sart_rows, nm_rows):
        if [r[0].strip() for r in other] != groups:
            raise ValueError("Group ordering mismatch across OSF ekvcg CSV tables")

    is_bfr = np.array([g == "BFR" for g in groups])
    is_sham = ~is_bfr

    # Verified column indices from raw CSV headers:
    # PERF: 3=PRE_TC_21, 4=POST_TC_21, 9=%PO_AVERAGED_PRE, 10=%PO_AVERAGED_POST
    # HR_TC: 22=DRIFT_TREC_PRE, 28=DRIFT_TREC_POST (duplicate header name in raw file)
    # SART: 1=PRE_RT_B2, 2=PRE_RT_B3, 3=PRE_ACC_B2, 4=PRE_ACC_B3, 5=PRE_GS_B2, 6=PRE_GS_B3,
    #       7=POST_RT_B2, 8=POST_RT_B3, 9=POST_ACC_B2, 10=POST_ACC_B3, 11=POST_GS_B2, 12=POST_GS_B3
    # NM: 4=CHANGEPRE (% MVC drop pre-HA), 9=CHANGEPOST (% MVC drop post-HA),
    #     15=DELTA_VA_BRIEF_PRE, 19=DELTA_VA_BRIEF_POST
    pairs = {
        "core_temp_21min_C": (
            np.array([_f(r[3]) for r in perf_rows]),
            np.array([_f(r[4]) for r in perf_rows]),
        ),
        "core_temp_drift_C": (
            np.array([_f(r[22]) for r in hrtc_rows]),
            np.array([_f(r[28]) for r in hrtc_rows]),
        ),
        "mean_rel_power_pct_pma": (
            np.array([_f(r[9]) for r in perf_rows]),
            np.array([_f(r[10]) for r in perf_rows]),
        ),
        "sart_acc_b2_pct": (
            np.array([_f(r[3]) for r in sart_rows]),
            np.array([_f(r[9]) for r in sart_rows]),
        ),
        "sart_acc_b3_pct": (
            np.array([_f(r[4]) for r in sart_rows]),
            np.array([_f(r[10]) for r in sart_rows]),
        ),
        "sart_acc_intrasession_b3_minus_b2_pp": (
            np.array([_f(r[4]) - _f(r[3]) for r in sart_rows]),
            np.array([_f(r[10]) - _f(r[9]) for r in sart_rows]),
        ),
        "sart_rt_b3_ms": (
            np.array([_f(r[2]) for r in sart_rows]),
            np.array([_f(r[8]) for r in sart_rows]),
        ),
        "sart_gs_b3_score": (
            np.array([_f(r[6]) for r in sart_rows]),
            np.array([_f(r[12]) for r in sart_rows]),
        ),
        "acute_mvc_change_pct": (
            np.array([_f(r[4]) for r in nm_rows]),
            np.array([_f(r[9]) for r in nm_rows]),
        ),
        "acute_va_delta_pp": (
            np.array([_f(r[15]) for r in nm_rows]),
            np.array([_f(r[19]) for r in nm_rows]),
        ),
    }

    channels = {}
    for name, (pre, post) in pairs.items():
        m = np.isfinite(pre) & np.isfinite(post)
        pre_m, post_m = pre[m], post[m]
        delta = post_m - pre_m
        t_all, p_all = stats.ttest_rel(post_m, pre_m)
        d_bfr = (post - pre)[m & is_bfr]
        d_sham = (post - pre)[m & is_sham]
        t_grp, p_grp = stats.ttest_ind(d_bfr, d_sham, equal_var=False)
        channels[name] = {
            "n_valid": int(m.sum()),
            "n_bfr_valid": int((m & is_bfr).sum()),
            "n_sham_valid": int((m & is_sham).sum()),
            "pre_ha_mean_sd": [round(float(pre_m.mean()), 3), round(float(pre_m.std(ddof=1)), 3)],
            "post_ha_mean_sd": [round(float(post_m.mean()), 3), round(float(post_m.std(ddof=1)), 3)],
            "pooled_post_minus_pre": round(float(delta.mean()), 3),
            "pooled_delta_ci95": boot_mean_ci(delta, rng),
            "pooled_paired_p": round(float(p_all), 5),
            "bfr_delta_mean": round(float(d_bfr.mean()), 3),
            "sham_delta_mean": round(float(d_sham.mean()), 3),
            "bfr_minus_sham_delta": round(float(d_bfr.mean() - d_sham.mean()), 3),
            "bfr_minus_sham_ci95": boot_diff_ind_ci(d_bfr, d_sham, rng),
            "bfr_vs_sham_welch_p": round(float(p_grp), 4),
        }

    tc21_pre, tc21_post = pairs["core_temp_21min_C"]
    return {
        "source_id": "SRC-0196",
        "dataset": "Goepp et al. 2026 (PMC13132146, OSF ekvcg, Scand J Med Sci Sports)",
        "n_total": n,
        "n_bfr": int(is_bfr.sum()),
        "n_sham": int(is_sham.sum()),
        "environment": "40 C / 40% RH",
        "protocol_duration_s": 1260,
        "tc_below_39C_pre_ha_n": int((tc21_pre < 39.0).sum()),
        "tc_below_39C_post_ha_n": int((tc21_post < 39.0).sum()),
        "channels": channels,
        "cpe45_screening_verdict": (
            "HOLD (4-channel internal Heat Acclimation improves T_re [-0.17 C], concurrent SART B3 accuracy [+21.6 pp], "
            "and acute post-exercise MVC retention [+2.44 pp] without BFR superiority over SHAM; however duration is 1260 s < 2700 s, "
            "intra-session B3-B2 SART drop remains ~-10 pp, no spatial coordination in meters, and no +45 min/+24 h post45 probe)."
        ),
    }


def ols_fit(X: np.ndarray, y: np.ndarray, names: list[str]) -> dict:
    n, k = X.shape
    Xd = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    df = n - (k + 1)
    s2 = float((resid @ resid) / df)
    cov = s2 * np.linalg.inv(Xd.T @ Xd)
    se = np.sqrt(np.diag(cov))
    tvals = beta / se
    pvals = 2.0 * stats.t.sf(np.abs(tvals), df=df)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((resid @ resid) / ss_tot)
    out = {"n": int(n), "r2": round(r2, 4), "df_resid": int(df), "predictors": {}}
    for idx, nm in enumerate(["intercept"] + names):
        t_i = float(tvals[idx])
        part_r = float(np.sign(t_i) * np.sqrt((t_i * t_i) / (t_i * t_i + df))) if idx > 0 else None
        entry = {
            "beta": round(float(beta[idx]), 4),
            "se": round(float(se[idx]), 4),
            "t": round(t_i, 3),
            "p": round(float(pvals[idx]), 5),
        }
        if part_r is not None:
            entry["partial_r"] = round(part_r, 3)
        out["predictors"][nm] = entry
    return out


def analyze_agostinelli_2025(data_root: Path, src_cfg: dict, rng: np.random.Generator) -> dict:
    xpath = data_root / src_cfg["data_subdir"] / "agostinelli_FORD_Training.xlsx"
    wb = openpyxl.load_workbook(xpath, data_only=True)
    ws = wb["Sheet1"]
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[0])
    idx = {h: i for i, h in enumerate(header)}

    recs = []
    for r in rows[1:]:
        if r[idx["ID"]] is None:
            continue
        def _num(col: str) -> float:
            v = r[idx[col]]
            return float("nan") if v is None else float(v)

        w = _num("Weight")
        sq = _num("Squat")
        bn = _num("Bench")
        dl = _num("Deadlift")
        recs.append({
            "sex": _num("Sex"),
            "weight": w,
            "vo2": _num("VO2"),
            "rel_str": (sq + bn + dl) / w,
            "rel_dl": dl / w,
            "vj_max": _num("VJ_max"),
            "total_time_s": _num("TotalTime"),
            "max_ct_C": _num("maxCT"),
            "avg_ct_C": _num("avgCT"),
            "max_hr": _num("maxHR"),
            "blc_mmol_l": _num("IMP_BLC"),
            "total_errors": _num("Total_errors"),
        })

    def arr(k: str) -> np.ndarray:
        return np.array([r[k] for r in recs], dtype=float)

    predictors = ["rel_str", "vj_max", "vo2"]
    outcomes = ["total_time_s", "max_ct_C", "blc_mmol_l", "total_errors", "max_hr"]
    bivariate = {}
    for p in predictors:
        bivariate[p] = {}
        xp = arr(p)
        for o in outcomes:
            yo = arr(o)
            m = np.isfinite(xp) & np.isfinite(yo)
            r_val, p_val = stats.pearsonr(xp[m], yo[m])
            bivariate[p][o] = {
                "n": int(m.sum()),
                "r": round(float(r_val), 3),
                "p": round(float(p_val), 5),
                "ci95": boot_corr_ci(xp[m], yo[m], rng),
            }

    ols_models = {}
    for o in ["total_time_s", "max_ct_C", "blc_mmol_l", "total_errors"]:
        y = arr(o)
        rs = arr("rel_str")
        v2 = arr("vo2")
        sx = arr("sex")
        m = np.isfinite(y) & np.isfinite(rs) & np.isfinite(v2) & np.isfinite(sx)
        ols_models[o] = ols_fit(np.column_stack([rs[m], v2[m], sx[m]]), y[m], ["rel_str", "vo2", "sex"])

    rs_all = arr("rel_str")
    med_rs = float(np.median(rs_all))
    hi = rs_all >= med_rs
    lo = ~hi
    split_comp = {"median_rel_str_kg_per_kg": round(med_rs, 3), "n_high": int(hi.sum()), "n_low": int(lo.sum()), "outcomes": {}}
    for o in ["total_time_s", "max_ct_C", "blc_mmol_l", "total_errors"]:
        y = arr(o)
        yh = y[hi & np.isfinite(y)]
        yl = y[lo & np.isfinite(y)]
        _, pv = stats.ttest_ind(yh, yl, equal_var=False)
        split_comp["outcomes"][o] = {
            "high_rel_str_mean_sd": [round(float(yh.mean()), 3), round(float(yh.std(ddof=1)), 3)],
            "low_rel_str_mean_sd": [round(float(yl.mean()), 3), round(float(yl.std(ddof=1)), 3)],
            "high_minus_low": round(float(yh.mean() - yl.mean()), 3),
            "ci95": boot_diff_ind_ci(yh, yl, rng),
            "welch_p": round(float(pv), 5),
        }

    tt = arr("total_time_s")
    tt_valid = tt[np.isfinite(tt)]
    return {
        "source_id": "SRC-0197",
        "dataset": "Agostinelli et al. 2025 (PMC12015927, Figshare 28768673, JFMK 10:129)",
        "n_total": len(recs),
        "environment": "35 C / 50% RH",
        "protocol_duration_mean_sd_s": [round(float(tt_valid.mean()), 1), round(float(tt_valid.std(ddof=1)), 1)],
        "bivariate_correlations": bivariate,
        "ols_controlling_vo2_and_sex": ols_models,
        "high_vs_low_rel_str_split": split_comp,
        "stage3_probe_verdict": (
            "EMPIRICAL COMPATIBILITY CONSTRAINT ESTABLISHED (NOT STAGE 3 CLOSURE): "
            "Within the same adults under 35 C heat + 4-round loaded carries/deadlifts + cognition, "
            "mass-normalized strength (RelStr) independently speeds up intermittent loaded work without degrading core temp or cognitive accuracy, "
            "BUT elevates blood lactate and does NOT replace VO2max for thermal ceiling control (VO2max remains the dominant predictor of maxCT). "
            "Stage 3 remains HOLD because Stage 1 and Stage 2 are unclosed and this cohort is cross-sectional (~1124 s < 2700 s) with no tendon safety or post45 tracking."
        ),
    }


def run_experiment(data_root: Path) -> dict:
    src_cfg = json.loads(SOURCES_PATH.read_text("utf-8"))
    verified = verify_sources(data_root, src_cfg)
    rng = np.random.default_rng(SEED)

    duogait = analyze_duogait(data_root, src_cfg, rng)
    goepp = analyze_goepp_2026(data_root, src_cfg, rng)
    agostinelli = analyze_agostinelli_2025(data_root, src_cfg, rng)

    return {
        "experiment_id": "EXP-0155",
        "stage2_verdict": "HOLD",
        "stage2_blocker_status": "DATA_BLOCKED",
        "stage3_verdict": "HOLD",
        "stage3_blocker_status": "DATA_BLOCKED_PREREQS_AND_UNIFIED_COHORT",
        "scientific_criteria_closed": {"stage2": False, "stage3": False},
        "canonical_cpe45_unchanged": True,
        "verified_sources": verified,
        "track1_duogait_spatial_anchor": duogait,
        "track2_goepp2026_four_channel_heat_ha": goepp,
        "track3_agostinelli2025_stage3_compat_probe": agostinelli,
        "summary_ruling": (
            "EXP-0155 advances Stage 2 by replacing UNASSESSED_NO_HUMAN_ANCHOR for spatial coordination with a verified paired human anchor in meters (DUO-GAIT, n=16) "
            "and auditing a 4-channel internal Heat Acclimation trial (Goepp 2026, n=20, 40 C), and advances Stage 3 with a direct within-person compatibility probe "
            "(Agostinelli 2025, n=33, 35 C) quantifying strength-speed synergy vs lactate/VO2max thermal constraint. "
            "Both Stage 2 and Stage 3 remain HOLD / DATA_BLOCKED because no single open human cohort covers >=2700 s alternating load + spatial meters + cognition + thermoregulation + post45, "
            "nor links it longitudinally to Stage 1 ADAPT25/FORCE20 + validated tendon safety."
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
            raise SystemExit("EXP-0155 replay mismatch")
        print("EXP-0155 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(
            f"Wrote {RESULTS_PATH} ({len(payload)} bytes); "
            f"stage2={res['stage2_verdict']}/{res['stage2_blocker_status']}; "
            f"stage3={res['stage3_verdict']}"
        )


if __name__ == "__main__":
    main()
