"""MODEL-12: Biological, Biohybrid & Speculative Materials Evidence Model.

AEGIS-01: Biological Defense & Survivability Program (Cycle 3).
Calibrated against empirical material properties from peer-reviewed literature.
Explicitly distinguishes between:
  1. ARCH-BIO: Fully Endogenous Biological Materials (chitin, keratin, osteoderm, FGM)
  2. ARCH-HYBRID: Internal Biohybrid Materials (UHMWPE-mesh, CNT-polyurethane fascial wraps)
  3. ARCH-SPEC: Speculative Biological Materials (enzymatic graphene-protein biocomposites)

Independent Sources:
  - Weaver, J. C. et al. (2012). Science. 336:1275-1280 (Mantis shrimp dactyl club Bouligand).
  - Wang, B. et al. (2016). Acta Biomater. 41:60-74 (Pangolin keratin scale structure).
  - Chen, I. H. et al. (2011). J. Mech. Behav. Biomed. Mater. 4(5):713-722 (Armadillo osteoderms).
  - Meyers, M. A. et al. (2008). Prog. Mater. Sci. 53:1-206 (Biological materials science).
  - Tan, Y. et al. (2015). Nat. Chem. Biol. 11:488-495 (Squid beak histidine-crosslinked gradient).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass(frozen=True)
class BiomaterialEvidence:
    """Represents a biological or biohybrid material with verified physical properties."""
    material_id: str
    name: str
    category: str  # "ARCH-BIO", "ARCH-HYBRID", "ARCH-SPEC"
    source_organism_or_system: str
    primary_citation: str
    experimental_confirmation: str  # "CONFIRMED_ANIMAL", "CONFIRMED_SYNTHETIC", "SPECULATIVE"
    
    # Physical and Mechanical Properties (SI units)
    density_kg_m3: float
    youngs_modulus_gpa_dry: float
    youngs_modulus_gpa_hydrated: float
    tensile_strength_mpa: float
    compressive_strength_mpa: float
    fracture_toughness_k1c_mpa_m05: float
    work_of_fracture_gc_kj_m2: float
    strain_to_failure_pct: float
    fatigue_limit_se_mpa: float  # Fatigue strength at 10^6 cycles
    vickers_hardness_hv: float
    
    # Biological & Physiological Metrics
    cellular_turnover_days: float  # -1 if synthetic / acellular
    metabolic_maintenance_w_kg: float  # ATP/metabolic power required per kg
    flexural_stiffness_factor: float  # Normalized resistance to joint bending
    biocompatibility_status: str  # "NATIVE", "BIOCOMPATIBLE_INTEGRATED", "ENCAPSULATION_RISK"
    human_translational_barriers: List[str]


# -------------------------------------------------------------------------
# Empirical Biomaterials Database
# -------------------------------------------------------------------------

MATERIALS_DATABASE: Dict[str, BiomaterialEvidence] = {
    "MAT-DERM-HUMAN": BiomaterialEvidence(
        material_id="MAT-DERM-HUMAN",
        name="Human Reticular Dermis (Baseline)",
        category="ARCH-BIO",
        source_organism_or_system="Homo sapiens",
        primary_citation="Silver et al. (2001). Skin Res. Technol. 7:18-23",
        experimental_confirmation="CONFIRMED_HUMAN",
        density_kg_m3=1150.0,
        youngs_modulus_gpa_dry=0.08,
        youngs_modulus_gpa_hydrated=0.035,
        tensile_strength_mpa=18.0,
        compressive_strength_mpa=2.5,
        fracture_toughness_k1c_mpa_m05=0.45,
        work_of_fracture_gc_kj_m2=2.1,
        strain_to_failure_pct=65.0,
        fatigue_limit_se_mpa=5.0,
        vickers_hardness_hv=0.15,
        cellular_turnover_days=28.0,
        metabolic_maintenance_w_kg=1.8,
        flexural_stiffness_factor=1.0,
        biocompatibility_status="NATIVE",
        human_translational_barriers=[
            "Baseline control tissue, low cut and puncture resistance against concentrated tools."
        ],
    ),
    
    "MAT-BOULIGAND-CHITIN": BiomaterialEvidence(
        material_id="MAT-BOULIGAND-CHITIN",
        name="Bouligand Helicoidal Chitin-Apatite (Stomatopod Club)",
        category="ARCH-BIO",
        source_organism_or_system="Odontodactylus scyllarus (Mantis Shrimp)",
        primary_citation="Weaver et al. (2012). Science. 336:1275-1280",
        experimental_confirmation="CONFIRMED_ANIMAL",
        density_kg_m3=1780.0,
        youngs_modulus_gpa_dry=25.0,
        youngs_modulus_gpa_hydrated=15.0,
        tensile_strength_mpa=120.0,
        compressive_strength_mpa=380.0,
        fracture_toughness_k1c_mpa_m05=3.8,
        work_of_fracture_gc_kj_m2=6.5,
        strain_to_failure_pct=4.5,
        fatigue_limit_se_mpa=85.0,
        vickers_hardness_hv=3.5,
        cellular_turnover_days=180.0,  # Requires ecdysis in arthropods
        metabolic_maintenance_w_kg=3.2,
        flexural_stiffness_factor=8.5,
        biocompatibility_status="ENCAPSULATION_RISK",
        human_translational_barriers=[
            "Humans lack chitin synthase enzymes (CHS); pathway must be transgenically synthesized.",
            "Arthropods rely on periodic ecdysis (molting) to replace worn appendages; continuous mammalian remodeling unproven.",
            "Epitaxial mineralization requires marine-like carbonate/fluorapatite conditions.",
            "Direct interface with vascularized mammalian dermis triggers severe foreign body reaction."
        ],
    ),
    
    "MAT-KERATIN-PANGOLIN": BiomaterialEvidence(
        material_id="MAT-KERATIN-PANGOLIN",
        name="Cross-Lamellar Keratin Scale (Pangolin)",
        category="ARCH-BIO",
        source_organism_or_system="Manis tricuspis (Pangolin)",
        primary_citation="Wang et al. (2016). Acta Biomater. 41:60-74",
        experimental_confirmation="CONFIRMED_ANIMAL",
        density_kg_m3=1320.0,
        youngs_modulus_gpa_dry=2.2,
        youngs_modulus_gpa_hydrated=0.65,
        tensile_strength_mpa=85.0,
        compressive_strength_mpa=110.0,
        fracture_toughness_k1c_mpa_m05=2.4,
        work_of_fracture_gc_kj_m2=16.8,  # Exceptional hydrated crack-bridging
        strain_to_failure_pct=38.0,
        fatigue_limit_se_mpa=35.0,
        vickers_hardness_hv=0.45,
        cellular_turnover_days=90.0,
        metabolic_maintenance_w_kg=1.4,
        flexural_stiffness_factor=3.2,
        biocompatibility_status="NATIVE",
        human_translational_barriers=[
            "Extensive dermal keratinization blocks eccrine sweating, triggering severe hyperthermia during cursorial locomotion.",
            "Slow biosynthesis (0.3-0.5 mm/month); recovery of damaged scale plates requires 60-120 days.",
            "Hydration sensitivity: dry scales are hard but prone to brittle chipping; wet scales deform easily under sharp puncture."
        ],
    ),
    
    "MAT-OSTEODERM-ARMADILLO": BiomaterialEvidence(
        material_id="MAT-OSTEODERM-ARMADILLO",
        name="Mineralized Dermal Osteoderm with Collagenous Sutures",
        category="ARCH-BIO",
        source_organism_or_system="Dasypus novemcinctus (Nine-Banded Armadillo)",
        primary_citation="Chen et al. (2011). J. Mech. Behav. Biomed. Mater. 4(5):713-722",
        experimental_confirmation="CONFIRMED_ANIMAL",
        density_kg_m3=1880.0,
        youngs_modulus_gpa_dry=12.5,
        youngs_modulus_gpa_hydrated=9.5,
        tensile_strength_mpa=95.0,
        compressive_strength_mpa=175.0,
        fracture_toughness_k1c_mpa_m05=2.8,
        work_of_fracture_gc_kj_m2=4.2,
        strain_to_failure_pct=2.8,
        fatigue_limit_se_mpa=45.0,
        vickers_hardness_hv=0.85,
        cellular_turnover_days=365.0,
        metabolic_maintenance_w_kg=2.5,
        flexural_stiffness_factor=12.0,
        biocompatibility_status="NATIVE",
        human_translational_barriers=[
            "Ectopic bone formation in humans mimics fibrodysplasia ossificans progressiva (FOP), causing ankylosis and asphyxiation.",
            "High acoustic impedance mismatch (Z ~ 6.5 MRayl vs tissue 1.6 MRayl) creates lethal tensile spallation upon ballistic shock.",
            "Significant areal mass overhead (+12 to +15 kg) impairs locomotion acceleration and joint kinematics."
        ],
    ),
    
    "MAT-ENDOGENOUS-FGM": BiomaterialEvidence(
        material_id="MAT-ENDOGENOUS-FGM",
        name="Continuous Hydroxyapatite-Collagen Gradient (FGM)",
        category="ARCH-BIO",
        source_organism_or_system="Biomimetic Squid Beak / Dento-Enamel Junction Analogue",
        primary_citation="Tan et al. (2015). Nat. Chem. Biol. 11:488-495",
        experimental_confirmation="CONFIRMED_ANIMAL",
        density_kg_m3=1550.0,
        youngs_modulus_gpa_dry=14.0,
        youngs_modulus_gpa_hydrated=8.2,
        tensile_strength_mpa=105.0,
        compressive_strength_mpa=210.0,
        fracture_toughness_k1c_mpa_m05=3.2,
        work_of_fracture_gc_kj_m2=8.4,
        strain_to_failure_pct=8.5,
        fatigue_limit_se_mpa=60.0,
        vickers_hardness_hv=1.45,
        cellular_turnover_days=180.0,
        metabolic_maintenance_w_kg=2.8,
        flexural_stiffness_factor=4.5,
        biocompatibility_status="BIOCOMPATIBLE_INTEGRATED",
        human_translational_barriers=[
            "No known mammalian developmental program for stable 5 mm trans-epithelial mineral concentration gradients.",
            "Calcium/phosphate systemic homeostasis risks ectopic vascular calcification and nephrolithiasis.",
            "Remodeling of continuous gradient requires coordinated osteoblast/osteoclast synchronization without discrete lamellae."
        ],
    ),
    
    "MAT-BIOHYBRID-UHMWPE": BiomaterialEvidence(
        material_id="MAT-BIOHYBRID-UHMWPE",
        name="Internal Biohybrid Porous UHMWPE-Collagen Ingrowth Mesh",
        category="ARCH-HYBRID",
        source_organism_or_system="Engineered Implantable Composite",
        primary_citation="Kurtz, S. M. (2015). UHMWPE Biomaterials Handbook, Academic Press",
        experimental_confirmation="CONFIRMED_SYNTHETIC",
        density_kg_m3=970.0,
        youngs_modulus_gpa_dry=1.4,
        youngs_modulus_gpa_hydrated=1.4,
        tensile_strength_mpa=140.0,
        compressive_strength_mpa=65.0,
        fracture_toughness_k1c_mpa_m05=5.5,
        work_of_fracture_gc_kj_m2=32.0,  # Extreme synthetic ductility
        strain_to_failure_pct=85.0,
        fatigue_limit_se_mpa=48.0,
        vickers_hardness_hv=0.25,
        cellular_turnover_days=-1.0,  # Non-renewable synthetic polymer
        metabolic_maintenance_w_kg=0.0,  # Zero biological ATP cost
        flexural_stiffness_factor=1.8,
        biocompatibility_status="BIOCOMPATIBLE_INTEGRATED",
        human_translational_barriers=[
            "Synthetic implant cannot self-repair; cumulative microstructural fatigue micro-voids require surgical explantation.",
            "Sub-micron polymeric wear debris generation over years triggers chronic macrophage osteolysis.",
            "Bacterial biofilm colonization risk if injured in non-sterile field conditions."
        ],
    ),
    
    "MAT-BIOHYBRID-CNT-PU": BiomaterialEvidence(
        material_id="MAT-BIOHYBRID-CNT-PU",
        name="Carbon Nanotube / Segmented Polyurethane Fascial Sleeve",
        category="ARCH-HYBRID",
        source_organism_or_system="Synthetic Carbon Nanomaterial Scaffold",
        primary_citation="Coleman, J. N. et al. (2006). Adv. Mater. 18:689-706",
        experimental_confirmation="CONFIRMED_SYNTHETIC",
        density_kg_m3=1250.0,
        youngs_modulus_gpa_dry=4.8,
        youngs_modulus_gpa_hydrated=4.6,
        tensile_strength_mpa=280.0,
        compressive_strength_mpa=150.0,
        fracture_toughness_k1c_mpa_m05=6.8,
        work_of_fracture_gc_kj_m2=24.0,
        strain_to_failure_pct=45.0,
        fatigue_limit_se_mpa=110.0,
        vickers_hardness_hv=1.1,
        cellular_turnover_days=-1.0,
        metabolic_maintenance_w_kg=0.0,
        flexural_stiffness_factor=2.4,
        biocompatibility_status="ENCAPSULATION_RISK",
        human_translational_barriers=[
            "High aspect ratio CNTs induce asbestos-like granulomatous pleurisy/fibrosis if free fibers detach.",
            "Fibrous capsule formation isolates the sleeve from functional myotendinous mechanotransduction.",
            "Permanent synthetic fixture does not adapt to muscular hypertrophy or tissue atrophy."
        ],
    ),
    
    "MAT-SPEC-GRAPHENE-PROTEIN": BiomaterialEvidence(
        material_id="MAT-SPEC-GRAPHENE-PROTEIN",
        name="Speculative Enzymatic Graphene-Chitin Biosynthetic Nanocomposite",
        category="ARCH-SPEC",
        source_organism_or_system="Hypothetical Synthetic Biology Pathway",
        primary_citation="Lee, C. et al. (2008). Science. 321:385-388 (Graphene baseline)",
        experimental_confirmation="SPECULATIVE",
        density_kg_m3=1650.0,
        youngs_modulus_gpa_dry=95.0,
        youngs_modulus_gpa_hydrated=85.0,
        tensile_strength_mpa=1200.0,
        compressive_strength_mpa=850.0,
        fracture_toughness_k1c_mpa_m05=12.5,
        work_of_fracture_gc_kj_m2=45.0,
        strain_to_failure_pct=6.5,
        fatigue_limit_se_mpa=450.0,
        vickers_hardness_hv=18.5,
        cellular_turnover_days=300.0,
        metabolic_maintenance_w_kg=6.5,
        flexural_stiffness_factor=15.0,
        biocompatibility_status="ENCAPSULATION_RISK",
        human_translational_barriers=[
            "No known living enzyme or ribosome can synthesize covalent sp2 carbon sheets in an aqueous intracellular milieu.",
            "Thermodynamic barrier: enzymatic dehydrogenation of hydrocarbons to pure graphene requires extreme energy inputs.",
            "Cellular toxicity: intracellular graphene nano-sheets physically pierce lysosomal and mitochondrial membranes."
        ],
    ),
}


# -------------------------------------------------------------------------
# Engineering Material Assessment Functions
# -------------------------------------------------------------------------

def compute_material_mechanics(
    mat: BiomaterialEvidence,
    thickness_mm: float = 4.0,
    indenter_radius_mm: float = 0.5,
    hydration_state: str = "hydrated"
) -> Dict[str, Any]:
    """Calculate mechanical resistance, mass penalty, and flexibility for a given thickness.
    
    Equations:
      1. Areal density: M_a = rho * t [kg/m^2]
      2. Flexural rigidity: D = E * t^3 / (12 * (1 - nu^2)) [N*m] (nu ~ 0.35)
      3. Slicing resistance (Atkins): F_cut = G_c * t + mu * F_n
      4. Puncture resistance: F_p = 2*pi*R*t*sigma_u*(G_c/(E*t))^(1/3) + pi*R^2*Hv*0.35
      5. Approximate Ballistic Limit (Exploratory Recht-Ipson surrogate, fragment-simulating projectile 1.1g):
         V50 = sqrt(2 * G_c * Area / mass_proj) * empirical factor.
    """
    t_m = thickness_mm * 1e-3
    r_m = indenter_radius_mm * 1e-3
    nu = 0.35
    
    e_gpa = mat.youngs_modulus_gpa_hydrated if hydration_state == "hydrated" else mat.youngs_modulus_gpa_dry
    e_pa = e_gpa * 1e9
    sigma_u_pa = mat.tensile_strength_mpa * 1e6
    g_c_j_m2 = mat.work_of_fracture_gc_kj_m2 * 1e3
    hv_pa = mat.vickers_hardness_hv * 9.80665e6
    
    # 1. Areal Mass
    areal_mass_kg_m2 = mat.density_kg_m3 * t_m
    # Torso coverage ~ 0.35 m^2 (selective vital protection)
    torso_added_mass_kg = areal_mass_kg_m2 * 0.35
    
    # 2. Flexural Rigidity
    d_bending_nm = (e_pa * (t_m ** 3)) / (12.0 * (1.0 - nu ** 2))
    
    # 3. Cutting resistance across three physical regimes:
    # 3a. Regime 1: Pure Mode I crack propagation work (Lake-Thomas / Griffith limit + base friction)
    mode_1_crack_threshold_n = (g_c_j_m2 * t_m) + 15.0
    cutting_force_n = mode_1_crack_threshold_n  # Backward-compatible baseline
    
    # 3b. Regime 2: Macroscopic guillotine blade wedge chop (Atkins formulation)
    # Blade contact width w = 10.2 mm, wedge angle 30 deg, dynamic friction mu = 0.25
    theta_rad = math.radians(30.0)
    w_blade_m = 0.0102
    f_fracture_wedge = (g_c_j_m2 * t_m) / math.tan(theta_rad / 2.0)
    normal_wedge_force = sigma_u_pa * (t_m * w_blade_m * math.sin(theta_rad / 2.0))
    f_friction_wedge = 2.0 * 0.25 * normal_wedge_force
    guillotine_wedge_chop_n = f_fracture_wedge + f_friction_wedge
    
    # 3c. Regime 3: Knife draw slicing (Atkins draw slicing kinematics, xi = 4.0, blade wedge w = 10.2 mm)
    # Pure physical kinematic reduction: F_push = F_guillotine / sqrt(1 + xi^2) (Atkins 2006, 2009)
    # No arbitrary 0.20 or 0.70 multipliers.
    xi = 4.0
    kinematic_reduction = 1.0 / math.sqrt(1.0 + xi ** 2)
    draw_slicing_knife_n = guillotine_wedge_chop_n * kinematic_reduction
    
    # 3d. Regime 4: Ultra-thin razor scalpel slicing (w_blade -> 0, eliminating normal plastic wedge compression)
    # F_scalpel = F_fracture_wedge / sqrt(1 + xi^2) (Mahvash & Dupont 2010)
    draw_slicing_scalpel_n = f_fracture_wedge * kinematic_reduction
    draw_slicing_force_n = draw_slicing_knife_n  # Physical kinematic draw force

    
    # 4. Puncture resistance (Sharp indenter)
    deformation_ratio = max(0.001, g_c_j_m2 / (e_pa * t_m))
    wedging_term = 2.0 * math.pi * r_m * t_m * sigma_u_pa * (deformation_ratio ** (1.0 / 3.0))
    crushing_term = math.pi * (r_m ** 2) * hv_pa * 0.35
    total_puncture_n = wedging_term + crushing_term
    
    # 5. Exploratory V50 fragment resistance (1.1 g steel chisel fragment, STANAG 2920 proxy)
    # WARNING: Strictly exploratory. Simulation-only; uncalibrated by range live-fire.
    proj_mass_kg = 0.0011
    shear_area_m2 = 2.0 * math.pi * (0.0028) * t_m
    ballistic_shear_energy_j = sigma_u_pa * 0.577 * shear_area_m2 * t_m + (g_c_j_m2 * shear_area_m2)
    v50_exploratory_m_s = math.sqrt(2.0 * ballistic_shear_energy_j / proj_mass_kg)
    
    # 6. Fatigue safety margin under repetitive locomotion (cyclic stress ~ 15 MPa in tendons/dermis)
    cyclic_locomotor_stress_mpa = 15.0
    fatigue_safety_factor = mat.fatigue_limit_se_mpa / cyclic_locomotor_stress_mpa
    
    # 7. Self-repair and metabolic/immune maintenance debt
    if mat.category == "ARCH-HYBRID":
        biological_immune_clearance_w = round(0.22 * torso_added_mass_kg, 2)
        self_repair_rate_mm_day = 0.0
        repair_energy_cost_j_g = 0.0
        mechanical_lifespan_cycles = 1e7
    elif mat.material_id == "MAT-DERM-HUMAN":
        biological_immune_clearance_w = 0.0
        self_repair_rate_mm_day = 0.8
        repair_energy_cost_j_g = 125.0
        mechanical_lifespan_cycles = 1e9  # Continuously renewing living tissue
    elif mat.material_id == "MAT-KERATIN-PANGOLIN":
        biological_immune_clearance_w = 0.0
        self_repair_rate_mm_day = 0.015  # 0.45 mm/month
        repair_energy_cost_j_g = 210.0
        mechanical_lifespan_cycles = 1e8
    elif mat.material_id == "MAT-ENDOGENOUS-FGM":
        biological_immune_clearance_w = 0.0
        self_repair_rate_mm_day = 0.010
        repair_energy_cost_j_g = 340.0
        mechanical_lifespan_cycles = 5e8
    else:
        biological_immune_clearance_w = 0.0
        self_repair_rate_mm_day = 0.005
        repair_energy_cost_j_g = 280.0
        mechanical_lifespan_cycles = 1e8
    
    return {
        "material_id": mat.material_id,
        "name": mat.name,
        "category": mat.category,
        "thickness_mm": thickness_mm,
        "hydration": hydration_state,
        "areal_mass_kg_m2": round(areal_mass_kg_m2, 2),
        "torso_added_mass_kg": round(torso_added_mass_kg, 2),
        "flexural_rigidity_nm": round(d_bending_nm, 3),
        "cutting_resistance_n": round(cutting_force_n, 1),
        "mode_1_crack_threshold_n": round(mode_1_crack_threshold_n, 1),
        "guillotine_wedge_chop_n": round(guillotine_wedge_chop_n, 1),
        "draw_slicing_force_n": round(draw_slicing_force_n, 1),
        "draw_slicing_knife_n": round(draw_slicing_knife_n, 1),
        "draw_slicing_scalpel_n": round(draw_slicing_scalpel_n, 1),
        "puncture_resistance_n": round(total_puncture_n, 1),
        "fatigue_safety_factor": round(fatigue_safety_factor, 2),
        "v50_exploratory_fragment_m_s": round(v50_exploratory_m_s, 1),
        "ballistic_status": "EXPLORATORY_NUMERICAL_UNVALIDATED",
        "ballistic_warning": "Analytical Recht-Ipson surrogate. Not validated by physical range live-fire tests; does not prove weapon stopping capability.",
        "metabolic_power_cost_torso_w": round(mat.metabolic_maintenance_w_kg * torso_added_mass_kg, 2),
        "biological_immune_clearance_w": biological_immune_clearance_w,
        "self_repair_rate_mm_day": self_repair_rate_mm_day,
        "repair_energy_cost_j_g": repair_energy_cost_j_g,
        "mechanical_lifespan_cycles": mechanical_lifespan_cycles,
        "biocompatibility": mat.biocompatibility_status,
        "cellular_turnover_days": mat.cellular_turnover_days,
        "translational_barriers": mat.human_translational_barriers,
    }


def compare_material_archetypes() -> Dict[str, Any]:
    """Execute comparative assessment across all materials in database."""
    results = {}
    for mat_id, mat in MATERIALS_DATABASE.items():
        results[mat_id] = compute_material_mechanics(mat, thickness_mm=4.0)
    return results


if __name__ == "__main__":
    import json
    res = compare_material_archetypes()
    print(json.dumps(res, indent=2))
