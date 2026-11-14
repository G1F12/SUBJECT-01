#!/usr/bin/env python3
"""
Self-contained independent verification script for SUBJECT-01
functional mechanics re-validation.
Checks mathematical derivations, statistical tests, and invariants from first principles.
"""
import sys
import json
from pathlib import Path
import numpy as np

ROOT = Path("D:/SUBJECT-01")
OUT_DIR = ROOT / "research/functional_mechanics_validation"

def verify_all():
    problems = []
    
    # 1. Verify Muscle Double-Cosine Artifact
    th0_rad = np.radians(14.0)
    cos_th0 = np.cos(th0_rad)
    ratio_double_vs_single = 1.0 / cos_th0
    expected_ratio = 1.0306
    if abs(ratio_double_vs_single - expected_ratio) > 0.001:
        problems.append(f"Double cosine ratio mismatch: {ratio_double_vs_single}")
        
    sigma_flawed = 27.22
    sigma_corrected = sigma_flawed * cos_th0
    if abs(sigma_corrected - 26.41) > 0.05:
        problems.append(f"Corrected sigma mismatch: {sigma_corrected} vs 26.41")
        
    # 2. Verify Isomass Scaling Math
    # Constant thickness aponeurosis model:
    f_rel_18 = np.sin(np.radians(36.0)) / np.sin(np.radians(28.0))
    if abs((f_rel_18 - 1.0) * 100.0 - 25.20) > 0.05:
        problems.append(f"Isomass force gain mismatch: {f_rel_18}")
        
    lf_ratio = np.sin(np.radians(14.0)) / np.sin(np.radians(18.0))
    vmax_loss = (1.0 - lf_ratio) * 100.0
    if abs(vmax_loss - 21.71) > 0.05:
        problems.append(f"Isomass vmax loss mismatch: {vmax_loss}")
        
    # Peak power product:
    pmax_change = (f_rel_18 * lf_ratio - 1.0) * 100.0
    if abs(pmax_change - (-1.98)) > 0.05:
        problems.append(f"Isomass peak power change mismatch: {pmax_change}")
        
    # Simple cosine model with lf = 6.71 cm:
    f_gain_simple_cosine = (1.252 * np.cos(np.radians(18.0)) / np.cos(np.radians(14.0)) - 1.0) * 100.0
    if abs(f_gain_simple_cosine - 22.70) > 0.05:
        problems.append(f"Simple cosine gain mismatch: {f_gain_simple_cosine}")
        
    # 3. Verify Tendon Fatigue Formulas
    # Power-law with B = 8.45:
    ret_pow = 1.20 ** (-8.45)
    loss_pow = (1.0 - ret_pow) * 100.0
    if abs(loss_pow - 78.58) > 0.1:
        problems.append(f"Power law loss mismatch: {loss_pow}")
        
    # Semi-log with slope -10.808:
    delta_s = (46.15 - 38.46) / 95.0
    log_drop = -10.808 * delta_s
    ret_semi = 10.0 ** log_drop
    loss_semi = (1.0 - ret_semi) * 100.0
    if abs(loss_semi - 86.67) > 0.1:
        problems.append(f"Semi-log loss mismatch: {loss_semi}")
        
    # 4. Verify Case 2C Adapted Stress Arithmetic
    f_plus20 = 4000.0 * 1.20 # 4800 N
    csa_adapted = 104.0 * 1.15 # 119.6 mm2
    sigma_adapted = f_plus20 / csa_adapted # 40.1338 MPa
    if abs(sigma_adapted - 40.13) > 0.02:
        problems.append(f"Case 2C adapted stress mismatch: {sigma_adapted}")
        
    # Check origin of 34.78 MPa error:
    sigma_flawed_calc = 4000.0 / 115.0 # 34.7826 MPa
    if abs(sigma_flawed_calc - 34.78) > 0.02:
        problems.append(f"34.78 error origin mismatch: {sigma_flawed_calc}")
        
    # 5. Verify Iso-durability Conservation Invariant
    # (1 + d_CSA) * (1 + d_UTS) >= 1.20
    # For Case 2C: 1.15 * 1.10 = 1.265 >= 1.20 (Safe!)
    if (1.15 * 1.10) < 1.20:
        problems.append("Case 2C fails conservation invariant")
        
    if problems:
        print("INDEPENDENT VERIFICATION FAILED:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
        
    print("ALL INDEPENDENT VERIFICATION CHECKS PASSED (100% SUCCESS)!")
    return True

if __name__ == '__main__':
    verify_all()
