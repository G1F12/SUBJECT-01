#!/usr/bin/env python3
"""Comprehensive Regression and Scientific Validity Unit Tests for Research Cycle 8.
Verifies all validity corrections:
1. Bibliography cross-validation (DOI/PMCID, Edwards 2013 authorship, Andersen 1985 DOI).
2. EXP-0032 sEMG recruitment validity, 2 kHz hardware sampling, separate trials, scenario status.
3. EXP-0033 absolute phosphagen scale, enthalpy vs Gibbs free energy, numerical consistency.
4. EXP-0034 M_loc literature provenance (quadriceps transfer caveat vs calf).
5. EXP-0035 3-level identifiability resolution, nuisance parameters, no identity shortcuts.
6. EXP-0036 D2 macro-model isolation and TARGET-CPE45 NO_GO policy.
7. Numerical consistency between JSON artifacts and REPORT.md.
"""
import unittest
from pathlib import Path
import json
import re

BASE = Path(__file__).resolve().parent

class TestEmpiricalAnchorsValidity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.franke_path = BASE / 'franke2020_extracted_measurements.json'
        cls.exp_path = BASE / 'experiment_results.json'
        cls.ident_path = BASE / 'identifiability_physical_results.json'
        cls.sources_path = BASE / 'sources.json'
        cls.report_path = BASE / 'REPORT.md'

        cls.franke_data = json.loads(cls.franke_path.read_text(encoding='utf-8'))
        cls.exp_data = json.loads(cls.exp_path.read_text(encoding='utf-8'))
        cls.ident_data = json.loads(cls.ident_path.read_text(encoding='utf-8'))
        cls.sources_data = json.loads(cls.sources_path.read_text(encoding='utf-8'))
        cls.report_text = cls.report_path.read_text(encoding='utf-8')

    def test_01_doi_and_pmcid_cross_validation(self):
        """Verify correct DOI, PMCID, and author attribution across all Cycle 8 sources."""
        sources_by_id = {s['id']: s for s in self.sources_data}

        # Meyerspeer 2021
        s65 = sources_by_id['SRC-0065']
        self.assertEqual(s65['pmc'], 'PMC8243949', "Meyerspeer 2021 PMCID must be PMC8243949 (not PMC8359288)")
        self.assertEqual(s65['doi'], '10.1002/nbm.4246')

        # Andersen & Saltin 1985
        s66 = sources_by_id['SRC-0066']
        self.assertEqual(s66['doi'], '10.1113/jphysiol.1985.sp015794', "Andersen & Saltin 1985 DOI must be sp015794 (not sp015864)")

        # Edwards et al. 2013 (InSight trial)
        s64 = sources_by_id['SRC-0064']
        self.assertEqual(s64['doi'], '10.1038/srep01182')
        self.assertEqual(s64['pmc'], 'PMC3560356')
        self.assertIn('Edwards', s64['name'], "InSight trial primary first author is Edwards et al., not Sleigh et al.")

        # Franke et al. 2020
        s63 = sources_by_id['SRC-0063']
        self.assertEqual(s63['doi'], '10.3389/fbioe.2020.00622')
        self.assertEqual(s63['pmc'], 'PMC7332772')

        # Ryan et al. 2014
        s67 = sources_by_id['SRC-0067']
        self.assertEqual(s67['doi'], '10.1113/jphysiol.2013.265686')

    def test_02_semg_recruitment_and_volume_caveats(self):
        """Verify that sEMG RMS is not equated to active volume and sampling is documented."""
        franke = self.franke_data
        semg = franke['semg_activation_statistics']
        self.assertEqual(semg['hardware_sampling_rate_hz'], 2000)
        self.assertEqual(semg['count'], 240001)
        self.assertEqual(semg['grid_time_step_s'], 0.00025)
        self.assertIn('4 kHz', semg['sampling_note'])

        # Experimental separation
        self.assertIn('separate', franke['subject_info']['experimental_separation_note'].lower())

        # EXP-0032 classification
        exp32 = self.exp_data['experiments']['EXP-0032']
        audit = exp32['methodological_audit']
        self.assertEqual(audit['active_volume_status'], 'SCENARIO_HYPOTHESIS')
        self.assertIn('NOT an empirical measurement', audit['recruitment_validity'])

        bounds = exp32['active_volume_bounds_L']
        self.assertEqual(bounds['classification'], 'SCENARIO_HYPOTHESIS_NOT_EMPIRICALLY_MEASURED')
        self.assertAlmostEqual(bounds['min_L'], 0.0835758, places=2)
        self.assertAlmostEqual(bounds['max_L'], 0.1443582, places=2)

    def test_03_absolute_phosphagen_quantification_and_thermodynamic_scale(self):
        """Verify absolute phosphagen distinctions, enthalpy vs Gibbs free energy, and pool bounds."""
        exp33 = self.exp_data['experiments']['EXP-0033']
        phos = exp33['empirical_phosphagen_quantification_edwards2013']
        self.assertEqual(phos['measured_pcr_to_gamma_atp_ratio'], 4.10)
        self.assertEqual(phos['absolute_concentration_status'], 'REQUIRES_ASSUMED_ATP_REFERENCE')
        self.assertEqual(phos['assumed_atp_reference_nominal_mM'], 8.2)

        thermo = exp33['enthalpy_vs_gibbs_comparison']
        self.assertAlmostEqual(thermo['delta_H_reaction_heat_kJ_mol'], 21.0, places=1)
        self.assertAlmostEqual(thermo['delta_G_ATP_work_potential_kJ_mol'], 54.0, places=1)
        self.assertAlmostEqual(thermo['ratio_delta_G_to_delta_H'], 54.0 / 21.0, places=4)
        self.assertIn('energy_definition_caveat', thermo)

        pool = exp33['pcr_buffer_pool_capacity_bounds_J']
        self.assertEqual(pool['min_J'], 111.4)
        self.assertEqual(pool['nom_J'], 217.9)
        self.assertEqual(pool['max_J'], 947.0)
        self.assertEqual(pool['ratio_max_min'], 8.50)

    def test_04_m_loc_baseline_and_quadriceps_transfer_caveat(self):
        """Verify EXP-0034 resting M_loc catheterization anchor and ASL/NIRS uncertainties."""
        exp34 = self.exp_data['experiments']['EXP-0034']
        cath = exp34['invasive_catheterization_literature_benchmark']
        self.assertEqual(cath['transfer_to_calf_status'], 'MODEL_ASSUMED_QUADRICEPS_TRANSFER')
        self.assertIn('quadriceps', cath['muscle_studied'].lower())
        self.assertAlmostEqual(cath['M_loc_nominal_mM_s'], 0.0064, places=3)

        asl = exp34['asl_mri_perfusion_evaluation']
        self.assertGreaterEqual(asl['uncertainty_ratio'], 2.0)

        nirs = exp34['nirs_vot_evaluation']
        self.assertGreaterEqual(nirs['uncertainty_ratio'], 5.0)

    def test_05_identifiability_3_levels_and_no_identity_channels(self):
        """Verify 3-level identifiability resolution, nuisance parameters, and rank defects."""
        ident = self.ident_data

        # Level 1: Conditional full rank reaches 7/7 under frozen calibrations
        l1 = ident['level_1_conditional_mathematical_identifiability']
        self.assertEqual(l1['P7_physical_without_spec']['effective_rank'], 6)
        self.assertEqual(l1['P7_physical_without_spec']['nullspace_dim'], 1)
        self.assertEqual(l1['P8_physical_with_spectroscopy']['effective_rank'], 7)
        self.assertEqual(l1['P8_physical_with_spectroscopy']['nullspace_dim'], 0)
        self.assertLess(l1['P8_physical_with_spectroscopy']['condition_number_effective'], 20.0)

        # Level 2: Practical identifiability with unknown nuisance parameters
        l2 = ident['level_2_practical_identifiability_with_nuisance']
        self.assertEqual(l2['total_parameters'], 11)
        self.assertLess(l2['effective_rank'], 11, "With unknown nuisance parameters, system must have rank defect")
        self.assertGreaterEqual(l2['nullspace_dim'], 3, "Rank defect must be at least 3")

        diag = l2['parameter_diagnosis']
        self.assertEqual(diag['dG_ATP_kJ_mol']['status'], 'STRUCTURALLY_UNIDENTIFIABLE_OR_FLAT')
        self.assertEqual(diag['M_loc_mM_s']['status'], 'STRUCTURALLY_UNIDENTIFIABLE_OR_FLAT')

        # Level 3: Empirical human data status
        l3 = ident['level_3_empirical_identifiability_human_data']
        self.assertEqual(l3['status'], 'NOT_EMPIRICALLY_IDENTIFIED')

    def test_06_macro_model_isolation_and_target_cpe45(self):
        """Verify EXP-0036 D2 macro-model isolation and TARGET-CPE45 policy."""
        exp36 = self.exp_data['experiments']['EXP-0036']
        audit = exp36['scaling_discrepancy_audit']
        self.assertGreater(audit['muscle_mass_ratio_whole_body_to_GM'], 40.0)
        self.assertGreater(audit['maximal_aerobic_power_ratio'], 200.0)
        self.assertGreater(audit['basal_metabolic_power_ratio'], 1000.0)

        d2_act = exp36['d2_quotient_preservation']['action']
        self.assertEqual(d2_act, 'RETAIN_9D_QUOTIENT')

        cpe = exp36['target_cpe45_evaluation']
        self.assertEqual(cpe['status'], 'NOT_EXTERNALLY_VALIDATED')
        self.assertEqual(cpe['biological_interventions'], 'NO_GO')

    def test_07_numerical_consistency_between_json_and_report(self):
        """Verify strict numerical consistency between experiment_results.json and REPORT.md."""
        # 1. Pool capacity bounds: 111.4 and 947.0 J
        self.assertIn('111.4', self.report_text)
        self.assertIn('947.0', self.report_text)
        self.assertNotIn('111.2', self.report_text, "Old inconsistent 111.2 J must not appear in REPORT.md")
        self.assertNotIn('945.8', self.report_text, "Old inconsistent 945.8 J must not appear in REPORT.md")

        # 2. V_anat volume: 379.89 mL
        self.assertIn('379.89', self.report_text)

        # 3. Underestimation ratios: 2.63 and 4.55
        self.assertIn('2.63', self.report_text)
        self.assertIn('4.55', self.report_text)

        # 4. Edwards 2013 (no Sleigh as first author)
        self.assertIn('Edwards et al. 2013', self.report_text)
        self.assertNotIn('Sleigh et al. 2013', self.report_text)

        # 5. Meyerspeer PMCID
        self.assertIn('PMC8243949', self.report_text)
        self.assertNotIn('PMC8359288', self.report_text)

        # 6. Andersen & Saltin DOI
        self.assertIn('sp015794', self.report_text)
        self.assertNotIn('sp015864', self.report_text)

if __name__ == '__main__':
    unittest.main()
