"""Unit tests for MODEL-02: Multilayer Protection & Wave Attenuation."""

import pytest
from aegis.model_02_multilayer_protection import (
    ArmorLayer,
    MINERALIZED_HYDROXYAPATITE_PLATE,
    SHEAR_THICKENING_SUBDERMAL_FLUID,
    HIGH_DENSITY_COLLAGEN_BACKPLATE,
    HOMOGENEOUS_BONE_SLAB,
    compute_acoustic_properties,
    compute_interface_coefficients,
    evaluate_wave_attenuation,
    evaluate_energy_dissipation_capacity,
    run_benchmark_scenarios,
)


def test_acoustic_properties():
    props = compute_acoustic_properties(MINERALIZED_HYDROXYAPATITE_PLATE)
    assert props["sound_speed_m_s"] > 2000.0  # Speed in hydroxyapatite / mineral bone
    assert props["impedance_mrayl"] > 4.0
    assert props["areal_density_kg_m2"] > 5.0


def test_interface_energy_conservation():
    inter = compute_interface_coefficients(
        MINERALIZED_HYDROXYAPATITE_PLATE, SHEAR_THICKENING_SUBDERMAL_FLUID
    )
    # Conservation of acoustic energy: T_E + R_E == 1.0
    total_energy_ratio = inter["energy_transmission_ratio"] + inter["energy_reflection_ratio"]
    assert total_energy_ratio == pytest.approx(1.0, abs=1e-3)


def test_tri_layer_attenuation_advantage():
    tri_layer = [
        MINERALIZED_HYDROXYAPATITE_PLATE,
        SHEAR_THICKENING_SUBDERMAL_FLUID,
        HIGH_DENSITY_COLLAGEN_BACKPLATE,
    ]
    res = evaluate_wave_attenuation(tri_layer, initial_stress_mpa=250.0)
    assert res["total_stress_attenuation_pct"] > 80.0
    assert res["exit_stress_mpa"] < 50.0


def test_monolithic_poor_attenuation():
    res = evaluate_wave_attenuation([HOMOGENEOUS_BONE_SLAB], initial_stress_mpa=250.0)
    # Monolithic slab without interfaces has low high-frequency attenuation
    assert res["total_stress_attenuation_pct"] < 10.0


def test_energy_dissipation_capacity():
    tri_layer = [
        MINERALIZED_HYDROXYAPATITE_PLATE,
        SHEAR_THICKENING_SUBDERMAL_FLUID,
        HIGH_DENSITY_COLLAGEN_BACKPLATE,
    ]
    res = evaluate_energy_dissipation_capacity(tri_layer, impact_area_cm2=10.0)
    assert res["total_energy_capacity_j"] > 50.0
    assert res["interfacial_delamination_j"] > 0.0
    assert res["specific_energy_j_per_kg_m2"] > 5.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-02"
    assert bench["comparison"]["exit_stress_reduction_ratio"] > 5.0
    assert bench["verdict"]["tri_layer_attenuation_advantage"] == "CONFIRMED_LEVEL_B"
