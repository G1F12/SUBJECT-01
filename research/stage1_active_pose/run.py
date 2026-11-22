"""Replay EXP-0147 from the versioned source transcription."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.stats import t

HERE = Path(__file__).resolve().parent


def interval(point, se, n):
    error = float(t.ppf(.975, n - 1)) * se
    return [point, point - error, point + error]


def paired(i, c, n, weeks):
    gain, sd_i = i
    control, sd_c = c
    scale = math.sqrt(n)
    return {
        "control_rate": interval(control / weeks, sd_c / scale / weeks, n),
        "intervention_pct": interval(gain, sd_i / scale, n),
        "adapt25_by_correlation": {
            str(r): interval((gain - 1.25 * control) / weeks,
                             math.sqrt((sd_i - 1.25 * sd_c)**2 + 2 * (1-r) * sd_i * 1.25 * sd_c)
                             / scale / weeks, n)
            for r in (-1, 0, .5, .9, 1)
        },
        "adjusted_force20_widest_pp": interval(gain - control, (sd_i + sd_c) / scale, n),
    }


def relative(values, n):
    (a, sa), (b, sb) = values
    return 100 * (b / a - 1), 100 * (b * sa / a**2 + sb / a) / math.sqrt(n)


def compare(i, c, ni, nc, weeks, independent=False):
    pi, se_i = relative(i, ni)
    pc, se_c = relative(c, nc)
    n = min(ni, nc)
    return {
        "gain_pct": pi,
        "control_pct": pc,
        "control_rate": interval(pc / weeks, se_c / weeks, nc),
        "adapt25": interval((pi - 1.25 * pc) / weeks, (se_i + 1.25 * se_c) / weeks, n),
        "force20": interval(pi - pc, math.hypot(se_i, se_c) if independent else se_i + se_c, n),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    source = (HERE / "SOURCES.json").read_bytes()
    d = json.loads(source)
    if args.source_dir:
        for filename, (_, digest) in d["files"].items():
            if hashlib.sha256((args.source_dir / filename).read_bytes()).hexdigest() != digest:
                parser.error(f"Digest mismatch: {filename}")
        print(f"Verified {len(d['files'])} source digests")
    k, ts, y, f = (d[key] for key in ("kubo_ishigaki", "tsai", "kubo_yata", "foure"))
    i, c = (k["individual_gain_pct_sd"][key] for key in ("iso", "ply"))
    main_pair = paired(i, c, k["n"], k["weeks"])
    half = k["rounding_half_step"]
    adverse = paired((i[0]-half, i[1]+half), (c[0]+half, c[1]+half), k["n"], k["weeks"])
    tissue = {}
    for key in ("iso_ramp", "iso_ballistic", "ply_ramp", "ply_ballistic"):
        (a, sa), (b, sb) = k[key+"_peak_elongation_mm"]
        tissue[key] = interval(b-a, (sa+sb)/math.sqrt(k["n"]), k["n"])
    moments, counts = ts["mvc_nm_mean_sd"], ts["summary_n_legs"]
    matches = {}
    for first, second in (("LFLV", "HFLV"), ("LFHV", "HFHV")):
        for a, b in ((first, second), (second, first)):
            matches[f"{a}_vs_{b}"] = {
                str(w): compare([moments[a][0], moments[a][j]], [moments[b][0], moments[b][j]],
                                counts[a], counts[b], w)
                for j, w in enumerate(ts["weeks"][1:], 1)
            }
    top, bottom = ts["strain_fig3c_y_12_and_2_pct"]
    out = {
        "status": "HOLD",
        "source_manifest_sha256": hashlib.sha256(source).hexdigest(),
        "kubo_ishigaki": {
            "mvc": main_pair,
            "adverse_rounding_adapt25": adverse["adapt25_by_correlation"]["-1"],
            "adverse_rounding_control": interval((c[0]-half)/k["weeks"],
                                                 (c[1]+half)/math.sqrt(k["n"])/k["weeks"], k["n"]),
            "moment_angle_deg": k["isometric_mvc_angle_deg_plantarflexion"],
            "tissue_angle_deg": k["tendon_assessment_angle_deg_plantarflexion"],
            "tissue_change_mm_widest": tissue,
            "table_ratio_of_means": {key: relative(value, k["n"])[0] for key, value in k["mvc_nm_mean_sd"].items()},
        },
        "tsai_active": matches,
        "tsai_strain_median_pct": {
            key: [12 - 10*(y-top)/(bottom-top) for y in rows]
            for key, rows in ts["strain_fig3c_median_y"].items()
        },
        "kubo_yata_mvc": compare(y["mvc_nm_mean_sd"]["con"], y["mvc_nm_mean_sd"]["ecc"], 9, 9, y["weeks"]),
        "kubo_yata_1rm": paired(*y["individual_1rm_gain_pct_sd"].values(), y["paired_legs_n"], y["weeks"]),
        "foure": compare(*f["mvc_nm_mean_sd"].values(), *f["n"], f["weeks"], independent=True),
    }
    encoded = json.dumps(out, indent=2, allow_nan=False) + "\n"
    path = HERE / "RESULTS.json"
    if args.check:
        if path.read_text(encoding="utf-8") != encoded:
            parser.error("RESULTS.json differs from replay")
        print("EXP-0147 exact replay")
    else:
        path.write_text(encoded, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
