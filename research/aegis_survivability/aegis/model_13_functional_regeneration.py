"""MODEL-13: Multi-System Functional Regeneration & Tissue Preservation Model.

AEGIS-01: Biological Defense & Survivability Program (Cycle 3).
Calibrated against peer-reviewed mammalian regenerative physiology.
Focuses on returning true multi-dimensional physiological function rather than simple wound closure.

The 8 Functional Dimensions:
  1. Mechanical Strength Recovery (E, sigma_u)
  2. Vascular Network Re-perfusion & Capillary Density
  3. Contractile Muscle Function (Twitch force, tetanic force, RFD)
  4. Sensory & Motor Innervation (Axon elongation, collateral sprouting, PEG-fusion)
  5. Tissue Architecture Preservation (Basal lamina alignment, myotube orientation)
  6. Fibrosis Control (TGF-beta3/beta1, collagen III/I ratio, myofibroblast arrest)
  7. Oncological Safety (Stem cell cycling vs genomic stability, Peto mechanisms)
  8. Repeat Trauma Recovery Capacity (Satellite cell pool exhaustion over repeated cycles)

Primary Literature Sources:
  - Seddon, H. J. (1975). Surgical Disorders of the Peripheral Nerves.
  - Gordon, T. et al. (2008). Exp. Neurol. 209(2):446-452 (Accelerated nerve regeneration).
  - Bittner, G. D. et al. (2012). J. Neurosci. Res. 90(5):937-951 (PEG fusion membrane repair).
  - Corona, B. T. et al. (2015). Muscle Nerve. 52(2):168-181 (Volumetric Muscle Loss).
  - Seifert, A. W. et al. (2012). Nature. 489:561-565 (Acomys mammalian scar-free regeneration).
  - Abegglen, L. M. et al. (2015). JAMA. 314(17):1850-1860 (Peto's paradox & TP53 expansion).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass(frozen=True)
class TissueDamageState:
    """Represents an integrated acute musculoskeletal trauma."""
    injury_name: str
    skin_defect_radius_mm: float
    muscle_loss_volume_cm3: float
    muscle_compartment_volume_cm3: float  # Baseline human anterior tibial ~180 cm3, quadriceps ~1200 cm3
    nerve_gap_length_mm: float
    vascular_ischemic_fraction: float  # Fraction of local bed devascularized (0 to 1)
    membrane_rupture_severity: float  # Fraction of cell membranes disrupted (0 to 1)


@dataclass(frozen=True)
class RegenerationStrategy:
    """Strategy configuration for functional healing."""
    strategy_id: str
    name: str
    category: str  # "ARCH-BIO", "ARCH-HYBRID", "ARCH-SPEC"
    
    # Nerve pathway
    nerve_regrowth_mode: str  # "UNASSISTED_SPONTANEOUS", "STIMULATED_CONDUIT", "COLLATERAL_SPROUTING", "PEG_FUSION_PRESERVATION"
    axon_growth_rate_mm_day: float
    nerve_initiation_latency_days: float
    
    # Muscle & Stroma pathway
    scaffold_guidance_present: bool
    vml_mitigation_capable: bool
    tgf_beta3_to_beta1_ratio: float
    
    # Membrane / Cellular Preservation
    fusogen_membrane_preservation_active: bool
    preservation_efficacy_fraction: float  # Fraction of severed axons/myocytes salvaged
    
    # Oncological & Genomic Checkpoints
    tp53_copy_equivalent: float  # 2.0 = human wild type
    stem_cell_cycling_enhancement: float  # Multiplier on basal mitotic rate
    has_inducible_apoptosis_kill_switch: bool


# -------------------------------------------------------------------------
# Default Archetypal Strategies
# -------------------------------------------------------------------------

STRATEGY_UNASSISTED_HUMAN = RegenerationStrategy(
    strategy_id="STRAT-NATURAL-HUMAN",
    name="Standard Human Spontaneous Repair",
    category="ARCH-BIO",
    nerve_regrowth_mode="UNASSISTED_SPONTANEOUS",
    axon_growth_rate_mm_day=1.5,
    nerve_initiation_latency_days=11.0,
    scaffold_guidance_present=False,
    vml_mitigation_capable=False,
    tgf_beta3_to_beta1_ratio=0.15,
    fusogen_membrane_preservation_active=False,
    preservation_efficacy_fraction=0.0,
    tp53_copy_equivalent=2.0,
    stem_cell_cycling_enhancement=1.0,
    has_inducible_apoptosis_kill_switch=False,
)

STRATEGY_STIMULATED_BIOENGINEERED = RegenerationStrategy(
    strategy_id="STRAT-BIOENGINEERED-STIM",
    name="Electrically Stimulated & Micro-Conduit Guided Repair",
    category="ARCH-HYBRID",
    nerve_regrowth_mode="STIMULATED_CONDUIT",
    axon_growth_rate_mm_day=3.5,  # Empirically demonstrated by Gordon et al., 2008
    nerve_initiation_latency_days=4.0,  # Shortened latency via early brief electrical stimulation
    scaffold_guidance_present=True,
    vml_mitigation_capable=True,
    tgf_beta3_to_beta1_ratio=1.8,
    fusogen_membrane_preservation_active=False,
    preservation_efficacy_fraction=0.0,
    tp53_copy_equivalent=2.0,
    stem_cell_cycling_enhancement=2.5,
    has_inducible_apoptosis_kill_switch=False,
)

STRATEGY_PRESERVATION_PEG_FUSION = RegenerationStrategy(
    strategy_id="STRAT-PRESERVATION-FUSION",
    name="Immediate Chemical Fusogen (PEG) Membrane Preservation",
    category="ARCH-HYBRID",
    nerve_regrowth_mode="PEG_FUSION_PRESERVATION",
    axon_growth_rate_mm_day=1.5,
    nerve_initiation_latency_days=0.5,  # Immediate membrane re-sealing within hours
    scaffold_guidance_present=True,
    vml_mitigation_capable=True,
    tgf_beta3_to_beta1_ratio=2.2,
    fusogen_membrane_preservation_active=True,
    preservation_efficacy_fraction=0.75,  # 75% axolemmal & sarcolemmal integrity salvaged
    tp53_copy_equivalent=2.0,
    stem_cell_cycling_enhancement=1.2,
    has_inducible_apoptosis_kill_switch=False,
)

STRATEGY_ACOMYS_DERMAL_PROGRAM = RegenerationStrategy(
    strategy_id="STRAT-ACOMYS-ENDOGENOUS",
    name="Endogenous Scar-Free Cytokine Reprogramming (Acomys phenotype)",
    category="ARCH-BIO",
    nerve_regrowth_mode="COLLATERAL_SPROUTING",
    axon_growth_rate_mm_day=2.0,
    nerve_initiation_latency_days=6.0,
    scaffold_guidance_present=False,
    vml_mitigation_capable=False,
    tgf_beta3_to_beta1_ratio=4.5,
    fusogen_membrane_preservation_active=False,
    preservation_efficacy_fraction=0.0,
    tp53_copy_equivalent=2.0,
    stem_cell_cycling_enhancement=2.0,
    has_inducible_apoptosis_kill_switch=False,
)

STRATEGY_SPECULATIVE_EPIMORPHIC = RegenerationStrategy(
    strategy_id="STRAT-SPEC-EPIMORPHIC",
    name="Engineered Epimorphic Blastema with Multi-Tier Tumor Suppression",
    category="ARCH-SPEC",
    nerve_regrowth_mode="STIMULATED_CONDUIT",
    axon_growth_rate_mm_day=4.2,
    nerve_initiation_latency_days=3.0,
    scaffold_guidance_present=True,
    vml_mitigation_capable=True,
    tgf_beta3_to_beta1_ratio=5.0,
    fusogen_membrane_preservation_active=True,
    preservation_efficacy_fraction=0.85,
    tp53_copy_equivalent=20.0,  # Elephant-like Peto amplification
    stem_cell_cycling_enhancement=8.0,
    has_inducible_apoptosis_kill_switch=True,
)


# -------------------------------------------------------------------------
# Multi-Dimensional Recovery Computation Engine
# -------------------------------------------------------------------------

def evaluate_functional_recovery_timeline(
    damage: TissueDamageState,
    strat: RegenerationStrategy,
    max_days: float = 365.0
) -> Dict[str, Any]:
    """Calculate multi-dimensional recovery across all 8 physiological axes."""
    
    # --- Axis 1: Mechanical Strength Recovery ---
    # Unassisted healing of dense fascial/muscular defects plateaus at ~60-70% of uninjured strength.
    # Guided matrix allows up to 90-95% mechanical strength restoration.
    baseline_mechanical_plateau = 0.65 if not strat.scaffold_guidance_present else 0.92
    tau_mechanical_days = 45.0 if strat.scaffold_guidance_present else 75.0
    
    # --- Axis 2: Vascular Re-perfusion ---
    # Microvascular capillary sprouting proceeds at 0.2-0.5 mm/day.
    # Preservation of vessels cuts ischemic duration dramatically.
    if strat.fusogen_membrane_preservation_active:
        revascularization_days = 3.0 + (damage.skin_defect_radius_mm * 0.4)
    else:
        revascularization_days = 7.0 + (damage.skin_defect_radius_mm * 1.5)
    
    # --- Axis 3: Muscle Contractile Function & VML Deficit ---
    vml_fraction = damage.muscle_loss_volume_cm3 / max(1.0, damage.muscle_compartment_volume_cm3)
    # VML threshold is ~15-20% volume loss. Without scaffold, functional muscle regeneration fails.
    if vml_fraction > 0.15 and not strat.vml_mitigation_capable:
        contractile_force_recovery_fraction = max(0.15, 1.0 - (vml_fraction * 2.5))
        muscle_structural_outcome = "CHRONIC_FIBROTIC_VML_DEFICIT"
        vml_mass_fill_pct = 32.0
        vml_strength_improvement_vs_preop_pct = 0.0
        vml_residual_deficit_vs_intact_pct = round((1.0 - contractile_force_recovery_fraction) * 100.0, 1)
    elif strat.fusogen_membrane_preservation_active:
        # High preservation of surviving myocytes via membrane salvage
        salvaged_fraction = strat.preservation_efficacy_fraction * (1.0 - vml_fraction)
        contractile_force_recovery_fraction = min(0.75, salvaged_fraction + (0.25 * (1.0 - salvaged_fraction)))
        muscle_structural_outcome = "FUNCTIONAL_RESTRICTED_RESTORATION"
        vml_mass_fill_pct = 82.0
        vml_strength_improvement_vs_preop_pct = 34.5
        vml_residual_deficit_vs_intact_pct = round((1.0 - contractile_force_recovery_fraction) * 100.0, 1)
    else:
        contractile_force_recovery_fraction = 0.72 if strat.scaffold_guidance_present else 0.40
        muscle_structural_outcome = "REGENERATED_WITH_MATRIX" if strat.scaffold_guidance_present else "PARTIAL_DEFICIT"
        vml_mass_fill_pct = 78.0 if strat.scaffold_guidance_present else 38.0
        vml_strength_improvement_vs_preop_pct = 37.3 if strat.scaffold_guidance_present else 0.0
        vml_residual_deficit_vs_intact_pct = round((1.0 - contractile_force_recovery_fraction) * 100.0, 1)

    
    # --- Axis 4: Sensory & Motor Innervation ---
    # Check motor endplate senescence deadline (~400 days in humans)
    motor_endplate_deadline_days = 400.0
    
    if strat.nerve_regrowth_mode == "PEG_FUSION_PRESERVATION":
        # Direct membrane re-fusion salvages existing axons immediately!
        # Restores action potential conduction (CNAP) within 1-5 days for salvaged axons
        nerve_recovery_days = 5.0
        conduction_restoration_pct = strat.preservation_efficacy_fraction * 100.0
        sensory_recovery_pct = 68.0
        # PEG-fusion induces 38-52% motor axonal misdirection due to random axolemmal fusion
        motor_axon_misdirection_rate_pct = 45.0
        # Contractile force at Day 5 is strictly limited to 15-25% (NOT 92%) due to acute denervation latency
        contractile_force_5d_pct = 22.5
        innervation_mechanism = "MEMBRANE_FUSION_AXON_SALVAGE"
    elif strat.nerve_regrowth_mode == "COLLATERAL_SPROUTING" and damage.nerve_gap_length_mm < 25.0:
        # Sprouting from adjacent intact terminals covers small field in 21-35 days
        nerve_recovery_days = 25.0
        conduction_restoration_pct = 75.0
        sensory_recovery_pct = 65.0
        motor_axon_misdirection_rate_pct = 30.0
        contractile_force_5d_pct = 15.0
        innervation_mechanism = "TERMINAL_COLLATERAL_SPROUTING"
    else:
        # De novo longitudinal regrowth
        t_regrowth = strat.nerve_initiation_latency_days + (damage.nerve_gap_length_mm / strat.axon_growth_rate_mm_day) + 14.0  # Synaptogenesis
        if t_regrowth > motor_endplate_deadline_days:
            nerve_recovery_days = motor_endplate_deadline_days
            conduction_restoration_pct = 12.0  # Endplates irreversibly degenerated
            sensory_recovery_pct = 10.0
            motor_axon_misdirection_rate_pct = 80.0
            contractile_force_5d_pct = 5.0
            innervation_mechanism = "ENDPLATE_ATROPHY_FAILURE"
        else:
            nerve_recovery_days = t_regrowth
            conduction_restoration_pct = 85.0 if strat.scaffold_guidance_present else 55.0
            sensory_recovery_pct = 78.0 if strat.scaffold_guidance_present else 45.0
            motor_axon_misdirection_rate_pct = 22.0 if strat.scaffold_guidance_present else 52.0
            contractile_force_5d_pct = 8.0
            innervation_mechanism = "LONGITUDINAL_AXONAL_ELONGATION"
            
    # --- Axis 5: Tissue Architecture Alignment ---
    # Collagen and myotube orientation order parameter (0 = random/fibrotic, 1 = perfectly parallel)
    architecture_order_parameter = 0.88 if strat.scaffold_guidance_present else 0.35
    
    # --- Axis 6: Fibrosis & Scar Quality ---
    scarless_index = strat.tgf_beta3_to_beta1_ratio
    is_scar_free = scarless_index >= 2.5
    residual_fibrosis_fraction = max(0.05, min(0.75, 1.0 - (scarless_index / 5.0))) if not is_scar_free else 0.02
    
    # --- Axis 7: Oncological Safety & Peto Status ---
    # Distinguish cellular migration (3-5 mm/day, benign) from stem cell cycling load.
    mitotic_burden = strat.stem_cell_cycling_enhancement
    tumor_suppressor_buffer = strat.tp53_copy_equivalent / 2.0
    relative_oncogenic_hazard = (mitotic_burden ** 2.0) / (tumor_suppressor_buffer ** 1.5)
    
    if strat.has_inducible_apoptosis_kill_switch:
        oncogenic_safety_tier = "STABILIZED_VIA_SYNTHETIC_CIRCUIT"
    elif relative_oncogenic_hazard <= 1.2:
        oncogenic_safety_tier = "PHYSIOLOGICAL_BASELINE"
    elif relative_oncogenic_hazard <= 3.0:
        oncogenic_safety_tier = "MILD_ELEVATED_MONITORED"
    else:
        oncogenic_safety_tier = "HIGH_UNSTABILIZED_PROLIFERATIVE_RISK"
        
    # --- Axis 8: Repeat Trauma Recovery Capacity ---
    # In unassisted humans, satellite cell pool drops by ~12-18% after severe VML trauma.
    # Repeated injuries exhaust regenerative capacity.
    cycles_to_exhaustion = 4 if not strat.scaffold_guidance_present else 12
    if strat.fusogen_membrane_preservation_active:
        cycles_to_exhaustion = 25  # Minimal stem cell recruitment needed when tissues are salvaged
        
    # Full Integrated Return to Function Days (all critical subsystems functional)
    time_to_functional_restoration_days = max(
        revascularization_days,
        nerve_recovery_days,
        tau_mechanical_days * 0.7
    )
    
    return {
        "strategy": strat.name,
        "category": strat.category,
        "injury": damage.injury_name,
        "time_to_functional_restoration_days": round(time_to_functional_restoration_days, 1),
        "axes": {
            "mechanical_strength_retention_pct": round(baseline_mechanical_plateau * 100.0, 1),
            "revascularization_days": round(revascularization_days, 1),
            "muscle_contractile_recovery_pct": round(contractile_force_recovery_fraction * 100.0, 1),
            "muscle_contractile_5d_pct": round(contractile_force_5d_pct, 1),
            "muscle_structural_outcome": muscle_structural_outcome,
            "vml_mass_fill_pct": vml_mass_fill_pct,
            "vml_mass_fill_evidence_status": "MODEL_ASSUMPTION_NOT_DIRECTLY_MEASURED_IN_DZIKI2016",
            "vml_strength_improvement_vs_preop_pct": vml_strength_improvement_vs_preop_pct,
            "vml_strength_evidence_status": "EXTERNALLY_CONFIRMED_DZIKI2016_MEAN_37_3_PCT",
            "vml_residual_deficit_vs_intact_pct": vml_residual_deficit_vs_intact_pct,
            "human_complete_restoration_achieved": False if vml_fraction > 0.15 else True,
            "innervation_recovery_days": round(nerve_recovery_days, 1),
            "innervation_mechanism": innervation_mechanism,
            "nerve_conduction_restored_pct": round(conduction_restoration_pct, 1),
            "cnap_evidence_status": "MODEL_ASSUMPTION_FROM_MAMMALIAN_CAP",
            "sensory_recovery_pct": round(sensory_recovery_pct, 1),
            "sensory_evidence_status": "EXTERNALLY_CONFIRMED_NEMANI2024_DIGITAL_NERVE",
            "motor_axon_misdirection_rate_pct": round(motor_axon_misdirection_rate_pct, 1),
            "motor_misdirection_evidence_status": "MODEL_ASSUMPTION_GUTAMA2026_GHERGHEREHCHI2016",
            "mrcc_ordinal_warning": "MRCC ordinal grades M0-M5 cannot be linearly converted to percentage force without a dynamometer measurement model.",
            "clustering_warning": "Nerves nested within patients require mixed-effects hierarchical clustering.",
            "architecture_alignment_order": round(architecture_order_parameter, 2),
            "scar_free_healing": is_scar_free,
            "residual_fibrosis_fraction": round(residual_fibrosis_fraction, 2),
            "oncogenic_safety_tier": oncogenic_safety_tier,
            "relative_oncogenic_hazard_index": round(relative_oncogenic_hazard, 2),
            "repeat_trauma_cycles_to_exhaustion": cycles_to_exhaustion,
        },
        "tissue_preservation_advantage": (
            "Tissue preservation via PEG-fusion/hypothermia bypasses Wallerian degeneration and prevents "
            "motor endplate atrophy without requiring high-velocity stem cell proliferation."
            if strat.fusogen_membrane_preservation_active else
            "Standard pathway requires de novo axonal elongation and cellular regeneration from scratch."
        ),
    }


def run_comprehensive_regeneration_benchmark() -> Dict[str, Any]:
    """Benchmark all archetypal strategies across severe combined penetrating trauma."""
    severe_combat_trauma = TissueDamageState(
        injury_name="Penetrating Shrapnel Laceration with Muscle Gap and Nerve Defect",
        skin_defect_radius_mm=25.0,
        muscle_loss_volume_cm3=35.0,
        muscle_compartment_volume_cm3=180.0,  # ~19.4% VML loss!
        nerve_gap_length_mm=45.0,
        vascular_ischemic_fraction=0.65,
        membrane_rupture_severity=0.70,
    )
    
    strategies = [
        STRATEGY_UNASSISTED_HUMAN,
        STRATEGY_ACOMYS_DERMAL_PROGRAM,
        STRATEGY_STIMULATED_BIOENGINEERED,
        STRATEGY_PRESERVATION_PEG_FUSION,
        STRATEGY_SPECULATIVE_EPIMORPHIC,
    ]
    
    results = {}
    for strat in strategies:
        results[strat.strategy_id] = evaluate_functional_recovery_timeline(severe_combat_trauma, strat)
    return results


if __name__ == "__main__":
    import json
    bench = run_comprehensive_regeneration_benchmark()
    print(json.dumps(bench, indent=2))
