"""Follow-up stage 1 audit from frozen public articles, figures, and EXP-0090."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree

from bs4 import BeautifulSoup
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects, label
from scipy.stats import t

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REBUILD = ROOT / 'research/program_evidence_audit/GRAVITY_REBUILD_RESULTS.json'
SEED = 451141


def sha(path, *, lf=False):
    data = path.read_bytes()
    return hashlib.sha256(data.replace(b'\r\n', b'\n') if lf else data).hexdigest()


def interval(center, se, df):
    radius = t.ppf(.975, df) * se
    return {'estimate': float(center), 'ci95': [float(center-radius), float(center+radius)]}


def mean_ci(mean, sd, n):
    return interval(mean, sd / np.sqrt(n), n - 1)


def welch(a, b, w=1):
    ma, sa, na = a
    mb, sb, nb = b
    va, vb = sa**2/na, (w*sb)**2/nb
    df = (va + vb)**2 / (va**2/(na - 1) + vb**2/(nb - 1))
    return interval(ma - w*mb, np.sqrt(va + vb), df)


def values(cell):
    return [float(re.sub(r'\s', '', x))
            for x in re.findall(r'-?\s*\d+(?:\.\d+)?', cell.replace('\u2212', '-'))]


def walker(folder, source):
    root = ElementTree.parse(folder / 'walker2020.xml').getroot()
    rows = {}
    for row in root.find(".//table-wrap[@id='Tab1']").iter('tr'):
        cells = [''.join(cell.itertext()) for cell in row]
        if len(cells) == 10:
            rows[cells[0].strip()] = cells[1:]
    mvc = rows['MVC (Nm)']
    changes = dict(zip(('AEL', 'TRAD', 'CON'), [values(mvc[i])[:2] for i in (2, 5, 8)]))
    late = source['walker_late_mvc_pct_mean_sd_n']
    outcomes = {}
    for label_, inputs, windows in [('whole', changes, (10, 11, 12)), ('late', late, (5,))]:
        outcomes[label_] = {}
        for weeks in windows:
            arms = {k: (vals[0]/weeks, vals[1]/weeks, 10 if k != 'CON' else 8) for k, vals in inputs.items()}
            a, b = arms['AEL'], arms['TRAD']
            result = {**{k: mean_ci(*v) for k, v in arms.items()},
                      'AEL_minus_TRAD': welch(a, b), 'AEL_minus_1_25_TRAD': welch(a, b, 1.25)}
            # Bound published rounding of the input mean and SD for the threshold contrast.
            half_steps_a = (.05, .05) if label_ == 'whole' else (.5, .5)
            half_steps_b = (.05, .05) if label_ == 'whole' else (.05, .5)
            candidates = [welch((a[0]+i*half_steps_a[0]/weeks, a[1]+j*half_steps_a[1]/weeks, a[2]),
                                (b[0]+k*half_steps_b[0]/weeks, b[1]+l*half_steps_b[1]/weeks, b[2]), 1.25)['ci95']
                          for i in (-1, 1) for j in (-1, 1) for k in (-1, 1) for l in (-1, 1)]
            result['rounding_outer_interval'] = [min(c[0] for c in candidates), max(c[1] for c in candidates)]
            if 'CON' in arms:
                result['AEL_minus_CON'] = welch(a, arms['CON'])
            outcomes[label_][str(weeks)] = result
    tissue = {}
    for metric, cells in rows.items():
        if metric.startswith(('Absolute (N', 'Relative (N', 'Hysteresis')):
            a, b = [values(cells[i])[:2] for i in (2, 5)]
            # Data table does not disclose the endpoint-specific N. Figure 4 has overlap.
            tissue[metric] = {f'{na}_AEL_{nb}_TRAD': welch((*a, na), (*b, nb))
                              for na, nb in ((10, 10), (8, 9), (8, 8))}
            tissue[metric]['group_paired_change_pct_mean_sd'] = {'AEL': a, 'TRAD': b}
    return {'mvc_rate_pct_baseline_per_week': outcomes, 'tissue': tissue,
            'published_pairing': 'same cohort, unlabeled figures and group summaries; no individual crosswalk',
            'linked_stiffness_full_trajectory': False}


def massey(folder, sizes):
    article = BeautifulSoup((folder / 'massey.html').read_bytes(), 'html.parser')
    first_table = article.select_one('table')
    desired = {
        'Maximum voluntary torque (MVT), Nm': 'MVT',
        'Stiffness, N.mm': None,
        'Strain at 80% pre-MVT, %': 'free_tendon_strain_pct',
    }
    table = {}
    stiffness_keys = iter(('free_tendon_stiffness_N_mm', 'aponeurosis_complex_stiffness_N_mm'))
    for row in first_table.find_all('tr'):
        cells = [cell.get_text(' ', strip=True) for cell in row.find_all('td')]
        if len(cells) < 5:
            continue
        key = next((desired[k] if desired[k] is not None else next(stiffness_keys)
                    for k in desired if cells[0].startswith(k)), '')
        if key:
            table[key] = np.array([values(x)[:2] for x in cells[1:5]]).reshape(2, 2, 2)
    if set(table) != {'MVT', 'free_tendon_strain_pct', 'free_tendon_stiffness_N_mm', 'aponeurosis_complex_stiffness_N_mm'}:
        raise ValueError('Massey Table 1 changed')
    result = {}
    for endpoint, data in table.items():
        n = sizes['MVT' if endpoint == 'MVT' else 'aponeurosis_complex' if endpoint.startswith('aponeurosis_') else 'free_tendon']
        # Relative strength contrast is scaled by group baseline mean, treated as fixed here.
        scaling = 100 / data[:, 0, 0] / 12 if endpoint == 'MVT' else np.ones(2)
        delta = (data[:, 1, 0] - data[:, 0, 0]) * scaling
        result[endpoint] = {'ECT_and_SCT_pre_post_mean_sd': data.tolist(), 'sensitivity': {}}
        for rho in (-1, 0, .5, .9, 1):
            change_sd = np.sqrt(data[:, 0, 1]**2 + data[:, 1, 1]**2 - 2*rho*data[:, 0, 1]*data[:, 1, 1]) * scaling
            ect, sct = zip(delta, change_sd, n)
            result[endpoint]['sensitivity'][str(rho)] = {
                'ECT': mean_ci(*ect), 'SCT': mean_ci(*sct), 'SCT_minus_ECT': welch(sct, ect),
                **({'SCT_minus_1_25_ECT': welch(sct, ect, 1.25)} if endpoint == 'MVT' else {})}
    return result


def population_check(pred, observed):
    mean, sd, n = observed
    bias = pred - mean
    rmse_model = np.sqrt((n-1)/n*sd**2 + bias**2)
    rmse_loso = np.sqrt(n/(n-1))*sd
    # Jensen bounds absolute error below by absolute bias and above by RMS error.
    return {'n': n, 'observed_peak_N': mean_ci(mean, sd, n), 'fixed_baseline_model_prediction_N': pred,
            'model_minus_observed_bias_N': mean_ci(bias, sd, n), 'model_RMSE_N': float(rmse_model),
            'LOSO_mean_RMSE_N': float(rmse_loso), 'MAE_model_lower_bound_N': abs(bias),
            'MAE_LOSO_upper_bound_N': float(rmse_loso),
            'MAE_LOSO_advantage_guaranteed_in_sample': bool(abs(bias) > rmse_loso)}


def zoger_markers(path, angle):
    # Coordinates are for the hashed full-resolution figure. Solid, isolated squares only.
    settings = {100: (250, 570, 160, 254, (163, 1000, 524, 4000), (72, 1000, 331, -1000)),
                140: (245, 565, 590, 806, (166, 2000, 589, 8000), (580, 1000, 841, -1000))}
    x0, x1, y0, y1, xticks, yticks = settings[angle]
    with Image.open(path) as figure:
        if figure.size != (2008, 948):
            raise ValueError('Unexpected raster dimensions')
        raster = np.asarray(figure.convert('L'))
    blobs, _ = label(raster[y0:y1, x0:x1] < 60)
    centers = []
    for index, (rows, columns) in enumerate(find_objects(blobs), 1):
        height, width = rows.stop - rows.start, columns.stop - columns.start
        if 7 <= width <= 10 and 7 <= height <= 10 and 61 <= np.count_nonzero(blobs[rows, columns] == index) <= 82:
            centers.append((x0 + (columns.start + columns.stop - 1)/2, y0 + (rows.start + rows.stop - 1)/2))
    xy = np.array(centers)

    def transform(p, ticks):
        pix0, val0, pix1, val1 = ticks
        return val0 + (p-pix0)*(val1-val0)/(pix1-pix0)

    avg, diff = transform(xy[:, 0], xticks), transform(xy[:, 1], yticks)
    return xy, avg + diff/2, avg - diff/2


def paired_errors(s2, s3, pred):
    def compare(model, y):
        loso = (y.sum() - y)/(len(y)-1)
        return abs(loso-y)-abs(model-y)

    delta = compare(pred, s3)
    ix = np.random.default_rng(SEED).integers(0, len(delta), (20000, len(delta)))
    delta_persistence = abs(s2-s3)-abs(pred-s3)
    # +/-25 N independently on each ordinate: difference in the two MAEs has a <= 50 N envelope.
    return {'model_MAE_N': float(abs(pred-s3).mean()), 'model_bias_N': float((pred-s3).mean()),
            'LOSO_MAE_N': float(abs((s3.sum()-s3)/(len(s3)-1)-s3).mean()),
            'persistence_S2_to_S3_MAE_N': float(abs(s2-s3).mean()),
            'LOSO_minus_model_MAE_N': {'estimate': float(delta.mean()), 'ci95': np.quantile(delta[ix].mean(axis=1), [.025, .975]).tolist()},
            'LOSO_minus_model_center_pixel_error_envelope_N': [float(delta.mean()-50), float(delta.mean()+50)],
            'persistence_minus_model_MAE_N': {'estimate': float(delta_persistence.mean()),
                                               'ci95': np.quantile(delta_persistence[ix].mean(axis=1), [.025, .975]).tolist()}}


def force(folder, source):
    archive = json.loads(REBUILD.read_bytes())['outputs']['tendon_cases']
    cases = {angle: [r for r in archive if r['posture'].endswith(f'{angle}deg_int')] for angle in (100, 140)}
    baseline = {angle: next(r['plate_force_bilateral_N'] for r in rows if r['scenario'] == 'baseline')
                for angle, rows in cases.items()}
    observed = source['zoger_force_mean_sd_n']
    result = {}
    for angle in (100, 140):
        table = observed[str(angle)]
        xy, s2, s3 = zoger_markers(folder / 'zoger_fig2.png', angle)
        if not 12 <= len(xy) < table['S3'][2]:
            raise ValueError('Unexpected count of isolated squares')
        result[str(angle)] = {'full_sample': {session: population_check(baseline[angle], table[session]) for session in ('S2', 'S3')},
                              'full_sample_S2_minus_S3_N': mean_ci(*table['S2_minus_S3']),
                              'parsed_marker_count': len(xy), 'centers_pixels': xy.tolist(),
                              'digitized_only_S2_mean_N': float(s2.mean()), 'digitized_only_S3_mean_N': float(s3.mean()),
                              'digitized_only_S2_minus_S3_mean_N': float((s2-s3).mean()),
                              'subset_prediction_compare': paired_errors(s2, s3, baseline[angle])}
    return {'zoger': result, 'petrovic_140': population_check(baseline[140], source['petrovic_force_mean_sd_n']['140']),
            'model_scenario_140_grid': [r for r in cases[140] if r['scenario'] == 'strategy_2_coordinated_chain'],
            'observed_augmentation_contrast_at_matched_pose': None,
            'observed_individual_geometry_and_tissue_at_matched_pose': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'tmp/stage1_followup')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for name, (_, expect) in manifest['files'].items():
        if sha(args.data_dir / name) != expect:
            raise ValueError(f'SHA-256 mismatch: {name}')
    source = manifest['transcribed_published_statistics']
    inputs = [HERE / name for name in ('run.py', 'PROTOCOL.md', 'SOURCES.json')] + [REBUILD]
    result = {'experiment_id': 'EXP-0141', 'stage1': 'HOLD', 'ready_for_compatibility': False,
              'ADAPT25': {'status': 'INSUFFICIENT_DATA', 'walker': walker(args.data_dir, source),
                          'massey': massey(args.data_dir, source['massey_n'])},
              'FORCE20': {'status': 'INSUFFICIENT_DATA', **force(args.data_dir, source)},
              'dependencies_sha256_lf': {p.relative_to(ROOT).as_posix(): sha(p, lf=True) for p in inputs}}
    rendered = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    output = HERE / 'RESULTS.json'
    if args.check:
        if output.read_text(encoding='utf-8') != rendered:
            raise ValueError('Saved output differs')
        print('EXP-0141 results reproduced')
    else:
        output.write_text(rendered, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
