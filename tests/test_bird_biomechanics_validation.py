#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUBJECT-01 — Unit Tests for Cycle 12 Biomechanical Validation (Bird et al. 2026)
Tests cryptographic provenance, variable ontology, dynamic mechanics, fatigue models,
and structural consistency with negative testing battery.
"""

from pathlib import Path
import copy
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
CYCLE12_DIR = ROOT / "research" / "muscle_force_biomechanics_2026_11_10"
RESULTS_JSON = CYCLE12_DIR / "biomechanics_validation_results.json"
REPORT_MD = CYCLE12_DIR / "BIOMECHANICAL_VALIDATION_REPORT.md"
RAW_DIR = CYCLE12_DIR / "raw_data"
PDF_PATH = RAW_DIR / "arxiv_2510_20866.pdf"

from tools.generate_biomechanics_report_tables import verify_biomechanics_structural_consistency


class TestBirdBiomechanicsValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not RESULTS_JSON.is_file():
            raise FileNotFoundError(f"Missing results JSON: {RESULTS_JSON}")
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            cls.results = json.load(f)

    def test_sha256_digests_against_official_dryad_api(self):
        """Verify that expected file digests match official Dryad API values."""
        prov = self.results["stage1_cryptographic_provenance"]
        files_audit = prov["files_audit"]
        self.assertIn("DATA_Dynamic_Knee.mat", files_audit)
        self.assertIn("DATA_Isometric_Knee.xlsx", files_audit)
        self.assertIn("DATA_Fatiguing_Isometric_Knee.xlsx", files_audit)

        # Official Dryad API digest for DATA_Dynamic_Knee.mat
        self.assertEqual(
            files_audit["DATA_Dynamic_Knee.mat"]["expected_sha256"],
            "7cb256a8eadf621b9822266c473b620b8121e40fb62ed7615cdfbb32024da7f9",
        )
        # Official Dryad API digest for DATA_Isometric_Knee.xlsx
        self.assertEqual(
            files_audit["DATA_Isometric_Knee.xlsx"]["expected_sha256"],
            "1c415188ba7008586d05e5c4f0a0794c2858fe63e8a4f176d4b653630a7ac37f",
        )
        # Verify LSTM_Data_Outputs.zip has actual 64-char SHA256 (not byte size!)
        self.assertEqual(
            files_audit["LSTM_Data_Outputs.zip"]["expected_sha256"],
            "863307becd150259a2bdeb685eceee2be65e5c24d206cceebb4162d7e7e471f0",
        )
        # Verify LME_Data_Outputs.mat has distinct official SHA256 from CODE_LME_Estimate_Torque.m
        self.assertEqual(
            files_audit["LME_Data_Outputs.mat"]["expected_sha256"],
            "f532559ce51352342503d776821b13cf78cee81e52d6ba8f2ac48860642199b7",
        )
        self.assertEqual(
            files_audit["CODE_LME_Estimate_Torque.m"]["expected_sha256"],
            "f83dcf36c9226498908d7760655df98f494b1cecc7fd034a66b411e4c672a1d8",
        )
        self.assertNotEqual(
            files_audit["LME_Data_Outputs.mat"]["expected_sha256"],
            files_audit["CODE_LME_Estimate_Torque.m"]["expected_sha256"],
        )
        # Rule: Acquired files must be ACQUIRED_AND_VERIFIED, unacquired files must be PENDING
        acquired_files = {
            "arxiv_2510_20866.pdf",
            "DATA_Dynamic_Knee.mat",
            "DATA_Isometric_Knee.xlsx",
            "LME_Data_Outputs.mat",
            "LSTM_Data_Outputs.zip",
        }
        for fname, fmeta in files_audit.items():
            if fname in acquired_files:
                self.assertEqual(
                    fmeta["status"],
                    "ACQUIRED_AND_VERIFIED",
                    f"Acquired file {fname} must be ACQUIRED_AND_VERIFIED",
                )
                self.assertEqual(fmeta["sha256"], fmeta["expected_sha256"])
            else:
                self.assertEqual(
                    fmeta["status"],
                    "PENDING_OWNER_ASSISTED_ACQUISITION",
                    f"Unacquired file {fname} must not be marked VERIFIED",
                )

    def test_manuscript_sha256_and_unabridged_pdf(self):
        """Verify that acquired primary manuscript PDF matches verified SHA256 and size."""
        self.assertTrue(PDF_PATH.is_file(), f"PDF manuscript must be present at {PDF_PATH}")
        data = PDF_PATH.read_bytes()
        self.assertEqual(len(data), 5494859, "PDF size must match exact unabridged manuscript (5,494,859 bytes)")
        actual_sha = hashlib.sha256(data).hexdigest()
        self.assertEqual(
            actual_sha,
            "eb1377aecc1df8564e5ac3f99b4afa8b8dc673df1736080de0ab7f598e02176c",
        )

    def test_cohort_and_protocol_counts(self):
        """Verify participant numbers across all 4 protocols."""
        from tools.evaluate_bird_biomechanics import COHORT_DEMOGRAPHICS

        self.assertEqual(COHORT_DEMOGRAPHICS["isometric_knee"]["n_participants_tested"], 16)
        self.assertEqual(COHORT_DEMOGRAPHICS["isometric_ankle"]["n_participants_tested"], 6)
        self.assertEqual(COHORT_DEMOGRAPHICS["fatiguing_isometric_knee"]["n_participants_tested"], 18)
        self.assertEqual(COHORT_DEMOGRAPHICS["dynamic_knee"]["n_participants_tested"], 6)

    def test_dynamic_decoupling_findings(self):
        """Verify empirical decoupling of torque from activation and fascicle strain in dynamic motion."""
        dyn = self.results["stage3_dynamic_contraction_mechanics"]
        decoupling = dyn["decoupling_findings_published"]
        # In dynamic contractions, static correlation is broken (R2 < 0.25)
        self.assertLess(decoupling["torque_vs_activation_fixed"], 0.20)
        self.assertLess(decoupling["torque_vs_fascicle_strain_fixed"], 0.05)
        self.assertLess(decoupling["torque_vs_fascicle_strain_rate_fixed"], 0.05)

    def test_dynamic_models_hierarchy(self):
        """Verify dynamic models (M3 Hill, M4 SUBJECT-01) substantially outperform static models (M1, M2, M0)."""
        dyn = self.results["stage3_dynamic_contraction_mechanics"]["model_comparisons"]
        m4 = dyn["M4_subject01_biomechanical"]
        m3 = dyn["M3_hill_type_dynamic"]
        m1 = dyn["M1_static_semg_activation"]
        m0 = dyn["M0_constant_baseline"]

        self.assertGreater(m4["r_squared_mean"], 0.70)
        self.assertGreater(m3["r_squared_mean"], 0.55)
        self.assertLess(m1["r_squared_mean"], 0.25)
        self.assertLess(m0["r_squared_mean"], 0.0)

    def test_fatiguing_protocol_neuromuscular_compensation(self):
        """Verify +26 +/- 15% activation drift under 20-min fatiguing isometric knee extensions."""
        fat = self.results["stage4_fatigue_and_recovery"]
        self.assertEqual(fat["n_participants"], 18)
        self.assertEqual(fat["protocol_duration_minutes"], 20)
        self.assertAlmostEqual(fat["mean_activation_increase_pct"], 26.0, delta=1.0)
        self.assertAlmostEqual(fat["sd_activation_increase_pct"], 15.0, delta=1.0)
        self.assertEqual(fat["significant_participants_count"], 17)
        self.assertEqual(fat["resistant_participants_count"], 1)

    def test_fatigue_models_hierarchy(self):
        """Verify biophysical fatigue model M2 captures fatigue whereas M0 fails."""
        fat_models = self.results["stage4_fatigue_and_recovery"]["fatigue_models_evaluation"]
        m2 = fat_models["M2_subject01_biophysical_fatigue"]
        m0 = fat_models["M0_constant_capacity"]

        self.assertGreater(m2["r_squared"], 0.75)
        self.assertLess(m2["rmse_force_loss_pct"], 7.0)
        self.assertLess(m0["r_squared"], 0.0)
        self.assertIn("REJECTED", m0["verdict"])

    def test_epistemic_invariants_cpe45_and_biological_interventions(self):
        """Verify non-negotiable invariants: TARGET-CPE45 = NOT EXTERNALLY VALIDATED, BIOLOGICAL INTERVENTIONS = NO_GO."""
        invariants = self.results["invariants"]
        self.assertEqual(invariants["target_cpe45"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(invariants["biological_interventions"], "NO_GO")

    def test_report_markdown_json_structural_consistency(self):
        """Verify that BIOMECHANICAL_VALIDATION_REPORT.md matches canonical JSON 100%."""
        self.assertTrue(REPORT_MD.is_file(), f"Report markdown missing: {REPORT_MD}")
        md_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_biomechanics_structural_consistency(md_text, self.results)
        self.assertEqual(len(errors), 0, f"Structural inconsistencies found: {errors}")

    def test_negative_reject_dynamometer_torque_as_single_muscle_force(self):
        """Negative Test: Disallow equating dynamometer torque to single muscle force without moment arm."""
        onto = self.results["stage2_variable_ontology"]["variable_ontology_and_epistemic_classification"]
        t_joint = onto["joint_torque"]
        self.assertNotEqual(t_joint["epistemic_status"], "MEASURED_SINGLE_MUSCLE_FORCE")
        self.assertEqual(t_joint["epistemic_status"], "MEASURED_JOINT_LEVEL")
        self.assertIn("NOT", t_joint["biomechanical_relationship"])

    def test_negative_prohibit_cpe45_claim_on_20min_fatigue(self):
        """Negative Test: Disallow claiming 20-min knee extension validates TARGET-CPE45."""
        fat = self.results["stage4_fatigue_and_recovery"]
        epistemic = fat["epistemic_boundaries"]
        self.assertIn("DOES NOT validate TARGET-CPE45", epistemic["protocol_does_not_validate_cpe45"])
        self.assertEqual(epistemic["target_cpe45_status"], "NOT EXTERNALLY VALIDATED")

    def test_four_tier_taxonomy_separation(self):
        """Verify strict 4-tier model taxonomy separation and honest empirical status."""
        dyn = self.results["stage3_dynamic_contraction_mechanics"]
        self.assertIn("BIRD_AUTHOR_REPORTED", dyn)
        self.assertIn("model_taxonomy_status", dyn)

        status = dyn["model_taxonomy_status"]
        self.assertEqual(status["SUBJECT01_INDEPENDENT_REPRODUCTION"]["status"], "REPRODUCED_CONFIRMED_ON_RAW_ARRAYS")
        self.assertEqual(status["SUBJECT01_NEW_MODEL_FIT"]["status"], "FIT_ON_RAW_OBSERVATIONS")
        self.assertEqual(status["SUBJECT01_HELD_OUT_PREDICTION"]["status"], "EXECUTED_LOSO_ON_RAW_OBSERVATIONS")

    def test_empirical_author_metrics_reproduction(self):
        """Verify independent reproduction of author LME and LSTM metrics from raw outputs."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        self.assertTrue(empirical_file.is_file(), "Empirical validation JSON must exist")
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        lme = emp["reproduced_author_lme_outputs"]
        self.assertEqual(lme["status"], "REPRODUCED_CONFIRMED")
        self.assertAlmostEqual(lme["mean_r2"], 0.984, delta=0.002)
        self.assertAlmostEqual(lme["mean_nrmse_pct"], 3.3, delta=0.1)

        lstm = emp["reproduced_author_lstm_outputs"]
        self.assertEqual(lstm["status"], "REPRODUCED_CONFIRMED")
        self.assertAlmostEqual(lstm["mean_r2"], 0.988, delta=0.002)
        self.assertAlmostEqual(lstm["mean_rmse_pct"], 2.7, delta=0.1)

    def test_cross_subject_loso_radar_generalization_collapse(self):
        """Verify critical audit finding: UWB radar collapses under cross-subject LOSO (R2 < 0)."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_and_loso_evaluation"]
        radar = dyn["models_evaluation"]["UWB_radar_ridge"]
        # Intra-participant 5-fold CV achieves high accuracy
        self.assertGreater(radar["intra_participant_5fold"]["r_squared_mean"], 0.95)
        # Cross-subject LOSO completely collapses (R2 < 0)
        self.assertLess(radar["cross_subject_loso"]["r_squared_mean"], 0.0)
        self.assertGreater(radar["cross_subject_loso"]["nrmse_pct_mean"], 35.0)

    def test_cross_subject_loso_physiological_models(self):
        """Verify that physiological models maintain positive generalization across human subjects."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_and_loso_evaluation"]
        m1 = dyn["models_evaluation"]["M1_static_semg"]
        m4 = dyn["models_evaluation"]["M4_subject01_biomechanical"]

        # sEMG maintains positive cross-subject generalization
        self.assertGreater(m1["cross_subject_loso"]["r_squared_mean"], 0.40)
        # Multiscale model maintains positive cross-subject generalization
        self.assertGreater(m4["cross_subject_loso"]["r_squared_mean"], 0.25)

    def test_physical_constraints_audit(self):
        """Verify that all physical constraints are marked unmeasured in Bird 2026 and classified appropriately."""
        constraints = self.results["physical_constraints_audit"]
        expected_keys = [
            "specific_muscle_tension_sigma_max",
            "patellar_tendon_peak_force",
            "ultimate_patellar_tendon_strain",
            "patellar_tendon_safety_factor",
            "muscle_volume_hypertrophy_limit",
            "microvascular_diffusion_limit",
            "concurrent_training_phenotypic_tradeoff",
        ]
        for key in expected_keys:
            self.assertIn(key, constraints)
            self.assertFalse(constraints[key]["measured_in_bird_2026"])
            self.assertIn(constraints[key]["epistemic_status"], [
                "LITERATURE_DERIVED",
                "ASSUMPTION_AND_LEVER_CALCULATION",
                "THEORETICAL_DERIVATION",
                "ANATOMICAL_HYPOTHESIS",
                "LITERATURE_DERIVED_BIOCHEMICAL_MECHANISM",
            ])

    def test_henneman_size_principle_vs_ampk_mtorc1_correction(self):
        """Verify explicit correction of Henneman's Size Principle vs AMPK-mTORC1 Molecular Interference."""
        tradeoff = self.results["physical_constraints_audit"]["concurrent_training_phenotypic_tradeoff"]
        self.assertEqual(tradeoff["mechanism"], "AMPK-mTORC1 Molecular Interference Effect")
        correction = tradeoff["correction_regarding_henneman"]
        self.assertIn("Henneman's Size Principle strictly governs", correction)
        self.assertIn("motor unit recruitment", correction.lower())
        self.assertIn("AMPK", correction)
        self.assertIn("mTORC1", correction)

    def test_leakage_and_pseudoreplication_audit(self):
        """Verify intra-participant vs LOSO leakage and condition pseudoreplication controls."""
        dyn_leakage = self.results["stage3_dynamic_contraction_mechanics"]["leakage_and_pseudoreplication_audit"]
        self.assertIn("intra-subject 5-fold CV", dyn_leakage["participant_level_leakage"]["finding"])
        self.assertIn("SAME 6 participants", dyn_leakage["condition_level_pseudoreplication"]["finding"])
        self.assertIn("N=6, not N=96", dyn_leakage["condition_level_pseudoreplication"]["implication"])
        self.assertIn("temporal autocorrelation", dyn_leakage["temporal_autocorrelation_leakage"]["finding"])
        self.assertIn("peak MVC", dyn_leakage["mvc_normalization_leakage"]["finding"])

    def test_negative_tampered_model_r2_fails_structural_verification(self):
        """Negative Test: Tampering model R2 in JSON triggers structural verification error."""
        corrupted = copy.deepcopy(self.results)
        corrupted["stage3_dynamic_contraction_mechanics"]["model_comparisons"]["M4_subject01_biomechanical"]["r_squared_mean"] = 0.999
        md_text = REPORT_MD.read_text(encoding="utf-8")
        errors = verify_biomechanics_structural_consistency(md_text, corrupted)
        self.assertGreater(len(errors), 0, "Tampered R2 must be caught by structural verification")

    def test_negative_tampered_source_id_fails_structural_verification(self):
        """Negative Test: Tampering source ID triggers structural verification error."""
        md_text = REPORT_MD.read_text(encoding="utf-8").replace("SRC-0076", "SRC-9999")
        errors = verify_biomechanics_structural_consistency(md_text, self.results)
        self.assertGreater(len(errors), 0, "Missing SRC-0076 must trigger error")

    def test_stage1_observation_discrepancy_resolution(self):
        """Verify resolution of the 3,226 dynamic observations (1,382 passive protocol, 1,844 active protocol)."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        self.assertTrue(empirical_file.is_file(), "Empirical JSON must exist")
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_scientific_audit"]
        stage1 = dyn["stage1_raw_observation_audit"]
        self.assertEqual(stage1["total_dynamic_observations"], 3226)
        self.assertEqual(stage1["passive_protocol_count"], 1382)
        self.assertEqual(stage1["active_protocol_count"], 1844)
        self.assertEqual(stage1["active_positive_torque_count"], 1821)
        self.assertEqual(stage1["active_negative_count"], 23)
        self.assertEqual(stage1["passive_torque_zero_count"], 1382)
        self.assertEqual(stage1["active_negative_sensor_drift_count"], 23)
        self.assertTrue(stage1["sum_check_exact_match"])
        self.assertTrue(stage1["protocol_partition_exact"])
        self.assertTrue(stage1["all_channels_clean"])
        self.assertIn("fraction of MVC", stage1["torque_units"])

        # Check negative offset details
        neg = stage1["negative_values_details"]
        self.assertLess(neg["max_fraction_mvc"], 0.0)
        self.assertGreater(neg["min_fraction_mvc"], -0.05)
        self.assertEqual(neg["count"], 23)

    def test_stage2_cross_validation_scheme_separation(self):
        """Verify strict separation of INTRA_SUBJECT_CV, BLOCKED_TEMPORAL_CV, LOSO, PRECOMPUTED, RETRAINING."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_scientific_audit"]
        cv_schemes = dyn["stage2_cv_schemes_definition"]
        self.assertIn("INTRA_SUBJECT_CV", cv_schemes)
        self.assertIn("BLOCKED_TEMPORAL_CV", cv_schemes)
        self.assertIn("LEAVE_ONE_SUBJECT_OUT", cv_schemes)
        self.assertIn("AUTHOR_REPORTED_PRECOMPUTED_OUTPUTS", cv_schemes)
        self.assertIn("FULL_MODEL_RETRAINING", cv_schemes)
        self.assertFalse(cv_schemes["m4_held_out_leakage_audit"]["uses_held_out_subject_data"])

    def test_stage3_uwb_radar_sensitivity_suite(self):
        """Verify UWB radar collapse persists across all 15 sensitivity configurations (all mean R2 < 0)."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_scientific_audit"]
        suite = dyn["stage3_radar_sensitivity_suite"]
        self.assertEqual(len(suite), 15, "Sensitivity suite must contain exactly 15 configurations")
        for cfg_name, cfg_res in suite.items():
            self.assertTrue(
                cfg_res["is_mean_r2_negative"],
                f"Configuration {cfg_name} must produce negative mean R2 under LOSO (got {cfg_res['r2_mean']:.4f})",
            )
            self.assertLess(cfg_res["r2_mean"], 0.0)

    def test_stage4_m4_falsification_vs_semg_and_hill(self):
        """Verify M4 is falsified as superior architecture: underperforms M1 sEMG, no benefit over M3 Hill."""
        empirical_file = CYCLE12_DIR / "bird2026_empirical_validation.json"
        with open(empirical_file, "r", encoding="utf-8") as f:
            emp = json.load(f)

        dyn = emp["dynamic_knee_scientific_audit"]
        all_dset = dyn["stage4_dataset_evaluations"]["all_dynamic_observations"]
        models = all_dset["models"]
        stats_comp = all_dset["statistical_comparisons"]

        m1_r2 = models["M1_static_semg"]["cross_subject_loso"]["r_squared_mean"]
        m3_r2 = models["M3_hill_dynamic"]["cross_subject_loso"]["r_squared_mean"]
        m4_r2 = models["M4_subject01_biomechanical"]["cross_subject_loso"]["r_squared_mean"]

        self.assertAlmostEqual(m1_r2, 0.4628, delta=0.005)
        self.assertAlmostEqual(m3_r2, 0.3103, delta=0.005)
        self.assertAlmostEqual(m4_r2, 0.3251, delta=0.005)

        # M4 vs M3 advantage is statistically insignificant and does NOT prove equivalence
        self.assertFalse(stats_comp["m4_vs_m3_hill"]["statistically_significant_at_alpha_005"])
        self.assertFalse(stats_comp["m4_vs_m3_hill"]["does_p_prove_equivalence"])
        self.assertGreater(stats_comp["m4_vs_m3_hill"]["paired_t_pvalue"], 0.05)

        # M4 vs M1 sEMG: point estimate favors M1, but difference is NOT statistically significant at alpha=0.05
        self.assertFalse(stats_comp["m4_vs_m1_semg"]["statistically_significant_at_alpha_005"])
        self.assertAlmostEqual(stats_comp["m4_vs_m1_semg"]["paired_t_pvalue"], 0.0571, delta=0.005)
        self.assertAlmostEqual(stats_comp["m4_vs_m1_semg"]["wilcoxon_pvalue"], 0.0625, delta=0.005)
        self.assertLess(stats_comp["m4_vs_m1_semg"]["delta_r2_ci95"][0], 0.0)
        self.assertGreater(stats_comp["m4_vs_m1_semg"]["delta_r2_ci95"][1], 0.0)
        self.assertEqual(stats_comp["m4_vs_m1_semg"]["model_scope_designation"], "ENGINEERED_FEATURE_M4_NO_VERIFIED_ADVANTAGE")
        self.assertEqual(stats_comp["m4_vs_m1_semg"]["multiscale_architecture_status"], "FULL_SUBJECT01_MULTISCALE_ARCHITECTURE_NOT_FALSIFIED_BY_THIS_TEST")

        # On active-only points (torque > 0), both M1 and M4 collapse below zero
        act_dset = dyn["stage4_dataset_evaluations"]["active_only_conditions"]
        act_m1 = act_dset["models"]["M1_static_semg"]["cross_subject_loso"]["r_squared_mean"]
        act_m4 = act_dset["models"]["M4_subject01_biomechanical"]["cross_subject_loso"]["r_squared_mean"]
        self.assertLess(act_m1, 0.0)
        self.assertLess(act_m4, 0.0)

    def test_registry_neg0038_and_neg0039_integrity(self):
        """Verify NEG-0038 and NEG-0039 presence, uniqueness, and proper referencing."""
        neg_file = ROOT / "registry" / "negative_results.json"
        with open(neg_file, "r", encoding="utf-8") as f:
            negs = json.load(f)

        neg_ids = {n["id"]: n for n in negs}
        self.assertIn("NEG-0038", neg_ids)
        self.assertIn("NEG-0039", neg_ids)

        neg38 = neg_ids["NEG-0038"]
        self.assertIn("TARGET-CPE45", neg38["hypothesis"])
        self.assertIn("extrapolate", neg38["impact"].lower())

        neg39 = neg_ids["NEG-0039"]
        self.assertIn("UWB radar", neg39["hypothesis"])
        self.assertIn("M4", neg39["hypothesis"])
        self.assertIn("-2.4457", neg39["result"])
        self.assertIn("ENGINEERED_FEATURE_M4_NO_VERIFIED_ADVANTAGE", neg39["result"])
        self.assertIn("FULL_SUBJECT01_MULTISCALE_ARCHITECTURE_NOT_FALSIFIED_BY_THIS_TEST", neg39["result"])


if __name__ == "__main__":
    unittest.main()
