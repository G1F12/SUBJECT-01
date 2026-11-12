"""Regression test suite for AEGIS-01 Cycle 2A Mandatory Fixes (Stage 1).

Covers all 8 mandatory fixes specified in the Cycle 2A charter:
1. Radial artery anatomical range and diameter variance.
2. Removal of 100% deterministic survival claims in hemorrhage.
3. Rebuttal of unconditional guaranteed biocomposite resistance >800 N.
4. Disqualification of proven Acomys translation to humans.
5. Separation of synthetic STF from biological fluid secretion.
6. Elimination of single-scalar deterministic AIS diagnosis.
7. Correction of the logical comparison in the Dodge Horizon theorem.
8. Inclusion of environmental psychrometrics in whole-body heat dissipation.
"""

import math
import pytest

from aegis.model_05_hemodynamic_stability import (
    RADIAL_ARTERY,
    FEMORAL_ARTERY,
    CAPILLARY_DERMAL_BED,
    BASELINE_HUMAN_HEMOSTASIS,
    BIOENGINEERED_LOCAL_SEALANT,
    simulate_hemorrhage,
    run_benchmark_scenarios as run_model05,
)
from aegis.model_01_tissue_mechanics import (
    BIOENGINEERED_TOUGHENED_COLLAGEN,
    calculate_cutting_force,
    calculate_slicing_force,
    run_benchmark_scenarios as run_model01,
)
from aegis.model_06_regeneration_dynamics import (
    ACOMYS_SPINY_MOUSE_ANALOGUE,
    run_benchmark_scenarios as run_model06,
)
from aegis.model_02_multilayer_protection import (
    SYNTHETIC_COLLOIDAL_STF_INTERLAYER,
    BIOLOGICAL_HYDROGEL_INTERLAYER,
    run_benchmark_scenarios as run_model02,
)
from aegis.model_04_energy_transfer import (
    CARTRIDGE_9MM_FMJ,
    RIGID_OSTEODERM_COMPOSITE,
    simulate_thoracic_impact,
)
from aegis.model_03_reaction_movement import (
    run_benchmark_scenarios as run_model03,
)
from aegis.model_07_integrated_architecture import (
    ARCH_0_HUMAN_BASELINE,
    ARCH_4_BALANCED_ADAPTIVE,
    TEMPERATE_STANDARD,
    HOT_HUMID_JUNGLE,
    HOT_DRY_DESERT,
    evaluate_architecture,
    run_benchmark_scenarios as run_model07,
)


def test_fix1_radial_artery_anatomical_range():
    """Fix 1: Radial artery must have anatomical variance range (2.2-3.2 mm diameter)."""
    assert hasattr(RADIAL_ARTERY, "lumen_radius_range_mm")
    r_min, r_max = RADIAL_ARTERY.lumen_radius_range_mm
    assert r_min == 1.1, f"Expected min lumen radius 1.1 mm (2.2 mm diam), got {r_min}"
    assert r_max == 1.6, f"Expected max lumen radius 1.6 mm (3.2 mm diam), got {r_max}"
    assert RADIAL_ARTERY.lumen_radius_mm >= r_min
    assert RADIAL_ARTERY.lumen_radius_mm <= r_max
    assert len(RADIAL_ARTERY.outer_diameter_range_mm) == 2


def test_fix2_no_100pct_survival_claim():
    """Fix 2: No claim of 100% deterministic survival at any hemorrhage level."""
    res05 = run_model05()
    limits_text = str(res05["scientific_limits"]).lower()
    assert "100% survivable" not in limits_text
    assert "100% выживаемость" not in limits_text
    assert "fully survivable" not in limits_text
    assert "non-deterministic" in limits_text or "mortality" in limits_text


def test_fix3_rebuttal_of_guaranteed_800n():
    """Fix 3: Unconditional guaranteed resistance >800 N is refuted by slicing kinematics."""
    # Under pure guillotine wedging, resistance is high
    guillotine = calculate_cutting_force(BIOENGINEERED_TOUGHENED_COLLAGEN, 30.0, 20.0)
    assert guillotine["f_cut_n"] > 500.0

    # Under draw slicing (xi = 4.0) with sharp edge (0.5 um), normal force drops significantly
    slicing = calculate_slicing_force(
        BIOENGINEERED_TOUGHENED_COLLAGEN,
        blade_wedge_angle_deg=30.0,
        blade_width_mm=20.0,
        slice_to_push_ratio=4.0,
        blade_edge_radius_um=0.5,
    )
    assert slicing["guaranteed_800n_valid"] is False
    assert slicing["f_push_normal_n"] < 250.0, f"Expected force <250 N under slicing, got {slicing['f_push_normal_n']}"
    assert slicing["force_reduction_pct"] > 60.0


def test_fix4_acomys_human_translation_unproven():
    """Fix 4: Acomys dermal healing must be clearly stated as unproven in humans."""
    res06 = run_model06()
    fibrosis_text = res06["fundamental_biological_boundaries"]["fibrosis_control"]
    assert "UNPROVEN HYPOTHESIS" in fibrosis_text
    assert "avotermin" in fibrosis_text or "clinical trials" in fibrosis_text


def test_fix5_synthetic_vs_biological_stf_distinction():
    """Fix 5: Explicitly separate synthetic industrial STF from biological fluid secretion."""
    assert SYNTHETIC_COLLOIDAL_STF_INTERLAYER.loss_factor_eta > 0.40
    assert BIOLOGICAL_HYDROGEL_INTERLAYER.youngs_modulus_gpa < 0.05
    res02 = run_model02()
    stf_info = res02["verdict"]["stf_material_distinction"]
    assert "synthetic_colloidal_stf" in stf_info
    assert "biological_fluid_synthesis" in stf_info
    assert "UNVALIDATED_SPECULATION" in stf_info["biological_fluid_synthesis"]


def test_fix6_no_deterministic_ais_prediction():
    """Fix 6: Dynamic ballistic blunt trauma must provide a probabilistic injury corridor, not deterministic AIS diagnosis."""
    res = simulate_thoracic_impact(CARTRIDGE_9MM_FMJ, RIGID_OSTEODERM_COMPOSITE)
    assert "multifactorial_injury_corridor" in res
    assert "clinical_validation_status" in res
    assert "MULTIFACTORIAL_PROBABILISTIC_CORRIDOR" in res["clinical_validation_status"]


def test_fix7_dodge_horizon_logical_comparison_fixed():
    """Fix 7: Dodge horizon comparison must evaluate total movement time vs flight time, avoiding 19-69 < 30.2 error."""
    res03 = run_model03()
    justification = res03["scientific_conclusion"]["justification"]
    # Verify that the erroneous phrase 'flight times (19.4 - 69.4 ms) are shorter than ... 30.2 ms' is gone
    assert "flight times (19.4 - 69.4 ms) are shorter than biological sensorimotor latency (30.2 ms" not in justification
    assert "Electromechanical Delay" in justification
    assert "Inertial Acceleration Time" in justification


def test_fix8_environment_in_heat_exchange():
    """Fix 8: Psychrometric environmental conditions must modulate heat dissipation."""
    res_temperate = evaluate_architecture(ARCH_0_HUMAN_BASELINE, env=TEMPERATE_STANDARD)
    res_humid = evaluate_architecture(ARCH_0_HUMAN_BASELINE, env=HOT_HUMID_JUNGLE)

    # In hot humid jungle (35 C, 85% RH), evaporative capacity collapses drastically
    assert res_humid["max_heat_dissipation_w"] < 0.35 * res_temperate["max_heat_dissipation_w"]
    # Even unarmored human suffers acute hyperthermia within 45 minutes under exertion in jungle
    assert res_humid["hyperthermia_limit_minutes"] < 45.0
