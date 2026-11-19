"""Control the tissue assumptions while varying the muscle adaptation rate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
path = ROOT / "research/exp0062_enthesis_viscoelastic_hazard/run_exp0062_enthesis_and_heterochrony.py"
source = path.read_text(encoding="utf-8")
old = 'run_regime("Accelerated +25% Adaptation Target (TARGET-ADAPT25, tau_m = 12 d)", 12.0, 14.0, 90.0, False)'
assert source.count(old) == 1

def invoke(text):
    context = {"__name__": "exp0062_adaptation_audit", "__file__": str(path)}
    exec(compile(text, str(path), "exec"), context)
    return context["simulate_remodeling_heterochrony_ode"]()["regimes"]

archived = json.loads((path.parent/"RESULTS.json").read_text(encoding="utf-8"))["part_c_remodeling_heterochrony_ode"]["regimes"]
original = invoke(source)
assert original == archived
results = {"historical_H0": original["H0_uncoordinated_standard_16d"],
           "historical_H1": original["H1_uncoordinated_target_adapt25_12d"]}
for label, tau in (("controlled_1_25x", 12.8), ("controlled_1_333x", 12.0)):
    replacement = f'run_regime("{label}", {tau}, 10.0, 84.0, False)'
    result = invoke(source.replace(old, replacement))["H1_uncoordinated_target_adapt25_12d"]
    results[label] = result
out = {
    "experiment_id": "EXP-0070",
    "classification": "MODEL_ONLY_CONTROLLED_SCENARIO",
    "source_sha256_lf": hashlib.sha256(source.encode()).hexdigest(),
    "protocol_sha256_lf": hashlib.sha256((HERE/"ADAPT25_PROTOCOL.md").read_text(encoding="utf-8").encode()).hexdigest(),
    "muscle_time_constants_days": {"control": 16, "controlled_1_25x": 12.8, "controlled_1_333x": 12},
    "results": results,
}
(HERE/"ADAPT25_RESULTS.json").write_text(json.dumps(out, indent=2)+"\n", encoding="utf-8")
print(json.dumps(out, indent=2))
