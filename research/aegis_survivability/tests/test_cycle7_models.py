"""Unit tests for AEGIS-01 Research Cycle 7: Reproducible Evidence & Cross-Study Validation."""

import csv
import json
import pytest
from pathlib import Path

from aegis.cycle7_validation import (
    FORENSIC_OBSERVATIONS_LEDGER,
    export_forensic_observations_csv,
    evaluate_materials_transfer_framework,
    evaluate_regeneration_loso,
    evaluate_thermoregulation_audit,
    run_cycle7_master_validation,
    predict_keratin_modulus_unscaled,
    predict_keratin_modulus_scaled
)


def test_forensic_evidence_ledger(tmp_path):
    """Verify that all 21 observations are audited and exported with strict provenance."""
    assert len(FORENSIC_OBSERVATIONS_LEDGER) == 21
    
    # Check extraction methods: group aggregates must be distinguished from individual measurements
    group_aggregates = [e for e in FORENSIC_OBSERVATIONS_LEDGER if "GROUP_MEAN" in e.extraction_method or "DIGITIZED" in e.extraction_method]
    assert len(group_aggregates) >= 19
    
    # Check that unverified extrapolation is flagged
    dyn_obs = next(e for e in FORENSIC_OBSERVATIONS_LEDGER if e.observation_id == "OBS-MAT-05")
    assert dyn_obs.verification_status == "NOT_VERIFIED"
    
    # Test CSV export
    csv_file = tmp_path / "test_observations.csv"
    export_forensic_observations_csv(csv_file)
    assert csv_file.exists()
    
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 21


def test_materials_transfer_tests():
    """Verify within-study holdout (Test A), cross-study transfer (Test B), and cross-material transfer (Test C)."""
    res = evaluate_materials_transfer_framework()
    
    # Test A: Within-study holdout (Bertram 1986)
    test_a = res["test_a_within_study"]
    assert test_a["status"] == "PASS"
    assert test_a["error_reduction_pct"] > 60.0
    
    # Test B: Cross-study transfer (Bovine hoof -> Sheep horn)
    test_b = res["test_b_cross_study"]
    assert test_b["status"] == "PASS"
    assert test_b["error_reduction_pct"] > 40.0  # Actually 43.08%
    
    # Test C: Cross-material transfer (Horn -> Pangolin scale)
    # The unscaled horn model MUST FAIL without lamellar scaling
    test_c = res["test_c_cross_material"]
    unscaled = test_c["unscaled_model"]
    assert unscaled["status"] == "FAIL_WITHOUT_LAMELLAR_SCALING"
    assert unscaled["error_reduction_pct"] < 0.0  # Worse than baseline!
    
    # The scaled model with structural parameter passes
    scaled = test_c["scaled_model_with_phi_045"]
    assert scaled["status"] == "PASS_WITH_STRUCTURAL_PARAMETER"
    assert scaled["error_reduction_pct"] > 40.0


def test_regeneration_loso_cross_validation():
    """Verify Leave-One-Study-Out (LOSO) cross-validation for functional muscle recovery."""
    res = evaluate_regeneration_loso()
    assert res["verdict"] == "PASS"
    assert res["total_independent_animals"] == 82
    assert res["total_experimental_cohorts"] == 11
    assert len(res["independent_studies_evaluated"]) == 3
    
    perf = res["overall_performance"]
    assert perf["mechanistic_mae_pct"] < 7.5
    assert perf["mae_reduction_vs_study_mean_pct"] > 50.0
    assert perf["mae_reduction_vs_no_neuro_pct"] > 40.0


def test_thermoregulation_authentic_audit():
    """Verify thermoregulation reproduction under authentic Montain et al. 1994 conditions (v=2.2 m/s)."""
    res = evaluate_thermoregulation_audit()
    assert res["verdict"] == "PARTIAL"
    assert res["environmental_parameters_audited"]["air_velocity_authentic_m_s"] == 2.2
    
    sim = res["authentic_simulations_clo_15"]
    # Model difference must be smaller than physiological measurement uncertainty
    assert sim["difference_exceeds_uncertainty"] is False
    assert sim["model_difference_k_min"] < sim["measurement_uncertainty_sd_k_min"]


def test_cycle7_master_validation_matrix():
    """Verify execution of full Cycle 7 master validation matrix."""
    matrix = run_cycle7_master_validation()
    assert matrix["program"] == "AEGIS-01"
    assert matrix["cycle"] == "Cycle 7"
    
    mandatory = matrix["mandatory_statuses"]
    assert mandatory["PR9_SYNC"] == "PASS"
    assert mandatory["EVIDENCE_PROVENANCE"] in ["PASS", "PARTIAL"]
    assert mandatory["MATERIALS_CROSS_STUDY"] == "PASS"
    assert mandatory["REGENERATION_CROSS_STUDY"] == "PASS"
    assert mandatory["THERMAL_HOLDOUT"] == "PARTIAL"
    assert mandatory["BIOLOGICAL_FEASIBILITY"] == "CONDITIONAL"
