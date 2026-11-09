"""Test suite for Aegis External Validation & Forensic Verification Engine (Cycle 4C).

Tests the forensic re-evaluation across the three validation tracks:
- Track 1: Authentic Dziki et al. 2016 Human VML Cohort (N=13, LOPO-CV)
- Track 2: Biological Materials Mechanics (Input Calibration vs Genuine Derived Predictions)
- Track 3: Human Thermoregulation (Three-Tier Classification: Conservation, ISO, Human Data)
"""

import pytest
from aegis.external_validation import (
    evaluate_track_1_muscle_recovery,
    evaluate_track_2_materials,
    evaluate_track_3_thermoregulation,
    run_all_validation_tracks
)


def test_track_1_authentic_dziki_vml_evaluation():
    """Verify Track 1 evaluates authentic Dziki et al. 2016 IPD (N=13) without synthetic records."""
    res = evaluate_track_1_muscle_recovery()
    assert res["track_id"] == "TRACK-1-HUMAN-MUSCLE-VML"
    assert res["cohort_size"] == 13
    assert res["forensic_verdict"] == "PARTIAL"
    
    # Authentic observed mean from Dziki 2016 Table 2 is 37.34% +/- 44.62%
    assert res["observed_mean_improvement_pct"] == pytest.approx(37.34, abs=0.2)
    assert res["observed_sd_improvement_pct"] == pytest.approx(44.62, abs=0.5)
    
    # Patient S12 is confirmed to have negative change (-2.30% mean), NOT +112.4%
    p12 = next(p for p in res["patient_records"] if p["patient_id"] == "S12")
    assert p12["observed_pct"] == pytest.approx(-2.30, abs=0.1)
    assert p12["cause"] == "Electrocution"
    
    # Check model performance and LOPO-CV error metrics
    assert res["model_performance"]["mae"] == pytest.approx(25.74, abs=0.5)
    assert res["model_performance"]["rmse"] == pytest.approx(42.00, abs=0.5)
    assert res["lopo_cross_validation"]["lopo_mae"] == pytest.approx(36.21, abs=0.5)


def test_track_2_biomaterials_data_leakage_separation():
    """Verify Track 2 separates circular calibration constants from genuine derived predictions."""
    res = evaluate_track_2_materials()
    assert res["track_id"] == "TRACK-2-BIOMATERIALS-MECHANICS"
    assert res["forensic_verdict"] == "PARTIAL"
    assert res["calibration_constants_count"] == 11
    assert res["genuine_predictions_count"] == 3
    
    # Genuine predictions error is ~9.15%, NOT artificial 0.50%
    assert res["mean_genuine_prediction_error_pct"] == pytest.approx(9.15, abs=0.5)
    assert res["genuine_predictions_within_1sigma"] is True


def test_track_3_thermoregulation_three_tiers():
    """Verify Track 3 evaluates conservation, ISO reference agreement, and live human literature."""
    res = evaluate_track_3_thermoregulation()
    assert res["track_id"] == "TRACK-3-HUMAN-THERMOREGULATION"
    assert res["forensic_verdict"] == "PARTIAL"
    
    # Tier 1: Energy conservation
    assert res["tier_1_energy_conservation"]["status"] == "PASS_ALGORITHMIC_CLOSURE"
    assert res["tier_1_energy_conservation"]["residual_watts"] < 1e-12
    
    # Tier 2: Reference model agreement (ISO 7933)
    assert res["tier_2_reference_model_agreement"]["status"] == "PASS_REFERENCE_MODEL_AGREEMENT"
    assert res["tier_2_reference_model_agreement"]["temperate_error_k_min"] < 0.010
    assert res["tier_2_reference_model_agreement"]["jungle_error_bio_k_min"] < 0.010
    
    # Tier 3: Independent human validation
    assert res["tier_3_independent_human_validation"]["status"] == "PARTIAL_LITERATURE_COHERENCE"
    assert res["tier_3_independent_human_validation"]["within_human_literature_range"] is True


def test_run_all_validation_tracks_master_matrix():
    """Verify run_all_validation_tracks produces complete forensic matrix with proper verdicts."""
    matrix = run_all_validation_tracks()
    verdicts = matrix["validation_verdicts"]
    
    assert verdicts["VALIDATION_VML"] == "PARTIAL"
    assert verdicts["VALIDATION_MATERIALS"] == "PARTIAL"
    assert verdicts["VALIDATION_THERMAL"] == "PARTIAL"
    assert verdicts["ARCHITECTURE_BIOLOGICAL_FEASIBILITY"] == "CONDITIONAL"
    assert verdicts["CYCLE_5_READY"] == "YES"
    assert matrix["summary"]["total_models"] == 14
