"""Replay study-level contrasts from audited publications for EXP-0145."""

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

from scipy.stats import t

HERE = Path(__file__).resolve().parent
CORRELATIONS = (-1, 0, 0.5, 0.9, 1)


def interval(estimate, se, df):
    half_width = t.ppf(0.975, df) * se
    return {"estimate": estimate, "ci95": [estimate - half_width, estimate + half_width]}


def percent_change(before, after):
    return 100 * (after / before - 1)


def relative_change(pre, post, pre_n, post_n, correlation):
    before, sd_before = pre
    after, sd_after = post
    pre_error = 100 * after * sd_before / (before**2 * math.sqrt(pre_n))
    post_error = 100 * sd_after / (before * math.sqrt(post_n))
    variance = (pre_error - post_error)**2 + 2 * (1 - correlation) * pre_error * post_error
    return percent_change(before, after), math.sqrt(variance)


def seasonal(case):
    intervention, control = case["intervention"], case["control"]
    visits = []
    for end in range(1, len(intervention["week"])):
        iw, cw = intervention["week"][end], control["week"][end]
        df = min(group["n"][visit] for group in (intervention, control) for visit in (0, end)) - 1
        sensitivity = {}
        for rho in CORRELATIONS:
            i, i_se = relative_change(
                intervention["mvc_nm_per_kg"][0], intervention["mvc_nm_per_kg"][end],
                intervention["n"][0], intervention["n"][end], rho,
            )
            c, c_se = relative_change(
                control["mvc_nm_per_kg"][0], control["mvc_nm_per_kg"][end],
                control["n"][0], control["n"][end], rho,
            )
            sensitivity[str(rho)] = {
                "intervention_gain_pct": interval(i, i_se, df),
                "control_rate_pp_per_week": interval(c / cw, c_se / cw, df),
                "force20_adjusted_pp": interval(i - c, math.hypot(i_se, c_se), df),
                "adapt25_pp_per_week": interval(
                    i / iw - 1.25 * c / cw, math.hypot(i_se / iw, 1.25 * c_se / cw), df
                ),
            }
        visits.append({"intervention_week": iw, "control_week": cw, "rho": sensitivity})
    tissue = {}
    for label, group in case.items():
        tissue[label] = {
            "body_mass_change_pct": percent_change(group["mass_kg"][0], group["mass_kg"][-1]),
            "mvc_approx_product_of_means_nm": [
                mass * mvc[0] for mass, mvc in zip(group["mass_kg"], group["mvc_nm_per_kg"], strict=True)
            ],
            "elongation_over_rest_length_pct_ratio_of_means": [
                100 * elongation / length
                for elongation, length in zip(group["max_elongation_mm"], group["rest_length_mm"], strict=True)
            ],
            "peak_tendon_force_change_pct": percent_change(*[group["peak_tendon_force_n"][i] for i in (0, -1)]),
            "stiffness_change_pct": percent_change(*[group["stiffness_n_per_mm"][i] for i in (0, -1)]),
        }
    return {"visits": visits, "tissue_and_mass": tissue}


def paired_comparison(i, i_se, c, c_se, weeks, df, leg_rho):
    return {
        "intervention_gain_pct": interval(i, i_se, df),
        "control_rate_pp_per_week": interval(c / weeks, c_se / weeks, df),
        "force20_adjusted_pp": interval(
            i - c, math.sqrt((i_se - c_se)**2 + 2 * (1 - leg_rho) * i_se * c_se), df
        ),
        "adapt25_pp_per_week": interval(
            (i - 1.25 * c) / weeks,
            math.sqrt((i_se - 1.25 * c_se)**2 + 2 * (1 - leg_rho) * i_se * 1.25 * c_se) / weeks, df,
        ),
    }


def angles(case):
    n, weeks = case["n"], case["weeks"]
    output = {}
    for label, field in (
        ("same_test_angle_long_vs_short", "mvc_at_80deg_individual_gain_pct_sd"),
        ("different_training_angles_short_vs_long", "mvc_at_training_angle_individual_gain_pct_sd"),
    ):
        groups = case[field]
        order = ("long", "short") if field.startswith("mvc_at_80") else ("short", "long")
        (i, i_sd), (c, c_sd) = [groups[group] for group in order]
        output[label] = {
            str(rho): paired_comparison(i, i_sd / math.sqrt(n), c, c_sd / math.sqrt(n), weeks, n - 1, rho)
            for rho in CORRELATIONS
        }
    return output


def convert_pixel(pixel, calibration):
    (p0, v0), (p1, v1) = calibration
    return v0 + (pixel - p0) * (v1 - v0) / (p1 - p0)


def digitized_tendon(case):
    def convert(xy):
        x, y = xy
        return (convert_pixel(x, case["elongation_mm_calibration"]), convert_pixel(y, case["force_n_calibration"]))

    def common_elongation(points):
        (x0, y0), (x1, y1) = map(convert, points)
        return x0 + (x1 - x0) * (case["common_force_n"] - y0) / (y1 - y0)

    pre_max = convert(case["pre_max_xy"])
    post_max = convert(case["post_max_xy"])
    return {
        "native_peak_pre_mm_n": pre_max,
        "native_peak_post_mm_n": post_max,
        "native_peak_tendon_force_gain_pct": percent_change(pre_max[1], post_max[1]),
        "per_point_reading_error_mm_n": [
            abs(convert_pixel(case["reading_error_pixels"], calibration) - convert_pixel(0, calibration))
            for calibration in (case["elongation_mm_calibration"], case["force_n_calibration"])
        ],
        "common_force_n": case["common_force_n"],
        "common_force_elongation_pre_mm": common_elongation(case["pre_common_brackets_xy"]),
        "common_force_elongation_post_mm": common_elongation(case["post_common_brackets_xy"]),
    }


def static_dynamic(case):
    n, weeks = case["n"], case["weeks"]
    sensitivity = {}
    for visit_rho, leg_rho in product(CORRELATIONS, repeat=2):
        i, i_se = relative_change(*case["mvc_at_90deg_nm"]["static"], n, n, visit_rho)
        c, c_se = relative_change(*case["mvc_at_90deg_nm"]["dynamic"], n, n, visit_rho)
        sensitivity[f"{visit_rho},{leg_rho}"] = paired_comparison(i, i_se, c, c_se, weeks, n - 1, leg_rho)
    i, c = (case["text_gain_pct"][group] for group in ("static", "dynamic"))
    return {
        "visit_and_leg_rho": sensitivity,
        "text_gain_pct_no_sd": case["text_gain_pct"],
        "text_force20_adjusted_pp": i - c,
        "text_adapt25_pp_per_week": (i - 1.25 * c) / weeks,
        "patellar_tendon_figure2a": digitized_tendon(case["figure2a"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path, help="Directory of original downloads for SHA-256 validation")
    args = parser.parse_args()
    source = HERE / "SOURCES.json"
    inputs = json.loads(source.read_text(encoding="utf-8"))
    if args.source_dir:
        for name, (_, expected) in inputs["files"].items():
            actual = hashlib.sha256((args.source_dir / name).read_bytes()).hexdigest()
            if actual != expected:
                parser.error(f"Source digest mismatch for {name}")
        print(f"Verified {len(inputs['files'])} source digests")
    results = {
        "experiment": "EXP-0145",
        "source_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "stage1_status": "HOLD",
        "seasonal": {name: seasonal(case) for name, case in inputs["seasonal"].items()},
        "kubo_angles": angles(inputs["kubo_angles"]),
        "kubo_static_dynamic": static_dynamic(inputs["kubo_static_dynamic"]),
        "mersmann_risk_reported": inputs["mersmann_risk"],
    }
    encoded = json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if path.read_text(encoding="utf-8") != encoded:
            parser.error("RESULTS.json differs from the replay")
        print("EXP-0145 exact replay")
    else:
        path.write_text(encoded, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
