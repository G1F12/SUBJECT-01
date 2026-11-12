"""Unit tests for MODEL-05: Hemodynamic Stability & Hemorrhage."""

import pytest
from aegis.model_05_hemodynamic_stability import (
    CAPILLARY_DERMAL_BED,
    RADIAL_ARTERY,
    FEMORAL_ARTERY,
    ABDOMINAL_AORTA,
    BASELINE_HUMAN_HEMOSTASIS,
    BIOENGINEERED_LOCAL_SEALANT,
    simulate_hemorrhage,
    run_benchmark_scenarios,
)


def test_microvascular_capillary_closure():
    res = simulate_hemorrhage(CAPILLARY_DERMAL_BED, BASELINE_HUMAN_HEMOSTASIS)
    assert res["hemostasis_achieved"] is True
    assert res["blood_lost_pct"] < 1.0
    assert res["shock_class"] == "CLASS_I_COMPENSATED"


def test_radial_artery_hemostasis_speedup():
    res_base = simulate_hemorrhage(RADIAL_ARTERY, BASELINE_HUMAN_HEMOSTASIS)
    res_bio = simulate_hemorrhage(RADIAL_ARTERY, BIOENGINEERED_LOCAL_SEALANT)

    assert res_bio["time_to_hemostasis_s"] < res_base["time_to_hemostasis_s"]
    assert res_bio["total_blood_lost_l"] < res_base["total_blood_lost_l"]


def test_aortic_catastrophic_failure():
    # Aorta transection must be fatal under any hemostatic chemistry without mechanical occlusion
    res_base = simulate_hemorrhage(ABDOMINAL_AORTA, BASELINE_HUMAN_HEMOSTASIS)
    res_bio = simulate_hemorrhage(ABDOMINAL_AORTA, BIOENGINEERED_LOCAL_SEALANT)

    assert res_base["shock_class"] == "CLASS_IV_LETHAL_EXSANGUINATION"
    assert res_bio["shock_class"] == "CLASS_IV_LETHAL_EXSANGUINATION"
    assert res_base["final_map_mmhg"] == 0.0


def test_blood_volume_conservation():
    res = simulate_hemorrhage(FEMORAL_ARTERY, BASELINE_HUMAN_HEMOSTASIS, total_blood_volume_l=5.0)
    # Total blood lost cannot exceed initial blood volume (or lethal threshold)
    assert res["total_blood_lost_l"] <= 5.0
    assert res["blood_lost_pct"] <= 100.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-05"
    assert "scientific_limits" in bench
