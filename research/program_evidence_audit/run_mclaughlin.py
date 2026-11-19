import hashlib
import inspect
import json
import math
from pathlib import Path
import sys

import numpy as np
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_audit import load_runner, lumped_peak, text_sha256

ROOT = Path(__file__).resolve().parent
DATA = Path(sys.argv[1])
expected = "499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531"
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == expected
workbook = load_workbook(DATA, read_only=True, data_only=True)

def columns(sheet, start, stop):
    headers = list(sheet.values)[1]
    values = headers[start:stop]
    ids = [x for x in values if isinstance(x, int)]
    assert len(ids) == len(set(ids))
    return {value: start + i for i, value in enumerate(values) if isinstance(value, int)}

temps = list(workbook["Core Temp"].values)
exercise = list(workbook["Exercise Data"].values)
environment = list(workbook["Environmental Conditions"].values)
demographics = list(workbook["Demographics"].values)
temp_cols = columns(workbook["Core Temp"], 2, 27)
power_cols = columns(workbook["Exercise Data"], 77, 101)
air_cols = columns(workbook["Environmental Conditions"], 2, 27)
rh_cols = columns(workbook["Environmental Conditions"], 27, 51)
mass = {row[0]: row[4] for row in demographics[1:] if isinstance(row[0], int)}
temp_rows = {row[1]: row for row in temps[2:] if isinstance(row[1], int)}
power_row = next(row for row in exercise if row[1] == "0-1")
env_row = next(row for row in environment[2:] if row[1] == "5-6")
all_ids = sorted(set(temp_cols) | set(power_cols) | set(air_cols) | set(rh_cols))
eligible, exclusions = [], []
for participant in all_ids:
    try:
        values = [
            mass[participant], temp_rows[1][temp_cols[participant]],
            temp_rows[45][temp_cols[participant]], temp_rows[60][temp_cols[participant]],
            power_row[power_cols[participant]], env_row[air_cols[participant]],
            env_row[rh_cols[participant]],
        ]
        if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ValueError("missing or non-numeric")
        weight, start, end, late, power, ambient, rh = values
        if not (30 <= weight <= 200 and 34 <= start <= 42 and 34 <= end <= 43 and 0 < power < 600 and 0 <= rh <= 100 and 0 <= ambient <= 50):
            raise ValueError("outside data-quality bounds")
        eligible.append((weight, start, end, late, power, ambient, rh / 100))
    except (KeyError, IndexError, ValueError):
        exclusions.append(participant)

module = load_runner(63)
source = inspect.getsource(lumped_peak).replace("def lumped_peak(", "def lumped_final(").replace("    return peak_C", "    return temp_C")
namespace = dict(lumped_peak.__globals__)
exec(source, namespace)
lumped_final = namespace["lumped_final"]
initial = sum(c * t for c, t in zip([75*3470*s for s in (0.35, 0.42, 0.16, 0.07)] + [3.2*3800], (37, 35.8, 34, 33, 36.85))) / (75*3470 + 3.2*3800)
observed, predictions, simple = [], [], []
for weight, start, end, late, power, ambient, rh in eligible:
    output = module.simulate_4layer_pennes_2700s(power, 1.0, ambient, rh, body_mass_kg=weight)
    trace = {row["time_s"]: row["T_core_C"] for row in output["trace_30s"]}
    observed.append(end - start)
    predictions.append(trace[2640.0] - trace[0.0])
    simple.append(lumped_final([power] * 528, 5.0, ambient, rh, module.saturation_vapor_pressure_kpa) - initial)

observed = np.asarray(observed)
predictions = np.asarray(predictions)
simple = np.asarray(simple)
errors = {"persistence": abs(observed), "pennes": abs(predictions-observed), "lumped": abs(simple-observed)}
rng = np.random.default_rng(20261120)
resamples = rng.integers(0, len(observed), size=(10000, len(observed)))
metrics = {}
for name, predicted in (("persistence", np.zeros_like(observed)), ("pennes", predictions), ("lumped", simple)):
    metrics[name] = {
        "mae_C": float(np.mean(errors[name])),
        "median_absolute_error_C": float(np.median(errors[name])),
        "bias_C": float(np.mean(predicted - observed)),
    }
comparisons = {}
for baseline in ("persistence", "lumped"):
    difference = errors[baseline] - errors["pennes"]
    comparisons[baseline] = {
        "mae_difference_C": float(np.mean(difference)),
        "ci95_C": np.quantile(difference[resamples].mean(axis=1), [0.025, 0.975]).tolist(),
    }
result = {
    "source": "10.6084/m9.figshare.29120024.v1",
    "source_sha256": expected,
    "protocol_sha256_lf": text_sha256(ROOT/"MCLAUGHLIN_PROTOCOL.md"),
    "runner_sha256_lf": text_sha256(Path(__file__)),
    "eligible_participants": len(eligible),
    "excluded_count": len(exclusions),
    "mean_observed_change_C": float(observed.mean()),
    "metrics": metrics,
    "paired_baseline_minus_pennes": comparisons,
    "status": "exploratory external transfer, not CPE45 validation",
}
(ROOT/"MCLAUGHLIN_RESULTS.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
