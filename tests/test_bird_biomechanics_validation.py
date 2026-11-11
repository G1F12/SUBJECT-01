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
        # Rule: No unacquired file shall be marked VERIFIED
        for fname, fmeta in files_audit.items():
            if fname != "arxiv_2510_20866.pdf":
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
        self.assertEqual(status["SUBJECT01_INDEPENDENT_REPRODUCTION"]["status"], "BLOCKED_PENDING_RAW_DATA_ARRAYS")
        self.assertEqual(status["SUBJECT01_NEW_MODEL_FIT"]["status"], "NOT_FIT_ON_RAW_ARRAYS")
        self.assertEqual(status["SUBJECT01_HELD_OUT_PREDICTION"]["status"], "NOT_EXECUTED_ON_RAW_OBSERVATIONS")

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


if __name__ == "__main__":
    unittest.main()
