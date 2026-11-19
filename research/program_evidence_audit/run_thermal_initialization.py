"""Compare two initial states on the previously inspected McLaughlin cohort."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from run_audit import text_sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
original_path = HERE / "run_mclaughlin.py"
solver_path = ROOT / "research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py"
script = original_path.read_text(encoding="utf-8")
marker = 'result = {\n    "source":'
assert script.count(marker) == 1
# Execute only the data loading and predictions section; do not rewrite its archived JSON.
section = script.split(marker)[0]
def execute_section(revised):
    args = sys.argv[:]
    sys.argv = [str(original_path), sys.argv[1]]
    context = {"__name__": "mclaughlin_analysis", "__file__": str(original_path)}
    try:
        exec(compile(revised, str(original_path), "exec"), context)
    finally:
        sys.argv = args
    return context

base = execute_section(section)
solver_source = solver_path.read_text(encoding="utf-8")
old = "T = np.array([37.0, 35.8, 34.0, 33.0], dtype=float)"
assert solver_source.count(old) == 1 and solver_source.count("T_art = 36.85") == 1
solver_source = solver_source.replace(old, "T = np.array([37.0, 37.0, 37.0, 37.0], dtype=float)").replace("T_art = 36.85", "T_art = 37.0")
solver_context = {"__name__": "uniform_solver", "__file__": str(solver_path)}
exec(compile(solver_source, str(solver_path), "exec"), solver_context)
solver = solver_context["simulate_4layer_pennes_2700s"]
uniform = []
for mass, start, end, late, power, ambient, rh in base["eligible"]:
    output = solver(power, 1.0, ambient, rh, body_mass_kg=mass)
    trace = {row["time_s"]: row["T_core_C"] for row in output["trace_30s"]}
    uniform.append(trace[2640.0] - trace[0.0])
uniform = np.asarray(uniform)
observed = base["observed"]
nominal = base["predictions"]
paired = abs(nominal-observed)-abs(uniform-observed)
rng = np.random.default_rng(20261120)
indices = rng.integers(0, len(observed), size=(10000, len(observed)))
res = {
    "experiment_id": "EXP-0072",
    "classification": "EXPLORATORY_REUSED_COHORT_NOT_NEW_VALIDATION",
    "protocol_sha256_lf": text_sha256(HERE/"THERMAL_INITIALIZATION_PROTOCOL.md"),
    "runner_sha256_lf": text_sha256(Path(__file__)),
    "source_sha256": base["expected"],
    "participants": len(observed),
    "nominal_mae_C": float(np.mean(abs(nominal-observed))),
    "uniform_mae_C": float(np.mean(abs(uniform-observed))),
    "uniform_bias_C": float(np.mean(uniform-observed)),
    "nominal_minus_uniform_mae_C": float(paired.mean()),
    "paired_ci95_C": np.quantile(paired[indices].mean(axis=1), [0.025,0.975]).tolist(),
    "persistence_mae_C": float(np.mean(abs(observed))),
}
(HERE/"THERMAL_INITIALIZATION_RESULTS.json").write_text(json.dumps(res, indent=2)+"\n", encoding="utf-8")
print(json.dumps(res,indent=2))
