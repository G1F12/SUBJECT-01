"""Unit tests for MODEL-08: Comparative Mechanics of Protective Biological Materials."""

import pytest
from aegis.model_08_materials_comparison import (
    SYSTEM_A_HUMAN_SKIN,
    SYSTEM_B_KERATIN_MULTILAYER,
    SYSTEM_C_BIOMINERAL_OSTEODERM,
    SYSTEM_D_CROSSLINKED_COMPOSITE,
    SYSTEM_E_FUNCTIONALLY_GRADED,
    compute_mechanical_performance,
    perform_sensitivity_analysis,
    run_comparative_materials_benchmark,
)


def test_five_systems_defined_with_provenance():
    systems = [
        SYSTEM_A_HUMAN_SKIN,
        SYSTEM_B_KERATIN_MULTILAYER,
        SYSTEM_C_BIOMINERAL_OSTEODERM,
        SYSTEM_D_CROSSLINKED_COMPOSITE,
        SYSTEM_E_FUNCTIONALLY_GRADED,
    ]
    for s in systems:
        assert s.system_id.startswith("SYS-")
        assert s.total_thickness_mm > 0.0
        assert s.bulk_density_kg_m3 > 900.0
        assert s.provenance_status in ["EXPERIMENTALLY_SUPPORTED", "THEORETICALLY_ASSIGNED", "MIXED"]
        assert len(s.key_unknowns) > 0


def test_sharp_vs_blunt_puncture_ratio():
    """Sharp needle penetration force must be an order of magnitude lower than blunt punch across all materials."""
    systems = [
        SYSTEM_A_HUMAN_SKIN,
        SYSTEM_B_KERATIN_MULTILAYER,
        SYSTEM_C_BIOMINERAL_OSTEODERM,
        SYSTEM_D_CROSSLINKED_COMPOSITE,
        SYSTEM_E_FUNCTIONALLY_GRADED,
    ]
    for s in systems:
        perf = compute_mechanical_performance(s)
        assert perf["puncture_sharp_needle_n"] < 0.20 * perf["puncture_blunt_punch_n"], (
            f"{s.name}: Sharp puncture {perf['puncture_sharp_needle_n']}N was not << blunt {perf['puncture_blunt_punch_n']}N"
        )


def test_slicing_draw_reduces_cutting_force():
    """Lateral draw slicing (xi = 4.0) must drastically reduce normal incising force vs guillotine chop."""
    systems = [
        SYSTEM_A_HUMAN_SKIN,
        SYSTEM_B_KERATIN_MULTILAYER,
        SYSTEM_C_BIOMINERAL_OSTEODERM,
        SYSTEM_D_CROSSLINKED_COMPOSITE,
        SYSTEM_E_FUNCTIONALLY_GRADED,
    ]
    for s in systems:
        perf = compute_mechanical_performance(s)
        assert perf["cut_slicing_draw_n"] < 0.35 * perf["cut_guillotine_normal_n"], (
            f"{s.name}: Slicing cut {perf['cut_slicing_draw_n']}N not < 0.35 * guillotine {perf['cut_guillotine_normal_n']}N"
        )


def test_spallation_vulnerability_contrast():
    """Biomineral osteoderm must exhibit high tensile spall risk; cross-linked composite must not."""
    perf_osteoderm = compute_mechanical_performance(SYSTEM_C_BIOMINERAL_OSTEODERM)
    perf_composite = compute_mechanical_performance(SYSTEM_D_CROSSLINKED_COMPOSITE)
    perf_skin = compute_mechanical_performance(SYSTEM_A_HUMAN_SKIN)

    assert perf_osteoderm["tensile_spall_fracture_risk"] is True
    assert perf_osteoderm["acoustic_spall_reflection_coeff"] < -0.50

    assert perf_composite["tensile_spall_fracture_risk"] is False
    assert abs(perf_skin["acoustic_spall_reflection_coeff"]) < 0.10


def test_monte_carlo_sensitivity_bounds():
    sens = perform_sensitivity_analysis(SYSTEM_B_KERATIN_MULTILAYER, num_samples=100)
    assert sens["sample_count"] == 100
    ci_puncture = sens["sharp_puncture_95ci_n"]
    assert ci_puncture[0] < sens["sharp_puncture_mean_n"] < ci_puncture[1]


def test_benchmark_runner_and_ballistic_caveat():
    bench = run_comparative_materials_benchmark()
    assert bench["model_id"] == "MODEL-08"
    assert len(bench["systems_evaluated"]) == 5
    for p in bench["detailed_performance"]:
        assert "NO_DIRECT_BALLISTIC_RESISTANCE_PROVEN" in p["ballistic_claim_status"]
