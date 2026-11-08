#!/usr/bin/env python3
"""Unit tests for Research Cycle 8: Empirical Local Energy Anchors."""
import unittest
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parent

class TestEmpiricalAnchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.franke_path = BASE / 'franke2020_extracted_measurements.json'
        cls.exp_path = BASE / 'experiment_results.json'
        cls.ident_path = BASE / 'identifiability_physical_results.json'
        cls.sources_path = BASE / 'sources.json'

        cls.franke_data = json.loads(cls.franke_path.read_text(encoding='utf-8'))
        cls.exp_data = json.loads(cls.exp_path.read_text(encoding='utf-8'))
        cls.ident_data = json.loads(cls.ident_path.read_text(encoding='utf-8'))
        cls.sources_data = json.loads(cls.sources_path.read_text(encoding='utf-8'))

    def test_01_franke_extracted_data_integrity(self):
        """Verify extracted Franke 2020 MRI, sEMG and 31P-MRS data."""
        mri = self.franke_data['mri_anatomical_parameters']
        self.assertAlmostEqual(mri['volume_mL'], 379.89, places=2)
        self.assertAlmostEqual(mri['volume_L'], 0.37989, places=5)
        self.assertAlmostEqual(mri['muscle_mass_kg'], 0.3587, places=4)
        self.assertAlmostEqual(mri['pcsa_cm2'], 58.98, places=2)
        self.assertAlmostEqual(mri['optimal_fiber_length_m'], 0.0574, places=4)
        self.assertAlmostEqual(mri['f_max_isometric_N'], 1474.4, delta=1.0)

        mrs = self.franke_data['mrs_dynamic_energy_accumulation']
        self.assertEqual(len(mrs['energy_exp_J_per_kg']), 11)
        self.assertEqual(len(mrs['time_points_s']), 11)
        self.assertEqual(mrs['time_points_s'][0], 0.0)
        self.assertEqual(mrs['time_points_s'][-1], 50.0)
        self.assertAlmostEqual(mrs['energy_exp_J_per_kg'][0], 0.0, places=5)
        self.assertGreater(mrs['energy_exp_J_per_kg'][5], 100.0) # > 100 J/kg at 25 s

    def test_02_exp_0032_active_volume_dissociation(self):
        """Verify EXP-0032 volume dissociation and flux distortion bounds."""
        res = self.exp_data['experiments']['EXP-0032']
        bounds = res['active_volume_bounds_L']
        self.assertGreater(bounds['min_L'], 0.08)
        self.assertLess(bounds['max_L'], 0.15)
        self.assertLess(bounds['max_L'], res['mri_measured_parameters']['V_anat_L'])

        audit = res['flux_distortion_audit']
        self.assertGreater(audit['nominal_underestimation_ratio'], 2.5)
        self.assertLess(audit['nominal_underestimation_ratio'], 5.0)
        self.assertIn('negative_result', res)

    def test_03_exp_0033_thermodynamic_scaling_invariants(self):
        """Verify EXP-0033 enthalpy vs Gibbs free energy scaling and pool capacity."""
        res = self.exp_data['experiments']['EXP-0033']
        thermo = res['enthalpy_vs_gibbs_comparison']
        self.assertAlmostEqual(thermo['delta_H_reaction_heat_kJ_mol'], 21.0, places=1)
        self.assertAlmostEqual(thermo['delta_G_ATP_work_potential_kJ_mol'], 54.0, places=1)
        self.assertAlmostEqual(thermo['ratio_delta_G_to_delta_H'], 54.0 / 21.0, places=4)
        self.assertGreater(thermo['thermodynamic_work_power_total_W'], 4.0) # ~5.35 W

        pool = res['pcr_buffer_pool_capacity_bounds_J']
        self.assertGreater(pool['min_J'], 100.0)
        self.assertLess(pool['max_J'], 1000.0)
        self.assertGreater(pool['ratio_max_min'], 8.0)

    def test_04_exp_0034_m_loc_baseline_bounds(self):
        """Verify EXP-0034 resting M_loc catheterization anchor and ASL/NIRS uncertainties."""
        res = self.exp_data['experiments']['EXP-0034']
        cath = res['invasive_catheterization_gold_standard']
        self.assertGreater(cath['M_loc_nominal_mM_s'], 0.005)
        self.assertLess(cath['M_loc_nominal_mM_s'], 0.008)

        asl = res['asl_mri_perfusion_evaluation']
        self.assertGreaterEqual(asl['uncertainty_ratio'], 2.0)

        nirs = res['nirs_vot_evaluation']
        self.assertGreaterEqual(nirs['uncertainty_ratio'], 5.0)

    def test_05_exp_0035_physical_identifiability_ranks(self):
        """Verify EXP-0035 physical Jacobian ranks and spectroscopic rank restoration."""
        phys = self.ident_data['physical_topologies_cycle8']
        self.assertEqual(phys['P1_ergometer_input']['effective_rank'], 0)
        self.assertEqual(phys['P2_ergometer_relPCr']['effective_rank'], 3)
        self.assertEqual(phys['P3_ergometer_relPCr_pulmVO2']['effective_rank'], 4)
        self.assertEqual(phys['P4_ergometer_absPCr']['effective_rank'], 3)
        self.assertEqual(phys['P5_ergometer_absPCr_mriAnat']['effective_rank'], 4)
        self.assertEqual(phys['P6_ergometer_absPCr_mri_uncalNIRS']['effective_rank'], 5)
        self.assertEqual(phys['P7_physical_without_spec']['effective_rank'], 6)
        self.assertEqual(phys['P8_physical_with_spectroscopy']['effective_rank'], 7) # FULL RANK 7/7

        # Condition number of P8
        self.assertLess(phys['P8_physical_with_spectroscopy']['condition_number_effective'], 20.0)
        self.assertEqual(phys['P8_physical_with_spectroscopy']['nullspace_dim'], 0)

        # In P7 nullspace dimension is strictly 1
        self.assertEqual(phys['P7_physical_without_spec']['nullspace_dim'], 1)
        p7_null = phys['P7_physical_without_spec']['nullspace_basis'][0]
        # Nullspace must have non-zero components for eta_loc and dG_ATP
        self.assertNotAlmostEqual(p7_null['eta_loc'], 0.0)
        self.assertNotAlmostEqual(p7_null['dG_ATP_kJ_mol'], 0.0)

    def test_06_exp_0036_d2_isolation_and_cpe45_policy(self):
        """Verify EXP-0036 D2 macro-model scale isolation and TARGET-CPE45 policy."""
        res = self.exp_data['experiments']['EXP-0036']
        audit = res['scaling_discrepancy_audit']
        self.assertGreater(audit['muscle_mass_ratio_whole_body_to_GM'], 40.0)
        self.assertGreater(audit['maximal_aerobic_power_ratio'], 200.0)
        self.assertGreater(audit['basal_metabolic_power_ratio'], 1000.0)

        d2_act = res['d2_quotient_preservation']['action']
        self.assertEqual(d2_act, 'RETAIN_9D_QUOTIENT')

        cpe = res['target_cpe45_evaluation']
        self.assertEqual(cpe['status'], 'NOT_EXTERNALLY_VALIDATED')
        self.assertEqual(cpe['biological_interventions'], 'NO_GO')

    def test_07_cycle8_sources_registry_consistency(self):
        """Verify that all 5 new Cycle 8 sources exist with valid fields."""
        source_ids = [s['id'] for s in self.sources_data]
        expected_ids = ['SRC-0063', 'SRC-0064', 'SRC-0065', 'SRC-0066', 'SRC-0067']
        for sid in expected_ids:
            self.assertIn(sid, source_ids)

        for s in self.sources_data:
            self.assertTrue(s['id'].startswith('SRC-'))
            self.assertIn('name', s)
            self.assertIn('doi', s)
            self.assertIn('verified_channels', s)
            self.assertIn('verification_status', s)

if __name__ == '__main__':
    unittest.main()
