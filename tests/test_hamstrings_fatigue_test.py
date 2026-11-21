"""
Unit test suite for EXP-0136 (Hamstrings Knee Flexion Fatigue Test on Evangelidis et al. 2023 / SRC-0115).

Verifies:
- Direct test execution and artifact presence
- Sample composition audit (9 participants, 3 within-subject conditions: ISO, CON, ECC)
- Pronounced fatigue verification (force depression 18% to 34%)
- Measured mechanical work in Joules and torque-time impulse
- LOSO cross-validation with participant-clustered bootstrap (95% CI spans zero)
- Simpler non-work retention baseline outperforming work models
- Epistemic conclusions regarding measured work vs post-exercise MVT prediction
"""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestHamstringsFatigueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/HAMSTRINGS_FATIGUE_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/HAMSTRINGS_FATIGUE_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_hamstrings_fatigue_test.py"
        cls.excel_path = ROOT / "data/fatigue_hamstrings/421_2022_5104_MOESM2_ESM.xlsx"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())
        self.assertTrue(self.excel_path.is_file())

    def test_experiment_metadata(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0136")
        self.assertIn("FND-0132", self.res["findings"])
        self.assertIn("NEG-0116", self.res["negative_results"])
        self.assertIn("DEC-0033", self.res["decisions"])
        self.assertEqual(self.res["dataset_source"], "SRC-0115")
        self.assertTrue(self.res["scientific_conclusion"]["direct_test_passed"])
        self.assertTrue(self.res["scientific_conclusion"]["pronounced_fatigue_verified"])
        self.assertFalse(self.res["scientific_conclusion"]["work_improves_prediction_on_held_out"])

    def test_sample_provenance_and_fatigue_kinetics(self):
        kinetics = self.res["condition_fatigue_kinetics"]
        self.assertEqual(set(kinetics.keys()), {"ISO", "CON", "ECC"})

        # Pronounced fatigue verified in all conditions
        self.assertLess(kinetics["CON"]["drop_pct_mean"], -25.0)
        self.assertLess(kinetics["ECC"]["drop_pct_mean"], -25.0)
        self.assertLess(kinetics["ISO"]["drop_pct_mean"], -15.0)

        # Work in Joules
        self.assertGreater(kinetics["CON"]["work_j_mean"], 3000.0)
        self.assertGreater(kinetics["ECC"]["work_j_mean"], 3000.0)
        self.assertEqual(kinetics["ISO"]["work_j_mean"], 0.0)

    def test_loso_cross_validation_dynamic(self):
        dyn = self.res["loso_evaluations"]["dynamic_conditions_con_ecc"]
        self.assertEqual(dyn["n_participants"], 9)
        self.assertEqual(dyn["n_observations"], 18)

        # MAE values
        maes = dyn["maes"]
        self.assertAlmostEqual(maes["mean_retention"], 11.25, places=1)
        self.assertAlmostEqual(maes["cond_retention"], 11.59, places=1)
        self.assertAlmostEqual(maes["pre_plus_cond"], 14.27, places=1)
        self.assertAlmostEqual(maes["pre_plus_cond_plus_work"], 13.72, places=1)

        # Simple retention beats model with work
        self.assertLess(maes["mean_retention"], maes["pre_plus_cond_plus_work"])

        # Bootstrap 95% CI strictly spans zero
        ci95 = dyn["dmae_95ci"]
        self.assertLess(ci95[0], 0.0)
        self.assertGreater(ci95[1], 0.0)
        self.assertEqual(dyn["verdict"], "INCONCLUSIVE_SPANS_ZERO")

    def test_loso_cross_validation_all_conditions(self):
        all_cond = self.res["loso_evaluations"]["all_conditions_iso_con_ecc"]
        self.assertEqual(all_cond["n_participants"], 9)
        self.assertEqual(all_cond["n_observations"], 27)

        # Adding work to Pre+Cond increases MAE (worsens prediction)
        maes = all_cond["maes"]
        self.assertGreater(maes["pre_plus_cond_plus_work"], maes["pre_plus_cond"])
        self.assertLess(all_cond["dmae_base_minus_work"], 0.0)

    def test_collinearity_and_depletion_formulation(self):
        regr = self.res["regression_and_collinearity"]
        self.assertGreater(regr["pre_work_correlation"], 0.8)
        self.assertGreater(regr["work_coef"], 0.0)  # Positive, not negative depletion!

        depletion = self.res["depletion_formulation_audit"]
        self.assertEqual(depletion["verdict"], "DEPLETION_MODEL_INFERIOR_TO_CONSTANT_RETENTION")
        self.assertLess(depletion["mae_constant_retention"], depletion["mae_physical_depletion"])


if __name__ == "__main__":
    unittest.main()
