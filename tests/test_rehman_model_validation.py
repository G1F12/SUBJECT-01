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
        """Automated Corrigendum Test: Verifies that REAL_DATA_VALIDATION_REPORT.md matches canonical JSON."""
        report_path = CYCLE9_DIR / "REAL_DATA_VALIDATION_REPORT.md"
        self.assertTrue(report_path.is_file(), "REAL_DATA_VALIDATION_REPORT.md must exist")
        text = report_path.read_text(encoding='utf-8')
        
        # 1. Verified PCr values at 90s (1920, 1291, 1277)
        self.assertIn("1920", text, "Report must record Trial 1 PCr@90s = 1920")
        self.assertIn("1291", text, "Report must record Trial 2 PCr@90s = 1291")
        self.assertIn("1277", text, "Report must record Trial 3 PCr@90s = 1277")
        
        # 2. Verified PCr values at nadir (1670, 1245, 1231)
        self.assertIn("1670", text, "Report must record Trial 1 Nadir PCr = 1670")
        self.assertIn("1245", text, "Report must record Trial 2 Nadir PCr = 1245")
        self.assertIn("1231", text, "Report must record Trial 3 Nadir PCr = 1231")
        
        # 3. Verified in-sample RMSEs
        self.assertIn("230.88", text, "Report must record M0 T1 RMSE = 230.88")
        self.assertIn("120.21", text, "Report must record M0 T2 RMSE = 120.21")
        self.assertIn("141.69", text, "Report must record M0 T3 RMSE = 141.69")
        self.assertIn("26.05", text, "Report must record M1 T1 RMSE = 26.05")
        self.assertIn("15.73", text, "Report must record M1 T2 RMSE = 15.73")
        self.assertIn("14.70", text, "Report must record M1 T3 RMSE = 14.70")
        self.assertIn("31.72", text, "Report must record M2 T1 RMSE = 31.72")
        self.assertIn("37.67", text, "Report must record M2 T2 RMSE = 37.67")
        self.assertIn("32.80", text, "Report must record M2 T3 RMSE = 32.80")
        
        # 4. M0 R2 is negative (not 0.000)
        self.assertIn("-0.553", text, "Report must record negative M0 T1 R2")
        self.assertIn("-1.130", text, "Report must record negative M0 T2 R2")
        self.assertIn("-0.962", text, "Report must record negative M0 T3 R2")
        
        # 5. Verified minimum pH and retracted statement
        self.assertIn("6.7932", text, "Report must record min pH = 6.7932")
        self.assertIn("6.8840", text, "Report must record min pH = 6.8840")
        self.assertIn("6.8911", text, "Report must record min pH = 6.8911")
        self.assertIn("RETRACTED", text, "Report must record formal retraction of pH >= 6.86 throughout")
        
        # 6. M2 reclassification and M3 status
        self.assertIn("CONSTRAINED_MONOEXPONENTIAL_BASELINE", text)
        self.assertIn("M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS", text)
        
        # 7. Scenarios: Conditional reconstruction vs Prospective prediction
        self.assertIn("CONDITIONAL_TRAJECTORY_RECONSTRUCTION", text)
        self.assertIn("PROSPECTIVE_PREDICTION_BLOCKED", text)
        self.assertIn("INFERRED_TIMING_ASSUMPTION", text)


if __name__ == '__main__':
    unittest.main()
