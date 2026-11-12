"""Unit tests for MODEL-14: Three-Tier Architectural Categorization & SUBJECT-01 Compatibility Engine."""

import pytest
from aegis.model_14_architecture_categories import (
    ARCH_BIO_KERATIN_FGM,
    ARCH_HYBRID_UHMWPE_CERAMIC,
    ARCH_SPEC_GRAPHENE_RADIATOR,
    SUBJECT01_MUSCLE_ARCH_A,
    SUBJECT01_CONDITIONAL_ARCH_B,
    SUBJECT01_CONDITIONAL_ARCH_C,
    evaluate_subject01_compatibility,
    run_cross_category_evaluation,
)


def test_categories_distinct():
    assert ARCH_BIO_KERATIN_FGM.category == "ARCH-BIO"
    assert ARCH_HYBRID_UHMWPE_CERAMIC.category == "ARCH-HYBRID"
    assert ARCH_SPEC_GRAPHENE_RADIATOR.category == "ARCH-SPEC"
    
    assert ARCH_BIO_KERATIN_FGM.is_fully_endogenous is True
    assert ARCH_HYBRID_UHMWPE_CERAMIC.requires_synthetic_implants is True
    assert ARCH_SPEC_GRAPHENE_RADIATOR.requires_scientific_breakthrough is True


def test_subject01_muscle_arch_a_temperate_compatibility():
    # In temperate conditions (25C, 50% RH), ARCH-BIO-4 should be compatible
    res = evaluate_subject01_compatibility(
        arch=ARCH_BIO_KERATIN_FGM,
        host=SUBJECT01_MUSCLE_ARCH_A,
        climate="temperate"
    )
    
    assert res["feasibility_verdict"] == "COMPATIBLE_WITH_SUBJECT01"
    assert res["locomotion"]["speed_retention_pct"] > 90.0
    assert res["locomotion"]["tendon_status"] == "SAFE"
    assert res["thermal_and_cpe45"]["reaches_hyperthermia_in_cpe45"] is False
    # Heating rate in temperate conditions is low (<0.04 K/min)
    assert res["thermal_and_cpe45"]["heating_rate_k_min"] < 0.04


def test_subject01_hot_humid_thermal_collapse_preservation():
    # In hot-humid conditions (35C, 80% RH), skin occlusion triggers thermal limitation
    res = evaluate_subject01_compatibility(
        arch=ARCH_BIO_KERATIN_FGM,
        host=SUBJECT01_MUSCLE_ARCH_A,
        climate="hot_humid"
    )
    
    # Negative result must be preserved: thermal bottleneck occurs
    assert res["thermal_and_cpe45"]["reaches_hyperthermia_in_cpe45"] is True
    # Rate of heating must be realistic (~0.09 to 0.16 K/min)
    assert 0.08 <= res["thermal_and_cpe45"]["heating_rate_k_min"] <= 0.18
    # Time to 40C is between 18 and 35 minutes
    assert 16.0 <= res["thermal_and_cpe45"]["time_to_40_0c_min"] <= 35.0


def test_biohybrid_skin_sparing_advantage():
    # Biohybrid has minimal skin occlusion (8%) because it is subdermal
    res_hybrid = evaluate_subject01_compatibility(
        arch=ARCH_HYBRID_UHMWPE_CERAMIC,
        host=SUBJECT01_MUSCLE_ARCH_A,
        climate="temperate"
    )
    
    assert res_hybrid["thermal_and_cpe45"]["effective_dissipation_w"] > 700.0
    assert res_hybrid["locomotion"]["accel_retention_pct"] > 94.0


def test_cross_category_evaluation_suite():
    suite = run_cross_category_evaluation()
    assert len(suite) == 3
    for arch_id, climates in suite.items():
        assert "temperate" in climates
        assert "hot_humid" in climates
