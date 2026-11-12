"""
E2 Experiment: Tendon Regional Mechanics Validation
Cycle 15 — SUBJECT-01

Hypothesis HYP-0010: Using regional tendon CSA improves local strain prediction
vs single mean CSA.

STATUS: DATA_BLOCKED — no suitable public dataset identified.

This script contains:
1. The pre-registered analysis implementation (ready to run when data are available).
2. Stubbed data loading section — replace with actual dataset path when available.

Pre-registration lock date: 2026-11-12
Agent: e2-tendon

RULES (locked):
- Do NOT substitute literature mean CSA as individual participant data.
- Do NOT mix structural stiffness (k, N/mm) with material modulus (E, MPa).
- Do NOT combine strength endpoints into a single index.
- Record negative results honestly.
"""

import json
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# PRE-REGISTRATION: Locked analysis constants
# ---------------------------------------------------------------------------

# Decision criterion: GO if RMSE_reduction >= 10% across majority of participants
GO_THRESHOLD_RMSE_REDUCTION = 0.10  # 10%
MAJORITY_THRESHOLD = 0.50           # >50% of participants

# Sensitivity analysis: CSA measurement error
CSA_ERROR_FRACTION = 0.10           # ±10%

# Material law: linear elastic  sigma = E * epsilon
# E (MPa) is estimated from structural stiffness k (N/mm) via:
#   E = k * L0 / CSA_mean
# where L0 is resting tendon length (mm).
# E is IDENTICAL for Model A and Model B — only CSA differs.

# ---------------------------------------------------------------------------
# DATA LOADING (stub — replace when data become available)
# ---------------------------------------------------------------------------

def load_dataset(data_path: Path) -> dict:
    """
    Load participant-specific tendon mechanics dataset.

    Expected data schema per participant:
    {
        "participant_id": str,
        "csa_proximal_mm2": float,   # participant-specific, ultrasound/MRI
        "csa_mid_mm2": float,        # participant-specific, ultrasound/MRI
        "csa_distal_mm2": float,     # participant-specific, ultrasound/MRI
        "tendon_force_N": list[float],      # time series or load levels
        "strain_proximal_obs": list[float], # observed local strain, proximal
        "strain_mid_obs": list[float],      # observed local strain, mid
        "strain_distal_obs": list[float],   # observed local strain, distal
        "tendon_length_mm": float,          # resting length
        "structural_stiffness_N_per_mm": float  # from load-elongation curve
    }
    """
    raise NotImplementedError(
        "DATA_BLOCKED: No suitable public dataset available. "
        "Required variables: participant-specific regional CSA, local strain "
        "per region, applied force, >=6 participants."
    )


# ---------------------------------------------------------------------------
# MODEL A: Single mean CSA
# ---------------------------------------------------------------------------

def model_a_strain(force_N: np.ndarray, csa_prox: float, csa_mid: float,
                   csa_dist: float, E_MPa: float) -> dict:
    """
    Model A: single mean CSA -> same stress/strain at all regions.

    Parameters
    ----------
    force_N      : applied tendon force (N), shape (T,)
    csa_prox     : participant CSA at proximal region (mm²)
    csa_mid      : participant CSA at mid region (mm²)
    csa_dist     : participant CSA at distal region (mm²)
    E_MPa        : material modulus (MPa) — derived from structural stiffness

    Returns
    -------
    dict with keys: strain_proximal, strain_mid, strain_distal (all equal)
    """
    csa_mean_mm2 = np.mean([csa_prox, csa_mid, csa_dist])
    # Convert N and mm² to MPa: 1 MPa = 1 N/mm²
    stress_MPa = force_N / csa_mean_mm2   # N / mm² = MPa
    strain = stress_MPa / E_MPa           # dimensionless
    return {
        "strain_proximal": strain,
        "strain_mid": strain,
        "strain_distal": strain,
        "csa_mean_mm2": csa_mean_mm2,
    }


# ---------------------------------------------------------------------------
# Model B: Regional CSA
# ---------------------------------------------------------------------------

def model_b_strain(force_N: np.ndarray, csa_prox: float, csa_mid: float,
                   csa_dist: float, E_MPa: float) -> dict:
    """
    Model B: regional CSA -> different stress/strain at each region.

    ONLY difference from Model A: CSA_region used instead of CSA_mean.
    E (material modulus) is IDENTICAL to Model A.

    Parameters
    ----------
    force_N      : applied tendon force (N), shape (T,)
    csa_prox     : participant CSA at proximal region (mm²)
    csa_mid      : participant CSA at mid region (mm²)
    csa_dist     : participant CSA at distal region (mm²)
    E_MPa        : material modulus (MPa) — SAME as Model A

    Returns
    -------
    dict with keys: strain_proximal, strain_mid, strain_distal (differ by region)
    """
    strain_prox = (force_N / csa_prox) / E_MPa
    strain_mid  = (force_N / csa_mid)  / E_MPa
    strain_dist = (force_N / csa_dist) / E_MPa
    return {
        "strain_proximal": strain_prox,
        "strain_mid": strain_mid,
        "strain_distal": strain_dist,
    }


# ---------------------------------------------------------------------------
# Derive material modulus from structural stiffness
# ---------------------------------------------------------------------------

def derive_material_modulus(structural_stiffness_N_per_mm: float,
                             tendon_length_mm: float,
                             csa_mean_mm2: float) -> float:
    """
    E (MPa) = k (N/mm) * L0 (mm) / CSA_mean (mm²)

    Units:
        k    : N/mm
        L0   : mm
        CSA  : mm²
        E    : (N/mm * mm) / mm² = N/mm² = MPa  ✓

    Parameters
    ----------
    structural_stiffness_N_per_mm : k from load-elongation curve (N/mm)
    tendon_length_mm              : resting tendon length (mm)
    csa_mean_mm2                  : mean CSA for normalisation (mm²)

    Returns
    -------
    E_MPa : float
    """
    return structural_stiffness_N_per_mm * tendon_length_mm / csa_mean_mm2


# ---------------------------------------------------------------------------
# RMSE calculation
# ---------------------------------------------------------------------------

def rmse(predicted: np.ndarray, observed: np.ndarray) -> float:
    return float(np.sqrt(np.mean((predicted - observed) ** 2)))


# ---------------------------------------------------------------------------
# Sensitivity analysis: ±10% CSA perturbation
# ---------------------------------------------------------------------------

def sensitivity_analysis(participant_data: dict, E_MPa: float,
                          error_fraction: float = CSA_ERROR_FRACTION) -> dict:
    """
    Perturb CSA by ±error_fraction and recompute RMSE difference (Model A - Model B).
    Returns bounds on RMSE_reduction across perturbation directions.
    """
    results = {}
    for direction, sign in [("plus10", 1 + error_fraction), ("minus10", 1 - error_fraction)]:
        csa_prox_p = participant_data["csa_proximal_mm2"] * sign
        csa_mid_p  = participant_data["csa_mid_mm2"] * sign
        csa_dist_p = participant_data["csa_distal_mm2"] * sign
        force = np.array(participant_data["tendon_force_N"])

        pred_a = model_a_strain(force, csa_prox_p, csa_mid_p, csa_dist_p, E_MPa)
        pred_b = model_b_strain(force, csa_prox_p, csa_mid_p, csa_dist_p, E_MPa)

        for region in ["proximal", "mid", "distal"]:
            obs = np.array(participant_data[f"strain_{region}_obs"])
            rmse_a = rmse(pred_a[f"strain_{region}"], obs)
            rmse_b = rmse(pred_b[f"strain_{region}"], obs)
            reduction = (rmse_a - rmse_b) / rmse_a if rmse_a > 0 else 0.0
            results[f"{direction}_{region}"] = {
                "rmse_model_a": rmse_a,
                "rmse_model_b": rmse_b,
                "rmse_reduction_fraction": reduction,
            }
    return results


# ---------------------------------------------------------------------------
# Main analysis (stubbed — will execute when data are available)
# ---------------------------------------------------------------------------

def run_analysis(data_path: Path) -> dict:
    """Full E2 analysis pipeline."""
    dataset = load_dataset(data_path)  # raises NotImplementedError if DATA_BLOCKED

    participants = dataset["participants"]
    n = len(participants)
    results_per_participant = []

    for p in participants:
        force = np.array(p["tendon_force_N"])
        csa_prox = p["csa_proximal_mm2"]
        csa_mid  = p["csa_mid_mm2"]
        csa_dist = p["csa_distal_mm2"]
        L0       = p["tendon_length_mm"]
        k        = p["structural_stiffness_N_per_mm"]

        csa_mean = np.mean([csa_prox, csa_mid, csa_dist])
        E_MPa = derive_material_modulus(k, L0, csa_mean)

        pred_a = model_a_strain(force, csa_prox, csa_mid, csa_dist, E_MPa)
        pred_b = model_b_strain(force, csa_prox, csa_mid, csa_dist, E_MPa)

        p_result = {"participant_id": p["participant_id"], "E_MPa": E_MPa, "regions": {}}
        n_regions_go = 0

        for region in ["proximal", "mid", "distal"]:
            obs = np.array(p[f"strain_{region}_obs"])
            rmse_a = rmse(pred_a[f"strain_{region}"], obs)
            rmse_b = rmse(pred_b[f"strain_{region}"], obs)
            reduction = (rmse_a - rmse_b) / rmse_a if rmse_a > 0 else 0.0
            region_go = reduction >= GO_THRESHOLD_RMSE_REDUCTION
            if region_go:
                n_regions_go += 1
            p_result["regions"][region] = {
                "rmse_model_a": rmse_a,
                "rmse_model_b": rmse_b,
                "rmse_reduction_fraction": reduction,
                "GO": region_go,
            }

        p_result["all_regions_GO"] = (n_regions_go == 3)
        p_result["sensitivity"] = sensitivity_analysis(p, E_MPa)
        results_per_participant.append(p_result)

    # Decision: GO if majority of participants show >=10% RMSE reduction across all regions
    n_go = sum(1 for r in results_per_participant if r["all_regions_GO"])
    fraction_go = n_go / n
    final_status = "GO" if fraction_go > MAJORITY_THRESHOLD else "NO_GO"

    return {
        "experiment": "E2",
        "hypothesis": "HYP-0010",
        "status": final_status,
        "n_participants": n,
        "n_participants_GO": n_go,
        "fraction_participants_GO": fraction_go,
        "GO_threshold_rmse_reduction": GO_THRESHOLD_RMSE_REDUCTION,
        "results_per_participant": results_per_participant,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output_path = Path(__file__).parent / "e2_results.json"

    # DATA_BLOCKED path
    blocked_result = {
        "experiment": "E2",
        "hypothesis": "HYP-0010",
        "status": "DATA_BLOCKED",
        "reason": (
            "No public dataset identified providing participant-specific regional "
            "tendon CSA (proximal, mid, distal) paired with local strain measurements "
            "and applied tendon force across >=6 independent participants. "
            "Literature population means (Kongsgaard et al.) are NOT substituted "
            "as individual participant data."
        ),
        "missing_variables": [
            "participant_specific_csa_proximal_mm2",
            "participant_specific_csa_mid_mm2",
            "participant_specific_csa_distal_mm2",
            "local_strain_per_region_observed",
            "applied_tendon_force_N",
        ],
        "repositories_searched": [
            "PhysioNet", "Zenodo", "Figshare", "Dryad",
            "OSF", "SimTK/OpenSim", "UMUD", "AddBiomechanics",
        ],
        "pre_registration_locked": True,
        "analysis_ready_when_data_available": True,
    }

    with open(output_path, "w") as f:
        json.dump(blocked_result, f, indent=2)
    print(f"E2_STATUS: DATA_BLOCKED — results written to {output_path}")
