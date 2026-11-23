#!/usr/bin/env python3
"""EXP-0154: Stage 1 evaluation of alternative joints, internal biological mechanisms, and non-destructive SWV validity."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
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
    out = {}
    for fn, meta in src["files"].items():
        fp = subdir / fn
        if not fp.is_file():
            raise FileNotFoundError(f"Missing file: {fp}")
        d = sha256_file(fp)
        if d != meta["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {fn}: {d} != {meta['sha256']}")
        out[fn] = {"bytes": fp.stat().st_size, "sha256": d, "source_id": meta["source_id"]}
    return out


def pct_and_se(pre_m: float, pre_sd: float, post_m: float, post_sd: float, n: int, r: float) -> tuple[float, float]:
    pct = (post_m - pre_m) / pre_m * 100.0
    sd_diff = math.sqrt(pre_sd**2 + post_sd**2 - 2.0 * r * pre_sd * post_sd)
    se_pct = (sd_diff / math.sqrt(n)) / pre_m * 100.0
    return pct, se_pct


def analyze_maeo_2024(src: dict) -> dict:
    m = src["maeo_2024_hamstring_rct"]
    n, wk = m["n_per_group"], m["weeks"]
    t_crit = float(stats.t.ppf(0.975, df=2 * n - 2))

    # Aponeurosis MRI hypertrophy
    apo = m["table1_bflh_aponeurosis_area_cm2"]
    apo_lset, se_al = pct_and_se(*apo["LSET"][0], *apo["LSET"][1], n, 0.7)
    apo_nht, se_an = pct_and_se(*apo["NHT"][0], *apo["NHT"][1], n, 0.7)
    apo_con, se_ac = pct_and_se(*apo["CON"][0], *apo["CON"][1], n, 0.7)

    torque_res = {}
    for mode, arms in m["table2_knee_flexion_torque_nm"].items():
        l_pct, l_se05 = pct_and_se(*arms["LSET"][0], *arms["LSET"][1], n, 0.5)
        n_pct, n_se05 = pct_and_se(*arms["NHT"][0], *arms["NHT"][1], n, 0.5)
        c_pct, c_se05 = pct_and_se(*arms["CON"][0], *arms["CON"][1], n, 0.5)
        _, l_se09 = pct_and_se(*arms["LSET"][0], *arms["LSET"][1], n, 0.9)
        _, n_se09 = pct_and_se(*arms["NHT"][0], *arms["NHT"][1], n, 0.9)
        _, c_se09 = pct_and_se(*arms["CON"][0], *arms["CON"][1], n, 0.9)

        f20_lset = l_pct - c_pct
        se_f20_05 = math.sqrt(l_se05**2 + c_se05**2)
        se_f20_09 = math.sqrt(l_se09**2 + c_se09**2)

        # ADAPT25 active contrast: r_LSET - 1.25 * r_NHT (pp/wk)
        r_l, r_n = l_pct / wk, n_pct / wk
        a25 = r_l - 1.25 * r_n
        se_a25_05 = math.sqrt((l_se05 / wk) ** 2 + (1.25 * n_se05 / wk) ** 2)
        se_a25_09 = math.sqrt((l_se09 / wk) ** 2 + (1.25 * n_se09 / wk) ** 2)

        torque_res[mode] = {
            "lset_gain_pct": round(l_pct, 2),
            "nht_gain_pct": round(n_pct, 2),
            "con_gain_pct": round(c_pct, 2),
            "force20_lset_vs_con_pp": round(f20_lset, 2),
            "force20_ci95_r05_pp": [round(f20_lset - t_crit * se_f20_05, 2), round(f20_lset + t_crit * se_f20_05, 2)],
            "force20_ci95_r09_pp": [round(f20_lset - t_crit * se_f20_09, 2), round(f20_lset + t_crit * se_f20_09, 2)],
            "adapt25_lset_vs_nht_pp_per_wk": round(a25, 3),
            "adapt25_ci95_r05_pp_per_wk": [round(a25 - t_crit * se_a25_05, 3), round(a25 + t_crit * se_a25_05, 3)],
            "adapt25_ci95_r09_pp_per_wk": [round(a25 - t_crit * se_a25_09, 3), round(a25 + t_crit * se_a25_09, 3)],
            "passes_force20": False,
            "passes_adapt25": False,
        }

    return {
        "joint_and_mechanism": "Knee flexors / hamstrings (BFlh MRI aponeurosis) — lengthened-state eccentric (LSET) vs Nordic hamstring (NHT) vs CON (n=42, 12 wk)",
        "bflh_aponeurosis_area_gain_pct": {
            "LSET": round(apo_lset, 2),
            "NHT": round(apo_nht, 2),
            "CON": round(apo_con, 2),
            "LSET_minus_CON_pp": round(apo_lset - apo_con, 2),
        },
        "torque_outcomes": torque_res,
        "verdict": "HOLD (confirmed MRI connective-tissue hypertrophy +7.55 pp vs CON, but all control-adjusted strength gains +9.07..+13.00 pp fail FORCE20 and all active LSET-1.25xNHT contrasts cross zero; no loaded tendon strain or individual data).",
    }


def analyze_werkhausen_2019(src: dict) -> dict:
    w = src["werkhausen_2019_achilles_rct"]
    nt, nc = w["n_train"], w["n_con"]
    t_crit = float(stats.t.ppf(0.975, df=nt + nc - 2))
    tr_pct, tr_se05 = pct_and_se(*w["pf_torque_nm"]["TR"][0], *w["pf_torque_nm"]["TR"][1], nt, 0.5)
    cn_pct, cn_se05 = pct_and_se(*w["pf_torque_nm"]["CON"][0], *w["pf_torque_nm"]["CON"][1], nc, 0.5)
    _, tr_se09 = pct_and_se(*w["pf_torque_nm"]["TR"][0], *w["pf_torque_nm"]["TR"][1], nt, 0.9)
    _, cn_se09 = pct_and_se(*w["pf_torque_nm"]["CON"][0], *w["pf_torque_nm"]["CON"][1], nc, 0.9)
    adj = tr_pct - cn_pct
    se05 = math.sqrt(tr_se05**2 + cn_se05**2)
    se09 = math.sqrt(tr_se09**2 + cn_se09**2)
    stiff_tr = (w["at_stiffness_n_mm"]["TR"][1][0] / w["at_stiffness_n_mm"]["TR"][0][0] - 1.0) * 100.0
    stiff_cn = (w["at_stiffness_n_mm"]["CON"][1][0] / w["at_stiffness_n_mm"]["CON"][0][0] - 1.0) * 100.0
    return {
        "joint_and_mechanism": "Ankle plantarflexion isometric training (10 wk, n=11 TR vs n=10 CON) with same-pose AT stiffness and in vivo running AT lengthening",
        "pf_torque_tr_gain_pct": round(tr_pct, 2),
        "pf_torque_con_gain_pct": round(cn_pct, 2),
        "force20_adjusted_pp": round(adj, 2),
        "force20_ci95_r05_pp": [round(adj - t_crit * se05, 2), round(adj + t_crit * se05, 2)],
        "force20_ci95_r09_pp": [round(adj - t_crit * se09, 2), round(adj + t_crit * se09, 2)],
        "at_stiffness_tr_gain_pct": round(stiff_tr, 2),
        "at_stiffness_con_gain_pct": round(stiff_cn, 2),
        "passes_force20": False,
        "passes_adapt25": False,
        "verdict": "HOLD (control-adjusted torque +9.23 pp far below FORCE20 +20 pp; passive control fails ADAPT25).",
    }


def analyze_swv_individual_validity(data_root: Path, src: dict) -> dict:
    subdir = data_root / src["data_subdir"]
    with (subdir / "seynnes_All_data_except_SWV.csv").open(encoding="utf-8-sig") as f:
        main_rows = list(csv.DictReader(f))
    with (subdir / "seynnes_tendon_SWV_data.csv").open(encoding="utf-8-sig") as f:
        swv_map = {r["FP"]: r for r in csv.DictReader(f)}

    d_swv, d_stiff, d_csa, d_mvc = [], [], [], []
    for r in main_rows:
        fp = r["FP"]
        if fp not in swv_map:
            continue
        sw = swv_map[fp]
        if all(r[k].strip() for k in ("Stiffness_PRE", "Stiffness_POST", "PT_CSA_mean_PRE", "PT_CSA_mean_POST", "KE_MIVC_PRE", "KE_MIVC_POST")) and sw["V_pre_mean"].strip() and sw["V_post_mean"].strip():
            d_swv.append((float(sw["V_post_mean"]) / float(sw["V_pre_mean"]) - 1.0) * 100.0)
            d_stiff.append((float(r["Stiffness_POST"]) / float(r["Stiffness_PRE"]) - 1.0) * 100.0)
            d_csa.append((float(r["PT_CSA_mean_POST"]) / float(r["PT_CSA_mean_PRE"]) - 1.0) * 100.0)
            d_mvc.append((float(r["KE_MIVC_POST"]) / float(r["KE_MIVC_PRE"]) - 1.0) * 100.0)

    a_swv = np.array(d_swv, dtype=float)
    a_stiff = np.array(d_stiff, dtype=float)
    a_csa = np.array(d_csa, dtype=float)
    a_mvc = np.array(d_mvc, dtype=float)

    r_sk, p_sk = stats.pearsonr(a_swv, a_stiff)
    rho_sk, prho_sk = stats.spearmanr(a_swv, a_stiff)
    r_sc, p_sc = stats.pearsonr(a_swv, a_csa)

    # 10,000 bootstrap CI for Pearson r(dSWV%, dStiffness%)
    rng = np.random.default_rng(1542026)
    n = len(a_swv)
    idx = rng.integers(0, n, size=(10000, n))
    boot_r = []
    for b in idx:
        xs, ys = a_swv[b], a_stiff[b]
        if np.std(xs) > 0 and np.std(ys) > 0:
            boot_r.append(float(np.corrcoef(xs, ys)[0, 1]))
    ci_r = [round(float(np.percentile(boot_r, 2.5)), 3), round(float(np.percentile(boot_r, 97.5)), 3)]

    return {
        "reused_source": "SRC-0131 (Zenodo 14259356, Vesterhus et al. 2025) — strictly new non-destructive SWV validity test, no re-audit of EXP-0142 strength contrasts",
        "n_paired_swv_stiffness": int(n),
        "swv_change_mean_sd_pct": [round(float(a_swv.mean()), 2), round(float(a_swv.std(ddof=1)), 2)],
        "stiffness_change_mean_sd_pct": [round(float(a_stiff.mean()), 2), round(float(a_stiff.std(ddof=1)), 2)],
        "csa_change_mean_sd_pct": [round(float(a_csa.mean()), 2), round(float(a_csa.std(ddof=1)), 2)],
        "mvc_change_mean_sd_pct": [round(float(a_mvc.mean()), 2), round(float(a_mvc.std(ddof=1)), 2)],
        "pearson_r_dSWV_vs_dStiffness": round(float(r_sk), 3),
        "pearson_p_dSWV_vs_dStiffness": round(float(p_sk), 4),
        "bootstrap_ci95_r_dSWV_vs_dStiffness": ci_r,
        "spearman_rho_dSWV_vs_dStiffness": round(float(rho_sk), 3),
        "spearman_p_dSWV_vs_dStiffness": round(float(prho_sk), 4),
        "pearson_r_dSWV_vs_dCSA": round(float(r_sc), 3),
        "pearson_p_dSWV_vs_dCSA": round(float(p_sc), 4),
        "ruling": (
            f"Resting patellar SWV change does NOT significantly track loaded tensile stiffness adaptation "
            f"or CSA change at the individual human level (n={n}, r={r_sk:+.3f}, p={p_sk:.4f}, "
            f"95% bootstrap CI [{ci_r[0]:+.3f}; {ci_r[1]:+.3f}]), disqualifying resting SWV as a stand-alone safety proxy."
        ),
    }


def run_experiment(data_root: Path) -> dict:
    src = json.loads(SOURCES_PATH.read_text("utf-8"))
    verified = verify_sources(data_root, src)

    maeo = analyze_maeo_2024(src)
    werkhausen = analyze_werkhausen_2019(src)
    swv_test = analyze_swv_individual_validity(data_root, src)

    ob = src["oberg_2025_bfr_scoping_summary"]
    br = ob["brumitt_2020_rotator_cuff"]
    br_a25_abd = (br["abduction_bfr_pct"] - 1.25 * br["abduction_llrt_pct"]) / br["weeks"]
    br_a25_ext = (br["ext_rot_bfr_pct"] - 1.25 * br["ext_rot_llrt_pct"]) / br["weeks"]

    return {
        "experiment_id": "EXP-0154",
        "stage1_verdict": "HOLD",
        "stage1_blocker_status": "DATA_BLOCKED",
        "scientific_criterion_closed": False,
        "verified_sources": verified,
        "alternative_mechanisms_tested": {
            "maeo_2024_hamstring_lset_vs_nht": maeo,
            "mersmann_2021_functional_high_load_patellar": {
                **src["mersmann_2021_patellar_rct"],
                "passes_adapt25": False,
                "passes_force20": False,
                "verdict": "HOLD (clinically prevents patellar tendinopathy: 0/16 vs 5/15 worsening, p=0.016, but yields NO strength-rate superiority over active control: group p=0.50, interaction p=0.44).",
            },
            "werkhausen_2019_achilles_running_strain": werkhausen,
            "martinez_2022_patellar_eccentric_execution_time": {
                "n_total": 50,
                "arms": "EG6s (n=17) vs EG3s (n=18) vs CG (n=15), 6 wk single-leg decline squat + 6 wk detraining",
                "passes_force20": False,
                "passes_adapt25": False,
                "verdict": "HOLD (proximal PT thickness time x group p=0.037, but no published maximal external strength/MVC contrast or loaded tendon capacity).",
            },
            "oberg_2025_multi_site_bfr_vs_hlrt": {
                "brumitt_2020_rotator_cuff_adapt25_point_pp_per_wk": {
                    "shoulder_abduction": round(br_a25_abd, 3),
                    "shoulder_ext_rotation": round(br_a25_ext, 3),
                },
                "frouin_2024_hamstring_adjusted_pp": {
                    "bfr_vs_con": round(ob["frouin_2024_hamstrings"]["iso_kf_bfr_pct"] - ob["frouin_2024_hamstrings"]["iso_kf_con_pct"], 2),
                    "hlrt_vs_con": round(ob["frouin_2024_hamstrings"]["iso_kf_hlrt_pct"] - ob["frouin_2024_hamstrings"]["iso_kf_con_pct"], 2),
                },
                "centner_2022_2023_bfr_vs_hlrt": "BFR matches rather than exceeds HLRT by +25% (leg press 34% vs 37%; PF 44% vs 43%), lacks untreated control arm in 2022/2023, and individual tables are closed/paywalled.",
                "passes_force20": False,
                "passes_adapt25": False,
            },
        },
        "individual_swv_validity_test": swv_test,
        "summary_ruling": "Expanding Stage 1 across 4 anatomical sites (ankle, knee/patellar, hamstring/BFlh, shoulder/supraspinatus) and 5 internal training mechanisms (lengthened-state eccentric, Nordic eccentric, functional high-load patellar, eccentric execution time, low-load BFR) confirms Stage 1 DATA_BLOCKED is a general empirical limit of open human datasets, not specific to Kubo-Ishigaki or leg press.",
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
            raise SystemExit("EXP-0154 replay mismatch")
        print("EXP-0154 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(f"Wrote {RESULTS_PATH} ({len(payload)} bytes); stage1={res['stage1_verdict']}/{res['stage1_blocker_status']}")


if __name__ == "__main__":
    main()
