"""Unit tests for MODEL-03: Neural Latency & Dodge Horizon."""

import pytest
from aegis.model_03_reaction_movement import (
    BASELINE_HUMAN,
    OPTIMIZED_HUMAN_STARTLE,
    THEORETICAL_MAX_BIOLOGICAL,
    THREAT_PISTOL_CLOSE,
    THREAT_RIFLE_50M,
    THREAT_ARROW_SPORT,
    compute_reaction_latency,
    simulate_movement_trajectory,
    evaluate_evasion_possibility,
    run_benchmark_scenarios,
)


def test_hursh_conduction_velocity():
    lat = compute_reaction_latency(BASELINE_HUMAN)
    # Hursh relation: v = 6 * d = 6 * 12 = 72 m/s
    assert lat["conduction_velocity_m_s"] == 72.0
    assert lat["total_sensorimotor_latency_ms"] > 90.0


def test_extreme_bioengineered_latency_bound():
    lat = compute_reaction_latency(THEORETICAL_MAX_BIOLOGICAL)
    # Even extreme bioengineered limit cannot reduce sensorimotor latency below ~25 ms
    assert lat["total_sensorimotor_latency_ms"] >= 25.0
    assert lat["total_neural_latency_ms"] >= 10.0


def test_displacement_zero_before_latency():
    sim = simulate_movement_trajectory(BASELINE_HUMAN, duration_s=0.2)
    lat_s = sim["total_latency_ms"] / 1000.0
    # Before latency expiry, displacement must be strictly zero
    t_arr = sim["time_s"]
    x_arr = sim["displacement_m"]
    pre_indices = np.where(t_arr < lat_s)[0]
    for idx in pre_indices:
        assert x_arr[idx] == 0.0


import numpy as np


def test_dodge_horizon_pistol_close():
    # 7m pistol flight time ~ 19.4 ms. Evasion must fail for all biological profiles
    for profile in [BASELINE_HUMAN, OPTIMIZED_HUMAN_STARTLE, THEORETICAL_MAX_BIOLOGICAL]:
        res = evaluate_evasion_possibility(profile, THREAT_PISTOL_CLOSE)
        assert res["evasion_successful"] is False
        assert res["displacement_at_impact_mm"] == 0.0
        assert res["physical_verdict"] == "DODGE_IMPOSSIBLE_NO_GO"


def test_dodge_horizon_rifle_50m():
    # 50m rifle flight time ~ 55 ms.
    res_human = evaluate_evasion_possibility(BASELINE_HUMAN, THREAT_RIFLE_50M)
    assert res_human["evasion_successful"] is False
    assert res_human["displacement_at_impact_mm"] == 0.0


def test_arrow_evasion_feasible():
    # Subsonic arrow (315 ms flight time) allows human side-step
    res_arrow = evaluate_evasion_possibility(BASELINE_HUMAN, THREAT_ARROW_SPORT)
    assert res_arrow["evasion_successful"] is True
    assert res_arrow["displacement_at_impact_mm"] > 150.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-03"
    assert bench["scientific_conclusion"]["reactive_bullet_dodging_status"] == "LEVEL_D_CONTRADICTED_NO_GO"
