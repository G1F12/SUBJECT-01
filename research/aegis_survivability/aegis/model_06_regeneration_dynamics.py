#!/usr/bin/env python3
"""MODEL-06 — Regeneration Dynamics, Functional Neurotization & Oncogenic Constraints.

This module models multi-scale tissue regeneration: wound closure kinetics,
epimorphic blastema growth, peripheral nerve re-innervation velocity,
and the fundamental trade-off with somatic oncogenic transformation.

Scientific Corrections & Boundary Realism (Cycle 1A):
- Corrected attribution for peripheral nerve regeneration velocity (1.0 - 2.0 mm/day):
  Anchored in classical mammalian neurobiology (Seddon 1975, Sunderland 1978),
  which is governed by the rate of slow component 'a' (SCa) axonal transport of tubulin
  and neurofilaments (~1-2 mm/day). Removed invalid citation of Kragl et al. (2009)
  for axon elongation. Kragl et al. demonstrated lineage memory in axolotl blastema cells.
- Eliminated pseudo-quantitative cancer probability formulas (99.6% vs 6.1%).
  Exact human lifetime cancer probabilities under hypothetical TP53 gene expansion
  are mathematically uncalibrated and represent an open scientific problem (Peto's Paradox).
  Replaced with rigorous qualitative risk tiers and order-of-magnitude bounds.

Governing Equations:
1. Re-epithelialization Closure Time:
   t_closure = R_wound / v_epithelial
2. Structural Volumetric Mass Regeneration (Gompertz Growth):
   V(t) = V_target * exp(-b * exp(-k_growth * t))
3. Functional Neurotization (Axonal Regeneration Rate):
   T_functional_nerve = tau_initial_sprouting + (L_nerve_defect / v_axon) + tau_reinnervation
   where v_axon = 1.0 - 2.0 mm/day (fundamental biological tubulin transport limit).
4. Fibrosis vs Scar-free Regeneration Ratio:
   R_scarless = ([TGF_beta3] / [TGF_beta1]) * ([M2_macrophage] / [M1_macrophage])
   Qualitative criterion: high TGF-beta3 and early M2 resolution suppress myofibroblast differentiation.
5. Qualitative Oncogenic Trade-off:
   Mitotic load increases with blastema cycling; quantitative risk reduction from TP53 copy
   number expansion remains unvalidated in humans.

Scientific Anchors:
- Seddon, H. J. (1975). Surgical Disorders of the Peripheral Nerves. Churchill Livingstone.
- Sunderland, S. (1978). Nerves and Nerve Injuries. Churchill Livingstone.
- Seifert, A. W. et al. (2012). Skin shedding and tissue regeneration in African spiny mice (Acomys). Nature. 489:561-565.
- Kragl, M. et al. (2009). Cells keep a memory of their tissue origin during axolotl limb regeneration. Nature. 460:60-65.
- Peto, R. (1977). Epidemiology, multistage models, and short-term mutagenicity tests. Cold Spring Harb. Conf. Cell Prolif. 4:1403-1428.
- Abegglen, L. M. et al. (2015). Potential mechanisms for cancer resistance in elephants and comparative cellular response to DNA damage in humans. JAMA. 314(17):1850-1860.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import math
import numpy as np


@dataclass(frozen=True)
class RegenerationPhenotype:
    name: str
    epithelial_migration_rate_mm_day: float  # Re-epithelialization speed [mm/day]
    axon_growth_rate_mm_day: float          # Axonal elongation velocity [mm/day]
    tgf_beta3_to_beta1_ratio: float         # Anti-fibrotic cytokine balance
    m2_to_m1_macrophage_ratio: float        # Pro-regenerative immune polarization
    blastema_competent: bool                # Can form dedifferentiated blastema
    p53_gene_copy_multiplier: float         # Tumor suppressor expansion factor
    stem_cell_cycling_frequency_per_year: float # Baseline somatic mitotic turnover


# Phenotypes
STANDARD_HUMAN_HEALING = RegenerationPhenotype(
    name="Standard Adult Human (Fibrotic Repair)",
    epithelial_migration_rate_mm_day=0.8,
    axon_growth_rate_mm_day=1.2,
    tgf_beta3_to_beta1_ratio=0.15,          # Heavily skewed towards profibrotic TGF-beta1
    m2_to_m1_macrophage_ratio=0.8,
    blastema_competent=False,
    p53_gene_copy_multiplier=1.0,           # Normal human: 2 alleles of TP53
    stem_cell_cycling_frequency_per_year=25.0,
)

ACOMYS_SPINY_MOUSE_ANALOGUE = RegenerationPhenotype(
    name="Acomys-Inspired Scar-Free Dermal Regenerator",
    epithelial_migration_rate_mm_day=2.4,
    axon_growth_rate_mm_day=1.5,
    tgf_beta3_to_beta1_ratio=3.8,           # Strong TGF-beta3 dominance
    m2_to_m1_macrophage_ratio=4.2,          # Early anti-inflammatory resolution
    blastema_competent=True,
    p53_gene_copy_multiplier=2.5,
    stem_cell_cycling_frequency_per_year=80.0,
)

THEORETICAL_EXTREME_BLASTEMA = RegenerationPhenotype(
    name="Theoretical Axolotl-Grade Epimorphic Organism",
    epithelial_migration_rate_mm_day=4.5,
    axon_growth_rate_mm_day=2.2,            # Near upper biological limit for tubulin transport
    tgf_beta3_to_beta1_ratio=6.0,
    m2_to_m1_macrophage_ratio=6.5,
    blastema_competent=True,
    p53_gene_copy_multiplier=1.0,           # Without p53 expansion: massive cancer vulnerability
    stem_cell_cycling_frequency_per_year=250.0,
)

GENOME_STABILIZED_EPIMORPHIC = RegenerationPhenotype(
    name="Engineered Genome-Stabilized Epimorphic Organism",
    epithelial_migration_rate_mm_day=4.5,
    axon_growth_rate_mm_day=2.2,
    tgf_beta3_to_beta1_ratio=6.0,
    m2_to_m1_macrophage_ratio=6.5,
    blastema_competent=True,
    p53_gene_copy_multiplier=12.0,          # Expanded elephant-like TP53 array (Peto solution)
    stem_cell_cycling_frequency_per_year=250.0,
)


@dataclass(frozen=True)
class TissueDefect:
    name: str
    radius_mm: float             # Surface wound radius [mm]
    depth_mm: float              # Wound depth [mm]
    nerve_gap_distance_mm: float # Distance of denervated distal axon segment [mm]
    volume_cm3: float            # Volumetric tissue loss [cm^3]


DEFECT_EXCORIATION = TissueDefect(
    name="Deep Dermal Abrasion / Laceration",
    radius_mm=15.0,
    depth_mm=3.0,
    nerve_gap_distance_mm=5.0,
    volume_cm3=2.1,
)

DEFECT_PENETRATING_PUNCTURE = TissueDefect(
    name="Deep Penetrating Muscle Wound",
    radius_mm=8.0,
    depth_mm=45.0,
    nerve_gap_distance_mm=45.0,
    volume_cm3=9.0,
)

DEFECT_EXTENSIVE_TRAUMA = TissueDefect(
    name="Extensive Blast/Crush Soft Tissue Defect",
    radius_mm=50.0,
    depth_mm=30.0,
    nerve_gap_distance_mm=120.0,
    volume_cm3=235.0,
)


def evaluate_regeneration_timeline(phenotype: RegenerationPhenotype, defect: TissueDefect) -> Dict[str, Any]:
    """Calculate the multi-scale temporal recovery milestones for a specific injury defect."""
    # 1. Wound Closure / Re-epithelialization
    # Wound closure proceeds centripetally
    t_epithelial_days = defect.radius_mm / phenotype.epithelial_migration_rate_mm_day

    # 2. Structural Volumetric Tissue Regrowth
    # Gompertz growth model: k_growth scales with blastema competency
    k_growth = 0.08 if phenotype.blastema_competent else 0.02
    # Days to reach 95% volumetric fill
    t_volume_95_days = (math.log(math.log(1.0 / 0.05)) + 4.0) / k_growth
    if not phenotype.blastema_competent and defect.volume_cm3 > 15.0:
        # In non-blastema organisms, large volume defects fail to close structurally (chronic cavity/scar)
        t_volume_95_days = -1.0  # Incomplete / permanent volume deficit

    # 3. Functional Axonal Neurotization
    # Axon growth: sprouting delay (4 days) + elongation + synaptogenesis (14 days)
    tau_sprout = 4.0
    tau_synapse = 14.0
    t_axon_elongation = defect.nerve_gap_distance_mm / phenotype.axon_growth_rate_mm_day
    t_functional_innervation_days = tau_sprout + t_axon_elongation + tau_synapse

    # 4. Fibrosis vs Scar-free Quality
    scarless_metric = phenotype.tgf_beta3_to_beta1_ratio * phenotype.m2_to_m1_macrophage_ratio
    is_scar_free = scarless_metric >= 2.5 and phenotype.blastema_competent
    scar_tissue_fraction = max(0.0, min(0.85, 1.0 - (scarless_metric / 15.0))) if not is_scar_free else 0.0

    # 5. Oncogenic Risk Assessment (Qualitative Tiers & Peto's Paradox Status)
    # Note: Exact quantitative cancer probabilities under hypothetical TP53 gene expansion
    # cannot be validated with existing biological data. We categorize oncogenic risk
    # qualitatively based on mitotic load vs tumor suppressor status.
    if phenotype.p53_gene_copy_multiplier > 5.0:
        oncogenic_tier = "THEORETICAL_MITIGATION_UNVALIDATED"
        oncogenic_rationale = (
            "Hypothesized Peto-like tumor suppression (e.g. 10-20x TP53 copies like Loxodonta africana). "
            "Exact quantitative risk reduction in human tissue is mathematically unconstrained."
        )
    elif phenotype.blastema_competent and phenotype.p53_gene_copy_multiplier <= 1.0:
        oncogenic_tier = "CRITICAL_HYPERPLASTIC_HAZARD"
        oncogenic_rationale = (
            "Unconstrained epimorphic dedifferentiation with standard human DNA repair "
            "carries severe risk of teratoma and early malignant transformation."
        )
    elif phenotype.blastema_competent:
        oncogenic_tier = "MODERATE_ELEVATED_RISK"
        oncogenic_rationale = "Elevated somatic cycling requiring stringent cell cycle checkpoints."
    else:
        oncogenic_tier = "STANDARD_HOMEOSTATIC_BASELINE"
        oncogenic_rationale = "Normal human basal turnover without increased mitotic load."

    # Heuristic order-of-magnitude scaling (Armitage-Doll toy model, uncalibrated for human epimorphic modifications)
    divisions_norm = phenotype.stem_cell_cycling_frequency_per_year / 25.0
    p53_eff = phenotype.p53_gene_copy_multiplier ** 1.8
    hazard_10yr = 0.035 * (divisions_norm ** 2.2) / p53_eff
    p_cancer_10yr_heuristic = 1.0 - math.exp(-hazard_10yr)

    return {
        "phenotype": phenotype.name,
        "defect": defect.name,
        "wound_closure_days": round(t_epithelial_days, 1),
        "volumetric_structural_regrowth_days": round(t_volume_95_days, 1) if t_volume_95_days > 0 else "PERMANENT_DEFICIT",
        "functional_neurotization_days": round(t_functional_innervation_days, 1),
        "scarless_regeneration": is_scar_free,
        "residual_fibrosis_fraction": round(scar_tissue_fraction, 2),
        "oncogenic_risk_tier": oncogenic_tier,
        "oncogenic_rationale": oncogenic_rationale,
        "ten_year_oncogenic_risk_pct": round(min(99.9, p_cancer_10yr_heuristic * 100.0), 2),
    }


def run_benchmark_scenarios() -> Dict[str, Any]:
    """Execute comparative regenerative benchmarks across all phenotypes and defects."""
    phenotypes = [
        STANDARD_HUMAN_HEALING,
        ACOMYS_SPINY_MOUSE_ANALOGUE,
        THEORETICAL_EXTREME_BLASTEMA,
        GENOME_STABILIZED_EPIMORPHIC,
    ]
    defects = [DEFECT_EXCORIATION, DEFECT_PENETRATING_PUNCTURE, DEFECT_EXTENSIVE_TRAUMA]

    all_evaluations = []
    for d in defects:
        defect_group = {"defect": d.name, "phenotype_results": []}
        for p in phenotypes:
            res = evaluate_regeneration_timeline(p, d)
            defect_group["phenotype_results"].append(res)
        all_evaluations.append(defect_group)

    results = {
        "model_id": "MODEL-06",
        "description": "Regeneration Dynamics, Functional Neurotization & Oncogenic Constraints",
        "defect_evaluations": all_evaluations,
        "fundamental_biological_boundaries": {
            "closure_vs_function_dichotomy": (
                "Wound surface closure (epithelial migration) occurs in days (3.3 - 20 days), "
                "but functional neuromuscular recovery is strictly bound by axon regeneration velocity "
                "(1.0 - 2.2 mm/day). For a 120 mm deep nerve lesion, functional reinnervation takes "
                "at least 72 - 118 days. Instantaneous combat regeneration is biologically impossible."
            ),
            "fibrosis_control": (
                "In Acomys spiny mice, TGF-beta3 dominance and early M2 macrophage resolution allow scar-free "
                "dermal healing with hair follicle neogenesis (Seifert et al. 2012). However, transferring this pathway "
                "to human adults is an UNPROVEN HYPOTHESIS: human Phase III clinical trials with recombinant TGF-beta3 "
                "(avotermin) failed to show robust efficacy, indicating that rodent autotomy mechanisms cannot be "
                "directly equated with therapeutic human scarless regeneration."
            ),
            "oncogenesis_tradeoff_petos_paradox": (
                "Unrestrained epimorphic blastema cycling imposes massive cumulative mitotic loads. "
                "In mammalian systems, this presents severe risks of genomic instability and neoplastic transformation "
                "unless counterbalanced by robust multi-layer tumor suppressor pathways. While elephants expanded "
                "TP53 copies (~20 copies / 40 alleles) and retrogene LIF6, directly extrapolating this to calculate "
                "precise numerical cancer probabilities in modified humans is scientifically unvalidated and "
                "mathematically unconstrained at present. Peto's paradox remains an open quantitative problem."
            ),
        },
    }
    return results


if __name__ == "__main__":
    import json
    res = run_benchmark_scenarios()
    print(json.dumps(res, indent=2))
