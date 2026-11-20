#!/usr/bin/env python3
"""Exploratory leave-one-participant-out sign/lag audit, not physiological validation."""
import argparse
import hashlib
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import openpyxl

HERE = Path(__file__).resolve().parent
SHA256 = 'c38628fa2a682ca784f9254d51c2b373b831f0e39929e3ea8640bdd368db3dcd'
TABLE_SHA256 = 'd58b3e596fb7a5d9d8aa91e511112e7fa4a6e6b98cbe7a3fad2c7d20d518a541'


def run(path, table_path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('unexpected archive hash')
    table_raw = table_path.read_bytes()
    if hashlib.sha256(table_raw).hexdigest() != TABLE_SHA256:
        raise ValueError('unexpected table hash')
    table = openpyxl.load_workbook(io.BytesIO(table_raw), read_only=True, data_only=True).active
    table_rows = {str(row[0]):row for row in table.iter_rows(min_row=3, values_only=True) if row[0]}
    candidates = [(sign, lag) for sign in (-1, 1) for lag in range(-50, 51)]
    records = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith('.xlsx'))
        if len(names) != 21:
            raise ValueError('unexpected participant count')
        for subject, name in enumerate(names):
            wb = openpyxl.load_workbook(io.BytesIO(archive.read(name)), read_only=True, data_only=True)
            if len(wb.sheetnames) != 6:
                raise ValueError('unexpected sheet count')
            for sheet_index, sheet in enumerate(wb):
                rows = []
                ended = False
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    try:
                        values = [float(x) for x in row[:4]]
                        if len(values) != 4 or not all(math.isfinite(x) for x in values):
                            raise ValueError()
                    except (TypeError, ValueError):
                        ended = True
                        continue
                    if ended:
                        raise ValueError('interior missing row')
                    rows.append(values)
                a = np.array(rows)
                if len(a) <= 102 or not np.allclose(np.diff(a[:, 0]), 0.01, atol=1e-6, rtol=0):
                    raise ValueError('insufficient data or irregular time grid')
                start, stop = 50, len(a) - 50
                torque = (a[start:stop-1, 2] + a[start+1:stop, 2]) / 2
                angle_change = np.diff(a[start:stop, 1])
                reference = float(np.sum(torque * angle_change) * np.pi / 180)
                angle_ref = float(np.sum(angle_change))
                estimates = []
                angle_estimates = []
                for sign, lag in candidates:
                    speed = (a[start+lag:stop-1+lag, 3] + a[start+1+lag:stop+lag, 3]) / 2
                    increments = sign * speed * 0.01
                    estimates.append(float(np.sum(torque * increments) * np.pi / 180))
                    angle_estimates.append(float(np.sum(increments)))
                records.append((subject, reference, angle_ref, np.array(estimates), np.array(angle_estimates), sheet_index))
    errors = np.array([abs(r[3]-r[1]) for r in records])
    summaries = {}
    def summary(indices):
        work_error = [float(errors[j, i]) for j, i in enumerate(indices)]
        angle_error = [abs(float(r[4][i]-r[2])) for r, i in zip(records, indices)]
        passes = [e <= 5 and e <= .05*abs(r[1]) for e, r in zip(work_error, records)]
        return {'median_work_error_J':float(np.median(work_error)), 'max_work_error_J':max(work_error),
                'median_angle_error_deg':float(np.median(angle_error)), 'passes':sum(passes), 'segments':len(passes)}
    for sign in (-1, 1):
        index = candidates.index((sign, 0))
        summaries[f'zero_lag_sign_{sign}'] = summary([index]*len(records))
    chosen = []
    selection_counts = {}
    for held_out in range(21):
        training = [j for j, r in enumerate(records) if r[0] != held_out]
        best = int(np.argmin(np.sum(errors[training], axis=0)))
        sign, lag = candidates[best]
        key = f'sign={sign},lag_samples={lag}'
        selection_counts[key] = selection_counts.get(key, 0) + 1
        chosen.extend([(j, best) for j, r in enumerate(records) if r[0] == held_out])
    chosen.sort()
    summaries['lopo'] = summary([index for _, index in chosen])
    group_comparison = {}
    for level in (0, 1):
        group = [j for j, r in enumerate(records) if r[5]//3 == level]
        minus = candidates.index((-1, 0))
        plus = candidates.index((1, 0))
        group_comparison[f'nivo_{level+1}'] = {
            'segments':len(group),
            'zero_lag_minus_sign_lower_error':int(sum(errors[j, minus] < errors[j, plus] for j in group)),
            'zero_lag_plus_sign_lower_error':int(sum(errors[j, plus] < errors[j, minus] for j in group)),
            'median_error_minus_J':float(np.median(errors[group, minus])),
            'median_error_plus_J':float(np.median(errors[group, plus]))}
    opposing_subjects = 0
    signs_by_leg = {'left_minus_right_plus':0, 'left_plus_right_minus':0, 'unresolved':0}
    for subject in range(21):
        best_signs = []
        for level in (0, 1):
            group = [j for j, r in enumerate(records) if r[0] == subject and r[5]//3 == level]
            best_signs.append(-1 if sum(errors[j, minus] for j in group) < sum(errors[j, plus] for j in group) else 1)
        opposing_subjects += best_signs[0] != best_signs[1]
        row = table_rows[f'S{subject+1:03}']
        left, right, int75 = row[5], row[6], row[9]
        if abs(int75-left)<1e-6 and abs(int75-right)>1e-6:
            leg_signs = best_signs
        elif abs(int75-right)<1e-6 and abs(int75-left)>1e-6:
            leg_signs = best_signs[::-1]
        else:
            signs_by_leg['unresolved'] += 1
            continue
        if leg_signs == [-1, 1]:
            signs_by_leg['left_minus_right_plus'] += 1
        elif leg_signs == [1, -1]:
            signs_by_leg['left_plus_right_minus'] += 1
        else:
            signs_by_leg['unresolved'] += 1
    return {'source_sha256':SHA256, 'table_sha256':TABLE_SHA256, 'subjects_in_archive':21, 'segments':len(records),
            'fixed_common_inner_margin_samples':50, 'candidates':len(candidates),
            'lopo_selected_sign_lag_by_fold_count':selection_counts, 'results':summaries,
            'exploratory_nivo_zero_lag_comparison':group_comparison,
            'exploratory_subjects_with_opposite_best_sign_by_nivo':opposing_subjects,
            'exploratory_inferred_leg_signs':signs_by_leg,
            'limits':'Exploratory after observing previous results; common sign/lag does not validate physiological work, article selection or equal-work response.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('table', type=Path)
    args = parser.parse_args()
    result = run(args.archive, args.table)
    out = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    (HERE/'PLANTAR_VELOCITY_RESULTS.json').write_text(out, encoding='utf8', newline='\n')
    print(out)
