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
