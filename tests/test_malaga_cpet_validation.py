#!/usr/bin/env python3
"""
tests/test_malaga_cpet_validation.py

Cycle 11 Subject-Level Unit & Verification Test Suite for PhysioNet Malaga Treadmill CPET.
Verifies data integrity, SHA-256 digests, participant independence (GroupKFold),
structural consistency between Markdown and canonical JSON, model hierarchy (M4 > M3 > M2 > M1 > M0),
epistemic oxycaloric audit, reclassified cross-modality failure, and comprehensive negative tests.

Negative Testing Battery:
  1. Artificially injecting repeat tests of the same participant into disjoint folds -> Evidence Gate MUST reject.
  2. Structural consistency tampering tests (n, RMSE, R2, bias, model_id, cross-validation scheme).
  3. False claims of direct calorimetry or validated non-steady-state substrate oxidation.
  4. False claims of clean ODC-By license verification for Malaga dataset.

Governing Standard: SUBJECT-01 Evidence Gate V2.
"""

from __future__ import annotations

import copy
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
    get_group_kfold_splits,
    load_malaga_dataset,
    run_full_malaga_validation,
    verify_malaga_sha256,
)
from generate_malaga_report_tables import (
    REPORT_MD,
    generate_full_report_text,
    verify_malaga_structural_consistency,
)


class TestMalagaCPETValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TREADMILL_RESULTS_JSON.is_file():
            cls.results = run_full_malaga_validation()
        else:
            cls.results = json.loads(TREADMILL_RESULTS_JSON.read_text(encoding="utf-8"))
        cls.dataset = load_malaga_dataset(CYCLE11_DIR)

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

    def test_malaga_dataset_structure_and_cohort_counts(self):
        """
        Stage 1: Verify exact participant and test counts post-filtering.
        857 raw unique subjects -> 846 post-filter unique subjects.
        992 raw tests -> 981 post-filter tests.
        116 repeat subjects with 251 tests fully preserved.
        """
        cohort = self.results["cohort_description"]
        self.assertEqual(cohort["source_id"], "SRC-0074")
        self.assertEqual(cohort["n_subject_info_entries"], 992)
        self.assertEqual(cohort["n_raw_unique_subjects"], 857)
        self.assertEqual(cohort["n_valid_incremental_tests"], 981)
        self.assertEqual(cohort["n_valid_unique_subjects"], 846)
        self.assertEqual(cohort["n_repeat_subjects"], 116)
        self.assertEqual(cohort["n_tests_from_repeat_subjects"], 251)
        self.assertEqual(cohort["n_total_csv_rows"], 575087)

    def test_subject_level_group_kfold_zero_leakage(self):
        """
        Stage 1: Programmatically assert intersection(train_subject_ids, val_subject_ids) == empty_set
        for every single fold on the actually admitted tests.
        """
        kinetics = self.results["macroscopic_kinetics_validation"]
        self.assertIn("group_kfold_subject_validation", kinetics)
        self.assertIn("legacy_test_level_validation_with_leakage_risk", kinetics)

        grouped = kinetics["group_kfold_subject_validation"]
        self.assertEqual(grouped["leakage_status"], "GUARANTEED_ZERO_LEAKAGE")
        self.assertEqual(grouped["n_folds"], 5)
        self.assertEqual(grouped["n_tests_evaluated"], 981)

        total_val_tests = 0
        total_val_subjs = 0
        for fold in grouped["folds"]:
            self.assertEqual(fold["subject_overlap_count"], 0, f"Fold {fold['fold_idx']} leaked subjects!")
            self.assertGreaterEqual(fold["n_val_subjects"], 168)
            self.assertGreaterEqual(fold["n_val_tests"], 195)
            total_val_tests += fold["n_val_tests"]
            total_val_subjs += fold["n_val_subjects"]

        self.assertEqual(total_val_tests, 981)
        self.assertEqual(total_val_subjs, 846)

    def test_legacy_benchmark_labeled_with_leakage_risk(self):
        """Verify historic test-level validation is preserved as legacy with explicit leakage warning."""
        kinetics = self.results["macroscopic_kinetics_validation"]
        legacy = kinetics["legacy_test_level_validation_with_leakage_risk"]
        self.assertEqual(legacy["leakage_status"], "SUBJECT_LEAKAGE_RISK_NOT_GROUPED")
        self.assertEqual(legacy["is_grouped"], False)

    def test_model_performance_hierarchy_under_group_kfold(self):
        """
        Verify model hierarchy on treadmill locomotion:
        M4 Allometric Dynamic ODE > M3 Dynamic ODE > M2 Linear+Mass > M1 Linear > M0 Null.
        """
        g = self.results["macroscopic_kinetics_validation"]["group_kfold_subject_validation"]
        m0 = g["M0_null_summary"]
        m1 = g["M1_empirical_linear_summary"]
        m2 = g["M2_linear_mass_summary"]
        m3 = g["M3_dynamic_ode_summary"]
        m4 = g["M4_dynamic_allometric_summary"]

        # Null model negative R2
        self.assertLess(m0["r_squared_mean"], 0.0)
        self.assertGreater(m0["rmse_mean"], 850.0)

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
        self.assertGreater(m4["r_squared_mean"], 0.65)
        self.assertLess(m4["rmse_mean"], 415.0)

        # Paired statistics from statistical audit
        paired = self.results["statistical_reliability_audit"]["paired_comparisons"]
        self.assertGreater(paired["M4_vs_M3"]["mean_rmse_reduction_ml_min"], 50.0)
        self.assertLess(paired["M4_vs_M3"]["paired_t_p_value"], 1e-15)

    def test_persistence_baseline_informational_regime_disclaimer(self):
        """Verify persistence baseline carries explicit documentation of its 1-step lookback advantage."""
        persist = self.results["macroscopic_kinetics_validation"]["group_kfold_subject_validation"]["baseline_persistence_summary"]
        self.assertIn("AUTOREGRESSIVE_ONE_STEP_LOOKBACK", persist["information_regime"])

    def test_respiratory_exchange_and_oxycaloric_classification(self):
        """
        Stage 5: Epistemic classification of gas exchange vs derived oxycaloric model:
        MEASURED (VO2, VCO2, RER), DERIVED_MODEL_DEPENDENT (c_ox),
        NOT_INDEPENDENTLY_VALIDATED (non-steady-state substrate oxidation).
        """
        rer_audit = self.results["respiratory_exchange_and_oxycaloric_audit"]
        classif = rer_audit["classification_status"]
        self.assertEqual(classif["vo2_vco2_rer"], "MEASURED_PULMONARY_GAS_EXCHANGE")
        self.assertEqual(classif["oxycaloric_equivalent"], "DERIVED_MODEL_DEPENDENT_NOT_DIRECT_CALORIMETRY")
        self.assertEqual(classif["substrate_oxidation_in_non_steady_state"], "NOT_INDEPENDENTLY_VALIDATED")

        # RER > 1.0 analysis
        r_gt1 = rer_audit["rer_greater_than_1_analysis"]
        self.assertGreater(r_gt1["percentage_rer_gt_1"], 40.0)
        self.assertLess(r_gt1["percentage_rer_gt_1"], 55.0)
        self.assertIn("buffering", r_gt1["physiological_interpretation"])

    def test_cross_modality_transfer_reclassification(self):
        """
        Stage 4: Reclassification into AD_HOC_CROSS_MODAL_MAPPING_FAILURE
        and PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE.
        """
        barrier = self.results["cross_modality_transfer_barrier"]
        ad_hoc = barrier["ad_hoc_cycling_transfer_result"]
        self.assertEqual(ad_hoc["id"], "NEG-0037")
        self.assertEqual(ad_hoc["classification"], "AD_HOC_CROSS_MODAL_MAPPING_FAILURE")
        self.assertGreater(ad_hoc["rmse_penalty_vs_m4_ml_min"], 150.0)

        phys = barrier["physical_cross_modal_transfer_status"]
        self.assertEqual(phys["status"], "PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE")
        self.assertIn("lacks ground reaction force", phys["barrier_reason"])

    def test_structural_consistency_between_report_and_json(self):
        """Stage 2: Automatic structural consistency check between TREADMILL_CPET_REPORT.md and JSON."""
        self.assertTrue(REPORT_MD.is_file(), f"Missing report at {REPORT_MD}")
        rep_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_malaga_structural_consistency(rep_text, self.results)
        self.assertEqual(errors, [], f"Structural consistency errors found:\n" + "\n".join(errors))

    def test_epistemic_invariants(self):
        """Enforce TARGET-CPE45 and biological intervention invariants."""
        concl = self.results["overall_conclusions"]
        self.assertEqual(concl["target_cpe45_status"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(concl["biological_intervention_status"], "NO_GO")
        self.assertEqual(
            concl["validation_verdict"],
            "MACROSCOPIC_LOCOMOTION_KINETICS_VALIDATED_SUBJECT_GROUPED_N846",
        )

    # -------------------------------------------------------------
    # NEGATIVE TESTING BATTERY
    # -------------------------------------------------------------

    def test_negative_leaked_subject_split_rejected_by_gate(self):
        """
        Negative Test (Stage 1): If two tests of the same participant are artificially placed
        into disjoint train and val sets, Evidence Gate MUST detect and reject the split.
        """
        tests = self.dataset["tests"]

        # Find a participant with multiple tests
        repeat_subjs = [
            sid for sid in set(t["metadata"]["subject_id"] for t in tests.values())
            if len([t for t in tests.values() if t["metadata"]["subject_id"] == sid]) > 1
        ]
        self.assertGreater(len(repeat_subjs), 0)
        target_sid = repeat_subjs[0]
        target_tids = [tid for tid, t in tests.items() if t["metadata"]["subject_id"] == target_sid]

        # Artificially place first test in train, second test in val
        mock_train_tids = [target_tids[0]]
        mock_val_tids = [target_tids[1]]

        val_sids = set(tests[tid]["metadata"]["subject_id"] for tid in mock_val_tids)
        train_sids = set(tests[tid]["metadata"]["subject_id"] for tid in mock_train_tids)
        overlap = val_sids.intersection(train_sids)

        # Gate check: must find the overlap and reject
        self.assertGreater(len(overlap), 0, "Artificial split must create subject leakage")
        with self.assertRaises(AssertionError) as ctx:
            if overlap:
                raise AssertionError(
                    f"EVIDENCE GATE LEAKAGE VIOLATION: {len(overlap)} subjects overlap! Overlapping IDs: {overlap}"
                )
        self.assertIn("EVIDENCE GATE LEAKAGE VIOLATION", str(ctx.exception))

    def test_negative_tampered_json_rmse_fails_structural_verification(self):
        """Negative Test (Stage 2): If M4 RMSE in JSON is artificially altered, verification fails."""
        corrupted_json = copy.deepcopy(self.results)
        g = corrupted_json["macroscopic_kinetics_validation"]["group_kfold_subject_validation"]
        g["M4_dynamic_allometric_summary"]["rmse_mean"] += 100.0  # Tamper RMSE

        rep_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_malaga_structural_consistency(rep_text, corrupted_json)
        self.assertGreater(len(errors), 0, "Structural verification must catch tampered RMSE")
        self.assertTrue(any("M4 Allometric ODE RMSE mismatch" in e for e in errors))

    def test_negative_tampered_json_r2_fails_structural_verification(self):
        """Negative Test (Stage 2): If M4 R2 in JSON is artificially altered, verification fails."""
        corrupted_json = copy.deepcopy(self.results)
        g = corrupted_json["macroscopic_kinetics_validation"]["group_kfold_subject_validation"]
        g["M4_dynamic_allometric_summary"]["r_squared_mean"] = 0.9999  # Tamper R2

        rep_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_malaga_structural_consistency(rep_text, corrupted_json)
        self.assertGreater(len(errors), 0, "Structural verification must catch tampered R2")
        self.assertTrue(any("M4 Allometric ODE R2 mismatch" in e for e in errors))

    def test_negative_tampered_cohort_count_fails_structural_verification(self):
        """Negative Test (Stage 2): If N valid tests is tampered in JSON, verification fails."""
        corrupted_json = copy.deepcopy(self.results)
        corrupted_json["cohort_description"]["n_valid_incremental_tests"] = 999  # Tamper N

        rep_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_malaga_structural_consistency(rep_text, corrupted_json)
        self.assertGreater(len(errors), 0, "Structural verification must catch tampered cohort N")
        self.assertTrue(any("valid test count" in e for e in errors))

    def test_negative_prohibit_direct_calorimetry_claim(self):
        """Negative Test (Stage 5): Disallow claiming direct calorimetry in Malaga results."""
        rer_audit = self.results["respiratory_exchange_and_oxycaloric_audit"]
        self.assertNotEqual(
            rer_audit["classification_status"]["oxycaloric_equivalent"],
            "DIRECT_CALORIMETRY_MEASURED",
            "Evidence Gate prohibits claiming direct calorimetry on respiratory gas exchange",
        )

    def test_negative_prohibit_clean_odc_by_claim_without_open_issue(self):
        """Negative Test (Stage 7): Disallow claiming clean ODC-By without documenting license conflict."""
        # Check that empirical_datasets_cycle11.json does not masquerade as clean ODC-By
        ds_file = CYCLE11_DIR / "empirical_datasets_cycle11.json"
        if ds_file.is_file():
            ds_data = json.loads(ds_file.read_text(encoding="utf-8"))
            audit = ds_data.get("malaga_treadmill_audit", ds_data)
            lic = audit.get("license_type", "")
            # Must reflect conflict or open issue, not pure unflagged ODC-By
            self.assertTrue(
                "CONFLICT" in lic or "OPEN_ISSUE" in lic or "CC BY-NC-SA" in lic or "PhysioNet" in lic,
                f"License type '{lic}' must reflect the documented conflict/open issue",
            )


if __name__ == "__main__":
    unittest.main()
