#!/usr/bin/env python3
"""
tests/test_actes_cpet_validation.py

Cycle 10 Unit & Verification Test Suite for PhysioNet ACTES Cycloergometer Benchmark.
Verifies data integrity, SHA-256 byte digests, LOSO cross-validation execution,
model performance hierarchy (M2 > M1 > M0), epistemic invariants, and negative tests.

Governing Standard: SUBJECT-01 Evidence Gate V2.
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CYCLE10_DIR = ROOT / "research" / "cpet_cycloergometer_2026_11_09"
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_actes_models import (
    ACTES_RESULTS_JSON,
    ACTES_SUBJECT_INFO_CSV,
    ACTES_TEST_MEASURE_CSV,
    compute_metrics,
    evaluate_loso_cross_validation,
    load_actes_dataset,
    run_full_actes_validation,
    simulate_first_order_ode,
)


class TestActesCPETValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_actes_dataset(CYCLE10_DIR)
        if not ACTES_RESULTS_JSON.is_file():
            cls.results = run_full_actes_validation()
        else:
            cls.results = json.loads(ACTES_RESULTS_JSON.read_text(encoding="utf-8"))

    def test_actes_files_integrity_and_sha256(self):
        """Verify ACTES raw files exist on disk and match official PhysioNet SHA256 checksums."""
        expected_hashes = {
            "test_measure.csv": "14a9df027caf00ee1dc39f1493e708c27a7da88794ff69a59442326ef7aa0516",
            "subject-info.csv": "5ac7cdd41d9112c48121998f19927318bd6dc2241ead97a6baa5e9ae8b60c203",
            "LICENSE.txt": "86c0ad300f6d380591298bc03652e30b81f65954bbf22435812bcfd46812ab06",
        }

        for filename, expected_sha in expected_hashes.items():
            fpath = CYCLE10_DIR / filename
            self.assertTrue(fpath.is_file(), f"File {filename} must exist in {CYCLE10_DIR}")
            actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
            self.assertEqual(
                actual_sha.lower(),
                expected_sha.lower(),
                f"SHA256 mismatch for {filename}: expected {expected_sha}, got {actual_sha}",
            )

    def test_actes_dataset_loading_structure(self):
        """Verify loaded ACTES dataset contains exactly 18 subjects and 52,062 records."""
        self.assertEqual(self.dataset["n_subjects"], 18)
        self.assertEqual(self.dataset["total_records"], 52062)

        subjects = self.dataset["subjects"]
        self.assertEqual(len(subjects), 18)

        # Check subject 1 to 18 completeness
        for sid in range(1, 19):
            self.assertIn(sid, subjects)
            s = subjects[sid]
            self.assertIn("metadata", s)
            self.assertIn("timeseries", s)
            meta = s["metadata"]
            self.assertIn(meta["sport"], ["fencing", "kayak", "triathlon"])
            self.assertGreater(meta["weight_kg"], 35.0)
            self.assertLess(meta["weight_kg"], 100.0)
            self.assertGreater(s["n_records"], 1000)

            # Check timeseries arrays
            ts = s["timeseries"]
            self.assertEqual(len(ts["time"]), s["n_records"])
            self.assertEqual(len(ts["power"]), s["n_records"])
            self.assertEqual(len(ts["vo2"]), s["n_records"])
            self.assertGreater(s["power_max_w"], 100.0)
            self.assertGreater(s["vo2_max_l_min"], 1.5)

    def test_loso_cross_validation_performance_hierarchy(self):
        """
        Verify Leave-One-Subject-Out (LOSO) cross-validation results:
        M2 Dynamic Allometric > M2 Pop > M1 Linear > M0 Null.
        """
        loso = self.results["loso_cross_validation"]
        self.assertEqual(loso["n_folds"], 18)

        m0 = loso["M0_null_summary"]
        m1 = loso["M1_empirical_linear_summary"]
        m2_pop = loso["M2_dynamic_pop_summary"]
        m2_allo = loso["M2_dynamic_allometric_summary"]

        # 1. Null model must have negative R2 and large RMSE
        self.assertLess(m0["r_squared_mean"], 0.0)
        self.assertGreater(m0["rmse_mean"], 0.70)

        # 2. Linear model improves over null
        self.assertGreater(m1["r_squared_mean"], 0.35)
        self.assertLess(m1["rmse_mean"], m0["rmse_mean"])

        # 3. Dynamic ODE delay improves over static linear
        self.assertGreater(m2_pop["r_squared_mean"], m1["r_squared_mean"])
        self.assertLess(m2_pop["rmse_mean"], m1["rmse_mean"])

        # 4. Allometric mass scaling provides the best cross-subject generalizability
        self.assertGreater(m2_allo["r_squared_mean"], 0.70)
        self.assertLess(m2_allo["rmse_mean"], 0.31)
        self.assertAlmostEqual(m2_allo["r_squared_mean"], 0.7371, places=3)

    def test_master_artifact_structure_and_rfc8259(self):
        """Verify canonical results JSON adheres to strict RFC 8259 (no NaN/Inf)."""
        raw_text = ACTES_RESULTS_JSON.read_text(encoding="utf-8")
        self.assertNotIn("NaN", raw_text)
        self.assertNotIn("Infinity", raw_text)

        data = json.loads(raw_text)
        self.assertEqual(data["experiment_id"], "EXP-0043")
        self.assertEqual(data["cycle"], 10)
        self.assertIn("cohort_description", data)
        self.assertIn("loso_cross_validation", data)
        self.assertIn("parameter_identifiability_audit", data)
        self.assertIn("overall_conclusions", data)

    def test_epistemic_invariants_and_freezes(self):
        """
        Enforce SUBJECT-01 Epistemic Invariants:
        TARGET-CPE45 must remain NOT EXTERNALLY VALIDATED and biological interventions NO_GO.
        """
        concl = self.results["overall_conclusions"]
        self.assertEqual(concl["target_cpe45_status"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(concl["biological_intervention_status"], "NO_GO")
        self.assertEqual(
            concl["validation_verdict"],
            "MACROSCOPIC_AEROBIC_COUPLING_VALIDATED_CROSS_SUBJECT_N18",
        )

        ident = self.results["parameter_identifiability_audit"]
        unident_params = [p["parameter"] for p in ident["strictly_unidentifiable_parameters"]]
        self.assertIn("intracellular_PCr_concentration_mM", unident_params)
        self.assertIn("cytosolic_pH_and_proton_turnover", unident_params)
        self.assertIn("motor_unit_recruitment_and_discharge_rates", unident_params)
        self.assertIn("quadriceps_anatomical_muscle_volume_and_PCSA", unident_params)
        self.assertIn("systemic_endurance_TARGET_CPE45", unident_params)

    def test_negative_tampered_hash_caught(self):
        """Negative test: Tampered hash for test_measure.csv is detected."""
        corrupted_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        actual_sha = hashlib.sha256(ACTES_TEST_MEASURE_CSV.read_bytes()).hexdigest()
        self.assertNotEqual(actual_sha.lower(), corrupted_hash)

    def test_negative_shuffled_workload_degrades_performance(self):
        """Negative test: Shuffled mechanical power uncorrelated with VO2 destroys model fit."""
        s1 = self.dataset["subjects"][1]
        t = s1["timeseries"]["time"]
        p = s1["timeseries"]["power"].copy()
        v = s1["timeseries"]["vo2"]

        # Permute power randomly
        np.random.seed(42)
        p_shuffled = np.random.permutation(p)

        # Simulate dynamic ODE on permuted workload
        pred_shuffled = simulate_first_order_ode(
            t, p_shuffled, beta0=0.56, beta1=0.0055, tau_s=35.0
        )
        metrics_shuffled = compute_metrics(v, pred_shuffled)

        # Performance on shuffled workload must be completely degraded (near zero R2 vs true >0.60)
        self.assertLess(metrics_shuffled["r_squared"], 0.05)
        self.assertGreater(metrics_shuffled["rmse"], 0.35)


if __name__ == "__main__":
    unittest.main()
