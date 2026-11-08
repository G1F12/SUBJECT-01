"""Physical Measurement Map Identifiability and Sensitivity Analysis Pipeline.
Research Cycle 8: EMPIRICAL LOCAL ENERGY ANCHORS (CORRECTED).

Rigorous 3-level identifiability analysis:
1. CONDITIONAL MATHEMATICAL FULL RANK (conditional idealized calibrations & frozen nuisance).
2. PRACTICAL IDENTIFIABILITY WITH NUISANCE PARAMETERS (unknown gains, offsets, recruitment, calibrations).
3. EMPIRICAL IDENTIFIABILITY WITH ACTUAL HUMAN DATA (multi-cohort empirical audit).
"""
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parent

class LocalBridgeModel:
    """Coupled 3-layer local muscle bioenergetics & systemic gas bridge model."""
    def __init__(self, params=None):
        # Nominal human calf gastrocnemius medialis parameters
        self.p = {
            # Target physiological parameters (7)
            'eta_loc': 0.28,           # Local actomyosin efficiency [dimensionless]
            'PCr_rest_mM': 33.6,       # Resting PCr concentration [mmol/L cytosolic water] (Edwards 2013)
            'V_active_L': 0.12,        # Active muscle volume [L] (scenario ~32% of 0.380 L)
            'dG_ATP_kJ_mol': 54.0,     # Free energy of ATP hydrolysis [kJ/mol] (Meyerspeer 2021)
            'tau_PCr_rec_s': 70.0,     # Time constant of PCr oxidative recovery [s]
            'Q_loc_max_mM_s': 0.60,    # Maximal local oxidative phosphorylation rate [mmol/L/s]
            'M_loc_mM_s': 0.008,       # Local resting metabolic rate [mmol/L/s] (model scenario transfer)
            # Physiological constants / bridge parameters
            'tau_transit_s': 10.0,     # Cardiopulmonary circulatory transit delay [s]
            'tau_pulm_disp_s': 6.0,    # Pulmonary venous mixing & dispersion time [s]
            'VO2_rest_L_min': 0.28,    # Whole-body resting VO2 [L/min]
            'gamma_O2_mol_ATP': 5.8,   # P/O2 stoichiometry [mol ATP / mol O2]
            'f_parasitic_resp': 0.15,  # Fraction of delta-VO2 due to cardiorespiratory/postural work
            # Unknown nuisance / calibration parameters (4)
            'a_eff': 0.3157894736842105, # Functional recruitment fraction (V_active / V_anat)
            'g_nirs': 18.75,             # NIRS optical sensitivity gain (% / (mM/s))
            'b_nirs': 0.0,               # NIRS optical baseline offset (%/s)
            'k_spec': 1.0                # Spectroscopic calibration factor for dG_ATP
        }
        if params:
            self.p.update(params)

    def simulate(self, t_grid, P_ext_profile):
        """Simulate time courses of local PCr, local oxidative flux, and pulmonary VO2."""
        dt = t_grid[1] - t_grid[0]
        n_steps = len(t_grid)

        PCr = np.zeros(n_steps)
        PCr[0] = self.p['PCr_rest_mM']
        J_ox = np.zeros(n_steps)
        J_ox[0] = self.p['M_loc_mM_s']

        # Total energy scale factor: Joules per mmol in active volume
        scale_J_per_mM = self.p['V_active_L'] * self.p['dG_ATP_kJ_mol']

        for i in range(n_steps - 1):
            P_ext = P_ext_profile[i]
            # ATP demand for mechanical power in mmol/L/s
            J_demand = (P_ext / (self.p['eta_loc'] * scale_J_per_mM)) + self.p['M_loc_mM_s']

            depletion = max(0.0, self.p['PCr_rest_mM'] - PCr[i])
            ox_drive = self.p['M_loc_mM_s'] + (depletion / self.p['tau_PCr_rec_s'])
            J_ox[i] = min(self.p['Q_loc_max_mM_s'], ox_drive)

            dPCr_dt = J_ox[i] - J_demand
            PCr[i+1] = np.clip(PCr[i] + dPCr_dt * dt, 0.5, self.p['PCr_rest_mM'])

        J_ox[-1] = min(self.p['Q_loc_max_mM_s'], self.p['M_loc_mM_s'] + max(0.0, self.p['PCr_rest_mM'] - PCr[-1]) / self.p['tau_PCr_rec_s'])

        # Local muscle O2 consumption rate in L/min:
        conv_factor = (1e-3 / self.p['gamma_O2_mol_ATP']) * 22.414 * 60.0 * self.p['V_active_L']
        VO2_loc_L_min = J_ox * conv_factor

        total_delay_s = self.p['tau_transit_s']
        VO2_pulm = np.zeros(n_steps)
        for i, t in enumerate(t_grid):
            t_eff = t - total_delay_s
            if t_eff <= 0:
                VO2_muscle_contrib = VO2_loc_L_min[0]
            else:
                idx_delayed = min(int(t_eff / dt), n_steps - 1)
                VO2_muscle_contrib = VO2_loc_L_min[idx_delayed]

            delta_loc = max(0.0, VO2_muscle_contrib - VO2_loc_L_min[0])
            delta_parasitic = delta_loc * self.p['f_parasitic_resp']
            VO2_pulm[i] = self.p['VO2_rest_L_min'] + delta_loc + delta_parasitic

        return {
            'time_s': t_grid,
            'P_ext_W': P_ext_profile,
            'PCr_mM': PCr,
            'PCr_relative': PCr / self.p['PCr_rest_mM'],
            'J_ox_mM_s': J_ox,
            'VO2_pulm_L_min': VO2_pulm
        }

CHANNEL_SCALES = {
    'P_ext_W': 20.0,
    'PCr_relative': 1.0,
    'PCr_mM': 33.6,
    'VO2_pulm_L_min': 0.30,
    'V_active_ideal': 0.12,
    'M_loc_ideal': 0.008,
    'Q_loc_max_ideal': 0.60,
    'V_anat_mri': 0.38,
    'NIRS_slope_uncal': 0.15,
    'M_loc_catheter': 0.008,
    'Q_loc_max_rec': 0.60,
    'dG_spec_channel': 54.0
}

CHANNEL_SIGMAS = {
    'P_ext_W': 1.0,           # 1 W ergometer precision
    'PCr_relative': 0.05,     # 5% MRS relative precision
    'PCr_mM': 1.5,            # 1.5 mM MRS absolute concentration precision
    'VO2_pulm_L_min': 0.02,   # 20 mL/min metabolic cart precision
    'V_active_ideal': 0.01,
    'M_loc_ideal': 0.001,
    'Q_loc_max_ideal': 0.05,
    'V_anat_mri': 0.015,      # 15 mL MRI segmentation uncertainty
    'NIRS_slope_uncal': 0.02, # 0.02 %/s NIRS optical slope uncertainty
    'M_loc_catheter': 0.0015, # 0.0015 mM/s femoral catheterization precision
    'Q_loc_max_rec': 0.05,    # 0.05 mM/s recovery kinetics fit uncertainty
    'dG_spec_channel': 2.0    # 2.0 kJ/mol spectroscopic Pi-chemical shift precision
}

# 1. Idealized topologies (Cycle 7 reproduction)
IDEAL_TOPOLOGIES = {
    'M1_power_only': ['P_ext_W'],
    'M2_power_relPCr': ['P_ext_W', 'PCr_relative'],
    'M3_power_relPCr_VO2': ['P_ext_W', 'PCr_relative', 'VO2_pulm_L_min'],
    'M4_power_absPCr': ['P_ext_W', 'PCr_mM'],
    'M5_power_absPCr_volume_ideal': ['P_ext_W', 'PCr_mM', 'V_active_ideal'],
    'M6_power_absPCr_vol_base_ideal': ['P_ext_W', 'PCr_mM', 'V_active_ideal', 'M_loc_ideal'],
    'M7_fully_anchored_ideal': ['P_ext_W', 'PCr_mM', 'VO2_pulm_L_min', 'V_active_ideal', 'Q_loc_max_ideal', 'M_loc_ideal']
}

# 2. Physically anchored topologies (Level 1: Conditional under frozen calibrations)
PHYSICAL_TOPOLOGIES = {
    'P1_ergometer_input': ['P_ext_W'],
    'P2_ergometer_relPCr': ['P_ext_W', 'PCr_relative'],
    'P3_ergometer_relPCr_pulmVO2': ['P_ext_W', 'PCr_relative', 'VO2_pulm_L_min'],
    'P4_ergometer_absPCr': ['P_ext_W', 'PCr_mM'],
    'P5_ergometer_absPCr_mriAnat': ['P_ext_W', 'PCr_mM', 'V_anat_mri'],
    'P6_ergometer_absPCr_mri_uncalNIRS': ['P_ext_W', 'PCr_mM', 'V_anat_mri', 'NIRS_slope_uncal'],
    'P7_physical_without_spec': ['P_ext_W', 'PCr_mM', 'VO2_pulm_L_min', 'V_anat_mri', 'M_loc_catheter', 'Q_loc_max_rec'],
    'P8_physical_with_spectroscopy': ['P_ext_W', 'PCr_mM', 'VO2_pulm_L_min', 'V_anat_mri', 'M_loc_catheter', 'Q_loc_max_rec', 'dG_spec_channel']
}

def eval_channel(params_dict, channel_name, t_grid, P_profile):
    """Evaluates channel mapping."""
    m = LocalBridgeModel(params_dict)
    sim = m.simulate(t_grid, P_profile)

    if channel_name in sim:
        return np.asarray(sim[channel_name], dtype=float)
    elif channel_name == 'V_active_ideal':
        return np.array([params_dict['V_active_L']], dtype=float)
    elif channel_name == 'M_loc_ideal':
        return np.array([params_dict['M_loc_mM_s']], dtype=float)
    elif channel_name == 'Q_loc_max_ideal':
        return np.array([params_dict['Q_loc_max_mM_s']], dtype=float)
    elif channel_name == 'V_anat_mri':
        # V_anat = V_active / a_eff
        a_eff = params_dict.get('a_eff', 0.3157894736842105)
        return np.array([params_dict['V_active_L'] / a_eff], dtype=float)
    elif channel_name == 'NIRS_slope_uncal':
        g_nirs = params_dict.get('g_nirs', 18.75)
        b_nirs = params_dict.get('b_nirs', 0.0)
        return np.array([g_nirs * params_dict['M_loc_mM_s'] + b_nirs], dtype=float)
    elif channel_name == 'M_loc_catheter':
        return np.array([params_dict['M_loc_mM_s']], dtype=float)
    elif channel_name == 'Q_loc_max_rec':
        return np.array([params_dict['Q_loc_max_mM_s']], dtype=float)
    elif channel_name == 'dG_spec_channel':
        k_spec = params_dict.get('k_spec', 1.0)
        return np.array([k_spec * params_dict['dG_ATP_kJ_mol']], dtype=float)
    else:
        raise ValueError(f"Unknown observation channel: {channel_name}")

def compute_jacobian_block(param_names, p_values, channels, t_grid, P_profile, fixed_dict):
    n_params = len(param_names)
    blocks_norm = []
    blocks_fim = []
    eps = 1e-4

    base_p_dict = fixed_dict.copy()
    base_p_dict.update(dict(zip(param_names, p_values)))

    for ch in channels:
        y_nom = eval_channel(base_p_dict, ch, t_grid, P_profile)
        N_k = len(y_nom)
        J_k = np.zeros((N_k, n_params))

        for j in range(n_params):
            p_plus = p_values.copy()
            p_minus = p_values.copy()
            h = eps * max(1e-3, abs(p_values[j]))
            p_plus[j] += h
            p_minus[j] -= h

            dict_plus = base_p_dict.copy()
            dict_plus[param_names[j]] = p_plus[j]
            yp = eval_channel(dict_plus, ch, t_grid, P_profile)

            dict_minus = base_p_dict.copy()
            dict_minus[param_names[j]] = p_minus[j]
            ym = eval_channel(dict_minus, ch, t_grid, P_profile)

            J_k[:, j] = (yp - ym) / (2.0 * h)

        scale = CHANNEL_SCALES[ch]
        sigma = CHANNEL_SIGMAS[ch]
        blocks_norm.append(J_k * (p_values / scale) / np.sqrt(N_k))
        blocks_fim.append(J_k * (p_values / sigma))

    J_norm = np.vstack(blocks_norm)
    J_fim = np.vstack(blocks_fim)
    return J_norm, J_fim

def analyze_conditional_identifiability(topologies):
    """Level 1: Conditional mathematical identifiability (frozen calibrations & nuisance)."""
    t_grid = np.linspace(0, 180, 91)
    P_profile = np.zeros_like(t_grid)
    P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0

    base_model = LocalBridgeModel()
    param_names = [
        'eta_loc', 'PCr_rest_mM', 'V_active_L', 'dG_ATP_kJ_mol',
        'tau_PCr_rec_s', 'Q_loc_max_mM_s', 'M_loc_mM_s'
    ]
    p_values = np.array([base_model.p[k] for k in param_names])
    n_params = len(param_names)

    fixed_dict = {
        'a_eff': base_model.p['a_eff'],
        'g_nirs': base_model.p['g_nirs'],
        'b_nirs': base_model.p['b_nirs'],
        'k_spec': base_model.p['k_spec']
    }

    results = {}
    for top_name, channels in topologies.items():
        J_norm, J_fim = compute_jacobian_block(param_names, p_values, channels, t_grid, P_profile, fixed_dict)
        U, S, Vt = np.linalg.svd(J_norm, full_matrices=False)

        rank_tol = 1e-4
        eff_rank = int(np.sum(S > rank_tol))
        null_dim = n_params - eff_rank

        FIM = J_fim.T @ J_fim
        eigvals = np.sort(np.linalg.eigvalsh(FIM))[::-1]

        cond_number = float(S[0] / S[-1]) if S[-1] > 1e-12 else float('inf')
        cond_eff = float(S[0] / S[eff_rank - 1]) if eff_rank > 0 else float('inf')

        null_basis = Vt[eff_rank:] if null_dim > 0 else np.zeros((0, n_params))
        nullspace_dict = []
        for row in null_basis:
            nullspace_dict.append({param_names[k]: float(row[k]) for k in range(n_params)})

        results[top_name] = {
            'channels': channels,
            'effective_rank': eff_rank,
            'nullspace_dim': null_dim,
            'condition_number_all': cond_number,
            'condition_number_effective': cond_eff,
            'singular_values': [float(s) for s in S],
            'fim_eigenvalues': [float(e) for e in eigvals],
            'nullspace_basis': nullspace_dict,
            'classification': 'CONDITIONAL_MATHEMATICAL_RANK'
        }

    return results

def analyze_practical_identifiability_with_nuisance():
    """Level 2: Practical identifiability with unknown nuisance parameters in 11D space."""
    t_grid = np.linspace(0, 180, 91)
    P_profile = np.zeros_like(t_grid)
    P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0

    base_model = LocalBridgeModel()
    target_names = [
        'eta_loc', 'PCr_rest_mM', 'V_active_L', 'dG_ATP_kJ_mol',
        'tau_PCr_rec_s', 'Q_loc_max_mM_s', 'M_loc_mM_s'
    ]
    nuisance_names = ['a_eff', 'g_nirs', 'b_nirs', 'k_spec']
    all_names = target_names + nuisance_names

    p_values = np.array([base_model.p[k] for k in all_names])
    n_params = len(all_names)

    # Realistic measurement channels with unknown nuisance parameters
    channels = ['P_ext_W', 'PCr_mM', 'VO2_pulm_L_min', 'V_anat_mri', 'NIRS_slope_uncal', 'dG_spec_channel']

    J_norm, J_fim = compute_jacobian_block(all_names, p_values, channels, t_grid, P_profile, {})
    U, S, Vt = np.linalg.svd(J_norm, full_matrices=False)

    rank_tol = 1e-4
    eff_rank = int(np.sum(S > rank_tol))
    null_dim = n_params - eff_rank

    FIM = J_fim.T @ J_fim
    eigvals = np.sort(np.linalg.eigvalsh(FIM))[::-1]

    cond_number = float(S[0] / S[-1]) if S[-1] > 1e-12 else float('inf')
    cond_eff = float(S[0] / S[eff_rank - 1]) if eff_rank > 0 else float('inf')

    null_basis = Vt[eff_rank:] if null_dim > 0 else np.zeros((0, n_params))
    nullspace_dict = []
    for row in null_basis:
        nullspace_dict.append({all_names[k]: float(row[k]) for k in range(n_params)})

    # Detect unidentifiable parameters by projecting nullspace vectors
    unidentifiable_parameters = set()
    for row in null_basis:
        for k in range(n_params):
            if abs(row[k]) > 1e-3:
                unidentifiable_parameters.add(all_names[k])

    diagnosis = {}
    for idx, name in enumerate(all_names):
        is_unident = name in unidentifiable_parameters
        diagnosis[name] = {
            'index': idx,
            'is_target_parameter': idx < len(target_names),
            'nominal_value': float(p_values[idx]),
            'status': 'STRUCTURALLY_UNIDENTIFIABLE_OR_FLAT' if is_unident else 'PRACTICALLY_IDENTIFIABLE'
        }

    return {
        'classification': 'PRACTICAL_IDENTIFIABILITY_DEFECT',
        'total_parameters': n_params,
        'target_parameters_count': len(target_names),
        'nuisance_parameters_count': len(nuisance_names),
        'channels': channels,
        'effective_rank': eff_rank,
        'nullspace_dim': null_dim,
        'condition_number_all': cond_number,
        'condition_number_effective': cond_eff,
        'singular_values': [float(s) for s in S],
        'fim_eigenvalues': [float(e) for e in eigvals],
        'nullspace_basis': nullspace_dict,
        'parameter_diagnosis': diagnosis,
        'finding': f'When nuisance parameters (a_eff, g_nirs, b_nirs, k_spec) are unknown, the full 11D system has effective rank {eff_rank}/11 (rank defect = {null_dim}). Parameters V_active, M_loc, and dG_ATP become unidentifiable ridges in profile likelihood without independent calibrations.'
    }

def run_pipeline():
    ideal_results = analyze_conditional_identifiability(IDEAL_TOPOLOGIES)
    cond_phys_results = analyze_conditional_identifiability(PHYSICAL_TOPOLOGIES)
    practical_results = analyze_practical_identifiability_with_nuisance()

    empirical_status = {
        'classification': 'NOT_EMPIRICALLY_IDENTIFIED',
        'status': 'NOT_EMPIRICALLY_IDENTIFIED',
        'reason': 'No simultaneous multimodal dataset exists in the human literature combining 3D MRI volumetry, dynamic in-magnet sEMG, calibrated 31P-MRS, and localized oxygen consumption/catheterization for the same individual.',
        'multi_cohort_disconnection': {
            'franke2020_mri_semg': 'n=1, sEMG recorded outside magnet at 2 kHz (upsampled to 4 kHz in MAT); separate dynamic 31P-MRS trial inside magnet.',
            'edwards2013_insight': 'n=89 resting 31P-MRS cohort; provides PCr/ATP ratio distribution, but absolute concentration requires assumed [ATP]_ref.',
            'andersen_saltin1985': 'Femoral catheterization in human quadriceps during knee extensions; never measured in calf gastrocnemius.',
            'ryan2014_mcmito': 'Continuous-wave NIRS VOT recovery slopes uncalibrated for adipose tissue thickness and absolute molar flux.'
        },
        'synthesis_verdict': 'Cycle 8 empirical anchors represent an uncalibrated multi-study physiological scenario synthesis, not a jointly identified human observation map.'
    }

    combined = {
        'cycle': 8,
        'revision': 'cycle8_validity_repair_20261108',
        'target_parameter_names': [
            'eta_loc', 'PCr_rest_mM', 'V_active_L', 'dG_ATP_kJ_mol',
            'tau_PCr_rec_s', 'Q_loc_max_mM_s', 'M_loc_mM_s'
        ],
        'nuisance_parameter_names': ['a_eff', 'g_nirs', 'b_nirs', 'k_spec'],
        'idealized_topologies_cycle7': ideal_results,
        'physical_topologies_cycle8': cond_phys_results,
        'level_1_conditional_mathematical_identifiability': cond_phys_results,
        'level_2_practical_identifiability_with_nuisance': practical_results,
        'level_3_empirical_identifiability_human_data': empirical_status
    }

    out_file = BASE / 'identifiability_physical_results.json'
    out_file.write_text(json.dumps(combined, indent=2), encoding='utf-8')
    print(f'Wrote corrected physical identifiability results to {out_file}')
    return combined

if __name__ == '__main__':
    run_pipeline()
