#!/usr/bin/env python3
"""Verify structural, mathematical, and tools/cpe45.py contract conformance of
research/targets/CPE45_CANDIDATE_FINAL_SPEC.json without modifying canonical CPE45.json.

NOTE: This script verifies schedule geometry, JSON strictness (RFC 8259), and tools/cpe45.py
API compatibility on a synthetic conformance trace. Passing this script is NOT empirical validation.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cpe45  # noqa: E402

SPEC_PATH = ROOT / "research" / "targets" / "CPE45_CANDIDATE_FINAL_SPEC.json"
CANON_PATH = ROOT / "research" / "targets" / "CPE45.json"


def build_episodes_from_spec(spec: dict) -> list[cpe45.Episode]:
    sched = spec["intensity_schedule"]
    eps: list[cpe45.Episode] = []
    t = 0.0
    for _ in range(int(sched["n_blocks"])):
        for seg in sched["per_block_sequence"]:
            for _ in range(int(seg["repeat"])):
                e_dur = float(seg["effort"]["duration_s"])
                r_dur = float(seg["recovery"]["duration_s"])
                eps.append(cpe45.Episode(t, t + e_dur, "effort", seg["effort"]["task_id"]))
                t += e_dur
                eps.append(cpe45.Episode(t, t + r_dur, "recovery", seg["recovery"]["task_id"]))
                t += r_dur
    return eps


def main() -> None:
    # 1. Strict RFC-8259 parse & canonical untouched check
    spec_text = SPEC_PATH.read_text("utf-8")
    spec = json.loads(spec_text, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Non-RFC8259 constant: {x}")))
    canon = json.loads(CANON_PATH.read_text("utf-8"))
    if canon["success_thresholds"] is not None or canon["historical_experiments_cpe45_status"] != "not_assessed":
        raise SystemExit("FAIL: canonical CPE45.json was altered prematurely")

    # 2. Verify schedule totals match exactly [0, 2700] s
    episodes = build_episodes_from_spec(spec)
    assert math.isclose(episodes[-1].end_s, 2700.0, abs_tol=1e-9), f"Schedule ends at {episodes[-1].end_s}"
    eff_s = sum(e.end_s - e.start_s for e in episodes if e.kind == "effort")
    rec_s = sum(e.end_s - e.start_s for e in episodes if e.kind == "recovery")
    totals = spec["intensity_schedule"]["totals_over_2700s"]
    assert math.isclose(eff_s, totals["total_effort_s"], abs_tol=1e-9)
    assert math.isclose(rec_s, totals["total_recovery_s"], abs_tol=1e-9)
    assert math.isclose(eff_s / 2700.0, totals["duty_cycle"], abs_tol=1e-9)

    # 3. Verify tools/cpe45.py contract execution on a synthetic conformance trace (NOT empirical validation!)
    win = spec["early_late_windows_s"]
    post_cfg = spec["post45_observation_times_s"]
    samples = [
        cpe45.Sample(float(t), 200.0, 400.0, 2.0, 0.5, 0.008, 0.02)
        for t in range(0, 2701)
    ]
    trials = [
        cpe45.Trial(float(30 + 36 * k), "go_nogo_2back", 0.45, True, False)
        for k in range(74)
    ]
    post_samples = [
        cpe45.Sample(post_cfg["post_acute_window_s"][0], 200.0, 380.0, 1.9, 0.4, 0.009, 0.02),
        cpe45.Sample(post_cfg["post_acute_window_s"][0] + 1.0, 200.0, 380.0, 1.9, 0.4, 0.009, 0.02),
    ]
    out = cpe45.analyze(
        samples,
        episodes,
        trials,
        early_end_s=win["early_end_s"],
        late_start_s=win["late_start_s"],
        max_gap_s=win["max_gap_s"],
        post_samples=post_samples,
        post_task_id="explosive_sprint_6s",
    )
    assert out["target_achievement"] == "not_assessed"
    assert out["physiological_validation"] is False
    print(
        f"PASS: CPE45_CANDIDATE_FINAL_SPEC.json conforms to tools/cpe45.py contract "
        f"(episodes={len(episodes)}, effort_s={eff_s:.0f}, D={eff_s/2700.0:.4f}, "
        f"canonical CPE45.json untouched; arithmetic conformance only — NOT empirical validation)."
    )


if __name__ == "__main__":
    main()
