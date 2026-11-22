"""Check the two public Vesterhus CSVs and estimate participant-level changes."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, variance

from scipy.stats import t

HERE = Path(__file__).resolve().parent


def rows(path, manifest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest[path.name]["sha256"]:
        raise ValueError(f"Unexpected version of {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        data = list(csv.DictReader(stream))
    indexed = {row["FP"]: row for row in data}
    if len(indexed) != len(data) or "" in indexed:
        raise ValueError(f"Invalid participant identifier in {path.name}")
    return indexed


def paired_change(row, pre_key, post_key, relative=False):
    before, after = row[pre_key], row[post_key]
    if not before or not after:
        return None
    before, after = float(before), float(after)
    return 100 * (after / before - 1) if relative else after - before


def ci(point, var_mean, df):
    radius = t.ppf(.975, df) * math.sqrt(var_mean)
    return {"df": df, "estimate": point, "ci95": [point - radius, point + radius]}


def compare(groups, multiplier):
    a, b = groups["OCU"], groups["NOC"]
    v1, v2 = variance(a) / len(a), multiplier**2 * variance(b) / len(b)
    df = (v1 + v2)**2 / (v1*v1/(len(a)-1) + v2*v2/(len(b)-1))
    return ci(mean(a) - multiplier*mean(b), v1 + v2, df)


def summarize(data, metric):
    vals = {g: [v for row in data if row["Group"] == g and (v := metric(row)) is not None]
            for g in ("OCU", "NOC")}
    output = {}
    for group, values in vals.items():
        n = len(values)
        output[group] = {"n": n, **ci(mean(values), variance(values) / n, n - 1)}
    output["OCU_minus_NOC"] = compare(vals, 1)
    return output, vals


def analyze(directory):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    main = rows(directory / "All_data_except_SWV.csv", manifest)
    swv = rows(directory / "tendon_SWV_data.csv", manifest)
    if not swv.keys() <= main.keys() or any(swv[key]["group"] != main[key]["Group"] for key in swv):
        raise ValueError("Inconsistent group or missing participant in SWV join")
    for key, row in main.items():
        row.update(swv.get(key, {"V_pre_mean": "", "V_post_mean": ""}))
    data = list(main.values())
    outcomes = {
        "mvc_change_pct": ("KE_MIVC_PRE", "KE_MIVC_POST", True),
        "stiffness_change_N_per_mm": ("Stiffness_PRE", "Stiffness_POST", False),
        "mean_csa_change_mm2": ("PT_CSA_mean_PRE", "PT_CSA_mean_POST", False),
        "mean_swv_change_m_per_s": ("V_pre_mean", "V_post_mean", False),
    }
    result = {"main_rows": len(main), "swv_rows_joined": len(swv), "outcomes": {}}
    for name, spec in outcomes.items():
        output, vals = summarize(data, lambda row: paired_change(row, *spec))
        result["outcomes"][name] = output
        if name == "mvc_change_pct":
            output["OCU_minus_1p25_NOC"] = compare(vals, 1.25)
    for name, spec in list(outcomes.items())[1:]:
        linked = [row for row in data if paired_change(row, *spec) is not None]
        result[f"mvc_linked_to_{name}"], vals = summarize(
            linked, lambda row: paired_change(row, *outcomes["mvc_change_pct"])
        )
        result[f"mvc_linked_to_{name}"]["OCU_minus_1p25_NOC"] = compare(vals, 1.25)
    result["baseline_weight_kg_and_sessions"] = {
        group: {column: mean(float(row[column]) for row in data if row["Group"] == group)
                for column in ("Weight", "Sessions completed (n)")}
        for group in ("OCU", "NOC")
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dest = HERE / "VESTERHUS_RESULTS.json"
    serialized = json.dumps(analyze(args.source_directory), indent=2, allow_nan=False) + "\n"
    if args.check:
        if serialized != dest.read_text(encoding="utf-8"):
            raise SystemExit("Vesterhus results differ")
        print("Vesterhus: exact replay")
    else:
        dest.write_text(serialized, encoding="utf-8")
