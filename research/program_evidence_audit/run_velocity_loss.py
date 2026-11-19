"""EXP-0080: held-participant retrospective velocity loss, not online prediction."""
import csv
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from run_audit import text_sha256

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = '9283595449be5d7a3ed1641d2ba1f6919288907805df9888098680df022bd3ad'
path = Path(sys.argv[1])
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'Unexpected source file hash'
groups = {}
excluded = 0
with path.open(encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f, delimiter=';'):
        try:
            x = float(row['PercMNR'].replace(',', '.'))
            y = float(row['PercVL'].replace(',', '.'))
            if not (np.isfinite(x) and np.isfinite(y)):
                raise ValueError('non-finite')
            groups.setdefault(row['Subject'], []).append((x, y))
        except (KeyError, ValueError):
            excluded += 1
assert len(groups) == 23
errors = []
ends = []
for person in sorted(groups, key=int):
    train = [rows for p, rows in groups.items() if p != person]
    x = np.array([v[0] for rows in train for v in rows])
    y = np.array([v[1] for rows in train for v in rows])
    w = np.array([1 / len(rows) for rows in train for _ in rows])
    design = np.column_stack((np.ones(len(x)), x))
    beta = np.linalg.lstsq(design * np.sqrt(w[:, None]), y * np.sqrt(w), rcond=None)[0]
    base = np.average(y, weights=w)
    test = np.array(groups[person]); residual_base = base - test[:, 1]
    residual_model = beta[0] + beta[1] * test[:, 0] - test[:, 1]
    errors.append([np.mean(np.abs(residual_base)), np.mean(np.abs(residual_model)),
                   np.mean(residual_base**2), np.mean(residual_model**2),
                   np.mean(residual_base), np.mean(residual_model)])
    ends.extend(y for x, y in groups[person] if abs(x - 100) < 1e-8)
e = np.array(errors); delta = e[:, 0] - e[:, 1]
rng = np.random.default_rng(20261120)
idx = rng.integers(0, len(delta), (10000, len(delta)))
result = {'experiment_id':'EXP-0080', 'classification':'EXPLORATORY_RETROSPECTIVE',
 'input_sha256_bytes':SOURCE_SHA256, 'protocol_sha256_lf':text_sha256(HERE/'VELOCITY_LOSS_PROTOCOL.md'),
 'runner_sha256_lf':text_sha256(Path(__file__)), 'participants':len(groups),
 'included_rows':sum(map(len, groups.values())), 'excluded_rows':excluded,
 'participant_weighted_mae_baseline_pp':e[:,0].mean(), 'participant_weighted_mae_linear_pp':e[:,1].mean(),
 'participant_weighted_rmse_baseline_pp':np.sqrt(e[:,2].mean()), 'participant_weighted_rmse_linear_pp':np.sqrt(e[:,3].mean()),
 'participant_weighted_bias_baseline_pp':e[:,4].mean(), 'participant_weighted_bias_linear_pp':e[:,5].mean(),
 'paired_gain_mae_pp':delta.mean(), 'paired_bootstrap_ci95_pp':np.quantile(delta[idx].mean(axis=1),[.025,.975]).tolist(),
 'endpoint_count':len(ends), 'endpoint_min_pp':min(ends), 'endpoint_max_pp':max(ends),
 'endpoint_sd_pp':np.std(ends,ddof=1)}
(HERE/'VELOCITY_LOSS_RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, indent=2))

