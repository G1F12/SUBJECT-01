import pandas as pd
import numpy as np
from pathlib import Path
import json
from scipy import stats
from sklearn.linear_model import LinearRegression, RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler

data_path = Path("D:/SUBJECT-01/research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv")
out_dir = Path("D:/SUBJECT-01/research/cycle16")
out_json = out_dir / "E1_MODEL_COMPARISON.json"

df = pd.read_csv(data_path)
df['sex_code'] = (df['sex'] == 'M').astype(float)

def bootstrap_ci(arr, n_boot=2000, ci=95):
    boot_means = [np.mean(np.random.choice(arr, size=len(arr), replace=True)) for _ in range(n_boot)]
    low = np.percentile(boot_means, (100 - ci) / 2)
    high = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return float(low), float(high)

def run_loso_evaluation(sub_df, action_name, agonist_cols, antagonist_cols):
    subjects = np.sort(sub_df['participant_id'].unique())
    demo_cols = ['angle_deg', 'mass', 'height', 'age', 'sex_code']
    
    # Store predictions
    preds = {
        'M0_mean': [],
        'M1_agonist': [],
        'M2_agonist_antagonist': [],
        'M3_ridge': [],
        'M4_demographics_kinematics': []
    }
    actuals = []
    subject_ids = []
    
    # Per-subject metrics
    subject_metrics = []
    
    for s in subjects:
        train_df = sub_df[sub_df['participant_id'] != s]
        test_df = sub_df[sub_df['participant_id'] == s]
        
        y_train = train_df['torque_nm'].values
        y_test = test_df['torque_nm'].values
        
        # M0: Baseline Mean
        m0_val = np.mean(y_train)
        y_pred_m0 = np.full_like(y_test, m0_val)
        
        # M1: Agonist-only OLS
        X1_train = train_df[agonist_cols].values
        X1_test = test_df[agonist_cols].values
        scaler1 = StandardScaler()
        X1_train_sc = scaler1.fit_transform(X1_train)
        X1_test_sc = scaler1.transform(X1_test)
        
        m1 = LinearRegression()
        m1.fit(X1_train_sc, y_train)
        y_pred_m1 = m1.predict(X1_test_sc)
        
        # M2: Agonist + Antagonist OLS
        feat2 = agonist_cols + antagonist_cols
        X2_train = train_df[feat2].values
        X2_test = test_df[feat2].values
        scaler2 = StandardScaler()
        X2_train_sc = scaler2.fit_transform(X2_train)
        X2_test_sc = scaler2.transform(X2_test)
        
        m2 = LinearRegression()
        m2.fit(X2_train_sc, y_train)
        y_pred_m2 = m2.predict(X2_test_sc)
        
        # M3: Ridge Regularized (Agonist + Antagonist)
        alphas = np.logspace(-2, 3, 20)
        m3 = RidgeCV(alphas=alphas)
        m3.fit(X2_train_sc, y_train)
        y_pred_m3 = m3.predict(X2_test_sc)
        
        # M4: Full demographic + kinematic + EMG
        feat4 = feat2 + demo_cols
        X4_train = train_df[feat4].values
        X4_test = test_df[feat4].values
        scaler4 = StandardScaler()
        X4_train_sc = scaler4.fit_transform(X4_train)
        X4_test_sc = scaler4.transform(X4_test)
        
        m4 = RidgeCV(alphas=alphas)
        m4.fit(X4_train_sc, y_train)
        y_pred_m4 = m4.predict(X4_test_sc)
        
        # Append
        preds['M0_mean'].extend(y_pred_m0)
        preds['M1_agonist'].extend(y_pred_m1)
        preds['M2_agonist_antagonist'].extend(y_pred_m2)
        preds['M3_ridge'].extend(y_pred_m3)
        preds['M4_demographics_kinematics'].extend(y_pred_m4)
        actuals.extend(y_test)
        subject_ids.extend([s] * len(y_test))
        
        # Subject-level RMSE
        rmse_m0 = np.sqrt(np.mean((y_test - y_pred_m0)**2))
        rmse_m1 = np.sqrt(np.mean((y_test - y_pred_m1)**2))
        rmse_m2 = np.sqrt(np.mean((y_test - y_pred_m2)**2))
        rmse_m3 = np.sqrt(np.mean((y_test - y_pred_m3)**2))
        rmse_m4 = np.sqrt(np.mean((y_test - y_pred_m4)**2))
        
        subject_metrics.append({
            'participant_id': s,
            'n_trials': len(y_test),
            'rmse_m0': float(rmse_m0),
            'rmse_m1': float(rmse_m1),
            'rmse_m2': float(rmse_m2),
            'rmse_m3': float(rmse_m3),
            'rmse_m4': float(rmse_m4),
            'delta_rmse_m1_m2': float(rmse_m1 - rmse_m2) # positive means M2 is better
        })
    
    y_true = np.array(actuals)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    
    model_summary = {}
    for m_key in preds:
        y_hat = np.array(preds[m_key])
        rmse = np.sqrt(np.mean((y_true - y_hat)**2))
        mae = np.mean(np.abs(y_true - y_hat))
        ss_res = np.sum((y_true - y_hat)**2)
        r2 = 1.0 - (ss_res / ss_tot)
        
        # Bootstrap CIs for RMSE and MAE
        errors_sq = (y_true - y_hat)**2
        errors_abs = np.abs(y_true - y_hat)
        
        boot_rmses = [np.sqrt(np.mean(np.random.choice(errors_sq, size=len(errors_sq), replace=True))) for _ in range(1000)]
        rmse_ci = [float(np.percentile(boot_rmses, 2.5)), float(np.percentile(boot_rmses, 97.5))]
        
        boot_maes = [np.mean(np.random.choice(errors_abs, size=len(errors_abs), replace=True)) for _ in range(1000)]
        mae_ci = [float(np.percentile(boot_maes, 2.5)), float(np.percentile(boot_maes, 97.5))]
        
        model_summary[m_key] = {
            'pooled_rmse': float(rmse),
            'pooled_rmse_95ci': rmse_ci,
            'pooled_mae': float(mae),
            'pooled_mae_95ci': mae_ci,
            'pooled_r2': float(r2)
        }
    
    # Statistical tests on subject-level paired differences (M1 vs M2)
    subj_df = pd.DataFrame(subject_metrics)
    diffs = subj_df['delta_rmse_m1_m2'].values
    ttest_res = stats.ttest_rel(subj_df['rmse_m1'], subj_df['rmse_m2'])
    wilcoxon_res = stats.wilcoxon(subj_df['rmse_m1'], subj_df['rmse_m2'])
    
    stat_test = {
        'mean_delta_rmse': float(np.mean(diffs)),
        'std_delta_rmse': float(np.std(diffs)),
        'delta_rmse_95ci': [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
        'paired_ttest_stat': float(ttest_res.statistic),
        'paired_ttest_pvalue': float(ttest_res.pvalue),
        'wilcoxon_stat': float(wilcoxon_res.statistic),
        'wilcoxon_pvalue': float(wilcoxon_res.pvalue),
        'interpretation': "M2 (Agonist+Antagonist) significantly outperforms M1 (Agonist-only)" if ttest_res.pvalue < 0.05 and np.mean(diffs) > 0 else "No statistically significant improvement of M2 over M1 in LOSO generalization"
    }
    
    return {
        'action': action_name,
        'n_trials': len(sub_df),
        'n_subjects': len(subjects),
        'models': model_summary,
        'antagonist_addition_test': stat_test,
        'subject_metrics': subject_metrics
    }

# 1. Knee Extension
df_ext = df[df['action'] == 'extension'].copy()
ext_agonists = ['emg_RF', 'emg_VM', 'emg_VL']
ext_antagonists = ['emg_BF', 'emg_ST']
res_ext = run_loso_evaluation(df_ext, 'Knee Extension', ext_agonists, ext_antagonists)

# 2. Knee Flexion (all trials)
df_flx = df[df['action'] == 'flexion'].copy()
flx_agonists = ['emg_BF', 'emg_ST']
flx_antagonists = ['emg_RF', 'emg_VM', 'emg_VL']
res_flx = run_loso_evaluation(df_flx, 'Knee Flexion (All Trials)', flx_agonists, flx_antagonists)

# 3. Knee Flexion (Clean - excluding outlier HA16 r3 spike of 717 Nm)
df_flx_clean = df[(df['action'] == 'flexion') & (df['torque_nm'] < 400)].copy()
res_flx_clean = run_loso_evaluation(df_flx_clean, 'Knee Flexion (Clean n=121)', flx_agonists, flx_antagonists)

master_results = {
    'experiment_id': 'EXP-0051',
    'experiment_name': 'E1-ISO',
    'dataset': 'DPValid (AMS Acta 7710, DOI: 10.6092/unibo/amsacta/7710)',
    'validation_protocol': 'Leave-One-Subject-Out (LOSO) Cross-Validation (20 folds)',
    'knee_extension': res_ext,
    'knee_flexion_all': res_flx,
    'knee_flexion_clean': res_flx_clean
}

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(master_results, f, indent=2)

print(f"Saved E1 results to {out_json}")

print("\n================== KNEE EXTENSION RESULTS ==================")
for m, vals in res_ext['models'].items():
    print(f"{m:28s}: RMSE = {vals['pooled_rmse']:.2f} Nm (95% CI {vals['pooled_rmse_95ci'][0]:.1f}-{vals['pooled_rmse_95ci'][1]:.1f}) | MAE = {vals['pooled_mae']:.2f} | R2 = {vals['pooled_r2']:.4f}")
print("Antagonist addition test (M1 vs M2):")
print(f"  Delta RMSE: {res_ext['antagonist_addition_test']['mean_delta_rmse']:.2f} Nm")
print(f"  Paired t-test p-value: {res_ext['antagonist_addition_test']['paired_ttest_pvalue']:.4f}")
print(f"  Interpretation: {res_ext['antagonist_addition_test']['interpretation']}")

print("\n============= KNEE FLEXION RESULTS (CLEAN n=121) =============")
for m, vals in res_flx_clean['models'].items():
    print(f"{m:28s}: RMSE = {vals['pooled_rmse']:.2f} Nm (95% CI {vals['pooled_rmse_95ci'][0]:.1f}-{vals['pooled_rmse_95ci'][1]:.1f}) | MAE = {vals['pooled_mae']:.2f} | R2 = {vals['pooled_r2']:.4f}")
print("Antagonist addition test (M1 vs M2):")
print(f"  Delta RMSE: {res_flx_clean['antagonist_addition_test']['mean_delta_rmse']:.2f} Nm")
print(f"  Paired t-test p-value: {res_flx_clean['antagonist_addition_test']['paired_ttest_pvalue']:.4f}")
print(f"  Interpretation: {res_flx_clean['antagonist_addition_test']['interpretation']}")
