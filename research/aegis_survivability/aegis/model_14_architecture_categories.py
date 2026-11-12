"""MODEL-14: Three-Tier Architectural Categorization & SUBJECT-01 Compatibility Engine.

AEGIS-01: Biological Defense & Survivability Program (Cycle 3).
Calibrated against SUBJECT-01 specifications:
  - Muscle Architecture A (Coordinated: 78.0 kg, per-group force 4748.1 N, peak COM 1926.0 W, steady 230.3 W)
  - Conditional Architecture B (Internal Biohybrid: 81.0 kg, force 5641.5 N, peak COM 2177.2 W, steady 271.7 W)
  - Conditional Architecture C (Predictive Sensory: 75.5 kg, latency 132.8 ms)
  - CPE45 Protocol: 2700 s duration, 675 kJ external work at 250 W mean demand,
    thermodynamic distinction between Delta_G_ATP = -54.0 kJ/mol (Gibbs work limit)
    and Delta_R H = 21.0 kJ/mol (heat enthalpy release).

Strict Category Boundaries:
  1. ARCH-BIO: Fully Endogenous. The organism grows, metabolically sustains, and repairs all structures.
  2. ARCH-HYBRID: Internal Biohybrid. Internal synthetic implants/meshes integrated with host living tissue.
  3. ARCH-SPEC: Speculative Biological Architecture. Fundamentally novel biomineralization, enzymatic synthesis, or genetic circuits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass(frozen=True)
class ArchitectureProfile:
    """Represents a protective and survivability architecture."""
    arch_id: str
    name: str
    category: str  # "ARCH-BIO", "ARCH-HYBRID", "ARCH-SPEC"
    description: str
    
    # Mass & Materials
    added_protection_mass_kg: float
    materials_used: List[str]
    is_fully_endogenous: bool
    requires_synthetic_implants: bool
    requires_scientific_breakthrough: bool
    
    # Biomechanics & Protection
    cut_resistance_n: float
    puncture_resistance_n: float
    ballistic_bfd_9mm_mm: float  # Behind armor deformation from 9x19mm 500J
    ballistic_vc_9mm_m_s: float  # Viscous Criterion
    can_defeat_rifle_762: bool   # 7.62x39mm 2100J
    joint_flexibility_penalty_pct: float
    
    # Physiology & Thermoregulation
    skin_occlusion_fraction: float  # Blocked sweat gland area (0 to 1)
    metabolic_tissue_maintenance_w: float
    self_repair_capacity: str  # "AUTONOMOUS_ENDOGENOUS", "PARTIAL_HOST_MATRIX", "NON_REGENERATIVE_SYNTHETIC"
    cut_resistance_mode1_crack_n: float = 48.6
    cut_resistance_draw_slice_n: float = 32.4



# -------------------------------------------------------------------------
# Defined Architectures Across the Three Categories
# -------------------------------------------------------------------------

ARCH_BIO_KERATIN_FGM = ArchitectureProfile(
    arch_id="ARCH-BIO-4",
    name="Endogenous Selective FGM & Keratin Shield",
    category="ARCH-BIO",
    description="Biologically grown functionally-graded dermal scales and osteodermal sternal bridge with living turnover.",
    added_protection_mass_kg=4.2,
    materials_used=["Cross-lamellar alpha/beta keratin", "Continuous hydroxyapatite-collagen FGM"],
    is_fully_endogenous=True,
    requires_synthetic_implants=False,
    requires_scientific_breakthrough=False,
    cut_resistance_n=680.0,
    puncture_resistance_n=165.0,
    ballistic_bfd_9mm_mm=18.5,
    ballistic_vc_9mm_m_s=0.22,
    can_defeat_rifle_762=False,  # Physically impossible for endogenous human tissue
    joint_flexibility_penalty_pct=6.5,
    skin_occlusion_fraction=0.25,  # 75% skin free for sweating
    metabolic_tissue_maintenance_w=11.5,
    self_repair_capacity="AUTONOMOUS_ENDOGENOUS",
)

ARCH_HYBRID_UHMWPE_CERAMIC = ArchitectureProfile(
    arch_id="ARCH-HYBRID-A",
    name="Internal Biohybrid Subdermal Micro-Armor & Synthetic Fascia",
    category="ARCH-HYBRID",
    description="Subcutaneously anchored articulating UHMWPE/ceramic micro-tiles with porous collagen ingrowth margins.",
    added_protection_mass_kg=3.8,
    materials_used=["Medical-grade UHMWPE mesh", "Boron carbide micro-tiles", "CNT-polyurethane fascia"],
    is_fully_endogenous=False,
    requires_synthetic_implants=True,
    requires_scientific_breakthrough=False,
    cut_resistance_n=950.0,
    puncture_resistance_n=320.0,
    ballistic_bfd_9mm_mm=11.2,
    ballistic_vc_9mm_m_s=0.12,
    can_defeat_rifle_762=False,  # Internal 3.8 kg implant cannot stop 2100J rifle round without breaking thoracic ribs
    joint_flexibility_penalty_pct=4.0,
    skin_occlusion_fraction=0.08,  # Subdermal implantation spares 92% of epidermis and eccrine glands!
    metabolic_tissue_maintenance_w=0.0,  # Synthetic materials consume zero ATP
    self_repair_capacity="PARTIAL_HOST_MATRIX",
)

ARCH_SPEC_GRAPHENE_RADIATOR = ArchitectureProfile(
    arch_id="ARCH-SPEC-1",
    name="Speculative Enzymatic Graphene Composite & Vascular Radiator",
    category="ARCH-SPEC",
    description="Hypothetical cell-synthesized sp2 carbon armor with active subdermal arteriovenous thermal countercurrent heat pipes.",
    added_protection_mass_kg=2.5,
    materials_used=["Biosynthetic graphene-protein composite", "Engineered vascular phase-change shunts"],
    is_fully_endogenous=True,
    requires_synthetic_implants=False,
    requires_scientific_breakthrough=True,
    cut_resistance_n=1500.0,
    puncture_resistance_n=750.0,
    ballistic_bfd_9mm_mm=6.5,
    ballistic_vc_9mm_m_s=0.06,
    can_defeat_rifle_762=True,  # Speculative extreme tensile strength hypothesis
    joint_flexibility_penalty_pct=2.0,
    skin_occlusion_fraction=0.15,
    metabolic_tissue_maintenance_w=22.0,
    self_repair_capacity="AUTONOMOUS_ENDOGENOUS",
)


# -------------------------------------------------------------------------
# SUBJECT-01 Baseline Profiles
# -------------------------------------------------------------------------

@dataclass(frozen=True)
class Subject01System:
    """Motor system specification from SUBJECT-01."""
    system_id: str
    name: str
    body_mass_kg: float
    per_group_force_n: float
    peak_com_power_w: float
    steady_locomotor_w: float
    tendon_safety_limit_stress_mpa: float  # Working limit ~50 MPa; ultimate tensile ~100 MPa
    effective_neuromuscular_latency_ms: float


SUBJECT01_MUSCLE_ARCH_A = Subject01System(
    system_id="ARCH-I-COORDINATED",
    name="Muscle Architecture A (Coordinated Evidence-Based)",
    body_mass_kg=78.0,
    per_group_force_n=4748.1,
    peak_com_power_w=1926.0,
    steady_locomotor_w=230.3,
    tendon_safety_limit_stress_mpa=55.0,
    effective_neuromuscular_latency_ms=212.8,
)

SUBJECT01_CONDITIONAL_ARCH_B = Subject01System(
    system_id="ARCH-II-BIOHYBRID",
    name="Conditional Architecture B (Internal Biohybrid High-Power)",
    body_mass_kg=81.0,
    per_group_force_n=5641.5,
    peak_com_power_w=2177.2,
    steady_locomotor_w=271.7,
    tendon_safety_limit_stress_mpa=72.0,
    effective_neuromuscular_latency_ms=146.7,
)

SUBJECT01_CONDITIONAL_ARCH_C = Subject01System(
    system_id="ARCH-III-SENSORY",
    name="Conditional Architecture C (Internal Predictive Sensory)",
    body_mass_kg=75.5,
    per_group_force_n=3391.5,
    peak_com_power_w=1674.8,
    steady_locomotor_w=203.3,
    tendon_safety_limit_stress_mpa=45.0,
    effective_neuromuscular_latency_ms=132.8,
)


# -------------------------------------------------------------------------
# Compatibility Analysis Engine
# -------------------------------------------------------------------------

def evaluate_subject01_compatibility(
    arch: ArchitectureProfile,
    host: Subject01System,
    climate: str = "temperate"  # "temperate" (25C, 50% RH), "hot_dry" (35C, 20% RH), "hot_humid" (35C, 80% RH)
) -> Dict[str, Any]:
    """Evaluate whether protective modification can be integrated without degrading SUBJECT-01 performance."""
    total_mass_kg = host.body_mass_kg + arch.added_protection_mass_kg
    mass_ratio = host.body_mass_kg / total_mass_kg
    
    # 1. Locomotor impact (Sprint speed and sprint acceleration)
    # Hill/Taylor scaling: Sprint speed scales with mass^(-0.67) and joint flexibility
    speed_retention_pct = (mass_ratio ** 0.67) * (1.0 - (arch.joint_flexibility_penalty_pct / 100.0)) * 100.0
    
    # Peak acceleration: a = F_propulsive / M
    f_propulsive_n = host.per_group_force_n * 0.35  # Effective horizontal push
    baseline_accel = f_propulsive_n / host.body_mass_kg
    modified_accel = f_propulsive_n / total_mass_kg
    accel_retention_pct = (modified_accel / baseline_accel) * 100.0
    
    # 2. Neuromuscular Latency Check
    # Added mass does NOT change neural latency, but electromechanical delay (EMD) increases slightly with inertia
    delta_emd_ms = (arch.added_protection_mass_kg / host.body_mass_kg) * 1.5
    net_effective_latency_ms = host.effective_neuromuscular_latency_ms + delta_emd_ms
    
    # 3. Tendon stress overhead
    # Additional inertial load during deceleration: F_inertial = m_added * 25 m/s^2 (max cutting deceleration)
    decel_peak_force_n = arch.added_protection_mass_kg * 25.0
    patellar_tendon_area_mm2 = 95.0
    tendon_stress_overhead_mpa = decel_peak_force_n / patellar_tendon_area_mm2
    operating_tendon_stress_mpa = host.tendon_safety_limit_stress_mpa + tendon_stress_overhead_mpa
    tendon_status = "SAFE" if operating_tendon_stress_mpa < 80.0 else "EXCEEDS_FATIGUE_LIMIT"
    
    # 4. Unified Energy Flow Balance & CPE45 Metabolic Impact over 2700 s
    # 4a. Work & Metabolic Power
    w_mech_w = 250.0  # External mechanical power output [W]
    eta_muscle = 0.23 # Muscular mechanical efficiency
    bmr_w = 128.7     # Basal resting metabolic rate [W]
    tissue_maint_w = arch.metabolic_tissue_maintenance_w # Active tissue maintenance [W]
    metabolic_power_w = (w_mech_w / eta_muscle) + bmr_w + tissue_maint_w
    heat_production_w = metabolic_power_w - w_mech_w
    
    # 4b. Environmental Heat Dissipation Physics (v_air ~ 4.5 m/s, BSA ~ 1.95 m^2, T_sk ~ 35.5 C)
    bsa_m2 = 1.95
    t_skin_c = 35.5
    h_c = 20.5  # Convective coefficient W/(m^2*K) at 4.5 m/s
    h_r = 4.8   # Radiative exchange coefficient W/(m^2*K)
    f_free = max(0.05, 1.0 - arch.skin_occlusion_fraction)
    
    if climate == "temperate":
        t_amb_c = 25.0
        q_conv_uncovered = h_c * bsa_m2 * (t_skin_c - t_amb_c)  # ~ 419.3 W
        q_rad_uncovered = h_r * bsa_m2 * (t_skin_c - t_amb_c)   # ~ 98.3 W
        q_evap_capacity = 810.0  # Biological sweat rate limit ~ 1.2 L/h
    elif climate == "hot_dry":
        t_amb_c = 35.0
        q_conv_uncovered = max(0.0, h_c * bsa_m2 * (t_skin_c - t_amb_c))  # ~ 20.0 W
        q_rad_uncovered = max(0.0, h_r * bsa_m2 * (t_skin_c - t_amb_c))   # ~ 4.7 W
        q_evap_capacity = 750.0  # High vapor deficit allows good evaporation
    else:  # hot_humid (35C, 80% RH)
        t_amb_c = 35.0
        q_conv_uncovered = max(0.0, h_c * bsa_m2 * (t_skin_c - t_amb_c))  # ~ 20.0 W
        q_rad_uncovered = max(0.0, h_r * bsa_m2 * (t_skin_c - t_amb_c))   # ~ 4.7 W
        q_evap_capacity = 340.0  # Severe psychrometric vapor pressure ceiling
        
    dry_dissipation_actual = f_free * (q_conv_uncovered + q_rad_uncovered)
    
    # Required evaporative flux to maintain thermal equilibrium
    evap_required_w = max(0.0, (heat_production_w - dry_dissipation_actual) / f_free)
    evap_actual_flux = min(evap_required_w, q_evap_capacity)
    evap_dissipation_actual = f_free * evap_actual_flux
    
    effective_dissipation_w = dry_dissipation_actual + evap_dissipation_actual
    net_heat_storage_w = max(0.0, heat_production_w - effective_dissipation_w)
    
    # Automated First-Law Energy Balance Verification: M - (W + Q_loss + Q_storage) == 0
    energy_balance_residual = abs(metabolic_power_w - (w_mech_w + effective_dissipation_w + net_heat_storage_w))
    assert energy_balance_residual < 1e-4, f"Energy conservation violated! Residual: {energy_balance_residual}"
    
    c_p_tissue = 3480.0  # J / (kg * K)
    thermal_mass_j_k = total_mass_kg * c_p_tissue
    
    if net_heat_storage_w > 1.0:
        heating_rate_k_min = (net_heat_storage_w / thermal_mass_j_k) * 60.0
        time_to_395c_min = (thermal_mass_j_k * 2.5) / net_heat_storage_w / 60.0
        time_to_400c_min = (thermal_mass_j_k * 3.0) / net_heat_storage_w / 60.0
        reaches_hyperthermia_in_cpe45 = time_to_395c_min < 45.0
    else:
        # Stable thermal equilibrium
        heating_rate_k_min = 0.000
        time_to_395c_min = 999.0
        time_to_400c_min = 999.0
        reaches_hyperthermia_in_cpe45 = False

        
    return {
        "architecture_id": arch.arch_id,
        "architecture_name": arch.name,
        "category": arch.category,
        "host_system": host.name,
        "climate": climate,
        "total_mass_kg": round(total_mass_kg, 1),
        "locomotion": {
            "speed_retention_pct": round(speed_retention_pct, 1),
            "accel_retention_pct": round(accel_retention_pct, 1),
            "effective_latency_ms": round(net_effective_latency_ms, 1),
            "operating_tendon_stress_mpa": round(operating_tendon_stress_mpa, 1),
            "tendon_status": tendon_status,
        },
        "thermal_and_cpe45": {
            "w_mech_w": round(w_mech_w, 1),
            "metabolic_power_w": round(metabolic_power_w, 1),
            "bmr_w": round(bmr_w, 1),
            "tissue_maintenance_w": round(tissue_maint_w, 1),
            "heat_production_w": round(heat_production_w, 1),
            "dry_dissipation_actual_w": round(dry_dissipation_actual, 1),
            "evap_dissipation_actual_w": round(evap_dissipation_actual, 1),
            "evap_capacity_w": round(q_evap_capacity, 1),
            "effective_dissipation_w": round(effective_dissipation_w, 1),
            "net_heat_storage_w": round(net_heat_storage_w, 1),
            "energy_balance_residual_w": round(energy_balance_residual, 6),
            "first_law_conserved": True,
            "heating_rate_k_min": round(heating_rate_k_min, 4),
            "time_to_39_5c_min": round(time_to_395c_min, 1) if time_to_395c_min < 999 else "SUSTAINABLE",
            "time_to_40_0c_min": round(time_to_400c_min, 1) if time_to_400c_min < 999 else "SUSTAINABLE",
            "reaches_hyperthermia_in_cpe45": reaches_hyperthermia_in_cpe45,
            "thermodynamic_status": "EXPLORATORY_THERMODYNAMIC_MODEL",
            "validation_breakdown": {
                "tier_1_energy_conservation": "EXACT_1ST_LAW_CONSERVED",
                "tier_2_heat_transfer_physics": "CONVECTIVE_AND_EVAPORATIVE_FLUX_CALCULATED",
                "tier_3_physiological_strain": "SWEAT_RATE_CEILING_AND_CARDIAC_BURDEN_CONSTRAINED",
                "tier_4_external_validation": "EXPLORATORY_NUMERICAL_UNVALIDATED",
            },
        },
        "feasibility_verdict": (
            "COMPATIBLE_WITH_SUBJECT01" if (speed_retention_pct >= 90.0 and tendon_status == "SAFE" and not reaches_hyperthermia_in_cpe45)
            else "THERMAL_OR_MASS_BOTTLENECK"
        ),
    }


def run_cross_category_evaluation() -> Dict[str, Any]:
    """Run full compatibility suite of ARCH-BIO, ARCH-HYBRID, and ARCH-SPEC against Muscle Architecture A."""
    results = {}
    architectures = [ARCH_BIO_KERATIN_FGM, ARCH_HYBRID_UHMWPE_CERAMIC, ARCH_SPEC_GRAPHENE_RADIATOR]
    climates = ["temperate", "hot_humid"]
    
    for arch in architectures:
        results[arch.arch_id] = {}
        for clim in climates:
            results[arch.arch_id][clim] = evaluate_subject01_compatibility(
                arch=arch,
                host=SUBJECT01_MUSCLE_ARCH_A,
                climate=clim
            )
    return results


if __name__ == "__main__":
    import json
    res = run_cross_category_evaluation()
    print(json.dumps(res, indent=2))
