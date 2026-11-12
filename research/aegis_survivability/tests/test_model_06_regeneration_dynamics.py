"""Unit tests for MODEL-06: Regeneration Dynamics & Oncogenic Limits."""

import pytest
from aegis.model_06_regeneration_dynamics import (
    STANDARD_HUMAN_HEALING,
    ACOMYS_SPINY_MOUSE_ANALOGUE,
    THEORETICAL_EXTREME_BLASTEMA,
    GENOME_STABILIZED_EPIMORPHIC,
    DEFECT_EXCORIATION,
    DEFECT_EXTENSIVE_TRAUMA,
    evaluate_regeneration_timeline,
    run_benchmark_scenarios,
)


def test_closure_vs_neurotization_timescale_gap():
    res = evaluate_regeneration_timeline(STANDARD_HUMAN_HEALING, DEFECT_EXCORIATION)
    # Wound closure is on scale of days; nerve repair takes significantly longer
    assert res["wound_closure_days"] < res["functional_neurotization_days"]
    assert res["residual_fibrosis_fraction"] > 0.5


def test_acomys_scar_free_regeneration():
    res = evaluate_regeneration_timeline(ACOMYS_SPINY_MOUSE_ANALOGUE, DEFECT_EXCORIATION)
    assert res["scarless_regeneration"] is True
    assert res["residual_fibrosis_fraction"] == 0.0
    assert res["wound_closure_days"] < 10.0


def test_peto_paradox_oncogenic_suppression():
    # Extreme blastema with only 1 TP53 copy has very high cancer hazard
    res_unprotected = evaluate_regeneration_timeline(THEORETICAL_EXTREME_BLASTEMA, DEFECT_EXTENSIVE_TRAUMA)
    # Genome-stabilized (12 TP53 copies) reduces cancer risk dramatically
    res_stabilized = evaluate_regeneration_timeline(GENOME_STABILIZED_EPIMORPHIC, DEFECT_EXTENSIVE_TRAUMA)

    assert res_unprotected["ten_year_oncogenic_risk_pct"] > 90.0
    assert res_stabilized["ten_year_oncogenic_risk_pct"] < 15.0


def test_benchmark_runner():
    bench = run_benchmark_scenarios()
    assert bench["model_id"] == "MODEL-06"
    assert "fundamental_biological_boundaries" in bench
