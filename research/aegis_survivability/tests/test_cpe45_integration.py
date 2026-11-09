#!/usr/bin/env python3
"""Unit tests for MODEL-10 SUBJECT-01 CPE45 Integration Engine."""

import pytest
from aegis.model_10_cpe45_integration import (
    ARCHITECTURES,
    CLIMATES,
    evaluate_architecture_cpe45,
    run_cpe45_comprehensive_matrix,
)


def test_architectures_parameter_bounds():
    """Verify that all defense architectures adhere strictly to SUBJECT-01 parameter schema bounds."""
    for arch_id, arch in ARCHITECTURES.items():
        assert 0.0 <= arch.armor_mass_kg <= 15.0, f"{arch_id} armor mass exceeds 15 kg bound"
        assert 0.0 <= arch.skin_coverage_fraction <= 1.0, f"{arch_id} skin coverage fraction out of bounds"
        assert 0.0 < arch.evaporated_water_scale <= 1.0, f"{arch_id} sweat capacity scale out of bounds"
        assert 1.0 <= arch.internal_work_factor <= 3.0, f"{arch_id} internal work factor out of bounds"


def test_arch0_temperate_thermal_equilibrium():
    """Verify baseline human ARCH-0 stays within safe thermal limits in temperate climate."""
    res = evaluate_architecture_cpe45(ARCHITECTURES["ARCH-0"], climate="temperate", dt=1.0)
    assert res["final_delta_K"] < 1.0, f"Baseline human temperature rise too high: {res['final_delta_K']} K"
    assert res["time_to_hyperthermia_39_5C_s"] == "NOT_REACHED"
    assert res["external_work_kJ"] > 80.0, "Expected >80 kJ external work delivered by ARCH-0"


def test_arch1_thermal_trap_and_work_collapse():
    """Verify that heavy shell ARCH-1 suffers severe hyperthermia and external work reduction."""
    res_temp = evaluate_architecture_cpe45(ARCHITECTURES["ARCH-1"], climate="temperate", dt=1.0)
    res_humid = evaluate_architecture_cpe45(ARCHITECTURES["ARCH-1"], climate="hot_humid", dt=1.0)

    # In hot-humid climate, body temperature elevation must exceed 4.0 K (fatal hyperthermia)
    assert res_humid["final_delta_K"] > 4.5, f"Expected fatal heat delta K (>4.5 K), got {res_humid['final_delta_K']}"
    assert isinstance(res_humid["time_to_hyperthermia_39_5C_s"], float)
    assert res_humid["time_to_hyperthermia_39_5C_s"] < 1500.0, "Should reach critical 39.5 C early"

    # External work must be severely degraded compared to ARCH-0
    assert res_temp["external_work_kJ"] < 40.0, f"Expected <40 kJ external work for ARCH-1, got {res_temp['external_work_kJ']}"


def test_arch4_balanced_pareto_performance():
    """Verify balanced architecture ARCH-4 delivers superior compromise over ARCH-1."""
    res_temp = evaluate_architecture_cpe45(ARCHITECTURES["ARCH-4"], climate="temperate", dt=1.0)

    assert res_temp["external_work_kJ"] > 60.0, "ARCH-4 should maintain robust external work (>60 kJ)"
    assert res_temp["speed_retention_pct"] > 60.0, "ARCH-4 speed retention should exceed 60%"
    assert res_temp["final_delta_K"] < 2.0, "ARCH-4 in temperate climate should remain sub-critical (<2.0 K)"


def test_cpe45_comprehensive_matrix_integrity():
    """Verify complete 15-cell matrix generates and contains valid schema."""
    matrix = run_cpe45_comprehensive_matrix()
    assert matrix["model_id"] == "MODEL-10"
    assert matrix["runs_count"] == 15
    assert len(matrix["matrix"]) == 15
    assert "key_findings" in matrix
    assert "hyperthermia_trap" in matrix["key_findings"]
