import pandas as pd
import numpy as np
from pathlib import Path
import json
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
import sys

def verify_cycle17():
    print("=== STARTING CYCLE 17 INDEPENDENT VERIFICATION ===")
    
    # 1. Check Data Presence
    dpvalid_csv = Path("D:/SUBJECT-01/research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv")
    bogaerts_csv = Path("D:/SUBJECT-01/research/cycle16/data/bogaerts/bogaerts_2017_data.csv")
    assert dpvalid_csv.exists(), "DPValid CSV missing!"
    assert bogaerts_csv.exists(), "Bogaerts CSV missing!"
    
    df_dp = pd.read_csv(dpvalid_csv)
    df_bog = pd.read_csv(bogaerts_csv)
    
    # 2. Verify E1 Factorial Ablation Recalculation
    ext = df_dp[df_dp['action'] == 'extension'].copy()
    ext['sex_code'] = (ext['sex'] == 'M').astype(float)
    assert len(ext) == 125, f"Expected 125 extension trials, got {len(ext)}"
    assert ext['participant_id'].nunique() == 20, "Expected 20 subjects"
    
    subjects = np.sort(ext['participant_id'].unique())
    alphas = np.logspace(-2, 3, 20)
    
    f0_cols = ['angle_deg', 'mass', 'height', 'age', 'sex_code']
    f3_cols = f0_cols + ['emg_RF', 'emg_VM', 'emg_VL']
    f4_cols = f3_cols + ['emg_BF', 'emg_ST']
    
    preds = {'F0': [], 'F3': [], 'F4': []}
    subj_rmses = {'F0': [], 'F3': [], 'F4': []}
    actuals = []
    
    for s in subjects:
        tr = ext[ext['participant_id'] != s]
        te = ext[ext['participant_id'] == s]
        y_tr = tr['torque_nm'].values
        y_te = te['torque_nm'].values
        
        for k, cols in [('F0', f0_cols), ('F3', f3_cols), ('F4', f4_cols)]:
            sc = StandardScaler()
            X_tr = sc.fit_transform(tr[cols].values)
            X_te = sc.transform(te[cols].values)
            m = RidgeCV(alphas=alphas).fit(X_tr, y_tr)
            p = m.predict(X_te)
            preds[k].extend(p)
            subj_rmses[k].append(np.sqrt(np.mean((y_te - p)**2)))
            
        actuals.extend(y_te)
        
    y_true = np.array(actuals)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    
    rmse_f0 = np.sqrt(np.mean((y_true - np.array(preds['F0']))**2))
    r2_f0 = 1.0 - np.sum((y_true - np.array(preds['F0']))**2) / ss_tot
    
    rmse_f3 = np.sqrt(np.mean((y_true - np.array(preds['F3']))**2))
    rmse_f4 = np.sqrt(np.mean((y_true - np.array(preds['F4']))**2))
    r2_f4 = 1.0 - np.sum((y_true - np.array(preds['F4']))**2) / ss_tot
    
    # Assert F0 alone dominates
    assert rmse_f0 < 50.0, f"F0 RMSE should be < 50 Nm, got {rmse_f0:.2f}"
    assert r2_f0 > 0.68, f"F0 R2 should be > 0.68, got {r2_f0:.4f}"
    assert rmse_f3 > rmse_f0, "Adding agonist EMG should increase RMSE over F0"
    assert rmse_f4 > rmse_f3, "Adding antagonist EMG should increase RMSE over F3"
    
    # Paired test F4 vs F3 (Antagonist noise test)
    t_f4_f3, p_f4_f3 = stats.ttest_rel(subj_rmses['F3'], subj_rmses['F4'])
    assert p_f4_f3 < 0.05, f"Antagonist degradation should be p < 0.05, got {p_f4_f3:.4f}"
    assert np.mean(np.array(subj_rmses['F3']) - np.array(subj_rmses['F4'])) < 0, "F4 should have higher error than F3"
    
    print(f"[PASS] E1 Factorial Ablation verified: F0 RMSE = {rmse_f0:.2f} Nm (R2 = {r2_f0:.4f}). Antagonist degradation p = {p_f4_f3:.4f}")
    
    # 3. Verify E2 Pseudoreplication Correction & Bogaerts Demographics
    demo = df_bog.groupby('participant_id').first()
    n_females = sum(demo['gender'] == 'Female')
    n_males = sum(demo['gender'] == 'Male')
    assert n_females == 4 and n_males == 6, f"Expected 4 Females and 6 Males, got {n_females}F / {n_males}M"
    print(f"[PASS] E2 Demographic audit verified: exactly 4 Females, 6 Males in S1 Table.")
    
    peak_iso = df_bog[(df_bog['time'] == 1) & (df_bog['activation'] == 'ISO')]
    subj_agg = peak_iso.groupby('participant_id')[['disp_sup_mm', 'disp_mid_mm', 'disp_deep_mm', 'strain_sup_pct', 'strain_mid_pct', 'strain_deep_pct']].mean()
    assert len(subj_agg) == 10, f"Expected 10 subjects, got {len(subj_agg)}"
    
    d_sup = subj_agg['disp_sup_mm'].values
    d_mid = subj_agg['disp_mid_mm'].values
    d_deep = subj_agg['disp_deep_mm'].values
    
    # Check that all 10 subjects have deep > mid > sup
    for i in range(10):
        assert d_deep[i] > d_mid[i] > d_sup[i], f"Subject {i+1} does not have deep > mid > sup"
        
    f_disp = stats.friedmanchisquare(d_sup, d_mid, d_deep)
    assert f_disp.statistic == 20.0, f"Expected Friedman statistic 20.0, got {f_disp.statistic}"
    assert f_disp.pvalue < 1e-4, f"Expected p < 0.0001, got {f_disp.pvalue}"
    
    # Check strain non-significance
    f_strain = stats.friedmanchisquare(subj_agg['strain_sup_pct'], subj_agg['strain_mid_pct'], subj_agg['strain_deep_pct'])
    assert f_strain.pvalue > 0.50, f"Subject-level strain should be non-significant (p > 0.50), got {f_strain.pvalue}"
    
    print(f"[PASS] E2 Pseudoreplication fix verified: Disp Q = 20.0 (p = {f_disp.pvalue:.2e}), Strain Q = {f_strain.statistic:.2f} (p = {f_strain.pvalue:.4f} non-sig).")
    
    # 4. Verify JSON artifacts
    for f in ["E1_RESULTS.json", "E2_RESULTS.json", "E5_RESULTS.json"]:
        p = Path("D:/SUBJECT-01/research/cycle17") / f
        assert p.exists(), f"Artifact {f} missing!"
        text = p.read_text(encoding='utf-8')
        assert "NaN" not in text and "Infinity" not in text, f"Non-standard token in {f}"
        d = json.load(open(p, encoding='utf-8'))
        assert len(d) > 0, f"Empty JSON {f}"
    print("[PASS] All cycle 17 JSON artifacts validated.")
    
    print("=== CYCLE 17 VERIFICATION FULLY PASSED ===")
    return True

if __name__ == '__main__':
    verify_cycle17()
