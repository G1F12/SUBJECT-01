#!/usr/bin/env python3
"""
Unit tests for Comprehensive Functional Augmentation Research:
Independent Scientific Revalidation, Human Strength Optimization & Tendon Mechanical Limits.
"""
import unittest
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestFunctionalMechanicsValidation(unittest.TestCase):
    def setUp(self):
        self.val_dir = ROOT / "research/functional_mechanics_validation"
        self.results_json = self.val_dir / "RESULTS.json"
        
    def test_required_artifacts_exist(self):
        required_files = [
            self.val_dir / "DATA_PROVENANCE.md",
            self.val_dir / "SCIENTIFIC_CORRECTIONS.md",
            self.val_dir / "MUSCLE_STRENGTH_VALIDATION.md",
            self.val_dir / "TENDON_FATIGUE_VALIDATION.md",
            self.val_dir / "INTEGRATED_FUNCTIONAL_MODEL.md",
            self.val_dir / "UNCERTAINTY_AND_SENSITIVITY.md",
            self.val_dir / "INDEPENDENT_VERIFICATION.md",
            self.val_dir / "SCIENTIFIC_NOVELTY.md",
            self.val_dir / "FUNCTIONAL_IMPACT.md",
            self.val_dir / "FINAL_SCIENTIFIC_REPORT_RU.md",
            self.val_dir / "RESULTS.json",
            self.val_dir / "MUSCLE_AUDIT_RESULTS.json",
            self.val_dir / "TENDON_AUDIT_RESULTS.json",
            self.val_dir / "INTEGRATED_MODEL_RESULTS.json",
            self.val_dir / "scripts/audit_and_recalculate_muscle.py",
            self.val_dir / "scripts/audit_and_recalculate_tendon.py",
            self.val_dir / "scripts/integrated_functional_model.py",
            self.val_dir / "scripts/run_independent_verification.py",
        ]
        for f in required_files:
            self.assertTrue(f.is_file(), f"Missing required file: {f}")

    def test_independent_verification_script(self):
        verifier_script = self.val_dir / "scripts/run_independent_verification.py"
        res = subprocess.run([sys.executable, str(verifier_script)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Verifier failed: {res.stdout} {res.stderr}")
        self.assertIn("ALL INDEPENDENT VERIFICATION CHECKS PASSED", res.stdout)

    def test_muscle_audit_results(self):
        self.assertTrue(self.results_json.is_file(), "Missing RESULTS.json")
        data = json.loads(self.results_json.read_text('utf-8'))
        m = data['muscle_audit']
        
        # Corrected specific tension should be 26.41 N/cm2
        sig_corrected = m['specific_tension_evaluations']['corrected_convA_single_cosine']['mean_n_cm2']
        self.assertAlmostEqual(sig_corrected, 26.41, places=1)
        
        # M2 strict model R2 should be >= 0.68
        m2_r2 = m['predictive_models_loso']['M2_biomechanical_pcsa_strict']['pooled_r2']
        self.assertGreater(m2_r2, 0.68)
        
        # Isomass power penalty should be negative (-1.98%)
        pmax_change = m['isomass_scaling_and_tradeoffs']['scenario_18deg_summary']['peak_mechanical_power_change_pct']
        self.assertAlmostEqual(pmax_change, -1.98, places=1)

    def test_tendon_audit_results(self):
        data = json.loads(self.results_json.read_text('utf-8'))
        t = data['tendon_audit']
        
        # Case 2C adapted stress must be 40.13 MPa (NOT 34.78 MPa)
        case_2c_stress = t['stress_and_hypertrophy_forensic_correction']['case_2c_corrected_stress_mpa']
        self.assertAlmostEqual(case_2c_stress, 40.13, places=1)
        
        # Retention ratio in Case 2C must be >= 1.50x
        ret_c = t['stress_and_hypertrophy_forensic_correction']['case_2c_retention_ratio_vs_base']
        self.assertGreaterEqual(ret_c, 1.50)
        
        # Semi-log loss must be 86.67%
        loss_semi = t['fatigue_laws_reconciliation']['semi_log_basquin_model']['loss_pct']
        self.assertAlmostEqual(loss_semi, 86.67, places=1)

    def test_integrated_model_results(self):
        data = json.loads(self.results_json.read_text('utf-8'))
        i = data['integrated_model']
        
        # Strategy 2 should achieve >= 20% torque and positive power gain
        s2 = i['deterministic_scenarios']['strategy_2_coordinated_biological_enhancement']
        self.assertGreaterEqual(s2['torque_gain_pct'], 20.0)
        self.assertGreater(s2['peak_power_change_pct'], 15.0)
        self.assertGreaterEqual(s2['fatigue_life_retention_ratio'], 1.0)

if __name__ == '__main__':
    unittest.main()
