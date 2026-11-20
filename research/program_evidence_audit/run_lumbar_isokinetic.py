#!/usr/bin/env python3
"""Source gate and, only when admitted, exploratory participant-held-out prediction."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import openpyxl

HERE = Path(__file__).resolve().parent
SHA256 = '21d242d7ba0e1021fbbdf923851de15079f3ec5d84abce207aba02356b1999e0'
# Original table columns and published Table 1 means in their original units.
COLS = [('age',0,21.43),('height',1,178.06),('weight',2,71.29),('bmi',3,22.45),
        ('fat_pct',4,10.64),('fat_mass',5,7.88),('ffm',6,63.41),
        ('pt_ext_60',7,414.91),('pt_flex_60',8,223.65),('tw_ext_60',9,2033.77),
        ('tw_flex_60',10,1191.21),('ap_ext_60',11,232.64),('ap_flex_60',12,143.80),
        ('pt_ext_240',14,425.89),('pt_flex_240',15,311.81),('tw_ext_240',16,3784.83),
        ('tw_flex_240',17,2030.55),('ap_ext_240',18,357.02),('ap_flex_240',19,167.14),
        ('pap',21,984.17)]


def run(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('input hash mismatch')
    sheet = openpyxl.load_workbook(path,read_only=True,data_only=True).active
    headers = next(sheet.iter_rows(min_row=1,max_row=1,values_only=True))
    rows = [row for row in sheet.iter_rows(min_row=2,values_only=True) if any(v is not None for v in row[:22])]
    invalid = 0
    values = []
    for row in rows:
        try:
            a = [float(row[col]) for _,col,_ in COLS]
            if not all(math.isfinite(x) for x in a):
                raise ValueError()
            values.append(a)
        except (ValueError,TypeError):
            invalid += 1
    duplicates = len(values)-len(set(tuple(row) for row in values))
    comparisons = {}
    for j,(name,_,published) in enumerate(COLS):
        mean = float(np.mean([r[j] for r in values])) if values else None
        comparisons[name] = {'mean':mean,'published':published,'absolute_error':abs(mean-published) if mean is not None else None}
    gate = len(rows)==30 and invalid==0 and duplicates==0 and all(c['absolute_error']<=0.02 for c in comparisons.values())
    result = {'source_sha256':SHA256,'nonempty_data_rows':len(rows),'incomplete_or_nonfinite_rows':invalid,
              'exact_duplicate_rows':duplicates,'nonempty_header_columns':sum(h is not None for h in headers),
              'table1_comparisons':comparisons,'source_gate_passed':gate}
    if not gate:
        result['decision'] = 'STOP: source mismatch; do not fit models or select/exclude rows.'
        return result
    data = np.array(values)
    names = [x[0] for x in COLS]
    y = data[:,names.index('pap')]
    ffm = data[:,names.index('ffm')]
    preds = {'mean':np.zeros(30),'ffm':np.zeros(30),'ffm_pt60':np.zeros(30),'ffm_pt240':np.zeros(30)}
    for held in range(30):
        train = np.arange(30)!=held
        preds['mean'][held] = np.mean(y[train])
        for key,features in [('ffm',[ffm]),('ffm_pt60',[ffm,data[:,names.index('pt_ext_60')]]),
                             ('ffm_pt240',[ffm,data[:,names.index('pt_ext_240')]])]:
            x = np.column_stack([np.ones(30),*features])
            coef = np.linalg.lstsq(x[train],y[train],rcond=None)[0]
            preds[key][held] = x[held]@coef
    errors = {k:np.abs(v-y) for k,v in preds.items()}
    rng = np.random.default_rng(20261120)
    draws = rng.integers(0,30,size=(10000,30))
    contrasts = {}
    for key in ('ffm_pt60','ffm_pt240'):
        d = errors['ffm']-errors[key]
        ci = np.percentile(np.mean(d[draws],axis=1),[2.5,97.5])
        contrasts[key] = {'ffm_minus_model_mae_W':float(np.mean(d)),'bootstrap_95_ci_W':[float(x) for x in ci]}
    ranges = {}
    for speed in (60,240):
        for action in ('ext','flex'):
            lower = data[:,names.index(f'tw_{action}_{speed}')]/(5*data[:,names.index(f'pt_{action}_{speed}')])*180/np.pi
            ranges[f'{action}_{speed}']={'median_conditional_deg':float(np.median(lower)),
                                         'max_conditional_deg':float(np.max(lower)),
                                         'count_above_180':int(np.sum(lower>180))}
    paired = {}
    for metric in ('pt_ext','pt_flex','ap_ext','ap_flex'):
        delta = data[:,names.index(metric+'_240')]-data[:,names.index(metric+'_60')]
        paired[metric] = {'mean_240_minus_60':float(np.mean(delta)),
                          'positive_differences':int(np.sum(delta>0))}
    result.update({'mae_W':{k:float(np.mean(v)) for k,v in errors.items()},'contrasts':contrasts,
                   'both_models_supported':all(v['bootstrap_95_ci_W'][0]>0 for v in contrasts.values()),
                   'conditional_minimum_angular_excursion_deg':ranges, 'descriptive_paired_differences':paired,
                   'limits':'Previously previewed cohort; no post-exercise MVC, time-resolved work, equal-work comparison, independent cohort or CPE45.'})
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('xlsx',type=Path); args = ap.parse_args()
    result = run(args.xlsx)
    out = json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    (HERE/'LUMBAR_ISOKINETIC_RESULTS.json').write_text(out,encoding='utf8',newline='\n')
    print(out)
