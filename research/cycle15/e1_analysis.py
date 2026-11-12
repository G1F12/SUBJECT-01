#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUBJECT-01 — CYCLE 15: EXPERIMENT E1
Independent Human Functional Strength Validation & Antagonist Co-Activation Transfer Audit

Hypothesis: Measured antagonist muscle activation (biceps femoris / semitendinosus) improves
the cross-subject generalization (LOSO) of active joint torque models relative to simple sEMG.

Pre-registered Models:
  M0: Constant mean baseline (fold-level training mean)
  M1: Linear sEMG model (agonist-only normalized sEMG -> joint torque)
  M2: M4 model from EXP-0045 (agonist sEMG + joint angle + angular velocity)
  M3: Bridge model with proxy co-activation from VL (as implemented in EXP-0046)
  M4: Novel Bridge model with DIRECTLY MEASURED antagonist sEMG

Evaluation Protocol:
  - Leave-One-Subject-Out (LOSO) cross-validation across independent human participants.
  - Evaluation on ACTIVE-ONLY contraction series (quiescent/passive trials excluded).
  - Primary Endpoint: Paired RMSE improvement in fractions of MVC relative to M1 (sEMG).
  - Practical threshold: RMSE_improvement >= 0.02 MVC across >50% of participants with 95% CI > 0.
  - Two distinct calibration regimes:
      Regime A: Completely uncalibrated (pure zero-shot LOSO transfer).
      Regime B: Pre-defined individual calibration (gain scaled by participant MVC).
    Results between Regime A and Regime B must NEVER be pooled.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CYCLE15_DIR = ROOT / "research" / "cycle15"
RESULTS_JSON = CYCLE15_DIR / "e1_results.json"
REPORT_MD = CYCLE15_DIR / "E1_STRENGTH_VALIDATION.md"


def get_pre_registration_protocol() -> Dict[str, Any]:
    """Return locked pre-registration protocol for Experiment E1."""
    return {
        "experiment_id": "EXP-0048",
        "cycle": 15,
        "date_locked": "2026-11-12",
        "hypothesis": "Directly measured antagonist EMG reduces active joint torque prediction RMSE relative to simple sEMG across unseen human participants.",
        "models": {
            "M0": "Fold training mean torque: tau_pred = mean(tau_train)",
            "M1": "Linear sEMG: tau_pred = beta_0 + beta_1 * sEMG_agonist",
            "M2": "M4 Model: tau_pred = beta_0 + beta_1 * sEMG_agonist + beta_2 * angle + beta_3 * velocity",
            "M3": "Bridge Proxy: tau_pred = f_active(sEMG_VL, theta, dtheta) - gamma_proxy(sEMG_VL)",
            "M4": "Bridge Measured Antagonist: tau_pred = f_active(sEMG_agonist, theta, dtheta) - f_antagonist(sEMG_antagonist, theta, dtheta)",
        },
        "primary_endpoint": "Paired RMSE reduction in MVC fractions relative to M1: Delta_RMSE = RMSE(M1) - RMSE(M4)",
        "decision_thresholds": {
            "GO": "Mean Delta_RMSE >= 0.02 MVC with 95% bootstrap CI strictly > 0 and sustained in > 50% of participants",
            "NO_GO": "Mean Delta_RMSE < 0.02 MVC or 95% CI crossing zero",
            "DATA_BLOCKED": "Absence of fully qualified independent human cohort meeting all pre-registration data criteria",
        },
        "calibration_regimes": {
            "Regime_A": "Zero-shot transfer (no subject-level parameters)",
            "Regime_B": "Pre-defined MVC normalization (subject gain anchored to isometric MVC)",
        },
    }


def audit_candidate_cohorts() -> Dict[str, Any]:
    """Audit candidates specifically against E1 required variables."""
    candidates = {
        "Bird_2026_Dryad": {
            "role": "Development set in EXP-0045/EXP-0046",
            "n_participants": 6,
            "has_measured_agonist_emg": True,
            "has_measured_antagonist_emg": False,
            "has_measured_torque": True,
            "has_angle_velocity": True,
            "has_mvc": True,
            "is_independent_validation_cohort": False,
            "status": "DISQUALIFIED_DEVELOPMENT_SET_AND_MISSING_ANTAGONIST",
            "reason": "Bird 2026 was the development cohort for EXP-0045/46. Furthermore, it only instrumented Vastus Lateralis (0 antagonist channels). Proxying gamma from VL yielded NEG-0044 (-0.1148 R^2 vs -0.0528 for sEMG).",
        },
        "Wang_2022_Zenodo": {
            "role": "External locomotion dataset",
            "n_participants": 12,
            "has_measured_agonist_emg": True,
            "has_measured_antagonist_emg": True,
            "has_measured_torque": False,
            "has_angle_velocity": True,
            "has_mvc": False,
            "is_independent_validation_cohort": True,
            "status": "REJECTED_INCOMPATIBLE_TASK_AND_DERIVED_TORQUE",
            "reason": "Wang 2022 records whole-body locomotion (walking/running/squats). Joint moments are derived from inverse dynamics via OpenSim ground reaction forces, not directly measured on a dynamometer load cell. Lacks isolated dynamic knee extension series and MVC normalization.",
        },
        "Sanchez_Sotelo_2014_UCI": {
            "role": "External lower-limb EMG dataset",
            "n_participants": 22,
            "has_measured_agonist_emg": True,
            "has_measured_antagonist_emg": True,
            "has_measured_torque": False,
            "has_angle_velocity": True,
            "has_mvc": False,
            "is_independent_validation_cohort": True,
            "status": "REJECTED_MISSING_TARGET_VARIABLE",
            "reason": "Contains leg extension with RF, VM, BF, ST and knee goniometer, but completely lacks any torque transducer or dynamometer. Predicting torque without ground truth torque is physically impossible.",
        },
    }
    return candidates


def run_e1_audit_and_evaluation() -> Dict[str, Any]:
    """Execute complete E1 audit pipeline."""
    protocol = get_pre_registration_protocol()
    candidates = audit_candidate_cohorts()

    # Determine availability
    qualified = [c for c, d in candidates.items() if d.get("status") == "QUALIFIED"]

    if len(qualified) == 0:
        verdict = "DATA_BLOCKED"
        notes = (
            "No qualified independent human cohort exists in public repositories that simultaneously "
            "provides synchronized dynamometer active knee torque, joint angle, angular velocity, "
            "raw agonist EMG, raw antagonist EMG, and participant MVC calibration. "
            "Per SUBJECT-01 integrity rules, synthetic antagonist signals and circular reuse of "
            "development data (Bird 2026) are strictly prohibited. Experiment E1 is DATA_BLOCKED."
        )
    else:
        verdict = "INCONCLUSIVE"
        notes = "Qualified cohort found but not evaluated."

    results = {
        "experiment_id": "EXP-0048",
        "title": "E1: Independent Human Functional Strength Validation",
        "protocol": protocol,
        "candidate_audit": candidates,
        "n_qualified_cohorts": len(qualified),
        "status": verdict,
        "decision": verdict,
        "negative_result_ref": "NEG-0045",
        "rationale": notes,
        "historical_benchmark_exp0046": {
            "cohort": "Bird 2026 (active-only, 6 participants, 1844 samples)",
            "mean_loso_r2": {
                "M0_baseline": 0.0,
                "sEMG": -0.05280,
                "Bridge_proxy_gamma": -0.11482,
                "M4_EXP0045": -0.11532,
            },
            "finding": "Coactivation model with VL-derived proxy was inferior to simple sEMG by 0.062 R^2 units (NEG-0044).",
        },
        "unblocking_specifications": {
            "required_instrumentation": "Biodex isokinetic dynamometer + multi-channel Delsys EMG",
            "muscles_required": ["Vastus Lateralis", "Rectus Femoris", "Biceps Femoris", "Semitendinosus"],
            "protocol_required": "Isokinetic knee extension at 60 deg/s and 120 deg/s, passive baseline, MVC ramps",
            "minimum_n": 10,
        },
    }

    CYCLE15_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"E1 results written to {RESULTS_JSON}")
    print(f"Verdict: {verdict}")
    return results


if __name__ == "__main__":
    run_e1_audit_and_evaluation()
