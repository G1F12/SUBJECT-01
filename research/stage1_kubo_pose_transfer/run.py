#!/usr/bin/env python3
"""EXP-0152: Pose-transfer audit (0 deg vs 10 deg PF) and tendon safety margin for Kubo-Ishigaki (2017) ADAPT25."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import openpyxl
import scipy.io
from scipy import stats

HERE = Path(__file__).resolve().parent
SOURCES_PATH = HERE / "SOURCES.json"
RESULTS_PATH = HERE / "RESULTS.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sources(data_root: Path, src: dict) -> dict:
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
    return checked


def _get_2d_arrays(mv) -> list[np.ndarray]:
    if isinstance(mv, np.ndarray) and mv.dtype == object:
        out = []
        for item in mv.flat:
            arr = np.asarray(item, dtype=float)
            if arr.ndim == 2 and arr.shape[0] >= 2:
                out.append(arr)
        return out
    arr = np.asarray(mv, dtype=float)
    if arr.ndim == 2 and arr.shape[0] >= 2:
        return [arr]
    return []


def extract_chen_franklin(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open("Supplementary_Chen_Franklin_2024/S3_Datasets.mat") as f:
            mat = scipy.io.loadmat(io.BytesIO(f.read()), squeeze_me=True, struct_as_record=False)

    pf_curves = []
    for i, e in enumerate(mat["dataset_isometric_passive"]):
        obj = str(e.measureObject)
        mtype = str(e.measureType)
        pdof = str(e.primaryDoF)
        sdof = str(e.secondaryDoF)
        if "ankle" not in obj.lower() or "plantar" not in obj.lower() or "passive" in mtype.lower():
            continue
        if "plantar(-)" not in pdof.lower() and "dorsi(+)" not in pdof.lower():
            continue
        for mv in _get_2d_arrays(e.measureValue):
            ang = mv[0, :]
            val = np.abs(mv[-1, :])
            sec = mv[1, :] if mv.shape[0] >= 3 else np.zeros_like(ang)
            mask = (np.isnan(sec) | (np.abs(sec) < 1e-6)) if "knee" in sdof.lower() else np.ones(len(ang), dtype=bool)
            if int(np.sum(mask)) < 2:
                continue
            a0, v0 = ang[mask], val[mask]
            order = np.argsort(a0)
            a0, v0 = a0[order], v0[order]
            if float(a0[0]) <= -10.0 and float(a0[-1]) >= 0.0:
                t10 = float(np.interp(-10.0, a0, v0))
                t0 = float(np.interp(0.0, a0, v0))
                if t0 > 0:
                    pf_curves.append({
                        "index": i + 1,
                        "reference": str(e.reference),
                        "subject_type": str(e.subjectType),
                        "measure_type": mtype,
                        "torque_10deg_pf_nm": round(t10, 4),
                        "torque_0deg_nm": round(t0, 4),
                        "ratio_10pf_to_0": round(t10 / t0, 6),
                    })

    ma_curves = []
    for i, e in enumerate(mat["dataset_momentArm"]):
        obj = str(e.measureObject)
        pdof = str(e.primaryDoF)
        stype = str(e.subjectType)
        if not any(k in obj.lower() for k in ("achilles", "triceps", "gastroc", "soleus")):
            continue
        if "ankle" not in pdof.lower():
            continue
        if "C" in stype or "cadaver" in str(e.subject).lower():
            continue
        if "plantar(-)" not in pdof.lower() and "dorsi(+)" not in pdof.lower():
            continue
        for mv in _get_2d_arrays(e.measureValue):
            ang = mv[0, :]
            val = np.abs(mv[-1, :])
            if mv.shape[0] >= 3 and "knee" in str(e.secondaryDoF).lower():
                sec = mv[1, :]
                mask = np.isnan(sec) | (np.abs(sec) < 1e-6)
                if int(np.sum(mask)) >= 2:
                    ang, val = ang[mask], val[mask]
            order = np.argsort(ang)
            ang, val = ang[order], val[order]
            if float(ang[0]) <= -10.0 and float(ang[-1]) >= 0.0:
                m10 = float(np.interp(-10.0, ang, val))
                m0 = float(np.interp(0.0, ang, val))
                if m0 > 0:
                    ma_curves.append({
                        "index": i + 1,
                        "reference": str(e.reference),
                        "subject_type": stype,
                        "object": obj,
                        "measure_type": str(e.measureType),
                        "ma_10deg_pf_mm": round(m10, 4),
                        "ma_0deg_mm": round(m0, 4),
                        "ratio_10pf_to_0": round(m10 / m0, 6),
                    })

    ratios_all = np.array([c["ratio_10pf_to_0"] for c in pf_curves], dtype=float)
    ratios_ym = np.array([c["ratio_10pf_to_0"] for c in pf_curves if c["subject_type"] in ("YM", "YA", "Y")], dtype=float)
    holzer_row = next(c for c in pf_curves if "Holzer" in c["reference"])

    ma0_all = np.array([c["ma_0deg_mm"] for c in ma_curves], dtype=float)
    ma10_all = np.array([c["ma_10deg_pf_mm"] for c in ma_curves], dtype=float)
    ma_rat = np.array([c["ratio_10pf_to_0"] for c in ma_curves], dtype=float)

    return {
        "n_pf_torque_curves_all": len(pf_curves),
        "n_pf_torque_curves_young_male": int(len(ratios_ym)),
        "torque_ratio_10pf_to_0_all": {
            "mean": round(float(np.mean(ratios_all)), 4),
            "sd": round(float(np.std(ratios_all, ddof=1)), 4),
            "median": round(float(np.median(ratios_all)), 4),
            "iqr": [round(float(np.percentile(ratios_all, 25)), 4), round(float(np.percentile(ratios_all, 75)), 4)],
            "min": round(float(np.min(ratios_all)), 4),
            "max": round(float(np.max(ratios_all)), 4),
        },
        "torque_ratio_10pf_to_0_young_male": {
            "mean": round(float(np.mean(ratios_ym)), 4),
            "sd": round(float(np.std(ratios_ym, ddof=1)), 4),
            "median": round(float(np.median(ratios_ym)), 4),
            "min": round(float(np.min(ratios_ym)), 4),
            "max": round(float(np.max(ratios_ym)), 4),
        },
        "holzer_2020_prone_extended_14m": holzer_row,
        "n_in_vivo_at_ma_curves": len(ma_curves),
        "ma_0deg_mm_summary": {
            "mean": round(float(np.mean(ma0_all)), 2),
            "sd": round(float(np.std(ma0_all, ddof=1)), 2),
            "min": round(float(np.min(ma0_all)), 2),
            "max": round(float(np.max(ma0_all)), 2),
        },
        "ma_10deg_pf_mm_summary": {
            "mean": round(float(np.mean(ma10_all)), 2),
            "sd": round(float(np.std(ma10_all, ddof=1)), 2),
            "min": round(float(np.min(ma10_all)), 2),
            "max": round(float(np.max(ma10_all)), 2),
        },
        "ma_ratio_10pf_to_0_summary": {
            "mean": round(float(np.mean(ma_rat)), 4),
            "sd": round(float(np.std(ma_rat, ddof=1)), 4),
            "min": round(float(np.min(ma_rat)), 4),
            "max": round(float(np.max(ma_rat)), 4),
        },
        "ma_10deg_pf_values_mm": [round(float(x), 4) for x in ma10_all],
    }


def extract_wolfram_mri(xlsx_path: Path) -> dict:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    neutral = []
    for r in range(2, ws.max_row + 1):
        val = ws.cell(r, 3).value
        if isinstance(val, (int, float)):
            neutral.append(float(val))
    arr = np.array(neutral, dtype=float)
    return {
        "n_participants": int(len(arr)),
        "ma_0deg_neutral_mri_mm": {
            "mean": round(float(np.mean(arr)), 2),
            "sd": round(float(np.std(arr, ddof=1)), 2),
            "cv_pct": round(float(np.std(arr, ddof=1) / np.mean(arr) * 100.0), 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
        },
    }


def compute_holzer_ma(src: dict) -> tuple[dict, np.ndarray, np.ndarray]:
    rows = []
    ma0_list, ma10_list, ratio_list = [], [], []
    for fn in src["holzer_2020_table2_ma_polynomials_cm"]["functions"]:
        p1, p2, p3 = fn["p1"], fn["p2"], fn["p3"]
        m0 = p3 * 10.0
        m10 = (p1 * ((-10.0) ** 2) + p2 * (-10.0) + p3) * 10.0
        rat = m10 / m0
        ma0_list.append(m0)
        ma10_list.append(m10)
        ratio_list.append(rat)
        rows.append({
            "study": fn["study"],
            "method": fn["method"],
            "intensity": fn["intensity"],
            "ma_0deg_mm": round(m0, 2),
            "ma_10deg_pf_mm": round(m10, 2),
            "ratio_10pf_to_0": round(rat, 4),
        })
    ma0 = np.array(ma0_list, dtype=float)
    ma10 = np.array(ma10_list, dtype=float)
    rat = np.array(ratio_list, dtype=float)
    mvc_ma10 = np.array([r["ma_10deg_pf_mm"] for r in rows if r["intensity"] == "MVC"], dtype=float)
    summary = {
        "n_functions": len(rows),
        "ma_0deg_mm": {"mean": round(float(np.mean(ma0)), 2), "sd": round(float(np.std(ma0, ddof=1)), 2), "min": round(float(np.min(ma0)), 2), "max": round(float(np.max(ma0)), 2)},
        "ma_10deg_pf_mm": {"mean": round(float(np.mean(ma10)), 2), "sd": round(float(np.std(ma10, ddof=1)), 2), "min": round(float(np.min(ma10)), 2), "max": round(float(np.max(ma10)), 2)},
        "mvc_only_n": int(len(mvc_ma10)),
        "mvc_only_ma_10deg_pf_mm_range": [round(float(np.min(mvc_ma10)), 2), round(float(np.max(mvc_ma10)), 2)],
        "ratio_10pf_to_0": {"mean": round(float(np.mean(rat)), 4), "sd": round(float(np.std(rat, ddof=1)), 4), "min": round(float(np.min(rat)), 4), "max": round(float(np.max(rat)), 4)},
        "models": rows,
    }
    return summary, ma0, ma10


def compute_tendon_safety(src: dict, holzer_ma0: np.ndarray, holzer_ma10: np.ndarray, cf: dict) -> dict:
    kb = src["kubo_ishigaki_2017_transcribed"]
    bm = src["tendon_failure_and_canonical_benchmarks"]

    tq10_pre, tq10_pre_sd = kb["table1_mvc_10deg_pf_nm"]["iso_pre"]
    tq10_post, tq10_post_sd = kb["table1_mvc_10deg_pf_nm"]["iso_post"]
    csa_pre, csa_pre_sd = kb["table2_tendon_0deg"]["iso_csa_mm2_pre"]
    csa_post, csa_post_sd = kb["table2_tendon_0deg"]["iso_csa_mm2_post"]

    # Digitization verification & +-2 px sensitivity
    dig = kb["digitized_fig5_fig6_mg_force_0deg_n"]
    px_err_n = dig["resolution_n_per_px"] * dig["sensitivity_px"]
    iso_ramp_gain_pct = (dig["iso_ramp_post"]["force_n"] / dig["iso_ramp_pre"]["force_n"] - 1.0) * 100.0
    iso_ramp_gain_lo = ((dig["iso_ramp_post"]["force_n"] - px_err_n) / (dig["iso_ramp_pre"]["force_n"] + px_err_n) - 1.0) * 100.0
    iso_ramp_gain_hi = ((dig["iso_ramp_post"]["force_n"] + px_err_n) / (dig["iso_ramp_pre"]["force_n"] - px_err_n) - 1.0) * 100.0
    iso_bal_gain_pct = (dig["iso_ballistic_post"]["force_n"] / dig["iso_ballistic_pre"]["force_n"] - 1.0) * 100.0

    # Pose-transfer force ratio F_AT(10 deg PF) / F_AT(0 deg)
    tq_r_ym = cf["torque_ratio_10pf_to_0_young_male"]["mean"]
    tq_r_holzer = cf["holzer_2020_prone_extended_14m"]["ratio_10pf_to_0"]
    ma_r_holzer = float(np.mean(holzer_ma10 / holzer_ma0))
    f_ratio_mean_ym = tq_r_ym / ma_r_holzer
    f_ratio_holzer_prone = tq_r_holzer / ma_r_holzer
    f_ratio_envelope = [
        cf["torque_ratio_10pf_to_0_young_male"]["min"] / float(np.max(holzer_ma10 / holzer_ma0)),
        cf["torque_ratio_10pf_to_0_young_male"]["max"] / float(np.min(holzer_ma10 / holzer_ma0)),
    ]

    # Deterministic Monte Carlo (N = 50,000, seed = 1522026)
    rng = np.random.default_rng(1522026)
    N = 50000
    ma10_draw = rng.choice(holzer_ma10, size=N)
    tq10_ind = np.clip(rng.normal(tq10_post, tq10_post_sd, N), 50.0, 250.0)
    csa_ind = np.clip(rng.normal(csa_post, csa_post_sd, N), 30.0, 120.0)
    uts_slow_ind = np.clip(rng.normal(bm["wren_2001_uts_slow_1pct_s_mpa"][0], bm["wren_2001_uts_slow_1pct_s_mpa"][1], N), 20.0, 150.0)
    uts_fast_ind = np.clip(rng.normal(bm["wren_2001_uts_fast_10pct_s_mpa"][0], bm["wren_2001_uts_fast_10pct_s_mpa"][1], N), 20.0, 180.0)
    avul_ind = np.clip(rng.normal(bm["nagelli_2022_avulsion_load_n"][0], bm["nagelli_2022_avulsion_load_n"][1], N), 1000.0, 9000.0)

    gate = bm["exp0062_safety_factor_gate"]
    ramp_mult = bm["exp0062_ramp_enthesis_von_mises_mult"]
    bal_mult = bm["exp0062_ballistic_enthesis_von_mises_mult"]

    scenarios_10pf = {}
    for f_ts_label, f_ts in [("total_torque_fTS_1.000", 1.0), ("pcsa_share_fTS_0.873", bm["fukunaga_1996_triceps_surae_pcsa_share"])]:
        f_cohort = f_ts * tq10_post / (holzer_ma10 / 1000.0)
        sig_cohort_nom = f_cohort / csa_post
        f_ind = f_ts * tq10_ind / (ma10_draw / 1000.0)
        sig_ind_nom = f_ind / csa_ind

        scen_map = {}
        for sname, mult, uts_fixed, uts_arr in [
            ("nominal_vs_wren_71mpa", 1.0, bm["wren_2001_uts_slow_1pct_s_mpa"][0], uts_slow_ind),
            ("ramp_enthesis_vs_wren_71mpa", ramp_mult, bm["wren_2001_uts_slow_1pct_s_mpa"][0], uts_slow_ind),
            ("ramp_enthesis_vs_exp0062_85mpa", ramp_mult, bm["exp0062_collagen_yield_mpa"], np.full(N, bm["exp0062_collagen_yield_mpa"])),
            ("ballistic_enthesis_vs_wren_86mpa", bal_mult, bm["wren_2001_uts_fast_10pct_s_mpa"][0], uts_fast_ind),
        ]:
            sf_c = uts_fixed / (sig_cohort_nom * mult)
            sf_i = uts_arr / (sig_ind_nom * mult)
            scen_map[sname] = {
                "effective_stress_cohort_mpa_range": [round(float(np.min(sig_cohort_nom * mult)), 2), round(float(np.max(sig_cohort_nom * mult)), 2)],
                "effective_stress_cohort_mpa_median": round(float(np.median(sig_cohort_nom * mult)), 2),
                "sf_cohort_mean_range": [round(float(np.min(sf_c)), 3), round(float(np.max(sf_c)), 3)],
                "sf_cohort_mean_median": round(float(np.median(sf_c)), 3),
                "cohort_models_below_1_50_pct": round(float(np.mean(sf_c < gate) * 100.0), 1),
                "sf_individual_mc_median": round(float(np.median(sf_i)), 3),
                "sf_individual_mc_p05_p95": [round(float(np.percentile(sf_i, 5)), 3), round(float(np.percentile(sf_i, 95)), 3)],
                "individual_mc_below_1_50_pct": round(float(np.mean(sf_i < gate) * 100.0), 1),
                "passes_sf_1_50_conservatively": bool(float(np.min(sf_c)) >= gate and float(np.percentile(sf_i, 5)) >= gate),
            }

        # Nagelli 2022 calcaneus avulsion load check (direct force, N)
        sf_avul_c = bm["nagelli_2022_avulsion_load_n"][0] / f_cohort
        sf_avul_i = avul_ind / f_ind
        scen_map["force_vs_nagelli_2022_avulsion_4217n"] = {
            "force_cohort_n_range": [round(float(np.min(f_cohort)), 1), round(float(np.max(f_cohort)), 1)],
            "force_cohort_n_median": round(float(np.median(f_cohort)), 1),
            "sf_cohort_mean_range": [round(float(np.min(sf_avul_c)), 3), round(float(np.max(sf_avul_c)), 3)],
            "sf_cohort_mean_median": round(float(np.median(sf_avul_c)), 3),
            "cohort_models_below_1_50_pct": round(float(np.mean(sf_avul_c < gate) * 100.0), 1),
            "sf_individual_mc_median": round(float(np.median(sf_avul_i)), 3),
            "sf_individual_mc_p05_p95": [round(float(np.percentile(sf_avul_i, 5)), 3), round(float(np.percentile(sf_avul_i, 95)), 3)],
            "individual_mc_below_1_50_pct": round(float(np.mean(sf_avul_i < gate) * 100.0), 1),
            "passes_sf_1_50_conservatively": bool(float(np.min(sf_avul_c)) >= gate and float(np.percentile(sf_avul_i, 5)) >= gate),
        }
        scenarios_10pf[f_ts_label] = scen_map

    # Reconstructed 0 deg neutral (ISO training & tendon test pose) using YM mean torque ratio & Holzer prone ratio
    pose_0deg = {}
    for label, tq_r in [("chen_franklin_ym_mean_0.7915", tq_r_ym), ("holzer_prone_14m_0.7480", tq_r_holzer)]:
        tq0_post = tq10_post / tq_r
        f0 = tq0_post / (holzer_ma0 / 1000.0)
        sig0_ent = (f0 / csa_post) * ramp_mult
        sf0_71 = bm["wren_2001_uts_slow_1pct_s_mpa"][0] / sig0_ent
        sf0_85 = bm["exp0062_collagen_yield_mpa"] / sig0_ent
        pose_0deg[label] = {
            "reconstructed_tq_post_0deg_nm": round(float(tq0_post), 2),
            "force_cohort_n_range": [round(float(np.min(f0)), 1), round(float(np.max(f0)), 1)],
            "enthesis_stress_mpa_range": [round(float(np.min(sig0_ent)), 2), round(float(np.max(sig0_ent)), 2)],
            "sf_enthesis_vs_wren_71mpa_range": [round(float(np.min(sf0_71)), 3), round(float(np.max(sf0_71)), 3)],
            "sf_enthesis_vs_exp0062_85mpa_range": [round(float(np.min(sf0_85)), 3), round(float(np.max(sf0_85)), 3)],
            "cohort_models_below_1_50_vs_71mpa_pct": round(float(np.mean(sf0_71 < gate) * 100.0), 1),
        }

    # EXP-0060 cyclic iso-durability invariant: (1+dCSA)*(1+dUTS) >= F1/F0
    csa_ratio = csa_post / csa_pre
    iso_durability = {}
    for nm, f_ratio in [
        ("10deg_pf_table_ratio", tq10_post / tq10_pre),
        ("10deg_pf_indiv_mean_gain", 1.0 + kb["table1_mvc_10deg_pf_nm"]["iso_indiv_gain_pct"][0] / 100.0),
        ("0deg_fig5b_ramp_force", dig["iso_ramp_post"]["force_n"] / dig["iso_ramp_pre"]["force_n"]),
        ("0deg_iso_training_mvc_gain", 1.0 + kb["iso_0deg_training_mvc_gain_pct"][0] / 100.0),
    ]:
        s_ratio = f_ratio / csa_ratio
        req_duts_pct = (s_ratio - 1.0) * 100.0
        ret_845 = s_ratio ** (-bm["exp0060_wohler_b_nominal"])
        ret_1327 = s_ratio ** (-bm["exp0060_wohler_b_fitted"])
        iso_durability[nm] = {
            "force_ratio": round(float(f_ratio), 4),
            "csa_ratio": round(float(csa_ratio), 4),
            "stress_ratio_if_dUTS_0": round(float(s_ratio), 4),
            "required_unmeasured_dUTS_pct": round(float(req_duts_pct), 2),
            "wohler_b8_45_life_change_pct_if_dUTS_0": round(float((ret_845 - 1.0) * 100.0), 1),
            "wohler_b13_27_life_change_pct_if_dUTS_0": round(float((ret_1327 - 1.0) * 100.0), 1),
        }

    return {
        "fig5_fig6_digitization_check": {
            "px_sensitivity_n": round(px_err_n, 2),
            "iso_ramp_force_gain_pct": round(iso_ramp_gain_pct, 2),
            "iso_ramp_force_gain_2px_bounds_pct": [round(iso_ramp_gain_lo, 2), round(iso_ramp_gain_hi, 2)],
            "iso_ballistic_force_gain_pct": round(iso_bal_gain_pct, 2),
            "max_abs_lmax_discrepancy_vs_table2_mm": round(max(
                abs(dig[k]["lmax_mm_fig"] - dig[k]["lmax_mm_table2"])
                for k in ("iso_ramp_pre", "iso_ramp_post", "iso_ballistic_pre", "iso_ballistic_post",
                          "ply_ramp_pre", "ply_ramp_post", "ply_ballistic_pre", "ply_ballistic_post")
            ), 3),
        },
        "pose_transfer_force_ratio_10pf_to_0": {
            "young_male_mean_ratio": round(f_ratio_mean_ym, 4),
            "holzer_prone_14m_ratio": round(f_ratio_holzer_prone, 4),
            "empirical_envelope_10pf_to_0": [round(f_ratio_envelope[0], 4), round(f_ratio_envelope[1], 4)],
            "implied_0deg_overload_vs_10pf_pct_range": [
                round((1.0 / f_ratio_envelope[1] - 1.0) * 100.0, 1),
                round((1.0 / f_ratio_envelope[0] - 1.0) * 100.0, 1),
            ],
            "direction_verified": "10 deg PF yields lower total AT force than 0 deg neutral across all paired human torque-angle and MA curves, but absolute SF at 10 deg PF still crosses below 1.50.",
        },
        "target_pose_10deg_pf_safety_margin": scenarios_10pf,
        "training_pose_0deg_reconstructed_safety_margin": pose_0deg,
        "exp0060_cyclic_iso_durability": iso_durability,
        "chen_franklin_35_ma_cross_check_10pf": {
            "f_ts_1_00_nominal_sf_71mpa_range": [
                round(71.0 / (tq10_post / (max(cf["ma_10deg_pf_values_mm"]) / 1000.0) / csa_post), 3),
                round(71.0 / (tq10_post / (min(cf["ma_10deg_pf_values_mm"]) / 1000.0) / csa_post), 3),
            ][::-1],
            "f_ts_1_00_enthesis_sf_71mpa_range": [
                round(71.0 / (tq10_post / (min(cf["ma_10deg_pf_values_mm"]) / 1000.0) / csa_post * ramp_mult), 3),
                round(71.0 / (tq10_post / (max(cf["ma_10deg_pf_values_mm"]) / 1000.0) / csa_post * ramp_mult), 3),
            ],
        },
    }


def compute_jacobs_same_pose_rct(src: dict) -> dict:
    jb = src["jacobs_2025_same_pose_rct"]
    n_i, n_c, weeks = jb["n_intervention"], jb["n_control"], jb["weeks"]
    t1 = jb["table1"]

    def arm_pct_change(pre_m, pre_sd, post_m, post_sd, n, r_assumed=0.5):
        # Conservative delta-method SE for percentage change from pre/post summary stats
        diff = post_m - pre_m
        sd_diff = math.sqrt(pre_sd**2 + post_sd**2 - 2.0 * r_assumed * pre_sd * post_sd)
        se_pct = (sd_diff / math.sqrt(n)) / pre_m * 100.0
        return diff / pre_m * 100.0, se_pct

    out = {}
    t_crit = float(stats.t.ppf(0.975, df=n_i + n_c - 2))
    for key in ("pf_mvc_nm", "ke_mvc_nm", "squat_1rm_kg", "pmax_w", "at_stiffness_n_mm", "pt_stiffness_n_mm"):
        d = t1[key]
        i_pct, i_se_r05 = arm_pct_change(*d["int_pre"], *d["int_post"], n_i, 0.5)
        c_pct, c_se_r05 = arm_pct_change(*d["con_pre"], *d["con_post"], n_c, 0.5)
        _, i_se_r09 = arm_pct_change(*d["int_pre"], *d["int_post"], n_i, 0.9)
        _, c_se_r09 = arm_pct_change(*d["con_pre"], *d["con_post"], n_c, 0.9)
        adj = i_pct - c_pct
        se_adj_r05 = math.sqrt(i_se_r05**2 + c_se_r05**2)
        se_adj_r09 = math.sqrt(i_se_r09**2 + c_se_r09**2)
        out[key] = {
            "intervention_ratio_gain_pct": round(i_pct, 2),
            "control_ratio_gain_pct": round(c_pct, 2),
            "control_adjusted_pp": round(adj, 2),
            "conditional_ci95_r05_pp": [round(adj - t_crit * se_adj_r05, 2), round(adj + t_crit * se_adj_r05, 2)],
            "conditional_ci95_r09_pp": [round(adj - t_crit * se_adj_r09, 2), round(adj + t_crit * se_adj_r09, 2)],
        }

    # For squat 1RM, text also reports individual mean +- SD (+20.0 +- 9.7%)
    sq_mean, sq_sd = t1["squat_1rm_kg"]["int_text_gain_pct"]
    sq_se = sq_sd / math.sqrt(n_i)
    sq_t = float(stats.t.ppf(0.975, df=n_i - 1))
    out["squat_1rm_kg"]["intervention_text_indiv_ci95_pct"] = [round(sq_mean - sq_t * sq_se, 2), round(sq_mean + sq_t * sq_se, 2)]

    return {
        "design": "12-week RCT in well-trained triathletes (n=9 ST+Endurance vs n=9 Endurance control); same-pose isometric PF (0 deg) + AT stiffness and isometric KE (60 deg) + PT stiffness",
        "measured_ankle_rotation_during_0deg_mvc_deg": "13 +- 5",
        "outcomes": out,
        "passes_force20": False,
        "passes_adapt25": False,
        "blockers": [
            "Same-pose isometric PF (+7.41 pp adjusted, NS) and KE (+10.36 pp adjusted) are far below FORCE20 +20 pp.",
            "Control arm is endurance-only (KE -1.51%, squat -1.55%, PF +1.42% NS), failing the positive active strength comparator requirement of ADAPT25.",
            f"Dynamic 1RM squat (+20.0 +- 9.7% text, unadjusted 95% CI {out['squat_1rm_kg']['intervention_text_indiv_ci95_pct']}%; adjusted +{out['squat_1rm_kg']['control_adjusted_pp']} pp, conditional 95% CI r=0.5 {out['squat_1rm_kg']['conditional_ci95_r05_pp']} / r=0.9 {out['squat_1rm_kg']['conditional_ci95_r09_pp']} pp) fails lower 95% CI >= +20 pp, differs in pose from isometric tendon tests, and lacks tendon CSA, loaded strain at 1RM, post body mass, and individual data."
        ],
    }


def run_experiment(data_root: Path) -> dict:
    src = json.loads(SOURCES_PATH.read_text("utf-8"))
    verified = verify_sources(data_root, src)
    subdir = data_root / src["data_subdir"]

    cf = extract_chen_franklin(subdir / "PMC12283864_10439_2025_3735_MOESM1_ESM.zip")
    wolfram = extract_wolfram_mri(subdir / "z4939556_AT_moment_arms.xlsx")
    holzer_summary, holzer_ma0, holzer_ma10 = compute_holzer_ma(src)
    safety = compute_tendon_safety(src, holzer_ma0, holzer_ma10, cf)
    jacobs = compute_jacobs_same_pose_rct(src)

    # Check if ANY scenario at 10 deg PF passes SF >= 1.50 conservatively
    any_pass_10pf = any(
        s["passes_sf_1_50_conservatively"]
        for grp in safety["target_pose_10deg_pf_safety_margin"].values()
        for s in grp.values()
    )

    return {
        "experiment_id": "EXP-0152",
        "stage1_verdict": "HOLD",
        "kubo_ishigaki_adapt25_strength_preserved_from_exp0147": {
            "control_rate_pp_per_wk": [0.37, 0.09, 0.65],
            "adapt25_contrast_r_neg1_pp_per_wk": [1.38, 0.24, 2.53],
            "status": "STRENGTH_COMPONENT_PASS_TISSUE_HOLD",
        },
        "verified_source_files": verified,
        "task1_kubo_ishigaki_pose_audit": {
            "joint": "Ankle plantar flexors (MG, LG, SOL)",
            "zero_and_sign": src["kubo_ishigaki_2017_transcribed"]["angle_convention"],
            "other_joints_posture": src["kubo_ishigaki_2017_transcribed"]["posture_all_tests"],
            "participants_and_mass": src["kubo_ishigaki_2017_transcribed"]["sex_age_height_mass"],
            "pose_10deg_pf_measurements": ["Isometric MVC torque (Table 1)", "Active muscle stiffness via 10 deg -> -10 deg fast stretch at 30/50/70% pre-MVC", "ZERO tendon measurements"],
            "pose_0deg_neutral_measurements": ["Ramp 5-s MVC compound tendon+aponeurosis elongation, stiffness (>50% MVC), hysteresis", "Ballistic MVC compound tendon+aponeurosis elongation, stiffness, hysteresis", "Resting Achilles tendon CSA at lateral malleolus (64.9 -> 66.0 +- 7.8 mm^2, +1.7% NS)", "ISO training (0 deg neutral, load adjusted every 4 wk, +27.6 +- 4.0% at wk 12)"],
            "compatibility_gaps": [
                "Compound outer tendon + MG deep aponeurosis elongation reported without resting length L_0 or isolated free Achilles tendon strain.",
                "Achilles moment arm MA(0 deg) estimated from lower-leg length (Grieve 1978), not individually measured (Clarke 2015 / Sheehan 2012 show poor anthropometric scaling).",
                "No tendon measurements at intermediate weeks 4 or 8 despite 4-weekly ISO MVC escalation to +27.6%.",
                "Unmatched mechanical exposure and load-adjustment outcome between ISO (0 deg MVC) and PLY (sledge 1RM +37.7%).",
                "Individual participant tables are not published (confirmed via PMC5555899.1 S3 inventory)."
            ],
        },
        "task2_open_pose_transfer_data": {
            "chen_franklin_2025_pmc12283864": {k: v for k, v in cf.items() if k != "ma_10deg_pf_values_mm"},
            "holzer_2020_pmc7658232": holzer_summary,
            "wolfram_2018_zenodo4939556": wolfram,
            "nagelli_2022_pmc9286485_in_vitro_failure": {
                "calcaneus_avulsion_load_n": src["tendon_failure_and_canonical_benchmarks"]["nagelli_2022_avulsion_load_n"],
                "midsubstance_rupture_load_n": src["tendon_failure_and_canonical_benchmarks"]["nagelli_2022_midsubstance_load_n"],
                "longitudinal_rupture_strain_pct": src["tendon_failure_and_canonical_benchmarks"]["nagelli_2022_longitudinal_rupture_strain_pct"],
            },
            "yin_2021_pmc7886322_subtendon_uts_mpa": src["tendon_failure_and_canonical_benchmarks"]["yin_2021_subtendon_uts_mpa"],
        },
        "task3_safety_margin_and_decision": {
            "any_10deg_pf_scenario_passes_sf_1_50_conservatively": any_pass_10pf,
            **safety,
            "same_pose_open_rct_jacobs_2025": jacobs,
            "decisive_missing_measurement": (
                "Participant-linked longitudinal measurements in the SAME ankle pose (+10 deg PF, plus 0 deg training pose) "
                "at weeks 0, 4, 8, and 12 combining: (1) individual MRI/3D-US Achilles tendon moment arm MA(theta) under MVC with motion-captured ankle rotation/heel lift, "
                "(2) isolated free Achilles tendon resting length L_0, longitudinal/regional strain at maximal voluntary load, and regional CSA along the free tendon/enthesis, "
                "and (3) exposure-matched active control with participant-linked strength and tendon trajectories."
            ),
        },
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
        existing = RESULTS_PATH.read_text("utf-8")
        if existing != payload:
            raise SystemExit("EXP-0152 replay mismatch against RESULTS.json")
        print("EXP-0152 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(f"Wrote {RESULTS_PATH} ({len(payload)} bytes); stage1_verdict={res['stage1_verdict']}")


if __name__ == "__main__":
    main()
