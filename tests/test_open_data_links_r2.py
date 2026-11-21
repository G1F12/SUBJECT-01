"""Unit and regression test suite for Milestone 2 / Requirement R2 (Open Data Link Verification).

Covers:
- Link 1 (EXP-0129, FND-0125, NEG-0109): Force -> Motion -> Tissue limits
- Link 2 (EXP-0130, FND-0126, NEG-0110): Work done -> Residual force -> Recovery
- Link 3 (EXP-0131, FND-0127, NEG-0111): ADAPT25, speed, motor control, CPE45
- Registry consistency and provenance gate invariants
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestOpenDataLinksR2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.link1_path = ROOT / "research/program_evidence_audit/LINK1_FORCE_TISSUE_RESULTS.json"
        cls.link2_path = ROOT / "research/program_evidence_audit/LINK2_WORK_RECOVERY_RESULTS.json"
        cls.link3_path = ROOT / "research/program_evidence_audit/LINK3_ADAPT25_CPE45_RESULTS.json"

        cls.link1 = json.loads(cls.link1_path.read_text(encoding="utf-8"))
        cls.link2 = json.loads(cls.link2_path.read_text(encoding="utf-8"))
        cls.link3 = json.loads(cls.link3_path.read_text(encoding="utf-8"))

        cls.experiments = {e["id"]: e for e in json.loads((ROOT / "registry/experiments.json").read_text(encoding="utf-8"))}
        cls.findings = {f["id"]: f for f in json.loads((ROOT / "registry/findings.json").read_text(encoding="utf-8"))}
        cls.negative = {n["id"]: n for n in json.loads((ROOT / "registry/negative_results.json").read_text(encoding="utf-8"))}

    # =========================================================================
    # LINK 1: Force -> Motion -> Tissue Limits (EXP-0129)
    # =========================================================================
    def test_link1_candidate_admission_and_zoger_blocked(self):
        audit = self.link1["admission_audit"]
        self.assertEqual(audit["verdict"], "EXTERNAL_OPEN_BILATERAL_ISOMETRIC_COHORTS_BLOCKED_REQUEST_ONLY")
        candidates = {c["cohort_id"]: c for c in audit["candidates"]}
        self.assertIn("Zoger_2025_IsoMed2000", candidates)
        zoger = candidates["Zoger_2025_IsoMed2000"]
        self.assertEqual(zoger["classification"], "REQUEST_ONLY_BLOCKED")
        self.assertFalse(zoger["open_data_available"])
        self.assertIn("upon reasonable request", zoger["data_availability_statement"].lower())

    def test_link1_santos_holdout_force_and_angle_sensitivity(self):
        w0 = self.link1["santos_w0_evaluation"]
        self.assertEqual(w0["n_participants"], 11)
        self.assertAlmostEqual(w0["observed_mean_N"], 2513.6, places=1)
        self.assertAlmostEqual(w0["observed_sd_N"], 577.7, places=1)

        metrics = w0["metrics"]
        self.assertAlmostEqual(metrics["corrected_model_110deg"]["bias_N"], 463.2, places=1)
        self.assertAlmostEqual(metrics["corrected_model_110deg"]["mae_N"], 613.6, places=1)
        self.assertAlmostEqual(metrics["fixed_const_2500N"]["mae_N"], 458.8, places=1)

        ang = w0["angular_sensitivity"]
        self.assertAlmostEqual(ang["mismatch_gradient_100_to_110_N_per_deg"], 40.98, places=1)
        self.assertAlmostEqual(ang["mismatch_gradient_110_to_140_N_per_deg"], 27.59, places=1)
        self.assertAlmostEqual(ang["artifact_magnitude_at_10deg_mismatch_N"], 409.8, places=1)

    def test_link1_anova_variance_separation(self):
        icc = self.link1["santos_longitudinal_variance_partitioning"]
        self.assertEqual(icc["n_subjects"], 10)
        self.assertEqual(icc["k_sessions"], 4)
        self.assertAlmostEqual(icc["within_subject_sd_naive_N"], 385.70, places=1)
        self.assertAlmostEqual(icc["within_subject_sd_detrended_N"], 309.08, places=1)
        anova = icc["anova_two_way_decomposition"]
        self.assertAlmostEqual(anova["ss_training_progression_sessions"], 1596999.4, places=0)
        self.assertAlmostEqual(anova["ss_residual_error"], 2865965.2, places=0)

    def test_link1_dpvalid_and_squat_transfer_boundaries(self):
        dp = self.link1["dpvalid_single_joint_benchmark"]
        self.assertEqual(dp["n_participants"], 20)
        self.assertEqual(dp["n_trials"], 125)
        self.assertAlmostEqual(dp["delta_r2_m2_pcsa_vs_baseline_f0"], 0.0735, places=3)
        self.assertIn("INCONCLUSIVE", dp["outcome"])

        sq = self.link1["scherpereel_squat_transfer"]
        self.assertEqual(sq["participants"], 12)
        self.assertIn("ISS-0028", sq["unit_ambiguity_blocker_ISS_0028"])

    def test_link1_tissue_safety_and_ballistic_hazard(self):
        tissue = self.link1["tissue_limits_and_enthesis_hazard"]
        qs = tissue["quasi_static_target_force_4800N"]
        self.assertEqual(qs["bilateral_footplate_force_N"], 4800.0)
        self.assertGreaterEqual(qs["safety_factor"], 1.50)
        self.assertTrue(qs["safety_gate_passed"])

        bal = tissue["ballistic_explosive_recruitment_hazard"]
        self.assertLess(bal["local_enthesis_effective_safety_factor"], 1.50)
        self.assertFalse(bal["safety_gate_passed"])
        self.assertEqual(bal["hazard_verdict"], "BALLISTIC_OVERLOAD_RISK_REQUIRING_RATE_LIMITER")

    # =========================================================================
    # LINK 2: Work Done -> Residual Force -> Recovery (EXP-0130)
    # =========================================================================
    def test_link2_norbury_loso_cv_and_paired_benchmark(self):
        nor = self.link2["norbury_summary"]
        self.assertEqual(nor["n_subjects"], 12)
        self.assertEqual(nor["n_observations"], 24)
        self.assertAlmostEqual(nor["volume_difference_percent"], 22.5, places=1)
        self.assertAlmostEqual(nor["retention_5m_paired_difference_pp"], 0.04, places=1)

        comp = self.link2["norbury_paired_comparisons_vs_retention_baseline"]["mean_retention_minus_volume_linear_model"]
        diff = comp["paired_mae_difference_N"]
        ci95 = comp["ci95_N"]
        self.assertAlmostEqual(diff, -4.0766, places=2)
        self.assertAlmostEqual(ci95[0], -8.4905, places=2)
        self.assertAlmostEqual(ci95[1], -0.2910, places=2)
        self.assertEqual(comp["favors"], "baseline")

    def test_link2_de_poli_directional_refutation(self):
        dp = self.link2["de_poli_directional_audit"]
        sit = dp["SIT_group"]
        self.assertEqual(sit["n_participants"], 11)
        self.assertAlmostEqual(sit["force_retention_shift_pp"], +3.72, places=2)
        self.assertTrue(sit["directional_refutation_of_scalar_work_depletion"])

    def test_link2_mclaughlin_work_bounds(self):
        mcl = self.link2["mclaughlin_work_audit"]
        self.assertIn(mcl["n_participants"], [23, 24])
        self.assertGreater(mcl["mean_work_kJ_2700s"], 400.0)
        self.assertIn("non-comparable across intensity domains", mcl["association_bounds"]["physiological_conclusion"].lower())

    def test_link2_four_component_candidate_framing(self):
        contrast = self.link2["multi_model_contrast"]
        four_comp = contrast["model_4_four_component_transition_model"]
        self.assertIn("UNVALIDATED_CANDIDATE_ARCHITECTURE", four_comp["status"])
        self.assertEqual(len(four_comp["components"]), 4)

    # =========================================================================
    # LINK 3: ADAPT25, Speed, Motor Control, CPE45 (EXP-0131)
    # =========================================================================
    def test_link3_pennes_thermal_validation_on_mclaughlin(self):
        therm = self.link3["thermal_validation_mclaughlin"]
        self.assertEqual(therm["n_participants"], 23)
        metrics = therm["metrics"]
        self.assertAlmostEqual(metrics["four_layer_pennes"]["mae_C"], 0.586, places=2)
        self.assertAlmostEqual(metrics["persistence"]["mae_C"], 1.275, places=2)

        comps = therm["paired_comparisons_vs_pennes"]
        self.assertAlmostEqual(comps["persistence_minus_pennes"]["mae_difference_C"], 0.689, places=2)
        self.assertGreater(comps["persistence_minus_pennes"]["ci95_C"][0], 0.40)
        self.assertEqual(comps["persistence_minus_pennes"]["favors"], "pennes")

    def test_link3_cpe45_continuous_breach_vs_intermittent_duty_cycles(self):
        env = self.link3["cpe45_2700s_thermal_envelope"]
        self.assertEqual(env["duration_s"], 2700)
        self.assertEqual(env["target_power_W"], 360.0)
        self.assertIn("BREACHES_SAFETY_LIMIT", env["verdict_continuous_360W"])
        self.assertIn("FEASIBLE_UNDER_DUTY_CYCLE", env["verdict_intermittent_pacing"])

        climates = {c["name"]: c for c in env["climates"]}
        self.assertLessEqual(climates["Temperate"]["continuous_breach_s"], 2700)
        self.assertLessEqual(climates["Warm"]["continuous_breach_s"], 2700)
        self.assertLessEqual(climates["Hot-Dry"]["continuous_breach_s"], 2700)
        self.assertLessEqual(climates["Hot-Humid"]["continuous_breach_s"], 2700)

        self.assertAlmostEqual(climates["Temperate"]["d_max_safe"], 0.92, places=2)
        self.assertAlmostEqual(climates["Warm"]["d_max_safe"], 0.74, places=2)
        self.assertAlmostEqual(climates["Hot-Dry"]["d_max_safe"], 0.59, places=2)
        self.assertAlmostEqual(climates["Hot-Humid"]["d_max_safe"], 0.65, places=2)

    def test_link3_santos_longitudinal_trajectory_and_tissue_sweep(self):
        adapt = self.link3["tissue_adaptation_longitudinal_audit"]
        self.assertEqual(adapt["complete_participants_n"], 10)
        self.assertAlmostEqual(adapt["growth_at_day_14_percent"], 18.35, places=1)
        self.assertAlmostEqual(adapt["growth_at_day_42_percent"], 20.01, places=1)

        sweep = {e["trajectory_label"]: e for e in adapt["sf0_sensitivity_sweep"]}
        self.assertFalse(sweep["SF0_1.500"]["tissue_gate_pass"])
        self.assertAlmostEqual(sweep["SF0_1.500"]["min_safety_factor"], 1.267, places=2)

        # Critical threshold SF0 >= 1.776 eliminates deficit completely
        self.assertTrue(sweep["SF0_1.776"]["tissue_gate_pass"])
        self.assertGreaterEqual(sweep["SF0_1.776"]["min_safety_factor"], 1.50)
        self.assertEqual(sweep["SF0_1.776"]["days_below_threshold_1_50"], 0)

    def test_link3_speed_and_motor_control_invariants(self):
        speed = self.link3["contractile_speed_and_motor_control"]
        self.assertAlmostEqual(speed["v_max_decrement_percent"], -1.7, places=1)
        self.assertAlmostEqual(speed["peak_power_amplification_percent"], 19.8, places=1)
        self.assertAlmostEqual(speed["torque_amplification_strategy_2_percent"], 21.93, places=1)

    # =========================================================================
    # REGISTRY INTEGRITY & CONSISTENCY FOR MILESTONE 2
    # =========================================================================
    def test_registry_consistency_for_m2(self):
        for exp_id in ["EXP-0129", "EXP-0130", "EXP-0131"]:
            self.assertIn(exp_id, self.experiments)
            exp = self.experiments[exp_id]
            self.assertEqual(exp["status"], "completed")
            self.assertTrue((ROOT / exp["model"]).is_file())
            self.assertTrue((ROOT / exp["inputs"]).is_file())
            self.assertTrue((ROOT / exp["report"]).is_file())
            for out in exp["outputs"]:
                self.assertTrue((ROOT / out).is_file())

        for fnd_id in ["FND-0125", "FND-0126", "FND-0127"]:
            self.assertIn(fnd_id, self.findings)
            self.assertEqual(self.findings[fnd_id]["confidence"], "arithmetic_reproduced")

        for neg_id in ["NEG-0109", "NEG-0110", "NEG-0111"]:
            self.assertIn(neg_id, self.negative)


if __name__ == "__main__":
    unittest.main()
