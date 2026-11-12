#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SUBJECT-01 Cycle 17: Independent Scientific Correction, Statistical Reanalysis & MTJ Validation
Verifies artifact integrity, factorial feature ablation, pseudoreplication fix, registry updates, and core invariants.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CYCLE17_DIR = REPO_ROOT / "research" / "cycle17"
REGISTRY_DIR = REPO_ROOT / "registry"


def test_cycle17_artifacts_exist():
    """Verify all mandatory Cycle 17 documents and scripts exist."""
    required_files = [
        "CYCLE16_FORENSIC_AUDIT.md",
        "E1_FEATURE_ABLATION.md",
        "E1_RESULTS.json",
        "E2_STATISTICAL_CORRECTION.md",
        "E2_RESULTS.json",
        "E5_OXFORD_REASSESSMENT.md",
        "E5_RESULTS.json",
        "INDEPENDENT_VERIFICATION.md",
        "NOVELTY_AND_PUBLICATION.md",
        "FUNCTIONAL_IMPACT.md",
        "CYCLE17_FINAL_REPORT_RU.md",
        "scripts/run_e1_factorial_ablation.py",
        "scripts/run_e2_statistical_correction.py",
        "scripts/run_e5_reassessment.py",
        "scripts/verify_cycle17.py",
    ]
    for filename in required_files:
        path = CYCLE17_DIR / filename
        assert path.is_file(), f"Missing required Cycle 17 file: {filename}"
        assert path.stat().st_size > 0, f"File is empty: {filename}"


def test_cycle17_e1_factorial_ablation_metrics():
    """Verify E1 Factorial Ablation proves anthropometric dominance and antagonist noise."""
    with open(CYCLE17_DIR / "E1_RESULTS.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    ridge_models = res["algorithms"]["Ridge"]
    f0_res = ridge_models["F0"]
    f3_res = ridge_models["F3"]
    f4_res = ridge_models["F4"]
    
    # F0 dominance
    assert f0_res["pooled_rmse"] < 50.0, f"F0 RMSE should be < 50 Nm, got {f0_res['pooled_rmse']}"
    assert f0_res["pooled_r2"] > 0.68, f"F0 R2 should exceed 0.68, got {f0_res['pooled_r2']}"
    
    # EMG noise penalty
    assert f3_res["pooled_rmse"] > f0_res["pooled_rmse"], "Adding agonist EMG should increase error"
    assert f4_res["pooled_rmse"] > f3_res["pooled_rmse"], "Adding antagonist EMG should increase error"
    
    # Antagonist degradation contrast F4 vs F3
    contrast_f4_f3 = ridge_models["contrasts"]["F4_minus_F3_antagonist_incremental"]
    assert contrast_f4_f3["paired_ttest_pvalue"] < 0.05, "Antagonist noise should be statistically significant"
    assert contrast_f4_f3["mean_delta_rmse"] < 0.0, "Delta RMSE should be negative (F4 worse than F3)"


def test_cycle17_e2_pseudoreplication_fix():
    """Verify E2 subject-level aggregation fixes pseudoreplication and reveals strain non-significance."""
    with open(CYCLE17_DIR / "E2_RESULTS.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    # Demographics audit
    true_sex = res["demographic_audit"]["sex_distribution_true"]
    assert true_sex.get("Male") == 6 and true_sex.get("Female") == 4, f"Expected 6M/4F, got {true_sex}"
    
    # Corrected subject-level ISO
    iso = res["analysis"]["ISO"]["corrected_subject_level_n10"]
    assert iso["n_subjects"] == 10
    
    # Displacement Friedman Q must be 20.0
    assert iso["friedman_disp_stat"] == 20.0
    assert iso["friedman_disp_pvalue"] < 1e-4
    
    # Paired displacement difference > 0
    diff = iso["paired_diff_deep_minus_sup_mm"]
    assert diff["mean"] > 0.50
    assert diff["paired_ttest_pvalue"] < 0.01
    
    # Strain omnibus test must be NON-SIGNIFICANT (p > 0.50)
    assert iso["friedman_strain_pvalue"] > 0.50, f"Strain p-value should be non-significant, got {iso['friedman_strain_pvalue']}"


def test_cycle17_e5_reassessment():
    """Verify E5 corrects the zero-myonuclei claim and documents replication blockage."""
    with open(CYCLE17_DIR / "E5_RESULTS.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    assert res["cycle16_audit"]["audit_classification"] == "CONTRADICTED"
    assert res["replication_feasibility_assessment"]["myonuclear_mtjcore_replication_status"] == "BLOCKED"
    assert res["new_hypothesis_demarcation"]["new_hypothesis"].startswith("HYP-0013")


def test_cycle17_registries_updated():
    """Verify registry entries for EXP, FND, NEG, HYP, and ISS."""
    # Experiments
    with open(REGISTRY_DIR / "experiments.json", "r", encoding="utf-8") as f:
        exps = json.load(f)
    exp_ids = {e["id"] for e in exps}
    assert {"EXP-0054", "EXP-0055", "EXP-0056"} <= exp_ids

    # Findings
    with open(REGISTRY_DIR / "findings.json", "r", encoding="utf-8") as f:
        fnds = json.load(f)
    fnd_ids = {fn["id"] for fn in fnds}
    assert {"FND-0055", "FND-0056", "FND-0057"} <= fnd_ids

    # Negative results
    with open(REGISTRY_DIR / "negative_results.json", "r", encoding="utf-8") as f:
        negs = json.load(f)
    neg_ids = {n["id"] for n in negs}
    assert {"NEG-0051", "NEG-0052", "NEG-0053"} <= neg_ids

    # Hypotheses
    with open(REGISTRY_DIR / "hypotheses.json", "r", encoding="utf-8") as f:
        hyps = json.load(f)
    hyp_ids = {h["id"] for h in hyps}
    assert "HYP-0013" in hyp_ids

    # Issues
    with open(REGISTRY_DIR / "issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)
    iss_ids = {i["id"] for i in issues}
    assert "ISS-0025" in iss_ids


def test_cycle17_invariants_preserved():
    """Verify that project invariants are maintained."""
    report_text = (CYCLE17_DIR / "CYCLE17_FINAL_REPORT_RU.md").read_text(encoding="utf-8")
    state_text = (REPO_ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")

    assert "CPE45_EXTERNALLY_VALIDATED = NO" in report_text
    assert "BIOLOGICAL_AUGMENTATION_GO = NO" in report_text
    assert "STRENGTH_PLUS_20_VALIDATED = NO" in report_text

    assert "TARGET-CPE45 = NOT EXTERNALLY VALIDATED" in state_text
    assert "BIOLOGICAL INTERVENTIONS = NO_GO" in state_text
