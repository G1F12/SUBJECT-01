"""Unit and regression test suite for EXP-0138
(Decisive Independent Out-of-Sample Evaluation of Terminal Torque and Dynamic Predictors).
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestIndependentTorqueTransfer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/INDEPENDENT_TORQUE_TRANSFER_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/INDEPENDENT_TORQUE_TRANSFER_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_independent_torque_transfer_test.py"

        if not cls.results_path.is_file():
            raise FileNotFoundError(f"Missing {cls.results_path}")
        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())

    def test_schema_and_provenance(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0138")
        self.assertIn("FND-0134", self.res["findings"])
        self.assertIn("NEG-0118", self.res["negative_results"])
        self.assertIn("DEC-0035", self.res["decisions"])
        self.assertEqual(self.res["provenance"]["krizaj_source"], "SRC-0112")
        self.assertEqual(self.res["provenance"]["evangelidis_source"], "SRC-0115")
        self.assertEqual(self.res["provenance"]["norbury_source"], "SRC-0111")

    def test_fixed_model_transfer_catastrophic_error(self):
        ft = self.res["krizaj_evaluation"]["fixed_model_transfer"]
        self.assertGreater(ft["fixed_tau_end_mae_Nm"], 45.0)
        self.assertGreater(ft["fixed_retention_mae_Nm"], 40.0)
        self.assertEqual(ft["transfer_status"], "CATASTROPHIC_ERROR_INCREASE")

    def test_krizaj_retrained_loso_utility_failure(self):
        ke = self.res["krizaj_evaluation"]
        maes = ke["retrained_loso_metrics"]
        comps = ke["comparisons"]

        # MeanRetention and PreAlone baselines
        self.assertAlmostEqual(maes["mean_retention_mae_Nm"], 10.48, places=1)
        self.assertAlmostEqual(maes["pre_alone_mae_Nm"], 9.63, places=1)
        self.assertAlmostEqual(maes["pre_plus_tau_end_mae_Nm"], 9.70, places=1)

        # DeltaMAE vs MeanRetention is < 1.0 and CI spans zero
        comp_ret = comps["tau_end_vs_mean_retention"]
        self.assertLess(comp_ret["dmae_Nm"], 1.0)
        self.assertLess(comp_ret["ci95_Nm"][0], 0.0)
        self.assertGreater(comp_ret["ci95_Nm"][1], 0.0)
        self.assertFalse(comp_ret["passes_utility_threshold"])

        # DeltaMAE vs PreAlone worsens error
        comp_pre = comps["tau_end_vs_pre_alone"]
        self.assertTrue(comp_pre["worsening"])
        self.assertLessEqual(comp_pre["dmae_Nm"], 0.0)

    def test_norbury_recovery_volume_worsens_prediction(self):
        ne = self.res["norbury_evaluation"]

        # 5-min
        n5 = ne["post_5m"]
        self.assertTrue(n5["worsening_vol4"])
        self.assertLess(n5["dmae_vol4_vs_pre_alone_N"], 0.0)
        self.assertAlmostEqual(n5["dmae_vol4_vs_pre_alone_N"], -7.25, places=1)

        # 45-min
        n45 = ne["post_45m"]
        self.assertTrue(n45["worsening_vol4"])
        self.assertLess(n45["dmae_vol4_vs_pre_alone_N"], 0.0)
        self.assertAlmostEqual(n45["dmae_vol4_vs_pre_alone_N"], -3.31, places=1)


if __name__ == "__main__":
    unittest.main()
