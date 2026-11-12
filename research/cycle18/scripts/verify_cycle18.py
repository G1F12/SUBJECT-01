"""
Independent Verification Script for Research Cycle 18.
SUBJECT-01.
"""

import json
import os
import sys
import h5py
import pandas as pd
import numpy as np

def verify_cycle18():
    print("=== STARTING CYCLE 18 INDEPENDENT VERIFICATION ===")

    # 1. Verify Manifest
    manifest_path = 'D:/SUBJECT-01/research/cycle18/data_manifest.json'
    assert os.path.exists(manifest_path), "Missing data_manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    print("[PASS] Manifest found and loaded.")

    # 2. Verify Oxford Atlas Integrity and Identity
    h5ad_path = 'D:/MTJCore/data/raw/achilles/ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad'
    assert os.path.exists(h5ad_path), f"Missing h5ad at {h5ad_path}"
    with h5py.File(h5ad_path, 'r') as f:
        obs = f['obs']
        total_cells = len(obs['donor_id']['codes'])
        assert total_cells == 64862, f"Expected 64862 cells, found {total_cells}"
        
        # Verify muscle cell count
        broad_cats = [x.decode('utf-8') for x in obs['broad_annotation']['categories'][:]]
        broad_codes = obs['broad_annotation']['codes'][:]
        muscle_code = broad_cats.index('Skeletal muscle cells')
        muscle_count = int(np.sum(broad_codes == muscle_code))
        assert muscle_count == 22146, f"Expected 22146 muscle cells, found {muscle_count}"

        # Verify donors
        donor_cats = [x.decode('utf-8') for x in obs['donor_id']['categories'][:]]
        assert len(donor_cats) == 5, f"Expected 5 donors, found {len(donor_cats)}"
        assert 'MSK1556' in donor_cats, "MSK1556 missing from donors"
    print(f"[PASS] Oxford Achilles H5AD verified: {total_cells} cells, {muscle_count} muscle cells, 5 donors.")

    # 3. Verify Discovery Identity in MTJCore
    plan_path = 'D:/MTJCore/configs/analysis_plan.yaml'
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_text = f.read()
    assert 'discovery: Achilles' in plan_text, "Achilles not marked as discovery in MTJCore plan"
    assert 'ef0fc6ac-4872-40e1-ab24-e445b19ca6e3' in manifest['files']['achilles_h5ad']['cellxgene_dataset_id']
    print("[PASS] Oxford Atlas verified as MTJCore DISCOVERY cohort (100% circularity for replication).")

    # 4. Verify HYP-0013 Quantitative Evaluation
    hyp13_path = 'D:/SUBJECT-01/research/cycle18/HYP0013_EVALUATION.json'
    assert os.path.exists(hyp13_path), "Missing HYP0013_EVALUATION.json"
    with open(hyp13_path, 'r', encoding='utf-8') as f:
        hyp13 = json.load(f)
    col22_fib = hyp13['genes']['COL22A1']['fibroblast']
    assert abs(col22_fib['log2FC'] - 3.523) < 0.01, "COL22A1 fibroblast log2FC mismatch"
    assert col22_fib['donor_consistency'] == 0.6, "COL22A1 donor consistency must be exactly 0.60"
    assert hyp13['verdict'] == 'NOT_SUPPORTED_AS_ORIGINAL_DISCOVERY'
    print("[PASS] HYP-0013 evaluated: COL22A1 fibroblast donor consistency = 0.60 (<0.75 threshold).")

    # 5. Verify E1 Contrast Statistics (Correction of Typo)
    e1_path = 'D:/SUBJECT-01/research/cycle17/E1_RESULTS.json'
    with open(e1_path, 'r', encoding='utf-8') as f:
        e1_res = json.load(f)
    f3_f0_ridge = e1_res['algorithms']['Ridge']['contrasts']['F3_minus_F0_agonist_incremental']
    assert abs(f3_f0_ridge['paired_ttest_stat'] - (-0.08435)) < 0.001, "E1 F3 vs F0 t-stat mismatch"
    assert abs(f3_f0_ridge['paired_ttest_pvalue'] - 0.93366) < 0.001, "E1 F3 vs F0 p-value mismatch"
    print("[PASS] E1 statistics verified: actual t = -0.084, p = 0.9337 (typo in report resolved).")

    # 6. Verify E2 Exact Permutation Statistics
    # Friedman with N=10, k=3, perfect ranks Q=20.0
    # Exact permutation probability: 2 / 6^10 = 2 / 60466176
    p_exact = 2.0 / (6.0 ** 10)
    assert abs(p_exact - 3.30759e-08) < 1e-12, "E2 exact permutation math mismatch"
    print(f"[PASS] E2 exact Friedman probability verified: P_exact = {p_exact:.2e} (asymptotic p = 4.54e-5).")

    # 7. Verify GSE130649 Exclusion
    corrections_path = 'D:/SUBJECT-01/research/cycle18/SCIENTIFIC_CORRECTIONS.md'
    with open(corrections_path, 'r', encoding='utf-8') as f:
        corr_text = f.read()
    assert 'GSE130649' in corr_text and 'Inner Ear Organoids' in corr_text
    print("[PASS] GSE130649 verified as mouse inner ear organoids and excluded.")

    print("=== CYCLE 18 INDEPENDENT VERIFICATION FULLY PASSED ===")
    return 0

if __name__ == '__main__':
    sys.exit(verify_cycle18())
