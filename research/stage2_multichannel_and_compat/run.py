#!/usr/bin/env python3
"""EXP-0155 (v2 — independent statistical audit & corrigendum):
1. DUO-GAIT (n=16 paired): 2x2 repeated-measures decomposition (Fatigue, Dual-Task, Interaction) + Wilcoxon + outlier/log sensitivity.
2. Goepp 2026 (n=20: 10 BFR vs 10 SHAM + CTRL n=25 SART test-retest): separates pure SHAM HA effect from baseline-adjusted ANCOVA BFR effect with equivalence/precision caveats.
3. Agostinelli 2025 (n=33): full robustness audit (Cook's D outliers, VIF multicollinearity, covariate sensitivity M0..M4, within-sex, Huber robust regression, LOOCV overfitting audit, and explicit 95% harm bounds — never treating p>0.05 as proof of zero harm).
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


def _rm_contrast_stats(eff: np.ndarray, rng: np.random.Generator) -> dict:
    n = len(eff)
    t_v, p_v = stats.ttest_1samp(eff, 0.0)
    _, pw_v = stats.wilcoxon(eff)
    sd = float(eff.std(ddof=1))
    dz = float(eff.mean() / sd) if sd > 0 else 0.0
    eta_p2 = float((t_v * t_v) / (t_v * t_v + (n - 1)))
    return {
        "mean": round(float(eff.mean()), 5),
        "sd": round(sd, 5),
        "ci95_boot": boot_mean_ci(eff, rng),
        "t": round(float(t_v), 3),
        "p_ttest": round(float(p_v), 5),
        "p_wilcoxon": round(float(pw_v), 5),
        "cohen_dz": round(dz, 3),
        "partial_eta2": round(eta_p2, 3),
    }


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
                rows = list(csv.DictReader(io.StringIO(zf.read(name).decode("utf-8"))))
                if rows:
                    data[cond][sub] = {k: float(rows[0][k]) for k, _ in metrics}

    common_subs = sorted(set.intersection(*(set(data[c].keys()) for c in conds)))
    n = len(common_subs)
    out_metrics = {}
    for key, unit in metrics:
        sc = np.array([data["OG_st_control"][s][key] for s in common_subs], dtype=float)
        sf = np.array([data["OG_st_fatigue"][s][key] for s in common_subs], dtype=float)
        dc = np.array([data["OG_dt_control"][s][key] for s in common_subs], dtype=float)
        df = np.array([data["OG_dt_fatigue"][s][key] for s in common_subs], dtype=float)

        diff_comb = df - sc
        pct_comb = 100.0 * (df.mean() - sc.mean()) / sc.mean()
        indiv_pct = 100.0 * (df - sc) / sc
        t_comb, p_comb = stats.ttest_rel(df, sc)

        # Exact 2x2 repeated-measures decomposition (equivalent to 1-df RM-ANOVA F = t^2)
        eff_fat = 0.5 * ((sf + df) - (sc + dc))
        eff_dt = 0.5 * ((dc + df) - (sc + sf))
        eff_int = (df - dc) - (sf - sc)

        out_metrics[key] = {
            "unit": unit,
            "st_control_mean_sd": [round(float(sc.mean()), 5), round(float(sc.std(ddof=1)), 5)],
            "st_fatigue_mean_sd": [round(float(sf.mean()), 5), round(float(sf.std(ddof=1)), 5)],
            "dt_control_mean_sd": [round(float(dc.mean()), 5), round(float(dc.std(ddof=1)), 5)],
            "dt_fatigue_mean_sd": [round(float(df.mean()), 5), round(float(df.std(ddof=1)), 5)],
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
            "rm_2x2_decomposition": {
                "fatigue_main_effect": _rm_contrast_stats(eff_fat, rng),
                "dual_task_main_effect": _rm_contrast_stats(eff_dt, rng),
                "fatigue_x_dual_task_interaction": _rm_contrast_stats(eff_int, rng),
            },
        }

    # Explicit outlier & log sensitivity for clearances_min_CV (sub_18 ST-Fat = 11.8075 vs median 0.7909)
    subs_no18 = [s for s in common_subs if s != "sub_18"]
    sc_log = np.log([data["OG_st_control"][s]["clearances_min_CV"] for s in common_subs])
    sf_log = np.log([data["OG_st_fatigue"][s]["clearances_min_CV"] for s in common_subs])
    dc_log = np.log([data["OG_dt_control"][s]["clearances_min_CV"] for s in common_subs])
    df_log = np.log([data["OG_dt_fatigue"][s]["clearances_min_CV"] for s in common_subs])

    sc_15 = np.array([data["OG_st_control"][s]["clearances_min_CV"] for s in subs_no18])
    sf_15 = np.array([data["OG_st_fatigue"][s]["clearances_min_CV"] for s in subs_no18])
    dc_15 = np.array([data["OG_dt_control"][s]["clearances_min_CV"] for s in subs_no18])
    df_15 = np.array([data["OG_dt_fatigue"][s]["clearances_min_CV"] for s in subs_no18])

    cv_sensitivity = {
        "flagged_outlier": "sub_18 in OG_st_fatigue (clearances_min_CV=11.8075 vs cohort median=0.7909, ~15x median)",
        "log_transformed_n16": {
            "fatigue_main_effect": _rm_contrast_stats(0.5 * ((sf_log + df_log) - (sc_log + dc_log)), rng),
            "dual_task_main_effect": _rm_contrast_stats(0.5 * ((dc_log + df_log) - (sc_log + sf_log)), rng),
            "fatigue_x_dual_task_interaction": _rm_contrast_stats((df_log - dc_log) - (sf_log - sc_log), rng),
        },
        "trimmed_excl_sub18_n15": {
            "fatigue_main_effect": _rm_contrast_stats(0.5 * ((sf_15 + df_15) - (sc_15 + dc_15)), rng),
            "dual_task_main_effect": _rm_contrast_stats(0.5 * ((dc_15 + df_15) - (sc_15 + sf_15)), rng),
            "fatigue_x_dual_task_interaction": _rm_contrast_stats((df_15 - dc_15) - (sf_15 - sc_15), rng),
        },
    }

    return {
        "source_id": "SRC-0195",
        "dataset": "DUO-GAIT (Zhou et al. 2023, Zenodo 8244887, Sci Data 10:543)",
        "n_paired_all_4_conditions": n,
        "participants": common_subs,
        "protocol_duration_s_approx": 360,
        "metrics": out_metrics,
        "clearances_min_cv_outlier_sensitivity": cv_sensitivity,
        "cpe45_spatial_anchor_verdict": (
            "PARTIAL HUMAN EMPIRICAL ANCHOR IN METERS (CORRECTED VIA 2x2 RM DECOMPOSITION): "
            "Fatigue and cognitive dual-task act ADDITIVELY (zero significant Fatigue x Dual-Task interaction on all 7 metrics, p>=0.229) "
            "on distinct spatial channels: cognitive dual-task dominates speed (-0.142 m/s, p=0.0002, eta_p2=0.612), stride length (-0.087 m, p=0.0009), "
            "and max-clearance asymmetry (+0.0255, p=0.0031), whereas physical fatigue dominates minimum foot clearance (-1.14 mm, p=0.0084, Wilcoxon p=0.0042), "
            "minimum-clearance CV (Wilcoxon p=0.0110; log p=0.0116; excl. outlier sub_18 p=0.0112), and stride-time CV (+0.0024, p=0.0384). "
            "Still NOT full CPE45 closure (~360 s << 2700 s, no heavy resistance alternation, no core temp, no post45)."
        ),
    }


def _read_osf_rows(path: Path) -> tuple[list[str], list[list[str]], list[list[str]]]:
    lines = [ln for ln in path.read_text("utf-8-sig").splitlines() if ln.strip()]
    reader = list(csv.reader(lines, delimiter=";"))
    header = [c.strip() for c in reader[0]]
    all_rows = reader[1:]
    arm_rows = [r for r in all_rows if r and r[0].strip() in ("BFR", "SHAM")]
    return header, arm_rows, all_rows


def _f(val: str) -> float:
    s = val.strip().replace(",", ".")
    return float("nan") if not s else float(s)


def analyze_goepp_2026(data_root: Path, src_cfg: dict, rng: np.random.Generator) -> dict:
    sub = data_root / src_cfg["data_subdir"]
    _, demo_rows, _ = _read_osf_rows(sub / "osf_ekvcg_DEMOGRAPHIC.csv")
    _, perf_rows, _ = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_PERFORMANCE.csv")
    _, hrtc_rows, _ = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_HR_TC.csv")
    _, sart_rows, sart_all = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_SART.csv")
    _, nm_rows, _ = _read_osf_rows(sub / "osf_ekvcg_HSTCMDT_NEUROMUSCULAR_FUNCTION.csv")

    n = len(demo_rows)
    if not (n == len(perf_rows) == len(hrtc_rows) == len(sart_rows) == len(nm_rows) == 20):
        raise ValueError("Unexpected OSF row counts")
    groups = [r[0].strip() for r in demo_rows]
    for other in (perf_rows, hrtc_rows, sart_rows, nm_rows):
        if [r[0].strip() for r in other] != groups:
            raise ValueError("Group ordering mismatch across OSF ekvcg CSV tables")

    is_bfr = np.array([g == "BFR" for g in groups])
    is_sham = ~is_bfr

    pairs = {
        "core_temp_21min_C": (np.array([_f(r[3]) for r in perf_rows]), np.array([_f(r[4]) for r in perf_rows])),
        "core_temp_drift_C": (np.array([_f(r[22]) for r in hrtc_rows]), np.array([_f(r[28]) for r in hrtc_rows])),
        "mean_rel_power_pct_pma": (np.array([_f(r[9]) for r in perf_rows]), np.array([_f(r[10]) for r in perf_rows])),
        "sart_acc_b2_pct": (np.array([_f(r[3]) for r in sart_rows]), np.array([_f(r[9]) for r in sart_rows])),
        "sart_acc_b3_pct": (np.array([_f(r[4]) for r in sart_rows]), np.array([_f(r[10]) for r in sart_rows])),
        "sart_acc_intrasession_b3_minus_b2_pp": (
            np.array([_f(r[4]) - _f(r[3]) for r in sart_rows]),
            np.array([_f(r[10]) - _f(r[9]) for r in sart_rows]),
        ),
        "sart_rt_b3_ms": (np.array([_f(r[2]) for r in sart_rows]), np.array([_f(r[8]) for r in sart_rows])),
        "sart_gs_b3_score": (np.array([_f(r[6]) for r in sart_rows]), np.array([_f(r[12]) for r in sart_rows])),
        "acute_mvc_change_pct": (np.array([_f(r[4]) for r in nm_rows]), np.array([_f(r[9]) for r in nm_rows])),
        "acute_va_delta_pp": (np.array([_f(r[15]) for r in nm_rows]), np.array([_f(r[19]) for r in nm_rows])),
    }

    channels = {}
    for name, (pre, post) in pairs.items():
        m = np.isfinite(pre) & np.isfinite(post)
        pre_m, post_m = pre[m], post[m]
        g_m = is_bfr[m].astype(float)
        delta = post_m - pre_m
        _, p_all = stats.ttest_rel(post_m, pre_m)

        d_bfr = delta[g_m == 1.0]
        d_sham = delta[g_m == 0.0]
        _, p_sham = stats.ttest_1samp(d_sham, 0.0)
        _, p_bfr_within = stats.ttest_1samp(d_bfr, 0.0)
        _, p_grp = stats.ttest_ind(d_bfr, d_sham, equal_var=False)

        # Baseline-adjusted ANCOVA: post ~ 1 + BFR + (pre - mean(pre))
        X_anc = np.column_stack([np.ones(len(g_m)), g_m, pre_m - pre_m.mean()])
        b_anc, *_ = np.linalg.lstsq(X_anc, post_m, rcond=None)
        res_anc = post_m - X_anc @ b_anc
        df_anc = len(g_m) - 3
        se_anc = np.sqrt(np.diag(((res_anc @ res_anc) / df_anc) * np.linalg.inv(X_anc.T @ X_anc)))
        t_anc = float(b_anc[1] / se_anc[1])
        p_anc = float(2.0 * stats.t.sf(abs(t_anc), df_anc))
        tcrit = float(stats.t.ppf(0.975, df_anc))
        ci_anc = [round(float(b_anc[1] - tcrit * se_anc[1]), 3), round(float(b_anc[1] + tcrit * se_anc[1]), 3)]

        channels[name] = {
            "n_valid": int(m.sum()),
            "n_bfr_valid": int(len(d_bfr)),
            "n_sham_valid": int(len(d_sham)),
            "pre_ha_mean_sd": [round(float(pre_m.mean()), 3), round(float(pre_m.std(ddof=1)), 3)],
            "post_ha_mean_sd": [round(float(post_m.mean()), 3), round(float(post_m.std(ddof=1)), 3)],
            "pooled_ha_delta": round(float(delta.mean()), 3),
            "pooled_ha_ci95": boot_mean_ci(delta, rng),
            "pooled_ha_paired_p": round(float(p_all), 5),
            "sham_only_ha_delta": round(float(d_sham.mean()), 3),
            "sham_only_ha_ci95": boot_mean_ci(d_sham, rng),
            "sham_only_ha_p": round(float(p_sham), 5),
            "bfr_only_ha_delta": round(float(d_bfr.mean()), 3),
            "bfr_only_ha_p": round(float(p_bfr_within), 5),
            "bfr_minus_sham_delta": round(float(d_bfr.mean() - d_sham.mean()), 3),
            "bfr_minus_sham_ci95_boot": boot_diff_ind_ci(d_bfr, d_sham, rng),
            "bfr_vs_sham_welch_p": round(float(p_grp), 4),
            "ancova_bfr_effect": round(float(b_anc[1]), 3),
            "ancova_bfr_ci95": ci_anc,
            "ancova_bfr_p": round(p_anc, 4),
        }

    # Embedded CTRL SART test-retest reliability cohort (n=25, cols 20..23)
    t_b1, r_b1, t_b2, r_b2 = [], [], [], []
    for r in sart_all:
        if len(r) >= 24 and r[20].strip():
            t_b1.append(_f(r[20]))
            r_b1.append(_f(r[21]))
            t_b2.append(_f(r[22]))
            r_b2.append(_f(r[23]))
    a_tb1, a_rb1, a_tb2, a_rb2 = np.array(t_b1), np.array(r_b1), np.array(t_b2), np.array(r_b2)
    _, p_ctrl_b1 = stats.ttest_rel(a_rb1, a_tb1)
    _, p_ctrl_b2 = stats.ttest_rel(a_rb2, a_tb2)
    ctrl_retest = {
        "n_ctrl": len(a_tb1),
        "b1_test_retest_delta": round(float((a_rb1 - a_tb1).mean()), 3),
        "b1_delta_ci95": boot_mean_ci(a_rb1 - a_tb1, rng),
        "b1_paired_p": round(float(p_ctrl_b1), 5),
        "b2_test_retest_delta": round(float((a_rb2 - a_tb2).mean()), 3),
        "b2_delta_ci95": boot_mean_ci(a_rb2 - a_tb2, rng),
        "b2_paired_p": round(float(p_ctrl_b2), 5),
        "note": "B1 shows significant retest familiarization (+6.19, p=0.0159), whereas B2 is stable (+0.23, p=0.894). No unacclimated 40 C heat-exposure control arm exists for HSTCMDT.",
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
        "ctrl_sart_test_retest": ctrl_retest,
        "cpe45_screening_verdict": (
            "HOLD (CORRECTED HA vs BFR DECOMPOSITION): Pure SHAM Heat Acclimation drives the statistically significant "
            "T_re reduction (-0.184 C, p=0.0089) and SART gains (B2 +22.30 pp p=0.0080, B3 +21.52 pp p=0.0036; CTRL B2 retest +0.23 p=0.894), "
            "while acute MVC drop (+2.44 pp pooled p=0.146; +2.69 pp SHAM p=0.353) and VA (+1.03 pp p=0.296) are NOT statistically significant. "
            "Baseline-adjusted ANCOVA shows no statistically detectable incremental BFR effect over SHAM (p>=0.297 across all 10 channels), "
            "but n=10/arm leaves wide 95% CIs (T_re [-0.173; +0.217] C, SART B3 [-13.89; +21.26] pp, MVC [-4.53; +8.25] pp) that do NOT prove equivalence/zero effect. "
            "Duration 1260 s < 2700 s, intra-session B3-B2 SART drop stays ~-9.6 pp, no spatial meters, no +45 min/+24 h post45."
        ),
    }


def _ols_full(X: np.ndarray, y: np.ndarray, names: list[str]) -> dict:
    n, k = X.shape
    Xd = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    df = n - (k + 1)
    s2 = float((resid @ resid) / df)
    xtx_inv = np.linalg.inv(Xd.T @ Xd)
    se = np.sqrt(np.diag(s2 * xtx_inv))
    tvals = beta / se
    pvals = 2.0 * stats.t.sf(np.abs(tvals), df=df)
    tcrit = float(stats.t.ppf(0.975, df))
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2_in = 1.0 - float((resid @ resid) / ss_tot)

    # Exact LOOCV via hat-matrix diagonal
    h = np.diag(Xd @ xtx_inv @ Xd.T)
    loo_err = resid / (1.0 - h)
    loo_null = (y - y.mean()) * (n / (n - 1.0))
    r2_loo = 1.0 - float((loo_err @ loo_err) / (loo_null @ loo_null))
    mae_loo = float(np.abs(loo_err).mean())
    mae_null = float(np.abs(loo_null).mean())
    cooks_d = (resid ** 2 / ((k + 1) * s2)) * (h / ((1.0 - h) ** 2))

    preds = {}
    for idx, nm in enumerate(["intercept"] + names):
        t_i = float(tvals[idx])
        part_r = float(np.sign(t_i) * np.sqrt((t_i * t_i) / (t_i * t_i + df))) if idx > 0 else None
        entry = {
            "beta": round(float(beta[idx]), 4),
            "se": round(float(se[idx]), 4),
            "ci95": [round(float(beta[idx] - tcrit * se[idx]), 4), round(float(beta[idx] + tcrit * se[idx]), 4)],
            "t": round(t_i, 3),
            "p": round(float(pvals[idx]), 5),
        }
        if part_r is not None:
            entry["partial_r"] = round(part_r, 3)
        preds[nm] = entry
    return {
        "n": int(n),
        "df_resid": int(df),
        "r2_in_sample": round(r2_in, 4),
        "r2_loocv": round(r2_loo, 4),
        "mae_loocv": round(mae_loo, 4),
        "mae_null_loocv": round(mae_null, 4),
        "predictors": preds,
        "_cooks_d": cooks_d,
    }


def _huber_irls(X: np.ndarray, y: np.ndarray, delta: float = 1.345, max_iter: int = 50) -> np.ndarray:
    Xd = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    for _ in range(max_iter):
        r = y - Xd @ beta
        mad = float(np.median(np.abs(r - np.median(r))))
        scale = max(mad / 0.6745, 1e-6)
        u = np.abs(r) / scale
        w = np.where(u <= delta, 1.0, delta / u)
        Xw = Xd * w[:, None]
        beta_new = np.linalg.lstsq(Xw, y * w, rcond=None)[0]
        if np.max(np.abs(beta_new - beta)) < 1e-8:
            beta = beta_new
            break
        beta = beta_new
    return beta


def _compute_vifs(X: np.ndarray, names: list[str]) -> dict[str, float]:
    out = {}
    for j, nm in enumerate(names):
        yj = X[:, j]
        Xo = np.column_stack([np.ones(len(yj)), np.delete(X, j, axis=1)])
        b, *_ = np.linalg.lstsq(Xo, yj, rcond=None)
        r2 = 1.0 - float(((yj - Xo @ b) ** 2).sum() / ((yj - yj.mean()) ** 2).sum())
        out[nm] = round(1.0 / (1.0 - r2), 2)
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
        recs.append({
            "id": int(r[idx["ID"]]),
            "sex": _num("Sex"),
            "age": _num("Age"),
            "weight": w,
            "pbf": _num("PBF"),
            "vo2": _num("VO2"),
            "rel_str": (_num("Squat") + _num("Bench") + _num("Deadlift")) / w,
            "vj_max": _num("VJ_max"),
            "total_time_s": _num("TotalTime"),
            "max_ct_C": _num("maxCT"),
            "max_hr": _num("maxHR"),
            "blc_mmol_l": _num("IMP_BLC"),
            "total_errors": _num("Total_errors"),
        })

    def arr(k: str) -> np.ndarray:
        return np.array([r[k] for r in recs], dtype=float)

    # 1. Bivariate Pearson & Spearman
    bivariate = {}
    for p in ["rel_str", "vj_max", "vo2"]:
        bivariate[p] = {}
        xp = arr(p)
        for o in ["total_time_s", "max_ct_C", "blc_mmol_l", "total_errors", "max_hr"]:
            yo = arr(o)
            m = np.isfinite(xp) & np.isfinite(yo)
            rv, pv = stats.pearsonr(xp[m], yo[m])
            rhov, prhov = stats.spearmanr(xp[m], yo[m])
            bivariate[p][o] = {
                "n": int(m.sum()),
                "pearson_r": round(float(rv), 3),
                "pearson_p": round(float(pv), 5),
                "pearson_ci95": boot_corr_ci(xp[m], yo[m], rng),
                "spearman_rho": round(float(rhov), 3),
                "spearman_p": round(float(prhov), 5),
            }

    # 2. Collinearity & VIF
    p_names = ["rel_str", "vo2", "sex", "pbf", "weight", "age"]
    C = np.corrcoef(np.column_stack([arr(k) for k in p_names]), rowvar=False)
    corr_dict = {p_names[i]: {p_names[j]: round(float(C[i, j]), 3) for j in range(len(p_names))} for i in range(len(p_names))}
    collinearity = {
        "predictor_correlations": corr_dict,
        "vif_M1_relstr_vo2_sex": _compute_vifs(np.column_stack([arr("rel_str"), arr("vo2"), arr("sex")]), ["rel_str", "vo2", "sex"]),
        "vif_M2_plus_pbf": _compute_vifs(np.column_stack([arr("rel_str"), arr("vo2"), arr("sex"), arr("pbf")]), ["rel_str", "vo2", "sex", "pbf"]),
    }

    # 3. Full covariate sensitivity, outlier diagnostics (Cook's D), Huber robust regression, and LOOCV
    robustness = {}
    for o in ["total_time_s", "max_ct_C", "blc_mmol_l", "total_errors"]:
        y_all = arr(o)
        m = np.isfinite(y_all)
        ids_m = [recs[i]["id"] for i in range(len(recs)) if m[i]]

        specs = [
            ("M0_relstr_only", ["rel_str"], m),
            ("M1_relstr_vo2_sex", ["rel_str", "vo2", "sex"], m),
            ("M2_plus_pbf", ["rel_str", "vo2", "sex", "pbf"], m),
            ("M3_plus_age_weight", ["rel_str", "vo2", "sex", "age", "weight"], m),
            ("M4_female_sex1", ["rel_str", "vo2"], m & (arr("sex") == 1.0)),
            ("M4_male_sex2", ["rel_str", "vo2"], m & (arr("sex") == 2.0)),
            ("benchmark_vo2_only", ["vo2"], m),
            ("benchmark_sex_only", ["sex"], m),
        ]
        spec_out = {}
        cooks_m1 = None
        for sname, cols, mask in specs:
            Xm = np.column_stack([arr(c)[mask] for c in cols])
            res_s = _ols_full(Xm, y_all[mask], cols)
            if sname == "M1_relstr_vo2_sex":
                cooks_m1 = res_s["_cooks_d"]
            del res_s["_cooks_d"]
            spec_out[sname] = res_s

        # Cook's D > 4/n refit & Huber robust M1
        n_m = int(m.sum())
        thr = 4.0 / n_m
        hi_pts = [
            {"id": ids_m[i], "cooks_d": round(float(cooks_m1[i]), 3), "y": round(float(y_all[m][i]), 3)}
            for i in range(n_m) if cooks_m1[i] > thr
        ]
        keep = cooks_m1 <= thr
        X_m1 = np.column_stack([arr("rel_str")[m], arr("vo2")[m], arr("sex")[m]])
        y_m1 = y_all[m]
        refit_no_hi = _ols_full(X_m1[keep], y_m1[keep], ["rel_str", "vo2", "sex"])
        del refit_no_hi["_cooks_d"]
        b_hub = _huber_irls(X_m1, y_m1)

        robustness[o] = {
            "specifications": spec_out,
            "cooks_d_threshold_4_over_n": round(thr, 4),
            "high_cooks_d_points": hi_pts,
            "m1_refit_excl_high_cooks_d": refit_no_hi,
            "m1_huber_robust_betas": {
                "intercept": round(float(b_hub[0]), 4),
                "rel_str": round(float(b_hub[1]), 4),
                "vo2": round(float(b_hub[2]), 4),
                "sex": round(float(b_hub[3]), 4),
            },
        }

    # Explicit non-zero-harm 95% confidence bounds summary
    harm_bounds = {
        "max_ct_C_per_1kg_kg_relstr": {
            "M1_ci95": robustness["max_ct_C"]["specifications"]["M1_relstr_vo2_sex"]["predictors"]["rel_str"]["ci95"],
            "M2_plus_pbf_ci95": robustness["max_ct_C"]["specifications"]["M2_plus_pbf"]["predictors"]["rel_str"]["ci95"],
            "interpretation": "p=0.572 does NOT prove absence of thermal harm: 95% CI allows up to +0.208 C (M1) or +0.306 C (M2) core-temp increase per +1 kg/kg RelStr.",
        },
        "total_errors_per_1kg_kg_relstr": {
            "M1_full_n33_ci95": robustness["total_errors"]["specifications"]["M1_relstr_vo2_sex"]["predictors"]["rel_str"]["ci95"],
            "M1_excl_ID17_n32_ci95": robustness["total_errors"]["m1_refit_excl_high_cooks_d"]["predictors"]["rel_str"]["ci95"],
            "M1_loocv_r2": robustness["total_errors"]["specifications"]["M1_relstr_vo2_sex"]["r2_loocv"],
            "interpretation": "p=0.525 does NOT prove absence of cognitive harm: ID=17 is an extreme outlier (55 errors, Cook's D=0.525), LOOCV R2 is negative (-0.055; worse than intercept mean), and 95% CIs allow +1.22 to +5.68 extra errors per +1 kg/kg RelStr.",
        },
        "total_time_s_sensitivity": {
            "M1_full_p": robustness["total_time_s"]["specifications"]["M1_relstr_vo2_sex"]["predictors"]["rel_str"]["p"],
            "M1_excl_high_cooks_p": robustness["total_time_s"]["m1_refit_excl_high_cooks_d"]["predictors"]["rel_str"]["p"],
            "M2_plus_pbf_p": robustness["total_time_s"]["specifications"]["M2_plus_pbf"]["predictors"]["rel_str"]["p"],
            "M1_r2_in_vs_loocv": [
                robustness["total_time_s"]["specifications"]["M1_relstr_vo2_sex"]["r2_in_sample"],
                robustness["total_time_s"]["specifications"]["M1_relstr_vo2_sex"]["r2_loocv"],
            ],
            "interpretation": "Speed association is directionally consistent across models (beta -122 to -195 s per +1 kg/kg), but weakens to p=0.083 when collinear PBF (r=-0.77, VIF=3.24/3.90) is added and to p=0.113 when 3 high-Cook's D cases are removed; in-sample R2=0.522 drops to LOOCV R2=0.335 (M0 RelStr-only generalizes best at R2_LOOCV=0.443).",
        },
    }

    tt = arr("total_time_s")
    tt_v = tt[np.isfinite(tt)]
    return {
        "source_id": "SRC-0197",
        "dataset": "Agostinelli et al. 2025 (PMC12015927, Figshare 28768673, JFMK 10:129)",
        "n_total": len(recs),
        "sex_counts": {"sex_1_female": int((arr("sex") == 1.0).sum()), "sex_2_male": int((arr("sex") == 2.0).sum())},
        "environment": "35 C / 50% RH",
        "protocol_duration_mean_sd_s": [round(float(tt_v.mean()), 1), round(float(tt_v.std(ddof=1)), 1)],
        "bivariate_correlations": bivariate,
        "collinearity_and_vif": collinearity,
        "robustness_audit": robustness,
        "absence_of_evidence_harm_bounds": harm_bounds,
        "stage3_probe_verdict": (
            "EXPLORATORY CROSS-SECTIONAL CONSTRAINT ONLY (CORRECTED — NO CLAIM OF PROVEN ZERO HARM): "
            "VO2max is a robust out-of-sample predictor of maxCT (VO2-only R2_LOOCV=0.409; robust to Cook's D removal p=0.0062). "
            "RelStr is directionally associated with faster loaded work (M0 R2_LOOCV=0.443; M1 beta=-145.9 s p=0.0056), "
            "but sensitive to collinear PBF (r=-0.77, M2 p=0.0827) and 3 high-Cook's D points (n=29 p=0.1129). "
            "Non-significant RelStr slopes on maxCT (95% CI [-0.117; +0.208] C) and Total_errors (extreme outlier ID=17=55 errors, "
            "LOOCV R2=-0.055, 95% CI [-2.96; +5.68] full / [-1.57; +1.22] trimmed) are INCONCLUSIVE and do NOT prove absence of thermal or cognitive harm. "
            "Bivariate BLC elevation (+1.78 mmol/L, p=0.0165) attenuates to NS after adjusting for Sex/VO2/PBF (p=0.38..0.93). Stage 3 remains HOLD."
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
        "audit_revision": "v2_independent_statistical_audit_corrigendum",
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
            "EXP-0155 v2 (independent statistical audit & corrigendum): "
            "(1) DUO-GAIT (n=16) 2x2 RM decomposition shows Fatigue and Dual-Task act additively (interaction p>=0.229) on distinct channels "
            "(Dual-Task drives speed/asymmetry; Fatigue drives min foot clearance and clearance CV after accounting for outlier sub_18); "
            "(2) Goepp 2026 (n=20) separates pure SHAM HA gains (T_re -0.184 C p=0.0089, SART B3 +21.52 pp p=0.0036; MVC drop NS p=0.146) "
            "from baseline-adjusted ANCOVA BFR contrasts (all p>=0.297, but wide n=10/arm CIs do not prove equivalence); "
            "(3) Agostinelli 2025 (n=33) confirms robust VO2max thermal prediction (R2_LOOCV=0.409), shows RelStr speed slope is sensitive to collinear PBF (r=-0.77, p=0.083) "
            "and 3 Cook's D points (p=0.113), flags ID=17 (55 errors), and retracts overstated 'no thermal/cognitive harm' claims because 95% CIs remain wide and Total_errors LOOCV R2 is negative (-0.055). "
            "Stage 2 and Stage 3 remain HOLD / DATA_BLOCKED."
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
