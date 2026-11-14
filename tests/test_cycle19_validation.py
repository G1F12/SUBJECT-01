#!/usr/bin/env python3
"""
Unit tests for Cycle 19: Human Functional Strength Limits & Tendon Fatigue Mechanics.
"""
import unittest
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

class TestCycle19Validation(unittest.TestCase):
    def setUp(self):
        self.c19_dir = ROOT / "research/cycle19"
        self.exp59_json = self.c19_dir / "EXP0059/RESULTS.json"
        self.exp60_json = self.c19_dir / "EXP0060/RESULTS.json"
        
    def test_cycle19_files_exist(self):
        required_files = [
            self.c19_dir / "SCIENTIFIC_CORRECTION.md",
            self.c19_dir / "DATASET_SEARCH_AND_SELECTION.md",
            self.c19_dir / "DATASET_PROVENANCE.json",
            self.c19_dir / "EXP0059/PREREGISTRATION.md",
            self.c19_dir / "EXP0059/DATA_AUDIT.md",
            self.c19_dir / "EXP0059/MODEL_SPECIFICATION.md",
            self.c19_dir / "EXP0059/EXPERIMENT_REPORT_RU.md",
            self.c19_dir / "EXP0060/PREREGISTRATION.md",
            self.c19_dir / "EXP0060/DATA_AUDIT.md",
            self.c19_dir / "EXP0060/FATIGUE_MODELS.md",
            self.c19_dir / "EXP0060/EXPERIMENT_REPORT_RU.md",
            self.c19_dir / "INTEGRATED_MECHANICAL_LIMITS.md",
            self.c19_dir / "scripts/run_exp0059_muscle_models.py",
            self.c19_dir / "scripts/run_exp0060_tendon_fatigue.py",
        ]
        for f in required_files:
            self.assertTrue(f.is_file(), f"Missing required file: {f}")

    def test_exp0059_results(self):
        self.assertTrue(self.exp59_json.is_file(), "Missing EXP0059 RESULTS.json")
        data = json.loads(self.exp59_json.read_text('utf-8'))
        
        # Verify specific tension range (human physiological bounds 20-32 N/cm2)
        sigma_mean = data['specific_tension_empirical_distribution']['mean_n_cm2']
        self.assertGreaterEqual(sigma_mean, 20.0)
        self.assertLessEqual(sigma_mean, 32.0)
        
        # Verify M1 model predictive performance
        m1_r2 = data['model_comparison_loso']['M1_anthropometry_angle']['pooled_r2']
        self.assertGreater(m1_r2, 0.60)
        
        # Verify M2 biomechanical model parity
        m2_r2 = data['model_comparison_loso']['M2_biomechanical_pcsa']['pooled_r2']
        self.assertGreater(m2_r2, 0.60)
        
        # Verify isomass feasible
        self.assertTrue(data['isomass_scaling_analysis']['scenario_3_combined_isomass_gain']['isomass_plus20_model_feasible'])

    def test_exp0060_results(self):
        self.assertTrue(self.exp60_json.is_file(), "Missing EXP0060 RESULTS.json")
        data = json.loads(self.exp60_json.read_text('utf-8'))
        
        # Verify S1 unadapted stress
        s1 = data['scenarios_evaluation']['S1_actual_plus20_transmitted_force_fixed_geometry']
        self.assertAlmostEqual(s1['proximal_stress_base_mpa'], 38.46, places=1)
        self.assertAlmostEqual(s1['proximal_stress_plus20_mpa'], 46.15, places=1)
        
        # Verify fatigue loss is significant (>65%)
        self.assertGreater(s1['fatigue_life_loss_pct'], 65.0)
        
        # Verify S2 Case 2C adaptation restores parity
        s2 = data['scenarios_evaluation']['S2_actual_plus20_force_with_adaptive_compensation']
        case_2c = s2['case_2c_realistic_combined_training_adaptation']
        self.assertGreaterEqual(case_2c['retention_ratio_vs_base'], 1.0)

if __name__ == '__main__':
    unittest.main()
