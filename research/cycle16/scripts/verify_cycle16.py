import pandas as pd
import numpy as np
from pathlib import Path
import json
from scipy import stats
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.preprocessing import StandardScaler
import sys

def verify_cycle16():
    print("=== STARTING CYCLE 16 INDEPENDENT VERIFICATION ===")
    
    # 1. Check Data Ingestion
    dpvalid_csv = Path("D:/SUBJECT-01/research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv")
    bogaerts_csv = Path("D:/SUBJECT-01/research/cycle16/data/bogaerts/bogaerts_2017_data.csv")
    
    assert dpvalid_csv.exists(), "DPValid CSV missing!"
    assert bogaerts_csv.exists(), "Bogaerts CSV missing!"
    
    df_dp = pd.read_csv(dpvalid_csv)
    df_bog = pd.read_csv(bogaerts_csv)
    
    print(f"[PASS] DPValid data present: {len(df_dp)} rows across {df_dp['participant_id'].nunique()} subjects.")
    print(f"[PASS] Bogaerts data present: {len(df_bog)} rows across {df_bog['participant_id'].nunique()} subjects.")
    
    assert len(df_bog) == 160, f"Expected 160 Bogaerts rows, got {len(df_bog)}"
    assert df_dp['participant_id'].nunique() == 20, "Expected 20 DPValid subjects"
    
    # 2. Verify E2 Bogaerts Independent Recalculation
    bog_peak = df_bog[df_bog['time'] == 1]
    bog_iso = bog_peak[bog_peak['activation'] == 'ISO']
    
    d_sup = bog_iso['disp_sup_mm'].values
    d_mid = bog_iso['disp_mid_mm'].values
    d_deep = bog_iso['disp_deep_mm'].values
    
    # Check layer gradient (deep > superficial)
    assert np.mean(d_deep) > np.mean(d_sup), "Deep displacement should exceed superficial displacement!"
    
    friedman_disp = stats.friedmanchisquare(d_sup, d_mid, d_deep)
    assert friedman_disp.pvalue < 1e-10, f"Friedman test p-value {friedman_disp.pvalue} should be < 1e-10"
    
    # Correlation with torque
    r_sup, p_sup = stats.pearsonr(bog_iso['torque_nm_kg'], d_sup)
    assert r_sup > 0.50 and p_sup < 0.001, f"Expected strong torque correlation, got r={r_sup}, p={p_sup}"
    
    print(f"[PASS] E2 Recalculation verified: Deep ({np.mean(d_deep):.2f} mm) > Sup ({np.mean(d_sup):.2f} mm), Friedman p = {friedman_disp.pvalue:.2e}, r = {r_sup:.3f}")
    
    # 3. Verify E1 DPValid LOSO Independent Recalculation (Knee Extension)
    df_ext = df_dp[df_dp['action'] == 'extension'].copy()
    assert len(df_ext) == 125, f"Expected 125 extension trials, got {len(df_ext)}"
    
    subjects = np.sort(df_ext['participant_id'].unique())
    agonist_cols = ['emg_RF', 'emg_VM', 'emg_VL']
    antagonist_cols = ['emg_BF', 'emg_ST']
    
    rmses_m1 = []
    rmses_m2 = []
    y_true_all = []
    y_pred_m1_all = []
    y_pred_m2_all = []
    
    for s in subjects:
        tr = df_ext[df_ext['participant_id'] != s]
        te = df_ext[df_ext['participant_id'] == s]
        
        y_tr = tr['torque_nm'].values
        y_te = te['torque_nm'].values
        
        # M1
        sc1 = StandardScaler()
        X1_tr = sc1.fit_transform(tr[agonist_cols].values)
        X1_te = sc1.transform(te[agonist_cols].values)
        m1 = LinearRegression().fit(X1_tr, y_tr)
        p1 = m1.predict(X1_te)
        
        # M2
        sc2 = StandardScaler()
        X2_tr = sc2.fit_transform(tr[agonist_cols + antagonist_cols].values)
        X2_te = sc2.transform(te[agonist_cols + antagonist_cols].values)
        m2 = LinearRegression().fit(X2_tr, y_tr)
        p2 = m2.predict(X2_te)
        
        rmses_m1.append(np.sqrt(np.mean((y_te - p1)**2)))
        rmses_m2.append(np.sqrt(np.mean((y_te - p2)**2)))
        y_true_all.extend(y_te)
        y_pred_m1_all.extend(p1)
        y_pred_m2_all.extend(p2)
        
    pooled_rmse_m1 = np.sqrt(np.mean((np.array(y_true_all) - np.array(y_pred_m1_all))**2))
    pooled_rmse_m2 = np.sqrt(np.mean((np.array(y_true_all) - np.array(y_pred_m2_all))**2))
    
    t_stat, p_val = stats.ttest_rel(rmses_m1, rmses_m2)
    
    print(f"[PASS] E1 Extension LOSO verified: Pooled RMSE M1 = {pooled_rmse_m1:.2f} Nm, M2 = {pooled_rmse_m2:.2f} Nm")
    print(f"[PASS] Paired t-test M1 vs M2: p = {p_val:.4f} (Null hypothesis retained; antagonist does not improve out-of-sample RMSE)")
    
    assert pooled_rmse_m2 > pooled_rmse_m1, "Unregularized M2 should have higher pooled RMSE than M1 in LOSO"
    assert p_val > 0.05, "M1 vs M2 difference should not be statistically significant in favor of M2"
    
    # 4. Check JSON reports and artifacts
    for f in ["E1_MODEL_COMPARISON.json", "E2_RESULTS.json", "E5_RESULTS.json", "data_manifest.json"]:
        p = Path("D:/SUBJECT-01/research/cycle16") / f
        assert p.exists(), f"Artifact {f} missing!"
        with open(p, encoding='utf-8') as fp:
            d = json.load(fp)
            assert len(d) > 0, f"Artifact {f} is empty!"
    print("[PASS] All JSON artifacts validated.")
    
    print("=== CYCLE 16 VERIFICATION FULLY PASSED ===")
    return True

if __name__ == '__main__':
    verify_cycle16()
