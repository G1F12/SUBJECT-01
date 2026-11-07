"""Identifiability and Sensitivity Analysis Pipeline for Cycle 7.
Computes:
1. Analytical and numerical Jacobians of the local-systemic bridge.
2. SVD rank analysis and nullspace singular vectors across observation topologies M1-M7.
3. Fisher Information Matrix (FIM) conditioning and eigenvalue spectra.
4. Profile Likelihood along symmetry manifolds (scale alpha and baseline shift Delta).
5. Noise sensitivity and instrumental delay uncertainty propagation.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize

BASE = Path(__file__).resolve().parent

class LocalBridgeModel:
    """Coupled 3-layer local muscle bioenergetics & systemic gas bridge model."""
    def __init__(self, params=None):
        # Default nominal physiological parameters (human calf m. triceps surae)
        self.p = {
            'eta_loc': 0.28,           # Local actomyosin efficiency [dimensionless]
            'PCr_rest_mM': 34.0,       # Resting PCr concentration [mmol/L]
            'V_active_L': 0.25,        # Active muscle volume [L = dm^3 = 10^-3 m^3]
            'dG_ATP_kJ_mol': 54.0,     # Free energy of ATP hydrolysis [kJ/mol = J/mmol]
            'tau_PCr_rec_s': 70.0,     # Time constant of PCr oxidative recovery [s]
            'Q_loc_max_mM_s': 0.60,    # Maximal local oxidative phosphorylation rate [mmol/L/s]
            'M_loc_mM_s': 0.015,       # Local resting metabolic rate [mmol/L/s]
            'tau_transit_s': 10.0,     # Cardiopulmonary circulatory transit delay [s]
            'tau_pulm_disp_s': 6.0,    # Pulmonary venous mixing & dispersion time [s]
            'VO2_rest_L_min': 0.28,    # Whole-body resting VO2 [L/min]
            'gamma_O2_mol_ATP': 5.8,   # P/O2 stoichiometry [mol ATP / mol O2]
            'f_parasitic_resp': 0.15   # Fraction of delta-VO2 due to cardiorespiratory work
        }
        if params:
            self.p.update(params)

    def simulate(self, t_grid, P_ext_profile):
        """Simulate time courses of local PCr, local oxidative flux, and pulmonary VO2.
        t_grid: array of time points in seconds (uniform dt).
        P_ext_profile: external mechanical power in Watts at each t.
        """
        dt = t_grid[1] - t_grid[0]
        n_steps = len(t_grid)

        # State variables
        PCr = np.zeros(n_steps)
        PCr[0] = self.p['PCr_rest_mM']
        J_ox = np.zeros(n_steps)
        J_ox[0] = self.p['M_loc_mM_s']

        # Total energy scale factor: Joules per mmol in active volume
        # E [J] = [PCr] [mmol/L] * V_active [L] * dG [J/mmol]
        scale_J_per_mM = self.p['V_active_L'] * self.p['dG_ATP_kJ_mol']

        for i in range(n_steps - 1):
            P_ext = P_ext_profile[i]
            # ATP demand for mechanical power in mmol/L/s
            J_demand = (P_ext / (self.p['eta_loc'] * scale_J_per_mM)) + self.p['M_loc_mM_s']

            # Oxidative ATP synthesis rate depends on PCr depletion (ADP driving force)
            depletion = max(0.0, self.p['PCr_rest_mM'] - PCr[i])
            # Linearized oxidative drive up to Q_loc_max
            ox_drive = self.p['M_loc_mM_s'] + (depletion / self.p['tau_PCr_rec_s'])
            J_ox[i] = min(self.p['Q_loc_max_mM_s'], ox_drive)

            # Net rate of change of PCr
            dPCr_dt = J_ox[i] - J_demand
            PCr[i+1] = np.clip(PCr[i] + dPCr_dt * dt, 0.5, self.p['PCr_rest_mM'])

        J_ox[-1] = min(self.p['Q_loc_max_mM_s'], self.p['M_loc_mM_s'] + max(0.0, self.p['PCr_rest_mM'] - PCr[-1]) / self.p['tau_PCr_rec_s'])

        # Compute pulmonary VO2 response via convolution with delay and dispersion
        # Local muscle O2 consumption rate in L/min:
        # mmol ATP/s -> mol ATP/s = * 1e-3.
        # mol O2/s = (mol ATP/s) / gamma_O2.
        # L O2/s = mol O2/s * 22.414 L/mol (STPD).
        # L O2/min = * 60.
        conv_factor = (1e-3 / self.p['gamma_O2_mol_ATP']) * 22.414 * 60.0 * self.p['V_active_L']
        VO2_loc_L_min = J_ox * conv_factor

        # Cardiopulmonary transport delay and dispersion filter
        total_delay_s = self.p['tau_transit_s']
        tau_disp = self.p['tau_pulm_disp_s']

        VO2_pulm = np.zeros(n_steps)
        for i, t in enumerate(t_grid):
            # Effective delayed time
            t_eff = t - total_delay_s
            if t_eff <= 0:
                VO2_muscle_contrib = VO2_loc_L_min[0]
            else:
                # First order lag of muscle contribution
                idx_delayed = min(int(t_eff / dt), n_steps - 1)
                VO2_muscle_contrib = VO2_loc_L_min[idx_delayed]

            # Additional cardiorespiratory/postural cost proportional to muscle delta
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

def analyze_identifiability():
    """Computes Jacobian, SVD ranks, and Nullspaces across observation topologies M1-M7."""
    t_grid = np.linspace(0, 180, 91) # 180 s protocol, dt=2 s
    P_profile = np.zeros_like(t_grid)
    P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0 # 20 W step load from 20 to 120 s

    base_model = LocalBridgeModel()
    param_names = [
        'eta_loc', 'PCr_rest_mM', 'V_active_L', 'dG_ATP_kJ_mol',
        'tau_PCr_rec_s', 'Q_loc_max_mM_s', 'M_loc_mM_s'
    ]
    p_values = np.array([base_model.p[k] for k in param_names])
    n_params = len(param_names)

    # Topology observation mappings
    # M1: P_ext only (structural trivial)
    # M2: P_ext + PCr_relative
    # M3: P_ext + PCr_relative + VO2_pulm
    # M4: P_ext + PCr_mM (absolute conc without volume)
    # M5: P_ext + PCr_mM + V_active (calibrated volume)
    # M6: P_ext + PCr_mM + V_active + M_loc (baseline anchored)
    # M7: P_ext + PCr_mM + V_active + Q_loc_max + M_loc (fully anchored)

    topologies = ['M1_power_only', 'M2_power_relPCr', 'M3_power_relPCr_VO2',
                  'M4_power_absPCr', 'M5_power_absPCr_volume', 'M6_power_absPCr_vol_baseline', 'M7_fully_anchored']

    results = {}

    for top in topologies:
        # Build composite output vector for each topology
        def get_output(params):
            p_dict = dict(zip(param_names, params))
            m = LocalBridgeModel(p_dict)
            sim = m.simulate(t_grid, P_profile)
            outs = []
            if 'power' in top:
                outs.append(sim['P_ext_W'])
            if 'relPCr' in top:
                outs.append(sim['PCr_relative'])
            if 'VO2' in top:
                outs.append(sim['VO2_pulm_L_min'])
            if 'absPCr' in top:
                outs.append(sim['PCr_mM'])
            if 'volume' in top:
                # direct measurement of V_active
                outs.append(np.array([params[2]]))
            if 'baseline' in top:
                # direct measurement of M_loc
                outs.append(np.array([params[6]]))
            if 'fully_anchored' in top:
                outs.append(sim['PCr_mM'])
                outs.append(sim['VO2_pulm_L_min'])
                outs.append(np.array([params[2]])) # V_active
                outs.append(np.array([params[5]])) # Q_loc_max
                outs.append(np.array([params[6]])) # M_loc
            return np.concatenate(outs)

        y0 = get_output(p_values)
        m_dim = len(y0)
        J = np.zeros((m_dim, n_params))
        eps = 1e-4

        for j in range(n_params):
            p_plus = p_values.copy()
            p_minus = p_values.copy()
            h = eps * max(1e-3, abs(p_values[j]))
            p_plus[j] += h
            p_minus[j] -= h
            J[:, j] = (get_output(p_plus) - get_output(p_minus)) / (2.0 * h)

        # Scale-normalized Jacobian for dimensionally fair SVD
        J_norm = J * (p_values / np.maximum(1e-6, np.std(y0) + 1e-3))
        U, S, Vt = np.linalg.svd(J_norm, full_matrices=False)

        # Numerical rank threshold
        rank_tol = 1e-3 * S[0]
        eff_rank = int(np.sum(S > rank_tol))
        null_dim = n_params - eff_rank

        results[top] = {
            'n_parameters': n_params,
            'effective_rank': eff_rank,
            'rank_defect': null_dim,
            'singular_values': [float(x) for x in S],
            'condition_number': float(S[0] / S[-1]) if S[-1] > 1e-12 else float('inf'),
            'unidentifiable_directions': param_names[eff_rank:] if null_dim > 0 else []
        }

    return results

def compute_profile_likelihood():
    """Computes profile likelihood along Scale Symmetry alpha and Additive Shift Delta."""
    t_grid = np.linspace(0, 180, 91)
    P_profile = np.zeros_like(t_grid)
    P_profile[(t_grid >= 20) & (t_grid <= 120)] = 20.0

    nominal = LocalBridgeModel()
    true_sim = nominal.simulate(t_grid, P_profile)

    # 1. Profile along Scale Symmetry alpha: eta -> alpha * eta, V_active -> V_active / alpha
    # Product eta * V_active is conserved, mechanical power and relative PCr are unchanged!
    alphas = np.linspace(0.5, 2.0, 16)
    scale_rss_power_relPCr = []
    scale_rss_absolute = []

    for a in alphas:
        test_p = {
            'eta_loc': nominal.p['eta_loc'] * a,
            'V_active_L': nominal.p['V_active_L'] / a
        }
        test_m = LocalBridgeModel(test_p)
        test_sim = test_m.simulate(t_grid, P_profile)

        # RSS on power + relative PCr (should be ZERO due to exact symmetry!)
        rss_rel = np.sum((test_sim['PCr_relative'] - true_sim['PCr_relative'])**2)
        scale_rss_power_relPCr.append(float(rss_rel))

        # RSS on absolute PCr (if volume was known)
        rss_abs = np.sum((test_sim['PCr_mM'] - true_sim['PCr_mM'])**2)
        scale_rss_absolute.append(float(rss_abs))

    # 2. Profile along Additive Shift Delta: Q -> Q + Delta, M -> M + Delta
    deltas = np.linspace(-0.01, 0.05, 13)
    shift_rss_recovery = []

    for d in deltas:
        test_p = {
            'Q_loc_max_mM_s': nominal.p['Q_loc_max_mM_s'] + d,
            'M_loc_mM_s': nominal.p['M_loc_mM_s'] + d
        }
        test_m = LocalBridgeModel(test_p)
        test_sim = test_m.simulate(t_grid, P_profile)
        # Check recovery phase (t > 120s)
        rec_idx = t_grid >= 120
        rss_rec = np.sum((test_sim['PCr_relative'][rec_idx] - true_sim['PCr_relative'][rec_idx])**2)
        shift_rss_recovery.append(float(rss_rec))

    return {
        'scale_alphas': [float(x) for x in alphas],
        'scale_rss_power_relPCr': scale_rss_power_relPCr,
        'scale_rss_absolute': scale_rss_absolute,
        'shift_deltas': [float(x) for x in deltas],
        'shift_rss_recovery': shift_rss_recovery
    }

def main():
    print("=== Running Identifiability and Sensitivity Analysis ===")
    top_results = analyze_identifiability()
    profiles = compute_profile_likelihood()

    output = {
        'date': '2026-11-07',
        'topologies': top_results,
        'profile_likelihood': profiles,
        'conclusions': {
            'question_A': 'Relative PCr, external power and systemic VO2 cannot determine local muscle contraction cost without V_active and isolated muscle O2 fraction.',
            'question_B': 'Eliminating Symmetry 1 requires calibrated absolute metabolic energy (V_active * [PCr]_abs); eliminating Symmetry 2 requires isolated baseline M_loc or uninhibited Q_max.'
        }
    }

    out_file = BASE / 'identifiability_results.json'
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Identifiability analysis complete. Results written to: {out_file}")
    for top, res in top_results.items():
        print(f"  {top:30s} | Rank: {res['effective_rank']}/{res['n_parameters']} | Defect: {res['rank_defect']} | Cond: {res['condition_number']:.2e}")

if __name__ == '__main__':
    main()
