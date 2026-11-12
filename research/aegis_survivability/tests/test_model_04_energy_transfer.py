"""Unit tests for MODEL-04: Ballistic Energy Transfer & BABT."""

import pytest
from aegis.model_04_energy_transfer import (
    CARTRIDGE_9MM_FMJ,
    CARTRIDGE_762X39_M43,
    UNARMORED_HUMAN_CHEST,
    RIGID_OSTEODERM_COMPOSITE,
    simulate_thoracic_impact,
    run_benchmark_scenarios,
)


def test_kinetic_energy_and_momentum_calculation():
    res = simulate_thoracic_impact(CARTRIDGE_9MM_FMJ, UNARMORED_HUMAN_CHEST)
    # 0.5 * 0.008 * 365^2 = 532.9 J
    assert res["kinetic_energy_j"] == pytest.approx(532.9, abs=0.5)
    # 0.008 * 365 = 2.92 N*s
    assert res["momentum_ns"] == pytest.approx(2.92, abs=0.05)


def test_unarmored_lethal_trauma():
    res = simulate_thoracic_impact(CARTRIDGE_762X39_M43, UNARMORED_HUMAN_CHEST)
    # Focal unarmored impact causes massive penetration and VC > 10 m/s
    assert res["max_viscous_criterion_m_s"] > 1.0
    assert res["max_backface_deformation_mm"] > 50.0
    assert res["clinical_severity"] == "CRITICAL_FATAL_CARDIAC_OR_AORTIC_RUPTURE_AIS_6"


def test_rigid_osteoderm_protection_gain():
    res_unarm = simulate_thoracic_impact(CARTRIDGE_9MM_FMJ, UNARMORED_HUMAN_CHEST)
    res_shield = simulate_thoracic_impact(CARTRIDGE_9MM_FMJ, RIGID_OSTEODERM_COMPOSITE)

    # Rigid osteoderm composite must drastically reduce BFD and VC
    assert res_shield["max_backface_deformation_mm"] < 25.0
    assert res_shield["max_viscous_criterion_m_s"] < 0.5
    assert res_shield["clinical_severity"] == "MILD_CONTUSION_AIS_1_2"
    assert res_shield["estimated_lethality_risk_pct"] < 5.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-04"
    assert "Unarmored Human Thorax (Focal Puncture/Blunt)" in bench["protection_evaluations"]
    assert "Bioengineered Rigid Osteoderm Composite (Armadillo-like with Rib Bridge)" in bench["protection_evaluations"]
