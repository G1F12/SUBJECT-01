"""EXP-0143 — linked workbook records and bounded longitudinal contrasts."""

import argparse
import hashlib
import json
import math
from collections import Counter
from itertools import product
from pathlib import Path
from statistics import mean, stdev, variance

from openpyxl import load_workbook
from scipy.stats import t

HERE = Path(__file__).resolve().parent


def interval(value, se, df):
    margin = t.ppf(.975, df) * se
    return {"estimate": value, "ci95": [value - margin, value + margin]}


def point_sample(values):
    return {"n": len(values), **interval(mean(values), stdev(values) / math.sqrt(len(values)), len(values)-1)}


def sample_ratio(pairs):
    start, end = map(mean, zip(*pairs, strict=True))
    values = [100 * (b - end * a / start) / start for a, b in pairs]
    return interval(100 * (end / start - 1), stdev(values) / math.sqrt(len(values)), len(values)-1)


def compare_samples(a, b, multiplier, weeks):
    va, vb = variance(a) / len(a), multiplier**2 * variance(b) / len(b)
    df = (va + vb)**2 / (va*va/(len(a)-1) + vb*vb/(len(b)-1))
    return interval((mean(a) - multiplier * mean(b)) / weeks, math.sqrt(va + vb) / weeks, df)


def audited_source(directory, files, name):
    path = directory / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != files[name]["sha256"]:
        raise ValueError(f"Unexpected version of {name}")
    return path


def mcmahon(directory, files):
    s1 = load_workbook(audited_source(directory, files, "mcmahon_s1.xlsx"), read_only=True, data_only=True)
    s2 = load_workbook(audited_source(directory, files, "mcmahon_s2.xlsx"), read_only=True, data_only=True)
    rows = list(s1["Sheet1"].values)
    companion = list(s2["Correlations by gender"].values)
    results, changes = {}, {}
    for group, start, end, second_start in (("men", 4, 11, 7), ("women", 18, 25, 23)):
        records = []
        for index in range(start, end + 1):
            row = rows[index-1]
            ids = {row[j-1] for j in (1, 6, 21, 47, 59, 73)}
            if len(ids) != 1 or not isinstance(row[5], int):
                raise ValueError(f"Unmatched blocks on S1 row {index}")
            other = companion[second_start+index-start-1]
            shared_s2 = (other[11], other[24]) == (row[5], row[5]) and all(
                isinstance(other[k-1], (int, float)) and math.isclose(row[j-1], other[k-1])
                for j, k in ((57, 22), (69, 35))
            )
            records.append((row[5], row[6], row[7], row[56], row[68], shared_s2))
        counts = Counter(r[0] for r in records)
        ambiguous = [index for index, row in enumerate(records) if counts[row[0]] > 1]
        peak_pairs = [(r[1], r[2]) for r in records]
        changes[group] = [100 * (b/a-1) for a, b in peak_pairs]
        result = {
            "row_count": len(records),
            "distinct_published_codes": len(counts),
            "ambiguous_s1_excel_rows": [start+i for i in ambiguous],
            "s2_rows_matching_code_and_k100": sum(row[-1] for row in records),
            "s1_mvc_pct_mean_individual_changes": point_sample(changes[group]),
            "s1_mvc_pct_change_of_means_delta_ci": sample_ratio(peak_pairs),
            "s1_k100_pct_mean_individual_changes": point_sample([100*(r[4]/r[3]-1) for r in records]),
            "s1_mvc_pp_per_week": point_sample([r/8 for r in changes[group]]),
            "fewer_rows_sensitivity": {},
        }
        for mask in product((False, True), repeat=len(ambiguous)):
            excluded = {i for i, omit in zip(ambiguous, mask, strict=True) if omit}
            if excluded:
                selected = [x for i, x in enumerate(changes[group]) if i not in excluded]
                label = ",".join(str(i + start) for i in sorted(excluded))
                result["fewer_rows_sensitivity"][label] = point_sample(selected)
        results[group] = result
    results["exploratory_men_minus_1p25_women_pp_per_week"] = compare_samples(
        changes["men"], changes["women"], 1.25, 8
    )
    s1.close()
    s2.close()
    return results


def trend(points, x):
    """Delta-method maximum SE for an OLS slope divided by baseline mean."""
    centered = [x_i - mean(x) for x_i in x]
    weights = [u / sum(v*v for v in centered) for u in centered]
    slope = sum(w*p[0] for w, p in zip(weights, points, strict=True))
    baseline = points[0][0]
    gradient = [100 * w / baseline for w in weights]
    gradient[0] -= 100 * slope / baseline**2
    return 100 * slope / baseline, sum(abs(g)*p[1] for g, p in zip(gradient, points, strict=True))


def trend_comparison(i, c, i_times, c_times, df):
    gain_i, se_i = trend(i, i_times)
    gain_c, se_c = trend(c, c_times)
    return {
        "I_pct": interval(gain_i, se_i, df),
        "C_pct": interval(gain_c, se_c, df),
        "I_minus_1p25_C": interval(gain_i - 1.25*gain_c, math.hypot(se_i, 1.25*se_c), df),
        "I_minus_C": interval(gain_i - gain_c, math.hypot(se_i, se_c), df),
    }


def weidlich(spec):
    moments = {}
    for group, values in spec["normalized_moment_mean_sd_n"].items():
        moments[group] = [(value, sd/math.sqrt(n)) for value, sd, n in values]
    i, c = moments["I"], moments["C"]
    x, y = spec["I_weeks"], spec["C_weeks"]
    return {
        "all_visits_pp_per_week": trend_comparison(i, c, x, y, 9),
        "ends_pp_per_week": trend_comparison(i[::3], c[::3], x[::3], y[::3], 9),
        "common_grid_pp_per_week": trend_comparison(i, c, y, y, 9),
        "end_to_end_gain_pct": trend_comparison(i[::3], c[::3], [0, 1], [0, 1], 9),
        "published_tissue_summary": spec["tissue"],
        "across_panel_linkage": "no complete pairing from figures because some markers overlap and the article gives no cross-panel key",
    }


def eriksen(spec):
    zero_y, high_y = spec["calibration_y"]
    scale = 250 / (zero_y-high_y)
    groups = {k: [((zero_y-top)*scale, (top-cap)*scale) for top, cap in group]
              for k, group in spec["pixels"].items()}
    results = {
        "digitized_moment_mean_sem": groups,
        "active_pp_per_month": trend_comparison(groups["HRT"], groups["MRT"], [0, 12], [0, 12], 9),
        "inactive_comparison_pp": trend_comparison(groups["HRT"], groups["CON"], [0, 1], [0, 1], 9),
        "published_tissue_summary": spec["tissue"],
    }
    force = spec["tissue"]["max_tendon_force_N_mean_sem"]
    strain = spec["tissue"]["max_strain_pct_mean_sem"]
    results["native_max_HRT_tendon_force_change_pct"] = trend_comparison(
        force["HRT"], force["MRT"], [0, 1], [0, 1], 9
    )["I_pct"]
    results["native_max_strain_change_pp"] = {
        group: interval(post[0] - pre[0], pre[1] + post[1], spec["tissue"]["group_n"][group]-1)
        for group, (pre, post) in strain.items()
    }
    sensitivity = []
    for offsets in product((-1, 1), repeat=8):
        variants = []
        for k, pairs in enumerate((spec["pixels"]["HRT"], spec["pixels"]["MRT"])):
            variants.append([((zero_y-(p+offsets[k*4+2*j]))*scale,
                              (p-cap+offsets[k*4+2*j]-offsets[k*4+2*j+1])*scale)
                             for j, (p, cap) in enumerate(pairs)])
        result = trend_comparison(*variants, [0, 12], [0, 12], 9)["I_minus_1p25_C"]
        sensitivity.append(result)
    results["pixel_sensitivity_active_pp_per_month"] = {
        "estimate_range": [min(r["estimate"] for r in sensitivity), max(r["estimate"] for r in sensitivity)],
        "ci95_envelope": [min(r["ci95"][0] for r in sensitivity), max(r["ci95"][1] for r in sensitivity)],
    }
    return results


def rieder(spec):
    means = spec["moment_means"]
    i, c, w = [100 * (means[k][1] / means[k][0] - 1) for k in ("HSR", "WBV", "WLC")]
    return {
        "HSR_gain_pct": i, "WBV_gain_pct": c, "WLC_gain_pct": w,
        "active_nominal_margin_pp_per_week": (i - 1.25*c)/12,
        "waitlist_adjusted_gain_pp": i-w,
        "paired_change_pct_fixed_baseline_and_published_ci": {
            k: [100*v/means[k][0] for v in stats]
            for k, stats in spec["paired_change_Nm_and_published_ci"].items()
        },
        "published_HSR_WBV_adjusted_difference_Nm": spec["published_HSR_WBV_adjusted_difference_Nm"],
        "published_tissue_summary": spec["tissue"],
    }


def bogdanis(spec):
    output = []
    for measured in spec["measurements"]:
        gain = measured["S_MTU_gain_pct"]
        reference = spec["L_MTU_all_angles_gain_pct"]
        output.append({
            **measured,
            "max_angle_specific_control_gain_pct_at_force20_point_threshold": gain - 20,
            "max_angle_specific_control_gain_pct_at_adapt25_point_threshold": gain / 1.25,
            "force20_pp_if_control_equals_all_angle_mean": gain - reference,
            "adapt25_pp_per_week_if_control_equals_all_angle_mean": (gain - 1.25*reference) / spec["weeks"],
        })
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-sources", action="store_true")
    args = parser.parse_args()
    source = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    if args.verify_sources:
        for name in source["files"]:
            audited_source(args.source_directory, source["files"], name)
        print(f"{len(source['files'])} source hashes matched")
    output = {
        "experiment": "EXP-0143", "stage1": "HOLD",
        "weidlich": weidlich(source["weidlich"]),
        "eriksen": eriksen(source["eriksen"]),
        "mcmahon": mcmahon(args.source_directory, source["files"]),
        "rieder": rieder(source["rieder"]),
        "bogdanis": bogdanis(source["bogdanis"]),
    }
    rendered = json.dumps(output, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if rendered != path.read_text(encoding="utf-8"):
            raise SystemExit("EXP-0143 results differ")
        print("EXP-0143 exact replay")
    else:
        path.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
