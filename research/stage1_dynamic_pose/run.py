"""Replay external force and distinct secondary outcomes for EXP-0148."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.stats import t

HERE = Path(__file__).resolve().parent


def gain(pre, post):
    return 100 * (post / pre - 1)


def interval(point, se, df):
    error = float(t.ppf(.975, df)) * se
    return [point, point-error, point+error]


def effect(data, ns):
    estimates, errors = [], []
    for ((a, sa), (b, sb)), n in zip(data, ns, strict=True):
        estimates.append(gain(a, b))
        errors.append(100 / a * (b/a * sa + sb) / math.sqrt(n))
    return {
        "gain_pct": estimates,
        "adjusted_pp": interval(estimates[0]-estimates[1], math.hypot(*errors), min(ns)-1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    manifest = (HERE / "SOURCES.json").read_bytes()
    source = json.loads(manifest)
    if args.source_dir:
        for name, (_, digest) in source["files"].items():
            if hashlib.sha256((args.source_dir/name).read_bytes()).hexdigest() != digest:
                parser.error(f"Digest mismatch: {name}")
        print(f"Verified {len(source['files'])} source digests")
    h = source["hirayama"]
    zero, high = h["phase_axis_y"]
    scale = 1800 / (zero-high)
    phase = []
    for bars, control in zip(h["phase_bar_y_and_upper_error_y"], h["phase_control"], strict=True):
        intervention = [[(zero-center)*scale, (center-upper)*scale] for center, upper in bars]
        phase.append(effect([intervention, control], h["dynamic_n"]))
    average = [[imp/duration for imp, duration in zip(impulse, contact, strict=True)]
               for impulse, contact in zip(h["impulse_ns"], h["contact_s"], strict=True)]
    k = source["kubo2007"]
    (i, sd_i), (c, sd_c) = k["weight_and_ply_gain_pct_sd"]
    n, weeks = k["n"], k["weeks"]
    out = {
        "status":"HOLD",
        "source_manifest_sha256":hashlib.sha256(manifest).hexdigest(),
        "hirayama_static": effect(h["static"]["data"],h["static"]["n"]),
        "hirayama_phase_means":phase,
        "hirayama_impulse_gain_pct":[gain(*values) for values in h["impulse_ns"]],
        "hirayama_ratio_of_means_contact_force_n":average,
        "hirayama_ratio_of_means_contact_force_gain_pct":[gain(*values) for values in average],
        "kubo2007_weight_vs_ply_adapt25":interval((i-1.25*c)/weeks,(sd_i+1.25*sd_c)/math.sqrt(n)/weeks,n-1),
        "kubo2007_control_rate":interval(c/weeks,sd_c/math.sqrt(n)/weeks,n-1),
        "kubo2021_estimated_muscle_force":{
            key:effect(value["data"],value["n"]) for key,value in source["kubo2021"].items() if key.endswith("_force")
        }
    }
    result = json.dumps(out, indent=2, allow_nan=False)+"\n"
    p = HERE/"RESULTS.json"
    if args.check:
        if p.read_text(encoding="utf-8") != result:
            parser.error("RESULTS.json differs from replay")
        print("EXP-0148 exact replay")
    else:
        p.write_text(result, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
