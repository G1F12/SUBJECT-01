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
        self.assertEqual(self.res["provenance"]["norbury_doi"], "10.1113/EP091705")

    def test_fixed_model_transfer_catastrophic_error(self):
        dt = self.res["direct_transfer_evaluation"]
        tau_m = dt["fixed_source_tau_end_model"]
        ret_m = dt["fixed_source_retention_baseline"]

        # Fixed model exhibits catastrophic error on Križaj
        self.assertGreater(tau_m["mae_Nm"], 70.0)
        self.assertGreater(ret_m["mae_Nm"], 40.0)
        self.assertEqual(tau_m["status"], "CATASTROPHIC_OVERESTIMATION")
        # Fixed tau_end model is substantially worse than fixed retention baseline
        self.assertGreater(tau_m["mae_Nm"], ret_m["mae_Nm"])

    def test_krizaj_same_leg_pre_alone_invariant_and_tau_end_failure(self):
        ke = self.res["krizaj_evaluation"]
        maes = ke["primary_metrics"]
        comps = ke["primary_comparisons"]
        sens = ke["sensitivity_across_rules"]

        # Baseline PreAlone is identically 10.60 Nm across all bipartite matching rules
        self.assertAlmostEqual(maes["pre_alone_mae_Nm"], 10.60, places=1)
        for rule_name, rule_res in sens.items():
            self.assertAlmostEqual(
                rule_res["pre_alone_mae_Nm"],
                10.60,
                places=1,
                msg=f"PreAlone failed 10.60 Nm invariance under {rule_name}",
            )

        # Pre + tau_end spans 10.59 to 11.03 Nm across rules
        for rule_name, rule_res in sens.items():
            self.assertGreaterEqual(rule_res["pre_plus_tau_end_mae_Nm"], 10.59)
            self.assertLessEqual(rule_res["pre_plus_tau_end_mae_Nm"], 11.10)
            # In each rule, 95% CI vs PreAlone spans zero or shows worsening
            ci = rule_res["ci95_vs_pre_alone_Nm"]
            self.assertLessEqual(ci[0], 0.0)

        # Primary rule (Rule 2): adding tau_end worsens error from 10.60 to 10.71 Nm
        self.assertAlmostEqual(maes["pre_plus_tau_end_mae_Nm"], 10.71, places=1)
        comp_pre = comps["tau_end_vs_pre_alone"]
        self.assertTrue(comp_pre["worsening"])
        self.assertFalse(comp_pre["passes_utility_threshold"])

    def test_norbury_recovery_volume_aligned_recalculation(self):
        ne = self.res["norbury_evaluation"]

        # 5-min post-exercise
        n5 = ne["post_5m"]
        self.assertAlmostEqual(n5["pre_alone_mae_N"], 49.50, places=1)
        self.assertAlmostEqual(n5["pre_plus_vol4_mae_N"], 47.58, places=1)
        self.assertAlmostEqual(n5["dmae_vol4_vs_pre_alone_N"], 1.93, places=1)
        # CI spans zero (e.g. [-6.13, 10.31])
        self.assertLess(n5["ci95_vol4_N"][0], 0.0)
        self.assertGreater(n5["ci95_vol4_N"][1], 0.0)
        self.assertFalse(n5["passes_utility_vol4"])

        # 45-min post-exercise
        n45 = ne["post_45m"]
        self.assertAlmostEqual(n45["pre_alone_mae_N"], 34.38, places=1)
        self.assertAlmostEqual(n45["pre_plus_vol4_mae_N"], 32.94, places=1)
        self.assertAlmostEqual(n45["dmae_vol4_vs_pre_alone_N"], 1.44, places=1)
        # CI spans zero (e.g. [-4.22, 6.87])
        self.assertLess(n45["ci95_vol4_N"][0], 0.0)
        self.assertGreater(n45["ci95_vol4_N"][1], 0.0)
        self.assertFalse(n45["passes_utility_vol4"])


if __name__ == "__main__":
    unittest.main()
