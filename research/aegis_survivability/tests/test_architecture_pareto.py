#!/usr/bin/env python3
"""Unit tests for MODEL-11 Multi-Criteria Architecture Comparison & Pareto Optimization."""

import pytest
from aegis.model_11_architecture_pareto import (
    ARCHITECTURES_DATA,
    compute_pareto_dominance,
)


def test_pareto_frontier_identification():
    """Verify Pareto frontier correctly identifies non-dominated architectures."""
    res = compute_pareto_dominance()
    frontier = res["pareto_frontier"]

    # ARCH-0, ARCH-1, ARCH-3, ARCH-4 must be on frontier
    assert "ARCH-0" in frontier, "ARCH-0 must be Pareto-optimal for baseline cursorial mobility"
    assert "ARCH-1" in frontier, "ARCH-1 must be Pareto-optimal for raw puncture hardness"
    assert "ARCH-3" in frontier, "ARCH-3 must be Pareto-optimal for rapid cutaneous closure"
    assert "ARCH-4" in frontier, "ARCH-4 must be Pareto-optimal for balanced survivability"

    # ARCH-2 should not be on the primary operational frontier
    assert "ARCH-2" not in frontier, "ARCH-2 is suboptimal and dominated across key trade-offs"


def test_arch4_dominates_arch2_pairwise():
    """Verify that ARCH-4 is superior to ARCH-2 across protection, mass, speed, and thermal metrics."""
    res = compute_pareto_dominance()
    proof = res["arch2_suboptimality_proof"]

    assert proof["protection_puncture_mm"]["winner"] == "ARCH-4"
    assert proof["cutting_resistance_N"]["winner"] == "ARCH-4"
    assert proof["mass_kg"]["winner"] == "ARCH-4"
    assert proof["sprint_speed_m_s"]["winner"] == "ARCH-4"
    assert proof["cpe45_work_net_kJ"]["winner"] == "ARCH-4"
    assert proof["heat_dissipation_W"]["winner"] == "ARCH-4"
    assert proof["epistemic_uncertainty"]["winner"] == "ARCH-4"


def test_epistemic_uncertainty_hierarchy():
    """Verify that uncertainty scores reflect clinical and experimental reality:
    ARCH-0 (1.0) < ARCH-1 (2.5) <= ARCH-4 (2.8) < ARCH-2 (3.5) < ARCH-3 (4.0).
    """
    m0 = ARCHITECTURES_DATA["ARCH-0"].epistemic_uncertainty_score
    m1 = ARCHITECTURES_DATA["ARCH-1"].epistemic_uncertainty_score
    m4 = ARCHITECTURES_DATA["ARCH-4"].epistemic_uncertainty_score
    m2 = ARCHITECTURES_DATA["ARCH-2"].epistemic_uncertainty_score
    m3 = ARCHITECTURES_DATA["ARCH-3"].epistemic_uncertainty_score

    assert m0 == 1.0, "Human baseline must have uncertainty 1.0"
    assert m0 < m1 < m2 < m3, "Uncertainty must increase with biological deviation and lack of mammalian precedent"
    assert m4 < m2, "FGM selective plating has stronger developmental analogues than whole-body STF hydrogel"


def test_pareto_robustness_scenarios_and_monte_carlo():
    """Verify that under shifted operational scenarios and parameter perturbations,
    ARCH-2 shows conditional viability rather than unconditional fatal obsolescence.
    """
    res = compute_pareto_dominance()
    assert "robustness_scenarios" in res
    assert "cold_climate_laceration_priority" in res["robustness_scenarios"]
    cold_frontier = res["robustness_scenarios"]["cold_climate_laceration_priority"]["frontier"]
    assert "ARCH-2" in cold_frontier, "ARCH-2 should be non-dominated under cold laceration scenario"

    mc_probs = res["monte_carlo_frontier_probabilities"]
    assert mc_probs["ARCH-2"] > 0.20, f"Expected ARCH-2 MC frontier probability > 20%, got {mc_probs['ARCH-2']}"

