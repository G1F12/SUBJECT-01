#!/usr/bin/env python3
"""Verify structural, mathematical, governance, and multi-channel tools/cpe45.py contract
conformance of research/targets/CPE45_CANDIDATE_FINAL_SPEC.json without modifying canonical CPE45.json.

IMPORTANT: Passing this script verifies JSON schema, schedule geometry, and software contract
conformance on synthetic test traces ONLY. It is NOT empirical physiological validation.
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


def build_synthetic_multichannel_session(
    spec: dict,
    episodes: list[cpe45.Episode],
    *,
    peak_temp_C: float = 38.1,
    power_scale: float = 1.0,
) -> dict:
    """Build a synthetic 100 Hz (effort) / 1 Hz (recovery) trace for software contract verification."""
    samples: list[cpe45.Sample] = []
    for idx, ep in enumerate(episodes):
        is_eff = ep.kind == "effort"
        step = 0.01 if is_eff else 1.0
        n_steps = int(round((ep.end_s - ep.start_s) / step))
        is_exp = ep.task_id == "explosive_sprint_6s"
        is_sub = ep.task_id == "submax_sustained_165s"
        # Mild late fatigue (~4-6% drop), well inside candidate bounds
        fatigue = 1.0 - 0.05 * (ep.start_s / 2700.0)
        for k in range(n_steps):
            t = round(ep.start_s + k * step, 4)
            if is_exp:
                pw = 900.0 * power_scale * fatigue
                fc = 450.0 * power_scale * fatigue
                sp = 4.0 * fatigue
            elif is_sub:
                pw = 240.0 * power_scale * fatigue
                fc = 160.0 * power_scale * fatigue
                sp = 2.6 * fatigue
            else:
                pw = 40.0 * power_scale
                fc = 40.0 * power_scale
                sp = 1.0
            ce = 0.010 * (1.0 + 0.08 * (t / 2700.0))
            me = 0.030 * (1.0 + 0.06 * (t / 2700.0))
            samples.append(
                cpe45.Sample(
                    time_s=t,
                    power_W=pw,
                    force_N=fc,
                    speed_m_s=sp,
                    acceleration_m_s2=0.2 if is_eff else 0.0,
                    coordination_error_m=ce,
                    maneuver_error_m=me,
                )
            )
        if idx == len(episodes) - 1:
            samples.append(
                cpe45.Sample(
                    time_s=2700.0,
                    power_W=40.0 * power_scale,
                    force_N=40.0 * power_scale,
                    speed_m_s=1.0,
                    acceleration_m_s2=0.0,
                    coordination_error_m=0.0108,
                    maneuver_error_m=0.0318,
                )
            )

    # 0.1 Hz thermal series covering [0, 2700] s
    thermal_samples = [
        cpe45.ThermalSample(
            time_s=float(t),
            core_temp_C=37.0 + (peak_temp_C - 37.0) * (t / 2700.0),
            skin_temp_C=33.0 + 1.5 * (t / 2700.0),
            ambient_temp_C=20.0,
            rh_pct=50.0,
        )
        for t in range(0, 2701, 10)
    ]

    # Concurrent cognitive trials in early [0, 540), late [2160, 2700], and post_45min [5280, 5580]
    trials: list[cpe45.Trial] = []
    for k in range(15):
        trials.append(cpe45.Trial(20.0 + 30.0 * k, "go_nogo_2back", 0.450, True, False))
    for k in range(15):
        trials.append(cpe45.Trial(2180.0 + 30.0 * k, "go_nogo_2back", 0.458, True, False))
    for k in range(12):
        trials.append(cpe45.Trial(5300.0 + 15.0 * k, "go_nogo_2back", 0.454, True, False))

    post_cfg = spec["post45_observation_times_s"]
    pbounds = {
        k: (float(v["window_s"][0]), float(v["window_s"][1]))
        for k, v in post_cfg.items()
        if isinstance(v, dict) and "window_s" in v
    }
    baseline_rec = cpe45.BaselineRecovery(task_id="knee_extensor_mvc", mvc_value=250.0, cmj_cm=40.0, va_pct=94.0, pain_nrs=0.0)
    probes = [
        cpe45.RecoveryProbe(2790.0, "post_acute", "knee_extensor_mvc", mvc_value=225.0, cmj_cm=37.0, va_pct=90.0, pain_nrs=1.0),
        cpe45.RecoveryProbe(5400.0, "post_45min", "knee_extensor_mvc", mvc_value=238.0, cmj_cm=38.8, va_pct=92.5, pain_nrs=0.5),
        cpe45.RecoveryProbe(89100.0, "post_24h", "knee_extensor_mvc", mvc_value=244.0, cmj_cm=39.2, va_pct=93.5, pain_nrs=0.5),
    ]

    win = spec["early_late_windows_s"]
    req = spec["sampling_and_sync_requirements"]
    return cpe45.analyze(
        samples,
        episodes,
        trials,
        early_end_s=win["early_end_s"],
        late_start_s=win["late_start_s"],
        max_gap_s=req["max_gap_s"],
        thermal_samples=thermal_samples,
        max_thermal_gap_s=req["max_thermal_gap_s"],
        recovery_probes=probes,
        baseline_recovery=baseline_rec,
        post45_window_bounds_s=pbounds,
        min_effort_hz=req["min_effort_hz"],
        min_overall_hz=req["min_overall_hz"],
        min_thermal_hz=req["min_thermal_hz"],
        stream_clock_offsets_s={"ergometer": 0.0, "imu_mocap": 0.012, "cognitive": -0.018, "thermal": 0.025},
        max_sync_offset_s=req["max_sync_offset_s"],
        body_mass_kg=75.0,
        critical_power_W=275.0,
        medical_abort_core_temp_C=spec["candidate_success_thresholds"]["thermoregulatory_limits"]["medical_abort_ceiling_C"],
    )


def main() -> None:
    # 1. Strict RFC-8259 parse & canonical untouched check
    spec_text = SPEC_PATH.read_text("utf-8")
    spec = json.loads(spec_text, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Non-RFC8259 constant: {x}")))
    canon = json.loads(CANON_PATH.read_text("utf-8"))
    if canon["success_thresholds"] is not None or canon["historical_experiments_cpe45_status"] != "not_assessed":
        raise SystemExit("FAIL: canonical CPE45.json was altered prematurely")

    # 2. Governance pre-registration & thermal separation checks
    assert spec["empirical_validation"] is False, "Candidate spec must keep empirical_validation=false"
    assert spec["status"] == "PREREGISTERED_CANDIDATE_NOT_EMPIRICALLY_VALIDATED"
    th_cfg = spec["candidate_success_thresholds"]["thermoregulatory_limits"]
    assert th_cfg["research_pass_ceiling_temperate_20C"] < th_cfg["medical_abort_ceiling_C"]
    assert th_cfg["research_pass_ceiling_warm_acclimatized_32C"] < th_cfg["medical_abort_ceiling_C"]

    # 3. Verify schedule totals match exactly [0, 2700] s
    episodes = build_episodes_from_spec(spec)
    assert math.isclose(episodes[-1].end_s, 2700.0, abs_tol=1e-9), f"Schedule ends at {episodes[-1].end_s}"
    eff_s = sum(e.end_s - e.start_s for e in episodes if e.kind == "effort")
    rec_s = sum(e.end_s - e.start_s for e in episodes if e.kind == "recovery")
    totals = spec["intensity_schedule"]["totals_over_2700s"]
    assert math.isclose(eff_s, totals["total_effort_s"], abs_tol=1e-9)
    assert math.isclose(rec_s, totals["total_recovery_s"], abs_tol=1e-9)
    assert math.isclose(eff_s / 2700.0, totals["duty_cycle"], abs_tol=1e-9)

    # 4. Full multi-channel synthetic contract verification (NOT empirical validation!)
    s1 = build_synthetic_multichannel_session(spec, episodes, peak_temp_C=38.05, power_scale=1.00)
    s2 = build_synthetic_multichannel_session(spec, episodes, peak_temp_C=38.15, power_scale=1.02)
    s3 = build_synthetic_multichannel_session(spec, episodes, peak_temp_C=38.10, power_scale=0.98)

    for s in (s1, s2, s3):
        assert s["target_achievement"] == "not_assessed"
        assert s["physiological_validation"] is False
        ev = cpe45.evaluate_session(s, spec, arm="temperate_20C")
        assert ev["overall_status"] == "CANDIDATE_SOFTWARE_PASS", f"Unexpected status: {ev}"
        assert ev["empirical_validation"] is False
        assert ev["medical_abort_triggered"] is False

    cohort_ev = cpe45.evaluate_cohort([s1, s2, s3], spec, arm="temperate_20C", n_boot=500, seed=20260420)
    assert cohort_ev["overall_cohort_status"] == "CANDIDATE_COHORT_SOFTWARE_PASS", f"Unexpected cohort status: {cohort_ev}"
    assert cohort_ev["empirical_validation"] is False
    assert cohort_ev["medical_aborts_n"] == 0

    print(
        f"PASS: {spec['spec_id']} conforms to multi-channel tools/cpe45.py contract "
        f"(episodes={len(episodes)}, effort_s={eff_s:.0f}, D={eff_s/2700.0:.4f}, "
        f"channels_evaluated={len(cohort_ev['channels'])}, canonical CPE45.json untouched; "
        f"SOFTWARE CONTRACT CHECK ONLY — NOT empirical validation)."
    )


if __name__ == "__main__":
    main()
