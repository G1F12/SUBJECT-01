"""Replay partial FORCE20 and ADAPT25 evidence without changing historical outputs."""
import argparse
import csv
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from pypdf import PdfReader
from scipy.stats import t
from sklearn.linear_model import LinearRegression

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT / 'research/program_evidence_audit'
sys.path[:0] = [str(AUDIT), str(ROOT / 'research/exp0061_multijoint_legpress')]
import run_exp0061_protocol_and_chain as mechanics
from run_adapt25_tissue_trajectory import tendon_capacity

SEED = 451140
DRAWS = 20_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path, normalize=False):
    data = path.read_bytes()
    return hashlib.sha256(data.replace(b'\r\n', b'\n') if normalize else data).hexdigest()


def numeric(value):
    return type(value) in (int, float) and np.isfinite(value)


def resample(values, seed=SEED):
    values = np.asarray(values, dtype=float)
    inds = np.random.default_rng(seed).integers(0, len(values), (DRAWS, len(values)))
    return values[inds]


def estimate(value, boot):
    return {'mean': float(value), 'ci95': np.quantile(boot, [.025, .975]).tolist()}


def summary(values):
    values = np.asarray(values, dtype=float)
    return {'n': len(values), **estimate(values.mean(), resample(values).mean(axis=1))}


def contrast(left, right, *, paired=False, rate=False):
    left, right = np.asarray(left), np.asarray(right)
    lboot = resample(left).mean(axis=1)
    rboot = resample(right, SEED if paired else SEED + 1).mean(axis=1)
    result = {'difference': estimate(left.mean() - right.mean(), lboot - rboot)}
    if rate:
        lower = np.quantile(rboot, .025)
        result.update({'excess_over_1_25_times_comparator': estimate(left.mean() - 1.25 * right.mean(), lboot - 1.25 * rboot),
                       'relative_advantage_pct': None,
                       'positive_comparator_draw_fraction': float(np.mean(rboot > 0)),
                       'denominator_lower_ci_above': {str(m): bool(lower > m) for m in (0, .25, .5)}})
        if lower > 0 and np.all(rboot > 0):
            result['relative_advantage_pct'] = estimate(100 * (left.mean()/right.mean() - 1), 100 * (lboot/rboot - 1))
    return result


def permutation_p(left, right):
    values = np.r_[left, right]
    total = values.sum()
    observed = abs(left.mean() - right.mean())
    n_left, n_right = len(left), len(right)
    differences = []
    for indices in combinations(range(len(values)), n_left):
        left_sum = values[list(indices)].sum()
        differences.append(abs(left_sum/n_left - (total-left_sum)/n_right))
    return float(np.mean(np.asarray(differences) >= observed - 1e-12))


def endpoint(left, right, weeks, randomized=False, paired=False):
    left, right = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    rates = {'pct_baseline_per_week': lambda a: 100 * (a[:, 1]/a[:, 0] - 1)/weeks,
             'source_unit_per_week': lambda a: (a[:, 1] - a[:, 0])/weeks,
             'log_pct_per_week': lambda a: 100 * np.log(a[:, 1]/a[:, 0])/weeks}
    result = {'weeks': weeks, 'left_pre': summary(left[:, 0]), 'right_pre': summary(right[:, 0])}
    for label, calc in rates.items():
        a, b = calc(left), calc(right)
        result[label] = {'left': summary(a), 'right': summary(b),
                         **contrast(a, b, paired=paired, rate=label == 'pct_baseline_per_week')}
        if randomized and label == 'pct_baseline_per_week':
            result[label]['exact_permutation_p_zero_difference'] = permutation_p(a, b)
    result['relative_change_pct'] = {'left': summary(100 * (left[:, 1]/left[:, 0] - 1)),
                                     'right': summary(100 * (right[:, 1]/right[:, 0] - 1))}
    result['ratio_of_group_means_pct_per_week'] = {
        k: 100 * (a[:, 1].mean()/a[:, 0].mean() - 1)/weeks for k, a in [('left', left), ('right', right)]}
    return result


def workbook_rows(path):
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return {sheet.title.strip(): list(sheet.values) for sheet in book}
    finally:
        book.close()


def harden(path):
    sheets = workbook_rows(path)
    results = {}
    for name in ('ISOMETRIC', 'CONCENTRIC', 'ECCENTRIC', 'SQUAT', 'TRADITIONAL'):
        groups = {2: [], 3: []}
        for code, pre, post, delta, pct in sheets[name][1:]:
            if code not in groups:
                continue
            require(numeric(pre) and numeric(post) and min(pre, post) > 0, 'Invalid Harden pair')
            require(np.isclose(delta, post-pre) and np.isclose(pct, 100*(post/pre-1)), 'Inconsistent Harden row')
            groups[code].append((pre, post))
        require(len(groups[2]) == len(groups[3]) == 6, 'Unexpected Harden randomized group sizes')
        # The published traditional-test deltas identify code 2 as AEL and 3 as TRAD.
        if name == 'TRADITIONAL':
            require(all(np.isclose(np.mean(np.diff(groups[code], axis=1)), ref, atol=.01)
                        for code, ref in ((2, 2.93), (3, -1.32))), 'Harden group code mismatch')
        results[name] = {str(w): endpoint(groups[2], groups[3], w, randomized=True) for w in (4, 5, 6)}
    return results


def kay(path):
    rows = workbook_rows(path)['Dataset']
    require(rows[1][1:6:2] == ('Right Limb (Trained)', 'Left Limb (Contralateral)', 'Left Limb'), 'Unexpected Kay limb labels')
    measures = {'isometric_Nm': 'Isometric Torque (Nm)', 'eccentric_Nm': 'Eccentric Torque (Nm)',
                'myoton_Achilles_tone_Hz': 'Achilles Tone (Hz)',
                'myoton_Achilles_stiffness_workbook_units': 'Achilles Stiffness (Nm\u00b7\u00b0-1)'}
    results = {}
    for key, measure in measures.items():
        data = np.array([row[1:7] for row in rows if row[0] == measure], dtype=float)
        require(data.shape == (13, 6) and np.isfinite(data).all() and (data > 0).all(), 'Invalid Kay block')
        results[key] = {'trained_vs_nontraining': endpoint(data[:, :2], data[:, 4:], 6),
                        'trained_vs_contralateral': endpoint(data[:, :2], data[:, 2:4], 6, paired=True)}
    return results


def santos(path):
    rows = workbook_rows(path)['Mechanical+EMG']
    require(rows[1][2] == "PF'", 'Unexpected Santos force header')
    visits = ('W0', 'W2', 'W4', 'POS')
    participants = {}
    person = None
    for subject, visit, force, *_ in rows[2:]:
        if subject is not None:
            person = subject
        if visit in visits and numeric(force) and force > 0:
            record = participants.setdefault(person, {})
            require(person is not None and visit not in record, 'Invalid Santos participant/visit')
            record[visit] = force
    baseline = np.array([r['W0'] for r in participants.values() if 'W0' in r])
    pairs = np.array([[r[k] for k in ('W0', 'POS')] for r in participants.values() if 'W0' in r and 'POS' in r])
    complete = np.array([[r[k] for k in visits] for r in participants.values() if all(k in r for k in visits)])
    require(len(baseline) == len(pairs) == 11 and len(complete) == 10, 'Unexpected Santos roster')
    ref = (baseline.sum() - baseline)/(len(baseline) - 1)
    prior = json.loads((AUDIT / 'GRAVITY_AUDIT_RESULTS.json').read_bytes())
    nominals = {r['pose_deg']: r['force_N'] for r in prior['scenarios'] if r['gravity'] == 'corrected' and r['variant'] == 'baseline'}
    rebuild = json.loads((AUDIT / 'GRAVITY_REBUILD_RESULTS.json').read_bytes())['outputs']
    selected = [r for r in rebuild['tendon_cases'] if r['scenario'] == 'strategy_2_coordinated_chain']
    nominals[140] = next(r['plate_force_bilateral_N'] for r in rebuild['tendon_cases']
                         if r['scenario'] == 'baseline' and r['posture'] == 'extended_140deg_int')
    errors = {}
    for angle in (100, 110, 140):
        error = nominals[angle] - baseline
        errors[str(angle)] = {'model_prediction_N': nominals[angle], 'MAE_N': summary(abs(error)), 'bias_N': summary(error),
                              'LOSO_minus_model_MAE_N': summary(abs(ref - baseline) - abs(error)), 'pose_match': angle == 110}
    weeks = np.arange(4) * 2
    relative = 100 * (complete / complete[:, :1] - 1)
    mean_forces = complete.mean(axis=0)
    days = weeks * 7
    daily = np.arange(43)
    threshold = []
    for trajectory, times, forces in [('observed', days, mean_forces),
                                      ('compressed_1_25', np.r_[days / 1.25, 42], np.r_[mean_forces, mean_forces[-1]])]:
        demands = np.interp(daily, times, forces)
        for delay in (0, 7, 14, 21):
            sf_per_unit_baseline = tendon_capacity(daily, forces[0], tau_delay=delay) / demands
            threshold.append({'trajectory': trajectory, 'delay_days': delay,
                              'day_of_min': int(np.argmin(sf_per_unit_baseline)),
                              'min_sf_at_initial_1_5': float(1.5 * min(sf_per_unit_baseline)),
                              'initial_sf_required': float(1.5/min(sf_per_unit_baseline))})
    return {'baseline_force_N': summary(baseline), 'loso_baseline_MAE_N': summary(abs(ref - baseline)), 'pose_errors': errors,
            'model_tendon_cases': selected, 'end_change_pct_available_pairs': summary(100 * (pairs[:, 1]/pairs[:, 0] - 1)),
            'end_change_N_available_pairs': summary(pairs[:, 1] - pairs[:, 0]),
            'complete_baseline_and_followup_mean_N': mean_forces.tolist(),
            'early_weekly_gain_pct': summary(relative[:, 1]/2), 'end_weekly_gain_pct': summary(relative[:, -1]/6),
            'linear_weekly_gain_pct': summary(np.polyfit(weeks, relative.T, 1)[0]),
            'tissue_sensitivity': threshold, 'active_comparator': False}


def dpvalid(path):
    raw = pd.read_csv(path).query("action == 'extension'").copy()
    require(not raw.duplicated(['participant_id', 'angle_deg', 'rep']).any(), 'Duplicate DPValid trial')
    require(set(raw.angle_deg) == {75, 90} and raw.participant_id.nunique() == 20, 'Unexpected DPValid cohort')
    fields = ['participant_id', 'angle_deg', 'mass', 'height', 'sex']
    condition = raw.groupby(fields, as_index=False)['torque_nm'].mean()
    require(len(condition) == 40, 'Inconsistent DPValid covariates or missing posture')
    results = {}
    for label, frame in [('condition_weighted', condition), ('trial_weighted', raw)]:
        data = frame.assign(sex_code=(frame.sex == 'M').astype(int)).copy()
        data['g'] = [mechanics.quad_volume_cm3(m, h, s) / mechanics.L_FASCICLE_QUAD_CM
                     * np.cos(np.deg2rad(mechanics.THETA_QUAD_BASE_DEG)) * mechanics.A_ACT_MAX
                     * mechanics.patellar_moment_arm_m(a) * mechanics.quad_force_length_multiplier(a)
                     for m, h, s, a in zip(data.mass, data.height, data.sex, data.angle_deg)]
        predictions = []
        covariates = ['mass', 'height', 'sex_code', 'angle_deg']
        for person in sorted(data.participant_id.unique()):
            train = data[data.participant_id != person]
            test = data[data.participant_id == person].copy()
            test['M2'] = test.g * ((train.g @ train.torque_nm)/(train.g @ train.g))
            test['F0'] = LinearRegression().fit(train[covariates], train.torque_nm).predict(test[covariates])
            test['mean_by_angle'] = test.angle_deg.map(train.groupby('angle_deg').torque_nm.mean())
            predictions.append(test[['participant_id', 'angle_deg', 'torque_nm', 'M2', 'F0', 'mean_by_angle']])
        pred = pd.concat(predictions).groupby(['participant_id', 'angle_deg'], as_index=False).mean()
        results[label] = {}
        for angle, section in [('75', pred[pred.angle_deg == 75]), ('90', pred[pred.angle_deg == 90]), ('pooled', pred)]:
            y = section.torque_nm.to_numpy().reshape(20, -1)
            errors = {k: section[k].to_numpy().reshape(20, -1) - y for k in ('M2', 'F0', 'mean_by_angle')}
            metrics = {name: {'MAE_Nm': summary(abs(e).mean(axis=1)), 'bias_Nm': summary(e.mean(axis=1))}
                       for name, e in errors.items()}
            for name in ('F0', 'mean_by_angle'):
                metrics[name]['paired_MAE_minus_M2_Nm'] = summary((abs(errors[name]) - abs(errors['M2'])).mean(axis=1))
            numerator = (errors['F0']**2 - errors['M2']**2).sum(axis=1)
            ys = resample(y).reshape(DRAWS, -1)
            boot_denominator = ((ys - ys.mean(axis=1, keepdims=True))**2).sum(axis=1)
            metrics['delta_r2_M2_over_F0'] = estimate(numerator.sum()/((y-y.mean())**2).sum(),
                                                       resample(numerator).sum(axis=1)/boot_denominator)
            results[label][angle] = metrics
    return results


def oc(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    require(len({r['FP'] for r in rows}) == len(rows) == 32, 'Unexpected OC roster')
    results = {}
    for group in ('NOC', 'OCU'):
        subset = [r for r in rows if r['Group'] == group]
        results[group] = {}
        for pre, post in [('KE_MIVC_PRE', 'KE_MIVC_POST'), ('Stiffness_PRE', 'Stiffness_POST'),
                          ('PT_CSA_mean_PRE', 'PT_CSA_mean_POST')]:
            pairs = np.array([(float(r[pre]), float(r[post])) for r in subset if r[pre] and r[post]])
            require(np.isfinite(pairs).all() and (pairs > 0).all(), 'Invalid OC outcome')
            results[group][pre] = summary(100 * (pairs[:, 1]/pairs[:, 0] - 1))
        paired = [r for r in subset if r['Stiffness_PRE'] and r['Stiffness_POST']]
        results[group]['MIVC_change_pct_in_stiffness_sample'] = summary(
            [100 * (float(r['KE_MIVC_POST'])/float(r['KE_MIVC_PRE']) - 1) for r in paired])
    return results


def mannarino(path):
    sheets = workbook_rows(path)
    mvc, thickness, wave = (sheets[name] for name in ('MVC + MT', 'PTT', 'SSI'))
    require(mvc[1][1] == 'MVC_pre (direita)' and thickness[0][5] == 'PR\u00c9 DIREITO'
            and wave[0][0] == 'PRE' and wave[19][0] == 'POST', 'Unexpected Mannarino worksheet')

    def pairs(rows, cols):
        kept = {}
        for row in rows:
            person, pre, post = [row[i] for i in cols]
            if numeric(pre) and numeric(post) and min(pre, post) > 0:
                require(person not in kept, 'Duplicate Mannarino participant')
                kept[person] = 100 * (post/pre - 1)
        return kept

    right_mvc = pairs(mvc[2:17], (0, 1, 3))
    right_ptt = pairs(thickness[2:17], (0, 5, 15))
    require(len(right_mvc) == 15 and len(right_ptt) == 14, 'Unexpected Mannarino counts')
    require(all(a[1] == b[1] for a, b in zip(wave[2:17], wave[21:36])), 'Mannarino SWE ID mismatch')
    swe = pairs([(a[1], a[25], b[26]) for a, b in zip(wave[2:17], wave[21:36])], (0, 1, 2))
    shared = sorted(right_mvc.keys() & right_ptt.keys() & swe.keys())
    return {'MVC_relative_change_pct': summary(list(right_mvc.values())),
            'PT_thickness_relative_change_pct': summary(list(right_ptt.values())),
            'PT_shear_elastography_relative_change_pct': summary(list(swe.values())),
            'MVC_relative_change_pct_in_same_tissue_sample': summary([right_mvc[p] for p in shared]),
            'comparison_group': False}


def zushi(path):
    ids, forces = [], []
    for page in PdfReader(path).pages:
        for line in page.extract_text(extraction_mode='layout').splitlines():
            if re.fullmatch(r'\s*\d+\s+(?:-?\d+(?:\.\d+)?\s+){9}-?\d+(?:\.\d+)?\s*', line):
                fields = line.split()
                ids.append(int(fields[0]))
                forces.append(float(fields[6]))
    require(ids == list(range(1, 231)), 'Incomplete or duplicated Zushi PDF rows')
    return {'unilateral_peak_N_kg': summary(forces), 'range_N_kg': [min(forces), max(forces)],
            'absolute_force_or_individual_mass_available': False}


def walker(summaries):
    def interval(group_a, group_b, multiplier):
        a, sa, na = group_a
        b, sb, nb = group_b
        va, vb = sa**2 / na, (multiplier * sb)**2 / nb
        df = (va + vb)**2 / (va**2/(na - 1) + vb**2/(nb - 1))
        diff = a - multiplier * b
        radius = t.ppf(.975, df) * np.sqrt(va + vb)
        return {'mean': float(diff/10), 'ci95': [float((diff-radius)/10), float((diff+radius)/10)]}

    return {outcome: {'AEL_minus_TRAD_pct_per_week': interval(groups[0], groups[1], 1),
                      'AEL_minus_1_25_TRAD_pct_per_week': interval(groups[0], groups[1], 1.25)}
            for outcome, groups in summaries.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT / 'tmp')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    meta = json.loads((HERE / 'SOURCES.json').read_bytes())
    outcomes = {}
    for name, analyze in [('harden', harden), ('kay', kay), ('santos', santos), ('dpvalid', dpvalid),
                          ('oc', oc), ('mannarino', mannarino), ('zushi', zushi)]:
        source = meta['inputs'][name]
        folder = ROOT if source.get('in_repository') else args.data_root
        path = folder / source['path']
        require(sha(path, source.get('normalize_lf', False)) == source['sha256'], f'Source hash mismatch: {path}')
        outcomes[name] = analyze(path)
    outcomes['walker_published_group_summaries'] = walker(meta['walker_10_training_weeks_mean_sd_n'])
    dependencies = [HERE / name for name in ('SOURCES.json', 'PROTOCOL.md', 'run.py')]
    dependencies += [AUDIT / name for name in ('GRAVITY_AUDIT_RESULTS.json', 'GRAVITY_REBUILD_RESULTS.json', 'run_adapt25_tissue_trajectory.py')]
    dependencies += [Path(mechanics.__file__)]
    result = {'experiment_id': 'EXP-0140', 'stage_verdict': 'NO_PATH_READY_FOR_COMPATIBILITY',
              'bootstrap': {'seed': SEED, 'draws': DRAWS, 'unit': 'participant'}, 'analyses': outcomes,
              'dependencies_sha256_lf': {p.relative_to(ROOT).as_posix(): sha(p, True) for p in dependencies}}
    rendered = json.dumps(result, indent=2, allow_nan=False) + '\n'
    output = HERE / 'RESULTS.json'
    if args.check:
        require(output.read_text(encoding='utf-8') == rendered, 'Saved results differ')
        print('EXP-0140 results reproduced')
    else:
        output.write_text(rendered, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
