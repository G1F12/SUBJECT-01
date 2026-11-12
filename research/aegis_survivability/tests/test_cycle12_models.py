"""
Unit tests for AEGIS-01 Research Cycle 12 Core Models & Verification Engine.
Predictive Biology · Independent Validation · Biological Architecture.
"""

import pytest
import math
from aegis.cycle12_models import (
    calculate_fox_tg,
    calculate_linear_tg_cycle11,
    audit_keratin_tg_parameters,
    compare_keratin_physical_models,
    audit_regeneration_priors_and_sensitivity,
    evaluate_biological_protection_robustness,
    simulate_cpe45_coupling_and_humidity_uncertainty,
)


def test_audit_keratin_tg_parameters():
    """Verify Tg equation audit, Fox comparison, and parameter provenance."""
    res = audit_keratin_tg_parameters()
    assert res["verdict"] == "MODEL_ASSUMPTIONS_IDENTIFIED"
    prov = res["parameters_provenance"]
    assert prov["cystine_slope_2_5"]["status"] == "MODEL_ASSUMPTION"
    assert prov["hydration_slope_750"]["status"] == "MODEL_ASSUMPTION"
    
    # Fox equation behavior
    tg_dry_fox = calculate_fox_tg(0.0)
    assert abs(tg_dry_fox - 160.0) < 0.5
    tg_wet_fox = calculate_fox_tg(0.19)
    assert 30.0 < tg_wet_fox < 40.0


def test_compare_keratin_physical_models():
    """Verify 5-model comparison on Li 2010 and cross-material domain boundary."""
    res = compare_keratin_physical_models()
    assert res["verdict"] == "NO_VERIFIED_IMPROVEMENT"
    li = res["li2010_evaluations"]
    
    # Model 4 (Hill + Microarchitecture) achieves lower error on Li 2010 than Model 2 and Model 5
    assert li["Model_4_Hydration_Plus_Microarchitecture"]["mae_gpa"] < 0.30
    assert li["Model_5_Cycle11_Nine_Parameter"]["mae_gpa"] > 0.50
    
    # Cross-material hoof failure
    hoof = res["equine_hoof_extrapolation"]
    assert hoof["domain_boundary_breached"] is True
    assert hoof["error_on_dry_hoof_gpa"] > 11.0


def test_audit_regeneration_priors_and_sensitivity():
    """Verify regeneration priors sensitivity and external multi-center lab audit."""
    res = audit_regeneration_priors_and_sensitivity()
    assert res["verdict"] == "INSUFFICIENT_DATA"
    assert abs(res["baseline_mae_pct"] - 7.56) < 0.1
    
    # Sensitivity sweeps exist
    sens = res["sensitivity_analysis"]
    assert "ecm" in sens
    assert "+10%" in sens["ecm"]
    
    # External studies recorded
    studies = res["external_laboratory_survey"]
    assert len(studies) >= 3
    assert any("Sicari" in s["study"] for s in studies)
    assert any("Merritt" in s["study"] for s in studies)


def test_evaluate_biological_protection_robustness():
    """Verify Pareto non-dominance proof and scale kinematics."""
    res = evaluate_biological_protection_robustness()
    assert res["verdict"] == "CONDITIONAL"
    
    # Pareto dominance proof: neither B dominates A nor B dominates C
    pareto = res["pareto_dominance_analysis"]
    assert bool(pareto["b_strictly_dominates_a"]) is False
    assert bool(pareto["b_strictly_dominates_c"]) is False
    
    # Monte Carlo weight distribution
    mc = res["monte_carlo_weight_sensitivity_pct"]
    assert mc["architecture_b_wins"] > 85.0
    assert mc["architecture_c_wins"] > 5.0
    
    # Kinematics parameter table
    kin = res["scale_kinematics_model"]
    assert len(kin) == 3
    assert kin[1]["max_skin_strain_pct"] >= 45.0


def test_simulate_cpe45_coupling_and_humidity_uncertainty():
    """Verify TARGET-CPE45 mass-energy consistency and humidity sensitivity."""
    res = simulate_cpe45_coupling_and_humidity_uncertainty()
    assert res["verdict"] == "NOT_VALIDATED"
    assert abs(res["nominal_heat_capacity_j_k"] - 270450.0) < 1.0
    
    scenarios = res["humidity_scenarios"]
    # At 50% RH: survives below 40C
    sc_50 = [s for s in scenarios if s["ambient_rh_pct"] == 50.0][0]
    assert sc_50["threshold_breached"] is False
    assert sc_50["final_t_core_c"] < 40.0
    
    # At 90% RH: breaches 40C in < 40 min
    sc_90 = [s for s in scenarios if s["ambient_rh_pct"] == 90.0][0]
    assert sc_90["threshold_breached"] is True
    assert float(sc_90["time_to_40c_min"]) < 40.0
