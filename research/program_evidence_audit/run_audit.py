"""Reproduce archived calculations and audit thermal comparisons at equal work."""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import platform
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNNERS = {
    61: "exp0061_multijoint_legpress/run_exp0061_protocol_and_chain.py",
    62: "exp0062_enthesis_viscoelastic_hazard/run_exp0062_enthesis_and_heterochrony.py",
    63: "exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py",
    64: "architecture_a_integration/run_exp0064_master_integration.py",
}
CLIMATES = {
    "temperate_20C_50RH": (20, 0.50),
    "warm_28C_60RH": (28, 0.60),
    "hot_dry_35C_30RH": (35, 0.30),
    "hot_humid_32C_80RH": (32, 0.80),
}
DURATION_S = 2700
EFFORT_W = 360.0
RECOVERY_W = 35.0
EFFICIENCY = 0.21
RESTING_HEAT_W = 88.0


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_sha256(path):
    """Hash the text as committed by Git, independent of checkout line endings."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_runner(number):
    path = ROOT / "research" / RUNNERS[number]
    spec = importlib.util.spec_from_file_location(f"exp{number}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def json_differences(expected, actual, path="$"):
    if type(expected) is not type(actual):
        yield f"{path}: types differ"
    elif isinstance(expected, dict):
        if expected.keys() != actual.keys():
            yield f"{path}: different field names"
        for key in expected.keys() & actual.keys():
            yield from json_differences(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            yield f"{path}: different lengths"
        for i, (left, right) in enumerate(zip(expected, actual)):
            yield from json_differences(left, right, f"{path}[{i}]")
    elif isinstance(expected, float):
        if not math.isclose(expected, actual, rel_tol=1e-6, abs_tol=1e-5):
            yield f"{path}: {expected!r} != {actual!r}"
    elif expected != actual:
        yield f"{path}: {expected!r} != {actual!r}"


def replay():
    records = {}
    with tempfile.TemporaryDirectory(prefix="subject01-replay-") as scratch:
        for number, runner in RUNNERS.items():
            module = load_runner(number)
            source = ROOT / "research" / runner
            archived = source.parent / "RESULTS.json"
            module.OUT_DIR = Path(scratch) / str(number)
            if number == 64:
                for previous in (61, 62, 63):
                    setattr(module, f"EXP{previous}_JSON", Path(scratch) / str(previous) / "RESULTS.json")
            module.main()
            result = module.OUT_DIR / "RESULTS.json"
            differences = sorted(json_differences(read_json(archived), read_json(result)))
            records[f"EXP-{number:04}"] = {
                "archived_path": archived.relative_to(ROOT).as_posix(),
                "runner_sha256": text_sha256(source),
                "archived_sha256": text_sha256(archived),
                "replayed_sha256": text_sha256(result),
                "text_hash_newlines": "LF",
                "differences_outside_tolerance": differences,
            }
    return records


def step_powers(duty, step_s):
    """Mirror the EXP-0063 zero-order-hold input, including any phase aliasing."""
    period_s = 60.0 / duty
    return [
        EFFORT_W if i * step_s % period_s < 60.0 else RECOVERY_W
        for i in range(round(DURATION_S / step_s))
    ]


def lumped_peak(powers, step_s, ambient_C, humidity, vapor_pressure):
    """Compare effective storage temperature without a spatial gradient."""
    layer_capacities = [75 * 3470 * share for share in (0.35, 0.42, 0.16, 0.07)]
    capacities = layer_capacities + [3.2 * 3800]
    total_capacity = sum(capacities)
    temp_C = sum(c * t for c, t in zip(capacities, (37, 35.8, 34, 33, 36.85))) / total_capacity
    peak_C = temp_C
    ambient_vapor = humidity * vapor_pressure(ambient_C)
    area = 1.92
    for power_W in powers:
        dry_W = area * (
            7.8 * (temp_C - ambient_C)
            + 0.95 * 5.670374419e-8 * ((temp_C + 273.15)**4 - (ambient_C + 273.15)**4)
        )
        thermal_drive = max(0.0, temp_C - 37 + 0.15 * (temp_C - 33))
        evaporation_limit_W = max(0.0, 16.5 * 7.8 * area * (vapor_pressure(temp_C) - ambient_vapor))
        sweat_W = (1.20 / 3600) * 0.72 * 2.42e6 * min(1.0, thermal_drive / 1.5)
        metabolic_W = 82 + power_W / EFFICIENCY
        respiration_W = max(8.0, metabolic_W * (0.075 + 0.0014 * (34 - ambient_C)))
        heat_W = RESTING_HEAT_W + power_W * (1 / EFFICIENCY - 1)
        temp_C += step_s * (heat_W - dry_W - min(sweat_W, evaporation_limit_W) - respiration_W) / total_capacity
        peak_C = max(peak_C, temp_C)
    return peak_C


def summary(result):
    return {key: result[key] for key in (
        "peak_T_core_C", "peak_T_muscle_C", "passes_core_39_5C_gate",
        "energy_balance_error_J", "mean_heat_generated_W",
    )}


def compare_thermal():
    module = load_runner(63)
    archive = read_json(module.OUT_DIR / "RESULTS.json")
    records = []
    for climate, (ambient, humidity) in CLIMATES.items():
        envelope = archive["part_b_3d_envelope_summary"]["climate_thresholds_for_360W_arch_a"][climate]
        duty = envelope["max_safe_duty_cycle_360W"]
        for step_s in (5.0, 2.5, 1.0):
            powers = step_powers(duty, step_s)
            mean_W = sum(powers) / len(powers)
            same_work = [mean_W] * len(powers)
            continuous = [EFFORT_W] * len(powers)
            models = {
                "intermittent": summary(module.simulate_4layer_pennes_2700s(EFFORT_W, duty, ambient, humidity, dt_s=step_s)),
                "equal_work_constant": summary(module.simulate_4layer_pennes_2700s(mean_W, 1, ambient, humidity, dt_s=step_s)),
                "full_power_constant": summary(module.simulate_4layer_pennes_2700s(EFFORT_W, 1, ambient, humidity, dt_s=step_s)),
            }
            traces = dict(zip(models, (powers, same_work, continuous)))
            for name, power_trace in traces.items():
                work_J = sum(power_trace) * step_s
                assert abs(models[name]["energy_balance_error_J"]) <= 0.001, (climate, name)
                mean_heat_W = RESTING_HEAT_W + (work_J / DURATION_S) * (1 / EFFICIENCY - 1)
                assert abs(mean_heat_W - models[name]["mean_heat_generated_W"]) <= 0.051, (climate, name)
                models[name]["work_J"] = round(work_J, 3)
                models[name]["lumped_peak_storage_C"] = round(
                    lumped_peak(power_trace, step_s, ambient, humidity, module.saturation_vapor_pressure_kpa), 4
                )
            assert models["intermittent"]["work_J"] == models["equal_work_constant"]["work_J"]
            records.append({"climate": climate, "step_s": step_s, "input_duty": duty, "runs": models})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "RESULTS.json")
    args = parser.parse_args()
    result = {
        "experiment_id": "EXP-0065",
        "classification": "MODEL_ONLY_AND_ARCHIVE_REPLAY",
        "target_cpe45": "not_assessed",
        "historical_head": "c3113f1c49dee47d177006dedb9e4efee9050fad",
        "environment": {
            "python": platform.python_version(),
            **{name: importlib.metadata.version(name) for name in ("numpy", "scipy", "pandas")},
        },
        "protocol_sha256": text_sha256(HERE / "PROTOCOL.md"),
        "audit_script_sha256": text_sha256(Path(__file__)),
        "archive_replay": replay(),
        "thermal": compare_thermal(),
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    failures = [key for key, value in result["archive_replay"].items() if value["differences_outside_tolerance"]]
    if failures:
        print(f"Archive deviations outside tolerance: {', '.join(failures)}")
    else:
        print("All four archived results reproduced within tolerance")


if __name__ == "__main__":
    main()
