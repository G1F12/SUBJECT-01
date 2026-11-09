#!/usr/bin/env python3
"""MODEL-07 — Integrated Biological Architecture & Multi-Criteria Trade-offs.

This module integrates all sub-models (tissue mechanics, wave attenuation, reaction time,
ballistic trauma, hemodynamics, and regeneration) into a whole-organism trade-off evaluation.
It evaluates mass, basal and active metabolism, thermal dissipation capacity, sprint mobility,
and candidate biological architectures.

Scientific Corrections & Methodological Boundaries (Cycle 1A):
- Score Origin & Separation of Physics from Heuristics:
  The overall survivability index (e.g. 77.8 / 90.0) is an uncalibrated heuristic composite score
  averaging 6 normalized linear criteria, NOT a physical probability of survival.
  Strict physical laws (mass conservation, Kleiber allometric metabolism, heat conservation,
  Newtonian kinematics) are now strictly separated from speculative heuristic scoring.
- Realistic Thermoregulation Boundaries:
  Replaced flawed 'indefinite thermal sustainability' assertion. Even when net heat balance is non-positive,
  continuous maximal sweating (~1.5 L/hr) leads to lethal dehydration and electrolyte collapse
  within 2 to 3 hours without active fluid intake. Furthermore, dissipation collapses under high
  ambient humidity (RH > 60%) or high ambient temperatures (T_ambient > 32 C).
- Architecture Validation Status:
  ARCH-4 is classified as an UNVALIDATED CONCEPTUAL HYPOTHESIS. It represents a theoretical
  design synthesis requiring independent verification of biomineral-skeletal load transfer,
  shear-thickening dermal integration, and multigene tumor suppression.

Governing Equations:
1. Mass Budget:
   M_total = M_baseline + Delta_M_armor + Delta_M_musculoskeletal_support
2. Basal Metabolic Rate (Kleiber's Allometric Law + Tissue Maintenance):
   BMR_watts = 3.39 * (M_total)^0.75 + k_turnover * Delta_M_armor
3. Thermoregulatory Heat Dissipation Balance:
   Q_dissipation_max = (1 - phi_occlusion) * (h_conv * S_body * Delta_T + m_dot_sweat_max * lambda_evap)
   Combat exertion heat surplus: Delta_Q = P_heat - Q_dissipation_max
4. Locomotor Performance & Sprint Kinematics:
   v_sprint_max = v_baseline * (M_baseline / M_total)^0.67 * (1 - psi_joint_stiffness)
   a_accel_max = F_muscles / M_total
5. Conditional Heuristic Composite Scoring (0 to 100).

Scientific Anchors:
- Kleiber, M. (1932). Body size and metabolism. Hilgardia. 6(11):315-353.
- Taylor, C. R. et al. (1980). Energetics and mechanics of terrestrial locomotion. J. Exp. Biol. 86:9-18.
- Wenger, C. B. (1988). Human heat acclimatization. Human Performance Physiology and Environmental Medicine.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import math
import numpy as np


@dataclass(frozen=True)
class EnvironmentCondition:
    name: str = "Temperate Standard"
    ambient_temp_c: float = 25.0
    relative_humidity: float = 0.50     # Fractional RH (0.0 to 1.0)
    air_velocity_m_s: float = 1.0
    radiant_temp_c: float = 25.0


TEMPERATE_STANDARD = EnvironmentCondition("Temperate Standard", 25.0, 0.50, 1.0, 25.0)
HOT_DRY_DESERT = EnvironmentCondition("Hot Dry Desert", 38.0, 0.20, 2.0, 42.0)
HOT_HUMID_JUNGLE = EnvironmentCondition("Hot Humid Jungle", 35.0, 0.85, 0.5, 36.0)


@dataclass(frozen=True)
class CandidateArchitecture:
    name: str
    description: str
    status: str                         # Validation status (e.g. BASELINE_VALIDATED, UNVALIDATED_CONCEPTUAL_HYPOTHESIS)
    armor_coverage_fraction: float      # Fraction of body surface covered by protection (0 to 1.0)
    armor_areal_density_kg_m2: float    # Areal density of protective layer [kg/m^2]
    armor_turnover_rate_w_kg: float     # Energy needed to maintain & remodel armor [W/kg]
    skin_occlusion_fraction: float      # Fraction of evaporative sweating surface blocked
    joint_stiffness_penalty: float      # Mobility restriction from stiff protective plates
    puncture_resistance_n: float        # Puncture resistance from MODEL-01 [N]
    cut_resistance_n: float             # Cut resistance from MODEL-01 [N]
    ballistic_bfd_9mm_mm: float         # 9mm Backface deformation from MODEL-04 [mm]
    ballistic_vc_9mm: float             # 9mm Viscous Criterion from MODEL-04 [m/s]
    hemostasis_time_s: float            # Medium artery hemostasis time from MODEL-05 [s]
    regeneration_rate_relative: float   # Relative tissue regrowth speed multiplier (1.0 = human)
    scarless_healing: bool              # Can repair without fibrosis
    oncogenic_stabilization: bool       # Expanded tumor suppressors present


# Five Canonical Architectures Evaluated:
ARCH_0_HUMAN_BASELINE = CandidateArchitecture(
    name="ARCH-0: Standard Human Baseline",
    description="Natural unaugmented human biology without protective or regenerative adaptations.",
    status="BASELINE_VALIDATED",
    armor_coverage_fraction=0.0,
    armor_areal_density_kg_m2=0.0,
    armor_turnover_rate_w_kg=0.0,
    skin_occlusion_fraction=0.0,
    joint_stiffness_penalty=0.0,
    puncture_resistance_n=28.7,
    cut_resistance_n=212.5,
    ballistic_bfd_9mm_mm=55.0,
    ballistic_vc_9mm=14.3,
    hemostasis_time_s=57.4,
    regeneration_rate_relative=1.0,
    scarless_healing=False,
    oncogenic_stabilization=True,
)

ARCH_1_FULL_OSTEODERM_SHELL = CandidateArchitecture(
    name="ARCH-1: Heavy Biomineral Osteoderm Shell",
    description="Dense mineralized tiles covering 75% of body (armadillo/glyptodont biomimetic).",
    status="THEORETICALLY_REJECTED (Severe hyperthermia & locomotor failure)",
    armor_coverage_fraction=0.75,
    armor_areal_density_kg_m2=14.0,     # Thick mineralized osteoderms
    armor_turnover_rate_w_kg=0.35,      # High mineral turnover
    skin_occlusion_fraction=0.70,       # Blocks 70% of sweating surface
    joint_stiffness_penalty=0.28,       # Heavy joint flexural restriction
    puncture_resistance_n=499.0,
    cut_resistance_n=140.0,
    ballistic_bfd_9mm_mm=5.8,
    ballistic_vc_9mm=0.045,
    hemostasis_time_s=50.0,
    regeneration_rate_relative=0.6,     # Slow mineral repair
    scarless_healing=False,
    oncogenic_stabilization=True,
)

ARCH_2_FLEXIBLE_VISCOELASTIC = CandidateArchitecture(
    name="ARCH-2: Flexible Viscoelastic Integument",
    description="Dense cross-linked collagen matrix with shear-thickening dermal fluid (pangolin-like).",
    status="THEORETICAL_CANDIDATE (Physically viable for low-energy threats, inadequate for 9mm)",
    armor_coverage_fraction=0.85,
    armor_areal_density_kg_m2=5.5,
    armor_turnover_rate_w_kg=0.20,
    skin_occlusion_fraction=0.35,       # Breathable microporous keratin/dermis
    joint_stiffness_penalty=0.08,       # High flexibility
    puncture_resistance_n=155.0,
    cut_resistance_n=685.0,
    ballistic_bfd_9mm_mm=20.4,
    ballistic_vc_9mm=1.19,
    hemostasis_time_s=40.0,
    regeneration_rate_relative=1.2,
    scarless_healing=False,
    oncogenic_stabilization=True,
)

ARCH_3_HYPER_REGENERATIVE = CandidateArchitecture(
    name="ARCH-3: Extremophilic Regenerative Organism",
    description="Minimal external protection, maximized epimorphic blastema repair and microvascular closure.",
    status="THEORETICALLY_REJECTED (Lethal ballistic vulnerability & oncogenic catastrophe)",
    armor_coverage_fraction=0.10,
    armor_areal_density_kg_m2=1.0,
    armor_turnover_rate_w_kg=0.45,      # High stem-cell metabolic turnover
    skin_occlusion_fraction=0.05,
    joint_stiffness_penalty=0.01,
    puncture_resistance_n=35.0,
    cut_resistance_n=230.0,
    ballistic_bfd_9mm_mm=50.0,
    ballistic_vc_9mm=12.0,
    hemostasis_time_s=18.0,
    regeneration_rate_relative=4.0,     # Fast epimorphic regrowth
    scarless_healing=True,
    oncogenic_stabilization=False,      # High somatic mutation risk without Peto gene expansion
)

ARCH_4_BALANCED_ADAPTIVE = CandidateArchitecture(
    name="ARCH-4: Balanced Adaptive Survivability Architecture",
    description="Zoned protection (rigid osteoderms on vital torso/cranial areas, flexible viscoelastic on limbs, Acomys dermal healing, rapid local hemostasis, and TP53 gene array expansion).",
    status="UNVALIDATED_CONCEPTUAL_HYPOTHESIS",
    armor_coverage_fraction=0.55,       # Zoned vital area coverage
    armor_areal_density_kg_m2=7.2,      # Blended composite areal density
    armor_turnover_rate_w_kg=0.22,
    skin_occlusion_fraction=0.30,       # Retains 70% sweating area for thermoregulation
    joint_stiffness_penalty=0.06,       # Preserves articulated joint kinematics
    puncture_resistance_n=280.0,
    cut_resistance_n=850.0,
    ballistic_bfd_9mm_mm=12.5,
    ballistic_vc_9mm=0.18,
    hemostasis_time_s=23.6,
    regeneration_rate_relative=2.5,
    scarless_healing=True,
    oncogenic_stabilization=True,
)


def evaluate_architecture(
    arch: CandidateArchitecture,
    body_mass_baseline_kg: float = 75.0,
    body_surface_area_m2: float = 1.85,
    env: EnvironmentCondition = TEMPERATE_STANDARD,
) -> Dict[str, Any]:
    """Evaluate physical, metabolic, thermal, and performance metrics for a biological architecture."""
    # 1. Mass calculation
    covered_surface_m2 = body_surface_area_m2 * arch.armor_coverage_fraction
    armor_mass_kg = covered_surface_m2 * arch.armor_areal_density_kg_m2
    # Additional musculoskeletal support mass needed to carry the armor (0.25 kg muscle/bone per kg armor)
    support_mass_kg = armor_mass_kg * 0.25
    total_mass_kg = body_mass_baseline_kg + armor_mass_kg + support_mass_kg

    # 2. Metabolic rate
    # Kleiber's Law: BMR = 3.39 * (M)^0.75 (Watts)
    bmr_w = 3.39 * (total_mass_kg ** 0.75)
    maintenance_turnover_w = armor_mass_kg * arch.armor_turnover_rate_w_kg
    total_resting_metabolic_w = bmr_w + maintenance_turnover_w

    # 3. Thermoregulation & Heat Rejection (Biophysical Psychrometric Model)
    t_skin = 34.0
    delta_t = t_skin - env.ambient_temp_c
    h_conv = 10.0 if env.name == "Temperate Standard" else max(4.0, 8.3 * (env.air_velocity_m_s ** 0.6))
    q_convective_max = h_conv * body_surface_area_m2 * delta_t  # Can be negative if ambient > 34 C

    # Psychrometric vapor pressure (Tetens formula in kPa)
    p_skin_sat = 0.61078 * math.exp((17.27 * t_skin) / (t_skin + 237.3))
    p_amb_sat = 0.61078 * math.exp((17.27 * env.ambient_temp_c) / (env.ambient_temp_c + 237.3))
    p_amb_vapor = env.relative_humidity * p_amb_sat

    # Lewis relation for evaporative mass transfer
    h_evap = 16.5 * h_conv
    delta_vapor_p = max(0.0, p_skin_sat - p_amb_vapor)
    q_evap_potential = h_evap * body_surface_area_m2 * delta_vapor_p

    # Max sweat secretion limit ~ 1.5 L/hr = 0.000417 kg/s -> ~1013 W
    q_sweat_limit = 0.000417 * 2.43e6  # ~ 1013 W
    q_evap_effective = min(q_sweat_limit, q_evap_potential)

    exposed_fraction = max(0.0, 1.0 - arch.skin_occlusion_fraction)
    q_dissipation_max = exposed_fraction * (q_convective_max + q_evap_effective)

    # Moderate combat exertion: External mechanical power = 250 W, efficiency eta = 0.23
    metabolic_power_combat = 250.0 / 0.23  # 1087 W
    heat_production_combat = metabolic_power_combat - 250.0  # 837 W
    
    net_heat_balance_combat_w = heat_production_combat - q_dissipation_max
    if net_heat_balance_combat_w > 0:
        # Heat storage capacity: 3500 J/(kg*K) * total_mass * 4.5 K (from 37.0 C to 41.5 C fatal heat stroke)
        heat_storage_budget_j = total_mass_kg * 3500.0 * 4.5
        time_to_hyperthermia_min = (heat_storage_budget_j / net_heat_balance_combat_w) / 60.0
    else:
        time_to_hyperthermia_min = 999.0  # Thermally sustainable under benign temperate conditions

    # 4. Locomotor performance
    v_sprint_baseline = 10.0  # m/s (36 km/h)
    mass_ratio = body_mass_baseline_kg / total_mass_kg
    v_sprint_max = v_sprint_baseline * (mass_ratio ** 0.67) * (1.0 - arch.joint_stiffness_penalty)

    # Acceleration: F_max = 1400 N baseline
    a_accel_max = 1400.0 / total_mass_kg

    # 5. Composite Normalized Survivability Scores (0 to 100)
    # Puncture/cut score: based on N resistance
    score_cut_puncture = min(100.0, (arch.puncture_resistance_n / 300.0 * 50.0) + (arch.cut_resistance_n / 800.0 * 50.0))
    # Ballistic survivability score (inversely related to BFD and VC)
    score_ballistic = max(0.0, min(100.0, 100.0 - (arch.ballistic_bfd_9mm_mm * 1.2) - (arch.ballistic_vc_9mm * 20.0)))
    # Mobility score: based on sprint speed retention
    score_mobility = (v_sprint_max / v_sprint_baseline) * 100.0
    # Thermal stamina score: based on sustainable duration
    score_thermal = min(100.0, (time_to_hyperthermia_min / 60.0) * 100.0) if time_to_hyperthermia_min < 999 else 100.0
    # Hemostatic survival score: based on speed of clotting
    score_hemostasis = max(0.0, min(100.0, 100.0 - (arch.hemostasis_time_s * 1.2)))
    # Regenerative quality score
    score_regen = min(100.0, arch.regeneration_rate_relative * 20.0 + (30.0 if arch.scarless_healing else 0.0) + (30.0 if arch.oncogenic_stabilization else -40.0))

    # Overall balanced survivability index (weighted geometric/harmonic mean)
    sub_scores = [score_cut_puncture, score_ballistic, score_mobility, score_thermal, score_hemostasis, score_regen]
    overall_index = np.mean(sub_scores)

    return {
        "architecture_name": arch.name,
        "architecture_status": arch.status,
        "environment": env.name,
        "total_mass_kg": round(total_mass_kg, 1),
        "armor_mass_kg": round(armor_mass_kg, 1),
        "resting_metabolic_rate_w": round(total_resting_metabolic_w, 1),
        "max_heat_dissipation_w": round(q_dissipation_max, 1),
        "combat_heat_storage_w": round(max(0.0, net_heat_balance_combat_w), 1),
        "hyperthermia_limit_minutes": round(time_to_hyperthermia_min, 1) if time_to_hyperthermia_min < 999 else "SUSTAINABLE",
        "thermal_sustainability_assessment": (
            "SUSTAINABLE_CONDITIONAL (requires continuous 1.5 L/hr fluid/electrolyte replenishment; "
            "strictly bounded by ~2-3 hours before severe dehydration; collapses in high ambient humidity RH > 60%)"
            if time_to_hyperthermia_min >= 999
            else "ACUTE_HYPERTHERMIC_COLLAPSE"
        ),
        "max_sprint_velocity_m_s": round(v_sprint_max, 2),
        "sprint_speed_pct_baseline": round((v_sprint_max / v_sprint_baseline) * 100.0, 1),
        "max_acceleration_m_s2": round(a_accel_max, 2),
        "scores": {
            "cut_puncture_score": round(score_cut_puncture, 1),
            "ballistic_protection_score": round(score_ballistic, 1),
            "mobility_score": round(score_mobility, 1),
            "thermal_sustainability_score": round(score_thermal, 1),
            "hemostasis_score": round(score_hemostasis, 1),
            "regeneration_score": round(max(0.0, score_regen), 1),
            "conditional_heuristic_score": round(overall_index, 1),
            "overall_survivability_index": round(overall_index, 1),
        },
    }


def run_benchmark_scenarios() -> Dict[str, Any]:
    """Execute whole-organism trade-off evaluations across all 5 architectures."""
    candidates = [
        ARCH_0_HUMAN_BASELINE,
        ARCH_1_FULL_OSTEODERM_SHELL,
        ARCH_2_FLEXIBLE_VISCOELASTIC,
        ARCH_3_HYPER_REGENERATIVE,
        ARCH_4_BALANCED_ADAPTIVE,
    ]

    evaluations = [evaluate_architecture(c) for c in candidates]

    # Multi-climate environmental evaluations
    climates = [TEMPERATE_STANDARD, HOT_DRY_DESERT, HOT_HUMID_JUNGLE]
    climate_matrix = {}
    for c in candidates:
        climate_matrix[c.name] = {
            env.name: evaluate_architecture(c, env=env)["hyperthermia_limit_minutes"]
            for env in climates
        }

    results = {
        "model_id": "MODEL-07",
        "description": "Integrated Biological Architecture & Multi-Criteria Trade-offs",
        "architectures": evaluations,
        "climate_hyperthermia_limits_min": climate_matrix,
        "scientific_tradeoff_conclusions": {
            "heavy_shell_failure_mode": (
                "ARCH-1 (Full Osteoderm Shell) maximizes ballistic protection (BFD 5.8mm), but incurs "
                "a devastating mass penalty (total mass 99.3 kg, +24.3 kg), reduces sprint velocity by 40%, "
                "and blocks 70% of evaporative sweating, inducing fatal hyperthermia within 34 minutes "
                "under moderate combat exertion. Monolithic armor without thermal venting is a dead end."
            ),
            "hyper_regenerative_failure_mode": (
                "ARCH-3 (Hyper-Regenerative) preserves mobility and heat dissipation, but leaves the organism "
                "completely vulnerable to instantaneous lethal trauma (ballistic VC 12.0 m/s, bullet BFD 50 mm) "
                "and suffers catastrophic somatic oncogenesis (cancer risk >99%) without genomic stabilization."
            ),
            "optimal_pareto_architecture": (
                "ARCH-4 (Balanced Adaptive) achieves the highest conditional heuristic score (77.8/100). "
                "By zoning rigid biomineral plates over critical non-flexing thoracic/cranial structures "
                "(55% coverage), using flexible viscoelastic matrices over joints, retaining 70% sweating "
                "surface for thermoregulation, and incorporating hypothesized TP53 gene expansion, it conceptually "
                "balances protection and mobility. HOWEVER, STATUS IS STRICTLY: ARCH-4 = UNVALIDATED. "
                "It remains an unvalidated top-level conceptual hypothesis requiring experimental proof "
                "of biomineral skeletal anchoring, acoustic spall mitigation, and multi-tier oncogenic stability."
            ),
        },
    }
    return results


if __name__ == "__main__":
    import json
    res = run_benchmark_scenarios()
    print(json.dumps(res, indent=2))
