# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
SUBJECT-01 — Unit Tests for Rehman 2024 Real Data Scientific Validation & Freeze
Verifies:
1. Protocol timing audit & nadir identification (nominal vs actual lag).
2. Phase-selection kinetics sensitivity & systematic uncertainty separation.
3. Chemical shift & pH calibration audit (partial calibration without fudge factors).
4. Model comparison (M0, M1, M2) in-sample vs within-subject trial transfer (R2 > 0.75).
5. Parameter identifiability matrix & TARGET-CPE45 unvalidated freeze.
6. LOSO prohibition guard on single-participant dataset.
7. Master validation JSON artifact integrity.
"""

import unittest
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CYCLE9_DIR = ROOT / 'research' / 'empirical_recruitment_2026_11_08'
sys.path.insert(0, str(ROOT / 'tools'))

from evaluate_rehman_models import (
    load_extracted_timeseries,
    audit_protocol_timing,
    evaluate_kinetics_sensitivity,
    audit_ph_calibration,
    evaluate_model_comparison,
    analyze_parameter_identifiability,
    run_full_validation,
    VALIDATION_RESULTS_JSON
)
from generate_rehman_report_tables import (
    parse_markdown_timing_table,
    parse_markdown_insample_table,
    parse_markdown_transfer_table,
    verify_structural_consistency
)
from process_rehman_xlsx import LosoProhibitedError, validate_cross_subject_loso_applicability


class TestRehmanModelValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extracted = load_extracted_timeseries()
        cls.timing_audit = audit_protocol_timing(cls.extracted)
        cls.sensitivity = evaluate_kinetics_sensitivity(cls.extracted)
        cls.ph_audit = audit_ph_calibration(cls.extracted)
        cls.model_comp = evaluate_model_comparison(cls.extracted)
        cls.identifiability = analyze_parameter_identifiability()

    def test_extracted_timeseries_structure(self):
        """Verify extracted data has 3 trials and 222 total spectra."""
        trials = self.extracted["trials"]
        self.assertEqual(len(trials), 3)
        total_spectra = sum(t["number_of_spectra"] for t in trials)
        self.assertEqual(total_spectra, 222)
        self.assertEqual(self.extracted["total_spectra_extracted"], 222)

    def test_protocol_timing_audit(self):
        """Stage 1: Verify protocol timing reconstruction, inferred timing, and exact PCr values."""
        self.assertEqual(
            self.timing_audit["status"],
            "PROTOCOL_TIMING_DISCREPANCY_IDENTIFIED"
        )
        self.assertEqual(
            self.timing_audit["timing_synchronization_status"],
            "INFERRED_TIMING_ASSUMPTION"
        )
        trials = self.timing_audit["trials"]
        
        # Trial 1: PCr@90s=1920, Nadir at 144s (PCr=1670, 54s lag)
        t1 = trials[1]
        self.assertEqual(t1["nominal_protocol"]["pcr_at_stop"], 1920.0)
        self.assertEqual(t1["actual_biochemical_nadir"]["nadir_pcr"], 1670.0)
        self.assertEqual(t1["actual_biochemical_nadir"]["nadir_time_s"], 144.0)
        self.assertEqual(t1["actual_biochemical_nadir"]["nadir_spectrum"], 24)
        self.assertEqual(t1["recovery_onset"]["lag_from_nominal_stop_s"], 54.0)
        self.assertAlmostEqual(t1["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 32.70, delta=0.5)
        self.assertLessEqual(t1["actual_biochemical_nadir"]["nadir_vs_published_diff_pct"], 2.0)
        
        # Trial 2: PCr@90s=1291, Nadir at 108s (PCr=1245, 18s lag)
        t2 = trials[2]
        self.assertEqual(t2["nominal_protocol"]["pcr_at_stop"], 1291.0)
        self.assertEqual(t2["actual_biochemical_nadir"]["nadir_pcr"], 1245.0)
        self.assertEqual(t2["actual_biochemical_nadir"]["nadir_time_s"], 108.0)
        self.assertEqual(t2["actual_biochemical_nadir"]["nadir_spectrum"], 18)
        self.assertEqual(t2["recovery_onset"]["lag_from_nominal_stop_s"], 18.0)
        self.assertAlmostEqual(t2["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 25.85, delta=0.5)
        self.assertLessEqual(t2["actual_biochemical_nadir"]["nadir_vs_published_diff_pct"], 2.0)
        
        # Trial 3: PCr@90s=1277, Nadir at 108s (PCr=1231, 18s lag)
        t3 = trials[3]
        self.assertEqual(t3["nominal_protocol"]["pcr_at_stop"], 1277.0)
        self.assertEqual(t3["actual_biochemical_nadir"]["nadir_pcr"], 1231.0)
        self.assertEqual(t3["actual_biochemical_nadir"]["nadir_time_s"], 108.0)
        self.assertEqual(t3["actual_biochemical_nadir"]["nadir_spectrum"], 18)
        self.assertEqual(t3["recovery_onset"]["lag_from_nominal_stop_s"], 18.0)
        self.assertAlmostEqual(t3["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 26.53, delta=0.5)
        self.assertLessEqual(t3["actual_biochemical_nadir"]["nadir_vs_published_diff_pct"], 2.0)

    def test_kinetics_sensitivity(self):
        """Stage 2: Verify kinetics sensitivity to recovery onset shifts and delta_k_sys separation."""
        self.assertEqual(
            self.sensitivity["status"],
            "PHASE_SELECTION_SENSITIVITY_QUANTIFIED"
        )
        trials = self.sensitivity["trials"]
        for tid in [1, 2, 3]:
            t_res = trials[tid]
            evals = t_res["shift_evaluations"]
            self.assertEqual(len(evals), 7)  # -18, -12, -6, 0, 6, 12, 18 s
            
            # Zero-shift (actual nadir) k should closely match published Table 1 within 0.1 min^-1
            zero_shift = next(e for e in evals if e["nominal_shift_s"] == 0)
            pub_k = t_res["published_k_min_minus_1"]
            self.assertAlmostEqual(zero_shift["k_min_minus_1"], pub_k, delta=0.10)
            
            # Pre-nadir shifts (-18s) should underestimate k due to ongoing depletion
            neg_shift = next(e for e in evals if e["nominal_shift_s"] == -18)
            self.assertLess(neg_shift["k_min_minus_1"], zero_shift["k_min_minus_1"])
            
            # Systematic uncertainty should be quantified and positive
            self.assertGreater(t_res["systematic_uncertainty_k_min_minus_1"], 0.0)

    def test_ph_calibration_audit(self):
        """Stage 3: Verify chemical shift & pH calibration audit, partial status, and retracted claim."""
        self.assertEqual(
            self.ph_audit["status"],
            "PH_CALIBRATION_PARTIAL"
        )
        # Offset should be systematically between -0.07 and -0.04 pH units
        mean_offset = self.ph_audit["mean_offset_delta_ph"]
        self.assertGreaterEqual(mean_offset, -0.07)
        self.assertLessEqual(mean_offset, -0.04)
        
        # Verify calculated pH ranges and global minimum (pH >= 6.86 retracted)
        ph_ranges = self.ph_audit["calculated_ph_ranges"]
        self.assertAlmostEqual(ph_ranges["trial_1"][0], 6.7932, places=4)
        self.assertAlmostEqual(ph_ranges["trial_2"][0], 6.8840, places=4)
        self.assertAlmostEqual(ph_ranges["trial_3"][0], 6.8911, places=4)
        self.assertAlmostEqual(ph_ranges["global_min_ph"], 6.7932, places=4)
        self.assertIn("RETRACTED", self.ph_audit["retraction_statement"])
        
        # Ensure physical investigation factors are recorded
        self.assertIn("factor_1_henderson_hasselbalch_pk", self.ph_audit["physical_investigation"])
        self.assertIn("factor_2_jmrui_chemical_shift_referencing", self.ph_audit["physical_investigation"])
        self.assertIn("factor_3_spreadsheet_rounding", self.ph_audit["physical_investigation"])
        self.assertIn("epistemic_ruling", self.ph_audit["physical_investigation"])

    def test_model_comparison_in_sample(self):
        """Stage 4: Verify in-sample model comparison (M0 vs M1 vs M2), negative M0 R2, and M3 status."""
        in_sample = self.model_comp["in_sample_fits"]
        
        # Exact verified RMSE benchmarks from canonical JSON
        expected_rmse = {
            1: {"M0": 230.8789, "M1": 26.0469, "M2": 31.7198},
            2: {"M0": 120.2115, "M1": 15.7271, "M2": 37.6714},
            3: {"M0": 141.6887, "M1": 14.7023, "M2": 32.7989}
        }
        
        for tid in [1, 2, 3]:
            res = in_sample[tid]
            self.assertEqual(res["provenance"], "IN_SAMPLE_FIT_NOT_VALIDATION")
            
            # Null model M0 predicts baseline and has negative R2 relative to recovery slice mean
            self.assertLess(res["M0_null_constant"]["r_squared"], 0.0)
            self.assertAlmostEqual(res["M0_null_constant"]["rmse"], expected_rmse[tid]["M0"], places=3)
            
            # Empirical M1 has high in-sample R2 (> 0.96) and matches exact RMSE
            self.assertGreater(res["M1_monoexponential_3param"]["r_squared"], 0.96)
            self.assertAlmostEqual(res["M1_monoexponential_3param"]["rmse"], expected_rmse[tid]["M1"], places=3)
            
            # M2 is reclassified as CONSTRAINED_MONOEXPONENTIAL_BASELINE
            m2 = res["M2_constrained_monoexponential_baseline"]
            self.assertEqual(m2["model_class"], "CONSTRAINED_MONOEXPONENTIAL_BASELINE")
            self.assertGreater(m2["r_squared"], 0.75)
            self.assertAlmostEqual(m2["rmse"], expected_rmse[tid]["M2"], places=3)
            self.assertLess(m2["rmse"], res["M0_null_constant"]["rmse"])
            
            # M3 is classified as M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS
            m3 = res["M3_full_physiological_ode"]
            self.assertEqual(m3["status"], "M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS")
            self.assertIn("mechanical pedal power (W)", m3["reason"])

    def test_within_subject_trial_transfer_and_scenarios(self):
        """Stage 4: Verify Scenario A (Conditional Reconstruction) and Scenario B (Prospective Prediction Blocked)."""
        scenarios = self.model_comp["transfer_scenarios"]
        
        # Scenario A: Conditional Trajectory Reconstruction (test nadir & baseline known)
        scen_a = scenarios["scenario_A_conditional_trajectory_reconstruction"]
        self.assertEqual(scen_a["status"], "VALIDATED_TECHNICAL_REPRODUCIBILITY")
        self.assertAlmostEqual(scen_a["m2_transfer_r_squared_mean"], 0.8566, places=3)
        self.assertAlmostEqual(scen_a["m1_transfer_r_squared_mean"], 0.8268, places=3)
        self.assertLess(scen_a["m2_transfer_rmse_mean"], 42.0)
        
        # Scenario B: Prospective Prediction (blocked prior to observing nadir)
        scen_b = scenarios["scenario_B_prospective_prediction"]
        self.assertEqual(scen_b["status"], "PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS")
        self.assertEqual(scen_b["forecast_origin_time_s"], 90.0)
        
        # Individual transfers
        transfers = self.model_comp["within_subject_trial_transfers"]
        self.assertEqual(len(transfers), 6)  # (1->2, 1->3, 2->1, 2->3, 3->1, 3->2)
        for tr in transfers:
            self.assertEqual(tr["evaluation_scenario"], "CONDITIONAL_TRAJECTORY_RECONSTRUCTION")
            self.assertGreater(tr["M2_transfer"]["r_squared"], 0.75)
            self.assertGreater(tr["M1_transfer"]["r_squared"], 0.70)

    def test_cross_subject_loso_prohibition(self):
        """Stage 4: Verify cross-subject LOSO on N=1 strictly raises LosoProhibitedError."""
        with self.assertRaises(LosoProhibitedError):
            validate_cross_subject_loso_applicability(1)
        with self.assertRaises(LosoProhibitedError):
            validate_cross_subject_loso_applicability(self.extracted["n_biological_participants"])

    def test_parameter_identifiability_and_freeze(self):
        """Stage 5: Verify identifiability breakdown and preservation of TARGET-CPE45 unvalidated freeze."""
        ident = self.identifiability["identifiable_parameters"]
        unident = self.identifiability["strictly_unidentifiable_parameters"]
        guarantees = self.identifiability["scientific_integrity_guarantees"]
        
        # Identifiable kinetics
        self.assertIn("tau_PCr_rec_s", ident)
        self.assertIn("k_rec_min_minus_1", ident)
        self.assertIn("intra_subject_repeatability_cv_pct", ident)
        self.assertIn("fractional_pcr_depletion", ident)
        
        # Strictly unidentifiable properties
        self.assertIn("PCr_rest_absolute_mM", unident)
        self.assertIn("active_muscle_volume_V_active_L", unident)
        self.assertIn("absolute_ATP_turnover_J_ATP_mol_s", unident)
        self.assertIn("local_actomyosin_efficiency_eta_loc", unident)
        self.assertIn("maximal_oxidative_capacity_Q_max_mM_s", unident)
        self.assertIn("systemic_endurance_TARGET_CPE45", unident)
        
        # Freeze statuses
        self.assertEqual(guarantees["target_cpe45_verdict"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(guarantees["biological_intervention_verdict"], "NO_GO_MAINTAINED")

    def test_master_validation_artifact_exists_and_valid(self):
        """Stage 6: Verify rehman2024_validation_results.json exists and has valid structure."""
        if not VALIDATION_RESULTS_JSON.is_file():
            run_full_validation()
            
        self.assertTrue(VALIDATION_RESULTS_JSON.is_file())
        data = json.loads(VALIDATION_RESULTS_JSON.read_text(encoding='utf-8'))
        
        self.assertIn("stage_1_protocol_timing_audit", data)
        self.assertIn("stage_2_kinetics_sensitivity", data)
        self.assertIn("stage_3_ph_calibration_audit", data)
        self.assertIn("stage_4_model_comparison_and_transfer", data)
        self.assertIn("stage_5_identifiability_and_scientific_integration", data)
        self.assertIn("overall_conclusions", data)
        
        concl = data["overall_conclusions"]
        self.assertEqual(concl["ph_status"], "PH_CALIBRATION_PARTIAL")
        self.assertEqual(concl["target_cpe45_status"], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(concl["biological_intervention_status"], "NO_GO")
        self.assertEqual(concl["m2_reclassification"], "CONSTRAINED_MONOEXPONENTIAL_BASELINE")
        self.assertEqual(concl["m3_status"], "M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS")

    def test_report_markdown_json_consistency(self):
        """
        Automated Structural Consistency Test (Replaces substring assertIn):
        Parses Markdown tables into structured dictionaries by trial_id, metric_id, and model_id,
        and verifies 1:1 mathematical alignment with rehman2024_validation_results.json.
        """
        report_path = CYCLE9_DIR / "REAL_DATA_VALIDATION_REPORT.md"
        self.assertTrue(report_path.is_file(), "REAL_DATA_VALIDATION_REPORT.md must exist")
        text = report_path.read_text(encoding='utf-8')
        
        json_path = VALIDATION_RESULTS_JSON
        self.assertTrue(json_path.is_file(), "Canonical JSON must exist")
        data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # 1. Full structural comparison across all table cells
        errors = verify_structural_consistency(text, data)
        self.assertEqual(errors, [], f"Structural table-to-JSON discrepancies found:\n" + "\n".join(errors))
        
        # 2. Structural parsing and explicit field checks
        timing_table = parse_markdown_timing_table(text)
        insample_table = parse_markdown_insample_table(text)
        transfer_table = parse_markdown_transfer_table(text)
        
        # Check canonical baseline values (mean and SD per trial)
        self.assertAlmostEqual(timing_table[1]["baseline_mean"], 2481.43, places=2)
        self.assertAlmostEqual(timing_table[1]["baseline_sd"], 74.26, places=2)
        self.assertAlmostEqual(timing_table[2]["baseline_mean"], 1679.00, places=2)
        self.assertAlmostEqual(timing_table[2]["baseline_sd"], 38.71, places=2)
        self.assertAlmostEqual(timing_table[3]["baseline_mean"], 1675.57, places=2)
        self.assertAlmostEqual(timing_table[3]["baseline_sd"], 34.21, places=2)
        
        # Check stop and nadir PCr values
        self.assertEqual(timing_table[1]["pcr_stop"], 1920.0)
        self.assertEqual(timing_table[2]["pcr_stop"], 1291.0)
        self.assertEqual(timing_table[3]["pcr_stop"], 1277.0)
        self.assertEqual(timing_table[1]["nadir_pcr"], 1670.0)
        self.assertEqual(timing_table[2]["nadir_pcr"], 1245.0)
        self.assertEqual(timing_table[3]["nadir_pcr"], 1231.0)
        self.assertEqual(timing_table[1]["nadir_time_s"], 144.0)
        self.assertEqual(timing_table[2]["nadir_time_s"], 108.0)
        self.assertEqual(timing_table[3]["nadir_time_s"], 108.0)
        
        # Check in-sample model metrics (M0, M1, M2)
        # M0 (null constant)
        self.assertAlmostEqual(insample_table[1]["M0"]["rmse"], 230.88, places=2)
        self.assertAlmostEqual(insample_table[2]["M0"]["rmse"], 120.21, places=2)
        self.assertAlmostEqual(insample_table[3]["M0"]["rmse"], 141.69, places=2)
        self.assertLess(insample_table[1]["M0"]["r2"], 0.0)
        self.assertLess(insample_table[2]["M0"]["r2"], 0.0)
        self.assertLess(insample_table[3]["M0"]["r2"], 0.0)
        
        # M1 (empirical monoexponential)
        self.assertAlmostEqual(insample_table[1]["M1"]["rmse"], 26.05, places=2)
        self.assertAlmostEqual(insample_table[2]["M1"]["rmse"], 15.73, places=2)
        self.assertAlmostEqual(insample_table[3]["M1"]["rmse"], 14.70, places=2)
        self.assertAlmostEqual(insample_table[1]["M1"]["k"], 1.393, places=3)
        self.assertAlmostEqual(insample_table[2]["M1"]["k"], 1.686, places=3)
        self.assertAlmostEqual(insample_table[3]["M1"]["k"], 1.480, places=3)
        
        # M2 (canonical constrained baseline k and tau)
        self.assertAlmostEqual(insample_table[1]["M2"]["rmse"], 31.72, places=2)
        self.assertAlmostEqual(insample_table[2]["M2"]["rmse"], 37.67, places=2)
        self.assertAlmostEqual(insample_table[3]["M2"]["rmse"], 32.80, places=2)
        self.assertAlmostEqual(insample_table[1]["M2"]["k"], 1.298, places=3)
        self.assertAlmostEqual(insample_table[2]["M2"]["k"], 1.147, places=3)
        self.assertAlmostEqual(insample_table[3]["M2"]["k"], 0.970, places=3)
        self.assertAlmostEqual(insample_table[1]["M2"]["tau"], 46.2, places=1)
        self.assertAlmostEqual(insample_table[2]["M2"]["tau"], 52.3, places=1)
        self.assertAlmostEqual(insample_table[3]["M2"]["tau"], 61.9, places=1)
        
        # Check transfer table pairs
        self.assertIn((1, 2), transfer_table)
        self.assertIn((1, 3), transfer_table)
        self.assertIn((2, 1), transfer_table)
        self.assertIn((2, 3), transfer_table)
        self.assertIn((3, 1), transfer_table)
        self.assertIn((3, 2), transfer_table)
        self.assertAlmostEqual(transfer_table[(1, 2)]["calibrated_k"], 1.298, places=3)
        self.assertAlmostEqual(transfer_table[(2, 1)]["calibrated_k"], 1.147, places=3)
        self.assertAlmostEqual(transfer_table[(3, 1)]["calibrated_k"], 0.970, places=3)
        
        # Check pH audit and governance statuses in text
        self.assertIn("6.7932", text, "Report must record min pH = 6.7932")
        self.assertIn("6.8840", text, "Report must record min pH = 6.8840")
        self.assertIn("6.8911", text, "Report must record min pH = 6.8911")
        self.assertIn("RETRACTED", text, "Report must record formal retraction of pH >= 6.86 throughout")
        self.assertIn("CONSTRAINED_MONOEXPONENTIAL_BASELINE", text)
        self.assertIn("M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS", text)
        self.assertIn("CONDITIONAL_TRAJECTORY_RECONSTRUCTION", text)
        self.assertIn("PROSPECTIVE_PREDICTION_BLOCKED", text)
        self.assertIn("INFERRED_TIMING_ASSUMPTION", text)

    def test_negative_structural_consistency_trial_permutation(self):
        """
        Negative Test 1: Permutation of values between trials.
        Demonstrates that swapping Trial 1 and Trial 2 rows in the Markdown table
        FAILS structural comparison even though all numbers still exist in the document
        (which previously tricked simple substring assertIn checks).
        """
        report_path = CYCLE9_DIR / "REAL_DATA_VALIDATION_REPORT.md"
        text = report_path.read_text(encoding='utf-8')
        data = json.loads(VALIDATION_RESULTS_JSON.read_text(encoding='utf-8'))
        
        # Swap Trial 1 and Trial 2 lines in the Timing Table
        tampered_text = text.replace(
            "| **Trial 1** | $2481.43 \\pm 74.26$",
            "| **Trial 1** | $1679.00 \\pm 38.71$"
        ).replace(
            "| **Trial 2** | $1679.00 \\pm 38.71$",
            "| **Trial 2** | $2481.43 \\pm 74.26$"
        )
        
        # Verify that substring assertIn would PASS on both numbers:
        self.assertIn("2481.43", tampered_text)
        self.assertIn("1679.00", tampered_text)
        
        # BUT structural consistency MUST fail with an explicit mismatch:
        errors = verify_structural_consistency(tampered_text, data)
        self.assertTrue(len(errors) > 0, "Structural verification must fail on permuted trial values")
        self.assertTrue(any("Trial 1 baseline mean" in e for e in errors))

    def test_negative_structural_consistency_unrelated_text_number(self):
        """
        Negative Test 2: Placing correct number in unrelated text while table has corrupted value.
        Demonstrates that changing a table cell (Trial 1 nadir PCr = 9999) while placing
        '1670' elsewhere in prose FAILS structural check (catching table corruption).
        """
        report_path = CYCLE9_DIR / "REAL_DATA_VALIDATION_REPORT.md"
        text = report_path.read_text(encoding='utf-8')
        data = json.loads(VALIDATION_RESULTS_JSON.read_text(encoding='utf-8'))
        
        # Corrupt table cell in Trial 1 nadir PCr, but add '1670' to a comment paragraph
        tampered_text = text.replace(
            "| **$144.0\\text{ s}$** (Spec 24) | **$1670$** |",
            "| **$144.0\\text{ s}$** (Spec 24) | **$9999$** |"
        ) + "\n\nUnrelated paragraph preserving number 1670 in prose."
        
        # Substring assertIn passes:
        self.assertIn("1670", tampered_text)
        
        # Structural verification fails:
        errors = verify_structural_consistency(tampered_text, data)
        self.assertTrue(len(errors) > 0, "Structural verification must fail on corrupted table cell")
        self.assertTrue(any("Trial 1 nadir PCr" in e for e in errors))

    def test_negative_structural_consistency_metric_swap(self):
        """
        Negative Test 3: Swapping M1 RMSE and M2 RMSE in In-Sample table.
        Demonstrates that column confusion within the same trial FAILS structural check.
        """
        report_path = CYCLE9_DIR / "REAL_DATA_VALIDATION_REPORT.md"
        text = report_path.read_text(encoding='utf-8')
        data = json.loads(VALIDATION_RESULTS_JSON.read_text(encoding='utf-8'))
        
        # Swap M1 RMSE (26.05) and M2 RMSE (31.72) in Trial 1 row
        tampered_text = text.replace(
            "| **$26.05$** | $21.34$ | **$0.9802$** | $1.3932$ | $43.1$ | **$31.72$** |",
            "| **$31.72$** | $21.34$ | **$0.9802$** | $1.3932$ | $43.1$ | **$26.05$** |"
        )
        
        errors = verify_structural_consistency(tampered_text, data)
        self.assertTrue(len(errors) > 0, "Structural verification must fail on swapped metric columns")
        self.assertTrue(any("M1 RMSE" in e or "M2 RMSE" in e for e in errors))


if __name__ == '__main__':
    unittest.main()
