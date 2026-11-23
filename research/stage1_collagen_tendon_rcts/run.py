#!/usr/bin/env python3
"""EXP-0156: Stage 1 new internal biological mechanism — Hydrolysed/Bioactive Collagen Peptides + RT
on patellar tendon (Balshaw 2025, Lee 2025, Lee 2023) and high-loading strain-targeted Achilles RT
(Radovanovic 2022). Tests ADAPT25/FORCE20 simultaneously with tendon matrix remodeling and strain safety.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
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


def adapt25_from_pct_means_sds(m_i: float, sd_i: float, n_i: int, m_c: float, sd_c: float, n_c: int, weeks: float) -> dict:
    r_i = m_i / weeks
    r_c = m_c / weeks
    se_i = (sd_i / math.sqrt(n_i)) / weeks
    se_c = (sd_c / math.sqrt(n_c)) / weeks
    diff = r_i - 1.25 * r_c
    se = math.sqrt(se_i ** 2 + (1.25 * se_c) ** 2)
    df = n_i + n_c - 2
    tcrit = float(stats.t.ppf(0.975, df))
    ci = [round(diff - tcrit * se, 3), round(diff + tcrit * se, 3)]
    return {
        "rate_I_pp_per_wk": round(r_i, 3),
        "rate_C_pp_per_wk": round(r_c, 3),
        "adapt25_contrast_pp_per_wk": round(diff, 3),
        "ci95_pp_per_wk": ci,
        "passes_adapt25": bool(r_c > 0 and ci[0] > 0),
    }


def adapt25_from_pre_post(
    pre_i: tuple[float, float], post_i: tuple[float, float], n_i: int,
    pre_c: tuple[float, float], post_c: tuple[float, float], n_c: int,
    weeks: float, r_corr: float,
) -> dict:
    pct_i = 100.0 * (post_i[0] - pre_i[0]) / pre_i[0]
    pct_c = 100.0 * (post_c[0] - pre_c[0]) / pre_c[0]
    sd_di = math.sqrt(pre_i[1] ** 2 + post_i[1] ** 2 - 2.0 * r_corr * pre_i[1] * post_i[1])
    sd_dc = math.sqrt(pre_c[1] ** 2 + post_c[1] ** 2 - 2.0 * r_corr * pre_c[1] * post_c[1])
    sd_pct_i = 100.0 * sd_di / pre_i[0]
    sd_pct_c = 100.0 * sd_dc / pre_c[0]
    res = adapt25_from_pct_means_sds(pct_i, sd_pct_i, n_i, pct_c, sd_pct_c, n_c, weeks)
    res["gain_I_pct"] = round(pct_i, 2)
    res["gain_C_pct"] = round(pct_c, 2)
    return res


def analyze_balshaw_2025(cfg: dict) -> dict:
    n_cp, n_pla, wk = cfg["n_cp"], cfg["n_pla"], cfg["weeks"]
    ke = adapt25_from_pct_means_sds(*cfg["ke_mvt_pct_mean_sd"]["CP"], n_cp, *cfg["ke_mvt_pct_mean_sd"]["PLA"], n_pla, wk)
    kf = adapt25_from_pct_means_sds(*cfg["kf_mvt_pct_mean_sd"]["CP"], n_cp, *cfg["kf_mvt_pct_mean_sd"]["PLA"], n_pla, wk)

    # Mass change check
    bm_cp = 100.0 * (cfg["body_mass_kg_pre_post"]["CP"][1][0] - cfg["body_mass_kg_pre_post"]["CP"][0][0]) / cfg["body_mass_kg_pre_post"]["CP"][0][0]
    bm_pla = 100.0 * (cfg["body_mass_kg_pre_post"]["PLA"][1][0] - cfg["body_mass_kg_pre_post"]["PLA"][0][0]) / cfg["body_mass_kg_pre_post"]["PLA"][0][0]

    # Linear-secant projection of patellar tendon strain from 80% Pre-MVT (7.5%) to 100% Post-MVT (+21.4%)
    post_strain_80pre = cfg["pt_strain_80pct_pre_mvt_pct"]["CP"][1][0]
    projected_strain_100post_linear = post_strain_80pre * ((1.0 + cfg["ke_mvt_pct_mean_sd"]["CP"][0] / 100.0) / 0.80)

    return {
        "source_id": "SRC-0198",
        "cohort": "Balshaw et al. 2025 (n=39 completers: 19 CP vs 20 PLA, 15 wk lower-body RT, 3T MRI)",
        "ke_mvt_adapt25": {**ke, "published_gxt_p_range": cfg["ke_mvt_pct_mean_sd"]["gxt_p_range"]},
        "kf_mvt_adapt25": {**kf, "published_gxt_p_range": cfg["kf_mvt_pct_mean_sd"]["gxt_p_range"]},
        "body_mass_gain_pct": {"CP": round(bm_cp, 2), "PLA": round(bm_pla, 2), "note": "Both groups gained body mass significantly (CP p<0.001, PLA p=0.016); no untreated control arm exists for FORCE20."},
        "tendon_outcomes": {
            "pt_mean_csa_pct": cfg["pt_mean_csa_pct"],
            "vl_aponeurosis_area_pct": cfg["vl_aponeurosis_area_pct"],
            "pt_stiffness_pct": cfg["pt_stiffness_pct"],
            "pt_strain_at_80pct_pre_mvt": cfg["pt_strain_80pct_pre_mvt_pct"],
            "linear_extrapolated_strain_at_100pct_post_mvt_pct": round(projected_strain_100post_linear, 2),
            "strain_limitation": "Strain measured only at fixed 80% pre-RT MVT (8.5->7.5%), NOT at the new post-RT 100% MVT (+21.4%); linear scaling yields ~11.4% (>9.0% patellar threshold).",
        },
        "passes_adapt25": False,
        "passes_force20": False,
        "verdict": (
            f"HOLD (strictly negative ADAPT25 point estimate on KE MVT {ke['adapt25_contrast_pp_per_wk']:+.3f} pp/wk "
            f"[{ke['ci95_pp_per_wk'][0]:+.3f}; {ke['ci95_pp_per_wk'][1]:+.3f}], GxT p>=0.596; no CP advantage on 3T MRI PT CSA, "
            f"stiffness, or strain; no untreated control arm and +{bm_cp:.1f}% mass gain disqualify FORCE20)."
        ),
    }


def analyze_lee_2025(cfg: dict) -> dict:
    n_c, n_p, wk = cfg["n_col"], cfg["n_pla"], cfg["weeks"]
    ke_r05 = adapt25_from_pre_post(tuple(cfg["ke_mvt_nm"]["COL"][0]), tuple(cfg["ke_mvt_nm"]["COL"][1]), n_c,
                                   tuple(cfg["ke_mvt_nm"]["PLA"][0]), tuple(cfg["ke_mvt_nm"]["PLA"][1]), n_p, wk, 0.5)
    ke_r09 = adapt25_from_pre_post(tuple(cfg["ke_mvt_nm"]["COL"][0]), tuple(cfg["ke_mvt_nm"]["COL"][1]), n_c,
                                   tuple(cfg["ke_mvt_nm"]["PLA"][0]), tuple(cfg["ke_mvt_nm"]["PLA"][1]), n_p, wk, 0.9)
    rm10_r09 = adapt25_from_pre_post(tuple(cfg["ten_rm_kg"]["COL"][0]), tuple(cfg["ten_rm_kg"]["COL"][1]), n_c,
                                     tuple(cfg["ten_rm_kg"]["PLA"][0]), tuple(cfg["ten_rm_kg"]["PLA"][1]), n_p, wk, 0.9)

    stiff_col = 100.0 * (cfg["pt_stiffness_n_mm"]["COL"][1][0] - cfg["pt_stiffness_n_mm"]["COL"][0][0]) / cfg["pt_stiffness_n_mm"]["COL"][0][0]
    stiff_pla = 100.0 * (cfg["pt_stiffness_n_mm"]["PLA"][1][0] - cfg["pt_stiffness_n_mm"]["PLA"][0][0]) / cfg["pt_stiffness_n_mm"]["PLA"][0][0]
    csa_col = 100.0 * (cfg["pt_csa_mm2"]["COL"][1][0] - cfg["pt_csa_mm2"]["COL"][0][0]) / cfg["pt_csa_mm2"]["COL"][0][0]
    csa_pla = 100.0 * (cfg["pt_csa_mm2"]["PLA"][1][0] - cfg["pt_csa_mm2"]["PLA"][0][0]) / cfg["pt_csa_mm2"]["PLA"][0][0]

    return {
        "source_id": "SRC-0199",
        "cohort": "Lee et al. 2025 (PMC11917387, n=20: 9 COL vs 11 PLA, 12 wk RT, middle-aged adults)",
        "ke_mvt_adapt25_r05": ke_r05,
        "ke_mvt_adapt25_r09": ke_r09,
        "ke_mvt_published_gxt_p": cfg["ke_mvt_nm"]["gxt_p"],
        "ten_rm_submax_adapt25_r09": {**rm10_r09, "published_gxt_p": cfg["ten_rm_kg"]["gxt_p"], "note": "Submaximal 10-RM, not 1RM/MVC; ADAPT25 point estimate is still negative (-0.383 pp/wk)."},
        "explosive_and_power_gxt_p": {"ke_prtd_p": cfg["ke_prtd_nms"]["gxt_p"], "cmj_power_p": cfg["cmj_power_w"]["gxt_p"]},
        "tendon_remodeling_proven": {
            "pt_stiffness_gain_pct": {"COL": round(stiff_col, 2), "PLA": round(stiff_pla, 2), "gxt_p": cfg["pt_stiffness_n_mm"]["gxt_p"]},
            "pt_modulus_gxt_p": cfg["pt_modulus_gpa"]["gxt_p"],
            "pt_csa_gain_pct": {"COL": round(csa_col, 2), "PLA": round(csa_pla, 2), "gxt_p": cfg["pt_csa_mm2"]["gxt_p"]},
            "pt_max_strain_pre_post_pct": cfg["pt_strain_pct"],
        },
        "passes_adapt25": False,
        "passes_force20": False,
        "verdict": (
            "HOLD (NO DETECTABLE STRENGTH ACCELERATION DESPITE TENDON REMODELING): Collagen significantly accelerates patellar tendon stiffness "
            "(+56.4% vs +18.9%, p=0.009), modulus (p=0.018), and CSA (+6.5% vs 0.0%, p=0.027) while reducing strain 11.3->9.1%, "
            "YET yields no statistically detectable strength/power advantage (KE MVT GxT p=0.754, pRTD p=0.637, CMJ power p=0.422); "
            "however, n=9 vs 11 leaves wide ADAPT25 95% CIs ([-0.964; +1.182] at r=0.9) that do not prove strict zero effect."
        ),
    }


def analyze_lee_2023(cfg: dict) -> dict:
    n_c, n_p, wk = cfg["n_col"], cfg["n_pla"], cfg["weeks"]
    # Exact published Delta +- SD in Nm converted to % of Pre mean
    iso_c = cfg["iso_ke_mvc_nm"]["COL"]
    iso_p = cfg["iso_ke_mvc_nm"]["PLA"]
    iso = adapt25_from_pct_means_sds(
        100.0 * iso_c[2][0] / iso_c[0][0], 100.0 * iso_c[2][1] / iso_c[0][0], n_c,
        100.0 * iso_p[2][0] / iso_p[0][0], 100.0 * iso_p[2][1] / iso_p[0][0], n_p, wk
    )
    con_c = cfg["con_ke_mvc_nm"]["COL"]
    con_p = cfg["con_ke_mvc_nm"]["PLA"]
    con = adapt25_from_pct_means_sds(
        100.0 * con_c[2][0] / con_c[0][0], 100.0 * con_c[2][1] / con_c[0][0], n_c,
        100.0 * con_p[2][0] / con_p[0][0], 100.0 * con_p[2][1] / con_p[0][0], n_p, wk
    )
    return {
        "source_id": "SRC-0200",
        "cohort": "Lee et al. 2023 (PMC9910607, n=17: 8 COL vs 9 PLA, 10 wk in-season RT, female soccer players)",
        "iso_ke_mvc_adapt25": {**iso, "published_gxt_p": cfg["iso_ke_mvc_nm"]["gxt_p"]},
        "con_ke_mvc_adapt25": {**con, "published_gxt_p": cfg["con_ke_mvc_nm"]["gxt_p"]},
        "pt_strain_pre_post_pct": cfg["pt_strain_pct"],
        "passes_adapt25": False,
        "passes_force20": False,
        "verdict": (
            f"HOLD (PT strain stays <9.0% in COL [8.9->7.3%], but Iso KE MVC ADAPT25 CI spans zero "
            f"[{iso['ci95_pp_per_wk'][0]:+.3f}; {iso['ci95_pp_per_wk'][1]:+.3f}] pp/wk with GxT p=0.325 and near-zero PLA rate "
            f"+{iso['rate_C_pp_per_wk']:.3f} pp/wk; Con KE MVC is negative {con['adapt25_contrast_pp_per_wk']:+.3f} pp/wk)."
        ),
    }


def analyze_radovanovic_2022(cfg: dict) -> dict:
    n_hl = cfg["n_high_load"]
    m_mvc, sd_mvc = cfg["hl_pf_mvc_pct_mean_sd"]
    se_mvc = sd_mvc / math.sqrt(n_hl)
    tcrit = float(stats.t.ppf(0.975, n_hl - 1))
    ci_mvc = [round(m_mvc - tcrit * se_mvc, 2), round(m_mvc + tcrit * se_mvc, 2)]
    return {
        "source_id": "SRC-0201",
        "cohort": "Radovanovic et al. 2022 (PMC9768072, n=44: 15 High-Load vs 15 Alfredson vs 14 Passive, 12 wk Achilles tendinopathy RCT)",
        "high_load_pf_mvc_gain_pct": {"mean": m_mvc, "sd": sd_mvc, "ci95": ci_mvc},
        "high_load_tendon_remodeling": {
            "at_stiffness_pct": cfg["hl_at_stiffness_pct_mean_sd"],
            "at_csa_pct": cfg["hl_at_csa_pct_mean_sd"],
            "at_max_strain_pct": cfg["hl_at_max_strain_pct_mean_sd"],
        },
        "cmj_tradeoff": {
            "hl_pre_post_cm": cfg["cmj_cm_hl_pre_post"],
            "overall_change_cm_sd_p": cfg["cmj_overall_change_cm"],
        },
        "passes_adapt25": False,
        "passes_force20": False,
        "verdict": "HOLD (strain-targeted high-loading genuinely increases Achilles CSA +8.98%, stiffness +20.1%, and lowers max strain -12.4% p=0.001, YET PF MVC rises only +7.2% [1.72; 12.68]% — far below FORCE20 — and explosive CMJ height decreases -0.63 cm p=0.005; tendinopathic clinical cohort).",
    }


def run_experiment(data_root: Path) -> dict:
    src_cfg = json.loads(SOURCES_PATH.read_text("utf-8"))
    verified = verify_sources(data_root, src_cfg)

    balshaw = analyze_balshaw_2025(src_cfg["balshaw_2025"])
    lee25 = analyze_lee_2025(src_cfg["lee_2025"])
    lee23 = analyze_lee_2023(src_cfg["lee_2023"])
    rado = analyze_radovanovic_2022(src_cfg["radovanovic_2022"])

    return {
        "experiment_id": "EXP-0156",
        "stage1_verdict": "HOLD",
        "stage1_blocker_status": "DATA_BLOCKED",
        "scientific_criterion_closed": False,
        "n_cohorts_tested": 4,
        "n_participants_total": 120,
        "cohorts_passing_stage1": 0,
        "verified_sources": verified,
        "trials": {
            "balshaw_2025_cp_patellar_15wk": balshaw,
            "lee_2025_hc_patellar_12wk": lee25,
            "lee_2023_col_patellar_10wk": lee23,
            "radovanovic_2022_hl_achilles_12wk": rado,
        },
        "summary_ruling": (
            "Testing a new internal biological mechanism — hydrolysed/bioactive collagen peptides + heavy RT across 3 double-blind RCTs "
            "on the patellar tendon (Balshaw 2025 n=39, Lee 2025 n=20, Lee 2023 n=17) plus strain-targeted Achilles loading (Radovanovic 2022 n=44) — "
            "yields 0/4 cohorts closing Stage 1. In Lee 2025 and Radovanovic 2022, significant tendon remodeling (stiffness +20..+56%, CSA +6.5..+9.0%, strain reduction) "
            "was not accompanied by statistically detectable ADAPT25 or FORCE20 strength superiority (KE MVT GxT p=0.754 in Lee 2025, though wide n=9 vs 11 CIs do not prove strict zero effect; "
            "PF MVC +7.2% with CMJ decline in Radovanovic 2022). In the largest trial (Balshaw 2025 n=39), ADAPT25 KE MVT is -0.382 [-0.852; +0.089] pp/wk (p>=0.596), "
            "practically ruling out a large +25% acceleration, while collagen also did not significantly alter tendon remodeling (p>=0.365). Stage 1 remains HOLD / DATA_BLOCKED."
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
            raise SystemExit("EXP-0156 replay mismatch")
        print("EXP-0156 exact replay")
    else:
        RESULTS_PATH.write_text(payload, "utf-8")
        print(f"Wrote {RESULTS_PATH} ({len(payload)} bytes); stage1={res['stage1_verdict']}/{res['stage1_blocker_status']}")


if __name__ == "__main__":
    main()
