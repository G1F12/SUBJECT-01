"""One-factor sensitivity of the archived EXP-0061 closed-chain LP."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
source_path = ROOT / "research/exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py"
source = source_path.read_text(encoding="utf-8")
parameters = {
    "friction": ("mu_friction = 0.80", [0.4, 0.6, 0.8, 1.0]),
    "forefoot_m": ("x_forefoot = 0.160", [0.10, 0.13, 0.16, 0.19]),
    "plate_angle_deg": ("psi_p_deg = 10.0", [0, 5, 10, 15, 20]),
    "height_m": ("height_m = 1.78", [1.60, 1.69, 1.78, 1.87, 1.96]),
    "specific_tension_multiplier": ("SIGMA_QUAD_CANONICAL_N_CM2 = 26.41", [0.7, 0.85, 1.0, 1.15, 1.3]),
}

def run(fragment, value, parameter):
    assert source.count(fragment) == 1
    variable = fragment.split("=")[0].strip()
    replacement = f"{variable} = {26.41 * value if parameter == 'specific_tension_multiplier' else value!r}"
    namespace = {"__name__": "archived_exp0061_sensitivity", "__file__": str(source_path)}
    exec(compile(source.replace(fragment, replacement), str(source_path), "exec"), namespace)
    return namespace["solve_closed_chain_3dof_model"]()

def gains(result):
    item = result["scenarios"]["strategy_2_coordinated_chain"]["postures"]
    return {name: entry["comparison_to_baseline"]["bilateral_footplate_force_gain_pct"] for name, entry in item.items()}

archive = json.loads((source_path.parent / "RESULTS.json").read_text(encoding="utf-8"))
target = gains(archive["part_c_closed_chain_3dof_model"])
reference = gains(run("mu_friction = 0.80", 0.8, "friction"))
assert target == reference, (target, reference)
outcomes = {}
for parameter, (fragment, grid) in parameters.items():
    outcomes[parameter] = []
    for value in grid:
        try:
            outcomes[parameter].append({"value": value, "gain_pct": gains(run(fragment, value, parameter))})
        except RuntimeError as error:
            outcomes[parameter].append({"value": value, "error": str(error)})
result = {
    "experiment_id": "EXP-0068",
    "classification": "MODEL_ONLY_ONE_FACTOR_SENSITIVITY",
    "source_sha256_lf": hashlib.sha256(source.encode()).hexdigest(),
    "protocol_sha256_lf": hashlib.sha256((HERE / "CHAIN_SENSITIVITY_PROTOCOL.md").read_text(encoding="utf-8").encode()).hexdigest(),
    "archive_reference_gain_pct": target,
    "results": outcomes,
}
(HERE / "CHAIN_SENSITIVITY_RESULTS.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
