#!/usr/bin/env python3
"""MODEL-01 — Biological Tissue Mechanics & Puncture/Cut Resistance.

This module models the mechanical resistance of multilayered biological integument
against blunt punch puncture, sharp indenter contact, and cutting (laceration).

Scientific Calibration & Limitations (Cycle 1A Audit):
- Sharp hypodermic needle insertion into living human skin typically requires 1.5 - 3.5 N
  (Shergold & Fleck 2004, 2005; Davis et al. 2004).
- The classical Lake-Thomas / Atkins gross-puncture formulation below models BLUNT PUNCH
  puncture or thick spike penetration (where the entire dermal cross-section must be
  plastically sheared or stretched to ultimate tensile failure), yielding ~25-30 N for human skin.
- For scalpel cutting with lateral draw motion (slicing), forces are 0.5 - 2.5 N (Mahvash & Dupont 2010).
  The Atkins guillotine formula below calculates pure normal wedging without slicing motion,
  yielding higher forces (~200 N).
- These boundaries are now explicitly labeled and bounded with uncertainty ranges.

Governing Equations:
1. Puncture resistance (Lake-Thomas / Griffith fracture criteria with indenter contact):
   F_puncture = 2 * pi * R_tip * t_dermis * sigma_u * (G_c / (E * t_dermis))^(1/3) + F_friction
2. Cutting resistance (Atkins fracture mechanics):
   F_cut = (G_c * t_layer) / tan(theta_wedge / 2) + mu_blade * P_contact * Area_contact
3. Layered composite work to penetrate:
   W_total = sum( G_c_i * Area_crack_i + Integral(sigma_i(epsilon) dV) )

Scientific Anchors:
- Wang, Yang, Sherman, Meyers (2016), Acta Biomater. 41:60-74 (Pangolin keratin).
- Chen, Kiang, Correa, Meyers (2011), J Mech Behav Biomed Mater. 4(5):713-722 (Armadillo osteoderms).
- Shergold, O. A., & Fleck, N. A. (2004). Mechanisms of deep penetration into soft solids. Proc. R. Soc. A. 460:3037-3058.
- Lake & Thomas (1967), Proc. R. Soc. A. 300:108-119.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import math
import numpy as np


@dataclass(frozen=True)
class LayerProperties:
    name: str
    thickness_mm: float           # Layer thickness [mm]
    youngs_modulus_mpa: float     # Young's modulus E [MPa]
    tensile_strength_mpa: float   # Ultimate tensile strength sigma_u [MPa]
    fracture_toughness_j_m2: float # Critical strain energy release rate G_c [J/m^2]
    density_kg_m3: float          # Density [kg/m^3]
    hardness_vickers_hv: float    # Vickers hardness [kgf/mm^2]
    friction_coeff: float         # Dynamic friction with steel [dimensionless]


# Reference physiological & bio-material parameters
HUMAN_STRATUM_CORNEUM = LayerProperties(
    name="Human Stratum Corneum",
    thickness_mm=0.02,
    youngs_modulus_mpa=5.0,
    tensile_strength_mpa=3.0,
    fracture_toughness_j_m2=1200.0,
    density_kg_m3=1100.0,
    hardness_vickers_hv=2.0,
    friction_coeff=0.35,
)

HUMAN_DERMIS = LayerProperties(
    name="Human Reticular Dermis",
    thickness_mm=2.0,
    youngs_modulus_mpa=35.0,
    tensile_strength_mpa=18.0,
    fracture_toughness_j_m2=8500.0,
    density_kg_m3=1050.0,
    hardness_vickers_hv=1.0,
    friction_coeff=0.40,
)

HUMAN_HYPODERMIS = LayerProperties(
    name="Human Hypodermis (Adipose)",
    thickness_mm=4.0,
    youngs_modulus_mpa=0.05,
    tensile_strength_mpa=0.15,
    fracture_toughness_j_m2=400.0,
    density_kg_m3=920.0,
    hardness_vickers_hv=0.1,
    friction_coeff=0.20,
)

PANGOLIN_SCALE_KERATIN = LayerProperties(
    name="Pangolin Scale Beta-Keratin",
    thickness_mm=2.5,
    youngs_modulus_mpa=1200.0,
    tensile_strength_mpa=85.0,
    fracture_toughness_j_m2=14500.0,
    density_kg_m3=1300.0,
    hardness_vickers_hv=22.0,
    friction_coeff=0.25,
)

ARMADILLO_OSTEODERM = LayerProperties(
    name="Armadillo Mineralized Osteoderm",
    thickness_mm=2.0,
    youngs_modulus_mpa=6500.0,
    tensile_strength_mpa=20.0,
    fracture_toughness_j_m2=2200.0,
    density_kg_m3=1850.0,
    hardness_vickers_hv=45.0,
    friction_coeff=0.30,
)

BIOENGINEERED_TOUGHENED_COLLAGEN = LayerProperties(
    name="Bioengineered Cross-linked Collagen Mat",
    thickness_mm=4.0,
    youngs_modulus_mpa=250.0,
    tensile_strength_mpa=75.0,
    fracture_toughness_j_m2=32000.0,
    density_kg_m3=1200.0,
    hardness_vickers_hv=8.0,
    friction_coeff=0.28,
)


def calculate_puncture_force(layer: LayerProperties, indenter_radius_mm: float) -> Dict[str, float]:
    """Calculate the peak puncture resistance force for a single tissue layer.
    
    Uses Lake-Thomas / Atkins elastomeric fracture mechanics with indenter radius scaling.
    Units:
      indenter_radius_mm: [mm]
      F_puncture: [Newtons]
    """
    if indenter_radius_mm <= 0.0:
        raise ValueError("Indenter radius must be strictly positive")
    if layer.thickness_mm <= 0.0:
        raise ValueError("Layer thickness must be strictly positive")

    r_m = indenter_radius_mm * 1e-3
    t_m = layer.thickness_mm * 1e-3
    e_pa = layer.youngs_modulus_mpa * 1e6
    sigma_u_pa = layer.tensile_strength_mpa * 1e6
    g_c_j_m2 = layer.fracture_toughness_j_m2

    # Dimensionless fracture ratio (energy release vs elastic work)
    dimensionless_g = g_c_j_m2 / (e_pa * t_m)
    scale_factor = max(1e-4, dimensionless_g) ** (1.0 / 3.0)

    # Indentation contact force to reach ultimate strain
    f_fracture = 2.0 * math.pi * r_m * t_m * sigma_u_pa * scale_factor

    # Yield hardness resistance (direct compressive yield under indenter tip)
    tip_area_m2 = math.pi * (r_m ** 2)
    # Vickers hardness in Pa: HV * 9.80665e6
    hardness_pa = layer.hardness_vickers_hv * 9.80665e6
    f_hardness = tip_area_m2 * hardness_pa * 0.35  # Effective yield pressure factor

    f_total = f_fracture + f_hardness
    work_to_puncture_j = f_total * t_m * 0.5  # Triangular approximation of indentation work

    return {
        "f_puncture_n": round(f_total, 3),
        "f_fracture_component_n": round(f_fracture, 3),
        "f_hardness_component_n": round(f_hardness, 3),
        "work_to_puncture_j": round(work_to_puncture_j, 4),
    }


def calculate_cutting_force(layer: LayerProperties, blade_wedge_angle_deg: float, blade_width_mm: float) -> Dict[str, float]:
    """Calculate the cutting (laceration) force of a sharp blade through tissue.
    
    Atkins cutting model: F_cut = (G_c * t) / tan(theta/2) + F_friction
    """
    if blade_wedge_angle_deg <= 0.0 or blade_wedge_angle_deg >= 180.0:
        raise ValueError("Blade wedge angle must be in (0, 180) degrees")

    theta_rad = math.radians(blade_wedge_angle_deg)
    t_m = layer.thickness_mm * 1e-3
    w_m = blade_width_mm * 1e-3
    g_c = layer.fracture_toughness_j_m2

    # Atkins steady-state pure cutting fracture term
    f_fracture = (g_c * t_m) / math.tan(theta_rad / 2.0)

    # Normal blade-tissue contact force and friction
    # Contact pressure estimated from ultimate tensile strength
    sigma_u = layer.tensile_strength_mpa * 1e6
    normal_force = sigma_u * (t_m * w_m * math.sin(theta_rad / 2.0))
    f_friction = 2.0 * layer.friction_coeff * normal_force

    f_cut_total = f_fracture + f_friction

    return {
        "f_cut_n": round(f_cut_total, 3),
        "f_cut_fracture_n": round(f_fracture, 3),
        "f_cut_friction_n": round(f_friction, 3),
        "specific_cut_energy_j_m": round(f_cut_total * 1.0, 3),
    }


def calculate_slicing_force(
    layer: LayerProperties,
    blade_wedge_angle_deg: float = 30.0,
    blade_width_mm: float = 20.0,
    slice_to_push_ratio: float = 0.0,  # 0.0 = pure guillotine chop; >=4.0 = draw slicing
    blade_edge_radius_um: float = 1.0, # 0.2 um razor scalpel, 2.0 um utility blade, 20 um dull knife
) -> Dict[str, Any]:
    """Calculate realistic cutting force accounting for blade sharpness and slicing draw kinematics.
    
    Atkins slicing mechanics:
    F_push(xi) = F_guillotine / sqrt(1 + xi^2) + F_sharpness_correction
    Under lateral drawing (xi >= 4), normal penetration force drops by >75-90%.
    Under ultra-sharp razor edges (r_edge <= 0.5 um), cutting force drops to tens of Newtons,
    refuting any unconditional 'guaranteed resistance > 800 N'.
    """
    guillotine = calculate_cutting_force(layer, blade_wedge_angle_deg, blade_width_mm)
    f_guillotine = guillotine["f_cut_n"]
    
    xi = max(0.0, slice_to_push_ratio)
    kinematic_reduction = 1.0 / math.sqrt(1.0 + xi ** 2)
    sharpness_factor = min(2.5, max(0.05, blade_edge_radius_um / 2.0))
    
    f_push_effective = f_guillotine * kinematic_reduction * (0.35 + 0.65 * sharpness_factor)
    f_slice_lateral = f_push_effective * xi * layer.friction_coeff
    
    return {
        "slice_to_push_ratio": xi,
        "blade_edge_radius_um": blade_edge_radius_um,
        "f_push_normal_n": round(f_push_effective, 2),
        "f_slice_lateral_n": round(f_slice_lateral, 2),
        "guillotine_reference_n": round(f_guillotine, 2),
        "force_reduction_pct": round((1.0 - (f_push_effective / f_guillotine)) * 100.0, 1),
        "guaranteed_800n_valid": False,  # Slicing and sharp edges invalidate unconditional >800 N guarantee
        "scientific_caveat": (
            "Guaranteed cut resistance >800 N is FALSE under slicing draw (xi > 2) and sharp edges "
            "(r_edge < 1 um). Real cutting force drops to 15-60 N for scalpels and utility razors."
        ),
    }


def evaluate_composite_puncture(layers: List[LayerProperties], indenter_radius_mm: float) -> Dict[str, Any]:
    """Evaluate puncture resistance through a sequence of anatomical layers."""
    total_force_n = 0.0
    total_work_j = 0.0
    total_thickness_mm = 0.0
    areal_density_kg_m2 = 0.0
    layer_breakdown = []

    for l in layers:
        res = calculate_puncture_force(l, indenter_radius_mm)
        # In a layered stack, peak force is dominated by the strongest outer/middle barrier
        # while total work is cumulative across all penetrated layers
        total_force_n = max(total_force_n, res["f_puncture_n"])
        total_work_j += res["work_to_puncture_j"]
        total_thickness_mm += l.thickness_mm
        layer_mass_areal = (l.density_kg_m3 * (l.thickness_mm * 1e-3))
        areal_density_kg_m2 += layer_mass_areal

        layer_breakdown.append({
            "name": l.name,
            "thickness_mm": l.thickness_mm,
            "f_puncture_n": res["f_puncture_n"],
            "work_j": res["work_to_puncture_j"],
            "areal_density_kg_m2": round(layer_mass_areal, 3),
        })

    return {
        "peak_puncture_force_n": round(total_force_n, 2),
        "total_puncture_work_j": round(total_work_j, 3),
        "total_thickness_mm": round(total_thickness_mm, 2),
        "total_areal_density_kg_m2": round(areal_density_kg_m2, 3),
        "layers": layer_breakdown,
    }


def sensitivity_analysis(base_layer: LayerProperties, indenter_radius_mm: float = 0.5) -> Dict[str, float]:
    """Perform One-At-A-Time (OAT) dimensionless sensitivity analysis:
    S_param = (dF / F) / (dParam / Param).
    """
    base_res = calculate_puncture_force(base_layer, indenter_radius_mm)["f_puncture_n"]
    delta = 0.05  # 5% perturbation
    sensitivities = {}

    params = [
        ("thickness_mm", base_layer.thickness_mm),
        ("youngs_modulus_mpa", base_layer.youngs_modulus_mpa),
        ("tensile_strength_mpa", base_layer.tensile_strength_mpa),
        ("fracture_toughness_j_m2", base_layer.fracture_toughness_j_m2),
        ("hardness_vickers_hv", base_layer.hardness_vickers_hv),
    ]

    for name, val in params:
        d = dict(asdict(base_layer))
        d[name] = val * (1.0 + delta)
        perturbed_layer = LayerProperties(**d)
        perturbed_res = calculate_puncture_force(perturbed_layer, indenter_radius_mm)["f_puncture_n"]
        dF = perturbed_res - base_res
        s = (dF / base_res) / delta
        sensitivities[name] = round(s, 4)

    return sensitivities


def run_benchmark_scenarios() -> Dict[str, Any]:
    """Run standardized comparative benchmarks for MODEL-01:
    1. Baseline Human Skin (Epidermis + Dermis + Subcutis)
    2. Keratin-Shielded (Pangolin-like overlay on Human Dermis)
    3. Osteoderm Composite (Armadillo-like mineralized plates + Dermis)
    4. Bioengineered Advanced Matrix (Engineered cross-linked collagen + nanoceramic composite)
    """
    sharp_tip_radius_mm = 0.25  # Sharp needle / blade tip
    utility_tip_radius_mm = 1.0  # Moderate blunt puncture (e.g. screwdriver, fang)
    blade_angle_deg = 30.0
    blade_width_mm = 20.0

    human_stack = [HUMAN_STRATUM_CORNEUM, HUMAN_DERMIS, HUMAN_HYPODERMIS]
    pangolin_stack = [PANGOLIN_SCALE_KERATIN, HUMAN_DERMIS, HUMAN_HYPODERMIS]
    armadillo_stack = [ARMADILLO_OSTEODERM, HUMAN_DERMIS, HUMAN_HYPODERMIS]
    bioengineered_stack = [ARMADILLO_OSTEODERM, BIOENGINEERED_TOUGHENED_COLLAGEN, HUMAN_HYPODERMIS]

    results = {
        "model_id": "MODEL-01",
        "description": "Tissue Mechanics & Puncture/Cut Resistance",
        "scenarios": {
            "human_baseline": {
                "sharp_puncture": evaluate_composite_puncture(human_stack, sharp_tip_radius_mm),
                "utility_puncture": evaluate_composite_puncture(human_stack, utility_tip_radius_mm),
                "cut_resistance": calculate_cutting_force(HUMAN_DERMIS, blade_angle_deg, blade_width_mm),
                "sensitivity": sensitivity_analysis(HUMAN_DERMIS, sharp_tip_radius_mm),
            },
            "keratin_pangolin_analogue": {
                "sharp_puncture": evaluate_composite_puncture(pangolin_stack, sharp_tip_radius_mm),
                "utility_puncture": evaluate_composite_puncture(pangolin_stack, utility_tip_radius_mm),
                "cut_resistance": calculate_cutting_force(PANGOLIN_SCALE_KERATIN, blade_angle_deg, blade_width_mm),
                "sensitivity": sensitivity_analysis(PANGOLIN_SCALE_KERATIN, sharp_tip_radius_mm),
            },
            "mineralized_osteoderm": {
                "sharp_puncture": evaluate_composite_puncture(armadillo_stack, sharp_tip_radius_mm),
                "utility_puncture": evaluate_composite_puncture(armadillo_stack, utility_tip_radius_mm),
                "cut_resistance": calculate_cutting_force(ARMADILLO_OSTEODERM, blade_angle_deg, blade_width_mm),
                "sensitivity": sensitivity_analysis(ARMADILLO_OSTEODERM, sharp_tip_radius_mm),
            },
            "bioengineered_composite": {
                "sharp_puncture": evaluate_composite_puncture(bioengineered_stack, sharp_tip_radius_mm),
                "utility_puncture": evaluate_composite_puncture(bioengineered_stack, utility_tip_radius_mm),
                "cut_resistance": calculate_cutting_force(BIOENGINEERED_TOUGHENED_COLLAGEN, blade_angle_deg, blade_width_mm),
                "sensitivity": sensitivity_analysis(BIOENGINEERED_TOUGHENED_COLLAGEN, sharp_tip_radius_mm),
            },
        },
        "verdict": {
            "regime_classification": "BLUNT_PUNCH_AND_GUILLOTINE_WEDGING",
            "clinical_caveat": (
                "Calculated forces (~28.7N puncture, ~212N cut) overestimate sharp surgical needle "
                "insertion (1.5-3.5N) and slicing scalpel cuts (0.5-2.5N) by ~8-10x due to neglecting "
                "Mode-I tip crack wedging and lateral draw slicing ratios. Valid as blunt/spike bounds."
            ),
            "cut_resistance_status": "CONFIRMED_HIGH_BLUNT_BOUND",
            "guaranteed_800n_status": "REFUTED_DEPENDENT_ON_SLICING_AND_SHARPNESS",
            "slicing_draw_reduction": calculate_slicing_force(
                BIOENGINEERED_TOUGHENED_COLLAGEN, blade_wedge_angle_deg=30.0, blade_width_mm=20.0, slice_to_push_ratio=4.0, blade_edge_radius_um=0.5
            ),
            "puncture_resistance_status": "CONFIRMED_HIGH_BLUNT_BOUND",
            "human_vs_bioengineered_gain_ratio": round(
                evaluate_composite_puncture(bioengineered_stack, sharp_tip_radius_mm)["peak_puncture_force_n"]
                / evaluate_composite_puncture(human_stack, sharp_tip_radius_mm)["peak_puncture_force_n"],
                2,
            ),
        },
    }
    return results


if __name__ == "__main__":
    import json
    res = run_benchmark_scenarios()
    print(json.dumps(res, indent=2))
