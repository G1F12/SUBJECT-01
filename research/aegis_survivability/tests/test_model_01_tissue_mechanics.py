"""Unit tests for MODEL-01: Tissue Mechanics & Puncture/Cut Resistance."""

import pytest
import math
from aegis.model_01_tissue_mechanics import (
    LayerProperties,
    HUMAN_DERMIS,
    PANGOLIN_SCALE_KERATIN,
    ARMADILLO_OSTEODERM,
    calculate_puncture_force,
    calculate_cutting_force,
    evaluate_composite_puncture,
    sensitivity_analysis,
    run_benchmark_scenarios,
)


def test_puncture_force_positive_and_scaling():
    res = calculate_puncture_force(HUMAN_DERMIS, indenter_radius_mm=0.5)
    assert res["f_puncture_n"] > 0.0
    assert res["work_to_puncture_j"] > 0.0
    assert res["f_fracture_component_n"] > 0.0

    # Larger radius must require higher or equal force
    res_large = calculate_puncture_force(HUMAN_DERMIS, indenter_radius_mm=1.0)
    assert res_large["f_puncture_n"] > res["f_puncture_n"]


def test_invalid_indenter_radius():
    with pytest.raises(ValueError):
        calculate_puncture_force(HUMAN_DERMIS, indenter_radius_mm=0.0)
    with pytest.raises(ValueError):
        calculate_puncture_force(HUMAN_DERMIS, indenter_radius_mm=-1.0)


def test_cutting_force_mechanics():
    res_acute = calculate_cutting_force(HUMAN_DERMIS, blade_wedge_angle_deg=20.0, blade_width_mm=15.0)
    res_blunt = calculate_cutting_force(HUMAN_DERMIS, blade_wedge_angle_deg=60.0, blade_width_mm=15.0)
    assert res_acute["f_cut_n"] > 0.0
    # Atkins model: blunter wedge angle increases the required cutting force
    assert res_blunt["f_cut_fracture_n"] < res_acute["f_cut_fracture_n"]  # 1/tan(theta/2) is larger for acute


def test_pangolin_superiority_over_human_skin():
    human = calculate_puncture_force(HUMAN_DERMIS, indenter_radius_mm=0.5)
    pangolin = calculate_puncture_force(PANGOLIN_SCALE_KERATIN, indenter_radius_mm=0.5)
    assert pangolin["f_puncture_n"] > human["f_puncture_n"] * 2.0


def test_composite_evaluation():
    stack = [ARMADILLO_OSTEODERM, HUMAN_DERMIS]
    res = evaluate_composite_puncture(stack, indenter_radius_mm=0.5)
    assert res["peak_puncture_force_n"] >= max(
        calculate_puncture_force(ARMADILLO_OSTEODERM, 0.5)["f_puncture_n"],
        calculate_puncture_force(HUMAN_DERMIS, 0.5)["f_puncture_n"],
    )
    assert res["total_thickness_mm"] == pytest.approx(4.0, abs=1e-3)
    assert len(res["layers"]) == 2


def test_sensitivity_analysis():
    sens = sensitivity_analysis(HUMAN_DERMIS, indenter_radius_mm=0.5)
    # Tensile strength should have strong positive sensitivity
    assert sens["tensile_strength_mpa"] > 0.5
    # Modulus has negative sensitivity because high E reduces elastic crack opening / compliance
    assert sens["youngs_modulus_mpa"] < 0.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-01"
    assert "human_baseline" in bench["scenarios"]
    assert "bioengineered_composite" in bench["scenarios"]
    assert bench["verdict"]["human_vs_bioengineered_gain_ratio"] > 4.0
