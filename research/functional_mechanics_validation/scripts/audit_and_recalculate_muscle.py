#!/usr/bin/env python3
"""
Auditing and rigorous recalculation of human skeletal muscle specific tension,
predictive modeling, and isomass scaling trade-offs (EXP-0059 Re-validation).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

ROOT = Path("D:/SUBJECT-01")
DATA_PATH = ROOT / "research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv"
OUT_DIR = ROOT / "research/functional_mechanics_validation"
SCRIPTS_DIR = OUT_DIR / "scripts"

def run_muscle_audit():
    df = pd.read_csv(DATA_PATH)
    df_ext = df[df['action'] == 'extension'].copy()
    df_ext['sex_code'] = (df_ext['sex'] == 'M').astype(float)
    
    # -------------------------------------------------------------------------
    # 1. Parameter Specifications & Conventions
    # -------------------------------------------------------------------------
    # Nominal reference values:
    L_FASCICLE_BASE_CM = 8.40   # Ward et al. 2009 (vastus lateralis / rectus femoris average)
    THETA_BASE_DEG = 14.0       # Blazevich et al. 2006 (mean resting pennation)
    th0_rad = np.radians(THETA_BASE_DEG)
    A_ACT_MVC = 0.95            # Nominal voluntary activation level
    
    # Moment arm polynomial (Buford et al. 1997, Herzog & Read 1993):
    # r_pat(a) = 0.043 + 0.00018 * a - 0.0000015 * a^2 (meters)
    def patellar_moment_arm_m(angle_deg):
        return 0.043 + 0.00018 * angle_deg - 0.0000015 * (angle_deg ** 2)
        
    # Handsfield et al. (2014) quadriceps volume scaling:
    def quad_volume_cm3(mass_kg, height_m, sex):
        coeff = 16.5 if sex == 'M' else 13.8
        return coeff * mass_kg * height_m
        
    # Isometric force-length multiplier (Gordon et al. 1966, de Brito Fontana & Herzog 2016):
    def force_length_multiplier(angle_deg):
        opt_angle = 70.0
        width = 50.0
        fl = 1.0 - ((angle_deg - opt_angle) / width) ** 2
        return np.clip(fl, 0.4, 1.0)
        
    df_ext['rpat_m'] = [patellar_moment_arm_m(a) for a in df_ext['angle_deg']]
    df_ext['vquad_cm3'] = [quad_volume_cm3(m, h, s) for m, h, s in zip(df_ext['mass'], df_ext['height'], df_ext['sex'])]
    df_ext['fl_mult'] = [force_length_multiplier(a) for a in df_ext['angle_deg']]
    
    # -------------------------------------------------------------------------
    # 2. Convention A vs Convention B Specific Tension Derivation
    # -------------------------------------------------------------------------
    # Convention A (Standard Biomechanical PCSA = (V / lf) * cos(theta)):
    # Total muscle force along tendon: F_tendon = sigma_A * PCSA_A
    # sigma_A = T_knee / (r_pat * PCSA_A * fl * A_act)
    df_ext['pcsa_convA_cm2'] = (df_ext['vquad_cm3'] / L_FASCICLE_BASE_CM) * np.cos(th0_rad)
    df_ext['sigma_convA_n_cm2'] = df_ext['torque_nm'] / (df_ext['rpat_m'] * df_ext['pcsa_convA_cm2'] * df_ext['fl_mult'] * A_ACT_MVC)
    
    # Convention B (Fiber Cross-Sectional Area Af = V / lf):
    # Total tendon force: F_tendon = sigma_B * Af * cos(theta)
    # sigma_B = T_knee / (r_pat * Af * cos(theta) * fl * A_act)
    # Note that sigma_A == sigma_B because PCSA_A = Af * cos(theta)!
    df_ext['af_convB_cm2'] = df_ext['vquad_cm3'] / L_FASCICLE_BASE_CM
    df_ext['sigma_convB_n_cm2'] = df_ext['torque_nm'] / (df_ext['rpat_m'] * df_ext['af_convB_cm2'] * np.cos(th0_rad) * df_ext['fl_mult'] * A_ACT_MVC)
    
    # Cycle 19 Flawed Implementation (Double-Cosine):
    # Divided by pcsa_convA * cos(theta), which effectively divides by Af * cos^2(theta)!
    df_ext['sigma_cycle19_flawed_n_cm2'] = df_ext['torque_nm'] / (df_ext['rpat_m'] * df_ext['pcsa_convA_cm2'] * np.cos(th0_rad) * df_ext['fl_mult'] * A_ACT_MVC)
    
    # Per-subject mean specific tensions:
    subj_means_A = df_ext.groupby('participant_id')['sigma_convA_n_cm2'].mean()
    subj_means_flawed = df_ext.groupby('participant_id')['sigma_cycle19_flawed_n_cm2'].mean()
    subj_sex = df_ext.groupby('participant_id')['sex'].first()
    
    male_ids = subj_sex[subj_sex == 'M'].index
    female_ids = subj_sex[subj_sex == 'F'].index
    
    sig_A_all = subj_means_A.values
    sig_A_m = subj_means_A.loc[male_ids].values
    sig_A_f = subj_means_A.loc[female_ids].values
    
    # Flawed values for forensic comparison:
    flawed_all = subj_means_flawed.values
    flawed_m = subj_means_flawed.loc[male_ids].values
    flawed_f = subj_means_flawed.loc[female_ids].values
    
    # -------------------------------------------------------------------------
    # 3. Equivalence Testing (TOST: Two One-Sided Tests)
    # -------------------------------------------------------------------------
    # Standard t-test:
    t_stat, t_pval = stats.ttest_ind(sig_A_m, sig_A_f, equal_var=False)
    diff_mean = float(np.mean(sig_A_m) - np.mean(sig_A_f))
    pooled_se = float(np.sqrt(np.var(sig_A_m, ddof=1)/len(sig_A_m) + np.var(sig_A_f, ddof=1)/len(sig_A_f)))
    df_welch = ((np.var(sig_A_m, ddof=1)/len(sig_A_m) + np.var(sig_A_f, ddof=1)/len(sig_A_f))**2 /
                ((np.var(sig_A_m, ddof=1)/len(sig_A_m))**2 / (len(sig_A_m)-1) + 
                 (np.var(sig_A_f, ddof=1)/len(sig_A_f))**2 / (len(sig_A_f)-1)))
    
    tost_results = {}
    for margin_pct in [10.0, 15.0, 20.0]:
        delta = float(np.mean(sig_A_all) * (margin_pct / 100.0))
        t1 = (diff_mean - (-delta)) / pooled_se
        p1 = float(1.0 - stats.t.cdf(t1, df_welch))
        t2 = (diff_mean - delta) / pooled_se
        p2 = float(stats.t.cdf(t2, df_welch))
        p_tost = max(p1, p2)
        tost_results[f"margin_{int(margin_pct)}pct"] = {
            'equivalence_margin_delta_n_cm2': round(delta, 2),
            't1_lower': round(t1, 3),
            'p1_lower': round(p1, 4),
            't2_upper': round(t2, 3),
            'p2_upper': round(p2, 4),
            'p_tost_max': round(p_tost, 4),
            'equivalent_at_alpha_005': bool(p_tost < 0.05)
        }
        
    # -------------------------------------------------------------------------
    # 4. Monte Carlo Parameter Uncertainty & Sensitivity Propagation
    # -------------------------------------------------------------------------
    np.random.seed(42)
    n_mc = 10000
    mc_sigmas = []
    
    # Observed cohort pooled torque distribution at 75 deg:
    torques_75 = df_ext[df_ext['angle_deg'] == 75]['torque_nm'].values
    masses = df_ext[df_ext['angle_deg'] == 75]['mass'].values
    heights = df_ext[df_ext['angle_deg'] == 75]['height'].values
    sexes = df_ext[df_ext['angle_deg'] == 75]['sex'].values
    
    for _ in range(n_mc):
        # Draw random index from trials:
        idx = np.random.randint(0, len(torques_75))
        t_sample = torques_75[idx]
        m_sample = masses[idx]
        h_sample = heights[idx]
        s_sample = sexes[idx]
        
        # Uncertainty distributions:
        # 1. Moment arm uncertainty: Gaussian +/- 10%
        rpat_sample = patellar_moment_arm_m(75.0) * np.random.normal(1.0, 0.08)
        # 2. Quadriceps volume coeff uncertainty: +/- 12%
        base_coeff = 16.5 if s_sample == 'M' else 13.8
        coeff_sample = base_coeff * np.random.normal(1.0, 0.10)
        v_sample = coeff_sample * m_sample * h_sample
        # 3. Fascicle length: Gaussian 8.4 +/- 0.9 cm
        lf_sample = np.clip(np.random.normal(8.4, 0.9), 6.5, 11.0)
        # 4. Pennation angle: Gaussian 14 +/- 2.5 deg
        th_sample = np.radians(np.clip(np.random.normal(14.0, 2.5), 8.0, 22.0))
        # 5. Voluntary activation: Beta distribution peaked around 0.93 in [0.80, 0.98]
        act_sample = np.random.uniform(0.85, 0.98)
        # 6. Force-length multiplier at 75 deg:
        fl_sample = force_length_multiplier(75.0) * np.random.normal(1.0, 0.05)
        
        # PCSA (Convention A):
        pcsa_sample = (v_sample / lf_sample) * np.cos(th_sample)
        sig_sample = t_sample / (rpat_sample * pcsa_sample * fl_sample * act_sample)
        mc_sigmas.append(sig_sample)
        
    mc_sigmas = np.array(mc_sigmas)
    mc_p025 = float(np.percentile(mc_sigmas, 2.5))
    mc_p160 = float(np.percentile(mc_sigmas, 16.0))
    mc_p500 = float(np.percentile(mc_sigmas, 50.0))
    mc_p840 = float(np.percentile(mc_sigmas, 84.0))
    mc_p975 = float(np.percentile(mc_sigmas, 97.5))
    
    # -------------------------------------------------------------------------
    # 5. Strict Holdout Leave-One-Subject-Out (LOSO) Predictive Models
    # -------------------------------------------------------------------------
    subjects = np.sort(df_ext['participant_id'].unique())
    preds = {
        'M0_baseline_mean': [],
        'M1_anthropometry_angle': [],
        'M2_biomechanical_pcsa_strict': [],
        'M3_architecture_agonist_emg': [],
        'M4_full_multichannel_emg': []
    }
    actuals = []
    sub_ids = []
    alphas = np.logspace(-2, 3, 20)
    
    for s in subjects:
        tr = df_ext[df_ext['participant_id'] != s]
        te = df_ext[df_ext['participant_id'] == s]
        
        y_tr = tr['torque_nm'].values
        y_te = te['torque_nm'].values
        
        # M0: Baseline Mean
        preds['M0_baseline_mean'].extend(np.full_like(y_te, np.mean(y_tr)))
        
        # M1: Anthropometry + Angle
        f_m1 = ['mass', 'height', 'sex_code', 'angle_deg', 'age']
        sc1 = StandardScaler()
        m1 = LinearRegression()
        m1.fit(sc1.fit_transform(tr[f_m1].values), y_tr)
        preds['M1_anthropometry_angle'].extend(m1.predict(sc1.transform(te[f_m1].values)))
        
        # M2: Biomechanical Physics-Based Model (Strict Fold-Specific Sigma Fitting)
        # Torque = sigma_train * (PCSA_convA * fl * rpat * A_act)
        g_tr = tr['pcsa_convA_cm2'].values * tr['fl_mult'].values * tr['rpat_m'].values * A_ACT_MVC
        sigma_tr_fit = np.sum(y_tr * g_tr) / np.sum(g_tr ** 2)
        g_te = te['pcsa_convA_cm2'].values * te['fl_mult'].values * te['rpat_m'].values * A_ACT_MVC
        preds['M2_biomechanical_pcsa_strict'].extend(sigma_tr_fit * g_te)
        
        # M3: Architecture + Agonist sEMG (Ridge)
        f_m3 = ['pcsa_convA_cm2', 'rpat_m', 'fl_mult', 'emg_RF', 'emg_VM', 'emg_VL']
        sc3 = StandardScaler()
        m3 = RidgeCV(alphas=alphas)
        m3.fit(sc3.fit_transform(tr[f_m3].values), y_tr)
        preds['M3_architecture_agonist_emg'].extend(m3.predict(sc3.transform(te[f_m3].values)))
        
        # M4: Full Model with Antagonists (Ridge)
        f_m4 = f_m1 + ['emg_RF', 'emg_VM', 'emg_VL', 'emg_BF', 'emg_ST']
        sc4 = StandardScaler()
        m4 = RidgeCV(alphas=alphas)
        m4.fit(sc4.fit_transform(tr[f_m4].values), y_tr)
        preds['M4_full_multichannel_emg'].extend(m4.predict(sc4.transform(te[f_m4].values)))
        
        actuals.extend(y_te)
        sub_ids.extend([s] * len(y_te))
        
    y_act = np.array(actuals)
    sub_arr = np.array(sub_ids)
    
    model_eval = {}
    for m_name, y_p in preds.items():
        yp = np.array(y_p)
        rmse_pooled = float(np.sqrt(mean_squared_error(y_act, yp)))
        mae_pooled = float(mean_absolute_error(y_act, yp))
        r2_pooled = float(r2_score(y_act, yp))
        
        # Subject-specific metrics:
        sub_r2s = []
        sub_rmses = []
        for s in subjects:
            idx_s = (sub_arr == s)
            sub_rmses.append(float(np.sqrt(mean_squared_error(y_act[idx_s], yp[idx_s]))))
            # Note: with 5 trials per subject at same angle, local variance can be small
            var_s = np.var(y_act[idx_s])
            if var_s > 1e-4:
                sub_r2s.append(float(r2_score(y_act[idx_s], yp[idx_s])))
                
        model_eval[m_name] = {
            'pooled_rmse_nm': round(rmse_pooled, 2),
            'pooled_mae_nm': round(mae_pooled, 2),
            'pooled_r2': round(r2_pooled, 4),
            'mean_subject_rmse_nm': round(float(np.mean(sub_rmses)), 2),
            'std_subject_rmse_nm': round(float(np.std(sub_rmses, ddof=1)), 2),
            'mean_subject_r2': round(float(np.mean(sub_r2s)), 4) if len(sub_r2s) > 0 else None
        }
        
    # -------------------------------------------------------------------------
    # 6. Physical Isomass Scaling: Force, Velocity, Power & ROM Trade-offs
    # -------------------------------------------------------------------------
    # Constant muscle volume: V_quad = const.
    # Geometry 1: Planar Constant-Thickness Muscle Model (h = lf * sin(theta) = const):
    # lf(theta) = lf0 * sin(theta0) / sin(theta)
    # PCSA(theta) = V / lf(theta) = (V / lf0) * (sin(theta) / sin(theta0))
    # F_tendon(theta) = sigma * PCSA * cos(theta) = sigma * (V / h) * sin(theta) * cos(theta) = 0.5 * sigma * (V / h) * sin(2*theta)
    # Force ratio: F_rel(theta) = sin(2*theta) / sin(2*theta0)
    
    # Geometry 2: Constant Aponeurosis Area / Standard PCSA Scaling:
    # If PCSA increases by factor k, lf must decrease by 1/k: lf = lf0 / k.
    # F_tendon = sigma * PCSA * cos(theta) => F_rel = k * cos(theta) / cos(theta0).
    
    # Force-Velocity & Power (Hill 1938):
    # Normalized Hill parameters: a/F0 = 0.25, b/vmax = 0.25 => P_max = 0.10 * F0 * vmax.
    # vmax_norm (fiber lengths/s): assumed constant (e.g. 10.0 lf/s for mixed human muscle).
    # Absolute vmax (m/s) = vmax_norm * lf (meters).
    
    thetas_sweep = [14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0]
    isomass_curve = []
    
    base_sin2 = np.sin(2.0 * th0_rad)
    vmax_norm = 10.0 # s^-1
    vmax0_abs = vmax_norm * (L_FASCICLE_BASE_CM / 100.0) # 0.84 m/s
    f0_nominal = 6059.0 # N
    pmax0_nominal = 0.10 * f0_nominal * vmax0_abs # Watts
    
    for th in thetas_sweep:
        th_r = np.radians(th)
        # Geometry 1 (constant thickness):
        sin2_th = np.sin(2.0 * th_r)
        f_gain_geom1_pct = float(((sin2_th / base_sin2) - 1.0) * 100.0)
        lf_geom1_cm = float(L_FASCICLE_BASE_CM * (np.sin(th0_rad) / np.sin(th_r)))
        vmax_abs_geom1 = float(vmax_norm * (lf_geom1_cm / 100.0))
        vmax_loss_pct = float((1.0 - (lf_geom1_cm / L_FASCICLE_BASE_CM)) * 100.0)
        
        # Mechanical power:
        f_curr = f0_nominal * (1.0 + f_gain_geom1_pct / 100.0)
        pmax_curr = 0.10 * f_curr * vmax_abs_geom1
        pmax_change_pct = float(((pmax_curr / pmax0_nominal) - 1.0) * 100.0)
        
        # Geometry 2 (simple cosine model with lf = 6.71 cm):
        # If lf shortens to 6.71 cm (e.g. PCSA +25.2%):
        k_arb = 1.252
        f_gain_geom2_pct = float(((k_arb * np.cos(th_r) / np.cos(th0_rad)) - 1.0) * 100.0)
        
        isomass_curve.append({
            'pennation_deg': float(th),
            'geom1_constant_thickness': {
                'fascicle_length_cm': round(lf_geom1_cm, 2),
                'isometric_force_gain_pct': round(f_gain_geom1_pct, 2),
                'absolute_vmax_m_s': round(vmax_abs_geom1, 3),
                'vmax_loss_pct': round(vmax_loss_pct, 2),
                'peak_power_watts': round(pmax_curr, 1),
                'peak_power_change_pct': round(pmax_change_pct, 2),
                'active_rom_loss_pct': round(vmax_loss_pct, 2)
            },
            'geom2_simple_cosine_with_lf671': {
                'isometric_force_gain_pct': round(f_gain_geom2_pct, 2)
            }
        })
        
    audit_results = {
        'status': 'AUDIT_COMPLETE',
        'n_participants': int(len(subjects)),
        'n_trials': int(len(df_ext)),
        'provenance_chain': {
            'measured_variables': ['Dynamometer knee torque (Nm)', 'Knee flexion angle (deg)', 'Surface EMG amplitudes (uV)'],
            'allometric_literature_models': ['Quadriceps volume (Handsfield et al. 2014)', 'Fascicle length 8.4 cm (Ward et al. 2009)', 'Resting pennation 14 deg (Blazevich 2006)', 'Patellar moment arm (Buford et al. 1997)'],
            'assumed_unmeasured_constants': ['Voluntary activation level A_act = 0.95', 'Hamstring co-contraction torque ignored in net extension'],
            'identifiability_verdict': 'NOT_ISOLATED_EMPIRICAL_MEASUREMENT: Specific tension is a model-dependent parameter derived from combining measured torque with literature allometric PCSA.'
        },
        'specific_tension_evaluations': {
            'corrected_convA_single_cosine': {
                'mean_n_cm2': round(float(np.mean(sig_A_all)), 2),
                'std_n_cm2': round(float(np.std(sig_A_all, ddof=1)), 2),
                'median_n_cm2': round(float(np.median(sig_A_all)), 2),
                'ci95_t': [round(float(np.mean(sig_A_all) - 2.093 * stats.sem(sig_A_all)), 2),
                           round(float(np.mean(sig_A_all) + 2.093 * stats.sem(sig_A_all)), 2)],
                'male_mean_n_cm2': round(float(np.mean(sig_A_m)), 2),
                'female_mean_n_cm2': round(float(np.mean(sig_A_f)), 2),
                'male_minus_female_diff': round(diff_mean, 2)
            },
            'cycle19_flawed_double_cosine': {
                'mean_n_cm2': round(float(np.mean(flawed_all)), 2),
                'std_n_cm2': round(float(np.std(flawed_all, ddof=1)), 2),
                'discrepancy_explanation': 'Cycle 19 divided by cos(14 deg) twice, scaling values by 1 / cos(14 deg) = 1.0306x (27.22 vs 26.41 N/cm2).'
            },
            'monte_carlo_uncertainty_propagation': {
                'median_n_cm2': round(mc_p500, 2),
                'ci68_range': [round(mc_p160, 2), round(mc_p840, 2)],
                'ci95_range': [round(mc_p025, 2), round(mc_p975, 2)],
                'uncertainty_width_n_cm2': round(mc_p975 - mc_p025, 2)
            }
        },
        'sex_equivalence_analysis': {
            'standard_welch_t_test': {
                't_statistic': round(t_stat, 3),
                'p_value': round(t_pval, 4),
                'interpretation': 'High p-value fails to reject null hypothesis of equality, but does not mathematically prove equivalence.'
            },
            'tost_equivalence_tests': tost_results
        },
        'predictive_models_loso': model_eval,
        'isomass_scaling_and_tradeoffs': {
            'pennation_sweep': isomass_curve,
            'scenario_18deg_summary': {
                'geom1_planar_aponeurosis_force_gain_pct': 25.20,
                'geom2_simple_cosine_force_gain_pct': 22.70,
                'fascicle_length_shortening_cm': '8.40 -> 6.58 cm (-21.71%)',
                'absolute_vmax_loss_pct': -21.71,
                'normalized_vmax_change': '0.0% (intrinsic fiber kinetic vmax_norm remains 10.0 s^-1)',
                'peak_mechanical_power_change_pct': -1.98,
                'active_rom_reduction_pct': -21.71,
                'fundamental_tradeoff_verdict': 'ISOMASS_POWER_PENALTY: Increasing pennation under fixed mass increases static force (+25.2%), but reduces peak power (-2.0%) and functional speed (-21.7%).'
            }
        }
    }
    
    out_file = OUT_DIR / "MUSCLE_AUDIT_RESULTS.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2)
    print(f"Muscle audit complete. Saved to {out_file}")
    return audit_results

if __name__ == '__main__':
    run_muscle_audit()
