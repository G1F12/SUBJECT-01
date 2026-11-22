"""Recalculate EXP-0146 from published tables and graph coordinates."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.stats import t

HERE = Path(__file__).resolve().parent
RHOS = (-1, 0, 0.5, 0.9, 1)


def ci(value, se, df):
    margin = t.ppf(0.975, df) * se
    return {"estimate": value, "ci95": [value - margin, value + margin]}


def relative(pre, post, n, dispersion, rho):
    before, pre_spread = pre
    after, post_spread = post
    factor = 100 / (before * (math.sqrt(n) if dispersion == "SD" else 1))
    a = factor * after * pre_spread / before
    b = factor * post_spread
    return 100 * (after / before - 1), math.sqrt((a - b)**2 + 2 * (1 - rho) * a * b)


def controlled(i, c, n_i, n_c, dispersion, rho):
    i_change, i_se = relative(*i, n_i, dispersion, rho)
    c_change, c_se = relative(*c, n_c, dispersion, rho)
    return ci(i_change - c_change, math.hypot(i_se, c_se), min(n_i, n_c) - 1)


def pixel_value(y, axis, span):
    zero, top = axis
    return (zero - y) * span / (zero - top)


def bar_values(bars, axis):
    return [
        (pixel_value(center, axis, 50), pixel_value(upper, axis, 50) - pixel_value(center, axis, 50))
        for center, upper in bars
    ]


def kubo(case):
    n_i, n_c = case["n"]
    mvc, control = case["mvc"], case["control_mvc"]
    dispersion = case["dispersion"]
    figure = "figure2a_bars_center_and_upper_error_y"
    bars = bar_values(case[figure], case["figure2a_axis_y_0_and_50_pct"]) if figure in case else None
    results = []
    for visit, month in enumerate(case["time_months"][1:], start=1):
        group = (mvc[0], mvc[visit])
        length = case["max_elongation_mm"]
        stiffness = case["stiffness_published"]
        result = {
            "month": month,
            "within_mvc_pct": {
                str(r): ci(*relative(*group, n_i, dispersion, r), n_i - 1) for r in RHOS
            },
            "max_elongation_mm": length[visit][0],
            "max_elongation_change_from_training_end_mm": length[visit][0] - length[3][0],
            "stiffness_relative_to_baseline": stiffness[visit] / stiffness[0],
        }
        if bars:
            result["fig2a_individual_gain_pct"] = ci(*bars[visit - 1], n_i - 1)
        if control[visit]:
            ref = (control[0], control[visit])
            result["control_adjusted_pct_points"] = {
                str(r): controlled(group, ref, n_i, n_c, dispersion, r) for r in RHOS
            }
            if bars:
                gain, sem = bars[visit - 1]
                result["mixed_scale_figure_gain_minus_control_pct_points"] = {}
                for rho in RHOS:
                    control_gain, control_se = relative(*ref, n_c, dispersion, rho)
                    result["mixed_scale_figure_gain_minus_control_pct_points"][str(rho)] = ci(
                        gain - control_gain, math.hypot(sem, control_se), n_c - 1
                    )
        results.append(result)
    return results


def epro(case):
    checks = {}
    for label, n_key, mvc_key, visit in (
        ("14_week_full", "n_medium", "medium_mvc", 1),
        ("14_week_completers", "n_long", "long_mvc", 1),
        ("1_5_year_completers", "n_long", "long_mvc", 2),
    ):
        n_i, n_c = case[n_key]
        i = (case[mvc_key][0], case[mvc_key][visit])
        c = (case["control_mvc"][0], case["control_mvc"][visit])
        checks[label] = {
            str(rho): {
                "within_gain_pct": ci(*relative(*i, n_i, "SD", rho), n_i - 1),
                "adjusted_pct_points": controlled(i, c, n_i, n_c, "SD", rho),
            }
            for rho in RHOS
        }
    return checks


def active_contrasts(groups, n, time, reported_sem=False):
    results = {}
    for label, (i, i_sd), (c, c_sd), (n_i, n_c) in groups:
        i_se = i_sd if reported_sem else i_sd / math.sqrt(n[n_i])
        c_se = c_sd if reported_sem else c_sd / math.sqrt(n[n_c])
        results[label] = {
            "intervention_gain_pct": ci(i, i_se, n[n_i] - 1),
            "control_rate_pp_per_week": ci(c / time, c_se / time, n[n_c] - 1),
            "adapt25_pp_per_week": ci(
                (i - 1.25 * c) / time, math.hypot(i_se, 1.25 * c_se) / time, min(n[n_i], n[n_c]) - 1
            ),
        }
    return results


def quinlan(case):
    n = case["strength_n"]
    positions = case["figure5_change_center_and_upper_error_y"]
    strength_axis = case["figure5_axis_y_0_and_50_pct"]
    bars = {group: bar_values(points, strength_axis) for group, points in positions.items()}
    visits = {}
    for visit, week in enumerate(case["weeks"]):
        groups = []
        for age in ("young", "older"):
            for i, c in (("ecc", "con"), ("con", "ecc")):
                keys = (f"{age}_{i}", f"{age}_{c}")
                groups.append((keys[0] + "_vs_" + c, bars[keys[0]][visit], bars[keys[1]][visit], keys))
        visits[str(week)] = active_contrasts(groups, n, week)
    axis = case["figure1_axis_y_at_0_and_4000_n_per_mm"]
    return {
        "strength_and_adapt25": visits,
        "stiffness_n_per_mm": {
            key: [pixel_value(y, axis, 4000) for y in points]
            for key, points in case["figure1_stiffness_center_y"].items()
        },
        "max_final_adapt25_point_reading_error_pp_per_week": (
            (1 + 1.25) * pixel_value(strength_axis[0] - 2, strength_axis, 50) / case["weeks"][-1]
        ),
    }


def geremia(case):
    n = case["n"]
    forces = case["calculated_peak_tendon_force_n"]
    windows = [(0, 1), (1, 2), (1, 3), (1, 4)]
    return {
        f"{case['time_week'][pre]}_to_{case['time_week'][post]}": {
            "estimated_tendon_force_gain_pct": {
                str(r): ci(*relative(forces[pre], forces[post], n, "SD", r), n - 1) for r in RHOS
            },
            "native_peak_strain_change_pp": case["native_peak_strain_pct"][post][0] - case["native_peak_strain_pct"][pre][0],
        }
        for pre, post in windows
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    manifest = (HERE / "SOURCES.json").read_bytes()
    data = json.loads(manifest)
    if args.source_dir:
        for filename, (_, expected) in data["files"].items():
            if hashlib.sha256((args.source_dir / filename).read_bytes()).hexdigest() != expected:
                parser.error(f"Digest mismatch: {filename}")
        print(f"Verified {len(data['files'])} source digests")
    s = data["seynnes"]
    gain, spread = s["text_gain_pct_and_dispersion"]
    high, low = data["grosset"]["high_and_low_force_pct_sem"]
    output = {
        "experiment": "EXP-0146",
        "stage1_status": "HOLD",
        "source_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "kubo_knee": kubo(data["kubo_knee"]),
        "kubo_achilles": kubo(data["kubo_achilles"]),
        "epro": epro(data["epro"]),
        "seynnes": {
            "mvc_individual_change_pct_if_sd": ci(gain, spread / math.sqrt(s["n"]), s["n"] - 1),
            "mvc_individual_change_pct_if_sem": ci(gain, spread, s["n"] - 1),
            "common_force_tissue": s["common_force_tissue"],
        },
        "quinlan": quinlan(data["quinlan"]),
        "geremia": geremia(data["geremia"]),
        "grosset_estimated_force_only": active_contrasts(
            [("low_vs_high", low, high, (1, 0)), ("high_vs_low", high, low, (0, 1))],
            data["grosset"]["n"], data["grosset"]["weeks"], reported_sem=True,
        ),
        "nct03079180": data["nct03079180"],
    }
    result = json.dumps(output, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if path.read_text(encoding="utf-8") != result:
            parser.error("RESULTS.json differs from the replay")
        print("EXP-0146 exact replay")
    else:
        path.write_text(result, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
