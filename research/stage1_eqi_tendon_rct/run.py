"""Reproduce EXP-0150 Stage 1 analysis on Krizaj 2026 RCT, O'Leary 2026, and Waugh 2021."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from openpyxl import load_workbook
from scipy.stats import pearsonr, spearmanr, t as student_t

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 1502026
DRAWS = 10000
WEEKS_KRIZAJ = 6.0


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def boot_mean(arr, rng):
    arr = np.asarray(arr, dtype=float)
    idx = rng.integers(0, len(arr), (DRAWS, len(arr)))
    means = arr[idx].mean(axis=1)
    return {
        'n': int(len(arr)),
        'mean': float(arr.mean()),
        'sd': float(arr.std(ddof=1)),
        'ci95': [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
    }


def boot_diff(a, b, rng, factor_b=1.0):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ia = rng.integers(0, len(a), (DRAWS, len(a)))
    ib = rng.integers(0, len(b), (DRAWS, len(b)))
    diffs = a[ia].mean(axis=1) - factor_b * b[ib].mean(axis=1)
    est = float(a.mean() - factor_b * b.mean())
    return {
        'estimate': est,
        'ci95': [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
    }


def analyze_krizaj(xlsx_path, baseline_check):
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb['Data']
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    col = {h: i for i, h in enumerate(hdr)}
    recs = [r for r in rows[1:] if r[col['GROUP']] is not None]
    require(len(recs) == 46, f'Expected 46 participants, got {len(recs)}')

    gmap = {1: 'EQI', 2: 'ECC', 3: 'Control'}
    by_group = {name: [r for r in recs if r[col['GROUP']] == code] for code, name in gmap.items()}
    require((len(by_group['EQI']), len(by_group['ECC']), len(by_group['Control'])) == (15, 15, 16), 'Unexpected group sizes')

    # Verify Table 1 baseline means against JSSM 2026 PDF
    check_cols = {
        'IS_Nm': 'ISOMETRIC_MVC_TORQUE_PRE',
        'CS_Nm': 'CONCENTRIC_MVC_TORQUE_PRE',
        'ES_Nm': 'ECCENTRIC_MVC_TORQUE_PRE',
        'ATT_mm': 'ACHILLES_TENDON_THICKNESS_PRE',
        'ATS_kPa': 'ACHILLES_TENDON_STIFFNESS_PRE',
    }
    max_table1_err = 0.0
    for gname, expected in baseline_check.items():
        for short_k, col_name in check_cols.items():
            obs = float(np.mean([r[col[col_name]] for r in by_group[gname]]))
            max_table1_err = max(max_table1_err, abs(obs - expected[short_k]))
    require(max_table1_err < 0.01, f'Table 1 baseline mismatch: {max_table1_err}')

    rng = np.random.default_rng(SEED)

    def pct_changes(gname, base):
        vals = []
        for r in by_group[gname]:
            pre, post = r[col[f'{base}_PRE']], r[col[f'{base}_POST']]
            require(pre is not None and post is not None and pre > 0, f'Invalid pair {base}')
            vals.append(100.0 * (post / pre - 1.0))
        return np.asarray(vals, dtype=float)

    strength_vars = [
        'ISOMETRIC_MVC_TORQUE',
        'CONCENTRIC_MVC_TORQUE',
        'ECCENTRIC_MVC_TORQUE',
        'EQI_REP1_PEAK_TORQUE',
    ]
    tissue_and_func_vars = [
        'ACHILLES_TENDON_THICKNESS',
        'ACHILLES_TENDON_STIFFNESS',
        'MEDIAL_GASTROC_THICKNESS',
        'LATERAL_GASTROC_THICKNESS',
        'CLOSED_CHAIN_TOTAL_ROM',
    ]

    within_group = {}
    for var in strength_vars + tissue_and_func_vars:
        within_group[var] = {}
        for gname in ('EQI', 'ECC', 'Control'):
            arr = pct_changes(gname, var)
            s = boot_mean(arr, rng)
            if var in strength_vars:
                s['n_ge_20pct'] = int(np.sum(arr >= 20.0))
            within_group[var][gname] = s

    force20_adjusted = {}
    adapt25_active = {}
    for var in strength_vars:
        eqi = pct_changes('EQI', var)
        ecc = pct_changes('ECC', var)
        con = pct_changes('Control', var)
        force20_adjusted[var] = {
            'EQI_minus_Control_pp': boot_diff(eqi, con, rng, 1.0),
            'ECC_minus_Control_pp': boot_diff(ecc, con, rng, 1.0),
        }
        r_eqi = eqi / WEEKS_KRIZAJ
        r_ecc = ecc / WEEKS_KRIZAJ
        adapt25_active[var] = {
            'rate_EQI_pct_per_wk': boot_mean(r_eqi, rng),
            'rate_ECC_pct_per_wk': boot_mean(r_ecc, rng),
            'EQI_minus_1p25_ECC_pp_per_wk': boot_diff(r_eqi, r_ecc, rng, 1.25),
            'ECC_minus_1p25_EQI_pp_per_wk': boot_diff(r_ecc, r_eqi, rng, 1.25),
        }

    # Same-participant strength-to-tendon correlations in active arms (n=30)
    active_iso = np.concatenate([pct_changes('EQI', 'ISOMETRIC_MVC_TORQUE'), pct_changes('ECC', 'ISOMETRIC_MVC_TORQUE')])
    active_att = np.concatenate([pct_changes('EQI', 'ACHILLES_TENDON_THICKNESS'), pct_changes('ECC', 'ACHILLES_TENDON_THICKNESS')])
    active_ats = np.concatenate([pct_changes('EQI', 'ACHILLES_TENDON_STIFFNESS'), pct_changes('ECC', 'ACHILLES_TENDON_STIFFNESS')])
    r_att, p_att = pearsonr(active_iso, active_att)
    rho_att, prho_att = spearmanr(active_iso, active_att)
    r_ats, p_ats = pearsonr(active_iso, active_ats)
    rho_ats, prho_ats = spearmanr(active_iso, active_ats)

    # Session pain & effort summaries across 12 sessions
    session_monitoring = {}
    for gname in ('EQI', 'ECC'):
        pains = [r[col[f'PAIN_SCORE_SESSION_{s}']] for r in by_group[gname] for s in range(1, 13) if r[col[f'PAIN_SCORE_SESSION_{s}']] is not None]
        efforts = [r[col[f'EFFORT_SCORE_SESSION_{s}']] for r in by_group[gname] for s in range(1, 13) if r[col[f'EFFORT_SCORE_SESSION_{s}']] is not None]
        part_max_pain = [max(r[col[f'PAIN_SCORE_SESSION_{s}']] for s in range(1, 13) if r[col[f'PAIN_SCORE_SESSION_{s}']] is not None) for r in by_group[gname]]
        session_monitoring[gname] = {
            'n_pain_obs': len(pains),
            'pain_mean': float(np.mean(pains)),
            'pain_max': float(np.max(pains)),
            'n_participants_pain_ge_4': int(sum(x >= 4 for x in part_max_pain)),
            'effort_mean': float(np.mean(efforts)),
        }

    return {
        'n_total': 46,
        'group_n': {'EQI': 15, 'ECC': 15, 'Control': 16},
        'weeks': WEEKS_KRIZAJ,
        'table1_baseline_max_abs_diff': max_table1_err,
        'post_body_mass_available': False,
        'intermediate_strength_or_tendon_visits_available': False,
        'tendon_stiffness_modality': 'resting_shear_wave_elastography_kPa_prone_5cm_above_insertion',
        'within_group_pct_change': within_group,
        'force20_control_adjusted_pp': force20_adjusted,
        'adapt25_active_controlled_pp_per_wk': adapt25_active,
        'active_arms_strength_tendon_correlations_n30': {
            'iso_mvc_vs_tendon_thickness': {'pearson_r': float(r_att), 'p': float(p_att), 'spearman_rho': float(rho_att), 'p_spearman': float(prho_att)},
            'iso_mvc_vs_tendon_stiffness': {'pearson_r': float(r_ats), 'p': float(p_ats), 'spearman_rho': float(rho_ats), 'p_spearman': float(prho_ats)},
        },
        'session_monitoring_12_sessions': session_monitoring,
    }


def analyze_oleary(pub):
    # Reconstruct SE from published paired 95% CI (mean_diff, lo, hi) using t-critical
    t5 = pub['table5_paired_complete']
    n_c, n_i = t5['control_n'], t5['intervention_n']
    tc = float(student_t.ppf(0.975, n_c - 1))
    ti = float(student_t.ppf(0.975, n_i - 1))

    def diff_from_ci(pair_i, pair_c):
        mi, loi, hii = pair_i
        mc, loc, hic = pair_c
        sei = (hii - loi) / (2.0 * ti)
        sec = (hic - loc) / (2.0 * tc)
        se_diff = math.hypot(sei, sec)
        df = min(n_i, n_c) - 1
        rad = float(student_t.ppf(0.975, df)) * se_diff
        d = mi - mc
        return {'diff': d, 'ci95_approx': [d - rad, d + rad]}

    mvc_w18_diff = diff_from_ci(t5['mvc_N_w1_w18']['intervention'], t5['mvc_N_w1_w18']['control'])
    # Scale by intervention baseline mean (127 N) as diagnostic % of baseline
    base_i = pub['table4_means']['intervention_n17']['mvc_N'][0]
    return {
        'design': pub['design'],
        'complete_pairs_n': {'intervention': n_i, 'control': n_c},
        'table4_ratio_of_means_mvc_w1_to_w18_pct': {
            'intervention': 100.0 * (pub['table4_means']['intervention_n17']['mvc_N'][2] / base_i - 1.0),
            'control': 100.0 * (pub['table4_means']['control_n14']['mvc_N'][2] / pub['table4_means']['control_n14']['mvc_N'][0] - 1.0),
        },
        'control_adjusted_mvc_w18_N': mvc_w18_diff,
        'control_adjusted_mvc_w18_pct_of_w1_mean': {
            'diff_pp': 100.0 * mvc_w18_diff['diff'] / base_i,
            'ci95_approx_pp': [100.0 * x / base_i for x in mvc_w18_diff['ci95_approx']],
        },
        'control_adjusted_tendon_force_w18_N': diff_from_ci(t5['tendon_force_N_w1_w18']['intervention'], t5['tendon_force_N_w1_w18']['control']),
        'control_adjusted_stress_w18_MPa': diff_from_ci(t5['stress_MPa_w1_w18']['intervention'], t5['stress_MPa_w1_w18']['control']),
        'control_adjusted_strain_w18_pp': diff_from_ci(t5['strain_pct_w1_w18']['intervention'], t5['strain_pct_w1_w18']['control']),
        'control_adjusted_stiffness_w6_N_mm': diff_from_ci(t5['stiffness_N_mm_w1_w6']['intervention'], t5['stiffness_N_mm_w1_w6']['control']),
        'control_adjusted_stiffness_w18_N_mm': diff_from_ci(t5['stiffness_N_mm_w1_w18']['intervention'], t5['stiffness_N_mm_w1_w18']['control']),
        'limitations': 'Non-randomised postpartum cohort, passive standard-care control (not active ADAPT25 comparator), individual data not published.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT / 'tmp')
    parser.add_argument('--output', type=Path, default=HERE / 'RESULTS.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for key, info in sources['files_under_data_root'].items():
        p = args.data_root / info['path']
        require(p.is_file(), f'Missing source file {key}: {p}')
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        require(digest == info['sha256'], f'SHA-256 mismatch for {key}: {digest}')

    krizaj_path = args.data_root / sources['files_under_data_root']['krizaj_xlsx']['path']
    krizaj_res = analyze_krizaj(krizaj_path, sources['krizaj_table1_baseline_check'])
    oleary_res = analyze_oleary(sources['oleary_2026_published_tables'])

    artifacts = ('PROTOCOL.md', 'SOURCES.json', 'run.py')
    result = {
        'experiment_id': 'EXP-0150',
        'stage': 'Stage 1',
        'verdict': 'HOLD',
        'bootstrap': {'seed': SEED, 'draws': DRAWS, 'unit': 'participant'},
        'artifact_sha256_lf': {
            name: hashlib.sha256((HERE / name).read_text(encoding='utf-8').encode()).hexdigest()
            for name in artifacts
        },
        'krizaj_2026_rct_zenodo_19202208': krizaj_res,
        'oleary_2026_18wk_patellar_tendon': oleary_res,
        'waugh_2021_walking_transfer_comparator': sources['waugh_2021_published_table1'],
    }
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.check:
        require(args.output.read_text(encoding='utf-8') == text, 'EXP-0150 output differs from saved RESULTS.json')
        print('EXP-0150 exact replay')
    else:
        args.output.write_text(text, encoding='utf-8', newline='\n')
        print('EXP-0150 RESULTS.json written')


if __name__ == '__main__':
    main()
