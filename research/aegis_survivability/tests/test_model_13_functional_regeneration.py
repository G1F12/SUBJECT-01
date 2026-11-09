"""Unit tests for MODEL-13: Multi-System Functional Regeneration & Tissue Preservation Model."""

import pytest
from aegis.model_13_functional_regeneration import (
    TissueDamageState,
    STRATEGY_UNASSISTED_HUMAN,
    STRATEGY_STIMULATED_BIOENGINEERED,
    STRATEGY_PRESERVATION_PEG_FUSION,
    STRATEGY_ACOMYS_DERMAL_PROGRAM,
    STRATEGY_SPECULATIVE_EPIMORPHIC,
    evaluate_functional_recovery_timeline,
    run_comprehensive_regeneration_benchmark,
)


@pytest.fixture
def severe_wound():
    return TissueDamageState(
        injury_name="Severe Combined Penetrating Injury",
        skin_defect_radius_mm=20.0,
        muscle_loss_volume_cm3=35.0,
        muscle_compartment_volume_cm3=180.0,  # ~19.4% VML
        nerve_gap_length_mm=45.0,
        vascular_ischemic_fraction=0.60,
        membrane_rupture_severity=0.75,
    )


def test_unassisted_human_vml_failure(severe_wound):
    res = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_UNASSISTED_HUMAN)
    
    # Unassisted VML (>15%) leads to permanent fibrotic deficit
    assert res["axes"]["muscle_structural_outcome"] == "CHRONIC_FIBROTIC_VML_DEFICIT"
    assert res["axes"]["muscle_contractile_recovery_pct"] < 60.0
    # Spontaneous nerve growth takes > 40 days
    assert res["axes"]["innervation_recovery_days"] > 40.0


def test_peg_fusion_preservation_breakthrough(severe_wound):
    res = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_PRESERVATION_PEG_FUSION)
    
    # Membrane fusion salvages severed axons in days rather than waiting for 45 mm regrowth
    assert res["axes"]["innervation_mechanism"] == "MEMBRANE_FUSION_AXON_SALVAGE"
    assert res["axes"]["innervation_recovery_days"] <= 7.0
    assert res["axes"]["nerve_conduction_restored_pct"] >= 70.0
    # Muscle contractile force retention is significantly superior
    assert res["axes"]["muscle_contractile_recovery_pct"] >= 70.0


def test_stimulated_conduit_acceleration(severe_wound):
    res_stim = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_STIMULATED_BIOENGINEERED)
    res_unassisted = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_UNASSISTED_HUMAN)
    
    # Accelerated axonal elongation (3.5 mm/day) finishes significantly faster than unassisted (1.5 mm/day)
    assert res_stim["axes"]["innervation_recovery_days"] < res_unassisted["axes"]["innervation_recovery_days"]
    assert res_stim["axes"]["innervation_recovery_days"] < 35.0


def test_acomys_scarless_healing_profile(severe_wound):
    res = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_ACOMYS_DERMAL_PROGRAM)
    
    assert res["axes"]["scar_free_healing"] is True
    assert res["axes"]["residual_fibrosis_fraction"] < 0.10


def test_oncological_safety_tiers(severe_wound):
    res_base = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_UNASSISTED_HUMAN)
    res_spec = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_SPECULATIVE_EPIMORPHIC)
    
    assert res_base["axes"]["oncogenic_safety_tier"] == "PHYSIOLOGICAL_BASELINE"
    # Speculative blastema has synthetic apoptosis kill-switch
    assert res_spec["axes"]["oncogenic_safety_tier"] == "STABILIZED_VIA_SYNTHETIC_CIRCUIT"


def test_comprehensive_benchmark_runner():
    bench = run_comprehensive_regeneration_benchmark()
    assert len(bench) >= 5
    for strat_id, data in bench.items():
        assert "time_to_functional_restoration_days" in data
        assert "axes" in data


def test_peg_fusion_5day_force_refutation(severe_wound):
    res = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_PRESERVATION_PEG_FUSION)
    
    # CNAP conduction is salvaged rapidly
    assert res["axes"]["nerve_conduction_restored_pct"] >= 70.0
    # BUT contractile force at Day 5 is strictly limited (refuting the 92% claim)
    assert res["axes"]["muscle_contractile_5d_pct"] < 30.0
    # Synkinesis / motor misdirection rate is substantial
    assert res["axes"]["motor_axon_misdirection_rate_pct"] >= 35.0


def test_human_vml_clinical_deficit(severe_wound):
    res = evaluate_functional_recovery_timeline(severe_wound, STRATEGY_STIMULATED_BIOENGINEERED)
    
    # Volumetric filling is high with bioscaffold
    assert res["axes"]["vml_mass_fill_pct"] >= 70.0
    # Force improvement over pre-op deficit is moderate (+25-38%)
    assert res["axes"]["vml_strength_improvement_vs_preop_pct"] > 25.0
    # Persistent deficit relative to uninjured intact limb remains
    assert res["axes"]["vml_residual_deficit_vs_intact_pct"] >= 25.0
    assert res["axes"]["human_complete_restoration_achieved"] is False

