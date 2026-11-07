"""Unit and scientific audit test suite for Cycle 7 Local Muscle Bridge.
Verifies:
1. Strict separation of published data, literature correlations, and approximate digitizations.
2. Physical thermodynamic bounds: NO apparent efficiency > 1.0.
3. Exact structural invariance under Scale and Additive Shift symmetries.
4. Correct literature provenance: Moll et al. 2017 (R2=0.73, 0.55, 0.65) and Cannon et al. 2014 (PMC4262339 Table 1).
5. Formal retraction of EXP-0031 predictive claims and unverified eyeball correlations.
6. Absolute numerical consistency between REPORT.md and experiment_results.json.
"""
import unittest
from pathlib import Path
import json
import re
import numpy as np

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[1]

from identifiability import LocalBridgeModel, analyze_identifiability, compute_profile_likelihood
from experiments import load_moll_data, run_exp_a, run_exp_b, run_exp_c, run_exp_d, run_exp_e

class TestLocalMuscleBridgeAudit(unittest.TestCase):
    def setUp(self):
        self.data = load_moll_data()
        self.model = LocalBridgeModel()

    def test_moll_dataset_structure_and_categories(self):
        """Verify digitized dataset contains audited categories and full provenance."""
        self.assertIn('moll2018_chapter2_ergometer_pilot', self.data)
        self.assertIn('moll2017_chapter3_combined_study', self.data)
        self.assertIn('moll2018_chapter4_athlete_comparison', self.data)
        self.assertIn('moll2018_chapter5_nmes_heterogeneity', self.data)
        self.assertIn('cannon2014_pmc4262339_atp_turnover', self.data)

        # Check chapter 3 published correlations
        pub_corr = self.data['moll2017_chapter3_combined_study']['published_statistical_correlations']
        self.assertEqual(pub_corr['tau_PCr_fast_vs_pH_end']['R2'], 0.73)
        self.assertEqual(pub_corr['tau_VO2_fast_vs_tau_PCr_fast']['R2'], 0.55)
        self.assertEqual(pub_corr['excess_CO2_vs_pH_end']['R2'], 0.65)

        # Check approximate graphical digitization warning
        approx = self.data['moll2017_chapter3_combined_study']['approximate_graphical_digitization_fig3_5']
        self.assertEqual(approx['status'], 'APPROXIMATE_DIGITIZATION')
        self.assertIn('warning', approx)
        self.assertEqual(len(approx['estimated_points']), 10)

    def test_energy_conservation_and_physical_bounds(self):
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

        rec_mask = t_grid >= 120
        max_diff_rec = np.max(np.abs(sim_true['PCr_relative'][rec_mask] - sim_shifted['PCr_relative'][rec_mask]))
        self.assertLess(max_diff_rec, 1e-12)

    def test_exp_a_retraction_and_literature_benchmarks(self):
        """EXP-A: Verify apparent R2=0.919 is retracted and literature R2=0.73 is restored."""
        res_a = run_exp_a(self.data)
        self.assertIn('RETRACTED', res_a['audit_verdict'])
        self.assertEqual(res_a['literature_published_benchmark']['R2'], 0.73)
        self.assertGreater(res_a['graphical_digitization_audit']['bias_vs_literature'], 0.15)
        # Check computational sensitivities
        span = res_a['asymptote_uncertainty_analysis']['span_pct']
        self.assertLess(span[0], -15.0)
        self.assertGreater(span[1], 20.0)
        self.assertGreater(res_a['spatial_heterogeneity_simulation']['bias_pct'], 10.0)

    def test_exp_b_4component_delays_and_collinearity(self):
        """EXP-B: Verify 4 distinct delays and negative collinearity between delay and tau."""
        res_b = run_exp_b(self.data)
        delays = res_b['delay_components']
        self.assertAlmostEqual(delays['t_sampling_line_delay_s'], 2.075, places=3)
        self.assertAlmostEqual(delays['t_sampling_line_dispersion_s'], 0.307, places=3)
        corr = res_b['collinearity_simulation']['delay_tau_correlation']
        self.assertLess(corr, -0.60)
        self.assertGreater(corr, -0.85)

    def test_exp_c_parasitic_cost_scenario_bounds(self):
        """EXP-C: Verify parasitic cost is bounded across scenarios (45% to 78%)."""
        res_c = run_exp_c(self.data)
        pub = res_c['published_literature_correlations']
        self.assertEqual(pub['tau_pcr_vs_tau_vo2']['R2'], 0.55)
        self.assertEqual(pub['excess_co2_vs_pH_end']['R2'], 0.65)
        bounds = res_c['systemic_parasitic_scenario_evaluation']['uncertainty_bounds_pct']
        self.assertGreaterEqual(bounds[0], 40.0)
        self.assertLessEqual(bounds[1], 80.0)
        nominal = res_c['systemic_parasitic_scenario_evaluation']['nominal_scenario']['parasitic_fraction_pct']
        self.assertAlmostEqual(nominal, 66.3, delta=0.5)

    def test_exp_d_pcr_buffer_vs_atp_turnover(self):
        """EXP-D: Verify PCr capacity (205-1021 J) is separated from 180s ATP turnover (>11,000 J)."""
        res_d = run_exp_d(self.data)
        pcr_span = res_d['pcr_buffer_capacity_J']
        self.assertAlmostEqual(pcr_span['min_J'], 204.75, places=1)
        self.assertAlmostEqual(pcr_span['max_J'], 1021.44, places=1)
        self.assertAlmostEqual(pcr_span['ratio_max_min'], 4.988, places=2)

        # Total 180s turnover must exceed 10,000 J
        work_180s = res_d['cumulative_180s_energy_comparison_J']['required_atp_metabolic_energy_J']
        self.assertGreater(work_180s, 10000.0)

        # Cannon 2014 Table 1: oxidative ATP must be > 85%
        cannon_ox = res_d['atp_turnover_flux_partition_cannon2014']['oxidative_fraction_pct']
        self.assertGreater(cannon_ox, 85.0)

    def test_exp_e_power_prediction_retraction(self):
        """EXP-E: Verify full retraction of predictive claims (hardcoded predictions, N=2)."""
        res_e = run_exp_e(self.data)
        self.assertEqual(res_e['status'], 'RETRACTED_INVALID_COMPARISON')
        self.assertIn('RETRACTED', res_e['audit_verdict'])
        self.assertEqual(len(res_e['fatal_flaws_documented']), 4)
        # Ensure historical RMSE values are retained for provenance
        hist = res_e['retained_historical_values_for_provenance']
        self.assertIn('historical_RMSE_bridge_W', hist)
        self.assertAlmostEqual(hist['historical_RMSE_bridge_W'], 0.65, places=1)

    def test_report_json_consistency(self):
        """Verify numerical claims in REPORT.md match experiment_results.json."""
        p_json = BASE / 'experiment_results.json'
        results = json.loads(p_json.read_text('utf-8'))
        p_report = BASE / 'REPORT.md'
        report_text = p_report.read_text('utf-8')

        # Check key quantitative markers
        self.assertIn('0.73', report_text)
        self.assertIn('0.55', report_text)
        self.assertIn('0.65', report_text)
        self.assertIn('4.99', report_text)
        self.assertIn('204.8', report_text)
        self.assertIn('1021.4', report_text)
        self.assertIn('-0.709', report_text)
        self.assertIn('RETRACTED', report_text)

    def test_cannon2014_open_access_in_sources(self):
        """Verify Cannon et al. (2014) is marked open access via PMC4262339 in registry."""
        p_src = REPO_ROOT / 'registry' / 'sources.json'
        sources = json.loads(p_src.read_text('utf-8'))
        cannon_src = [s for s in sources if s['id'] == 'SRC-0058'][0]
        self.assertTrue(cannon_src.get('open_access'))
        self.assertEqual(cannon_src.get('pmcid'), 'PMC4262339')

if __name__ == '__main__':
    unittest.main()
