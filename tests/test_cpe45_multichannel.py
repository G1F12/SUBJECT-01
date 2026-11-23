"""Automated multi-channel software contract tests for tools/cpe45.py and
research/targets/CPE45_CANDIDATE_FINAL_SPEC.json.

IMPORTANT: All data in this file are synthetic test fixtures designed solely to verify
software contract enforcement (missing channels, sync skew, Hz sampling floor, threshold
bounds, medical-abort separation, post45 window/task_id integrity, and cohort IUT CIs).
Passing these tests does NOT constitute empirical or physiological validation of CPE45.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cpe45  # noqa: E402
import verify_cpe45_candidate_spec as verifier  # noqa: E402

SPEC = json.loads((ROOT / "research" / "targets" / "CPE45_CANDIDATE_FINAL_SPEC.json").read_text("utf-8"))
EPISODES = verifier.build_episodes_from_spec(SPEC)
WIN = SPEC["early_late_windows_s"]
REQ = SPEC["sampling_and_sync_requirements"]
PBOUNDS = {
    k: (float(v["window_s"][0]), float(v["window_s"][1]))
    for k, v in SPEC["post45_observation_times_s"].items()
    if isinstance(v, dict) and "window_s" in v
}


def make_fast_samples(
    *,
    effort_hz: float = 100.0,
    recovery_hz: float = 1.0,
    late_exp_power_mult: float = 0.94,
    late_sub_power_mult: float = 0.96,
    late_force_mult: float = 0.96,
    late_speed_mult: float = 0.96,
    late_coord_mult: float = 1.05,
    late_man_mult: float = 1.05,
    power_scale: float = 1.0,
) -> list[cpe45.Sample]:
    """Generate a synthetic 2700-s trace with controlled sampling rates and late-vs-early shifts."""
    samples: list[cpe45.Sample] = []
    eff_dt = 1.0 / effort_hz
    rec_dt = 1.0 / recovery_hz
    for idx, ep in enumerate(EPISODES):
        is_eff = ep.kind == "effort"
        step = eff_dt if is_eff else rec_dt
        n_steps = max(1, int(round((ep.end_s - ep.start_s) / step)))
        frac = ep.start_s / 2700.0
        if ep.task_id == "explosive_sprint_6s":
            pw = 900.0 * power_scale * (1.0 - (1.0 - late_exp_power_mult) * frac)
            fc = 450.0 * power_scale * (1.0 - (1.0 - late_force_mult) * frac)
            sp = 4.0 * (1.0 - (1.0 - late_speed_mult) * frac)
        elif ep.task_id == "submax_sustained_165s":
            pw = 240.0 * power_scale * (1.0 - (1.0 - late_sub_power_mult) * frac)
            fc = 160.0 * power_scale * (1.0 - (1.0 - late_force_mult) * frac)
            sp = 2.6 * (1.0 - (1.0 - late_speed_mult) * frac)
        else:
            pw = 40.0 * power_scale
            fc = 40.0 * power_scale
            sp = 1.0
        ce = 0.010 * (1.0 + (late_coord_mult - 1.0) * frac)
        me = 0.030 * (1.0 + (late_man_mult - 1.0) * frac)
        for k in range(n_steps):
            t = round(ep.start_s + k * step, 5)
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
        if idx == len(EPISODES) - 1:
            samples.append(
                cpe45.Sample(
                    time_s=2700.0,
                    power_W=pw,
                    force_N=fc,
                    speed_m_s=sp,
                    acceleration_m_s2=0.0,
                    coordination_error_m=ce,
                    maneuver_error_m=me,
                )
            )
    return samples


def make_thermal(*, peak_temp_C: float = 38.1, dt_s: float = 10.0) -> list[cpe45.ThermalSample]:
    n = int(round(2700.0 / dt_s))
    return [
        cpe45.ThermalSample(
            time_s=round(k * dt_s, 4),
            core_temp_C=37.0 + (peak_temp_C - 37.0) * ((k * dt_s) / 2700.0),
            skin_temp_C=33.5,
            ambient_temp_C=20.0,
            rh_pct=50.0,
        )
        for k in range(n + 1)
    ]


def make_trials(
    *,
    task_id: str = "go_nogo_2back",
    n_early: int = 12,
    n_late: int = 12,
    n_post45: int = 12,
    early_rt_s: float = 0.450,
    late_rt_s: float = 0.458,
    post45_rt_s: float = 0.454,
    late_omissions: int = 0,
    late_errors: int = 0,
) -> list[cpe45.Trial]:
    trials: list[cpe45.Trial] = []
    for k in range(n_early):
        trials.append(cpe45.Trial(20.0 + 30.0 * k, task_id, early_rt_s, True, False))
    for k in range(n_late):
        if k < late_omissions:
            trials.append(cpe45.Trial(2180.0 + 30.0 * k, task_id, None, False, True))
        elif k < late_omissions + late_errors:
            trials.append(cpe45.Trial(2180.0 + 30.0 * k, task_id, late_rt_s, False, False))
        else:
            trials.append(cpe45.Trial(2180.0 + 30.0 * k, task_id, late_rt_s, True, False))
    for k in range(n_post45):
        trials.append(cpe45.Trial(5300.0 + 15.0 * k, task_id, post45_rt_s, True, False))
    return trials


def make_recovery(
    *,
    task_id: str = "knee_extensor_mvc",
    acute_mvc: float = 225.0,
    p45_mvc: float = 238.0,
    p24_mvc: float = 244.0,
    p24_cmj: float = 39.2,
    p24_pain: float = 0.5,
) -> tuple[cpe45.BaselineRecovery, list[cpe45.RecoveryProbe]]:
    base = cpe45.BaselineRecovery(task_id=task_id, mvc_value=250.0, cmj_cm=40.0, va_pct=94.0, pain_nrs=0.0)
    probes = [
        cpe45.RecoveryProbe(2790.0, "post_acute", task_id, mvc_value=acute_mvc, cmj_cm=37.0, va_pct=90.0, pain_nrs=1.0),
        cpe45.RecoveryProbe(5400.0, "post_45min", task_id, mvc_value=p45_mvc, cmj_cm=38.8, va_pct=92.5, pain_nrs=0.5),
        cpe45.RecoveryProbe(89100.0, "post_24h", task_id, mvc_value=p24_mvc, cmj_cm=p24_cmj, va_pct=93.5, pain_nrs=p24_pain),
    ]
    return base, probes


# Reuse a baseline 100 Hz sample array across fast unit tests to keep pytest quick
BASE_SAMPLES_100HZ = make_fast_samples(effort_hz=100.0, recovery_hz=1.0)


def run_full_analysis(**overrides) -> dict:
    base_rec, probes = make_recovery()
    kwargs = dict(
        samples=BASE_SAMPLES_100HZ,
        episodes=EPISODES,
        trials=make_trials(),
        early_end_s=WIN["early_end_s"],
        late_start_s=WIN["late_start_s"],
        max_gap_s=REQ["max_gap_s"],
        thermal_samples=make_thermal(),
        max_thermal_gap_s=REQ["max_thermal_gap_s"],
        recovery_probes=probes,
        baseline_recovery=base_rec,
        post45_window_bounds_s=PBOUNDS,
        min_effort_hz=REQ["min_effort_hz"],
        min_overall_hz=REQ["min_overall_hz"],
        min_thermal_hz=REQ["min_thermal_hz"],
        stream_clock_offsets_s={"ergometer": 0.0, "imu": 0.01, "cog": -0.015, "thermal": 0.02},
        max_sync_offset_s=REQ["max_sync_offset_s"],
        body_mass_kg=75.0,
        critical_power_W=275.0,
        medical_abort_core_temp_C=39.5,
    )
    kwargs.update(overrides)
    samples = kwargs.pop("samples")
    episodes = kwargs.pop("episodes")
    trials = kwargs.pop("trials")
    return cpe45.analyze(samples, episodes, trials, **kwargs)


class TestCPE45MultichannelContract(unittest.TestCase):
    def test_1_happy_path_software_contract_never_claims_empirical_validation(self):
        an = run_full_analysis()
        self.assertEqual(an["target_achievement"], "not_assessed")
        self.assertIs(an["physiological_validation"], False)
        ev = cpe45.evaluate_session(an, SPEC, arm="temperate_20C")
        self.assertEqual(ev["overall_status"], "CANDIDATE_SOFTWARE_PASS")
        self.assertIs(ev["empirical_validation"], False)
        self.assertIs(ev["medical_abort_triggered"], False)
        self.assertEqual(ev["n_fail"], 0)
        self.assertEqual(ev["n_not_assessed"], 0)

    def test_2_missing_channels_yield_not_assessed_never_pass(self):
        # Missing thermal, post45 recovery, post45 cognitive, body_mass_kg, critical_power_W, sync offsets
        an = run_full_analysis(
            trials=make_trials(n_post45=0),
            thermal_samples=None,
            min_thermal_hz=None,
            recovery_probes=None,
            baseline_recovery=None,
            stream_clock_offsets_s=None,
            max_sync_offset_s=None,
            body_mass_kg=None,
            critical_power_W=None,
        )
        ev = cpe45.evaluate_session(an, SPEC, arm="temperate_20C")
        self.assertEqual(ev["overall_status"], "NOT_ASSESSED")
        for key in (
            "sampling_thermal_min_hz",
            "sync_max_abs_offset_s",
            "work_positive_kJ_per_kg",
            "submax_prescription_pct_cp",
            "thermal_research_ceiling_C",
            "post45_acute_mvc_retention_pct",
            "post45_45min_mvc_retention_pct",
            "post45_24h_mvc_retention_pct",
            "post45_24h_cmj_retention_pct",
            "post45_24h_tendon_pain_nrs",
            "post45_45min_cog_accuracy_drop_pp",
            "post45_45min_cog_rt_increase_ms",
        ):
            self.assertEqual(ev["channels"][key]["status"], "NOT_ASSESSED", f"{key} should be NOT_ASSESSED")

    def test_3_clock_sync_offset_violation_rejected_and_caught(self):
        # Hard rejection in analyze() when max_sync_offset_s enforced
        with self.assertRaisesRegex(ValueError, "синхронизации"):
            run_full_analysis(
                stream_clock_offsets_s={"ergometer": 0.0, "imu": 0.085},
                max_sync_offset_s=0.05,
            )
        # Caught as FAIL in evaluate_session() if analyze() ran without max_sync_offset_s
        an = run_full_analysis(
            stream_clock_offsets_s={"ergometer": 0.0, "imu": 0.085},
            max_sync_offset_s=None,
        )
        ev = cpe45.evaluate_session(an, SPEC)
        self.assertEqual(ev["channels"]["sync_max_abs_offset_s"]["status"], "FAIL")
        self.assertEqual(ev["overall_status"], "FAIL")

    def test_4_sampling_rate_hz_violation_rejected_even_when_max_gap_passes(self):
        # 10 Hz during effort passes max_gap_s=1.0 but violates min_effort_hz=100.0
        low_hz_samples = make_fast_samples(effort_hz=10.0, recovery_hz=1.0)
        with self.assertRaisesRegex(ValueError, "effort-эпизодах"):
            run_full_analysis(samples=low_hz_samples, min_effort_hz=100.0)
        # Even if analyze() omits min_effort_hz, evaluate_session() catches it as FAIL
        an = run_full_analysis(samples=low_hz_samples, min_effort_hz=None)
        ev = cpe45.evaluate_session(an, SPEC)
        self.assertEqual(ev["channels"]["sampling_effort_min_hz"]["status"], "FAIL")
        self.assertEqual(ev["overall_status"], "FAIL")

        # Insufficient thermal sampling rate (dt=30 s -> 0.033 Hz < 0.05 Hz, even though <= max_thermal_gap_s=60 s)
        with self.assertRaisesRegex(ValueError, "теплового ряда"):
            run_full_analysis(thermal_samples=make_thermal(dt_s=30.0), min_thermal_hz=0.05)

    def test_5_cognitive_task_id_binding_bug_regression_and_min_trials(self):
        # Cognitive task_id ('go_nogo_2back') is completely distinct from effort task_ids!
        an = run_full_analysis(trials=make_trials(task_id="go_nogo_2back", early_rt_s=0.400, late_rt_s=0.440))
        self.assertIn("go_nogo_2back", an["cognitive_early_late"])
        self.assertAlmostEqual(an["cognitive_early_late"]["go_nogo_2back"]["delta_correct_latency_ms"], 40.0, places=4)
        self.assertAlmostEqual(an["cognitive_early_late"]["go_nogo_2back"]["delta_correct_latency_pct"], 10.0, places=4)
        ev = cpe45.evaluate_session(an, SPEC)
        self.assertEqual(ev["channels"]["cognitive_rt_increase_ms"]["status"], "FAIL")
        self.assertEqual(ev["channels"]["cognitive_rt_increase_pct"]["status"], "FAIL")
        self.assertEqual(ev["overall_status"], "FAIL")

        # Too few trials (<10) in early/late or post_45min -> NOT_ASSESSED
        an_few = run_full_analysis(trials=make_trials(n_early=5, n_late=12, n_post45=4))
        ev_few = cpe45.evaluate_session(an_few, SPEC)
        self.assertEqual(ev_few["channels"]["cognitive_rt_increase_ms"]["status"], "NOT_ASSESSED")
        self.assertEqual(ev_few["channels"]["post45_45min_cog_rt_increase_ms"]["status"], "NOT_ASSESSED")

        # High omissions (>5%) and accuracy drop (>3 pp) -> FAIL
        an_omit = run_full_analysis(trials=make_trials(n_late=12, late_omissions=2))
        ev_omit = cpe45.evaluate_session(an_omit, SPEC)
        self.assertEqual(ev_omit["channels"]["cognitive_omission_rate_pct"]["status"], "FAIL")
        self.assertEqual(ev_omit["channels"]["cognitive_accuracy_drop_pp"]["status"], "FAIL")
        self.assertEqual(ev_omit["channels"]["cognitive_accuracy_abs_pct"]["status"], "FAIL")

    def test_6_thermal_research_ceiling_strictly_separated_from_medical_abort(self):
        # 38.7 C: fails temperate_20C research ceiling (<38.5 C), PASSES warm_acclimatized_32C (<39.0 C), NO medical abort (<39.5 C)
        an_387 = run_full_analysis(thermal_samples=make_thermal(peak_temp_C=38.7))
        ev_temp = cpe45.evaluate_session(an_387, SPEC, arm="temperate_20C")
        self.assertEqual(ev_temp["channels"]["thermal_research_ceiling_C"]["status"], "FAIL")
        self.assertIs(ev_temp["medical_abort_triggered"], False)
        self.assertEqual(ev_temp["overall_status"], "FAIL")

        ev_warm = cpe45.evaluate_session(an_387, SPEC, arm="warm_acclimatized_32C")
        self.assertEqual(ev_warm["channels"]["thermal_research_ceiling_C"]["status"], "PASS")
        self.assertIs(ev_warm["medical_abort_triggered"], False)
        self.assertEqual(ev_warm["overall_status"], "CANDIDATE_SOFTWARE_PASS")

        # 39.6 C: triggers medical abort AND fails research ceiling in BOTH arms
        an_396 = run_full_analysis(thermal_samples=make_thermal(peak_temp_C=39.6))
        for arm in ("temperate_20C", "warm_acclimatized_32C"):
            ev_ab = cpe45.evaluate_session(an_396, SPEC, arm=arm)
            self.assertIs(ev_ab["medical_abort_triggered"], True)
            self.assertEqual(ev_ab["channels"]["thermal_research_ceiling_C"]["status"], "FAIL")
            self.assertEqual(ev_ab["overall_status"], "FAIL")

        # Unknown arm raises ValueError
        with self.assertRaises(ValueError):
            cpe45.evaluate_session(an_387, SPEC, arm="invalid_arm")

    def test_7_threshold_violations_demand_mechanical_spatial_recovery(self):
        # Demand floor violation: low power_scale -> <5.0 kJ/kg and <80% CP
        low_demand = make_fast_samples(effort_hz=100.0, power_scale=0.65)
        ev_dem = cpe45.evaluate_session(run_full_analysis(samples=low_demand), SPEC)
        self.assertEqual(ev_dem["channels"]["work_positive_kJ_per_kg"]["status"], "FAIL")
        self.assertEqual(ev_dem["channels"]["submax_prescription_pct_cp"]["status"], "FAIL")

        # Mechanical + spatial drop violations
        fatigued = make_fast_samples(
            effort_hz=100.0,
            late_exp_power_mult=0.75,  # 25% drop > 15%
            late_sub_power_mult=0.82,  # 18% drop > 10%
            late_coord_mult=1.50,      # +50% (>20%) and +0.005 m (>0.003 m)
            late_man_mult=1.30,        # +30% (>15%)
        )
        ev_fat = cpe45.evaluate_session(run_full_analysis(samples=fatigued), SPEC)
        self.assertEqual(ev_fat["channels"]["explosive_peak_power_drop_pct"]["status"], "FAIL")
        self.assertEqual(ev_fat["channels"]["submax_mean_power_drop_pct"]["status"], "FAIL")
        self.assertEqual(ev_fat["channels"]["coordination_error_rel_increase_pct"]["status"], "FAIL")
        self.assertEqual(ev_fat["channels"]["coordination_error_abs_increase_m"]["status"], "FAIL")
        self.assertEqual(ev_fat["channels"]["maneuver_error_rel_increase_pct"]["status"], "FAIL")

        # post45 recovery failure (post_24h MVC <95%, pain >2.0)
        base_rec, bad_probes = make_recovery(p24_mvc=220.0, p24_pain=4.0)
        ev_rec = cpe45.evaluate_session(run_full_analysis(baseline_recovery=base_rec, recovery_probes=bad_probes), SPEC)
        self.assertEqual(ev_rec["channels"]["post45_24h_mvc_retention_pct"]["status"], "FAIL")
        self.assertEqual(ev_rec["channels"]["post45_24h_tendon_pain_nrs"]["status"], "FAIL")

    def test_8_post45_window_timestamp_baseline_and_task_id_integrity(self):
        base_rec, probes = make_recovery()

        # time_s <= 2700 rejected
        bad_t = copy.deepcopy(probes)
        bad_t[0] = cpe45.RecoveryProbe(2700.0, "post_acute", "knee_extensor_mvc", mvc_value=230.0)
        with self.assertRaisesRegex(ValueError, "строго > 2700"):
            run_full_analysis(baseline_recovery=base_rec, recovery_probes=bad_t)

        # Out-of-window timestamp rejected (post_45min window is [5280, 5580])
        bad_win = copy.deepcopy(probes)
        bad_win[1] = cpe45.RecoveryProbe(4000.0, "post_45min", "knee_extensor_mvc", mvc_value=238.0)
        with self.assertRaisesRegex(ValueError, "вне допустимого окна"):
            run_full_analysis(baseline_recovery=base_rec, recovery_probes=bad_win)

        # Duplicate post45 window rejected
        dup = [probes[0], cpe45.RecoveryProbe(2800.0, "post_acute", "knee_extensor_mvc", mvc_value=230.0)]
        with self.assertRaisesRegex(ValueError, "дублирующееся окно"):
            run_full_analysis(baseline_recovery=base_rec, recovery_probes=dup)

        # Missing baseline_recovery rejected
        with self.assertRaisesRegex(ValueError, "требуется baseline_recovery"):
            run_full_analysis(baseline_recovery=None, recovery_probes=probes)

        # task_id mismatch between probe and baseline_recovery rejected
        bad_tid = copy.deepcopy(probes)
        bad_tid[2] = cpe45.RecoveryProbe(89100.0, "post_24h", "plantarflexor_mvc", mvc_value=244.0)
        with self.assertRaisesRegex(ValueError, "несовпадение task_id"):
            run_full_analysis(baseline_recovery=base_rec, recovery_probes=bad_tid)

        # Pain NRS > 10 rejected
        bad_pain = copy.deepcopy(probes)
        bad_pain[2] = cpe45.RecoveryProbe(89100.0, "post_24h", "knee_extensor_mvc", mvc_value=244.0, pain_nrs=11.0)
        with self.assertRaisesRegex(ValueError, "pain_nrs"):
            run_full_analysis(baseline_recovery=base_rec, recovery_probes=bad_pain)

        # Out-of-window post45 cognitive trial (t=12000 s not in any post45 window) rejected
        bad_trials = make_trials() + [cpe45.Trial(12000.0, "go_nogo_2back", 0.45, True, False)]
        with self.assertRaisesRegex(ValueError, "вне основных/post"):
            run_full_analysis(trials=bad_trials)

    def test_9_cohort_iut_bootstrap_ci_rejects_borderline_mean_and_missing_data(self):
        # 10 synthetic participants with mean peak T_core = 38.42 C (<38.5 C)
        # BUT wide variance so upper 95% bootstrap CI crosses 38.5 C -> MUST FAIL IUT!
        temps = [38.10, 38.15, 38.25, 38.30, 38.40, 38.45, 38.55, 38.60, 38.65, 38.75]
        sessions = [run_full_analysis(thermal_samples=make_thermal(peak_temp_C=tc)) for tc in temps]
        coh = cpe45.evaluate_cohort(sessions, SPEC, arm="temperate_20C", n_boot=1000, seed=20260420)
        self.assertIs(coh["empirical_validation"], False)
        self.assertLess(coh["channels"]["thermal_research_ceiling_C"]["mean"], 38.5)
        self.assertGreaterEqual(coh["channels"]["thermal_research_ceiling_C"]["ci95_two_sided"][1], 38.5)
        self.assertEqual(coh["channels"]["thermal_research_ceiling_C"]["status"], "FAIL")
        self.assertEqual(coh["overall_cohort_status"], "FAIL")

        # Clean cohort well inside bounds -> CANDIDATE_COHORT_SOFTWARE_PASS (still empirical_validation=False)
        clean_sessions = [run_full_analysis(thermal_samples=make_thermal(peak_temp_C=38.0 + 0.02 * i)) for i in range(6)]
        coh_ok = cpe45.evaluate_cohort(clean_sessions, SPEC, arm="temperate_20C", n_boot=500, seed=20260420)
        self.assertEqual(coh_ok["overall_cohort_status"], "CANDIDATE_COHORT_SOFTWARE_PASS")
        self.assertIs(coh_ok["empirical_validation"], False)

        # Missing channel in just ONE participant -> NOT_ASSESSED (no imputation!)
        clean_sessions_missing = list(clean_sessions)
        clean_sessions_missing[-1] = run_full_analysis(body_mass_kg=None)
        coh_na = cpe45.evaluate_cohort(clean_sessions_missing, SPEC, arm="temperate_20C", n_boot=500, seed=20260420)
        self.assertEqual(coh_na["channels"]["work_positive_kJ_per_kg"]["status"], "NOT_ASSESSED")
        self.assertEqual(coh_na["overall_cohort_status"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
