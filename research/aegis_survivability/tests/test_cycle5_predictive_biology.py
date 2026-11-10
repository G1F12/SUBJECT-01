"""Test suite for AEGIS-01 Research Cycle 5: Predictive Biology & Epistemic Rectification.

Validates:
- Track 1 VML: Independent baseline comparison, LOPO-CV RMSE superiority of featureless baseline, and missing-data policy.
- Track 2 Materials: Epistemic 5-tier classification, LEFM Irwin identity verification, and holdout unvalidated status.
- Track 3 Thermoregulation: Matched microclimate simulation against Montain et al. (1994) (50% RH vs 80% RH divergence).
- Endogenous vs Biohybrid biomechanics and SUBJECT-01 system compatibility under TARGET-CPE45.
"""

import pytest
import math
from aegis.external_validation import (
    evaluate_track_1_muscle_recovery,
    evaluate_track_2_materials,
    evaluate_track_3_thermoregulation,
    DZIKI_2016_AUTHENTIC_COHORT
)
from aegis.model_14_architecture_categories import (
    evaluate_subject01_compatibility,
    ARCH_BIO_KERATIN_FGM,
    ARCH_HYBRID_UHMWPE_CERAMIC,
    ARCH_SPEC_GRAPHENE_RADIATOR,
    SUBJECT01_MUSCLE_ARCH_A
)


def test_vml_independent_baseline_superiority():
    """Verify that featureless cohort-mean baseline achieves MAE = 38.89 pp and RMSE = 46.44 pp,
    and that the trained group-mean predictor fails to beat baseline RMSE.
    """
    res = evaluate_track_1_muscle_recovery()
    base = res["independent_baseline_lopo"]
    
    # Exact prompt benchmarks
    assert base["cohort_mean_lopo_mae"] == pytest.approx(38.89, abs=0.1)
    assert base["cohort_mean_lopo_rmse"] == pytest.approx(46.44, abs=0.1)
    
    # Group model LOPO RMSE is 48.94 pp -> WORSE than simple baseline!
    group_rmse = res["lopo_cross_validation"]["lopo_rmse"]
    assert group_rmse == pytest.approx(48.94, abs=0.1)
    assert group_rmse > base["cohort_mean_lopo_rmse"]
    assert base["model_beats_baseline_rmse"] is False


def test_vml_missing_data_policy_complete_cases():
    """Verify that under Policy A (complete cases N=12, excluding S01 whose baseline is missing),
    the group model underperforms the simple baseline on BOTH MAE and RMSE.
    """
    res = evaluate_track_1_muscle_recovery()
    pol_a = res["missing_data_policies"]["policy_a_complete_cases_n12"]
    
    assert pol_a["baseline_lopo_mae"] == pytest.approx(39.59, abs=0.1)
    assert pol_a["baseline_lopo_rmse"] == pytest.approx(47.11, abs=0.1)
    
    assert pol_a["group_lopo_mae"] == pytest.approx(42.91, abs=0.1)
    assert pol_a["group_lopo_rmse"] == pytest.approx(52.51, abs=0.1)
    
    assert pol_a["group_beats_mae"] is False if "group_beats_mae" in pol_a else pol_a["group_lopo_mae"] > pol_a["baseline_lopo_mae"]
    assert pol_a["group_lopo_rmse"] > pol_a["baseline_lopo_rmse"]


def test_materials_epistemic_classification_and_k1c():
    """Verify that materials properties are classified into 5 epistemic tiers and
    Pangolin Keratin K1c is tagged as a mathematical Irwin identity check.
    """
    res = evaluate_track_2_materials()
    tiers = res["epistemic_classification"]
    
    assert tiers["tier_1_raw_calibration_constants"] == 11
    assert tiers["tier_2_mathematical_identities"] == 1
    assert tiers["tier_3_derived_boundary_value_predictions"] == 2
    assert tiers["tier_5_true_independent_holdout_validation"] == 0
    
    k1c_audit = res["k1c_independence_audit"]
    assert k1c_audit["status"] == "MATHEMATICAL_IDENTITY_VERIFICATION"
    assert k1c_audit["calculated_k1c_mpa_m05"] == pytest.approx(6.08, abs=0.05)


def test_thermoregulation_montain_matched_conditions():
    """Verify matched-conditions simulation against Montain et al. (1994)
    and prove 50% RH vs 80% RH evaporative capacity divergence (>50% drop).
    """
    res = evaluate_track_3_thermoregulation()
    audit = res["montain_1994_matched_conditions_audit"]
    
    assert audit["experimental_conditions"]["ambient_rh_tropical_pct"] == 50.0
    
    e_50 = audit["humidity_divergence_findings"]["evaporative_capacity_at_50rh_w"]
    e_80 = audit["humidity_divergence_findings"]["evaporative_capacity_at_80rh_w"]
    loss_pct = audit["humidity_divergence_findings"]["capacity_loss_at_80rh_pct"]
    
    assert e_50 == pytest.approx(109.9, abs=1.0)
    assert e_80 == pytest.approx(50.6, abs=1.0)
    assert loss_pct == pytest.approx(53.96, abs=0.5)


def test_subject01_cpe45_multiclimate_dynamics():
    """Verify that Muscle Architecture A with Endogenous Armor succeeds in temperate climate
    but encounters thermal hyperthermia in humid jungle climate under TARGET-CPE45.
    """
    res_temp = evaluate_subject01_compatibility(ARCH_BIO_KERATIN_FGM, SUBJECT01_MUSCLE_ARCH_A, climate="temperate")
    res_jungle = evaluate_subject01_compatibility(ARCH_BIO_KERATIN_FGM, SUBJECT01_MUSCLE_ARCH_A, climate="hot_humid")
    
    # Temperate: thermal equilibrium maintained, sustainable
    assert res_temp["thermal_and_cpe45"]["heating_rate_k_min"] == 0.000
    assert res_temp["feasibility_verdict"] == "COMPATIBLE_WITH_SUBJECT01"
    
    # Jungle: severe heat storage due to 80% RH ceiling and skin occlusion
    assert res_jungle["thermal_and_cpe45"]["heating_rate_k_min"] > 0.080
    assert res_jungle["thermal_and_cpe45"]["reaches_hyperthermia_in_cpe45"] is True
    assert res_jungle["feasibility_verdict"] == "THERMAL_OR_MASS_BOTTLENECK"
