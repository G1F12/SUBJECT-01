#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SUBJECT-01 Cycle 16: Independent Biomechanics, Tendon Mechanics & MTJ Replication
Verifies artifact integrity, empirical dataset validation, registry updates, and core invariants.
"""

import json
from pathlib import Path
import pytest
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
CYCLE16_DIR = REPO_ROOT / "research" / "cycle16"
REGISTRY_DIR = REPO_ROOT / "registry"


def test_cycle16_artifacts_exist():
    """Verify all mandatory Cycle 16 documents and scripts exist."""
    required_files = [
        "CYCLE15_CORRECTIONS.md",
        "DATASET_VERIFICATION.md",
        "data_manifest.json",
        "E1_ISOMETRIC_STRENGTH.md",
        "E1_MODEL_COMPARISON.json",
        "E1_REPRODUCIBILITY.md",
        "E2_REGIONAL_TENDON.md",
        "E2_RESULTS.json",
        "E5_OXFORD_MTJ.md",
        "E5_RESULTS.json",
        "CROSS_EXPERIMENT_FINDINGS.md",
        "SCIENTIFIC_NOVELTY.md",
        "PUBLICATION_POTENTIAL.md",
        "SUBJECT01_FUNCTIONAL_IMPACT.md",
        "INDEPENDENT_VERIFICATION.md",
        "CYCLE16_FINAL_REPORT_RU.md",
        "scripts/run_e1_iso.py",
        "scripts/run_e2_regional.py",
        "scripts/run_e5_mtj_audit.py",
        "scripts/verify_cycle16.py",
    ]
    for filename in required_files:
        path = CYCLE16_DIR / filename
        assert path.is_file(), f"Missing required Cycle 16 file: {filename}"
        assert path.stat().st_size > 0, f"File is empty: {filename}"


def test_cycle16_empirical_data_integrity():
    """Verify extracted datasets have exact human observations."""
    dpvalid_csv = CYCLE16_DIR / "data" / "dpvalid" / "dpvalid_isometric_trials.csv"
    bogaerts_csv = CYCLE16_DIR / "data" / "bogaerts" / "bogaerts_2017_data.csv"
    
    assert dpvalid_csv.is_file(), "dpvalid_isometric_trials.csv missing!"
    assert bogaerts_csv.is_file(), "bogaerts_2017_data.csv missing!"
    
    df_dp = pd.read_csv(dpvalid_csv)
    df_bog = pd.read_csv(bogaerts_csv)
    
    # DPValid assertions
    assert len(df_dp) == 247, f"Expected 247 DPValid trials, got {len(df_dp)}"
    assert df_dp["participant_id"].nunique() == 20, "Expected 20 DPValid participants"
    assert set(df_dp["action"].unique()) == {"extension", "flexion"}
    
    # Bogaerts assertions
    assert len(df_bog) == 160, f"Expected 160 Bogaerts observations, got {len(df_bog)}"
    assert df_bog["participant_id"].nunique() == 10, "Expected 10 Bogaerts participants"
    assert set(df_bog["activation"].unique()) == {"PAS", "ISO"}


def test_cycle16_e1_iso_metrics():
    """Verify E1-ISO Leave-One-Subject-Out results in E1_MODEL_COMPARISON.json."""
    with open(CYCLE16_DIR / "E1_MODEL_COMPARISON.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    ext = res["knee_extension"]
    assert ext["n_subjects"] == 20
    assert ext["n_trials"] == 125
    
    models = ext["models"]
    m1_rmse = models["M1_agonist"]["pooled_rmse"]
    m2_rmse = models["M2_agonist_antagonist"]["pooled_rmse"]
    m4_rmse = models["M4_demographics_kinematics"]["pooled_rmse"]
    m4_r2 = models["M4_demographics_kinematics"]["pooled_r2"]
    
    # M4 must dominate M1 and M2
    assert m4_rmse < m1_rmse, f"M4 RMSE ({m4_rmse}) should be lower than M1 ({m1_rmse})"
    assert m4_r2 > 0.60, f"M4 R2 ({m4_r2}) should exceed 0.60"
    
    # Antagonist OLS addition test: p > 0.05
    test_res = ext["antagonist_addition_test"]
    assert test_res["paired_ttest_pvalue"] > 0.05, "Paired t-test should not be significant"
    assert test_res["mean_delta_rmse"] < 0, "Unregularized M2 should have higher error on average"


def test_cycle16_e2_regional_metrics():
    """Verify E2-REG regional displacement gradient and tests in E2_RESULTS.json."""
    with open(CYCLE16_DIR / "E2_RESULTS.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    iso_disp = res["results_by_activation"]["ISO"]["disp_mm"]
    d_sup = iso_disp["superficial"]["mean"]
    d_mid = iso_disp["middle"]["mean"]
    d_deep = iso_disp["deep"]["mean"]
    
    # Deep layer displaces more than superficial layer
    assert d_deep > d_mid > d_sup, f"Expected deep > mid > sup displacement: {d_deep}, {d_mid}, {d_sup}"
    
    # Friedman test p-value < 1e-10
    p_disp = res["results_by_activation"]["ISO"]["friedman_layer_effect"]["disp_p_value"]
    assert p_disp < 1e-10, f"Friedman test p-value {p_disp} should be < 1e-10"
    
    # Blocked stress hypothesis
    assert res["hypothesis_status"]["HYP-0010_FULL_VALIDATION_STRESS"] == "BLOCKED_ABSENT_REGIONAL_CSA"


def test_cycle16_e5_mtj_audit():
    """Verify E5-OXFORD-MTJ cell type boundary findings in E5_RESULTS.json."""
    with open(CYCLE16_DIR / "E5_RESULTS.json", "r", encoding="utf-8") as f:
        res = json.load(f)
    
    audit = res["audit_findings"]["cellular_composition"]
    assert audit["myonuclei_present"] is False
    assert audit["stromal_fibroblasts_present"] is True
    assert res["audit_findings"]["karlsen_mtjcore_replication_feasibility"]["feasible"] is False


def test_cycle16_registries_updated():
    """Verify registry entries for EXP, FND, NEG, SRC, and ISS."""
    # Experiments
    with open(REGISTRY_DIR / "experiments.json", "r", encoding="utf-8") as f:
        exps = json.load(f)
    exp_ids = {e["id"] for e in exps}
    assert {"EXP-0051", "EXP-0052", "EXP-0053"} <= exp_ids

    # Findings
    with open(REGISTRY_DIR / "findings.json", "r", encoding="utf-8") as f:
        fnds = json.load(f)
    fnd_ids = {fn["id"] for fn in fnds}
    assert {"FND-0052", "FND-0053", "FND-0054"} <= fnd_ids

    # Negative results
    with open(REGISTRY_DIR / "negative_results.json", "r", encoding="utf-8") as f:
        negs = json.load(f)
    neg_ids = {n["id"] for n in negs}
    assert {"NEG-0048", "NEG-0049", "NEG-0050"} <= neg_ids

    # Sources
    with open(REGISTRY_DIR / "sources.json", "r", encoding="utf-8") as f:
        srcs = json.load(f)
    src_ids = {s["id"] for s in srcs}
    assert {"SRC-0081", "SRC-0082", "SRC-0083"} <= src_ids

    # Issues
    with open(REGISTRY_DIR / "issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)
    iss_map = {i["id"]: i["status"] for i in issues}
    assert iss_map.get("ISS-0022") == "resolved"
    assert iss_map.get("ISS-0023") == "partially_resolved"


def test_cycle16_invariants_preserved():
    """Verify that project invariants are maintained."""
    report_text = (CYCLE16_DIR / "CYCLE16_FINAL_REPORT_RU.md").read_text(encoding="utf-8")
    state_text = (REPO_ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")

    assert "TARGET-CPE45**: НЕ ВАЛИДИРОВАН ВНЕШНЕ" in report_text or "TARGET-CPE45**: НЕ ВАЛИДИРОВАН" in report_text
    assert "Биологические вмешательства**: NO-GO" in report_text
    assert "TARGET-CPE45 = NOT EXTERNALLY VALIDATED" in state_text
    assert "BIOLOGICAL INTERVENTIONS = NO_GO" in state_text
