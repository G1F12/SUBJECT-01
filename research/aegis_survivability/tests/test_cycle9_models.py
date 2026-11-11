"""
Unit tests for AEGIS-01 Research Cycle 9 models and validation engine.
Independent Prediction, Biological Architecture & Canonical Integration.
"""

import pytest
from aegis.cycle9_models import (
    PARAMETER_FORENSIC_LEDGER,
    HUANG_2018_HOLDOUT_SET,
    VML_COHORTS_C9,
    BIOLOGICAL_GEOMETRY_EVALUATION,
    SUBJECT01_CANONICAL_AUDIT_C9,
    predict_unmodified_cycle8,
    predict_cycle9_reconciled,
    evaluate_independent_materials_holdout,
    audit_vml_regeneration_loso,
    run_thermodynamically_corrected_cpe45,
    evaluate_cpe45_corrections,
    run_cycle9_master_validation,
)


def test_phase1_parameter_forensic_audit():
    """Verify forensic audit correctly detects parameter conflations and provenance."""
    ledger = {item["parameter"]: item for item in PARAMETER_FORENSIC_LEDGER}
    
    # Check 38% ventral macro-layer conflation detection
    assert "Phi_IF (Pangolin Scale)" in ledger
    pang = ledger["Phi_IF (Pangolin Scale)"]
    assert pang["cycle8_value"] == 0.38
    assert pang["cycle9_verdict"] == "INVALIDATED_CONFLATION / MODEL_ASSUMPTION"
    assert "VENTRAL MACRO-LAYER" in pang["true_measurement_type"]
    
    # Check E_dry provenance
    assert "E_dry (4.60 +/- 0.45 GPa)" in ledger
    edry = ledger["E_dry (4.60 +/- 0.45 GPa)"]
    assert edry["cycle9_verdict"] == "VERIFIED_PRIMARY_MEASUREMENT"
    
    # Check sheep and bovine estimates
    assert ledger["Phi_IF (Sheep Horn)"]["cycle9_verdict"] == "LITERATURE_DERIVED_ESTIMATE"
    assert ledger["Phi_IF (Bovine Hoof)"]["cycle9_verdict"] == "LITERATURE_DERIVED_ESTIMATE"


def test_phase2_independent_materials_holdout():
    """Verify true holdout evaluation on 28 independent observations from Huang et al. 2018."""
    assert len(HUANG_2018_HOLDOUT_SET) == 28
    
    res = evaluate_independent_materials_holdout()
    assert res["dataset_metadata"]["total_independent_observations"] == 28
    assert len(res["dataset_metadata"]["species_evaluated"]) == 4
    
    # Baseline mean MAE
    baseline_mae = res["baseline_performance"]["baseline_mae_gpa"]
    assert pytest.approx(baseline_mae, abs=0.01) == 0.606
    
    # Unmodified Cycle 8 fails on hydrated cellular horn
    c8_mae = res["unmodified_cycle8_performance"]["model_mae_gpa"]
    assert c8_mae > 1.0  # ~1.308 GPa
    assert res["unmodified_cycle8_performance"]["error_reduction_pct"] < 0  # Severe overprediction
    
    # Reconciled Cycle 9 achieves positive error reduction
    c9_mae = res["reconciled_cycle9_performance"]["model_mae_gpa"]
    assert c9_mae < 0.45  # 0.397 GPa
    assert res["reconciled_cycle9_performance"]["error_reduction_pct"] > 30.0  # +34.55%
    
    # Check arithmetic discrepancy explanation
    arith = res["arithmetic_divergence_explained"]
    assert "cross-validated training baseline" in arith["root_cause_of_divergence"]
    assert "50.10%" in arith["static_baseline_arithmetic"]


def test_phase3_vml_regeneration_strict_dynamic_loso():
    """Verify 11-cohort functional regeneration strict LOSO and human translation limit."""
    assert len(VML_COHORTS_C9) == 11
    total_n = sum(c["n"] for c in VML_COHORTS_C9)
    assert total_n == 82
    
    res = audit_vml_regeneration_loso()
    assert res["total_cohorts"] == 11
    assert res["total_animals"] == 82
    assert res["overall_performance"]["strict_dynamic_loso_mae"] < 7.0  # 6.02%
    assert res["overall_performance"]["error_reduction_pct"] > 50.0  # +70.92%
    
    # Human clinical translation must be INSUFFICIENT_EVIDENCE
    assert res["human_scaling_status"] == "INSUFFICIENT_EVIDENCE"


def test_phase4_biological_geometry_comparison():
    """Verify comparative mechanics of three armor architectures."""
    geoms = BIOLOGICAL_GEOMETRY_EVALUATION
    assert len(geoms) == 6
    
    # Check strain metric
    strain_row = next(r for r in geoms if "Strain" in r["metric"])
    assert "1.75%" in strain_row["monolithic_plate"]
    assert "40 - 60%" in strain_row["segmented_imbricated_scales"]
    assert "25 - 35%" in strain_row["subdermal_fibrous_lattice"]


def test_phase5_cpe45_thermodynamic_corrections():
    """Verify thermodynamically sound CPE45 model."""
    res = evaluate_cpe45_corrections()
    
    # Check that heat capacity is in J/K (not kg)
    assert "270,450 J/K" in res["corrections_audit"]["heat_capacity_units"]
    
    # Baseline simulation (open skin 15%, carrying 6.8 kg)
    sim = res["baseline_simulation"]
    assert pytest.approx(sim["gross_metabolic_w"], abs=1.0) == 695.2
    assert sim["final_t_core_c"] < 40.0
    assert sim["final_t_core_c"] > 39.0
    
    # Restricted ventilation: open skin 5%
    sim_5 = res["open_skin_sweep"]["open_5pct"]
    assert sim_5["time_to_40c_min"] is not None
    assert sim_5["time_to_40c_min"] < 45.0
    
    # Epistemic tags
    assert res["corrections_audit"]["armor_mass_epistemic_tag"] == "Corrected to SCENARIO_ASSUMPTIONS"
    assert res["corrections_audit"]["target_cpe45_status"] == "NOT_EXTERNALLY_VALIDATED"


def test_phase7_subject01_integration_and_master_validation():
    """Verify all SUBJECT-01 audited metrics have explicit epistemic classifications and master status."""
    matrix = run_cycle9_master_validation()
    
    statuses = matrix["mandatory_statuses"]
    assert statuses["PR9_SYNC"] == "PASS"
    assert statuses["KERATIN_PARAMETER_PROVENANCE"] == "PARTIAL"
    assert statuses["MATERIALS_TRUE_HOLDOUT"] == "PASS"
    assert statuses["REGENERATION_LOSO"] == "PASS"
    assert statuses["BIOLOGICAL_GEOMETRY"] == "CONDITIONAL"
    assert statuses["CPE45_CONSISTENCY"] == "PASS"
    assert statuses["CYCLE_10_READY"] == "YES"
    
    # Check all audited indicators in SUBJECT-01 audit have non-empty epistemic tags
    indicators = matrix["phase7_subject01_integration"]
    assert len(indicators) >= 7
    valid_tags = {
        "EXPERIMENTAL_GROUND_TRUTH",
        "PRECLINICAL_VALIDATED / TRANSLATIONAL_INSUFFICIENT",
        "ANALYTICAL_UPPER_BOUND",
        "THERMODYNAMIC_SCENARIO_MODEL",
        "THEORETICAL_ESTIMATE",
        "UNVALIDATED",
        "MODEL_CALIBRATED",
        "LITERATURE_DERIVED",
        "SCENARIO_ASSUMPTIONS",
        "NOT_EXTERNALLY_VALIDATED"
    }
    for ind in indicators:
        assert ind["epistemic_tag"] in valid_tags
