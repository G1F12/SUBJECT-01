"""Extract participant-by-visit running summaries from PeerJ 6764 supplement 1."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat

HERE = Path(__file__).resolve().parent


def extract(path):
    source = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    if hashlib.sha256(path.read_bytes()).hexdigest() != source["files"]["werkhausen.mat"]["sha256"]:
        raise ValueError("Unexpected Werkhausen supplement version")
    data = loadmat(path, simplify_cells=True)["data"]
    result = {}
    for visit, fields in sorted(data.items()):
        length = fields["AT"]
        force = fields["AT_force"]["normal"]
        moment = fields["Ank_Mom"]
        if length.keys() != force.keys():
            raise ValueError(f"Length and force participant keys differ at {visit}")
        participants = {}
        for participant in sorted(length):
            traces = length[participant]
            estimates = force[participant]
            if traces.keys() != estimates.keys():
                raise ValueError(f"Length and force step keys differ at {visit} {participant}")
            a = np.stack(list(traces.values()))
            b = np.stack([estimates[key] for key in traces])
            if a.shape[1:] != (101,) or b.shape != a.shape or not np.isfinite([a, b]).all():
                raise ValueError(f"Invalid stance signal at {visit} {participant}")
            abs_peak = np.argmax(np.abs(b), axis=1)
            force_at_peak = b[np.arange(len(b)), abs_peak]
            participants[participant] = {
                "steps": len(a),
                "length_excursion_mm": round(float(np.ptp(a, axis=1).mean()), 9),
                "recoil_proxy_mm": round(float((a.max(axis=1) - a[:, -1]).mean()), 9),
                "estimated_peak_force_magnitude_N": round(float(np.abs(force_at_peak).mean()), 9),
                "negative_signed_peaks": int(np.sum(force_at_peak < 0)),
                "has_ankle_moment": participant in moment,
            }
        result[visit] = participants
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mat", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = HERE / "WERKHAUSEN_STANCE.json"
    content = json.dumps(extract(args.mat), indent=2, allow_nan=False) + "\n"
    if args.check:
        if content != destination.read_text(encoding="utf-8"):
            raise SystemExit("Werkhausen extraction differs")
        print("Werkhausen: exact extraction replay")
    else:
        destination.write_text(content, encoding="utf-8")
