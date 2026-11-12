"""Unit tests for MODEL-12: Biological, Biohybrid & Speculative Materials Evidence Model."""

import pytest
from aegis.model_12_biological_materials import (
    MATERIALS_DATABASE,
    compute_material_mechanics,
    compare_material_archetypes,
)


def test_database_categories_present():
    cats = {mat.category for mat in MATERIALS_DATABASE.values()}
    assert "ARCH-BIO" in cats
    assert "ARCH-HYBRID" in cats
    assert "ARCH-SPEC" in cats


def test_pangolin_keratin_hydration_softening_and_toughness():
    mat = MATERIALS_DATABASE["MAT-KERATIN-PANGOLIN"]
    res_hydrated = compute_material_mechanics(mat, thickness_mm=4.0, hydration_state="hydrated")
    res_dry = compute_material_mechanics(mat, thickness_mm=4.0, hydration_state="dry")
    
    # Dry keratin has higher flexural rigidity
    assert res_dry["flexural_rigidity_nm"] > res_hydrated["flexural_rigidity_nm"]
    # Exceptional hydrated work of fracture ensures cutting resistance > 60 N
    assert res_hydrated["cutting_resistance_n"] > 60.0
    # Mass overhead for torso is moderate (<6 kg)
    assert res_hydrated["torso_added_mass_kg"] < 6.0


def test_uhmwpe_biohybrid_zero_metabolic_maintenance():
    mat = MATERIALS_DATABASE["MAT-BIOHYBRID-UHMWPE"]
    res = compute_material_mechanics(mat, thickness_mm=4.0)
    
    # Synthetic polymers consume zero biological ATP
    assert res["metabolic_power_cost_torso_w"] == 0.0
    # Extreme ductility and fracture toughness give high cutting resistance
    assert res["cutting_resistance_n"] > 100.0
    assert res["category"] == "ARCH-HYBRID"


def test_exploratory_ballistics_status():
    mat = MATERIALS_DATABASE["MAT-ENDOGENOUS-FGM"]
    res = compute_material_mechanics(mat, thickness_mm=4.0)
    
    # Ballistic metrics must be explicitly flagged as EXPLORATORY
    assert res["ballistic_status"] == "EXPLORATORY_NUMERICAL_UNVALIDATED"
    assert "v50_exploratory_fragment_m_s" in res
    assert res["v50_exploratory_fragment_m_s"] > 100.0


def test_all_materials_comparative_runner():
    res = compare_material_archetypes()
    assert len(res) == len(MATERIALS_DATABASE)
    for mat_id, data in res.items():
        assert "puncture_resistance_n" in data
        assert "fatigue_safety_factor" in data
        assert len(data["translational_barriers"]) > 0


def test_fgm_cutting_regimes_discrepancy_resolved():
    mat = MATERIALS_DATABASE["MAT-ENDOGENOUS-FGM"]
    res = compute_material_mechanics(mat, thickness_mm=4.0)
    
    # Mode I steady-state crack growth work + 15 N nominal friction = 48.6 N
    assert res["mode_1_crack_threshold_n"] == pytest.approx(48.6, abs=0.1)
    # Macroscopic blunt guillotine wedge indentation yields ~680 N
    assert res["guillotine_wedge_chop_n"] == pytest.approx(679.8, abs=1.0)
    # Lateral draw slicing reduces normal cut resistance:
    # Knife wedge with drawing (xi=4): 164.9 N (vs 680 N guillotine chop)
    assert res["draw_slicing_knife_n"] == pytest.approx(164.9, abs=1.0)
    # Razor scalpel with drawing (xi=4): 30.4 N
    assert res["draw_slicing_scalpel_n"] == pytest.approx(30.4, abs=1.0)

    # Biohybrids have non-zero immune clearance tax
    uhmwpe = compute_material_mechanics(MATERIALS_DATABASE["MAT-BIOHYBRID-UHMWPE"], thickness_mm=4.0)
    assert uhmwpe["biological_immune_clearance_w"] > 0.0

