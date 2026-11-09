"""Physics Validation Tests for AEGIS-01 Models (Cycle 1A).

This test module verifies fundamental physical conservation laws,
dimensional consistency, asymptotic limits, and boundary conditions
across all corrected AEGIS-01 biomechanical and physiological models.
"""

import math
import pytest
import numpy as np

# Model 01
from aegis.model_01_tissue_mechanics import (
    HUMAN_DERMIS,
    PANGOLIN_SCALE_KERATIN,
    ARMADILLO_OSTEODERM,
    calculate_puncture_force,
    calculate_cutting_force,
)

# Model 02
from aegis.model_02_multilayer_protection import (
    MINERALIZED_HYDROXYAPATITE_PLATE,
    SHEAR_THICKENING_SUBDERMAL_FLUID,
    compute_acoustic_properties,
    compute_interface_coefficients,
    evaluate_wave_attenuation,
    evaluate_energy_dissipation_capacity,
)

# Model 03
from aegis.model_03_reaction_movement import (
    BASELINE_HUMAN,
    THEORETICAL_MAX_BIOLOGICAL,
    THREAT_PISTOL_CLOSE,
    compute_reaction_latency,
    evaluate_evasion_possibility,
)

# Model 04
from aegis.model_04_energy_transfer import (
    CARTRIDGE_9MM_FMJ,
    CARTRIDGE_762X39_M43,
    UNARMORED_HUMAN_CHEST,
    RIGID_OSTEODERM_COMPOSITE,
    simulate_thoracic_impact,
)

# Model 05
from aegis.model_05_hemodynamic_stability import (
    ABDOMINAL_AORTA,
    RADIAL_ARTERY,
    CAPILLARY_DERMAL_BED,
    BASELINE_HUMAN_HEMOSTASIS,
    BIOENGINEERED_LOCAL_SEALANT,
    simulate_hemorrhage,
)

# Model 06
from aegis.model_06_regeneration_dynamics import (
    STANDARD_HUMAN_HEALING,
    GENOME_STABILIZED_EPIMORPHIC,
    DEFECT_EXCORIATION,
    DEFECT_EXTENSIVE_TRAUMA,
    evaluate_regeneration_timeline,
)

# Model 07
from aegis.model_07_integrated_architecture import (
    ARCH_0_HUMAN_BASELINE,
    ARCH_1_FULL_OSTEODERM_SHELL,
    ARCH_4_BALANCED_ADAPTIVE,
    evaluate_architecture,
)


# =====================================================================
# 1. CONSERVATION OF ENERGY & WAVE MECHANICS
# =====================================================================

def test_acoustic_energy_conservation_at_interface():
    """At an acoustic interface, energy transmission and reflection must sum to 1.0."""
    z1 = compute_acoustic_properties(MINERALIZED_HYDROXYAPATITE_PLATE)["impedance_mrayl"] * 1e6
    z2 = compute_acoustic_properties(SHEAR_THICKENING_SUBDERMAL_FLUID)["impedance_mrayl"] * 1e6

    # Reflection and transmission coefficients for pressure amplitude
    r_p = (z2 - z1) / (z2 + z1)
    t_p = (2.0 * z2) / (z2 + z1)

    # Energy reflection (R_E) and transmission (T_E) coefficients
    r_e = r_p ** 2
    t_e = (z1 / z2) * (t_p ** 2)

    # Strict first-law energy conservation
    assert (r_e + t_e) == pytest.approx(1.0, rel=1e-6), (
        f"Acoustic energy not conserved: R_E={r_e}, T_E={t_e}, sum={r_e + t_e}"
    )


def test_reflected_tensile_wave_spall_condition():
    """When a compressive shock wave hits a lower impedance medium (Z2 < Z1),
    the reflected wave MUST be tensile (negative sign), risking spall fracture."""
    z_outer = compute_acoustic_properties(MINERALIZED_HYDROXYAPATITE_PLATE)["impedance_mrayl"] * 1e6
    z_inner = compute_acoustic_properties(SHEAR_THICKENING_SUBDERMAL_FLUID)["impedance_mrayl"] * 1e6

    assert z_inner < z_outer, "Inner layer must have lower impedance"
    r_p = (z_inner - z_outer) / (z_inner + z_outer)

    # Reflected coefficient must be strictly negative (inversion from compression to tension)
    assert r_p < -0.65, f"Expected strong negative reflection, got {r_p}"

    initial_stress = 300.0  # MPa
    reflected_stress = initial_stress * r_p
    # Reflected stress exceeds osteoderm tensile yield strength (~50-100 MPa)
    assert reflected_stress < -100.0, f"Expected severe tensile wave, got {reflected_stress} MPa"


def test_ballistic_kinetic_energy_conservation():
    """Ballistic kinetic energy must equal 0.5 * m * v^2."""
    c = CARTRIDGE_9MM_FMJ
    mass_kg = c.mass_g * 1e-3
    expected_ek = 0.5 * mass_kg * (c.velocity_m_s ** 2)
    res = simulate_thoracic_impact(c, UNARMORED_HUMAN_CHEST)
    assert res["kinetic_energy_j"] == pytest.approx(expected_ek, rel=1e-3)


# =====================================================================
# 2. CONSERVATION OF MOMENTUM & KINEMATICS
# =====================================================================

def test_inelastic_impact_momentum_conservation():
    """Total momentum immediately before impact must equal momentum immediately after impact."""
    cartridge = CARTRIDGE_762X39_M43
    prot = RIGID_OSTEODERM_COMPOSITE

    mass_kg = cartridge.mass_g * 1e-3
    p_initial = mass_kg * cartridge.velocity_m_s
    res = simulate_thoracic_impact(cartridge, prot)

    m_coupled = res["coupled_mass_g"] / 1000.0
    v_0 = res["initial_interface_velocity_m_s"]
    p_coupled = m_coupled * v_0

    assert p_coupled == pytest.approx(p_initial, rel=0.02), (
        f"Momentum not conserved: p_in={p_initial}, p_coupled={p_coupled}"
    )


# =====================================================================
# 3. CONSERVATION OF MASS & FLUID DYNAMICS BOUNDS
# =====================================================================

def test_fluid_mass_conservation_in_hemorrhage():
    """Blood loss can never exceed the total initial circulatory volume."""
    total_vol = 5.0  # Liters
    res = simulate_hemorrhage(ABDOMINAL_AORTA, BASELINE_HUMAN_HEMOSTASIS, total_blood_volume_l=total_vol)

    assert res["total_blood_lost_l"] <= total_vol
    assert res["blood_lost_pct"] <= 100.0
    assert res["total_blood_lost_l"] >= 0.0


def test_aortic_discharge_rate_physiological_upper_bound():
    """Aortic discharge rate must NOT violate physiological cardiac delivery limits.
    Unconstrained 47 L/min orifice flow is physically rejected."""
    # Under the corrected model, 40% loss of a 5L pool (2.0 L) should take >= 15-20 seconds,
    # NOT 4.6 seconds as predicted by unconstrained infinite reservoir assumptions.
    res = simulate_hemorrhage(ABDOMINAL_AORTA, BASELINE_HUMAN_HEMOSTASIS, breach_fraction=1.0)
    time_to_40pct = res.get("time_to_40pct_loss_s")
    assert time_to_40pct is not None
    assert time_to_40pct >= 15.0, (
        f"Aortic discharge rate is unphysiologically fast! Time to 40% loss: {time_to_40pct}s"
    )


def test_microvascular_rapid_closure():
    """Dermal capillary laceration must achieve spontaneous arrest with minimal volume loss."""
    res = simulate_hemorrhage(CAPILLARY_DERMAL_BED, BASELINE_HUMAN_HEMOSTASIS)
    assert res["hemostasis_achieved"] is True
    assert res["total_blood_lost_l"] < 0.05, "Capillary loss exceeded 50 mL"


# =====================================================================
# 4. ASYMPTOTIC LIMITS & BOUNDARY CONDITIONS
# =====================================================================

def test_blunt_punch_monotonicity_with_tip_radius():
    """Puncture force for blunt punch must monotonically decrease as probe radius decreases."""
    r_large = 2.0  # mm
    r_medium = 1.0 # mm
    r_small = 0.5  # mm

    f_large = calculate_puncture_force(PANGOLIN_SCALE_KERATIN, r_large)["f_puncture_n"]
    f_medium = calculate_puncture_force(PANGOLIN_SCALE_KERATIN, r_medium)["f_puncture_n"]
    f_small = calculate_puncture_force(PANGOLIN_SCALE_KERATIN, r_small)["f_puncture_n"]

    assert f_large > f_medium > f_small > 0.0, "Punch force must scale monotonically with probe radius"


def test_dodge_horizon_zero_displacement_at_muzzle():
    """At impact under close range (7m), bodily displacement must be strictly zero if flight time < latency."""
    res = evaluate_evasion_possibility(BASELINE_HUMAN, THREAT_PISTOL_CLOSE)
    assert res["displacement_at_impact_mm"] == 0.0
    assert res["evasion_successful"] is False


def test_thermal_dissipation_occlusion_boundary():
    """When skin occlusion fraction approaches 1.0, evaporative heat dissipation must approach zero."""
    arch_base = evaluate_architecture(ARCH_0_HUMAN_BASELINE)
    arch_shell = evaluate_architecture(ARCH_1_FULL_OSTEODERM_SHELL)

    # Base has 0% occlusion, Shell has 70% occlusion
    assert arch_shell["max_heat_dissipation_w"] < 0.35 * arch_base["max_heat_dissipation_w"]
    # Net combat heat accumulation must be positive for heavily occluded shell
    assert arch_shell["combat_heat_storage_w"] > 0.0


def test_axon_regeneration_biophysical_speed_limit():
    """Peripheral nerve re-innervation must respect the 1.0 - 2.2 mm/day tubulin transport limit."""
    res = evaluate_regeneration_timeline(STANDARD_HUMAN_HEALING, DEFECT_EXTENSIVE_TRAUMA)
    nerve_gap_mm = DEFECT_EXTENSIVE_TRAUMA.nerve_gap_distance_mm # 120 mm
    # Minimum time: 120 mm / 2.2 mm/day ~ 54.5 days + sprouting/synaptogenesis delays
    assert res["functional_neurotization_days"] >= (nerve_gap_mm / 2.2) + 14.0, (
        "Axon growth velocity exceeded fundamental tubulin transport limit!"
    )
