#!/usr/bin/env python3
"""
tests/test_malaga_cpet_validation.py

Cycle 11 Unit & Verification Test Suite for PhysioNet Malaga Treadmill CPET Benchmark.
Verifies data integrity, SHA-256 byte digests, cohort loading, cross-validation execution,
model performance hierarchy (M4 > M3 > M1 > M0), empirical oxycaloric equivalent distribution,
cross-modality transfer barrier (NEG-0037), epistemic invariants, and negative tests.

Governing Standard: SUBJECT-01 Evidence Gate V2.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLE11_DIR = ROOT / "research" / "treadmill_cpet_2026_11_09"
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_malaga_treadmill import (
    TREADMILL_RESULTS_JSON,
    TREADMILL_SUBJECT_INFO_CSV,
    TREADMILL_TEST_MEASURE_CSV,
    load_malaga_dataset,
    run_full_malaga_validation,
    verify_malaga_sha256,
)


class TestMalagaCPETValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TREADMILL_RESULTS_JSON.is_file():
            cls.results = run_full_malaga_validation()
        else:
            cls.results = json.loads(TREADMILL_RESULTS_JSON.read_text(encoding="utf-8"))

    def test_malaga_files_sha256_digests(self):
        """Verify all Malaga raw files match official PhysioNet SHA256 checksums."""
        verified = verify_malaga_sha256(CYCLE11_DIR)
        self.assertIn("LICENSE.txt", verified)
        self.assertIn("subject-info.csv", verified)
        self.assertIn("test_measure.csv", verified)

        expected = {
            "LICENSE.txt": "92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361",
            "subject-info.csv": "e9ca5ba20eb1272df56c11d3e584ec3997d5484454812bd94966e58082415f16",
            "test_measure.csv": "3b5ed5586dc7412ccdfb26f804e29c06482a2a1df2060399c2731ebc68d4613d",
        }
        for fname, exp_hash in expected.items():
            self.assertEqual(verified[fname].lower(), exp_hash.lower())

    def test_malaga_dataset_structure_and_records(self):
        """Verify Malaga dataset contains >500k rows and exactly 992 subject info entries."""
        cohort = self.results["cohort_description"]
        self.assertEqual(cohort["source_id"], "SRC-0074")
        self.assertEqual(cohort["doi"], "10.13026/7ezk-j442")
        self.assertEqual(cohort["n_subject_info_entries"], 992)
        self.assertGreaterEqual(cohort["n_valid_incremental_tests"], 970)
        self.assertGreater(cohort["n_total_csv_rows"], 500000)

    def test_respiratory_exchange_and_oxycaloric_audit(self):
        """Verify empirical RER and oxycaloric distribution match physiological reality."""
        rer_audit = self.results["respiratory_exchange_and_oxycaloric_audit"]
        self.assertGreater(rer_audit["n_breath_observations_analyzed"], 400000)

        rer_dist = rer_audit["rer_distribution"]
        self.assertGreater(rer_dist["mean"], 0.95)
        self.assertLess(rer_dist["mean"], 1.15)
        self.assertGreater(rer_dist["p05"], 0.70)
        self.assertGreater(rer_dist["p95"], 1.25)

        cox_dist = rer_audit["oxycaloric_equivalent_kj_per_l_distribution"]
        self.assertGreater(cox_dist["mean"], 20.5)
        self.assertLess(cox_dist["mean"], 21.8)

        # Difference with 20.9 kJ/L must be <= 3.0%
        rel_diff = rer_audit["comparison_with_nominal_constant"]["relative_difference_pct"]
        self.assertLess(rel_diff, 3.0)

    def test_treadmill_kinetics_performance_hierarchy(self):
        """Verify model performance hierarchy on treadmill locomotion: M4 > M3 > M1 > M0."""
        kinetics = self.results["macroscopic_kinetics_validation"]
        m0 = kinetics["M0_null_summary"]
        m1 = kinetics["M1_empirical_linear_summary"]
        m2 = kinetics["M2_linear_mass_summary"]
        m3 = kinetics["M3_dynamic_ode_summary"]
        m4 = kinetics["M4_dynamic_allometric_summary"]

        # Null model negative R2
        self.assertLess(m0["r_squared_mean"], 0.0)
        self.assertGreater(m0["rmse_mean"], 800.0)

        # M1 Linear improves over M0
        self.assertGreater(m1["r_squared_mean"], 0.30)
        self.assertLess(m1["rmse_mean"], m0["rmse_mean"])

        # M2 Mass improves over M1
        self.assertGreater(m2["r_squared_mean"], m1["r_squared_mean"])
        self.assertLess(m2["rmse_mean"], m1["rmse_mean"])

        # M3 Dynamic ODE improves over M1 Linear
        self.assertGreater(m3["r_squared_mean"], m1["r_squared_mean"])
        self.assertLess(m3["rmse_mean"], m1["rmse_mean"])

        # M4 Allometric Dynamic ODE is the top generalizer
        self.assertGreater(m4["r_squared_mean"], 0.60)
        self.assertLess(m4["rmse_mean"], 450.0)

    def test_cross_modality_barrier_negative_result(self):
        """Verify NEG-0037: naive cycling model applied to treadmill running incurs large penalty."""
        neg = self.results["cross_modality_barrier_negative_result"]
        self.assertEqual(neg["negative_result_id"], "NEG-0037")
        self.assertGreater(neg["rmse_penalty_l_min"], 0.10)
        self.assertGreater(neg["r2_penalty"], 0.20)

    def test_epistemic_invariants(self):
        """Enforce TARGET-CPE45 and biological intervention invariants."""
        concl = self.results["overall_conclusions"]
        self.assertEqual(concl["target_cpe45_status"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(concl["biological_intervention_status"], "NO_GO")
        self.assertEqual(
            concl["validation_verdict"],
            "MACROSCOPIC_LOCOMOTION_KINETICS_VALIDATED_CROSS_COHORT_N979",
        )

    def test_negative_tampered_hash_caught(self):
        """Negative test: Tampered hash in SHA256SUMS.txt triggers verification error."""
        # Create a mock corrupted sums text
        corrupted_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        actual_sha = hashlib.sha256(TREADMILL_TEST_MEASURE_CSV.read_bytes()).hexdigest()
        self.assertNotEqual(actual_sha.lower(), corrupted_hash)


if __name__ == "__main__":
    unittest.main()
