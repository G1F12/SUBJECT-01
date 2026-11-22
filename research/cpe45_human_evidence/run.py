"""Reproduce the participant-paired CPE45 partial evidence audit."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from statistics import mean

import numpy as np
from openpyxl import load_workbook
from scipy.stats import t

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'mclaughlin': ('mclaughlin_29120024.xlsx', '499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531'),
    'jutlah': ('recovery_raw/Power_rawdata.xlsx', 'b5cb03007190a63dae6a118a7a604cd906273f93febf42957a2e7799df16da20'),
    'norbury': ('norbury_24156741.xlsx', '295cbe90ebb84e7bfa3cd2804d81f87663b16088bdc06021256343d6f57acb9e'),
    'stroop': ('cpe45_human/task2.tab', '11e53a0d89651a1851c496c5061a675f0744904c1b627f6065146e553d80c9fc'),
    'velocity': ('cpe45_human/leg.csv', '9283595449be5d7a3ed1641d2ba1f6919288907805df9888098680df022bd3ad'),
}


def require(condition, description):
    if not condition:
        raise ValueError(description)


def finite(value):
    return type(value) in (int, float) and np.isfinite(value)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate key: {key}')
        result[key] = value
    return result


def summarize(values):
    values = np.asarray(list(values), dtype=float)
    if not len(values):
        return {'n': 0, 'mean': None, 'ci95': None}
    require(np.isfinite(values).all(), 'Non-finite summary input')
    draws = np.random.default_rng(451139).integers(0, len(values), (10000, len(values)))
    return {'n': len(values), 'mean': float(values.mean()),
            'ci95': np.quantile(values[draws].mean(axis=1), [.025, .975]).tolist()}


def sensitivity(summary, margins):
    if summary['ci95'] is None:
        return {}
    lo, hi = summary['ci95']
    return {str(m): 'below' if hi < m else 'above' if lo > m else 'overlaps' for m in margins}


def group(records, key):
    return summarize(row[key] for row in records if row[key] is not None)


def mclaughlin(path):
    with path.open('rb') as stream:
        book = load_workbook(stream, read_only=True, data_only=True)
        temp, power, env = [list(book[name].values) for name in ('Core Temp', 'Exercise Data', 'Environmental Conditions')]
    require((temp[0][2], temp[0][27], power[0][77]) == ('Rectal', 'CORE', 'Wattage'), 'Unexpected McLaughlin channels')

    def columns(rows, start, stop):
        return unique((rows[1][i], i) for i in range(start, stop) if type(rows[1][i]) is int)

    rectal_col, core_col = columns(temp, 2, 27), columns(temp, 27, 51)
    power_col, air_col, rh_col = columns(power, 77, 101), columns(env, 2, 27), columns(env, 27, 51)
    temperatures = unique((r[1], r) for r in temp[2:] if type(r[1]) is int)
    watts = unique((int(r[1].split('-')[0]) + 1 if isinstance(r[1], str) else r[1], r)
                   for r in power[2:] if type(r[1]) is int or re.fullmatch(r'\d+-\d+', str(r[1])))
    require(set(range(1, 46)) <= watts.keys(), 'Missing minute labels')
    require(all(type(watts[m][1]) is int or watts[m][1] == f'{m-1}-{m}' for m in range(1, 46)), 'Non-minute width')
    climate = unique((r[1], r) for r in env[2:] if r[1] is not None)['5-6']

    def get(row, mapping, person):
        value = row[mapping[person]] if person in mapping else None
        return value if finite(value) else None

    records = []
    for person in sorted(rectal_col.keys() | power_col.keys()):
        watts_45 = [get(watts[m], power_col, person) for m in range(1, 46)]
        valid_watts = [v if v is not None and 0 <= v <= 600 else None for v in watts_45]
        measured = [v for v in valid_watts if v is not None]
        base = get(temperatures[1], rectal_col, person)
        row = {'participant': person, 'rectal_min1_C': base, 'observed_work_J': 60 * sum(measured),
               'n_power_minutes': len(measured), 'work45_J': 60 * sum(measured) if len(measured) == 45 else None,
               'air_min5_6_C': get(climate, air_col, person), 'rh_min5_6_pct': get(climate, rh_col, person)}
        for m in (30, 45, 60):
            value = get(temperatures[m], rectal_col, person)
            core = get(temperatures[m], core_col, person)
            row[f'rectal_min{m}_C'] = value
            row[f'rectal_change_min{m}_C'] = value - base if base is not None and value is not None else None
            row[f'core_bias_min{m}_C'] = core - value if core is not None and value is not None else None
        for width in (5, 9, 11):
            early, late = valid_watts[:width], valid_watts[-width:]
            row[f'late_minus_early_{width}min_W'] = mean(late) - mean(early) if None not in early + late else None
        row['max_measured_W'] = max(measured, default=None)
        records.append(row)
    max_power = max(r['max_measured_W'] for r in records if r['max_measured_W'] is not None)
    candidates = [r for r in records if r['n_power_minutes']]
    return {'records': records, 'summaries': {key: group(records, key) for key in records[0] if key != 'participant'},
            'missing_work_bounds_mean_J': [mean(r['observed_work_J'] for r in candidates),
                                          mean(r['observed_work_J'] + 60 * max_power * (45 - r['n_power_minutes']) for r in candidates)],
            'missing_work_bounds_n': len(candidates), 'bound_W': max_power}


def jutlah(path):
    with path.open('rb') as stream:
        book = load_workbook(stream, read_only=True, data_only=True)
        data = {}
        for rest, visit in ((12, 4), (18, 3), (24, 2)):
            for metric in ('Peak', 'Avg', 'TW'):
                rows = iter(book[f'{metric}_{rest}'].values)
                require(next(rows)[1:11] == tuple(f's{i}' for i in range(1, 11)), 'Unexpected sprint columns')
                data[rest, metric] = unique((r[0].split('_')[0], [v if finite(v) and v > 0 else None for v in r[1:11]])
                                            for r in rows if re.fullmatch(rf'WTR\d{{2}}_{visit} power\.xlsx', str(r[0])))
                require(len(data[rest, metric]) == 21, 'Unexpected participant roster')
    ids = sorted(data[12, 'Peak'])
    require(all(set(series) == set(ids) for series in data.values()), 'Inconsistent participant IDs')
    records, summaries = [], {}
    for rest in (12, 18, 24):
        sessions = []
        for person in ids:
            peak, avg, work = (data[rest, metric][person] for metric in ('Peak', 'Avg', 'TW'))
            session = {'participant': person, 'rest_s': rest, 'main_duration_s': 60 + 9 * rest,
                       'sprint_work_J': sum(work) if None not in work else None}
            for metric, values in (('peak_W', peak), ('work_J', work), ('published_avg_W', avg)):
                for width in (1, 2, 3):
                    first, last = values[:width], values[-width:]
                    session[f'{metric}_loss_pct_{width}'] = (100 * (1 - mean(last) / mean(first))
                                                              if None not in first + last else None)
                    session[f'{metric}_late_minus_early_{width}'] = mean(last) - mean(first) if None not in first + last else None
                    pairs = [(a, b) for a, b in zip(first, last) if a is not None and b is not None]
                    session[f'{metric}_available_loss_pct_{width}'] = (100 * (1 - mean(b for a, b in pairs) / mean(a for a, b in pairs))
                                                                        if pairs else None)
            session['work_derived_minus_published_avg_W'] = mean(a / 6 - b for a, b in zip(work, avg)) if None not in work + avg else None
            session['next_minus_previous_peak_W'] = [b-a if a is not None and b is not None else None for a, b in zip(peak, peak[1:])]
            session['next_over_previous_peak'] = [b/a if a is not None and b is not None else None for a, b in zip(peak, peak[1:])]
            sessions.append(session)
        numeric_fields = [key for key in sessions[0] if 'loss_pct' in key or 'late_minus_early' in key or key in ('sprint_work_J', 'work_derived_minus_published_avg_W')]
        summary = {key: group(sessions, key) for key in numeric_fields}
        summary['loss_sensitivity'] = {k: sensitivity(summary[k], (3, 5, 10)) for k in numeric_fields if 'loss_pct' in k}
        summary['transitions_W'] = [summarize(r['next_minus_previous_peak_W'][i] for r in sessions
                                                if r['next_minus_previous_peak_W'][i] is not None) for i in range(9)]
        summaries[str(rest)] = summary
        records.extend(sessions)
    short, long = (unique((r['participant'], r) for r in records if r['rest_s'] == rest) for rest in (12, 24))
    contrasts = {key: summarize(long[p][key] - short[p][key] for p in ids if None not in (long[p][key], short[p][key]))
                 for key in ('sprint_work_J', 'peak_W_loss_pct_2', 'work_J_loss_pct_2')}
    contrasts['transitions_W'] = [summarize(long[p]['next_minus_previous_peak_W'][i] - short[p]['next_minus_previous_peak_W'][i]
                                          for p in ids if None not in (long[p]['next_minus_previous_peak_W'][i], short[p]['next_minus_previous_peak_W'][i]))
                                 for i in range(9)]
    return {'records': records, 'summaries_by_rest_s': summaries, 'paired_24_minus_12': contrasts}


def norbury(path):
    with path.open('rb') as stream:
        book = load_workbook(stream, read_only=True, data_only=True)
        mvc = list(book['MVC'].values)
        press = list(book['Leg Press Data'].values)
    delays = (300, 2700, 86400)
    records, summaries = [], {}
    for condition, index, leg_index in (('LL', 5, 3), ('HL', 21, 19)):
        require(mvc[index-1][2:6] == ('Pre', '5 min', '45 min', '24 hour'), 'Unexpected MVC header')
        loads = unique((r[1], r[13]) for r in press[leg_index:leg_index + 12])
        series = unique((r[1], r[2:6]) for r in mvc[index:index + 12])
        require(set(series) == set(loads) == set(range(1, 13)), 'MVC participant mismatch')
        sessions = []
        for person, (pre, *post) in sorted(series.items()):
            require(finite(pre) and pre > 0 and all(finite(v) and v > 0 for v in post), 'Invalid MVC')
            row = {'participant': person, 'condition': condition, 'load_kg': loads[person], 'pre_N': pre,
                   'post_N': dict(zip(map(str, delays), post)), 'actual_individual_delay_s': None}
            for delay, value in zip(delays, post):
                row[f'change_{delay}s_N'] = value - pre
                row[f'loss_{delay}s_pct'] = 100 * (1 - value / pre)
            sessions.append(row)
        records.extend(sessions)
        summaries[condition] = {key: group(sessions, key) for key in sessions[0] if key.startswith(('change_', 'loss_'))}
        summaries[condition]['loss_sensitivity'] = {key: sensitivity(result, (5, 10)) for key, result in summaries[condition].items() if key.startswith('loss_')}
        summaries[condition]['paired_change_300_to_2700_pp'] = summarize(r['loss_300s_pct'] - r['loss_2700s_pct'] for r in sessions)
    return {'records': records, 'summaries': summaries, 'nominal_post_delay_s': list(delays)}


def stroop(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = unique((r['id'], r) for r in csv.DictReader(stream, delimiter='\t'))
    records = []
    for person, r in sorted(rows.items()):
        row = {'participant': person, 'order': r['order']}
        for metric in ('rt', 'acc'):
            session = {}
            for s in ('ex_pre', 'ex_post', 're_pre', 're_post'):
                categories = ('neg', 'pos', 'neu')
                values = [float(r[f'{metric}_{c}_{s}']) for c in categories]
                counts = [float(r[f'n_{c}_{s}']) for c in categories]
                require(all(v.is_integer() and v > 0 for v in counts), 'Invalid trial count')
                require(all(np.isfinite(v) and (v > 0 if metric == 'rt' else 0 <= v <= 1)
                            for v in values), 'Invalid Stroop outcome')
                session[s] = mean(values)
            row[metric] = session['ex_post'] - session['ex_pre'] - (session['re_post'] - session['re_pre'])
        records.append(row)
    return {'records': records, 'post_delay_s': None, 'summary': {k: group(records, k) for k in ('rt', 'acc')},
            'order_sensitivity': {order: {k: group([r for r in records if r['order'] == order], k) for k in ('rt', 'acc')}
                                  for order in sorted({r['order'] for r in records})}}


def velocity(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        data = list(csv.DictReader(stream, delimiter=';'))
    grouped = {}
    for row in data:
        def value(key):
            return float(row[key].replace(',', '.'))
        subject, progress, loss = int(row['Subject']), value('PercMNR'), value('PercVL')
        require(0 <= progress <= 100 and np.isfinite(loss), 'Invalid velocity observation')
        grouped.setdefault(subject, []).append((progress, loss))
    records = []
    for person, observations in sorted(grouped.items()):
        end = [loss for progress, loss in observations if np.isclose(progress, 100)]
        require(len(end) == 1, f'Ambiguous final leg press repetition for {person}')
        records.append({'participant': person, 'terminal_velocity_loss_pct': end[0]})
    result = group(records, 'terminal_velocity_loss_pct')
    return {'records': records, 'summary': result, 'exploratory_loss_sensitivity': sensitivity(result, (5, 10))}


def published_halftime(sources):
    results = []
    for row in sources['published_halftime_summaries']:
        n = row['n']
        center = row['loss_mean_pct']
        radius = float(t.ppf(.975, n - 1)) * row['loss_sd_pct'] / n ** .5
        interval = [center - radius, center + radius]
        results.append({**row, 'approximate_ci95_from_rounded_summary': interval,
                        'exploratory_loss_sensitivity': sensitivity({'ci95': interval}, (5, 10))})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=ROOT / 'tmp')
    parser.add_argument('--output', type=Path, default=HERE / 'RESULTS.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    results = {}
    for name, analyze in (('mclaughlin', mclaughlin), ('jutlah', jutlah), ('norbury', norbury), ('stroop', stroop), ('velocity', velocity)):
        relative, expected = INPUTS[name]
        path = args.data_root / relative
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'SHA-256 mismatch: {path}')
        results[name] = {'source_sha256': expected, **analyze(path)}
    artifacts = ('PROTOCOL.md', 'SOURCES.json', 'run.py')
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    result = {'experiment_id': 'EXP-0139', 'target_id': 'TARGET-CPE45', 'verdict': 'NOT_CONFIRMED_PARTIAL_EVIDENCE',
              'joint_admitted_cohorts': 0, 'canonical_thresholds_approved': False,
              'artifact_sha256_lf': {name: hashlib.sha256((HERE / name).read_text(encoding='utf-8').encode()).hexdigest() for name in artifacts},
              'bootstrap': {'seed': 451139, 'draws': 10000, 'unit': 'participant'}, 'cohorts': results,
              'published_halftime_partial_evidence': published_halftime(sources)}
    output = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.check:
        require(args.output.read_text(encoding='utf-8') == output, 'Result differs from saved output')
        print('CPE45 results reproduced')
    else:
        args.output.write_text(output, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
