#!/usr/bin/env python3
"""
SUBJECT-01 — Research Cycle 9
Regression Test Battery for Empirical Data Acquisition, Recruitment Observability,
and Independent Validation Design (with Data Provenance Gate Verification).
"""

import unittest
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CYCLE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))

from verify_data_provenance import (
    audit_dataset_provenance_records,
    audit_registry_experiments,
    audit_validation_scripts
)

class TestEmpiricalRecruitmentCycle9(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.exp_results = json.loads((CYCLE_DIR / 'experiment_results.json').read_text(encoding='utf-8'))
        cls.report_text = (CYCLE_DIR / 'REPORT.md').read_text(encoding='utf-8')
        cls.audit_text = (CYCLE_DIR / 'DATA_AUDIT.md').read_text(encoding='utf-8')
        cls.sources = json.loads((ROOT / 'registry' / 'sources.json').read_text(encoding='utf-8'))
        
    def test_01_preflight_pcr_capacity_and_thermodynamic_reconciliation(self):
        """Verify strict separation between reaction enthalpy and Gibbs free energy."""
        preflight = self.exp_results['preflight']['question_1_pcr_capacity_reconciliation']
        self.assertAlmostEqual(preflight['enthalpy_delta_H_kJ_mol'], 21.0, places=1)
        self.assertAlmostEqual(preflight['gibbs_delta_G_ATP_nominal_kJ_mol'], 54.0, places=1)
        self.assertAlmostEqual(preflight['ratio_delta_G_to_delta_H'], 2.5714, places=3)
        
        # Verify buffer pool capacity numbers
        caps = preflight['buffer_pool_capacity_J']
        self.assertAlmostEqual(caps['gibbs_work_capacity_nominal_anat_J'], 689.5, places=1)
        self.assertAlmostEqual(caps['calorimetric_heat_capacity_nominal_anat_J'], 268.1, places=1)
        self.assertEqual(caps['gibbs_work_active_scenario_span_J'], [106.2, 389.1])
        
    def test_02_preflight_andersen_saltin_1985_audit_and_downgrade(self):
        """Verify Andersen & Saltin 1985 audit, absence of resting table, and downgraded status."""
        preflight = self.exp_results['preflight']['question_2_andersen_saltin_1985_audit']
        self.assertIn("DOWNGRADED_NOT_PRIMARY_RESTING_TABLE", preflight['status_downgrade'])
        self.assertIn("0.15 to 0.40 L/min", preflight['primary_resting_data_in_paper'])
        self.assertIn("NO resting row", preflight['primary_resting_data_in_paper'])
        
    def test_03_exp0037_empirical_datasets_acquisition(self):
        """Verify empirical human datasets: Rehman 2024 (PMC11617988) and Hug 2021 (Figshare)."""
        exp37 = self.exp_results['experiments']['EXP-0037']
        rehman = exp37['datasets']['rehman_2024_31p_mrs']
        self.assertEqual(rehman['pmcid'], "PMC11617988")
        self.assertEqual(rehman['trials_n'], 3)
        self.assertAlmostEqual(rehman['mean_tau_rec_s'], 39.41, places=1)
        self.assertEqual(rehman['ph_status'], "NON_ACIDOTIC_OXIDATIVE_DOMINATED")
        self.assertEqual(rehman['raw_download_status'], "RAW_TIMESERIES_UNAVAILABLE")
        
        hug = exp37['datasets']['hug_2021_hd_semg']
        self.assertEqual(hug['grid_channels'], 64)
        self.assertEqual(hug['inter_operator_agreement'], 0.996)
        self.assertEqual(hug['independent_subjects_n'], 1)
        self.assertEqual(hug['raters_n'], 8)
        rates = hug['gastrocnemius_medialis_rates_hz']
        self.assertLess(rates['10_mvc'], rates['30_mvc'])
        self.assertLess(rates['30_mvc'], rates['70_mvc'])
        self.assertEqual(hug['raw_download_status'], "RAW_ARCHIVE_BLOCKED_BY_CDN_CHALLENGE")
        
    def test_04_exp0038_biophysical_recruitment_forward_simulation(self):
        """Verify recruitment model: forward simulation hypothesis, 40.9x span, and force-sEMG dissociation."""
        exp38 = self.exp_results['experiments']['EXP-0038']
        self.assertEqual(exp38['data_type'], "SYNTHETIC")
        self.assertEqual(exp38['validation_status'], "COMPUTATIONAL_SIMULATION_HYPOTHESIS")
        
        franke_analysis = exp38['franke_operating_point_analysis']
        self.assertEqual(franke_analysis['target_measured_semg_rms'], 0.127)
        self.assertGreater(franke_analysis['uncertainty_ratio_a_eff'], 40.0)
        
        fatigue = exp38['fatigue_force_emg_dissociation']
        self.assertAlmostEqual(fatigue['force_change_percent'], -35.0, places=1)
        self.assertAlmostEqual(fatigue['semg_rms_change_percent'], 14.0, places=1)
        
    def test_05_exp0039_four_level_identifiability(self):
        """Verify 4-level identifiability resolution, nuisance rank defect, and profile ridge."""
        exp39 = self.exp_results['experiments']['EXP-0039']
        l1 = exp39['level_1_structural_conditional_rank']
        self.assertEqual(l1['status'], "CONDITIONAL_FULL_RANK_UNDER_FROZEN_CALIBRATION")
        
        l3 = exp39['level_3_practical_identifiability_with_nuisances']
        self.assertGreaterEqual(l3['rank_defect'], 4)
        self.assertEqual(l3['status'], "PRACTICALLY_UNIDENTIFIABLE_UNDER_NUISANCE_UNCERTAINTY")
        
        l4 = exp39['level_4_empirical_identifiability']
        self.assertEqual(l4['status'], "NOT_EMPIRICALLY_IDENTIFIED_CROSS_STUDY_DISCONNECTION")
        self.assertIn("No human subject currently exists", l4['blocker'])
        
    def test_06_exp0040_loso_synthetic_demonstration_and_empirical_blocker(self):
        """Verify EXP-0040 is reclassified to synthetic demonstration and empirical validation is blocked."""
        exp40 = self.exp_results['experiments']['EXP-0040']
        self.assertEqual(exp40['data_type'], "SYNTHETIC")
        self.assertEqual(exp40['validation_status'], "SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED")
        self.assertEqual(exp40['empirical_validation_status'], "BLOCKED_PENDING_RAW_DATA")
        self.assertIn("retracted", exp40['retraction_note'].lower())
        
        loso = exp40['cross_subject_loso_summary']
        self.assertIn("synthetic_metrics_retained_for_historical_record", loso)
        
    def test_07_exp0041_cpe45_energy_accounting_and_target_boundaries(self):
        """Verify physical CPE45 energy accounting: 675 kJ external work, ~3375 kJ metabolic expenditure, 0.1-0.6 kJ PCr, 21 kJ/mol enthalpy."""
        exp41 = self.exp_results['experiments']['EXP-0041']
        accounting = exp41['cpe45_energy_accounting']
        self.assertAlmostEqual(accounting['external_mechanical_work_kJ'], 675.0, places=1)
        self.assertAlmostEqual(accounting['whole_body_metabolic_expenditure_nominal_kJ'], 3375.0, places=1)
        self.assertAlmostEqual(accounting['assumed_gross_mechanical_efficiency_eta_gross'], 0.20, places=2)
        self.assertAlmostEqual(accounting['local_pcr_chemical_buffer_work_capacity_kJ']['anatomical_whole_gm_kJ'], 0.621, places=3)
        self.assertAlmostEqual(accounting['local_pcr_hydrolysis_reaction_enthalpy_delta_R_H_kJ_mol'], 21.0, places=1)
        self.assertEqual(exp41['target_cpe45_status'], "NOT EXTERNALLY VALIDATED")
        self.assertEqual(exp41['biological_interventions'], "NO_GO_MAINTAINED")
        
    def test_08_permanent_data_provenance_gate(self):
        """Verify automated data provenance gate passes with zero violations."""
        p1 = audit_dataset_provenance_records()
        self.assertEqual(p1, [], f"Dataset provenance errors: {p1}")
        
        p2 = audit_registry_experiments()
        self.assertEqual(p2, [], f"Registry experiment errors: {p2}")
        
        p3 = audit_validation_scripts()
        self.assertEqual(p3, [], f"Validation script errors: {p3}")
        
    def test_09_report_and_audit_consistency(self):
        """Ensure numerical and source consistency across reports."""
        self.assertIn("39.2", self.report_text)
        self.assertIn("64", self.report_text)
        self.assertIn("675", self.report_text)
        self.assertIn("3375", self.report_text)
        self.assertIn("SRC-0068", self.audit_text)
        self.assertIn("SRC-0069", self.audit_text)
        self.assertIn("SRC-0070", self.audit_text)
        self.assertIn("SRC-0071", self.audit_text)
        self.assertIn("SRC-0072", self.audit_text)

if __name__ == '__main__':
    unittest.main()
