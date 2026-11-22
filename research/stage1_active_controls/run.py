"""Recalculate published-summary contrasts for EXP-0142."""

import argparse
import json
import math
from pathlib import Path
from statistics import mean, stdev

from scipy.stats import t

HERE = Path(__file__).resolve().parent


def change(pre, post, n, relative):
    """Mean change and its two marginal SE components (published SDs)."""
    base, base_sd = pre
    end, end_sd = post
    if relative:
        return (end / base - 1) * 100, (100 * end * base_sd / base**2 / math.sqrt(n),
                                       100 * end_sd / base / math.sqrt(n))
    return end - base, (base_sd / math.sqrt(n), end_sd / math.sqrt(n))


def se_at(components, rho):
    a, b = components
    return math.sqrt(max(0, a*a + b*b - 2*rho*a*b))


def extrema(components):
    return se_at(components, 1), se_at(components, -1)


def interval(point, se, critical):
    return [point - critical * se, point + critical * se]


def summary(point, low_se, high_se, df):
    critical = t.ppf(.975, df)
    return {
        "estimate": point,
        "ci95_narrowest": interval(point, low_se, critical),
        "ci95_widest": interval(point, high_se, critical),
    }


def compare(left, right, n_left, n_right, multiplier, paired, weeks=1):
    u, v = extrema(left[1])
    w, z = (multiplier * value for value in extrema(right[1]))
    if paired:
        lowest, highest = max(0, u-z, w-v), v+z
    else:
        lowest, highest = math.hypot(u, w), math.hypot(v, z)
    df = min(n_left, n_right) - 1
    point = left[0] - multiplier * right[0]
    ans = summary(point / weeks, lowest / weeks, highest / weeks, df)
    if paired:
        critical = t.ppf(.975, df)
        if u == v and w == z:
            ans["required_change_correlation_for_positive_lower_bound"] = (
                (v*v+z*z-(point/critical)**2)/(2*v*z) if point > 0 and v and z else None
            )
            ans["ci95_if_change_correlation_zero"] = interval(
                point / weeks, math.hypot(v, z) / weeks, critical
            )
            return ans
        ans["conditional_ci95"] = {}
        for rho_pre_post in (0, .5, .7, .9):
            a = se_at(left[1], rho_pre_post)
            b = multiplier * se_at(right[1], rho_pre_post)
            if a and b:
                threshold = (a*a + b*b - (point / critical)**2) / (2*a*b)
                ans["conditional_ci95"][str(rho_pre_post)] = {
                    "required_change_correlation_for_positive_lower_bound": threshold if point > 0 else None,
                    "if_change_correlation_zero": interval(point / weeks, math.hypot(a, b) / weeks, critical),
                }
    return ans


def single(change_stats, n, weeks=1):
    return summary(change_stats[0] / weeks, *(se / weeks for se in extrema(change_stats[1])), n - 1)


def analyze(case):
    n_i, n_c = case["n"]
    weeks = case["weeks"]
    if "change_mean_sem" in case:
        i, c = [(mean, (0, sem)) for mean, sem in case["change_mean_sem"]]
    elif "change_mean_sd" in case:
        i, c = [(mean, (0, sd / math.sqrt(n)))
                for (mean, sd), n in zip(case["change_mean_sd"], case["n"], strict=True)]
    else:
        i, c = [change(*pair, n, relative=True) for pair, n in zip(case["moments"], case["n"], strict=True)]
    result = {
        "intervention_rate_pp_per_week": single(i, n_i, weeks),
        "comparator_rate_pp_per_week": single(c, n_c, weeks),
        "adapt25_margin_pp_per_week": compare(i, c, n_i, n_c, 1.25, case["paired"], weeks),
        "intervention_gain_pct": single(i, n_i),
        "control_adjusted_gain_pp": compare(i, c, n_i, n_c, 1, case["paired"]),
    }
    if "moments" in case:
        (base, base_sd), (end, end_sd) = case["moments"][0]
        force_margin = end - 1.2 * base
        components = (1.2 * base_sd / math.sqrt(n_i), end_sd / math.sqrt(n_i))
        a, b = components
        critical = t.ppf(.975, n_i-1)
        result["force20_direct_margin_native_units"] = single((force_margin, components), n_i)
        result["force20_required_pre_post_correlation"] = (
            (a*a+b*b-(force_margin/critical)**2)/(2*a*b) if force_margin > 0 else None
        )
    return result


def analyze_running(visits):
    """Summarize step-averaged paired changes using participants as replicates."""
    channels = ("length_excursion_mm", "recoil_proxy_mm", "estimated_peak_force_magnitude_N")
    result = {}
    for group in ("TG", "CG"):
        pre, post = (visits[f"{group}_{visit}"] for visit in ("pre", "post"))
        keys = sorted(pre.keys() & post.keys())
        n = len(keys)
        result[group] = {
            "paired_n": n,
            "paired_n_also_with_ankle_moment": sum(
                pre[key]["has_ankle_moment"] and post[key]["has_ankle_moment"] for key in keys
            ),
            "negative_signed_peaks": [sum(row["negative_signed_peaks"] for row in v.values()) for v in (pre, post)],
            "total_steps": [sum(row["steps"] for row in v.values()) for v in (pre, post)],
        }
        for channel in channels:
            paired = [(pre[key][channel], post[key][channel]) for key in keys]
            delta = [end - base for base, end in paired]
            result[group][channel] = {
                "pre_mean": mean(a for a, _ in paired),
                "post_mean": mean(b for _, b in paired),
                "mean_change": mean(delta),
                "ci95": interval(mean(delta), stdev(delta) / math.sqrt(n), t.ppf(.975, n-1)),
            }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inputs = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    output = {"experiment": "EXP-0142", "stage1": "HOLD", "cases": {}, "tissue": {}}
    for name, case in inputs["cases"].items():
        output["cases"][name] = analyze(case)
    for name, case in inputs["tissue"].items():
        output["tissue"][name] = single(change(case["pre"], case["post"], case["n"], False), case["n"])
    for name, (point, sd, n) in inputs["additional_inputs"]["malliaras_high_tissue_pct_mean_sd_n"].items():
        output["tissue"][f"malliaras_high_{name}"] = single((point, (0, sd / math.sqrt(n))), n)
    rehab_mean, rehab_sd, rehab_n = inputs["additional_inputs"]["rehab_high_load_mvc_percent_mean_sd_n"]
    output["rehab_high_load_mvc"] = {
        "estimate_pct": rehab_mean,
        "ci95_pct": interval(rehab_mean, rehab_sd / math.sqrt(rehab_n), t.ppf(.975, rehab_n-1)),
    }
    visits = json.loads((HERE / "WERKHAUSEN_STANCE.json").read_text(encoding="utf-8"))
    output["werkhausen_running_diagnostic"] = analyze_running(visits)
    serialized = json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if path.read_text(encoding="utf-8") != serialized:
            raise SystemExit("EXP-0142 results differ")
        print("EXP-0142: exact replay")
    else:
        path.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
