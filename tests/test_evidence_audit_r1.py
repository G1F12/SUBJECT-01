"""Unit and regression tests for Milestone 1 / R1 evidence base corrections.

Covers EXP-0126, EXP-0127, EXP-0128, and DEC-0032 invariants.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestEvidenceAuditR1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp126_path = ROOT / "research/program_evidence_audit/FORCE_TRANSFER_RELIABILITY_RESULTS.json"
        cls.exp127_path = ROOT / "research/program_evidence_audit/WORK_FORCE_TRANSITION_RESULTS.json"
        cls.exp128_path = ROOT / "research/program_evidence_audit/ADAPT25_TISSUE_TRAJECTORY_RESULTS.json"

        cls.exp126 = json.loads(cls.exp126_path.read_text(encoding="utf-8"))
        cls.exp127 = json.loads(cls.exp127_path.read_text(encoding="utf-8"))
        cls.exp128 = json.loads(cls.exp128_path.read_text(encoding="utf-8"))

        cls.decisions = {d["id"]: d for d in json.loads((ROOT / "registry/decisions.json").read_text(encoding="utf-8"))}
        cls.findings = {f["id"]: f for f in json.loads((ROOT / "registry/findings.json").read_text(encoding="utf-8"))}
        cls.negative = {n["id"]: n for n in json.loads((ROOT / "registry/negative_results.json").read_text(encoding="utf-8"))}

    def test_exp0126_angle_mismatch_and_anova_separation(self):
        angle_eval = self.exp126["angle_transfer_evaluation"]
        gradients = angle_eval["mismatch_gradient_N_per_deg"]
        self.assertAlmostEqual(gradients["100deg_to_110deg"], 40.98, places=1)
        self.assertAlmostEqual(gradients["110deg_to_140deg"], 27.59, places=1)
        self.assertAlmostEqual(angle_eval["artifact_magnitude_at_10deg_mismatch_N"], 409.8, places=1)

        rep = self.exp126["longitudinal_repeatability"]["four_sessions_10_subjects"]
        self.assertAlmostEqual(rep["within_subject_sd_naive_N"], 385.70, places=1)
        self.assertAlmostEqual(rep["within_subject_sd_detrended_N"], 309.08, places=1)

        anova = rep["anova_two_way_decomposition"]
        self.assertAlmostEqual(anova["ss_training_progression_sessions"], 1596999.4, places=0)
        self.assertAlmostEqual(anova["ss_residual_error"], 2865965.2, places=0)
        self.assertAlmostEqual(anova["residual_error_sd_N"], 325.80, places=1)

    def test_exp0127_benchmark_bootstrap_and_candidate_framing(self):
        comp = self.exp127["norbury_paired_comparisons_vs_retention_baseline"]["mean_retention_minus_volume_linear_model"]
        diff = comp["paired_mae_difference_N"]
        ci95 = comp["ci95_N"]

        # Control benchmark: paired difference -4.08 N [-8.49, -0.29] N
        self.assertAlmostEqual(diff, -4.0766, places=2)
        self.assertAlmostEqual(ci95[0], -8.4905, places=2)
        self.assertAlmostEqual(ci95[1], -0.2910, places=2)
        self.assertEqual(comp["favors"], "baseline")

        # Candidate framing
        arch = self.exp127["structural_coupling_decision"]["proposed_reconstructed_transition_architecture"]
        self.assertIn("UNVALIDATED_CANDIDATE_ARCHITECTURE", arch["status"])

        # de Poli group data restriction
        de_poli = self.exp127["de_poli_group_audit"]
        self.assertIn("scope_limitation", de_poli)
        self.assertIn("group-level", de_poli["scope_limitation"].lower())

    def test_exp0128_santos_force_and_sensitivity_sweep(self):
        forces = self.exp128["cohort_mean_forces_N"]
        w0 = forces["W0_day0"]
        w2 = forces["W2_day14"]
        gain_pct = (w2 / w0 - 1.0) * 100.0

        # Santos day 14 force gain must be +18.35%
        self.assertAlmostEqual(gain_pct, 18.3536, places=2)
        self.assertAlmostEqual(w0, 2525.16, places=1)
        self.assertAlmostEqual(w2, 2988.62, places=1)

        # Sensitivity sweep checks
        sweep = self.exp128["parametric_sensitivity_analysis"]["standard_rate"]
        sf0_sweep = {entry["trajectory_label"]: entry for entry in sweep["sf0_sensitivity_standard_rate"]}

        # Critical threshold SF0 >= 1.776 eliminates deficit
        crit = sf0_sweep["SF0_1.776"]
        self.assertGreaterEqual(crit["min_safety_factor"], 1.50)
        self.assertEqual(crit["days_below_threshold_1_50"], 0)

        # Removed rate limit claim from JSON
        self.assertNotIn("HOLD_RATE_LIMITED_BY_COLLAGEN_SYNTHESIS confirmed on empirical human trajectories", json.dumps(self.exp128))

    def test_registry_consistency_for_r1(self):
        # DEC-0032
        dec32 = self.decisions["DEC-0032"]
        self.assertIn("candidate transition architecture", dec32["decision"])
        self.assertIn("-8.49, -0.29", dec32["rationale"])

        # FND-0123
        fnd123 = self.findings["FND-0123"]
        self.assertIn("-8.49, -0.29", fnd123["statement"])

        # FND-0124
        fnd124 = self.findings["FND-0124"]
        self.assertIn("+18.35%", fnd124["statement"])
        self.assertNotIn("confirming rate-limiting collagen heterochrony under native conditions", fnd124["statement"])

        # NEG-0107
        neg107 = self.negative["NEG-0107"]
        self.assertTrue("-8.49" in neg107["statement"] or "−8.49" in neg107["statement"])
        self.assertTrue("-0.29" in neg107["statement"] or "−0.29" in neg107["statement"])


if __name__ == "__main__":
    unittest.main()
