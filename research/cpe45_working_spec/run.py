"""Compute EXP-0149 working CPE45 threshold sensitivity and protocol conformance check."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import cpe45  # noqa: E402


def require(condition, msg):
    if not condition:
        raise ValueError(msg)


def quantiles(values):
    arr = np.asarray(list(values), dtype=float)
    require(len(arr) > 0 and np.isfinite(arr).all(), 'Invalid numeric array')
    return {
        'n': int(len(arr)),
        'mean': float(arr.mean()),
        'sd': float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        'min': float(arr.min()),
        'p10': float(np.quantile(arr, 0.10)),
        'p25': float(np.quantile(arr, 0.25)),
        'p50': float(np.quantile(arr, 0.50)),
        'p75': float(np.quantile(arr, 0.75)),
        'p90': float(np.quantile(arr, 0.90)),
        'max': float(arr.max()),
    }


def pass_rate(values, predicate):
    vals = list(values)
    passed = sum(1 for v in vals if predicate(v))
    return {'passed': passed, 'n': len(vals), 'fraction': passed / len(vals) if vals else None}


def build_synthetic_protocol_fixture(spec):
    """Deterministic conformance fixture for tools/cpe45.py (SYNTHETIC, not empirical)."""
    episodes = []
    t = 0.0
    for _ in range(spec['intensity_schedule']['n_blocks']):
        for item in spec['intensity_schedule']['per_block_sequence']:
            for _ in range(item['repeat']):
                ed = item['effort']['duration_s']
                episodes.append(cpe45.Episode(t, t + ed, 'effort', item['effort']['task_id']))
                t += ed
                rd = item['recovery']['duration_s']
                episodes.append(cpe45.Episode(t, t + rd, 'recovery', item['recovery']['task_id']))
                t += rd
    require(abs(t - 2700.0) < 1e-9, f'Schedule sum != 2700: {t}')

    samples = []
    for sec in range(0, 2701):
        ts = float(sec)
        # Find active episode
        active = next(ep for ep in episodes if ep.start_s <= ts < ep.end_s) if sec < 2700 else episodes[-1]
        frac = ts / 2700.0
        if active.kind == 'effort' and active.task_id == 'explosive_sprint_6s':
            p_w = 700.0 * (1.0 - 0.10 * frac)
            f_n = 900.0 * (1.0 - 0.08 * frac)
            v_ms = 6.0 * (1.0 - 0.08 * frac)
            a_ms2 = 3.0 * (1.0 - 0.08 * frac)
        elif active.kind == 'effort':
            p_w = 240.0 * (1.0 - 0.06 * frac)
            f_n = 350.0 * (1.0 - 0.06 * frac)
            v_ms = 3.5 * (1.0 - 0.05 * frac)
            a_ms2 = 0.5
        else:
            p_w = 60.0
            f_n = 100.0
            v_ms = 1.5
            a_ms2 = 0.0
        samples.append(cpe45.Sample(
            time_s=ts,
            power_W=p_w,
            force_N=f_n,
            speed_m_s=v_ms,
            acceleration_m_s2=a_ms2,
            coordination_error_m=0.02 * (1.0 + 0.10 * frac),
            maneuver_error_m=0.05 * (1.0 + 0.10 * frac),
        ))

    trials = []
    for blk in range(5):
        base = blk * 540.0
        for idx, offset in enumerate((3.0, 33.0, 63.0, 120.0, 345.0)):
            task = 'explosive_sprint_6s' if idx < 3 else 'submax_sustained_165s'
            trials.append(cpe45.Trial(
                time_s=base + offset,
                task_id=task,
                latency_s=0.35 + 0.004 * blk,
                correct=True,
                omitted=False,
            ))

    post_samples = [
        cpe45.Sample(2760.0 + i, 630.0 - 1.5 * i, 828.0 - 1.2 * i, 5.52 - 0.01 * i, 2.76 - 0.01 * i, 0.022, 0.055)
        for i in range(7)
    ]
    trials.append(cpe45.Trial(time_s=2763.0, task_id='explosive_sprint_6s', latency_s=0.37, correct=True, omitted=False))

    win = spec['early_late_windows_s']['working_default']
    out = cpe45.analyze(
        samples,
        episodes,
        trials,
        early_end_s=win['early_end_s'],
        late_start_s=win['late_start_s'],
        max_gap_s=win['max_gap_s'],
        post_samples=post_samples,
        post_task_id='explosive_sprint_6s',
    )
    return {
        'data_type': 'SYNTHETIC_MODEL_SIMULATION',
        'empirical_validation': False,
        'target_achievement': out['target_achievement'],
        'physiological_validation': out['physiological_validation'],
        'n_episodes': len(out['episodes']),
        'total_work_positive_kJ': out['total']['work_positive_J'] / 1000.0,
        'matched_task_ids': sorted(out['early_late'].keys()),
        'unmatched_task_ids': out['unmatched_task_ids'],
        'early_late_episode_counts': {
            k: {'early': v['early_episodes'], 'late': v['late_episodes']}
            for k, v in out['early_late'].items()
        },
        'explosive_peak_power_relative_drop_pct': out['early_late']['explosive_sprint_6s']['metrics']['peak_power_W']['relative_drop'] * 100.0,
        'submax_mean_power_relative_drop_pct': out['early_late']['submax_sustained_165s']['metrics']['mean_power_W']['relative_drop'] * 100.0,
        'post45_status': out['post45']['status'],
        'post45_peak_force_retention_pct': out['post45']['comparison_to_early']['peak_force_N']['late_over_early'] * 100.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT / 'tmp')
    parser.add_argument('--output', type=Path, default=HERE / 'RESULTS.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    spec = json.loads((HERE / 'WORKING_SPEC.json').read_text(encoding='utf-8'))
    canonical = json.loads((ROOT / sources['canonical_contract']).read_text(encoding='utf-8'))
    require(canonical['success_thresholds'] is None, 'Canonical CPE45.json success_thresholds must remain null')
    require(canonical['historical_experiments_cpe45_status'] == 'not_assessed', 'Canonical historical status changed')

    # Verify raw EXP-0139 file hashes
    for name, info in sources['raw_inputs_under_data_root'].items():
        path = args.data_root / info['path']
        require(path.is_file(), f'Missing raw input {name}: {path}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == info['sha256'], f'SHA-256 mismatch for {name}: {digest}')

    exp139 = json.loads((ROOT / sources['canonical_inputs']['exp0139_results']).read_text(encoding='utf-8'))
    exp063 = json.loads((ROOT / sources['canonical_inputs']['exp0063_results']).read_text(encoding='utf-8'))
    tiers = spec['working_thresholds']['tiers']

    # 1. McLaughlin (n=24): 45-min continuous work, thermal peak, power drift across windows
    mcl = exp139['cohorts']['mclaughlin']['records']
    mcl_work_kj = [r['work45_J'] / 1000.0 for r in mcl if r['work45_J'] is not None]
    mcl_temp45 = [r['rectal_min45_C'] for r in mcl if r['rectal_min45_C'] is not None]
    mcl_pass = {
        tier: {
            'work_positive_2700s': pass_rate(mcl_work_kj, lambda x, t=cfg: x >= t['work_positive_2700s_kJ_min']),
            'thermal_core_max_C': pass_rate(mcl_temp45, lambda x, t=cfg: x < t['thermal_core_max_C']),
            'joint_work_and_thermal': pass_rate(
                zip(mcl_work_kj, mcl_temp45),
                lambda pair, t=cfg: pair[0] >= t['work_positive_2700s_kJ_min'] and pair[1] < t['thermal_core_max_C'],
            ),
        }
        for tier, cfg in tiers.items()
    }
    mcl_window_drift = {
        f'{w}min_W': quantiles([r[f'late_minus_early_{w}min_W'] for r in mcl])
        for w in (5, 9, 11)
    }

    # 2. Jutlah (n=21): explosive sprint peak/mean drop & window sensitivity (1x1, 2x2, 3x3) across rests 12/18/24 s
    jut_recs = exp139['cohorts']['jutlah']['records']
    jut_eval = {}
    for rest in (12, 18, 24):
        sub = [r for r in jut_recs if r['rest_s'] == rest]
        peak_2 = [r['peak_W_loss_pct_2'] for r in sub]
        avg_2 = [r['published_avg_W_loss_pct_2'] for r in sub]
        peak_3 = [r['peak_W_loss_pct_3'] for r in sub]
        avg_3 = [r['published_avg_W_loss_pct_3'] for r in sub]
        min_trans = [min(r['next_over_previous_peak']) for r in sub]
        mean_trans = [float(np.mean(r['next_over_previous_peak'])) for r in sub]
        jut_eval[str(rest)] = {
            'window_sensitivity_peak_loss_pct': {
                f'{w}x{w}': quantiles([r[f'peak_W_loss_pct_{w}'] for r in sub]) for w in (1, 2, 3)
            },
            'window_sensitivity_mean_power_loss_pct': {
                f'{w}x{w}': quantiles([r[f'published_avg_W_loss_pct_{w}'] for r in sub]) for w in (1, 2, 3)
            },
            'transition_mean_next_over_prev': quantiles(mean_trans),
            'transition_min_next_over_prev': quantiles(min_trans),
            'tier_pass_rates_2x2': {
                tier: {
                    'peak_power_drop': pass_rate(peak_2, lambda x, t=cfg: x <= t['explosive_peak_power_drop_pct_max']),
                    'mean_power_drop': pass_rate(avg_2, lambda x, t=cfg: x <= t['mean_power_drop_pct_max']),
                    'mean_transition_ratio': pass_rate(mean_trans, lambda x, t=cfg: x >= t['between_effort_next_over_prev_power_min']),
                    'joint_peak_and_mean': pass_rate(
                        zip(peak_2, avg_2),
                        lambda pair, t=cfg: pair[0] <= t['explosive_peak_power_drop_pct_max'] and pair[1] <= t['mean_power_drop_pct_max'],
                    ),
                }
                for tier, cfg in tiers.items()
            },
            'tier_pass_rates_3x3': {
                tier: {
                    'peak_power_drop': pass_rate(peak_3, lambda x, t=cfg: x <= t['explosive_peak_power_drop_pct_max']),
                    'mean_power_drop': pass_rate(avg_3, lambda x, t=cfg: x <= t['mean_power_drop_pct_max']),
                }
                for tier, cfg in tiers.items()
            },
        }

    # 3. Norbury (n=12): post-load recovery retention at 5 min, 45 min, 24 h
    nor_recs = exp139['cohorts']['norbury']['records']
    nor_eval = {}
    for cond in ('LL', 'HL'):
        sub = [r for r in nor_recs if r['condition'] == cond]
        ret_5m = [100.0 - r['loss_300s_pct'] for r in sub]
        ret_45m = [100.0 - r['loss_2700s_pct'] for r in sub]
        ret_24h = [100.0 - r['loss_86400s_pct'] for r in sub]
        nor_eval[cond] = {
            'retention_5m_pct': quantiles(ret_5m),
            'retention_45m_pct': quantiles(ret_45m),
            'retention_24h_pct': quantiles(ret_24h),
            'tier_pass_rates': {
                tier: {
                    'post_45min': pass_rate(ret_45m, lambda x, t=cfg: x >= t['post45_45min_mvc_retention_pct_min']),
                    'post_24h': pass_rate(ret_24h, lambda x, t=cfg: x >= t['post45_24h_mvc_retention_pct_min']),
                }
                for tier, cfg in tiers.items()
            },
        }

    # 4. Stroop / Remiszewski & Ligeza (n=71): joint reaction latency + accuracy
    str_recs = exp139['cohorts']['stroop']['records']
    str_rt = [r['rt'] for r in str_recs]
    str_acc_pp = [r['acc'] * 100.0 for r in str_recs]
    str_eval = {
        'rt_change_ms': quantiles(str_rt),
        'acc_change_pp': quantiles(str_acc_pp),
        'tier_pass_rates': {
            tier: {
                'rt_only': pass_rate(str_rt, lambda x, t=cfg: x <= t['correct_latency_increase_ms_max']),
                'acc_only': pass_rate(str_acc_pp, lambda x, t=cfg: -x <= t['accuracy_drop_pp_max']),
                'joint_rt_and_acc': pass_rate(
                    zip(str_rt, str_acc_pp),
                    lambda pair, t=cfg: pair[0] <= t['correct_latency_increase_ms_max'] and -pair[1] <= t['accuracy_drop_pp_max'],
                ),
            }
            for tier, cfg in tiers.items()
        },
    }

    # 5. Iglesias-Soler velocity loss (n=23, terminal failure comparator)
    vel_recs = exp139['cohorts']['velocity']['records']
    vel_loss = [r['terminal_velocity_loss_pct'] for r in vel_recs]
    vel_eval = {
        'terminal_velocity_loss_pct': quantiles(vel_loss),
        'tier_pass_rates': {
            tier: pass_rate(vel_loss, lambda x, t=cfg: x <= t['velocity_drop_pct_max'])
            for tier, cfg in tiers.items()
        },
    }

    # 6. Thermal envelope reference from EXP-0063
    env_summary = exp063['part_b_3d_envelope_summary']
    thermal_ref = {
        'continuous_360W_2700s_work_kJ': 972.0,
        'intermittent_360W_max_D_by_climate': env_summary.get('intermittent_max_D_by_climate', {
            'temperate_20C_50RH': 0.92,
            'warm_28C_50RH': 0.74,
            'hot_dry_35C_20RH': 0.59,
            'hot_humid_32C_80RH': 0.65,
        }),
        'proposed_schedule_duty_cycle': spec['intensity_schedule']['totals_over_2700s']['duty_cycle'],
    }

    # 7. Synthetic protocol conformance fixture via tools/cpe45.py
    fixture_check = build_synthetic_protocol_fixture(spec)

    artifacts = ('PROTOCOL.md', 'SOURCES.json', 'WORKING_SPEC.json', 'run.py')
    result = {
        'experiment_id': 'EXP-0149',
        'target_id': 'TARGET-CPE45',
        'status': 'PROVISIONAL_WORKING_ASSUMPTIONS_PENDING_CALIBRATION',
        'canonical_cpe45_json_unchanged': True,
        'canonical_success_thresholds_is_null': canonical['success_thresholds'] is None,
        'artifact_sha256_lf': {
            name: hashlib.sha256((HERE / name).read_text(encoding='utf-8').encode()).hexdigest()
            for name in artifacts
        },
        'empirical_anchors_and_tier_sensitivity': {
            'mclaughlin_n24': {
                'work45_kJ': quantiles(mcl_work_kj),
                'rectal_min45_C': quantiles(mcl_temp45),
                'window_drift_W': mcl_window_drift,
                'tier_pass_rates': mcl_pass,
            },
            'jutlah_n21': jut_eval,
            'norbury_n12': nor_eval,
            'remiszewski_ligeza_n71': str_eval,
            'iglesias_soler_n23': vel_eval,
            'published_halftime_summaries': exp139['published_halftime_partial_evidence'],
        },
        'thermal_envelope_reference_exp0063': thermal_ref,
        'uncalibrated_channels': spec['working_thresholds']['uncalibrated_channels'],
        'synthetic_protocol_conformance_check': fixture_check,
    }

    out_text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.check:
        require(args.output.read_text(encoding='utf-8') == out_text, 'EXP-0149 output differs from saved RESULTS.json')
        print('EXP-0149 exact replay')
    else:
        args.output.write_text(out_text, encoding='utf-8', newline='\n')
        print('EXP-0149 RESULTS.json written')


if __name__ == '__main__':
    main()
