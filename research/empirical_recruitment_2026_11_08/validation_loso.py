#!/usr/bin/env python3
"""
SUBJECT-01 — Research Cycle 9 (Data Integrity Repair)
Computational Demonstration of Cross-Subject Parameter Transfer vs Real Validation Blocker.

CRITICAL INTEGRITY CORRECTION:
The functions below evaluate synthetic exponential curves for methodological simulation.
THEY ARE NOT REAL EMPIRICAL HUMAN TIME SERIES.
EXP-0040 is officially reclassified as:
SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED.
Independent empirical validation is BLOCKED_PENDING_RAW_DATA.
"""

import numpy as np
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

def generate_synthetic_rehman_time_series():
    """
    Generate SYNTHETIC exponential simulation curve based on published Table 1 rates.
    NOTE: This is a synthetic curve generated for algorithmic demonstration, NOT real raw data.
    """
    t_rec = np.arange(0.0, 366.0, 6.0)
    delta_pcr = 33.6 * 0.272
    pcr_0 = 33.6 - delta_pcr
    k_s = 1.53 / 60.0
    rng = np.random.RandomState(42)
    noise = rng.normal(0.0, 0.6, size=len(t_rec))
    pcr_synthetic = pcr_0 + delta_pcr * (1.0 - np.exp(-k_s * t_rec)) + noise
    return t_rec, pcr_synthetic, pcr_0, 33.6, 39.22

def generate_synthetic_franke_time_series():
    """
    Generate SYNTHETIC exponential simulation curve based on Franke 2020 published tau.
    NOTE: This is a synthetic curve generated for algorithmic demonstration, NOT real raw data.
    """
    t_rec = np.arange(0.0, 56.0, 2.0)
    delta_pcr = 33.6 * 0.44
    pcr_0 = 33.6 - delta_pcr
    tau = 24.3
    rng = np.random.RandomState(123)
    noise = rng.normal(0.0, 0.7, size=len(t_rec))
    pcr_synthetic = pcr_0 + delta_pcr * (1.0 - np.exp(-t_rec / tau)) + noise
    return t_rec, pcr_synthetic, pcr_0, 33.6, tau

def evaluate_predictions(y_true, y_pred):
    """Compute RMSE, MAE, and R2 on demonstration arrays."""
    rmse = float(np.sqrt(np.mean((y_true - y_pred)**2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    ss_tot = float(np.sum((y_true - np.mean(y_true))**2))
    ss_res = float(np.sum((y_true - y_pred)**2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 1e-6 else 0.0
    return {'rmse_mM': round(rmse, 3), 'mae_mM': round(mae, 3), 'r2': round(r2, 3)}

def run_synthetic_loso_demonstration():
    """
    Execute computational demonstration of LOSO cross-validation.
    Retains numerical execution for historical reproducibility, but tags all outputs
    strictly as synthetic computational demonstration.
    """
    t_franke, y_franke_syn, p0_franke, prest_franke, tau_franke = generate_synthetic_franke_time_series()
    t_rehman, y_rehman_syn, p0_rehman, prest_rehman, tau_rehman = generate_synthetic_rehman_time_series()
    
    # FOLD 1 (Synthetic)
    pred_m0_fold1 = np.full_like(y_rehman_syn, np.mean(y_franke_syn))
    metrics_m0_fold1 = evaluate_predictions(y_rehman_syn, pred_m0_fold1)
    
    pred_m1_fold1 = p0_rehman + (prest_rehman - p0_rehman) * (1.0 - np.exp(-t_rehman / tau_franke))
    metrics_m1_fold1 = evaluate_predictions(y_rehman_syn, pred_m1_fold1)
    
    pred_m1_ref_fold1 = p0_rehman + (prest_rehman - p0_rehman) * (1.0 - np.exp(-t_rehman / tau_rehman))
    metrics_m1_ref_fold1 = evaluate_predictions(y_rehman_syn, pred_m1_ref_fold1)
    
    pred_m2_fold1 = p0_rehman + (prest_rehman - p0_rehman) * (1.0 - np.exp(-t_rehman / (tau_franke * 1.05)))
    metrics_m2_fold1 = evaluate_predictions(y_rehman_syn, pred_m2_fold1)
    
    # FOLD 2 (Synthetic)
    pred_m0_fold2 = np.full_like(y_franke_syn, np.mean(y_rehman_syn))
    metrics_m0_fold2 = evaluate_predictions(y_franke_syn, pred_m0_fold2)
    
    pred_m1_fold2 = p0_franke + (prest_franke - p0_franke) * (1.0 - np.exp(-t_franke / tau_rehman))
    metrics_m1_fold2 = evaluate_predictions(y_franke_syn, pred_m1_fold2)
    
    pred_m1_ref_fold2 = p0_franke + (prest_franke - p0_franke) * (1.0 - np.exp(-t_franke / tau_franke))
    metrics_m1_ref_fold2 = evaluate_predictions(y_franke_syn, pred_m1_ref_fold2)
    
    pred_m2_fold2 = p0_franke + (prest_franke - p0_franke) * (1.0 - np.exp(-t_franke / (tau_rehman * 0.95)))
    metrics_m2_fold2 = evaluate_predictions(y_franke_syn, pred_m2_fold2)
    
    degradation_fold1 = round((metrics_m1_fold1['rmse_mM'] - metrics_m1_ref_fold1['rmse_mM']) / metrics_m1_ref_fold1['rmse_mM'] * 100, 1)
    degradation_fold2 = round((metrics_m1_fold2['rmse_mM'] - metrics_m1_ref_fold2['rmse_mM']) / metrics_m1_ref_fold2['rmse_mM'] * 100, 1)
    
    results = {
        "experiment_id": "EXP-0040",
        "validation_design": "SYNTHETIC_DEMONSTRATION_LOSO_ALGORITHM_ONLY",
        "data_type": "SYNTHETIC",
        "source_provenance": "Generated via numpy random state and published exponential rate constants",
        "validation_status": "SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED",
        "empirical_validation_blocker": "Real raw spectral time-series are unavailable programmatically from Dryad (HTTP 403 WAF barrier). No real empirical continuous time-series exists for out-of-sample testing.",
        "synthetic_metrics_retained_for_historical_record": {
            "fold_1_synthetic_quad_test": {
                "M0_null": metrics_m0_fold1,
                "M1_transferred": metrics_m1_fold1,
                "M1_in_sample": metrics_m1_ref_fold1,
                "M2_transferred": metrics_m2_fold1,
                "synthetic_rmse_degradation_percent": degradation_fold1
            },
            "fold_2_synthetic_calf_test": {
                "M0_null": metrics_m0_fold2,
                "M1_transferred": metrics_m1_fold2,
                "M1_in_sample": metrics_m1_ref_fold2,
                "M2_transferred": metrics_m2_fold2,
                "synthetic_rmse_degradation_percent": degradation_fold2
            },
            "overall_synthetic_cross_rmse": round(float((metrics_m1_fold1['rmse_mM'] + metrics_m1_fold2['rmse_mM']) / 2.0), 3),
            "in_sample_synthetic_rmse": round(float((metrics_m1_ref_fold1['rmse_mM'] + metrics_m1_ref_fold2['rmse_mM']) / 2.0), 3)
        },
        "epistemic_warning": "DO NOT INTERPRET THESE METRICS AS EMPIRICAL EVIDENCE. They illustrate the mathematical behavior of parameter transfer between two different kinetic rates (tau=24.3 s vs tau=39.2 s) on synthetic data."
    }
    
    out_file = OUT_DIR / 'validation_loso_results.json'
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Saved: {out_file} ({out_file.stat().st_size} bytes)")
    return results

if __name__ == '__main__':
    run_synthetic_loso_demonstration()

# Backward compatibility alias
run_loso_cross_validation = run_synthetic_loso_demonstration
