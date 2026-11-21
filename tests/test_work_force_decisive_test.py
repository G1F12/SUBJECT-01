"""
Unit test suite for EXP-0133 (Decisive Work-to-Force and Work-to-Power Test).

Verifies:
- Jutlah repeated sprint cycling evaluation (567 observations, 21 males, work in Joules)
- Norbury multi-timepoint leg press recovery evaluation (5 min, 45 min, 24 h)
- Clustered bootstrap confidence intervals for work model vs retention baseline
- Definitive negative conclusion regarding scalar work-to-force predictability
"""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestWorkForceDecisiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/WORK_FORCE_DECISIVE_TEST_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/WORK_FORCE_DECISIVE_TEST_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_work_force_decisive_test.py"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())

    def test_basic_schema(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0133")
        self.assertIn("FND-0129", self.res["findings"])
        self.assertIn("NEG-0113", self.res["negative_results"])
        self.assertIn("DEC-0033", self.res["decisions"])
        self.assertIn("NO", self.res["definitive_answer"])

    def test_jutlah_evaluation_metrics(self):
        j = self.res["jutlah_evaluation"]
        self.assertEqual(j["participants"], 21)
        self.assertEqual(j["observations"], 567)
        self.assertTrue(j["work_measured_in_joules"])
        self.assertIn("Strictly includes only sprints prior", j["work_accumulation_verified"])
        
        models = j["models_mae_W"]
        self.assertAlmostEqual(models["unperturbed_persistence"], 114.64, places=1)
        self.assertAlmostEqual(models["mean_retention_baseline"], 89.23, places=1)
        self.assertAlmostEqual(models["sprint_and_rest_baseline"], 89.83, places=1)
        self.assertAlmostEqual(models["cumulative_work_linear_model"], 88.70, places=1)
        self.assertAlmostEqual(models["work_plus_rest_duration_model"], 89.48, places=1)
        self.assertAlmostEqual(models["sprint_rest_and_work_model"], 91.98, places=1)
        self.assertAlmostEqual(models["proportional_d2_depletion_model"], 105.96, places=1)

        comp = j["paired_comparisons_vs_retention_baseline"]["cumulative_work_linear_model"]
        self.assertAlmostEqual(comp["dmae_W"], 0.53, places=1)
        # CI covers zero
        self.assertLess(comp["ci95_W"][0], 0.0)
        self.assertGreater(comp["ci95_W"][1], 0.0)
        self.assertEqual(comp["favors"], "uncertain_inconclusive")

    def test_norbury_multitimepoint_evaluation(self):
        n = self.res["norbury_evaluation"]
        self.assertEqual(n["participants"], 12)
        self.assertEqual(n["observations"], 24)

        # Empirical recovery kinetics checkpoint
        rec = n["overall_empirical_recovery_pct"]
        self.assertAlmostEqual(rec["5m"], 91.01, places=1)
        self.assertAlmostEqual(rec["45m"], 93.34, places=1)
        self.assertAlmostEqual(rec["24h"], 99.10, places=1)

        delays = n["delays_evaluated"]
        self.assertIn("5m", delays)
        self.assertIn("45m", delays)
        self.assertIn("24h", delays)

        # 5m: volume model loses to retention baseline
        m5 = delays["5m"]
        self.assertAlmostEqual(m5["models_mae_N"]["mean_retention_baseline"], 50.61, places=1)
        self.assertAlmostEqual(m5["models_mae_N"]["volume_linear_model"], 54.69, places=1)
        self.assertAlmostEqual(m5["volume_model_vs_retention_baseline"]["dmae_N"], -4.08, places=2)
        self.assertLess(m5["volume_model_vs_retention_baseline"]["ci95_N"][1], 0.0)
        self.assertEqual(m5["volume_model_vs_retention_baseline"]["favors"], "baseline")

        # 45m: volume model loses to retention baseline
        m45 = delays["45m"]
        self.assertAlmostEqual(m45["models_mae_N"]["mean_retention_baseline"], 46.49, places=1)
        self.assertAlmostEqual(m45["models_mae_N"]["volume_linear_model"], 50.86, places=1)
        self.assertAlmostEqual(m45["volume_model_vs_retention_baseline"]["dmae_N"], -4.38, places=2)
        self.assertLess(m45["volume_model_vs_retention_baseline"]["ci95_N"][1], 0.0)
        self.assertEqual(m45["volume_model_vs_retention_baseline"]["favors"], "baseline")


if __name__ == "__main__":
    unittest.main()
