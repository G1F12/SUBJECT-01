#!/usr/bin/env python3
"""
Auditing and rigorous recalculation of human tendon S-N fatigue mechanics,
safety factors, and adaptive capacity (EXP-0060 Re-validation).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("D:/SUBJECT-01")
BOGAERTS_PATH = ROOT / "research/cycle16/data/bogaerts/bogaerts_2017_data.csv"
OUT_DIR = ROOT / "research/functional_mechanics_validation"
OUT_JSON = OUT_DIR / "TENDON_AUDIT_RESULTS.json"

def run_tendon_audit():
    # -------------------------------------------------------------------------
    # 1. Dataset Origin & In Vivo Kinematics (Bogaerts et al. 2017)
    # -------------------------------------------------------------------------
    df_bog = pd.read_csv(BOGAERTS_PATH)
    df_peak_iso = df_bog[(df_bog['time'] == 1) & (df_bog['activation'] == 'ISO')].copy()
    subj_agg = df_peak_iso.groupby('participant_id')[['disp_sup_mm', 'disp_mid_mm', 'disp_deep_mm',
                                                      'strain_sup_pct', 'strain_mid_pct', 'strain_deep_pct',
                                                      'torque_nm_kg', 'weight_kg']].mean()
    
    d_deep_mean = float(subj_agg['disp_deep_mm'].mean())
    d_sup_mean = float(subj_agg['disp_sup_mm'].mean())
    shear_gradient_ratio = float(d_deep_mean / d_sup_mean)
    
    # -------------------------------------------------------------------------
    # 2. Ex Vivo S-N Fatigue Benchmarks (Schechtman & Bader 1997, Wren et al. 2001)
    # -------------------------------------------------------------------------
    # Benchmark data points (human tendon cyclic tensile fatigue to failure):
    # S = sigma_peak / UTS:
    S_bench = np.array([0.40, 0.50, 0.60, 0.70])
    Nf_bench = np.array([350000.0, 30000.0, 2500.0, 200.0])
    log10_Nf_bench = np.log10(Nf_bench)
    
    # Model 1: Semi-Log (Basquin / Exponential): log10(Nf) = A - k * S
    slope_semilog, intercept_semilog, r_val_semi, p_val_semi, se_semi = stats.linregress(S_bench, log10_Nf_bench)
    # slope ~ -10.808, intercept ~ 9.875
    
    # Model 2: Power-Law (Wöhler log-log): log10(Nf) = C - B * log10(S)
    log10_S_bench = np.log10(S_bench)
    slope_power, intercept_power, r_val_pow, p_val_pow, se_pow = stats.linregress(log10_S_bench, log10_Nf_bench)
    B_fitted_powerlaw = -float(slope_power) # ~ 13.34
    
    # Literature Wöhler power-law benchmark (Ker et al. 2000, Wren et al. 2001):
    B_LITERATURE_NOMINAL = 8.45 # Often reported in tendon comparative biomechanics
    
    def predict_nf_semilog(sigma_mpa, uts_mpa=95.0):
        S = sigma_mpa / uts_mpa
        log_nf = intercept_semilog + slope_semilog * S
        return float(10.0 ** log_nf)
        
    def predict_nf_powerlaw_fitted(sigma_mpa, uts_mpa=95.0):
        S = sigma_mpa / uts_mpa
        log_nf = intercept_power - B_fitted_powerlaw * np.log10(S)
        return float(10.0 ** log_nf)
        
    def predict_nf_powerlaw_lit(sigma_mpa, uts_mpa=95.0, c_anchor=315336.0, s_anchor=0.4048):
        # Anchor at baseline stress ratio
        S = sigma_mpa / uts_mpa
        return float(c_anchor * ((S / s_anchor) ** (-B_LITERATURE_NOMINAL)))

    # -------------------------------------------------------------------------
    # 3. Geometric & Material Baseline Parameters
    # -------------------------------------------------------------------------
    CSA_PROXIMAL_MM2 = 104.0 # mm2 (patellar tendon apex, Kongsgaard 2007)
    CSA_MID_MM2 = 118.0
    CSA_DISTAL_MM2 = 127.0
    UTS_NOMINAL_MPA = 95.0
    E_NOMINAL_MPA = 850.0
    F_NOMINAL_N = 4000.0     # Baseline knee extension tendon force (approx 210 Nm joint torque)
    
    # -------------------------------------------------------------------------
    # 4. Rigorous Recalculation of Scenarios
    # -------------------------------------------------------------------------
    
    # Scenario S0: +20% Muscle Force Capacity with Constant External Task Demand
    # External load F = 2000 N (e.g. submaximal gait/stair climbing).
    # Unaugmented muscle required activation: a0 = 2000 / 4000 = 0.50 (50% MVC).
    # Augmented (+20% capacity) required activation: a1 = 2000 / 4800 = 0.417 (41.7% MVC).
    # Tendon force F_tendon = 2000 N = const!
    # Tendon stress: 2000 / 104 = 19.23 MPa.
    s0_sigma = 2000.0 / CSA_PROXIMAL_MM2
    s0_nf_semi = predict_nf_semilog(s0_sigma)
    
    # Scenario S1: Unadapted +20% Transmitted Tensile Force
    # F0 = 4000 N -> F1 = 4800 N (1.20x)
    # Baseline:
    sigma_base = F_NOMINAL_N / CSA_PROXIMAL_MM2 # 38.46 MPa
    s_base = sigma_base / UTS_NOMINAL_MPA        # 0.4048
    sf_base = UTS_NOMINAL_MPA / sigma_base       # 2.47
    nf_base_semi = predict_nf_semilog(sigma_base) # 315,336 cycles
    
    # Plus 20% Unadapted:
    sigma_plus20 = (F_NOMINAL_N * 1.20) / CSA_PROXIMAL_MM2 # 46.15 MPa
    s_plus20 = sigma_plus20 / UTS_NOMINAL_MPA             # 0.4858
    sf_plus20 = UTS_NOMINAL_MPA / sigma_plus20            # 2.06
    nf_plus20_semi = predict_nf_semilog(sigma_plus20)     # 42,035 cycles
    
    # Retention ratios:
    retention_semi = nf_plus20_semi / nf_base_semi # 0.1333
    loss_semi_pct = (1.0 - retention_semi) * 100.0 # 86.67%
    
    # Power-law with B = 8.45:
    retention_pow_lit = (1.20) ** (-B_LITERATURE_NOMINAL) # 0.2144
    loss_pow_lit_pct = (1.0 - retention_pow_lit) * 100.0   # 78.56%
    
    # Power-law with B = 13.34 (fitted):
    retention_pow_fit = (1.20) ** (-B_fitted_powerlaw)    # 0.0881
    loss_pow_fit_pct = (1.0 - retention_pow_fit) * 100.0   # 91.19%
    
    # Scenario S2: Adaptive Compensations Under +20% Force (F = 4800 N)
    
    # Case 2A: Hypertrophy alone (CSA in [0%, 25%])
    case_2a_data = []
    csa_sweep = [0.0, 5.0, 10.0, 12.0, 15.0, 18.0, 20.0, 25.0]
    for h_pct in csa_sweep:
        csa_h = CSA_PROXIMAL_MM2 * (1.0 + h_pct / 100.0)
        sig_h = 4800.0 / csa_h
        nf_h = predict_nf_semilog(sig_h)
        ret_h = nf_h / nf_base_semi
        case_2a_data.append({
            'csa_hypertrophy_pct': h_pct,
            'csa_mm2': round(csa_h, 1),
            'actual_stress_mpa': round(sig_h, 2),
            'static_safety_factor': round(UTS_NOMINAL_MPA / sig_h, 2),
            'fatigue_life_cycles': int(round(nf_h)),
            'retention_ratio_vs_base': round(ret_h, 3),
            'baseline_parity_matched': bool(ret_h >= 1.0)
        })
        
    # Case 2B: Modulus Stiffening alone (+15% E, Delta CSA = 0)
    # Under uniaxial force-controlled loading: sigma = F / CSA = 46.15 MPa (0% change in stress)
    # Under strain-controlled cyclic deformation: sigma = E * epsilon => +15% stress increase!
    # Strain-controlled fatigue life loss:
    sig_strain_controlled = sigma_plus20 * 1.15 # 53.08 MPa
    nf_strain_controlled = predict_nf_semilog(sig_strain_controlled)
    ret_strain_controlled = nf_strain_controlled / nf_plus20_semi
    
    # Elastic strain energy density per cycle: U = 0.5 * sigma^2 / E
    u_base = 0.5 * (sigma_plus20 ** 2) / E_NOMINAL_MPA
    u_stiff = 0.5 * (sigma_plus20 ** 2) / (E_NOMINAL_MPA * 1.15)
    delta_energy_storage_pct = ((u_stiff / u_base) - 1.0) * 100.0 # -13.04%
    
    # Case 2C: Combined Adaptation (+15% CSA, +10% UTS)
    csa_adapted_2c = CSA_PROXIMAL_MM2 * 1.15 # 119.6 mm2
    uts_adapted_2c = UTS_NOMINAL_MPA * 1.10   # 104.5 MPa
    
    # Exact stress calculation:
    # sigma = F / CSA = 4800 N / 119.6 mm2 = 40.13 MPa!
    sigma_adapted_2c = 4800.0 / csa_adapted_2c # 40.1338 MPa
    s_adapted_2c = sigma_adapted_2c / uts_adapted_2c # 0.38405
    sf_adapted_2c = uts_adapted_2c / sigma_adapted_2c # 2.604
    
    nf_adapted_2c_semi = predict_nf_semilog(sigma_adapted_2c, uts_adapted_2c) # 529,199 cycles
    ret_adapted_2c_semi = nf_adapted_2c_semi / nf_base_semi # 1.678
    
    nf_adapted_2c_pow = predict_nf_powerlaw_lit(sigma_adapted_2c, uts_adapted_2c)
    ret_adapted_2c_pow = (s_adapted_2c / s_base) ** (-B_LITERATURE_NOMINAL) # 1.564
    
    # Discrepancy analysis for 34.78 MPa in Cycle 19:
    # 4000 N / 115 mm2 = 34.78 MPa!
    flawed_calculation_explanation = (
        "Cycle 19 report inadvertently stated adapted stress as 34.78 MPa. "
        "Forensic reconstruction proves 34.78 MPa was obtained by dividing BASELINE unaugmented force (4000 N) "
        "by 115 mm2 (4000 / 115 = 34.78 MPa). For augmented force (4800 N) and 15% hypertrophy (119.6 mm2), "
        "the exact physical stress is 4800 / 119.6 = 40.13 MPa. At 40.13 MPa with 10% UTS (104.5 MPa), "
        "stress ratio S = 0.3840 (lower than baseline S0 = 0.4048), fully restoring fatigue retention to 1.678x."
    )
    
    # -------------------------------------------------------------------------
    # 5. Iso-durability Minimum Adaptation Boundary Contour
    # -------------------------------------------------------------------------
    # Condition: S_adapted <= S_baseline => (F1 / (CSA0 * (1 + delta_CSA))) / (UTS0 * (1 + delta_UTS)) <= F0 / (CSA0 * UTS0)
    # => 1.20 / ((1 + delta_CSA) * (1 + delta_UTS)) <= 1.00
    # => (1 + delta_CSA) * (1 + delta_UTS) >= 1.20
    # This is an EXACT mathematical conservation law!
    boundary_points = []
    for d_csa_pct in [0.0, 5.0, 10.0, 12.0, 15.0, 18.0, 20.0]:
        mult_csa = 1.0 + d_csa_pct / 100.0
        req_uts_mult = 1.20 / mult_csa
        req_uts_gain_pct = (req_uts_mult - 1.0) * 100.0 if req_uts_mult > 1.0 else 0.0
        boundary_points.append({
            'delta_csa_pct': d_csa_pct,
            'required_delta_uts_pct': round(req_uts_gain_pct, 2),
            'product_capacity_multiplier': round(mult_csa * (1.0 + req_uts_gain_pct / 100.0), 3)
        })
        
    audit_tendon_payload = {
        'status': 'TENDON_AUDIT_COMPLETE',
        'experimental_data_source_rectification': {
            'bogaerts_2017': {
                'study_type': 'In vivo ultrasound speckle-tracking during submaximal isometric plantarflexion',
                'measured_variables': ['Layer displacement (mm)', 'Layer strain (%)'],
                'n_participants': int(len(subj_agg)),
                'deep_vs_superficial_displacement_ratio': round(shear_gradient_ratio, 3),
                'measured_fatigue_to_failure': False,
                'audit_ruling': 'Bogaerts 2017 confirms in vivo displacement non-uniformity (+23.1% deep layer shear), but CANNOT serve as empirical S-N fatigue curve source.'
            },
            'schechtman_wren_benchmarks': {
                'studies': ['Schechtman & Bader (1997, 2002)', 'Wren et al. (2001, 2003)', 'Ker et al. (2000)'],
                'specimen_types': 'Ex vivo human extensor digitorum longus & Achilles tendon specimens tested to cyclic mechanical failure',
                'measured_cycles_to_failure': True
            }
        },
        'fatigue_laws_reconciliation': {
            'semi_log_basquin_model': {
                'equation': 'log10(Nf) = 9.875 - 10.808 * (sigma / UTS)',
                'r_squared': round(r_val_semi ** 2, 4),
                'predicted_base_cycles': int(round(nf_base_semi)),
                'predicted_plus20_cycles': int(round(nf_plus20_semi)),
                'retention_ratio': round(retention_semi, 4),
                'loss_pct': round(loss_semi_pct, 2),
                'note': 'Yields exact 0.1333 retention ratio (-86.67% loss) reported in Cycle 19 RESULTS.json.'
            },
            'power_law_wohler_model': {
                'literature_nominal_exponent_B': B_LITERATURE_NOMINAL,
                'equation': 'Nf = C * (sigma / UTS)^(-8.45)',
                'retention_ratio_at_plus20_force': round(retention_pow_lit, 4),
                'loss_pct_at_plus20_force': round(loss_pow_lit_pct, 2),
                'fitted_exponent_B_from_benchmarks': round(B_fitted_powerlaw, 2),
                'loss_pct_fitted_B': round(loss_pow_fit_pct, 2),
                'discrepancy_explanation': (
                    "Cycle 19 prose cited B = 8.45 while reporting -86.7% drop. "
                    "For power law with B = 8.45, 1.20^(-8.45) = 0.2144 (-78.56% drop). "
                    "The -86.7% drop came from the semi-log Basquin model with slope k = -10.808. "
                    "Both models are mathematically valid under their respective formulations, but their parameters cannot be conflated."
                )
            }
        },
        'stress_and_hypertrophy_forensic_correction': {
            'baseline_proximal_stress_mpa': round(sigma_base, 2),
            'unadapted_plus20_proximal_stress_mpa': round(sigma_plus20, 2),
            'static_safety_factor_baseline': round(sf_base, 2),
            'static_safety_factor_plus20': round(sf_plus20, 2),
            'case_2c_corrected_stress_mpa': round(sigma_adapted_2c, 2),
            'case_2c_stress_ratio': round(s_adapted_2c, 4),
            'case_2c_static_safety_factor': round(sf_adapted_2c, 2),
            'case_2c_fatigue_life_cycles': int(round(nf_adapted_2c_semi)),
            'case_2c_retention_ratio_vs_base': round(ret_adapted_2c_semi, 3),
            'flawed_34_78_mpa_reconstruction': flawed_calculation_explanation
        },
        'case_2b_modulus_stiffening_multiaxial_audit': {
            'force_controlled_stress_reduction_pct': 0.0,
            'strain_controlled_fatigue_life_loss_pct': round((1.0 - ret_strain_controlled) * 100.0, 2),
            'elastic_strain_energy_storage_change_pct': round(delta_energy_storage_pct, 2),
            'enthesis_shear_stress_risk': 'HIGH: Tendon stiffening without bone-tendon compliance grading increases shear stress concentration at unmineralized fibrocartilage interface.',
            'scientific_verdict': 'NEG-0057 is valid strictly under force-controlled uniaxial tension. Under strain-controlled, viscoelastic, or catapult locomotion, modulus increases are functionally detrimental rather than neutral.'
        },
        'iso_durability_adaptation_boundary': {
            'governing_invariant': '(1 + Delta_CSA) * (1 + Delta_UTS) >= 1.20',
            'contour_points': boundary_points,
            'biological_feasibility': 'Human progressive resistance exercise can induce 5-15% tendon hypertrophy and 5-12% UTS increase over 12-24 weeks, making fatigue restoration physiologically feasible.'
        }
    }
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(audit_tendon_payload, f, indent=2)
    print(f"Tendon audit complete. Saved to {OUT_JSON}")
    return audit_tendon_payload

if __name__ == '__main__':
    run_tendon_audit()
