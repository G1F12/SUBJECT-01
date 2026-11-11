"""
Unit and regression tests for AEGIS-01 Cycle 10.
Forensic data repair, pre-registered holdout validation, architecture trade-offs, and CPE45 uncertainty.
"""

import pytest
import math
from pathlib import Path

from aegis.cycle10_models import (
    load_canonical_zhang2018_matrix,
    evaluate_reconciled_zhang2018_development_set,
    evaluate_true_independent_holdouts,
    evaluate_three_protective_architectures,
    run_thermodynamic_cpe45_simulation,
    execute_cpe45_uncertainty_matrix,
    run_cycle10_master_validation,
    FROZEN_MODEL_SHA256,
    predict_keratin_modulus,
    CANONICAL_CSV
)


def test_canonical_csv_integrity_and_reconciliation():
    """Verify canonical CSV exists, contains exactly 28 rows, and reconciles arithmetic."""
    assert CANONICAL_CSV.is_file(), "Missing canonical CSV file!"
    rows = load_canonical_zhang2018_matrix()
    assert len(rows) == 28, f"Expected 28 canonical rows, got {len(rows)}"

    # Check that 24 are compression and 4 are tension
    comp_rows = [r for r in rows if r["test_mode"] == "compression"]
    tens_rows = [r for r in rows if r["test_mode"] == "tension"]
    assert len(comp_rows) == 24
    assert len(tens_rows) == 4

    # Verify reconciliation metrics
    res = evaluate_reconciled_zhang2018_development_set()
    assert res["dataset_metadata"]["status"] == "DEVELOPMENT_SET_CALIBRATION_ONLY"
    assert abs(res["baseline"]["mean_modulus_gpa"] - 0.868214) < 1e-4
    assert abs(res["baseline"]["mae_gpa"] - 0.606327) < 1e-4
    assert abs(res["cycle8_performance"]["mae_gpa"] - 1.307906) < 1e-4
    assert res["cycle8_performance"]["verdict"] == "FAILED_HOLDOUT"
    assert abs(res["cycle9_performance"]["mae_gpa"] - 0.396863) < 1e-4
    assert res["cycle9_performance"]["verdict"] == "DEVELOPMENT_SET_FIT"


def test_pre_registered_frozen_model_hash():
    """Verify cryptographic integrity of the pre-registered frozen model code."""
    expected_hash = "225d6994d5b97539f52c1ef5968ee8ac5f96a8b4da37c1e057e983b5f2faea25"
    assert FROZEN_MODEL_SHA256 == expected_hash, f"Model hash changed! Expected {expected_hash}, got {FROZEN_MODEL_SHA256}"


def test_true_holdout_li2010_bovine_success():
    """Verify pre-registered true holdout on Li et al. (2010) achieves positive error reduction."""
    res = evaluate_true_independent_holdouts()
    bovine = res["primary_holdout_li2010_bovine"]
    assert bovine["status"] == "PASS"
    assert bovine["model_mae_gpa"] < bovine["baseline_mae_gpa"]
    assert bovine["error_reduction_pct"] > 50.0  # observed ~52.95%
    assert abs(bovine["model_mae_gpa"] - 0.235) < 0.01


def test_true_holdout_tombolato2010_bighorn_bending_success():
    """Verify cross-coupon holdout on Tombolato et al. (2010) bending tests."""
    res = evaluate_true_independent_holdouts()
    tom = res["secondary_holdout_tombolato2010_bighorn"]
    assert tom["status"] == "PASS"
    assert tom["model_mae_gpa"] < tom["baseline_mae_gpa"]
    assert tom["error_reduction_pct"] > 80.0  # observed ~88.11%


def test_negative_boundary_equine_hoof_refuted():
    """Verify equine hoof wall fails cross-tissue transferability and is marked as domain boundary."""
    res = evaluate_true_independent_holdouts()
    hoof = res["negative_boundary_bertram1987_equine"]
    assert hoof["status"] == "REFUTED_DOMAIN_BOUNDARY"
    # Large absolute error on dry hoof
    assert hoof["model_mae_gpa"] > 3.0


def test_three_architectures_tradeoff_no_predetermined_winner():
    """Verify all 3 architectures are evaluated across 10 indicators with physical constraints."""
    res = evaluate_three_protective_architectures()
    assert res["tradeoff_verdict"] == "NO_UNIVERSAL_WINNER_CONFIRMED"
    archs = res["architectures"]
    assert len(archs) == 3

    # Arch A: monolithic has lowest ROM, highest compartment pressure surge
    assert archs["architecture_a_monolithic"]["sagittal_rom_pct"] < 10.0
    assert archs["architecture_a_monolithic"]["compartment_pressure_surge_mmhg"] > 40.0

    # Arch B: imbricated has moderate mass and high ROM
    assert archs["architecture_b_imbricated"]["total_mass_kg"] < 8.0
    assert archs["architecture_b_imbricated"]["sagittal_rom_pct"] > 85.0

    # Arch C: fibrous composite has highest mass and highest tearing toughness
    assert archs["architecture_c_fibrous_composite"]["total_mass_kg"] > 14.0
    assert archs["architecture_c_fibrous_composite"]["fatigue_fracture_toughness_j1c"] > 15.0


def test_cpe45_thermodynamic_corrections_and_scenario_threshold():
    """Verify 1-node thermodynamic model implements J/K units and defines 40C as scenario threshold."""
    res = run_thermodynamic_cpe45_simulation()
    # Heat capacity strictly in J/K (baseline 75kg human + 6.8kg armor: 270,450 J/K)
    assert abs(res["heat_capacity_j_k"] - 270450.0) < 1.0
    # Net thermal load deducting 20% mechanical efficiency
    assert abs(res["thermal_load_w"] - 556.2) < 1.0
    # Final core temp under nominal conditions
    assert res["final_t_core_c"] < 40.0
    assert res["scenario_threshold_maintained"] is True

    # Uncertainty matrix check
    unc = execute_cpe45_uncertainty_matrix()
    assert unc["status"] == "NOT_EXTERNALLY_VALIDATED"
    assert "scenario safety threshold" in unc["threshold_definition"]
    assert "60.0kg" in unc["body_mass_sweep"]


def test_cycle10_master_validation_matrix():
    """Verify master runner executes all tracks and confirms overall status."""
    matrix = run_cycle10_master_validation()
    status = matrix["overall_status"]
    assert status["FORENSIC_DATA_PARITY"] == "PASS"
    assert status["CYCLE9_DEVELOPMENT_CALIBRATION"] == "PASS"
    assert status["TRUE_HOLDOUT_BOVINE_LI2010"] == "PASS"
    assert status["CROSS_TISSUE_HOOF_BOUNDARY"] == "CONFIRMED_NEGATIVE_RESULT"
    assert status["THREE_ARCHITECTURE_TRADEOFF"] == "PASS_UNBIASED"
    assert status["TARGET_CPE45_UNCERTAINTY"] == "NOT_EXTERNALLY_VALIDATED"
