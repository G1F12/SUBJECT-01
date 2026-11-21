"""
Unit test suite for EXP-0135 (Plantarflexion Decisive Test on Zenodo 15679911 / SRC-0112).

Verifies:
- Direct test execution and artifact presence
- Sample composition audit (21 workbooks vs 20 published participants)
- Dynamometer spindle coordinate polarity resolution (3/6 sheets per book, physical discrepancy median 1.05 J)
- LOSO cross-validation with participant-clustered bootstrap (95% CI spans zero)
- Fatigue kinetics and work distribution overlap
- Epistemic conclusions regarding measured work vs post-exercise MVIC prediction
"""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestPlantarDecisiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_path = ROOT / "research/program_evidence_audit/PLANTAR_DECISIVE_TEST_RESULTS.json"
        cls.report_path = ROOT / "research/program_evidence_audit/PLANTAR_DECISIVE_TEST_REPORT.md"
        cls.script_path = ROOT / "research/program_evidence_audit/run_plantar_decisive_test.py"

        cls.res = json.loads(cls.results_path.read_text(encoding="utf-8"))

    def test_artifacts_exist(self):
        self.assertTrue(self.results_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertTrue(self.script_path.is_file())

    def test_experiment_metadata(self):
        self.assertEqual(self.res["experiment_id"], "EXP-0135")
        self.assertIn("FND-0131", self.res["findings"])
        self.assertIn("NEG-0115", self.res["negative_results"])
        self.assertIn("DEC-0033", self.res["decisions"])
        self.assertIn("SRC-0112", self.res["dataset_source"])
        self.assertTrue(self.res["scientific_conclusion"]["direct_test_passed"])
        self.assertFalse(self.res["scientific_conclusion"]["work_improves_prediction_on_held_out"])

    def test_sample_provenance_audit(self):
        prov = self.res["sample_provenance"]
        self.assertEqual(prov["total_workbooks_in_zip"], 21)
        self.assertEqual(prov["total_records_in_zip"], 126)
        self.assertEqual(prov["published_article_n"], 20)
        self.assertIn("Nivo2_1", prov["s021_notes"])

        # Men anthropometrics match Table 1 of Križaj et al. 2025
        men = prov["s001_s020_men_anthropometrics"]
        self.assertEqual(men["count"], 9)
        self.assertAlmostEqual(men["age_mean"], 25.1, places=1)
        self.assertAlmostEqual(men["age_sd"], 3.1, places=1)
        self.assertAlmostEqual(men["height_mean"], 183.2, places=1)
        self.assertAlmostEqual(men["height_sd"], 4.5, places=1)
        self.assertAlmostEqual(men["mass_mean"], 84.0, places=1)
        self.assertAlmostEqual(men["mass_sd"], 6.9, places=1)
        self.assertAlmostEqual(men["mvic_left_mean"], 202.7, places=1)
        self.assertAlmostEqual(men["mvic_left_sd"], 38.6, places=1)
        self.assertAlmostEqual(men["mvic_right_mean"], 199.0, places=1)
        self.assertAlmostEqual(men["mvic_right_sd"], 29.7, places=1)

    def test_coordinate_polarity_and_integral_discrepancy(self):
        audit = self.res["integral_audit"]
        self.assertTrue(audit["all_books_have_exactly_3_sign_divergences"])
        self.assertIn("HumacNorm dynamometer", audit["explanation"])

        # True physical discrepancy between angle and speed integrals
        self.assertLessEqual(audit["true_physical_work_discrepancy_median_J"], 1.5)
        self.assertAlmostEqual(audit["true_physical_work_discrepancy_median_J"], 1.05, places=1)
        self.assertLessEqual(audit["true_physical_work_discrepancy_mean_J"], 2.0)
        self.assertLessEqual(audit["true_physical_work_discrepancy_p95_J"], 4.0)

        # Naive signed difference was large due to uncoordinated coordinate frame
        self.assertGreater(audit["naive_signed_integral_abs_difference_median_J"], 20.0)

    def test_loso_cross_validation_primary(self):
        loso = self.res["loso_evaluations"]["n21_angle_integral"]
        self.assertEqual(loso["n_participants"], 21)
        self.assertEqual(loso["n_observations"], 42)

        # MAE metrics
        self.assertAlmostEqual(loso["mae_persistence_pre_equals_post_Nm"], 11.28, places=1)
        self.assertAlmostEqual(loso["mae_mean_retention_baseline_Nm"], 10.51, places=1)
        self.assertAlmostEqual(loso["mae_linear_pre_baseline_Nm"], 10.60, places=1)
        self.assertAlmostEqual(loso["mae_pre_plus_condition_baseline_Nm"], 11.00, places=1)
        self.assertAlmostEqual(loso["mae_model_with_work_Nm"], 10.62, places=1)

        # Paired delta MAE: base_cond - work
        dmae = loso["dmae_base_cond_minus_work_Nm"]
        ci95 = loso["dmae_base_cond_minus_work_95ci_Nm"]
        self.assertAlmostEqual(dmae, 0.38, places=1)
        # 95% CI strictly spans zero: does not achieve statistical significance
        self.assertLess(ci95[0], 0.0)
        self.assertGreater(ci95[1], 0.0)
        self.assertEqual(loso["verdict"], "INCONCLUSIVE_SPANS_ZERO")

        # Linear pre baseline beats model with work
        self.assertLess(loso["mae_linear_pre_baseline_Nm"], loso["mae_model_with_work_Nm"])

    def test_sensitivity_analyses(self):
        loso_speed = self.res["loso_evaluations"]["n21_speed_integral"]
        ci_speed = loso_speed["dmae_base_cond_minus_work_95ci_Nm"]
        self.assertLess(ci_speed[0], 0.0)
        self.assertGreater(ci_speed[1], 0.0)

        loso_n20_s021 = self.res["loso_evaluations"]["n20_exclude_s021"]
        ci_n20_s021 = loso_n20_s021["dmae_base_cond_minus_work_95ci_Nm"]
        self.assertLess(ci_n20_s021[0], 0.0)
        self.assertGreater(ci_n20_s021[1], 0.0)

        loso_n20_s004 = self.res["loso_evaluations"]["n20_exclude_s004"]
        ci_n20_s004 = loso_n20_s004["dmae_base_cond_minus_work_95ci_Nm"]
        self.assertLess(ci_n20_s004[0], 0.0)
        self.assertGreater(ci_n20_s004[1], 0.0)

    def test_fatigue_kinetics_and_work_distribution(self):
        w_dist = self.res["work_distribution"]
        self.assertGreater(w_dist["cond_75_mean_J"], w_dist["cond_90_mean_J"])
        self.assertGreater(w_dist["overlap_percentage"], 65.0)

        ret = self.res["retention_stats"]
        self.assertGreater(ret["cond_75_retention_mean_pct"], 95.0)
        self.assertGreater(ret["cond_90_retention_mean_pct"], 95.0)


if __name__ == "__main__":
    unittest.main()
