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
        """Stage 1: Verify protocol timing reconstruction and discrepancy detection."""
        self.assertEqual(
            self.timing_audit["status"],
            "PROTOCOL_TIMING_DISCREPANCY_IDENTIFIED"
        )
        trials = self.timing_audit["trials"]
        
        # Trial 1: Nadir at 144s (extended depletion / 54s lag)
        t1 = trials[1]
        self.assertEqual(t1["actual_biochemical_nadir"]["nadir_time_s"], 144.0)
        self.assertEqual(t1["actual_biochemical_nadir"]["nadir_spectrum"], 24)
        self.assertEqual(t1["recovery_onset"]["lag_from_nominal_stop_s"], 54.0)
        self.assertAlmostEqual(t1["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 32.7, delta=1.5)
        self.assertLessEqual(t1["actual_biochemical_nadir"]["nadir_vs_published_diff_pct"], 2.0)
        
        # Trial 2: Nadir at 108s (18s lag)
        t2 = trials[2]
        self.assertEqual(t2["actual_biochemical_nadir"]["nadir_time_s"], 108.0)
        self.assertEqual(t2["actual_biochemical_nadir"]["nadir_spectrum"], 18)
        self.assertEqual(t2["recovery_onset"]["lag_from_nominal_stop_s"], 18.0)
        self.assertAlmostEqual(t2["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 25.8, delta=1.5)
        self.assertLessEqual(t2["actual_biochemical_nadir"]["nadir_vs_published_diff_pct"], 2.0)
        
        # Trial 3: Nadir at 108s (18s lag)
        t3 = trials[3]
        self.assertEqual(t3["actual_biochemical_nadir"]["nadir_time_s"], 108.0)
        self.assertEqual(t3["actual_biochemical_nadir"]["nadir_spectrum"], 18)
        self.assertEqual(t3["recovery_onset"]["lag_from_nominal_stop_s"], 18.0)
        self.assertAlmostEqual(t3["actual_biochemical_nadir"]["pcr_drop_at_nadir_pct"], 26.5, delta=2.0)
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
        """Stage 3: Verify chemical shift & pH calibration audit and partial status."""
        self.assertEqual(
            self.ph_audit["status"],
            "PH_CALIBRATION_PARTIAL"
        )
        # Offset should be systematically between -0.07 and -0.04 pH units
        mean_offset = self.ph_audit["mean_offset_delta_ph"]
        self.assertGreaterEqual(mean_offset, -0.07)
        self.assertLessEqual(mean_offset, -0.04)
        
        # Ensure physical investigation factors are recorded
        self.assertIn("factor_1_henderson_hasselbalch_pk", self.ph_audit["physical_investigation"])
        self.assertIn("factor_2_jmrui_chemical_shift_referencing", self.ph_audit["physical_investigation"])
        self.assertIn("factor_3_spreadsheet_rounding", self.ph_audit["physical_investigation"])
        self.assertIn("epistemic_ruling", self.ph_audit["physical_investigation"])

    def test_model_comparison_in_sample(self):
        """Stage 4: Verify in-sample model comparison (M0 vs M1 vs M2)."""
        in_sample = self.model_comp["in_sample_fits"]
        for tid in [1, 2, 3]:
            res = in_sample[tid]
            self.assertEqual(res["provenance"], "IN_SAMPLE_FIT_NOT_VALIDATION")
            
            # Null model M0 has R2 = 0.0 (by definition of baseline residual variance)
            self.assertLessEqual(res["M0_null_constant"]["r_squared"], 0.05)
            
            # Empirical M1 has high in-sample R2 (> 0.95)
            self.assertGreater(res["M1_monoexponential_3param"]["r_squared"], 0.95)
            
            # Physiological M2 has R2 > 0.75
            self.assertGreater(res["M2_physiological_ode_model"]["r_squared"], 0.75)
            self.assertLess(res["M2_physiological_ode_model"]["rmse"], res["M0_null_constant"]["rmse"])

    def test_within_subject_trial_transfer(self):
        """Stage 4: Verify all 6 within-subject trial transfer pairs achieve R2 > 0.75."""
        transfers = self.model_comp["within_subject_trial_transfers"]
        self.assertEqual(len(transfers), 6)  # (1->2, 1->3, 2->1, 2->3, 3->1, 3->2)
        
        r2_values = []
        for tr in transfers:
            self.assertEqual(tr["evaluation_mode"], "WITHIN_SUBJECT_TRIAL_TRANSFER")
            m2_r2 = tr["M2_transfer"]["r_squared"]
            self.assertGreater(m2_r2, 0.75)
            r2_values.append(m2_r2)
            
        mean_r2 = sum(r2_values) / len(r2_values)
        self.assertGreater(mean_r2, 0.80)

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


if __name__ == '__main__':
    unittest.main()
