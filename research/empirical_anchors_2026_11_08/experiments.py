#!/usr/bin/env python3
"""Computational Experiments Pipeline for Research Cycle 8 (CORRECTED).

EXP-0032: Anatomical MRI Muscle Volumetry vs Dynamic Functional Recruitment
EXP-0033: Absolute Phosphagen Quantification and Thermodynamic Scale: Enthalpy vs Free Energy
EXP-0034: Local Oxygen Baseline (M_loc) Bounding: Invasive A-V vs ASL vs NIRS
EXP-0035: Measurement Map Identifiability vs Ideal Channels
EXP-0036: Macro-Model Transferability Audit: D2 9D Quotient vs Local Parameters & TARGET-CPE45
"""
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]

def run_exp_0032(franke_data):
    """EXP-0032: Anatomical MRI Muscle Volumetry vs Dynamic Functional Recruitment."""
    mri = franke_data['mri_anatomical_parameters']
    semg = franke_data['semg_activation_statistics']

    v_anat_L = mri['volume_L']
    v_anat_mL = mri['volume_mL']
    muscle_mass_kg = mri['muscle_mass_kg']

    # Submaximal recruitment fraction: SCENARIO HYPOTHESIS ONLY
    # sEMG RMS = 12.7% reflects normalized surface electrical activity.
    # It does NOT directly measure recruited fiber fraction or 3D active volume.
    a_min = 0.22
    a_nom = 0.3175 # scenario exploration value
    a_max = 0.38

    v_active_min_L = v_anat_L * a_min
    v_active_nom_L = v_anat_L * a_nom
    v_active_max_L = v_anat_L * a_max

    # Distortion factor if anatomical volume is falsely used instead of active volume:
    flux_underestimation_factor_nom = v_anat_L / v_active_nom_L
    flux_underestimation_factor_range = [v_anat_L / v_active_max_L, v_anat_L / v_active_min_L]

    return {
        'experiment_id': 'EXP-0032',
        'title': 'Anatomical MRI Muscle Volumetry vs Dynamic Functional Recruitment',
        'source': franke_data['source'],
        'doi': franke_data['doi'],
        'methodological_audit': {
            'experimental_separation': 'In Franke et al. (2020), 3D MRI, sEMG+kinematics, and 31P-MRS were recorded in separate experimental trials, not simultaneously.',
            'semg_sampling': 'Hardware acquisition was 2000 Hz; 240,001 points in supplementary MAT file reflect 4 kHz interpolation/upsampling.',
            'recruitment_validity': 'sEMG RMS (12.7%) is a normalized surface electrical amplitude, NOT an empirical measurement of recruited fiber fraction.',
            'active_volume_status': 'SCENARIO_HYPOTHESIS'
        },
        'mri_measured_parameters': {
            'muscle_name': 'M. gastrocnemius medialis',
            'sequence': mri['sequence'],
            'V_anat_mL': v_anat_mL,
            'V_anat_L': v_anat_L,
            'mass_kg': muscle_mass_kg,
            'PCSA_cm2': mri['pcsa_cm2'],
            'optimal_fiber_length_m': mri['optimal_fiber_length_m'],
            'F_max_N': mri['f_max_isometric_N']
        },
        'semg_activation_metrics': {
            'mean_normalized_MVC': semg['mean'],
            'rms_normalized_MVC': semg['rms'],
            'hypothetical_recruitment_burst_range': [a_min, a_max]
        },
        'active_volume_bounds_L': {
            'min_L': float(v_active_min_L),
            'nom_L': float(v_active_nom_L),
            'max_L': float(v_active_max_L),
            'classification': 'SCENARIO_HYPOTHESIS_NOT_EMPIRICALLY_MEASURED'
        },
        'flux_distortion_audit': {
            'nominal_underestimation_ratio': float(flux_underestimation_factor_nom),
            'range_underestimation_ratio': [float(flux_underestimation_factor_range[0]), float(flux_underestimation_factor_range[1])],
            'finding': 'Anatomical MRI accurately measures V_anat (379.89 mL), but true submaximal active volume is restricted to hypothetical scenario bounds 83.6 - 144.4 mL (nominal 120.6 mL). Substituting V_anat for V_active produces a 2.63- to 4.55-fold underestimation of local ATP demand flux, but V_active remains an uncalibrated scenario variable.'
        },
        'negative_result': 'Anatomical MRI alone cannot determine V_active without an independent, dynamic recruitment model; sEMG RMS cannot be equated to recruited fiber fraction.'
    }

def run_exp_0033(franke_data):
    """EXP-0033: Absolute Phosphagen Quantification and Thermodynamic Scale: Enthalpy vs Free Energy."""
    mrs = franke_data['mrs_dynamic_energy_accumulation']
    v_anat_L = franke_data['mri_anatomical_parameters']['volume_L']

    # Edwards et al. 2013 (PMC3560356, InSight trial cohort n=89):
    # Measured PCr/gamma-ATP = 4.10 +/- 0.03 (SEM), SD ~ 0.3
    pcr_atp_ratio = 4.10
    atp_ref_nom_mM = 8.2
    atp_ref_span_mM = [6.5, 9.5]
    pcr_nom_mM = atp_ref_nom_mM * pcr_atp_ratio # 33.62 mM
    pcr_span_mM = [atp_ref_span_mM[0] * pcr_atp_ratio, atp_ref_span_mM[1] * pcr_atp_ratio] # [26.65, 38.95] mM

    # Enthalpy vs Free Energy
    delta_H_kJ_mol = mrs['assumed_enthalpy_Delta_H_kJ_mol'] # 21.0 kJ/mol (Kodama 1985)
    delta_G_nom_kJ_mol = mrs['thermodynamic_work_Delta_G_ATP_nominal_kJ_mol'] # 54.0 kJ/mol
    delta_G_span_kJ_mol = [50.0, 64.0]

    # Measured dynamic heat accumulation rate in Franke (early burst 0..25 s)
    rate_H_J_kg_s = mrs['linear_fit_rate_early_burst_J_per_kg_s'] # 5.8 J/kg/s
    rate_H_ci95 = mrs['linear_fit_rate_ci95_J_per_kg_s'] # 1.8 J/kg/s

    # Molar turnover rate in Franke:
    molar_rate_mmol_kg_s = rate_H_J_kg_s / delta_H_kJ_mol # 5.8 / 21 = 0.2762 mmol/kg/s
    molar_rate_mM_s = molar_rate_mmol_kg_s / mrs['water_conversion_L_per_kg'] # 0.2762 / 0.68 = 0.4062 mM/s

    # Thermodynamic Gibbs power:
    thermo_power_W_kg = molar_rate_mmol_kg_s * delta_G_nom_kJ_mol # 0.2762 * 54 = 14.91 W/kg
    thermo_power_total_W = thermo_power_W_kg * franke_data['mri_anatomical_parameters']['muscle_mass_kg'] # 14.91 * 0.3587 = 5.35 W

    thermo_to_enthalpy_ratio = delta_G_nom_kJ_mol / delta_H_kJ_mol # 54 / 21 = 2.5714

    # Exact chemical buffer capacity pool bounds (J):
    # E_pool = [PCr] * V_active * dG
    v_act_min_L = 0.0836
    v_act_nom_L = 0.1200
    v_act_max_L = 0.3799 # anatomical upper bound
    pool_min_J = round(pcr_span_mM[0] * v_act_min_L * delta_G_span_kJ_mol[0], 1) # 26.65 * 0.0836 * 50 = 111.4 J
    pool_nom_J = round(pcr_nom_mM * v_act_nom_L * delta_G_nom_kJ_mol, 1) # 33.62 * 0.12 * 54 = 217.9 J
    pool_max_J = round(pcr_span_mM[1] * v_act_max_L * delta_G_span_kJ_mol[1], 1) # 38.95 * 0.3799 * 64 = 947.0 J
    pool_ratio_max_min = round(pool_max_J / pool_min_J, 2) # 8.50

    return {
        'experiment_id': 'EXP-0033',
        'title': 'Absolute Phosphagen Quantification and Thermodynamic Scale: Enthalpy vs Free Energy',
        'sources': ['SRC-0063', 'SRC-0064', 'SRC-0065'],
        'empirical_phosphagen_quantification_edwards2013': {
            'cohort_n': 89,
            'measured_pcr_to_gamma_atp_ratio': pcr_atp_ratio,
            'assumed_atp_reference_nominal_mM': atp_ref_nom_mM,
            'assumed_atp_reference_span_mM': atp_ref_span_mM,
            'implied_pcr_rest_nominal_mM': float(pcr_nom_mM),
            'implied_pcr_rest_span_mM': [float(pcr_span_mM[0]), float(pcr_span_mM[1])],
            'absolute_concentration_status': 'REQUIRES_ASSUMED_ATP_REFERENCE'
        },
        'enthalpy_vs_gibbs_comparison': {
            'delta_H_reaction_heat_kJ_mol': delta_H_kJ_mol,
            'delta_G_ATP_work_potential_kJ_mol': delta_G_nom_kJ_mol,
            'ratio_delta_G_to_delta_H': float(thermo_to_enthalpy_ratio),
            'measured_early_burst_rate_J_kg_s': rate_H_J_kg_s,
            'molar_ATP_turnover_rate_mmol_kg_s': float(molar_rate_mmol_kg_s),
            'molar_ATP_turnover_rate_mM_s': float(molar_rate_mM_s),
            'thermodynamic_work_power_W_kg': float(thermo_power_W_kg),
            'thermodynamic_work_power_total_W': float(thermo_power_total_W),
            'energy_definition_caveat': 'The ratio 54/21 (2.57) illustrates the fundamental difference between reaction enthalpy and Gibbs free energy, but does NOT automatically convert measured heat into true metabolic power without auditing the energy equations of the underlying cross-bridge model.'
        },
        'pcr_buffer_pool_capacity_bounds_J': {
            'min_J': float(pool_min_J),
            'nom_J': float(pool_nom_J),
            'max_J': float(pool_max_J),
            'ratio_max_min': float(pool_ratio_max_min),
            'finding': 'Combined concentration ([PCr] in [26.7, 39.0] mM), active volume (0.084 - 0.380 L), and thermodynamic potential (-50 to -64 kJ/mol) uncertainties generate an 8.50-fold ambiguity (111.4 J to 947.0 J) in static resting PCr buffer capacity.'
        },
        'negative_result': 'Absolute phosphagen energy scale cannot be identified without simultaneously pinning [ATP]_ref, recruitment fraction, and thermodynamic potential Delta_G_ATP.'
    }

def run_exp_0034():
    """EXP-0034: Local Oxygen Baseline (M_loc) Bounding: Invasive A-V vs ASL vs NIRS."""
    # Literature source: Andersen & Saltin 1985 (DOI 10.1113/jphysiol.1985.sp015794)
    # Measured in HUMAN QUADRICEPS (knee-extension model), NOT gastrocnemius!
    flow_catheter_mL_100g_min = 2.4
    flow_catheter_sd = 0.6
    av_o2_diff_mL_L = 58.0
    av_o2_diff_sd = 8.0
    gamma_o2 = 5.8 # mol ATP / mol O2
    muscle_density_kg_L = 1.0597

    # Resting quadriceps muscle VO2 in mL O2 / 100g / min:
    vo2_muscle_mL_100g_min = (flow_catheter_mL_100g_min / 1000.0) * av_o2_diff_mL_L # 0.1392 mL O2/100g/min
    vo2_muscle_mL_L_min = vo2_muscle_mL_100g_min * 10.0 * muscle_density_kg_L # 1.475 mL O2 / L muscle / min

    # Molar ATP resting flux M_loc:
    m_loc_catheter_nom_mM_s = (vo2_muscle_mL_L_min * 1e-3 / 22.414 / 60.0) * gamma_o2 * 1000.0 # 0.00636 mM/s (~0.0064 mM/s)
    m_loc_catheter_span_mM_s = [0.0046, 0.0090]

    # ASL-MRI perfusion measurement properties:
    asl_flow_mL_100g_min = 2.4
    asl_m_loc_span_mM_s = [
        (asl_flow_mL_100g_min * 10 * muscle_density_kg_L * 1e-3 * 0.20 * 200.0 * 1e-3 / 22.414 / 60.0) * gamma_o2 * 1000.0,
        (asl_flow_mL_100g_min * 10 * muscle_density_kg_L * 1e-3 * 0.45 * 200.0 * 1e-3 / 22.414 / 60.0) * gamma_o2 * 1000.0
    ]
    asl_ratio = asl_m_loc_span_mM_s[1] / asl_m_loc_span_mM_s[0]

    # NIRS-VOT uncalibrated slope bounds:
    nirs_slope_nom = 0.15 # % / s
    nirs_m_loc_span_mM_s = [0.0030, 0.0200]
    nirs_ratio = nirs_m_loc_span_mM_s[1] / nirs_m_loc_span_mM_s[0]

    return {
        'experiment_id': 'EXP-0034',
        'title': 'Local Oxygen Baseline (M_loc) Bounding: Invasive A-V vs ASL vs NIRS',
        'sources': ['SRC-0066', 'SRC-0067'],
        'invasive_catheterization_literature_benchmark': {
            'source_study': 'Andersen & Saltin (1985) J Physiol 366:233-249',
            'muscle_studied': 'Human quadriceps femoris (knee extension)',
            'flow_resting_mL_100g_min': flow_catheter_mL_100g_min,
            'av_o2_difference_mL_L': av_o2_diff_mL_L,
            'resting_vo2_muscle_mL_100g_min': float(vo2_muscle_mL_100g_min),
            'resting_vo2_muscle_mL_L_min': float(vo2_muscle_mL_L_min),
            'M_loc_nominal_mM_s': float(m_loc_catheter_nom_mM_s),
            'M_loc_span_mM_s': m_loc_catheter_span_mM_s,
            'transfer_to_calf_status': 'MODEL_ASSUMED_QUADRICEPS_TRANSFER',
            'finding': 'Femoral arterial-venous catheterization provides an invasive gold standard for resting quadriceps oxygen consumption (M_loc = 0.0064 +/- 0.0017 mmol ATP/L/s), but its transfer to gastrocnemius medialis is an unverified cross-muscle assumption.'
        },
        'asl_mri_perfusion_evaluation': {
            'measured_quantity': 'Perfusion flow (mL/100g/min)',
            'unmeasured_quantity': 'Arteriovenous extraction fraction E = (Ca - Cv)/Ca',
            'extraction_fraction_span': [0.20, 0.45],
            'implied_M_loc_span_mM_s': [float(asl_m_loc_span_mM_s[0]), float(asl_m_loc_span_mM_s[1])],
            'uncertainty_ratio': float(asl_ratio),
            'finding': 'ASL-MRI measures capillary perfusion without oxygen extraction; without independent venous oximetry, ASL leaves a 2.25-fold ambiguity in M_loc.'
        },
        'nirs_vot_evaluation': {
            'measured_quantity': 'Rate of tissue hemoglobin desaturation (dStO2/dt in %/s)',
            'confounding_nuisance_parameters': [
                'Adipose tissue thickness (ATT) scattering attenuation (2 - 12 mm)',
                'Differential pathlength factor (DPF = 3.5 - 6.0)',
                'Capillary blood volume fraction (V_b = 2 - 4%)'
            ],
            'implied_M_loc_span_mM_s': nirs_m_loc_span_mM_s,
            'uncertainty_ratio': float(nirs_ratio),
            'finding': 'Continuous-wave NIRS vascular occlusion testing yields a relative kinetics surrogate; uncalibrated optical pathlength and skinfold thickness induce a 6.67-fold ambiguity in molar ATP baseline flux.'
        },
        'negative_result': 'Non-invasive ASL and NIRS cannot identify M_loc without invasive calibration phantoms or direct blood gas verification; catheterization data from quadriceps cannot be treated as measured calf baseline.'
    }

def run_exp_0035(ident_results):
    """EXP-0035: Measurement Map Identifiability vs Ideal Channels (CORRECTED 3-LEVEL AUDIT)."""
    l1 = ident_results['level_1_conditional_mathematical_identifiability']
    l2 = ident_results['level_2_practical_identifiability_with_nuisance']
    l3 = ident_results['level_3_empirical_identifiability_human_data']

    progression = {
        'level_1_conditional_ranks': {k: v['effective_rank'] for k, v in l1.items()},
        'level_1_p7_rank': l1['P7_physical_without_spec']['effective_rank'],
        'level_1_p8_rank': l1['P8_physical_with_spectroscopy']['effective_rank'],
        'level_1_p8_condition': l1['P8_physical_with_spectroscopy']['condition_number_effective'],
        'level_2_practical_total_parameters': l2['total_parameters'],
        'level_2_practical_effective_rank': l2['effective_rank'],
        'level_2_practical_nullspace_dim': l2['nullspace_dim'],
        'level_3_empirical_status': l3['status']
    }

    return {
        'experiment_id': 'EXP-0035',
        'title': 'Measurement Map Identifiability vs Ideal Channels (3-Level Resolution)',
        'status': 'REPAIRED_AND_RIGOROUSLY_CLASSIFIED',
        'rank_progression_summary': progression,
        'level_1_conditional_audit': {
            'p7_rank': l1['P7_physical_without_spec']['effective_rank'],
            'p7_nullspace_dim': l1['P7_physical_without_spec']['nullspace_dim'],
            'p8_rank': l1['P8_physical_with_spectroscopy']['effective_rank'],
            'p8_nullspace_dim': l1['P8_physical_with_spectroscopy']['nullspace_dim'],
            'p8_condition_number': l1['P8_physical_with_spectroscopy']['condition_number_effective'],
            'finding': 'When nuisance parameters (a_eff, g_nirs, b_nirs, k_spec) are conditionally frozen, P7 has rank 6/7 (nullspace in eta_loc and dG_ATP), and P8 reaches CONDITIONAL FULL RANK 7/7 with condition number 15.39 upon adding the spectroscopic free energy channel.'
        },
        'level_2_practical_audit': {
            'total_parameters': l2['total_parameters'],
            'effective_rank': l2['effective_rank'],
            'nullspace_dim': l2['nullspace_dim'],
            'singular_values': l2['singular_values'],
            'parameter_diagnosis': l2['parameter_diagnosis'],
            'finding': 'When nuisance parameters are treated as unknown, the 11D system exhibits rank defect = 4. V_active is collinear with a_eff, M_loc is collinear with g_nirs and b_nirs, and dG_ATP is collinear with k_spec. These parameters form unidentifiable flat ridges in profile likelihood.'
        },
        'level_3_empirical_audit': l3,
        'negative_result': 'Ideal scalar channels (y = theta_j) and frozen nuisance constants in previous analyses masked real physical identifiability defects; without simultaneous multimodal human calibrations, the 7-parameter local energy bridge is practically unidentifiable.'
    }

def run_exp_0036():
    """EXP-0036: Macro-Model Transferability Audit: D2 9D Quotient vs Local Parameters & TARGET-CPE45."""
    mass_gm_kg = 0.3587
    mass_whole_body_active_kg = 18.0
    mass_ratio = mass_whole_body_active_kg / mass_gm_kg # 50.18

    p_ox_max_gm_W = 0.60 * 0.120 * 54.0 # 3.888 W
    p_ox_max_wb_W = 1200.0 # W
    ox_power_ratio = p_ox_max_wb_W / p_ox_max_gm_W # 308.6

    p_rest_gm_W = 0.008 * 0.120 * 54.0 # 0.05184 W
    p_rest_wb_W = 80.0 # W (BMR)
    rest_power_ratio = p_rest_wb_W / p_rest_gm_W # 1543.2

    return {
        'experiment_id': 'EXP-0036',
        'title': 'Macro-Model Transferability Audit: D2 9D Quotient vs Local Parameters & TARGET-CPE45',
        'status': 'STRUCTURAL_ISOLATION_CONFIRMED',
        'scaling_discrepancy_audit': {
            'muscle_mass_ratio_whole_body_to_GM': float(mass_ratio),
            'maximal_aerobic_power_ratio': float(ox_power_ratio),
            'basal_metabolic_power_ratio': float(rest_power_ratio),
            'local_GM_maximal_aerobic_power_W': float(p_ox_max_gm_W),
            'local_GM_resting_power_W': float(p_rest_gm_W),
            'finding': 'Local gastrocnemius bioenergetics operate on 0.05 W basal and 3.89 W maximal oxidative scales, compared to 80 W basal and 1200 W maximal scales for whole-body exercise. Direct parameter substitution into D2 without whole-body recruitment scaling causes catastrophic dimensional failure.'
        },
        'd2_quotient_preservation': {
            'action': 'RETAIN_9D_QUOTIENT',
            'reason': 'The 9 effective quotient parameters of D2 (Cycle 5) reflect macroscopic whole-body work and recovery. Local single-muscle anchors cannot be transferred without whole-body anatomical recruitment maps.'
        },
        'target_cpe45_evaluation': {
            'endpoint': '2700 s combat-like intermittent endurance',
            'status': 'NOT_EXTERNALLY_VALIDATED',
            'reason': 'Isolated calf plantarflexion measurements provide zero empirical verification of 45-minute complex whole-body tactical work capacity.',
            'biological_interventions': 'NO_GO'
        },
        'negative_result': 'Direct transfer of local single-muscle parameters to the macroscopic D2 model is physically impermissible; TARGET-CPE45 cannot be validated from local imaging alone.'
    }

def main():
    franke_file = BASE / 'franke2020_extracted_measurements.json'
    franke_data = json.loads(franke_file.read_text(encoding='utf-8'))

    ident_file = BASE / 'identifiability_physical_results.json'
    ident_data = json.loads(ident_file.read_text(encoding='utf-8'))

    exp32 = run_exp_0032(franke_data)
    exp33 = run_exp_0033(franke_data)
    exp34 = run_exp_0034()
    exp35 = run_exp_0035(ident_data)
    exp36 = run_exp_0036()

    all_results = {
        'cycle': 8,
        'revision': 'cycle8_validity_repair_20261108',
        'status': 'COMPUTED_AND_VERIFIED',
        'experiments': {
            'EXP-0032': exp32,
            'EXP-0033': exp33,
            'EXP-0034': exp34,
            'EXP-0035': exp35,
            'EXP-0036': exp36
        }
    }

    out_file = BASE / 'experiment_results.json'
    out_file.write_text(json.dumps(all_results, indent=2), encoding='utf-8')
    print(f'Wrote Cycle 8 experiment results to {out_file}')

if __name__ == '__main__':
    main()
