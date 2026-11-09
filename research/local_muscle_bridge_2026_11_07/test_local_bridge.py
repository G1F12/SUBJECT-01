"""Unit and scientific audit test suite for Cycle 7 Local Muscle Bridge.
Verifies:
1. Strict separation of published data, literature correlations, and approximate digitizations.
2. Cross-study isolation: Cannon et al. (2014, knee extension) vs Moll et al. (2017, 2018, plantarflexion).
3. Physical thermodynamic bounds: NO apparent efficiency > 1.0; 0.44-1.50 is a diagnostic artifact.
4. Exact structural invariance under Scale and Additive Shift symmetries.
5. Correct literature provenance: Moll et al. 2017 (R2=0.73, 0.55, 0.65) and Cannon et al. 2014 (PMC4262339 Table 1).
6. Formal retraction of EXP-0031 predictive claims, unverified eyeball correlations (R2=0.919, 0.978), and unverified slope (14 s / 0.1 pH).
7. Absolute numerical single-source-of-truth consistency across REPORT.md, registries, and experiment_results.json.
8. Identifiability pipeline: exact 7-parameter computed ranks (M1=0/7 .. M7=6/7), monotonicity, structured channels, and nullspace structure.
"""
import unittest
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[1]

from identifiability import LocalBridgeModel, analyze_identifiability, TOPOLOGY_CHANNELS
from experiments import load_moll_data, run_exp_a, run_exp_b, run_exp_c, run_exp_d, run_exp_e

class TestLocalMuscleBridgeConsistencyAudit(unittest.TestCase):
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

        # Check metadata concept separation
        meta = self.data['metadata']
        self.assertIn('physiological_concept_separation', meta)
        concepts = meta['physiological_concept_separation']
        for c in ['atp_turnover', 'atp_resynthesis', 'pcr_pool_capacity', 'net_pcr_depletion',
                  'chemical_free_energy', 'external_mechanical_work', 'whole_body_metabolic_cost']:
            self.assertIn(c, concepts)

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

    def test_cross_study_isolation_cannon_vs_moll(self):
        """Task 2: Verify Cannon 2014 is isolated as knee extension and not equated to calf."""
        cannon = self.data['cannon2014_pmc4262339_atp_turnover']
        self.assertIn('knee extension', cannon['exercise'].lower())
        self.assertIn('cross_study_isolation_warning', cannon)
        self.assertIn('quadriceps', cannon['cross_study_isolation_warning'].lower())
        self.assertIn('plantarflexion', cannon['cross_study_isolation_warning'].lower())

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

    def test_exp_a_numerical_truth_and_retractions(self):
        """EXP-A: Verify reproducible numerical results and retraction of R2=0.919 and slope."""
        res_a = run_exp_a(self.data)
        self.assertIn('RETRACTED', res_a['audit_verdict'])
        self.assertEqual(res_a['literature_published_benchmark']['R2'], 0.73)

        # Reproducible asymptote span: [-22.867%, +20.862%]
        span = res_a['asymptote_uncertainty_analysis']['span_pct']
        self.assertAlmostEqual(span[0], -22.867, places=2)
        self.assertAlmostEqual(span[1], 20.862, places=2)

        # Reproducible spatial heterogeneity: 10.5996% (10.6%)
        bias = res_a['spatial_heterogeneity_simulation']['bias_pct']
        self.assertAlmostEqual(bias, 10.5996, places=3)

        # Finding texts must contain exact rounded numbers
        finding_asym = res_a['asymptote_uncertainty_analysis']['finding']
        self.assertIn('-22.9%', finding_asym)
        self.assertIn('+20.9%', finding_asym)

        finding_het = res_a['spatial_heterogeneity_simulation']['finding']
        self.assertIn('10.6%', finding_het)

    def test_exp_b_4component_delays_and_collinearity(self):
        """EXP-B: Verify 4 distinct delays, FIM condition number 6.89, and structural identifiability."""
        res_b = run_exp_b(self.data)
        delays = res_b['delay_components']
        self.assertAlmostEqual(delays['t_sampling_line_delay_s'], 2.075, places=3)
        self.assertAlmostEqual(delays['t_sampling_line_dispersion_s'], 0.307, places=3)
        corr = res_b['collinearity_simulation']['delay_tau_correlation']
        self.assertAlmostEqual(corr, -0.709, places=2)
        cond = res_b['collinearity_simulation']['FIM_condition_number']
        self.assertAlmostEqual(cond, 6.89, places=1)

    def test_exp_c_deterministic_scenario_grid(self):
        """EXP-C: Verify deterministic scenario grid bounds (42.8% to 77.1%, nominal 66.3%)."""
        res_c = run_exp_c(self.data)
        pub = res_c['published_literature_correlations']
        self.assertEqual(pub['tau_pcr_vs_tau_vo2']['R2'], 0.55)
        self.assertEqual(pub['excess_co2_vs_pH_end']['R2'], 0.65)

        bounds = res_c['systemic_parasitic_scenario_evaluation']['uncertainty_bounds_pct']
        self.assertAlmostEqual(bounds[0], 42.8, places=1)
        self.assertAlmostEqual(bounds[1], 77.1, places=1)

        nominal = res_c['systemic_parasitic_scenario_evaluation']['nominal_scenario']['parasitic_fraction_pct']
        self.assertAlmostEqual(nominal, 66.3, places=1)

    def test_exp_d_pcr_buffer_vs_atp_turnover_and_artifact_warning(self):
        """EXP-D: Verify PCr capacity (204.8-1021.4 J), ATP turnover (>11,500 J) and diagnostic ratio note."""
        res_d = run_exp_d(self.data)
        pcr_span = res_d['pcr_buffer_capacity_J']
        self.assertAlmostEqual(pcr_span['min_J'], 204.75, places=1)
        self.assertAlmostEqual(pcr_span['max_J'], 1021.44, places=1)
        self.assertAlmostEqual(pcr_span['ratio_max_min'], 4.9887, places=2)

        # Total 180s turnover must exceed 10,000 J
        work_180s = res_d['cumulative_180s_energy_comparison_J']['required_atp_metabolic_energy_J']
        self.assertGreater(work_180s, 10000.0)

        # Cannon 2014 Table 1 (knee extension)
        cannon = res_d['atp_turnover_flux_partition_cannon2014']
        self.assertIn('knee extension', cannon['exercise_modality'].lower())
        self.assertGreater(cannon['oxidative_fraction_pct'], 85.0)

        # Initial burst ratio: must have diagnostic note that >1.0 violates energy conservation
        burst = res_d['initial_burst_efficiency_bounds']
        self.assertEqual(burst['eta_apparent_span'], [0.44, 1.50])
        self.assertIn('DIAGNOSTIC ARTIFACT', burst['apparent_ratio_diagnostic_note'])
        self.assertIn('energy conservation', burst['apparent_ratio_diagnostic_note'].lower())

    def test_exp_e_power_prediction_retraction(self):
        """EXP-E: Verify full retraction of predictive claims (hardcoded predictions, N=2)."""
        res_e = run_exp_e(self.data)
        self.assertEqual(res_e['status'], 'RETRACTED_INVALID_COMPARISON')
        self.assertIn('RETRACTED', res_e['audit_verdict'])
        self.assertEqual(len(res_e['fatal_flaws_documented']), 4)

        hist = res_e['retained_historical_values_for_provenance']
        self.assertIn('historical_RMSE_bridge_W', hist)
        self.assertAlmostEqual(hist['historical_RMSE_bridge_W'], 0.65, places=1)

    def test_identifiability_pipeline_ranks_and_monotonicity(self):
        """Verify explicit structured topologies, exact 7-parameter ranks, and monotonicity."""
        results = analyze_identifiability()

        # Check all topologies exist
        expected_topologies = [
            'M1_power_only', 'M2_power_relPCr', 'M3_power_relPCr_VO2',
            'M4_power_absPCr', 'M5_power_absPCr_volume', 'M6_power_absPCr_vol_baseline', 'M7_fully_anchored'
        ]
        for top in expected_topologies:
            self.assertIn(top, results)
            self.assertEqual(results[top]['n_parameters'], 7)
            self.assertIsInstance(results[top]['channels'], list)

        # M1 power only: prescribed ergometer input, zero parameter sensitivity
        self.assertEqual(results['M1_power_only']['effective_rank'], 0)
        self.assertEqual(results['M1_power_only']['rank_defect'], 7)
        self.assertIsNone(results['M1_power_only']['condition_number'])
        self.assertEqual(results['M1_power_only']['condition_number_status'], 'INFINITE')

        # Exact computed ranks over 7 parameters:
        self.assertEqual(results['M2_power_relPCr']['effective_rank'], 3)
        self.assertEqual(results['M3_power_relPCr_VO2']['effective_rank'], 4)
        self.assertEqual(results['M4_power_absPCr']['effective_rank'], 3)
        self.assertEqual(results['M5_power_absPCr_volume']['effective_rank'], 4)
        self.assertEqual(results['M6_power_absPCr_vol_baseline']['effective_rank'], 5)
        self.assertEqual(results['M7_fully_anchored']['effective_rank'], 6)

        # Monotonicity checks:
        # Branch 1 (relative PCr): M1 -> M2 -> M3
        self.assertLessEqual(results['M1_power_only']['effective_rank'], results['M2_power_relPCr']['effective_rank'])
        self.assertLessEqual(results['M2_power_relPCr']['effective_rank'], results['M3_power_relPCr_VO2']['effective_rank'])
        # Branch 2 (absolute PCr): M4 -> M5 -> M6 -> M7
        self.assertLessEqual(results['M4_power_absPCr']['effective_rank'], results['M5_power_absPCr_volume']['effective_rank'])
        self.assertLessEqual(results['M5_power_absPCr_volume']['effective_rank'], results['M6_power_absPCr_vol_baseline']['effective_rank'])
        self.assertLessEqual(results['M6_power_absPCr_vol_baseline']['effective_rank'], results['M7_fully_anchored']['effective_rank'])

        # M7 structural nullspace: exactly 1 defect spanning eta_loc - dG_ATP_kJ_mol
        self.assertEqual(results['M7_fully_anchored']['rank_defect'], 1)
        m7_null = results['M7_fully_anchored']['nullspace_basis'][0]
        self.assertIn('eta_loc', m7_null)
        self.assertIn('dG_ATP_kJ_mol', m7_null)
        self.assertAlmostEqual(abs(m7_null['eta_loc']), abs(m7_null['dG_ATP_kJ_mol']), places=5)

        # M7 condition number: well-conditioned on the 6 identifiable dimensions
        self.assertLess(results['M7_fully_anchored']['effective_condition_number'], 10.0)

    def test_identifiability_results_file_and_math_doc_consistency(self):
        """Verify identifiability_results.json and MATHEMATICS.md strictly report exact computed ranks."""
        res_file = BASE / 'identifiability_results.json'
        data = json.loads(res_file.read_text('utf-8'))
        topologies = data['topologies']

        self.assertEqual(topologies['M1_power_only']['effective_rank'], 0)
        self.assertEqual(topologies['M2_power_relPCr']['effective_rank'], 3)
        self.assertEqual(topologies['M3_power_relPCr_VO2']['effective_rank'], 4)
        self.assertEqual(topologies['M4_power_absPCr']['effective_rank'], 3)
        self.assertEqual(topologies['M5_power_absPCr_volume']['effective_rank'], 4)
        self.assertEqual(topologies['M6_power_absPCr_vol_baseline']['effective_rank'], 5)
        self.assertEqual(topologies['M7_fully_anchored']['effective_rank'], 6)

        # MATHEMATICS.md must contain exact 7-parameter table without fictitious 9/9 claims
        math_doc = (BASE / 'MATHEMATICS.md').read_text('utf-8')
        self.assertIn('M1: Только мощность', math_doc)
        self.assertIn('| **0** | 7 | 7 |', math_doc)
        self.assertIn('| **3** | 7 | 4 |', math_doc)
        self.assertIn('| **4** | 7 | 3 |', math_doc)
        self.assertIn('| **5** | 7 | 2 |', math_doc)
        self.assertIn('| **6** | 7 | 1 |', math_doc)
        self.assertNotIn('ПОЛНЫЙ РАНГ 9/9!', math_doc)
        self.assertNotIn('| 9 | 9 | 0 |', math_doc)

    def test_report_and_registries_strict_numerical_crosscheck(self):
        """Verify numerical single source of truth across REPORT.md, registries, and experiment_results.json."""
        p_json = BASE / 'experiment_results.json'
        results = json.loads(p_json.read_text('utf-8'))
        p_report = BASE / 'REPORT.md'
        report_text = p_report.read_text('utf-8')

        # Check exact numerical values from Python results
        self.assertIn('-22.9', report_text)
        self.assertIn('+20.9', report_text)
        self.assertIn('10.6', report_text)
        self.assertIn('42.8', report_text)
        self.assertIn('77.1', report_text)
        self.assertIn('66.3', report_text)
        self.assertIn('204.8', report_text)
        self.assertIn('1021.4', report_text)
        self.assertIn('4.99', report_text)
        self.assertIn('0.73', report_text)
        self.assertIn('0.55', report_text)
        self.assertIn('0.65', report_text)
        self.assertIn('-0.709', report_text)
        self.assertIn('6.89', report_text)

        # Check absence of old inconsistent numbers in REPORT.md
        self.assertNotIn('-17.8%', report_text)
        self.assertNotIn('+26.4%', report_text)
        self.assertNotIn('11.4%', report_text)
        self.assertNotIn('45%–78%', report_text)
        self.assertNotIn('45%-78%', report_text)
        self.assertNotIn('34.2', report_text)

        # Check that unverified slope claim is explicitly retracted and not claimed as an active finding
        self.assertIn('наклон отозван', report_text.lower())
        self.assertNotIn('140 с/pH', report_text)

        # Check registries
        p_exp = REPO_ROOT / 'registry' / 'experiments.json'
        exp_registry = json.loads(p_exp.read_text('utf-8'))
        exp27 = [e for e in exp_registry if e['id'] == 'EXP-0027'][0]
        self.assertEqual(exp27['results']['asymptote_tau_error_pct_span'], [-22.9, 20.9])
        self.assertEqual(exp27['results']['mono_fit_heterogeneity_max_error_pct'], 10.6)

        exp28 = [e for e in exp_registry if e['id'] == 'EXP-0028'][0]
        self.assertEqual(exp28['results']['FIM_condition_number'], 6.89)

        exp29 = [e for e in exp_registry if e['id'] == 'EXP-0029'][0]
        self.assertEqual(exp29['results']['scenario_parasitic_bounds_pct'], [42.8, 77.1])

        p_fnd = REPO_ROOT / 'registry' / 'findings.json'
        fnd_registry = json.loads(p_fnd.read_text('utf-8'))
        fnd29 = [f for f in fnd_registry if f['id'] == 'FND-0029'][0]
        self.assertIn('42.8-77.1%', fnd29['claim'])

        fnd30 = [f for f in fnd_registry if f['id'] == 'FND-0030'][0]
        self.assertIn('-22.9%..+20.9%', fnd30['claim'])
        self.assertIn('10.6%', fnd30['claim'])
        self.assertNotIn('140 s', fnd30['statement'])
        self.assertIn('отозван', fnd30['statement'].lower())
        self.assertNotIn('14 с', fnd30['claim'])

        fnd31 = [f for f in fnd_registry if f['id'] == 'FND-0031'][0]
        self.assertIn('6.89', fnd31['statement'])

    def test_cannon2014_open_access_in_sources(self):
        """Verify Cannon et al. (2014) is marked open access via PMC4262339 in registry."""
        p_src = REPO_ROOT / 'registry' / 'sources.json'
        sources = json.loads(p_src.read_text('utf-8'))
        cannon_src = [s for s in sources if s['id'] == 'SRC-0058'][0]
        self.assertTrue(cannon_src.get('open_access'))
        self.assertEqual(cannon_src.get('pmcid'), 'PMC4262339')

if __name__ == '__main__':
    unittest.main()
