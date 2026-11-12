"""
Unit tests for AEGIS-01 Research Cycle 11 Core Models & Forensic Verification Engine.
"""

import pytest
import math
from aegis.cycle11_models import (
    evaluate_li2010_forensic_recalculation,
    evaluate_tombolato2010_audit,
    audit_preregistration_status,
    predict_keratin_mechanics_cycle11,
    KeratinMicrostructure,
    run_leakage_free_regeneration_loso,
    evaluate_biological_protection_tradeoffs,
    simulate_cpe45_thermodynamic_trajectory,
)


def test_li2010_forensic_recalculation():
    """Verify exact recomputed metrics for Li et al. (2010) ground truth."""
    res = evaluate_li2010_forensic_recalculation()
    
    # Exact benchmarks from prompt
    assert abs(res["metrics"]["mae_gpa"] - 0.27833) < 1e-4
    assert abs(res["metrics"]["rmse_gpa"] - 0.30851) < 1e-4
    assert abs(res["metrics"]["bias_gpa"] - 0.17767) < 1e-4
    assert abs(res["baselines"]["retrospective_test_mean"]["mae_gpa"] - 0.50444) < 1e-4
    
    # Dual baselines
    assert abs(res["baselines"]["retrospective_test_mean"]["error_reduction_pct"] - 44.82) < 0.1
    assert abs(res["baselines"]["prospective_training_all_mean"]["error_reduction_pct"] - 61.73) < 0.1
    assert abs(res["baselines"]["prospective_training_tension_mean"]["error_reduction_pct"] - 52.69) < 0.1
    
    # 8% moisture overprediction interval check
    assert res["metrics"]["interval_1sigma_deviations_gpa"][1] > 0.40  # ~0.402 GPa outside 1-sigma
    assert res["verdict"] == "PARTIAL"


def test_tombolato2010_forensic_audit():
    """Verify forensic audit of Tombolato et al. (2010)."""
    res = evaluate_tombolato2010_audit()
    assert res["verdict"] == "NOT_VERIFIED"
    assert res["primary_source_doi_correction"]["true_tombolato_doi"] == "10.1016/j.actbio.2009.06.033"
    assert "08.033" in res["primary_source_doi_correction"]["cycle10_claimed_doi"]
    assert res["mode_conflation_audit"]["tabular_data_exists_for_bending"] is False
    assert res["parameter_leakage_audit"]["bending_mode_factor"] == 0.90


def test_preregistration_audit():
    """Verify cryptographic hash vs chronological pre-registration audit."""
    res = audit_preregistration_status()
    assert res["hash_strictly_reproducible"] is True
    assert res["git_provenance"]["co_committed_with_evaluation"] is True
    assert res["verdict"] == "PRE_REGISTRATION_UNVERIFIED"
    assert res["four_tier_taxonomy"]["REPRODUCIBLE_HASH"]["proves_temporal_priority"] is False
    assert res["four_tier_taxonomy"]["CHRONOLOGICALLY_PRE_REGISTERED"]["proves_temporal_priority"] is True


def test_keratin_mechanics_cycle11_cross_material():
    """Verify multi-parameter keratin model across species and hydration states."""
    # Bovid horn (Li 2010)
    horn_bovine = KeratinMicrostructure(
        species="Bos taurus",
        tissue_type="horn",
        phi_if=0.55,
        cystine_mol_pct=7.5,
        porosity=0.045,
        tubule_aspect_ratio=2.5,
        orientation_deg=0.0
    )
    
    # Dry tension
    pred_dry = predict_keratin_mechanics_cycle11(horn_bovine, hydration_w=0.00, mode="tension")
    assert 2.0 < pred_dry["predicted_e_gpa"] < 2.8
    assert pred_dry["tg_effective_c"] > 140.0
    
    # Wet tension
    pred_wet = predict_keratin_mechanics_cycle11(horn_bovine, hydration_w=0.19, mode="tension")
    assert pred_wet["predicted_e_gpa"] < 1.2
    assert pred_wet["tg_effective_c"] < 35.0  # Glass transition depressed toward room temp
    
    # Equine Hoof (high cystine, low porosity)
    hoof_equine = KeratinMicrostructure(
        species="Equus caballus",
        tissue_type="hoof",
        phi_if=0.60,
        cystine_mol_pct=14.5,  # High disulfide crosslink density
        porosity=0.015,
        tubule_aspect_ratio=5.0,
        orientation_deg=0.0
    )
    pred_hoof_dry = predict_keratin_mechanics_cycle11(hoof_equine, hydration_w=0.00, mode="compression")
    assert pred_hoof_dry["predicted_e_gpa"] > pred_dry["predicted_e_gpa"] * 1.3
    assert pred_hoof_dry["tg_effective_c"] > pred_dry["tg_effective_c"]


def test_regeneration_loso_leakage_free():
    """Verify leakage-free prospective LOSO on 11 VML cohorts."""
    res = run_leakage_free_regeneration_loso()
    assert res["cluster_audit"]["independent_research_groups"] == 1
    assert res["loso_metrics"]["error_reduction_vs_prospective_pct"] > 40.0
    assert res["verdict"] == "PARTIAL"
    assert len(res["predictions"]) == 11


def test_biological_protection_tradeoffs():
    """Verify multi-criteria evaluation of Architectures A, B, and C."""
    res = evaluate_biological_protection_tradeoffs()
    assert "Architecture_B" in res["fewest_unproven_assumptions"]
    assert res["verdict"] == "CONDITIONAL"
    arch_b = res["architectures"]["Architecture_B_Segmented_Imbricated"]
    arch_a = res["architectures"]["Architecture_A_Monolithic_Rigid"]
    assert arch_b["mean_overall_score"] > arch_a["mean_overall_score"]


def test_cpe45_mass_energy_reconciliation():
    """Verify rigorous mass and energy conservation in TARGET-CPE45."""
    res = simulate_cpe45_thermodynamic_trajectory(
        body_mass_kg=75.0,
        armor_mass_kg=6.8,
        open_skin_fraction=0.15,
        t_amb_c=35.0,
        rh_pct=50.0,
        duration_min=45.0
    )
    # Check exact J/K heat capacity: 75*3470 + 6.8*1500 = 260250 + 10200 = 270450 J/K
    assert abs(res["parameters"]["heat_capacity_j_k"] - 270450.0) < 1.0
    assert abs(res["parameters"]["q_thermal_w"] - 556.16) < 1.0
    assert res["results"]["final_t_core_c"] < 40.0
    assert res["results"]["threshold_breached"] is False
    assert res["verdict"] == "NOT_EXTERNALLY_VALIDATED"
