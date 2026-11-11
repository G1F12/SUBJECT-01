"""
Unit tests for AEGIS-01 Cycle 8 models and validation engine.
"""

import pytest
from aegis.cycle8_models import (
    audit_keratin_hydration_math,
    evaluate_keratin_materials_transfer,
    evaluate_regeneration_rigorous,
    evaluate_thermal_sensitivity_matrix,
    run_thermal_cpe45_simulation,
    predict_tier1_constant,
    predict_tier2_hydration_only,
    predict_tier3_hydration_rate,
    predict_tier4_microarchitecture,
    KERATIN_TRANSFER_DATASET,
    run_cycle8_master_validation
)


def test_phase1_keratin_mathematical_audit():
    res = audit_keratin_hydration_math()
    assert res["verdict"] == "RECONCILED"
    tp = res["two_point_fit"]
    assert pytest.approx(tp["calculated_kw"], abs=0.01) == 7.59
    assert pytest.approx(tp["extrapolated_e0_gpa"], abs=0.01) == 8.54
    emp = res["empirical_benchmark"]
    assert emp["measured_oven_dry_modulus_gpa"] == 4.60
    assert emp["discrepancy_factor"] > 1.80  # 8.54 / 4.60 ~ 1.85


def test_phase2_tier4_microarchitecture_transfer():
    res = evaluate_keratin_materials_transfer()
    assert res["dataset_summary"]["total_specimens"] == 14
    
    # Check that Tier 4 achieves significant error reduction on held-out pangolin scale
    folds = {f["held_out_material"]: f for f in res["loso_lomo_folds"]}
    assert "pangolin" in folds
    pang_fold = folds["pangolin"]
    assert pang_fold["tier4_mae_gpa"] < 0.40
    assert pang_fold["tier4_error_reduction_pct"] > 70.0
    assert pang_fold["tier4_outperforms_tier2"] is True
    
    overall = res["overall_loso_lomo_performance"]
    assert overall["tier4_mae_gpa"] < overall["tier2_mae_gpa"]
    assert overall["tier4_overall_error_reduction_pct"] > 50.0


def test_phase3_functional_regeneration_strict_loso():
    res = evaluate_regeneration_rigorous()
    meta = res["metadata"]
    assert meta["total_independent_cohort_means"] == 11
    assert meta["total_experimental_animals"] == 82
    
    overall = res["overall_evaluation"]
    # Strict dynamic LOSO should maintain low error ~ 6.02%
    assert overall["strict_dynamic_loso_mae"] < 8.00
    assert overall["strict_loso_error_reduction_pct"] > 50.0
    
    # Translation to human must be flagged as INSUFFICIENT_EVIDENCE
    assert res["translational_scaling_verdict"]["status"] == "INSUFFICIENT_EVIDENCE"


def test_phase4_thermal_sensitivity_sweeps():
    res = evaluate_thermal_sensitivity_matrix()
    sweeps = res["sensitivity_sweeps"]
    
    # Metabolic power sweep: 300W vs 900W
    assert sweeps["metabolic_power"]["m_300w"]["final_core_temp_c"] < 39.0
    assert sweeps["metabolic_power"]["m_900w"]["final_core_temp_c"] > 43.0
    
    # Open skin sweep: 0% vs 40%
    temp_0 = sweeps["open_skin_fraction"]["open_0pct"]["final_core_temp_c"]
    temp_40 = sweeps["open_skin_fraction"]["open_40pct"]["final_core_temp_c"]
    assert temp_0 > temp_40
    
    # Sensitivity ranking check: Metabolic power dominant
    ranking = res["sensitivity_ranking"]
    assert ranking[0]["parameter"] == "Metabolic Power (M)"
    assert ranking[0]["impact"] == "DOMINANT"


def test_phase6_master_validation_matrix():
    matrix = run_cycle8_master_validation()
    statuses = matrix["mandatory_statuses"]
    assert statuses["PR9_SYNC"] == "PASS"
    assert statuses["EVIDENCE_PROVENANCE"] == "PASS"
    assert statuses["MATERIALS_CROSS_STUDY"] == "PASS"
    assert statuses["REGENERATION_CROSS_STUDY"] == "PASS"
    assert statuses["THERMAL_HOLDOUT"] == "PASS"
    assert statuses["BIOLOGICAL_FEASIBILITY"] == "CONDITIONAL"
