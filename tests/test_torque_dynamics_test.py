"""
Unit test suite for EXP-0137 (Sequential Torque Fatigue Dynamics on Evangelidis et al. 2023 / SRC-0115).

Verifies:
- Direct test execution and artifact presence (JSON, MD)
- Extraction of pre-specified dynamic features (R_late, S_tau, tau_end)
- Pre-specified utility criterion check
- LOSO MAE values and comparisons against MeanRetention and BaseCond
- Clustered bootstrap confidence interval spanning zero (failing significance threshold)
- Destructive effect of adding mechanical work in Joules to tau_end
- Inter-subject heterogeneity and transfer boundary
"""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestTorqueDynamicsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/TORQUE_DYNAMICS_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/TORQUE_DYNAMICS_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_torque_dynamics_test.py"
        cls.excel_path = ROOT / "data/fatigue_hamstrings/421_2022_5104_MOESM2_ESM.xlsx"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())
        self.assertTrue(self.excel_path.is_file())

    def test_experiment_metadata(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0137")
        self.assertIn("FND-0133", self.res["findings"])
        self.assertIn("NEG-0117", self.res["negative_results"])
        self.assertIn("DEC-0034", self.res["decisions"])
        self.assertEqual(self.res["dataset_source"], "SRC-0115")

    def test_dynamic_feature_maes(self):
        maes = self.res["loso_maes"]
        self.assertAlmostEqual(maes["mean_retention"], 11.25, places=1)
        self.assertAlmostEqual(maes["cond_retention"], 11.59, places=1)
        self.assertAlmostEqual(maes["pre_plus_cond"], 14.27, places=1)
        self.assertAlmostEqual(maes["pre_plus_cond_plus_tau_end"], 10.22, places=1)
        self.assertAlmostEqual(maes["pre_plus_cond_plus_work_plus_tau_end"], 11.85, places=1)

        # R_late and S_tau fail to beat MeanRetention
        self.assertGreater(maes["pre_plus_cond_plus_r_late"], maes["mean_retention"])
        self.assertGreater(maes["pre_plus_cond_plus_s_tau"], maes["mean_retention"])

        # tau_end nominally beats MeanRetention by ~1.02 Nm
        tau_vs_mret = maes["mean_retention"] - maes["pre_plus_cond_plus_tau_end"]
        self.assertGreater(tau_vs_mret, 1.0)

        # Adding work to tau_end degrades MAE by >1.5 Nm
        work_degradation = maes["pre_plus_cond_plus_work_plus_tau_end"] - maes["pre_plus_cond_plus_tau_end"]
        self.assertGreater(work_degradation, 1.5)

    def test_utility_criterion_and_bootstrap_ci(self):
        tau_comp = self.res["comparisons"]["pre_plus_cond_plus_tau_end"]
        # Fails pre-specified utility criterion because CI spans zero
        self.assertFalse(tau_comp["passes_prespecified_criterion"])

        ci_mret = tau_comp["ci95_vs_mean_retention"]
        self.assertLess(ci_mret[0], 0.0)
        self.assertGreater(ci_mret[1], 0.0)

        ci_base = tau_comp["ci95_vs_base_cond"]
        self.assertLess(ci_base[0], 0.0)
        self.assertGreater(ci_base[1], 0.0)

    def test_inter_subject_heterogeneity(self):
        breakdown = self.res["participant_breakdown"]
        self.assertEqual(len(breakdown), 9)

        # Strong responders where tau_end helped (P3, P4, P5, P6)
        self.assertGreater(breakdown["3"]["dmae_improvement"], 15.0)
        self.assertGreater(breakdown["4"]["dmae_improvement"], 4.0)

        # Discrepant participants where tau_end increased error (P1, P2, P7)
        self.assertLess(breakdown["1"]["dmae_improvement"], -5.0)
        self.assertLess(breakdown["2"]["dmae_improvement"], -5.0)
        self.assertLess(breakdown["7"]["dmae_improvement"], -5.0)


if __name__ == "__main__":
    unittest.main()
