"""
Unit test suite for AEGIS-01 Research Cycle 13 Core Models & Multi-System Contract.
Strategic Realignment · Whole-Organism Interfaces · Neglected Domains.
"""

import pytest
import math
from aegis.cycle13_models import (
    get_whole_organism_contract_definition,
    analyze_dynamic_hemostasis_shear_limits,
    analyze_viscoelastic_acoustic_attenuation,
    analyze_sensorimotor_latency_and_dodge_horizon,
    analyze_vml_isolated_vs_synergist_torque,
    simulate_target_cpe45_multisystem_trajectory,
)


def test_whole_organism_contract_structure():
    """Verify all 9 interdependent subsystems are defined with required metadata."""
    contract = get_whole_organism_contract_definition()
    assert len(contract) == 9
    expected_subsystems = [
        "1_mass_and_geometry",
        "2_mechanical_loads",
        "3_neuromuscular_control",
        "4_vascular_and_organ_resilience",
        "5_functional_tissue_regeneration",
        "6_metabolic_cost",
        "7_thermoregulation",
        "8_locomotor_performance",
        "9_target_cpe45",
    ]
    for sub in expected_subsystems:
        assert sub in contract
        assert "inputs" in contract[sub]
        assert "outputs" in contract[sub]
        assert "governing_equations" in contract[sub]
        assert "validation_status" in contract[sub]


def test_hemostasis_shear_limits():
    """Verify traumatic hemorrhage flow bounding and critical shear stress."""
    res = analyze_dynamic_hemostasis_shear_limits(vessel_radius_mm=1.0, map_mmhg=90.0)
    assert res["validation_status"] == "NOT_EXTERNALLY_VALIDATED"
    scenarios = res["vasospasm_scenarios"]
    assert len(scenarios) == 5
    
    # Without vasospasm (spasm = 0.0), flow is high and wall shear is dangerous
    zero_spasm = scenarios[0]
    assert zero_spasm["clot_shear_stable"] is False
    assert zero_spasm["hemostasis_verdict"] == "EXSANGUINATION_RISK"
    
    # Extreme vasospasm (spasm = 0.96), lumen constricted, stable clot possible
    severe_spasm = scenarios[-1]
    assert severe_spasm["effective_lumen_radius_mm"] < 0.10
    assert severe_spasm["clot_shear_stable"] is True


def test_viscoelastic_acoustic_attenuation():
    """Verify multilayer acoustic impedance calculation and stress wave reflection."""
    res = analyze_viscoelastic_acoustic_attenuation(incident_pressure_mpa=100.0)
    assert res["validation_status"] == "PARTIALLY_VALIDATED_PHYSICS_ACOUSTICS"
    layers = res["stratified_tissue_layers"]
    assert len(layers) == 4
    
    # Keratin impedance is highest (~2.86 MRayl)
    assert layers[0]["acoustic_impedance_mrayl"] > 2.5
    # Adipose is lowest (~1.38 MRayl)
    assert layers[2]["acoustic_impedance_mrayl"] < 1.5
    
    # Stratified interfaces produce attenuation gain vs monolithic baseline
    assert res["layered_transmitted_pressure_mpa"] < res["homogeneous_baseline_transmitted_mpa"]
    assert res["acoustic_impedance_attenuation_gain_pct"] > 15.0


def test_sensorimotor_latency_and_dodge_horizon():
    """Verify biological sensorimotor delay components and dodge horizon."""
    res = analyze_sensorimotor_latency_and_dodge_horizon(projectile_velocity_m_s=320.0)
    assert res["validation_status"] == "PARTIALLY_VALIDATED_BIOPHYSICS"
    breakdown = res["premotor_latency_breakdown_ms"]
    
    # Electromechanical delay is the single largest peripheral delay
    assert breakdown["electromechanical_delay_emd"] >= 40.0
    assert breakdown["total_latency_ms"] > 80.0
    
    # Dodge horizon for 320 m/s is > 30 meters
    assert res["minimum_evasion_distance_m"] > 30.0
    
    # Close range (5m, 15m) must be impossible
    scenarios = {s["engagement_distance_m"]: s["evasion_verdict"] for s in res["distance_scenarios"]}
    assert scenarios[5.0] == "EVASION_IMPOSSIBLE"
    assert scenarios[15.0] == "EVASION_IMPOSSIBLE"


def test_vml_isolated_vs_synergist_torque():
    """Verify deconvolution of joint torque into isolated force and synergist artifact."""
    res = analyze_vml_isolated_vs_synergist_torque()
    assert res["epistemic_verdict"] == "SYNERGIST_CONFOUNDING_CONFIRMED"
    # Apparent joint recovery is around 35%
    assert 30.0 < res["reported_apparent_joint_torque_recovery_pct"] < 40.0
    # True isolated muscle recovery is near 0%
    assert res["true_isolated_muscle_force_recovery_pct"] < 5.0
    # Synergist artifact is > 25 percentage points
    assert res["synergist_artifact_percentage_points"] > 25.0


def test_simulate_target_cpe45_multisystem():
    """Verify TARGET-CPE45 variable workload 2700s simulation without scalar survival index."""
    res = simulate_target_cpe45_multisystem_trajectory(duration_s=2700)
    assert res["duration_seconds"] == 2700
    assert res["total_mass_kg"] == 75.0 + 6.8
    assert len(res["trajectory_checkpoints"]) == 4
    
    # Confirm status vector exists and is not a scalar probability
    status = res["status_vector"]
    assert "thermal_state" in status
    assert "cardiovascular_drift_state" in status
    assert "mechanical_capacity" in status
    
    # Verify breaches list tracks physical events
    breaches = res["threshold_breaches"]
    assert any(b["type"] == "CARDIOVASCULAR_STRAIN_SEVERE" for b in breaches)
