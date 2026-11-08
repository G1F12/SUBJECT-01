"""Cycle 7 Experimental Suite & Scientific Audit Verification.
Audits and verifies:
- EXP-0027: PCr recovery kinetics, acidosis coupling, asymptote sensitivity and multi-pool bias.
- EXP-0028: Pulmonary oxygen kinetics, 4-component transport delay and inseparability.
- EXP-0029: Local-systemic coupling, bicarbonate excess CO2, and scenario-based parasitic cost bounds.
- EXP-0030: Absolute metabolic energy scale, PCr buffer capacity vs 180s ATP turnover, and volume ambiguity.
- EXP-0031: Retraction and audit of mechanical power prediction comparison (N=2, hardcoded values).

SCIENTIFIC AUDIT DIRECTIVE:
- Do NOT claim unverified eyeball points as new empirical correlations.
- Published literature benchmarks (Moll et al. 2017: R2=0.73, R2=0.55, R2=0.65) are cited with primary attribution.
- The 66.3% cardiorespiratory/postural cost is treated as a SCENARIO CALCULATION, not an empirical measurement.
- PCr chemical reserve (205-1021 J) is strictly separated from 180s cumulative ATP turnover (>11,000 J).
- EXP-0031 predictive claims (RMSE 0.65 W) are RETRACTED due to hardcoded predictions, in-sample baseline, and N=2.
"""
from pathlib import Path
import json
import numpy as np
from scipy.stats import pearsonr

BASE = Path(__file__).resolve().parent

def load_moll_data():
    p = BASE / 'moll2018_extracted_measurements.json'
    return json.loads(p.read_text('utf-8'))

# ============================================================================
# EXP-A (EXP-0027): PCr Recovery Kinetics, Acidosis Coupling and Asymptote Sensitivity
# ============================================================================
def run_exp_a(data):
    ch3 = data['moll2017_chapter3_combined_study']
    published_corr = ch3['published_statistical_correlations']['tau_PCr_fast_vs_pH_end']
    approx_data = ch3['approximate_graphical_digitization_fig3_5']
    points = approx_data['estimated_points']

    # 1. Audit of approximate graphical digitization points
    pH_approx = np.array([pt['pH_end_est'] for pt in points])
    tau_approx = np.array([pt['tau_PCr_fast_s_est'] for pt in points])
    r_approx, p_approx = pearsonr(pH_approx, tau_approx)
    r2_approx = float(r_approx**2)

    # Note: r2_approx ~ 0.919 is an artifact of placing points smoothly along the regression line
    # in Fig 3-5, whereas the true published peer-reviewed R2 is 0.73 (p < 0.005).

    # 2. Mathematical sensitivity to baseline resting asymptote (+/- 5%)
    # Mono-exponential recovery: [PCr](t) = PCr_rest - Delta * exp(-t / tau)
    # Normalized: y(t) = 1 - (1 - y0) * exp(-t / tau_true)
    tau_true = 70.0
    t = np.linspace(0, 200, 101)
    y_true = 1.0 - 0.8 * np.exp(-t / tau_true)

    asymptote_errors = [-0.05, -0.02, 0.0, 0.02, 0.05]
    tau_fitted = []
    for err in asymptote_errors:
        y_assumed_rest = 1.0 + err
        # Invert linearized log: ln((y_assumed_rest - y(t)) / (y_assumed_rest - y0)) = -t / tau
        num = np.maximum(1e-4, y_assumed_rest - y_true)
        denom = y_assumed_rest - y_true[0]
        valid = (t > 10) & (t < 150)
        log_ratio = np.log(num[valid] / denom)
        slope, _ = np.polyfit(t[valid], log_ratio, 1)
        tau_est = -1.0 / slope
        tau_fitted.append(float(tau_est))

    tau_err_pct = [float((tau_est - tau_true) / tau_true * 100.0) for tau_est in tau_fitted]

    # 3. Spatial Heterogeneity & Multi-pool kinetics bias (from Chapter 5 NMES, 3 pools)
    # Pool 1 (38%): pH=6.22, tau=120s
    # Pool 2 (42%): pH=6.61, tau=75s
    # Pool 3 (20%): pH=6.94, tau=35s
    f1, tau1 = 0.38, 120.0
    f2, tau2 = 0.42, 75.0
    f3, tau3 = 0.20, 35.0
    t_rec = np.linspace(0, 300, 151)
    # Composite depleted PCr fraction
    pcr_depleted_composite = f1 * np.exp(-t_rec / tau1) + f2 * np.exp(-t_rec / tau2) + f3 * np.exp(-t_rec / tau3)
    # Fitting mono-exponential over early window (0-60s)
    early_idx = t_rec <= 60.0
    log_early = np.log(pcr_depleted_composite[early_idx])
    slope_mono, _ = np.polyfit(t_rec[early_idx], log_early, 1)
    tau_mono_early = float(-1.0 / slope_mono)
    harmonic_mean_tau = float(1.0 / (f1/tau1 + f2/tau2 + f3/tau3))
    heterogeneity_bias_pct = float(abs(tau_mono_early - harmonic_mean_tau) / harmonic_mean_tau * 100.0)

    return {
        'experiment_id': 'EXP-0027',
        'title': 'PCr Recovery Kinetics, Acidosis Coupling and Asymptote Sensitivity',
        'audit_verdict': 'RETRACTED_EMPIRICAL_DISCOVERY; CONFIRMED_COMPUTATIONAL_SENSITIVITY',
        'literature_published_benchmark': {
            'source': published_corr['source'],
            'R2': published_corr['R2'],
            'p_val': published_corr['p_val'],
            'finding': 'True peer-reviewed literature result: R2=0.73, p<0.005 for tau_PCr_fast vs end-exercise pH.'
        },
        'graphical_digitization_audit': {
            'R2_apparent': r2_approx,
            'p_val_apparent': float(p_approx),
            'bias_vs_literature': float(r2_approx - published_corr['R2']),
            'note': 'Apparent R2=0.919 was caused by manual graphical digitization error/placement bias and is RETRACTED as a scientific discovery.'
        },
        'asymptote_uncertainty_analysis': {
            'asymptote_errors_pct': [float(e*100) for e in asymptote_errors],
            'tau_fitted_s': tau_fitted,
            'tau_error_pct': tau_err_pct,
            'span_pct': [min(tau_err_pct), max(tau_err_pct)],
            'finding': f'A +/-5% error in baseline resting PCr asymptote distorts estimated tau_PCr by {min(tau_err_pct):.1f}% to +{max(tau_err_pct):.1f}%.'
        },
        'spatial_heterogeneity_simulation': {
            'true_pool_taus_s': [tau1, tau2, tau3],
            'pool_fractions': [f1, f2, f3],
            'early_mono_fit_tau_s': tau_mono_early,
            'harmonic_mean_tau_s': harmonic_mean_tau,
            'bias_pct': heterogeneity_bias_pct,
            'finding': f'Spatial fiber-type heterogeneity induces a {heterogeneity_bias_pct:.1f}% early recovery rate estimation bias when fitted with a mono-exponential model.'
        }
    }

# ============================================================================
# EXP-B (EXP-0028): Pulmonary Oxygen Kinetics, 4-Component Transport Delay & Collinearity
# ============================================================================
def run_exp_b(data):
    ch3 = data['moll2017_chapter3_combined_study']
    inst = ch3['instrumentation']

    # 4 physically distinct delay/filtering components
    delays = {
        't_sampling_line_delay_s': inst['line_delay_measured_ta_s'],        # 2.075 s
        't_sampling_line_dispersion_s': inst['line_dispersion_measured_t10_90_s'], # 0.307 s
        't_cardiopulmonary_transit_range_s': [10.0, 20.0],                  # 10-20 s venous transit
        'tau_muscle_activation_range_s': [20.0, 40.0]                       # 20-40 s mitochondrial tau
    }

    # Simulate collinearity in on-transient identification
    t_obs = np.linspace(0, 180, 181)
    tau_m_true = 30.0
    delay_true = 15.0 # composite circulatory transit + line delay
    noise_sigma = 0.04 # L/min breath-by-breath noise
    disp_s = 1.0 # Vascular and sampling line dispersion transition width

    def pulm_model(t, tau_m, td, s=disp_s):
        # Continuous dispersion response: sigmoidal vascular transit * exponential activation
        weight = 1.0 / (1.0 + np.exp(-(t - td) / s))
        resp = 1.0 - np.exp(-np.maximum(0.0, t - td) / tau_m)
        return weight * resp

    # Analytical / smooth Jacobian for Fisher Information Matrix
    eps = 1e-2
    p0 = np.array([tau_m_true, delay_true])
    J = np.zeros((len(t_obs), 2))
    J[:, 0] = (pulm_model(t_obs, p0[0] + eps, p0[1]) - pulm_model(t_obs, p0[0] - eps, p0[1])) / (2 * eps)
    J[:, 1] = (pulm_model(t_obs, p0[0], p0[1] + eps) - pulm_model(t_obs, p0[0], p0[1] - eps)) / (2 * eps)

    FIM = J.T @ J
    cov = np.linalg.inv(FIM)
    param_corr = float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1]))
    cond_number = float(np.linalg.cond(FIM))

    # Grid search for tau and delay on noisy synthetic realization
    np.random.seed(42)
    y_clean = pulm_model(t_obs, tau_m_true, delay_true)
    y_noisy = y_clean + np.random.normal(0, noise_sigma, len(t_obs))

    grid_tau = np.linspace(20.0, 40.0, 41)
    grid_td = np.linspace(10.0, 20.0, 41)
    rss_grid = np.zeros((len(grid_tau), len(grid_td)))

    for i, tm in enumerate(grid_tau):
        for j, td in enumerate(grid_td):
            pred = pulm_model(t_obs, tm, td)
            rss_grid[i, j] = np.sum((y_noisy - pred)**2)

    i_min, j_min = np.unravel_index(np.argmin(rss_grid), rss_grid.shape)
    best_tau = float(grid_tau[i_min])
    best_td = float(grid_td[j_min])

    return {
        'experiment_id': 'EXP-0028',
        'title': 'Pulmonary Oxygen Kinetics, 4-Component Transport Delay and Collinearity',
        'status': 'CONFIRMED_COMPUTATIONAL_IDENTIFIABILITY',
        'delay_components': delays,
        'collinearity_simulation': {
            'true_parameters': {'tau_muscle_s': tau_m_true, 'delay_s': delay_true},
            'fitted_parameters': {'best_tau_s': best_tau, 'best_delay_s': best_td},
            'delay_tau_correlation': param_corr,
            'FIM_condition_number': cond_number,
            'noise_sigma_L_min': noise_sigma,
            'finding': f'Circulatory transit delay and muscle oxidative time constant exhibit strong collinearity (r={param_corr:.3f}, cond={cond_number:.1f}); pulmonary on-transients cannot separate them without independent venous timing.'
        }
    }

# ============================================================================
# EXP-C (EXP-0029): Local-Systemic Coupling & Scenario Parasitic Cost Bounds
# ============================================================================
def run_exp_c(data):
    ch3 = data['moll2017_chapter3_combined_study']
    pub_corr = ch3['published_statistical_correlations']

    # 1. Literature peer-reviewed correlations (Moll et al. 2017)
    corr_pcr_vo2 = pub_corr['tau_VO2_fast_vs_tau_PCr_fast']
    corr_co2_ph = pub_corr['excess_CO2_vs_pH_end']

    # 2. Scenario-based energy partition (NOT an empirical measurement!)
    # External mechanical work: 18 W * 180 s = 3,240 J
    W_ext = 3240.0 # J

    # Measured whole-body pulmonary delta-VO2:
    # Baseline: 0.28 L/min. Peak load: 1.05 +/- 0.30 L/min.
    # Estimated mean load VO2 ranges from 0.70 to 1.05 L/min.
    # At caloric equivalent of 20.1 J/mL O2:
    # Scenario grid:
    eta_local_scenarios = [0.20, 0.25, 0.28, 0.35]
    mean_vo2_scenarios_L_min = [0.75, 0.85, 0.95] # Delta VO2 = 0.47, 0.57, 0.67 L/min

    partition_table = []
    for eta in eta_local_scenarios:
        for vo2_mean in mean_vo2_scenarios_L_min:
            delta_vo2_L_min = vo2_mean - 0.28
            delta_vo2_mL_s = (delta_vo2_L_min * 1000.0) / 60.0
            delta_E_pulm_W = delta_vo2_mL_s * 20.1
            total_delta_E_pulm_J = delta_E_pulm_W * 180.0

            local_metabolic_J = W_ext / eta
            parasitic_J = max(0.0, total_delta_E_pulm_J - local_metabolic_J)
            parasitic_pct = (parasitic_J / total_delta_E_pulm_J) * 100.0

            partition_table.append({
                'eta_local_assumed': eta,
                'mean_load_VO2_L_min': vo2_mean,
                'delta_E_pulm_total_J': float(round(total_delta_E_pulm_J, 1)),
                'local_metabolic_demand_J': float(round(local_metabolic_J, 1)),
                'parasitic_energy_J': float(round(parasitic_J, 1)),
                'parasitic_fraction_pct': float(round(parasitic_pct, 1))
            })

    parasitic_pcts = [item['parasitic_fraction_pct'] for item in partition_table]
    nominal_scenario = [item for item in partition_table if item['eta_local_assumed'] == 0.28 and item['mean_load_VO2_L_min'] == 0.85][0]

    return {
        'experiment_id': 'EXP-0029',
        'title': 'Local-Systemic Coupling and Scenario-Based Parasitic Cost Bounds',
        'status': 'LITERATURE_DERIVED_AND_SCENARIO_BOUNDED',
        'published_literature_correlations': {
            'tau_pcr_vs_tau_vo2': {
                'source': corr_pcr_vo2['source'],
                'R2': corr_pcr_vo2['R2'],
                'p_val': corr_pcr_vo2['p_val'],
                'interpretation': corr_pcr_vo2['interpretation']
            },
            'excess_co2_vs_pH_end': {
                'source': corr_co2_ph['source'],
                'R2': corr_co2_ph['R2'],
                'p_val': corr_co2_ph['p_val'],
                'outlier_note': corr_co2_ph['outlier_note'],
                'interpretation': corr_co2_ph['interpretation']
            }
        },
        'systemic_parasitic_scenario_evaluation': {
            'audit_note': 'The value 66.3% is a SCENARIO CALCULATION (at eta=0.28, mean VO2=0.85 L/min), NOT an independent empirical measurement.',
            'nominal_scenario': nominal_scenario,
            'uncertainty_bounds_pct': [min(parasitic_pcts), max(parasitic_pcts)],
            'scenario_grid': partition_table,
            'finding': f'Under plausible physiological assumptions, non-local cardiorespiratory and postural cost accounts for {min(parasitic_pcts):.1f}% to {max(parasitic_pcts):.1f}% of systemic delta-VO2 (nominal scenario: {nominal_scenario["parasitic_fraction_pct"]}%), confirming that whole-body VO2 cannot be equated to local muscle ATP turnover.'
        }
    }

# ============================================================================
# EXP-D (EXP-0030): Absolute Metabolic Energy Scale, PCr Buffer vs 180s ATP Turnover
# ============================================================================
def run_exp_d(data):
    # Parameter variation grids for human gastrocnemius
    V_active_grid = np.linspace(0.15, 0.40, 26)     # Liters
    ATP_ref_grid = np.linspace(6.5, 9.5, 7)         # mmol/L
    dG_grid = np.linspace(50.0, 64.0, 15)           # kJ/mol = J/mmol
    PCr_ratio = 4.2                                 # [PCr]/[ATP] ratio at rest

    # Calculate span of absolute resting PCr buffer capacity in Joules
    # E_PCr_pool = [ATP]_ref * PCr_ratio * V_active * dG
    E_min = float(np.min(ATP_ref_grid) * PCr_ratio * np.min(V_active_grid) * np.min(dG_grid))
    E_max = float(np.max(ATP_ref_grid) * PCr_ratio * np.max(V_active_grid) * np.max(dG_grid))
    E_median = float(8.2 * PCr_ratio * 0.25 * 54.0)

    # Physical distinction:
    # W_ext over 180 s = 3240 J.
    # Total ATP turnover required = W_ext / eta_actomyosin ~ 3240 / 0.28 = 11,571 J.
    # PCr buffer capacity (205 - 1021 J) accounts for only 2% to 9% of the cumulative energy flux!
    # Therefore, W_ext / (0.80 * E_PCr_pool) is NOT an efficiency: it is a category error.

    # Cannon et al. 2014 Table 1 verification:
    cannon_data = data['cannon2014_pmc4262339_atp_turnover']
    heavy_3min = cannon_data['atp_turnover_rates_mM_per_min']['heavy_3min']
    Q_rate = heavy_3min['Q_oxidative']['mean'] # 35 mM/min
    D_rate = heavy_3min['D_PCr']['mean']       # 1.1 mM/min
    L_rate = heavy_3min['L_glycolytic']['mean'] # 1.5 mM/min
    ATP_tot_rate = heavy_3min['ATP_tot']['mean'] # 38 mM/min

    oxidative_fraction_pct = (Q_rate / ATP_tot_rate) * 100.0
    pcr_fraction_pct = (D_rate / ATP_tot_rate) * 100.0

    # Initial 5-second burst apparent efficiency (where PCr is primary supply)
    # W_5s = 18 W * 5 s = 90 J
    # Delta[PCr]_5s ~ 8 mM
    # Energy from PCr = 8 mM * V_active * dG
    E_pcr_5s_min = 8.0 * np.min(V_active_grid) * np.min(dG_grid) # 8 * 0.15 * 50 = 60 J
    E_pcr_5s_max = 8.0 * np.max(V_active_grid) * np.max(dG_grid) # 8 * 0.40 * 64 = 204.8 J
    eta_initial_apparent_max = 90.0 / E_pcr_5s_min # 1.50 (unphysical if V_active underestimated!)
    eta_initial_apparent_min = 90.0 / E_pcr_5s_max # 0.44

    return {
        'experiment_id': 'EXP-0030',
        'title': 'Absolute Metabolic Energy Scale, PCr Buffer vs 180s ATP Turnover',
        'status': 'CORRECTED_THERMODYNAMIC_REVENUE_ANALYSIS',
        'audit_correction_note': 'Corrected previous unphysical apparent efficiency (>1.0). Differentiated stationary PCr buffer capacity from 180s cumulative ATP turnover flux.',
        'pcr_buffer_capacity_J': {
            'min_J': E_min,
            'median_J': E_median,
            'max_J': E_max,
            'ratio_max_min': float(E_max / E_min),
            'finding': f'Active muscle volume and reference metabolite uncertainty produces a {E_max/E_min:.2f}-fold ambiguity in resting chemical buffer capacity.'
        },
        'atp_turnover_flux_partition_cannon2014': {
            'source': 'Cannon et al. (2014) Table 1, PMC4262339',
            'exercise_modality': 'Bilateral knee extension (quadriceps femoris), NOT plantarflexion (calf)',
            'cross_study_isolation_warning': 'Qualitative proof of oxidative dominance in dynamic steady-state; quantitative fluxes (mM/min) cannot be directly transferred to calf plantarflexion.',
            'Q_oxidative_mM_min': Q_rate,
            'D_pcr_mM_min': D_rate,
            'L_glycolytic_mM_min': L_rate,
            'ATP_total_mM_min': ATP_tot_rate,
            'oxidative_fraction_pct': oxidative_fraction_pct,
            'pcr_hydrolysis_fraction_pct': pcr_fraction_pct,
            'finding': f'During steady high-intensity bilateral knee extension, oxidative phosphorylation supplies {oxidative_fraction_pct:.1f}% of ATP turnover; PCr hydrolysis supplies only {pcr_fraction_pct:.1f}%.'
        },
        'cumulative_180s_energy_comparison_J': {
            'external_work_done_J': 3240.0,
            'required_atp_metabolic_energy_J': 11571.4, # at true actomyosin eta=0.28
            'pcr_pool_energy_contribution_J': E_median * 0.8, # ~445 J (only 3.8% of total 180s energy)
            'oxidative_and_glycolytic_contribution_J': 11571.4 - (E_median * 0.8)
        },
        'initial_burst_efficiency_bounds': {
            'window_s': 5.0,
            'work_J': 90.0,
            'pcr_energy_released_span_J': [float(round(E_pcr_5s_min, 1)), float(round(E_pcr_5s_max, 1))],
            'eta_apparent_span': [float(round(eta_initial_apparent_min, 2)), float(round(eta_initial_apparent_max, 2))],
            'apparent_ratio_diagnostic_note': 'The apparent ratio W_ext / Delta_E_PCr (0.44 to 1.50) is a DIAGNOSTIC ARTIFACT of an incomplete energy balance (omitted early oxidative/glycolytic resynthesis) and volume underestimation (V_active=0.15 L), NOT a physiologically permissible range of efficiency (which is biophysically bounded to 0.25-0.30). Values > 1.0 violate energy conservation.',
            'finding': 'Apparent ratio from PCr alone exceeds unity (1.50) when active volume is underestimated, proving efficiency cannot be identified without direct volumetric MRI.'
        },
        'energy_identifiability_bounds_without_new_data': {
            'identifiable_constraints': [
                'Static resting PCr buffer capacity is bounded to 204.8 - 1021.4 J (4.99-fold span) given anatomical gastrocnemius volume bounds (0.15 - 0.40 L) and [ATP]_ref bounds (6.5 - 9.5 mM).',
                'External work over 180 s (3240 J) exceeds resting PCr buffer capacity by 3.2 to 15.8 times, proving continuous dynamic exercise cannot be powered solely by PCr buffer depletion.'
            ],
            'unidentifiable_without_new_data': [
                'True local actomyosin efficiency eta_local cannot be identified without synchronous volumetric MRI and complete ATP turnover fluxes.',
                'Quantitative ATP turnover rates (mM/min) for calf plantarflexion cannot be transferred from knee-extension studies without independent calf data.',
                'Non-local cardiorespiratory oxygen cost fraction cannot be determined beyond a scenario sensitivity grid (42.8% to 77.1%) without venous catheterization or isolated limb blood flow measurements.'
            ]
        }
    }

# ============================================================================
# EXP-E (EXP-0031): Audit & Retraction of Unverified Mechanical Power Comparison
# ============================================================================
def run_exp_e(data):
    # Historical values recorded in Cycle 7:
    observed_powers = [15.5, 21.8] # 2 points of 1 subject (Moll 2018 Table 2-1)
    historical_d2_raw = 450.0      # Handcoded in previous cycle
    historical_bridge = [14.8, 22.4] # Handcoded in previous cycle
    historical_constant = float(np.mean(observed_powers)) # 18.65 W

    rmse_d2_hist = float(np.sqrt(np.mean((np.array(observed_powers) - historical_d2_raw)**2)))
    rmse_bridge_hist = float(np.sqrt(np.mean((np.array(observed_powers) - np.array(historical_bridge))**2)))
    rmse_constant_hist = float(np.sqrt(np.mean((np.array(observed_powers) - historical_constant)**2)))

    return {
        'experiment_id': 'EXP-0031',
        'title': 'Audit & Retraction of Unverified Mechanical Power Comparison',
        'status': 'RETRACTED_INVALID_COMPARISON',
        'audit_verdict': 'RETRACTED; ALL CLAIMS OF LOCAL BRIDGE PREDICTIVE SUPERIORITY WITHDRAWN',
        'fatal_flaws_documented': [
            '1. D2 prediction was hardcoded as 450.0 W instead of executing the ODE solver.',
            '2. Local bridge predictions were hardcoded as [14.8, 22.4] W instead of executing a forward model.',
            '3. Constant benchmark predictor used the mean of the test observations themselves (in-sample leakage).',
            '4. Sample size was N=2 data points from 1 single participant.'
        ],
        'retained_historical_values_for_provenance': {
            'observed_powers_W': observed_powers,
            'historical_d2_raw_prediction_W': historical_d2_raw,
            'historical_bridge_prediction_W': historical_bridge,
            'historical_constant_mean_W': historical_constant,
            'historical_RMSE_d2_raw_W': rmse_d2_hist,
            'historical_RMSE_bridge_W': rmse_bridge_hist,
            'historical_RMSE_constant_W': rmse_constant_hist
        },
        'scientific_correction': 'No predictive superiority claim is valid. The local-systemic bridge remains an observational diagnostic tool, not an independently validated forward predictor of mechanical power. Real model comparison requires actual execution of all comparative models on a pre-registered holdout cohort.'
    }

def main():
    print("=== Running Corrected Cycle 7 Experimental Suite (EXP-0027..EXP-0031) ===")
    data = load_moll_data()

    exp_a = run_exp_a(data)
    exp_b = run_exp_b(data)
    exp_c = run_exp_c(data)
    exp_d = run_exp_d(data)
    exp_e = run_exp_e(data)

    results = {
        'date': '2026-11-07',
        'audit_status': 'SCIENTIFICALLY_CORRECTED_AND_AUDITED',
        'experiments': {
            'EXP-0027': exp_a,
            'EXP-0028': exp_b,
            'EXP-0029': exp_c,
            'EXP-0030': exp_d,
            'EXP-0031': exp_e
        }
    }

    out_file = BASE / 'experiment_results.json'
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Results successfully written to: {out_file}")

    print("\n--- Summary of Corrected Status ---")
    print(f"EXP-0027: {exp_a['audit_verdict']}")
    print(f"EXP-0028: {exp_b['status']}")
    print(f"EXP-0029: {exp_c['status']}")
    print(f"EXP-0030: {exp_d['status']}")
    print(f"EXP-0031: {exp_e['status']} ({exp_e['audit_verdict']})")

if __name__ == '__main__':
    main()
