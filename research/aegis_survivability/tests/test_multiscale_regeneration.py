#!/usr/bin/env python3
"""Unit tests for MODEL-09 Multi-Scale Tissue Regeneration Dynamics."""

import pytest
from aegis.model_09_multiscale_regeneration import (
    HUMAN_STANDARD_REPAIR,
    ACOMYS_DERMAL_AUTOTOMY_ANALOGUE,
    BIOENGINEERED_SCAFFOLD_HYPOTHESIS,
    TRAUMA_TIER_I_DEEP_LACERATION,
    TRAUMA_TIER_II_PENETRATING_PUNCTURE,
    TRAUMA_TIER_III_VOLUMETRIC_TRAUMA,
    simulate_multiscale_regeneration,
    run_regeneration_benchmark_suite,
)


def test_temporal_hierarchy_phase_ordering():
    """Verify that phases strictly follow biological temporal progression:
    Hemostasis < Vascularization < Epithelial closure < Axon contact < Functional strength.
    """
    sim = simulate_multiscale_regeneration(HUMAN_STANDARD_REPAIR, TRAUMA_TIER_I_DEEP_LACERATION)
    milestones = sim["milestones_days"]

    t_hemo = milestones["hemostatic_matrix_closure_day"]
    t_vasc = milestones["vascularization_half_day"]
    t_dermis = milestones["epithelial_closure_day"]
    t_axon = milestones["axon_target_contact_day"]
    t_neuro = milestones["full_neurotization_day"]

    assert t_hemo < t_vasc, "Vascular sprouting must follow hemostatic matrix formation"
    assert t_vasc < t_dermis, "Epithelial migration relies on underlying vascularized granulation bed"
    assert t_axon > t_hemo, "Axon growth latency and elongation exceeds acute hemostasis"
    assert t_neuro > t_axon, "Synaptogenesis and remyelination occur after axonal target contact"


def test_tier_iii_volumetric_muscle_loss_permanent_deficit():
    """Verify that Tier III trauma (45 cm^3 VML) results in permanent functional deficit (<40%)
    in adult human standard biology due to fibrotic cavity collapse.
    """
    sim_human = simulate_multiscale_regeneration(HUMAN_STANDARD_REPAIR, TRAUMA_TIER_III_VOLUMETRIC_TRAUMA)
    outcomes = sim_human["final_outcomes_365d"]

    assert outcomes["vml_permanent_deficit"] is True, "Tier III trauma must trigger VML deficit in human profile"
    assert outcomes["functional_strength_pct"] < 35.0, (
        f"Expected severe permanent deficit (<35%), got {outcomes['functional_strength_pct']}%"
    )
    assert sim_human["milestones_days"]["functional_strength_90pct_day"] == "PERMANENT_DEFICIT"


def test_axon_growth_rate_physical_limit():
    """Verify that no biological profile exceeds the fundamental tubulin slow component A
    axonal transport ceiling of 2.0 mm/day.
    """
    profiles = [HUMAN_STANDARD_REPAIR, ACOMYS_DERMAL_AUTOTOMY_ANALOGUE, BIOENGINEERED_SCAFFOLD_HYPOTHESIS]
    for p in profiles:
        assert p.axon_growth_rate_mm_day <= 2.0, (
            f"Profile {p.name} specifies {p.axon_growth_rate_mm_day} mm/day, exceeding 2.0 mm/day biophysical limit"
        )
        assert p.axon_growth_rate_mm_day >= 0.5, "Axon growth rate below plausible biological minimum"


def test_acomys_accelerated_dermal_closure_vs_human():
    """Verify that Acomys analog exhibits accelerated epithelial closure compared to human standard,
    but retains nerve growth constraints.
    """
    sim_human = simulate_multiscale_regeneration(HUMAN_STANDARD_REPAIR, TRAUMA_TIER_I_DEEP_LACERATION)
    sim_acomys = simulate_multiscale_regeneration(ACOMYS_DERMAL_AUTOTOMY_ANALOGUE, TRAUMA_TIER_I_DEEP_LACERATION)

    t_close_human = sim_human["milestones_days"]["epithelial_closure_day"]
    t_close_acomys = sim_acomys["milestones_days"]["epithelial_closure_day"]

    # Acomys should close dermal defect significantly faster (~3x)
    assert t_close_acomys < t_close_human
    assert t_close_acomys <= 6.0  # 12mm radius / 2.4 mm/day = 5.0 days
    assert t_close_human >= 12.0  # 12mm radius / 0.8 mm/day = 15.0 days


def test_regeneration_benchmark_suite_execution():
    """Verify benchmark suite executes and populates all trauma tiers and scientific conclusions."""
    suite = run_regeneration_benchmark_suite()
    assert suite["model_id"] == "MODEL-09"
    assert len(suite["trauma_benchmarks"]) == 3
    assert "scientific_conclusions" in suite
    assert "volumetric_muscle_loss_wall" in suite["scientific_conclusions"]
    assert "nerve_regeneration_bottleneck" in suite["scientific_conclusions"]
