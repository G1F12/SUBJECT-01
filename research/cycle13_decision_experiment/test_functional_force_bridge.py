"""
Unit Tests for Functional Biomechanical Multi-Muscle Bridge (EXP-0046)
"""

import os
import unittest
import numpy as np
from research.cycle13_decision_experiment.functional_force_bridge import FunctionalForceBridge


class TestFunctionalForceBridge(unittest.TestCase):
    def setUp(self):
        self.engine = FunctionalForceBridge()

    def test_cryptographic_verification(self):
        """Test that the raw dynamic knee dataset matches expected SHA-256."""
        self.assertTrue(self.engine.verify_cryptographic_digest())

    def test_data_loading_dimensions_and_invariants(self):
        """Test loaded array integrity, length, and protocol partition."""
        data = self.engine.load_data()
        self.assertEqual(len(data["torque"]), 3226)
        self.assertEqual(len(data["subject_id"]), 3226)
        self.assertEqual(len(data["angle"]), 3226)
        self.assertEqual(len(data["velocity"]), 3226)
        
        # Check subjects count is exactly 6
        unique_subs = np.unique(data["subject_id"])
        self.assertEqual(len(unique_subs), 6)
        np.testing.assert_array_equal(unique_subs, np.arange(6))
        
        # Check active / passive partition
        n_passive = np.sum(data["is_passive"])
        n_active = np.sum(data["is_active"])
        self.assertEqual(n_passive, 1382)
        self.assertEqual(n_active, 1844)
        self.assertEqual(n_passive + n_active, 3226)

    def test_contractile_state_bounds(self):
        """Test that contractile state is non-negative and finite."""
        data = self.engine.load_data()
        q = self.engine.compute_contractile_state(
            data["semg"], data["fascicle_length"], data["velocity"], data["pennation_angle"]
        )
        self.assertEqual(len(q), 3226)
        self.assertTrue(np.all(np.isfinite(q)))
        self.assertTrue(np.all(q >= -0.05)) # allow negligible numerical epsilon

    def test_loso_cross_validation_zero_leakage(self):
        """Test that LOSO cross-validation executes on all 6 folds and returns valid metrics."""
        res = self.engine.evaluate_loso_cross_validation(condition="all")
        self.assertEqual(res["held_out_subjects_count"], 6)
        models = res["models_summary"]
        
        # Check required models are present
        for m in ["M0_Mean", "M1_sEMG", "M3_Hill", "M4_Hill_Composite", "M_Bridge_CoActivation"]:
            self.assertIn(m, models)
            self.assertEqual(len(models[m]["fold_r2_values"]), 6)
            self.assertTrue(np.isfinite(models[m]["pooled_r2"]))
            self.assertTrue(np.isfinite(models[m]["pooled_rmse"]))
            
        # Verify M1 sEMG matches known benchmark
        self.assertAlmostEqual(models["M1_sEMG"]["mean_fold_r2"], 0.4628, places=2)

    def test_augmentation_simulation_physics(self):
        """Test augmentation scenarios and physical invariants."""
        sim = self.engine.simulate_augmentation_and_tendon_stress()
        
        # Nominal sanity
        self.assertIn("nominal", sim)
        self.assertAlmostEqual(sim["nominal"]["net_torque_gain_percent"], 0.0, places=1)
        self.assertTrue(sim["nominal"]["safety_threshold_met"])
        
        # Isolated muscle test: +20% fiber force gives +18.3% net torque (efficiency < 1.0 due to pennation penalty)
        sc1 = sim["TARGET_FORCE20_isolated_muscle"]
        self.assertAlmostEqual(sc1["net_torque_gain_percent"], 18.3, places=1)
        self.assertAlmostEqual(sc1["torque_transmission_efficiency"], 0.917, places=2)
        self.assertTrue(sc1["tendon_stress_MPa"] > sim["nominal"]["tendon_stress_MPa"])
        self.assertTrue(sc1["safety_factor"] < sim["nominal"]["safety_factor"])
        
        # Synergistic control test: antagonist suppression yields >20% net torque
        sc3 = sim["TARGET_FORCE20_synergistic_control"]
        self.assertTrue(sc3["net_torque_gain_percent"] > 20.0)
        self.assertTrue(sc3["torque_transmission_efficiency"] > 1.0)


if __name__ == "__main__":
    unittest.main()
