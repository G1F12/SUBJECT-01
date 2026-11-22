"""Recalculate EXP-0144 from versioned published summaries."""

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

from scipy.stats import t

HERE = Path(__file__).resolve().parent
CORRELATION_RUNS = (-1, .5, .9, 1)


def summary(value, se, df):
    margin = float(t.ppf(.975, df)) * se
    return {"estimate": value, "ci95": [value - margin, value + margin]}


def sd_components(pairs, unit, n, relative):
    """Return the point and nonnegative signed-gradient components of its SE."""
    (a, va), (b, vb) = pairs
    if unit == "SD":
        va, vb = va / math.sqrt(n), vb / math.sqrt(n)
    if relative:
        return 100 * (b / a - 1), 100 * b * va / a**2, 100 * vb / a
    return b - a, va, vb


def standard_error(a, b, rho):
    return math.sqrt((a - b)**2 + 2 * (1 - rho) * a * b)


def tolerance_by_rounding(pair, epsilon):
    states = [a + sign * epsilon for a in pair for sign in (-1, 1)]
    return [100 * (post / pre - 1) for pre in states[:2] for post in states[2:]]


def strength_comparison(case):
    ni, nc = case["n"]
    df = min(ni, nc) - 1
    w = case["weeks"]
    if "change_pct_sem" in case:
        (pi, isi), (pc, csi) = case["change_pct_sem"]
        i1, i2, c1, c2 = 0, isi, 0, csi
        rhos = (-1,)
    else:
        i, c = case["prepost"]
        pi, i1, i2 = sd_components(i, case["uncertainty_type"], ni, True)
        pc, c1, c2 = sd_components(c, case["uncertainty_type"], nc, True)
        rhos = CORRELATION_RUNS
    results = {}
    for rho in rhos:
        si, sc = standard_error(i1, i2, rho), standard_error(c1, c2, rho)
        label = "published_SEM" if "change_pct_sem" in case else str(rho)
        results[label] = {
            "intervention_pp_per_week": summary(pi / w, si / w, ni - 1),
            "control_pp_per_week": summary(pc / w, sc / w, nc - 1),
            "adapt25_pp_per_week": summary((pi - 1.25*pc) / w, math.hypot(si, 1.25*sc) / w, df),
            "within_intervention_gain_pct": summary(pi, si, ni - 1),
            "control_adjusted_gain_pp": summary(pi - pc, math.hypot(si, sc), df),
        }
        if "prepost" in case:
            (a, sa), (b, sb) = case["prepost"][0]
            scale = math.sqrt(ni) if case["uncertainty_type"] == "SD" else 1
            results[label]["force20_margin_original_units"] = summary(
                b - 1.2*a, standard_error(1.2*sa, sb, rho) / scale, ni - 1
            )
    output = {"rho_sensitivity": results}
    adapt_margin = pi - 1.25*pc
    covariance_coefficient = 2 * (i1*i2 + 1.25**2 * c1*c2)
    if adapt_margin > 0 and covariance_coefficient > 0:
        variance_at_zero = i1*i1 + i2*i2 + 1.25**2 * (c1*c1 + c2*c2)
        output["common_rho_threshold_for_positive_adapt25_lower_bound"] = (
            variance_at_zero - (adapt_margin / float(t.ppf(.975, df)))**2
        ) / covariance_coefficient
    if "rounding_half_step" in case:
        levels = [tolerance_by_rounding([p[0] for p in group], case["rounding_half_step"])
                  for group in case["prepost"]]
        contrasts = [(i - 1.25*c) / w for i, c in product(*levels)]
        output["adapt25_rounding_point_range_pp_per_week"] = [min(contrasts), max(contrasts)]
    return output


def tissue_comparison(channel):
    point, a, b = sd_components(channel["prepost"], channel["uncertainty_type"], channel["n"],
                               channel.get("relative", False))
    return {str(rho): summary(point, standard_error(a, b, rho), channel["n"] - 1)
            for rho in CORRELATION_RUNS}


def figure_strain(spec):
    origin, tick10 = spec["axis_origin_and_ten_percent_x"]
    factor = 10 / (tick10 - origin)
    return {group: {
        "estimated_visit_values_pct": [(x - origin) * factor for x in pixels],
        "estimated_change_pp": (pixels[1] - pixels[0]) * factor,
        "digitizing_change_error_pp": 2 * spec["digitizing_error_each_px"] * factor,
    } for group, pixels in spec["markers"].items()}


def mediation_bound(spec):
    lo, hi = spec["ci95_N_per_kg"]
    d = spec["difference_N_per_kg"]
    weeks = spec["weeks"]
    return {
        "adjusted_difference_N_per_kg_per_week": d / weeks,
        "its_ci95": [lo / weeks, hi / weeks],
        "positive_fixed_control_gain_compatible_with_positive_lower_bound_N_per_kg": [0, 4*lo],
        "sensitivity_to_fixed_control_gain": [
            {"fixed_control_gain_N_per_kg": c, "contrast_per_week": (d - .25*c) / weeks,
             "conditional_ci95": [(lo - .25*c) / weeks, (hi - .25*c) / weeks]}
            for c in (.25, .5, 1, 1.5)
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-sources", type=Path)
    args = parser.parse_args()
    spec = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    if args.verify_sources:
        for name, metadata in spec["files"].items():
            if hashlib.sha256((args.verify_sources / name).read_bytes()).hexdigest() != metadata["sha256"]:
                raise ValueError(f"Source checksum mismatch: {name}")
        print(f"{len(spec['files'])} source file hashes match")
    output = {
        "experiment": "EXP-0144",
        "stage1": "HOLD",
        "strength": {name: strength_comparison(c) for name, c in spec["strength"].items()},
        "tissue": {name: tissue_comparison(c) for name, c in spec["tissue"].items()},
        "agergaard_peak_strain_digitized": figure_strain(spec["agergaard_peak_strain_pixels"]),
        "deng_partial_absolute_rate_contrast": mediation_bound(spec["deng_partial"]),
    }
    text = json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if path.read_text(encoding="utf-8") != text:
            raise SystemExit("EXP-0144 results differ")
        print("EXP-0144 exact replay")
    else:
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
