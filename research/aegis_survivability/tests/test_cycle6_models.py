"""Unit tests for AEGIS-01 Research Cycle 6: Predictive Biology & Independent Holdouts."""

import pytest
from pathlib import Path
import json

from aegis.cycle6_validation import (
    evaluate_biological_materials_holdout,
    evaluate_muscle_regeneration_holdout,
    evaluate_thermoregulation_holdout,
    run_cycle6_master_validation,
    KeratinPhysicoChemicalModel,
    MechanisticVMLRegenerationModel,
    BIOLOGICAL_ABSOLUTES_AUDIT
)


def test_biological_materials_holdout():
    """Verify living protective biological materials model on independent held-out coupons."""
    res = evaluate_biological_materials_holdout()
    assert res["status"] == "PASS"
    assert res["holdout_sample_count"] == 8
    
    # Check that model significantly outperforms simple baseline (> 50% error reduction)
    mod_eval = res["modulus_evaluation"]
    assert mod_eval["beats_baseline"] is True
    assert mod_eval["error_reduction_pct"] > 70.0  # Actually ~84.8%
    assert mod_eval["model_mae_gpa"] < 0.25
    
    ys_eval = res["yield_stress_evaluation"]
    assert ys_eval["beats_baseline"] is True
    assert ys_eval["error_reduction_pct"] > 60.0  # Actually ~79.4%


def test_muscle_regeneration_holdout():
    """Verify functional muscle regeneration model against multi-species VML holdouts."""
    res = evaluate_muscle_regeneration_holdout()
    assert res["status"] == "PASS"
    assert res["specimen_count"] == 11
    
    # Model must beat naive baseline on MAE and RMSE
    assert res["beats_baseline"] is True
    assert res["error_reduction_pct"] > 40.0  # Actually ~53.0%
    assert res["model_performance"]["mae_pct"] < 8.0
    
    # Check that non-human specimens carry TRANSLATIONAL_UNVALIDATED tag
    for r in res["records"]:
        assert r["translational_tag"] == "TRANSLATIONAL_UNVALIDATED"
        
    # Check key biological finding: ECM scaffold alone provides minimal benefit without rehab/cells
    # In 35% defect: untreated is ~41.2%, ECM alone is ~43.5% (diff < 5%)
    untreated_35 = next(r for r in res["records"] if r["specimen_id"] == "VML-RAT-35-UNT")
    ecm_alone_35 = next(r for r in res["records"] if r["specimen_id"] == "VML-RAT-35-ECM")
    assert abs(ecm_alone_35["observed_pct"] - untreated_35["observed_pct"]) < 5.0


def test_thermoregulation_holdout():
    """Verify thermoregulation model under matched Montain et al. (1994) holdout conditions."""
    res = evaluate_thermoregulation_holdout()
    assert res["domain"] == "QUESTION_C_HUMAN_THERMOREGULATION"
    assert res["negative_result_registered"] is True
    assert res["verdict"] == "PARTIAL"
    
    # Both models should yield positive heating rates in uncompensable heat
    assert res["model_1node_baseline"]["425w_pred_rate_k_min"] > 0.03
    assert res["model_3node_dynamic"]["425w_pred_rate_k_min"] > 0.03
    assert res["model_3node_dynamic"]["600w_pred_rate_k_min"] > res["model_3node_dynamic"]["425w_pred_rate_k_min"]


def test_biological_absolutes_rectification():
    """Verify that false biological absolutes are formally downgraded or invalidated."""
    assert len(BIOLOGICAL_ABSOLUTES_AUDIT) == 6
    
    ids = [entry["absolute_id"] for entry in BIOLOGICAL_ABSOLUTES_AUDIT]
    assert "ABS-01-SATELLITE-DIVISIONS" in ids
    assert "ABS-02-DIFFUSION-DEATH-200UM" in ids
    assert "ABS-03-GUARANTEED-ARCH-BIO" in ids
    assert "ABS-04-HIGH-ENERGY-IMPOSSIBILITY" in ids
    assert "ABS-05-ZERO-BIOHYBRID-COST" in ids
    assert "ABS-06-EXACT-KINEMATICS-UNCALIBRATED" in ids
    
    # Check statuses
    statuses = {e["absolute_id"]: e["revised_status"] for e in BIOLOGICAL_ABSOLUTES_AUDIT}
    assert statuses["ABS-01-SATELLITE-DIVISIONS"] == "DOWNGRADED"
    assert statuses["ABS-02-DIFFUSION-DEATH-200UM"] == "DOWNGRADED"
    assert statuses["ABS-03-GUARANTEED-ARCH-BIO"] == "DOWNGRADED"
    assert statuses["ABS-04-HIGH-ENERGY-IMPOSSIBILITY"] == "DOWNGRADED"
    assert statuses["ABS-05-ZERO-BIOHYBRID-COST"] == "INVALIDATED"
    assert statuses["ABS-06-EXACT-KINEMATICS-UNCALIBRATED"] == "INVALIDATED"


def test_cycle6_master_validation():
    """Verify execution of full Cycle 6 master validation matrix."""
    matrix = run_cycle6_master_validation()
    assert matrix["program"] == "AEGIS-01"
    assert matrix["cycle"] == "Cycle 6"
    
    mandatory = matrix["mandatory_statuses"]
    assert mandatory["PR9_UPDATED"] == "YES"
    assert mandatory["CROSS_REPO_REGISTRY"] == "PASS"
    assert mandatory["MATERIALS_EXTERNAL_VALIDATION"] == "PASS"
    assert mandatory["REGENERATION_EXTERNAL_VALIDATION"] == "PASS"
    assert mandatory["THERMAL_EXTERNAL_VALIDATION"] == "PARTIAL"
    assert mandatory["BIOLOGICAL_ARCHITECTURE"] == "CONDITIONAL"
    assert mandatory["CYCLE_7_READY"] == "YES"
    
    # Check quantitative metrics
    metrics = matrix["quantitative_metrics"]
    assert metrics["new_independently_tested_experimental_results"] >= 20
    assert metrics["scientifically_refuted_hypotheses"] >= 5
