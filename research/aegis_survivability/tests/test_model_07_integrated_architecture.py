"""Unit tests for MODEL-07: Integrated Architecture Trade-offs."""

import pytest
from aegis.model_07_integrated_architecture import (
    ARCH_0_HUMAN_BASELINE,
    ARCH_1_FULL_OSTEODERM_SHELL,
    ARCH_2_FLEXIBLE_VISCOELASTIC,
    ARCH_3_HYPER_REGENERATIVE,
    ARCH_4_BALANCED_ADAPTIVE,
    evaluate_architecture,
    run_benchmark_scenarios,
)


def test_mass_conservation_and_support_cost():
    res_base = evaluate_architecture(ARCH_0_HUMAN_BASELINE)
    assert res_base["total_mass_kg"] == 75.0
    assert res_base["armor_mass_kg"] == 0.0

    res_shell = evaluate_architecture(ARCH_1_FULL_OSTEODERM_SHELL)
    assert res_shell["total_mass_kg"] > 90.0
    assert res_shell["armor_mass_kg"] > 15.0


def test_kleiber_metabolic_scaling():
    res_base = evaluate_architecture(ARCH_0_HUMAN_BASELINE)
    res_shell = evaluate_architecture(ARCH_1_FULL_OSTEODERM_SHELL)
    # Heavier organism must have higher BMR
    assert res_shell["resting_metabolic_rate_w"] > res_base["resting_metabolic_rate_w"]


def test_thermoregulation_hyperthermia_bottleneck():
    res_shell = evaluate_architecture(ARCH_1_FULL_OSTEODERM_SHELL)
    res_base = evaluate_architecture(ARCH_0_HUMAN_BASELINE)

    # Shell blocks 70% of sweating surface -> fatal heat stroke under exertion
    assert res_shell["combat_heat_storage_w"] > 300.0
    assert res_shell["hyperthermia_limit_minutes"] < 90.0
    # Baseline human sweating is sustainable
    assert res_base["hyperthermia_limit_minutes"] == "SUSTAINABLE"


def test_balanced_adaptive_pareto_dominance():
    res_arch4 = evaluate_architecture(ARCH_4_BALANCED_ADAPTIVE)
    res_arch1 = evaluate_architecture(ARCH_1_FULL_OSTEODERM_SHELL)
    res_arch0 = evaluate_architecture(ARCH_0_HUMAN_BASELINE)

    # Balanced adaptive should achieve the highest overall score
    assert res_arch4["scores"]["overall_survivability_index"] > res_arch1["scores"]["overall_survivability_index"]
    assert res_arch4["scores"]["overall_survivability_index"] > res_arch0["scores"]["overall_survivability_index"]
    # Retains high sprint speed
    assert res_arch4["sprint_speed_pct_baseline"] > 80.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-07"
    assert len(bench["architectures"]) == 5
