"""Reproduce EXP-0151 Stage 2 open human data audit against EXP-0149 working CPE45 assumptions."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 1512026
DRAWS = 10000


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
        'min': float(arr.min()),
        'max': float(arr.max()),
        'ci95': [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
    }


def boot_diff(a, b, rng):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ia = rng.integers(0, len(a), (DRAWS, len(a)))
    ib = rng.integers(0, len(b), (DRAWS, len(b)))
    diffs = a[ia].mean(axis=1) - b[ib].mean(axis=1)
    return {
        'estimate': float(a.mean() - b.mean()),
        'ci95': [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
    }


def analyze_narang(xlsx_path, working_spec):
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb['Exercise_heat_stress']
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    col = {h: i for i, h in enumerate(hdr)}
    recs = [r for r in rows[1:] if r[col['Participant_ID']] is not None]
    require(len(recs) == 53, f'Expected 53 sessions, got {len(recs)}')

    rng = np.random.default_rng(SEED)
    tiers = working_spec['working_thresholds']['tiers']

    sessions = []
    for r in recs:
        pw = float(r[col['Power_W']])
        work_kj = pw * 2700.0 / 1000.0
        tc_end = float(r[col['Tcore_end']]) if r[col['Tcore_end']] is not None else None
        tc_del = float(r[col['Tcore_delta']]) if r[col['Tcore_delta']] is not None else None
        sessions.append({
            'id': str(r[col['Participant_ID']]),
            'group': str(r[col['Group']]),
            'timepoint': str(r[col['Timepoint']]),
            'power_W': pw,
            'work45_kJ': work_kj,
            'tcore_end_C': tc_end,
            'tcore_delta_C': tc_del,
            'hr_ss': float(r[col['HR_ss']]) if r[col['HR_ss']] is not None else None,
            'vo2kg_ss': float(r[col['VO2kg_ss']]) if r[col['VO2kg_ss']] is not None else None,
            'lactate_delta': float(r[col['Lactate_delta']]) if r[col['Lactate_delta']] is not None else None,
            'borg_mean_45': float(r[col['Borg_mean_45']]) if r[col['Borg_mean_45']] is not None else None,
        })

    baseline = [s for s in sessions if s['timepoint'] == 'Baseline']
    post = [s for s in sessions if s['timepoint'] == 'Post']
    require(len(baseline) == 27 and len(post) == 26, 'Unexpected Baseline/Post counts')

    # Screen all 53 sessions and 27 baseline sessions against EXP-0149 working tiers
    def screen_subset(sub):
        out = {}
        for tname, cfg in tiers.items():
            t_obs = [s for s in sub if s['tcore_end_C'] is not None]
            w_pass = sum(1 for s in sub if s['work45_kJ'] >= cfg['work_positive_2700s_kJ_min'])
            t_pass = sum(1 for s in t_obs if s['tcore_end_C'] < cfg['thermal_core_max_C'])
            j_pass = sum(1 for s in t_obs if s['work45_kJ'] >= cfg['work_positive_2700s_kJ_min'] and s['tcore_end_C'] < cfg['thermal_core_max_C'])
            out[tname] = {
                'n_work': len(sub),
                'n_thermal_observed': len(t_obs),
                'work_passed': w_pass,
                'thermal_passed': t_pass,
                'joint_work_and_thermal_passed': j_pass,
                'thermal_breaches_ge_cap': len(t_obs) - t_pass,
            }
        return out

    # Paired Pre->Post hypoxia acclimation effect (complete non-null pairs only, no imputation)
    by_pair = {}
    for s in sessions:
        by_pair.setdefault((s['group'], s['id']), {})[s['timepoint']] = s
    paired = {}
    for grp in ('Hypoxia', 'Control'):
        d_end, d_delta = [], []
        for (g, pid), d in sorted(by_pair.items()):
            if g == grp and 'Baseline' in d and 'Post' in d:
                if d['Post']['tcore_end_C'] is not None and d['Baseline']['tcore_end_C'] is not None:
                    d_end.append(d['Post']['tcore_end_C'] - d['Baseline']['tcore_end_C'])
                if d['Post']['tcore_delta_C'] is not None and d['Baseline']['tcore_delta_C'] is not None:
                    d_delta.append(d['Post']['tcore_delta_C'] - d['Baseline']['tcore_delta_C'])
        paired[grp] = {
            'n_paired_tcore_end': len(d_end),
            'n_paired_tcore_delta': len(d_delta),
            'post_minus_base_tcore_end_C': boot_mean(d_end, rng),
            'post_minus_base_tcore_delta_C': boot_mean(d_delta, rng),
            '_raw_end': d_end,
            '_raw_delta': d_delta,
        }
    hyp_vs_con = {
        'tcore_end_C_diff_in_diff': boot_diff(paired['Hypoxia']['_raw_end'], paired['Control']['_raw_end'], rng),
        'tcore_delta_C_diff_in_diff': boot_diff(paired['Hypoxia']['_raw_delta'], paired['Control']['_raw_delta'], rng),
    }
    for grp in ('Hypoxia', 'Control'):
        del paired[grp]['_raw_end']
        del paired[grp]['_raw_delta']

    return {
        'n_unique_participants': len({s['id'] for s in sessions}),
        'n_sessions_total': len(sessions),
        'baseline_n27': {
            'power_W': boot_mean([s['power_W'] for s in baseline], rng),
            'work45_kJ': boot_mean([s['work45_kJ'] for s in baseline], rng),
            'tcore_end_C': boot_mean([s['tcore_end_C'] for s in baseline if s['tcore_end_C'] is not None], rng),
            'tcore_delta_C': boot_mean([s['tcore_delta_C'] for s in baseline if s['tcore_delta_C'] is not None], rng),
            'hr_ss_bpm': boot_mean([s['hr_ss'] for s in baseline if s['hr_ss'] is not None], rng),
            'borg_mean_45': boot_mean([s['borg_mean_45'] for s in baseline if s['borg_mean_45'] is not None], rng),
        },
        'post_n26': {
            'work45_kJ': boot_mean([s['work45_kJ'] for s in post], rng),
            'tcore_end_C': boot_mean([s['tcore_end_C'] for s in post if s['tcore_end_C'] is not None], rng),
            'tcore_delta_C': boot_mean([s['tcore_delta_C'] for s in post if s['tcore_delta_C'] is not None], rng),
        },
        'working_spec_screening': {
            'baseline_n27': screen_subset(baseline),
            'all_sessions_n53': screen_subset(sessions),
        },
        'paired_hypoxia_acclimation': {
            'by_group': paired,
            'hypoxia_minus_control': hyp_vs_con,
        },
        'cpe45_contract_gap': 'Constant-load 40% MAP in insulated heat suit; no alternating explosive bouts, no force/speed/coordination/maneuver/trials channels, no post45 MVC.',
    }


def analyze_bilgin(pub, working_spec):
    tiers = working_spec['working_thresholds']['tiers']
    out = {'n': pub['n'], 'bout_duration_min': pub['bout_duration_min'], 'conditions': {}}
    for cond in ('vt1', 'vt2'):
        h_pre, h_dual, h_post = pub['hits'][cond]['pre'][0], pub['hits'][cond]['dual'][0], pub['hits'][cond]['post'][0]
        rt_pre, rt_dual, rt_post = pub['hit_rt_ms'][cond]['pre'][0], pub['hit_rt_ms'][cond]['dual'][0], pub['hit_rt_ms'][cond]['post'][0]
        dp_pre, dp_dual, dp_post = pub['dprime'][cond]['pre'][0], pub['dprime'][cond]['dual'][0], pub['dprime'][cond]['post'][0]
        rt_inc_dual = rt_dual - rt_pre
        rt_inc_post = rt_post - rt_pre
        out['conditions'][cond] = {
            'hits_dual_change_pct': 100.0 * (h_dual / h_pre - 1.0),
            'hits_post_change_pct': 100.0 * (h_post / h_pre - 1.0),
            'dprime_dual_change_pct': 100.0 * (dp_dual / dp_pre - 1.0),
            'dprime_post_change_pct': 100.0 * (dp_post / dp_pre - 1.0),
            'hit_rt_dual_change_ms': rt_inc_dual,
            'hit_rt_post_change_ms': rt_inc_post,
            'dual_rt_exceeds_working_tiers': {
                tname: rt_inc_dual > cfg['correct_latency_increase_ms_max']
                for tname, cfg in tiers.items()
            },
        }
    out['anova_p'] = pub['anova_p']
    out['cpe45_contract_gap'] = '10-min continuous bouts at VT1/VT2; group summaries only; no 2700-s power/force/coordination/post45 MVC.'
    return out


def audit_zenodo_24353000(readme_path, demo_path):
    readme = readme_path.read_text(encoding='utf-8', errors='replace')
    with demo_path.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    levels = sorted({r.get('Poziom', '') for r in rows})
    return {
        'status': 'REJECTED_PROVENANCE_MISMATCH',
        'zenodo_metadata_claim': 'Pilot RCT in 8 elite male judokas (Polish National Judo Senior Team) under hypoxia/normoxia',
        'actual_file_rows_n': len(rows),
        'actual_file_poziom_values': levels,
        'readme_declares_topmma_n30': 'TopMMA' in readme and 'n = 30' in readme,
        'readme_discloses_prior_control_duplication': 'Duplikacja grupy CONTROL' in readme,
        'admitted': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT / 'tmp')
    parser.add_argument('--output', type=Path, default=HERE / 'RESULTS.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    working_spec = json.loads((ROOT / sources['working_spec_ref']).read_text(encoding='utf-8'))

    for key, info in sources['files_under_data_root'].items():
        p = args.data_root / info['path']
        require(p.is_file(), f'Missing source file {key}: {p}')
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        require(digest == info['sha256'], f'SHA-256 mismatch for {key}: {digest}')

    narang_res = analyze_narang(args.data_root / sources['files_under_data_root']['narang_xlsx']['path'], working_spec)
    bilgin_res = analyze_bilgin(sources['bilgin_2026_published_tables'], working_spec)
    z243_audit = audit_zenodo_24353000(
        args.data_root / sources['files_under_data_root']['zenodo_24353000_readme']['path'],
        args.data_root / sources['files_under_data_root']['zenodo_24353000_demographics']['path'],
    )

    artifacts = ('PROTOCOL.md', 'SOURCES.json', 'run.py')
    result = {
        'experiment_id': 'EXP-0151',
        'stage': 'Stage 2',
        'target_id': 'TARGET-CPE45',
        'verdict': 'NOT_EXTERNALLY_VALIDATED_HOLD',
        'joint_2700s_admitted_cohorts': 0,
        'bootstrap': {'seed': SEED, 'draws': DRAWS, 'unit': 'participant'},
        'artifact_sha256_lf': {
            name: hashlib.sha256((HERE / name).read_text(encoding='utf-8').encode()).hexdigest()
            for name in artifacts
        },
        'narang_2026_femadapt_zenodo_20284986': narang_res,
        'bilgin_2026_dual_task_cycling_pmc13702500': bilgin_res,
        'deely_2022_soccer_recovery_pmc9235147': {
            **sources['deely_2022_published_summary'],
            'breaches_working_24h_95pct_at_72h': True,
        },
        'zenodo_24353000_provenance_rejection': z243_audit,
    }
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.check:
        require(args.output.read_text(encoding='utf-8') == text, 'EXP-0151 output differs from saved RESULTS.json')
        print('EXP-0151 exact replay')
    else:
        args.output.write_text(text, encoding='utf-8', newline='\n')
        print('EXP-0151 RESULTS.json written')


if __name__ == '__main__':
    main()
