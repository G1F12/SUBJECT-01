"""Score the frozen Pennes model on measured Fujii temperatures."""
import argparse
from collections import defaultdict
from datetime import datetime, time, timedelta
import json
import math
from pathlib import Path
import re
from statistics import mean

import numpy as np
from openpyxl import load_workbook

from run_audit import HERE, load_runner, sha256, text_sha256

FILES = {
    "dataset.xlsx": "4d294670fdb033d12f2e4d6059b9a02a13d31a7c35932643be2d9dae9b6ddcfa",
    "metadata.xlsx": "62ce3643573a5149ec2b6a2a49d583c04d973a055b48403bd8e342d5eaeaa5c8",
}
OFFSET_S = 300
WINDOW_S = 15
HUMIDITIES = (0.30, 0.50, 0.70)


def metadata(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    participants = list(workbook["Participants"].values)
    characteristics = {
        participant: (mass, {"M": 90, "F": 60}[sex])
        for participant, sex, mass in zip(participants[2][2:], participants[3][2:], participants[6][2:])
    }
    month_day = None
    temperatures = ()
    sessions = []
    for row in workbook["Timing"].values:
        header = re.match(r"^(\d+)/(\d+)\s", str(row[0]))
        if header:
            month_day = (int(header[1]), int(header[2]))
            temperatures = [int(re.match(r"\d+", str(row[i]))[0]) for i in (2, 6, 10)]
            continue
        if row[1] not in characteristics:
            continue
        for i, ambient in zip((2, 6, 10), temperatures):
            onset, wind = row[i + 1:i + 3]
            if isinstance(onset, time) and isinstance(wind, time):
                sessions.append((row[1], month_day, ambient, onset, wind))
    workbook.close()
    return characteristics, sessions


def observed_changes(path, sessions):
    by_date = defaultdict(list)
    for index, (participant, month_day, _, _, _) in enumerate(sessions):
        by_date[(participant, *month_day)].append(index)
    years = defaultdict(set)
    windows = defaultdict(dict)
    duplicate_windows = set()
    workbook = load_workbook(path, read_only=True, data_only=True)
    rows = iter(workbook["pred20250509"].values)
    if next(rows)[:4] != ("time", "participant id", "day #", "T_es"):
        raise ValueError("Unexpected temperature workbook header")
    for timestamp, participant, _, observed, *_ in rows:
        if not isinstance(timestamp, datetime):
            continue
        for index in by_date.get((participant, timestamp.month, timestamp.day), ()):
            _, _, _, onset, wind = sessions[index]
            years[index].add(timestamp.year)
            onset = datetime.combine(timestamp.date(), onset)
            wind = datetime.combine(timestamp.date(), wind)
            if onset + timedelta(seconds=OFFSET_S + WINDOW_S) >= wind:
                continue
            if not isinstance(observed, (int, float)) or not math.isfinite(observed):
                continue
            relative_s = (timestamp - onset).total_seconds()
            for offset in (0, OFFSET_S):
                if abs(relative_s - offset) <= WINDOW_S:
                    key = (index, offset)
                    if timestamp in windows[key]:
                        duplicate_windows.add(key)
                    windows[key][timestamp] = observed
    workbook.close()
    outcomes = []
    for index, (participant, _, ambient, _, _) in enumerate(sessions):
        keys = [(index, 0), (index, OFFSET_S)]
        if len(years[index]) != 1 or any(key in duplicate_windows or len(windows[key]) < 21 for key in keys):
            continue
        start, finish = [mean(windows[key].values()) for key in keys]
        outcomes.append((participant, ambient, finish - start))
    return outcomes


def score(cases, characteristics, module, humidity):
    errors = defaultdict(list)
    climate_pairs = defaultdict(list)
    predictions = {}
    for participant, ambient, change in cases:
        key = (participant, ambient)
        if key not in predictions:
            mass, nominal_W = characteristics[participant]
            run = module.simulate_4layer_pennes_2700s(nominal_W, 1.0, ambient, humidity, body_mass_kg=mass)
            samples = {row["time_s"]: row["T_core_C"] for row in run["trace_30s"]}
            predictions[key] = samples[OFFSET_S] - samples[0]
        error = predictions[key] - change
        errors[participant].append((abs(change), abs(error), error))
        climate_pairs[ambient].append((change, predictions[key]))
    participant_scores = np.array([
        np.mean(errors[participant], axis=0) for participant in sorted(errors)
    ])
    if len(participant_scores) < 2:
        raise ValueError("At least two eligible participant clusters are needed")
    paired = participant_scores[:, 0] - participant_scores[:, 1]
    rng = np.random.default_rng(20261119)
    resamples = rng.choice(paired, size=(10000, len(paired)), replace=True).mean(axis=1)
    return {
        "relative_humidity": humidity,
        "persistence_mae_C": float(participant_scores[:, 0].mean()),
        "pennes_mae_C": float(participant_scores[:, 1].mean()),
        "pennes_bias_C": float(participant_scores[:, 2].mean()),
        "delta_mae_ci95_C": np.quantile(resamples, (0.025, 0.975)).tolist(),
        "means_by_ambient_C": {
            str(ambient): {
                "observed_change_C": mean(change for change, _ in climate_pairs[ambient]),
                "predicted_change_C": mean(prediction for _, prediction in climate_pairs[ambient]),
            }
            for ambient in sorted(climate_pairs)
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "THERMAL_TRANSFER.json")
    args = parser.parse_args()
    for filename, digest in FILES.items():
        if sha256(args.data_dir / filename) != digest:
            raise ValueError(f"Source hash mismatch: {filename}")
    characteristics, scheduled = metadata(args.data_dir / "metadata.xlsx")
    cases = observed_changes(args.data_dir / "dataset.xlsx", scheduled)
    module = load_runner(63)
    scores = [score(cases, characteristics, module, rh) for rh in HUMIDITIES]
    result = {
        "experiment_id": "EXP-0066",
        "source": "https://doi.org/10.5281/zenodo.19835255",
        "source_license": "CC BY 4.0",
        "publisher_md5": {
            "dataset.xlsx": "4b352838525d8c5ee918f9d7076cd95a",
            "metadata.xlsx": "14ddfe8f4655c306685daebcb382eec6",
        },
        "raw_file_sha256": FILES,
        "protocol_sha256": text_sha256(HERE / "THERMAL_TRANSFER_PROTOCOL.md"),
        "runner_sha256": text_sha256(Path(__file__)),
        "metadata_participants": len(characteristics),
        "scheduled_sessions_with_own_timing": len(scheduled),
        "eligible_sessions": len(cases),
        "eligible_participants": len({row[0] for row in cases}),
        "sessions_by_ambient_C": {str(t): sum(row[1] == t for row in cases) for t in (10, 20, 30)},
        "scores": scores,
        "limited_transfer_gate_passed": all(row["delta_mae_ci95_C"][0] > 0 for row in scores),
        "target_cpe45": "not_assessed",
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
