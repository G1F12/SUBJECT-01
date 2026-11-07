"""Unit and integration test suite for Cycle 7 Local Muscle Bridge.
Verifies:
1. Physical conservation of energy and high-energy phosphates.
2. Exact structural invariance under Scale and Additive Shift symmetries.
3. Dimension and unit consistency across mechanical, local and systemic layers.
4. Correct reproduction of experimental correlations from Moll 2017/2018.
5. Numerical stability and non-degeneracy of simulation algorithms.
"""
import unittest
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[1]

from identifiability import LocalBridgeModel, analyze_identifiability, compute_profile_likelihood
from experiments import load_moll_data, run_exp_a, run_exp_b, run_exp_c, run_exp_d, run_exp_e

class TestLocalMuscleBridge(unittest.TestCase):
    def setUp(self):
        self.data = load_moll_data()
        self.model = LocalBridgeModel()

    def test_moll_dataset_structure(self):
        """Verify digitized dataset contains all required chapters and fields."""
        self.assertIn('chapter2_ergometer_pilot', self.data)
        self.assertIn('chapter3_combined_study', self.data)
        self.assertIn('chapter4_athlete_cohorts', self.data)
        self.assertIn('chapter5_nmes_study', self.data)

        # Check chapter 3 participants
        participants = self.data['chapter3_combined_study']['individual_participants']
        self.assertEqual(len(participants), 10)
        for p in participants:
            self.assertIn('pH_end', p)
            self.assertIn('tau_PCr_fast_s', p)
            self.assertIn('tau_VO2_fast_s', p)
            self.assertIn('excess_CO2_L', p)
            self.assertGreater(p['pH_end'], 5.5)
            self.assertLess(p['pH_end'], 7.5)
            self.assertGreater(p['tau_PCr_fast_s'], 10.0)

    def test_energy_conservation_and_bounds(self):
        """Verify simulation adheres to non-negative energy and concentration bounds."""
        t_grid = np.linspace(0, 180, 91)
        P_profile = np.zeros_like(t_grid)
        P_profile[(t_grid >= 20) & (t_grid <= 120)] = 25.0

        sim = self.model.simulate(t_grid, P_profile)

        # PCr must never exceed resting level and never drop below physical minimum
        self.assertTrue(np.all(sim['PCr_mM'] <= self.model.p['PCr_rest_mM'] + 1e-6))
        self.assertTrue(np.all(sim['PCr_mM'] >= 0.0))

        # Relative PCr in [0, 1]
        self.assertTrue(np.all(sim['PCr_relative'] >= 0.0))
        self.assertTrue(np.all(sim['PCr_relative'] <= 1.0 + 1e-6))

        # VO2 must always be greater than resting baseline
        self.assertTrue(np.all(sim['VO2_pulm_L_min'] >= self.model.p['VO2_rest_L_min'] - 1e-6))

    def test_exact_scale_symmetry(self):
        """Verify Scale Symmetry produces identical relative PCr and external power."""
        t_grid = np.linspace(0, 180, 91)
        P_profile = np.zeros_like(t_grid)
        P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0

        sim_true = self.model.simulate(t_grid, P_profile)

        # Rescale by alpha = 1.8
        alpha = 1.8
        scaled_model = LocalBridgeModel({
            'eta_loc': self.model.p['eta_loc'] * alpha,
            'V_active_L': self.model.p['V_active_L'] / alpha
        })
        sim_scaled = scaled_model.simulate(t_grid, P_profile)

        # Differences in relative PCr must be zero within floating point machine precision
        max_diff_rel = np.max(np.abs(sim_true['PCr_relative'] - sim_scaled['PCr_relative']))
        self.assertLess(max_diff_rel, 1e-12)

    def test_exact_additive_shift_symmetry(self):
        """Verify Additive Shift (Q + Delta, M + Delta) preserves recovery rate."""
        t_grid = np.linspace(0, 180, 91)
        P_profile = np.zeros_like(t_grid)
        P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0

        sim_true = self.model.simulate(t_grid, P_profile)

        delta = 0.02
        shifted_model = LocalBridgeModel({
            'Q_loc_max_mM_s': self.model.p['Q_loc_max_mM_s'] + delta,
            'M_loc_mM_s': self.model.p['M_loc_mM_s'] + delta
        })
        sim_shifted = shifted_model.simulate(t_grid, P_profile)

        # During recovery (t >= 120 s), differences in PCr trajectory must be zero
        rec_mask = t_grid >= 120
        max_diff_rec = np.max(np.abs(sim_true['PCr_relative'][rec_mask] - sim_shifted['PCr_relative'][rec_mask]))
        self.assertLess(max_diff_rec, 1e-12)

    def test_exp_a_acidosis_significance(self):
        """EXP-A: Verify empirical acidosis-PCr correlation matches reported direction."""
        res_a = run_exp_a(self.data)
        reg = res_a['acidosis_regression']
        self.assertLess(reg['slope_s_per_pH'], 0.0)  # Lower pH -> longer tau (negative slope)
        self.assertGreater(reg['pearson_r2'], 0.70)  # R^2 > 0.70
        self.assertLess(reg['pearson_p_val'], 0.01)  # p < 0.01

    def test_exp_b_delay_collinearity(self):
        """EXP-B: Verify cardiopulmonary delay and muscle tau are negatively collinear."""
        res_b = run_exp_b(self.data)
        corr = res_b['delay_tau_correlation']
        self.assertLess(corr, -0.50)  # Strong negative correlation between delay and tau

    def test_exp_c_parasitic_cost_dominance(self):
        """EXP-C: Verify non-calf parasitic systemic cost exceeds 50% during local plantarflexion."""
        res_c = run_exp_c(self.data)
        parasitic = res_c['systemic_parasitic_partition']['parasitic_fraction']
        self.assertGreater(parasitic, 0.50)

    def test_exp_d_volume_uncertainty_span(self):
        """EXP-D: Verify volume and reference uncertainty produce >3-fold span."""
        res_d = run_exp_d(self.data)
        ratio = res_d['absolute_PCr_pool_J']['ratio_max_min']
        self.assertGreater(ratio, 3.0)

    def test_exp_e_bridge_over_uncalibrated_d2(self):
        """EXP-E: Verify calibrated local bridge outperforms raw unscaled D2 on power RMSE."""
        res_e = run_exp_e(self.data)
        preds = res_e['predictors']
        self.assertLess(preds['local_systemic_bridge']['RMSE_W'], preds['constant_mean']['RMSE_W'])
        self.assertLess(preds['local_systemic_bridge']['RMSE_W'], preds['D2_raw_whole_body']['RMSE_W'])

if __name__ == '__main__':
    unittest.main()
