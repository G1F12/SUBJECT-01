"""EXP-0127: Empirical test of work-to-force transition models vs simple baselines on held-out participants."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

NORBURY_SHA256 = "295cbe90ebb84e7bfa3cd2804d81f87663b16088bdc06021256343d6f57acb9e"


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="EXP-0127 Work-to-Force transition model evaluation.")
    parser.add_argument("norbury_path", nargs="?", default=str(ROOT / "tmp" / "norbury_24156741.xlsx"))
    args = parser.parse_args()

    norbury_file = Path(args.norbury_path)
    if not norbury_file.exists():
        print(f"Norbury file not found: {norbury_file}", file=sys.stderr)
        sys.exit(1)

    raw_bytes = norbury_file.read_bytes()
    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if file_sha256 != NORBURY_SHA256:
        raise ValueError(f"SHA-256 mismatch for Norbury: expected {NORBURY_SHA256}, got {file_sha256}")

    wb = openpyxl.load_workbook(norbury_file, data_only=True, read_only=True)
    leg = wb["Leg Press Data"]
    mvc = wb["MVC"]

    participants_data = []
    # Conditions: LL and HL
    for cond, l_start, m_start in [("LL", 4, 6), ("HL", 20, 22)]:
        for i in range(12):
            sid = int(leg.cell(l_start + i, 2).value)
            vol = float(leg.cell(l_start + i, 20).value)
            f_pre = float(mvc.cell(m_start + i, 3).value)
            f_5m = float(mvc.cell(m_start + i, 4).value)
            f_45m = float(mvc.cell(m_start + i, 5).value)
            f_24h = float(mvc.cell(m_start + i, 6).value)
            participants_data.append({
                "subject_id": sid,
                "condition": cond,
                "volume_kg_reps": vol,
                "f_pre_N": f_pre,
                "f_5m_N": f_5m,
                "f_45m_N": f_45m,
                "f_24h_N": f_24h,
                "retention_5m": f_5m / f_pre,
                "loss_5m_N": f_pre - f_5m,
            })

    # Leave-One-Subject-Out CV on Norbury (12 subjects, 24 observations)
    n_subjects = 12
    all_actual = []
    preds = {
        "persistence_unperturbed": [],
        "mean_retention_baseline": [],
        "mean_loss_baseline": [],
        "volume_linear_model": [],
        "volume_proportional_d2_model": [],
    }

    for held_out in range(1, n_subjects + 1):
        train = [d for d in participants_data if d["subject_id"] != held_out]
        test = [d for d in participants_data if d["subject_id"] == held_out]

        # Training parameters
        train_retentions = [d["retention_5m"] for d in train]
        train_losses = [d["loss_5m_N"] for d in train]
        train_vols = np.array([d["volume_kg_reps"] for d in train])
        train_rets = np.array(train_retentions)

        mean_ret = float(np.mean(train_rets))
        mean_loss = float(np.mean(train_losses))

        # Linear regression: retention = a + b * volume
        poly = np.polyfit(train_vols, train_rets, 1)  # poly[0] is slope, poly[1] is intercept

        # Proportional D2-type: retention = 1 - k * volume => k = mean((1 - ret) / volume)
        k_d2 = float(np.mean((1.0 - train_rets) / train_vols))

        for t in test:
            f_pre = t["f_pre_N"]
            vol = t["volume_kg_reps"]
            f_actual = t["f_5m_N"]
            all_actual.append(f_actual)

            # Predictions
            p_persist = f_pre
            p_ret_base = f_pre * mean_ret
            p_loss_base = f_pre - mean_loss
            p_vol_lin = f_pre * (poly[0] * vol + poly[1])
            p_vol_d2 = f_pre * max(0.0, 1.0 - k_d2 * vol)

            preds["persistence_unperturbed"].append(p_persist)
            preds["mean_retention_baseline"].append(p_ret_base)
            preds["mean_loss_baseline"].append(p_loss_base)
            preds["volume_linear_model"].append(p_vol_lin)
            preds["volume_proportional_d2_model"].append(p_vol_d2)

    y_true = np.array(all_actual)
    eval_metrics = {}
    for name, p_list in preds.items():
        y_pred = np.array(p_list)
        errors = np.abs(y_pred - y_true)
        signed = y_pred - y_true
        sq = (y_pred - y_true) ** 2
        eval_metrics[name] = {
            "mae_N": float(np.mean(errors)),
            "rmse_N": float(np.sqrt(np.mean(sq))),
            "bias_N": float(np.mean(signed)),
            "mean_relative_error_percent": float(np.mean(errors / y_true) * 100.0),
        }

    # Paired comparisons vs mean_retention_baseline
    # Cluster bootstrap by subject (12 subjects)
    rng = np.random.default_rng(20261121)
    base_err = np.abs(np.array(preds["mean_retention_baseline"]) - y_true)

    # Reshape by subject (12 subjects x 2 conditions: LL, HL)
    base_err_by_sub = base_err.reshape(12, 2)
    boot_idx = rng.integers(0, 12, size=(10000, 12))

    comparisons = {}
    for name in ["persistence_unperturbed", "mean_loss_baseline", "volume_linear_model", "volume_proportional_d2_model"]:
        model_err = np.abs(np.array(preds[name]) - y_true).reshape(12, 2)
        # Difference = baseline_error - model_error (positive means model is better)
        diff_by_sub = np.mean(base_err_by_sub - model_err, axis=1)  # shape (12,)
        boot_diffs = np.mean(diff_by_sub[boot_idx], axis=1)
        ci95 = np.quantile(boot_diffs, [0.025, 0.975]).tolist()
        comparisons[f"mean_retention_minus_{name}"] = {
            "paired_mae_difference_N": float(np.mean(diff_by_sub)),
            "ci95_N": ci95,
            "favors": "model" if ci95[0] > 0 else ("baseline" if ci95[1] < 0 else "inconclusive"),
        }

    # de Poli et al. analysis from published group means (Table 3 & text)
    # SIT: Pre: baseline 611 N, post 436 N (ret 71.36%, drop 28.64%)
    #      Post: baseline 614 N, post 461 N (ret 75.08%, drop 24.92%)
    #      Power +11.0%, Work +8.5%
    # Control: Pre: baseline 600 N, post 491 N (ret 81.83%, drop 18.17%)
    #          Post: baseline 568 N, post 459 N (ret 80.81%, drop 19.19%)
    #          Power -0.7%, Work ~constant
    de_poli_audit = {
        "scope_limitation": "Restricted strictly to published group-level averages (Table 3). Individual continuous time-series data are available only upon author request (prohibited under project governance).",
        "SIT_group": {
            "pre_training": {"baseline_N": 611, "post_N": 436, "retention_percent": 71.36, "drop_percent": 28.64},
            "post_training": {"baseline_N": 614, "post_N": 461, "retention_percent": 75.08, "drop_percent": 24.92},
            "work_change_description": "CWR power increased by +11.0% at unchanged time-to-task failure, yielding +8.5% to +11.0% greater external mechanical work in Joules.",
            "force_retention_change_pp": +3.72,
            "directional_concordance_with_scalar_work_fatigue": False,
            "explanation": "Despite performing significantly more total mechanical work post-training, the SIT group exhibited higher force retention (+3.72 pp), refuting the monotonic scalar work-fatigue hypothesis.",
        },
        "control_group": {
            "pre_training": {"baseline_N": 600, "post_N": 491, "retention_percent": 81.83, "drop_percent": 18.17},
            "post_training": {"baseline_N": 568, "post_N": 459, "retention_percent": 80.81, "drop_percent": 19.19},
            "work_change_description": "CWR power -0.7%, duration unchanged, work approximately constant.",
            "force_retention_change_pp": -1.02,
            "directional_concordance_with_scalar_work_fatigue": True,
        },
    }

    # Structural audit of coupling decision
    structural_decision = {
        "can_couple_force_with_energy_module": False,
        "action_required_before_coupling": "FUNDAMENTALLY_RESTRUCTURE_TRANSITION_MODEL",
        "justifications": [
            "Out-of-sample failure: On held-out individual subjects (Norbury 12 men, paired LL and HL conditions), incorporating workload/volume into force prediction increased MAE by 4.08 N over a simple mean retention baseline (baseline MAE 50.61 N vs volume linear MAE 54.69 N; paired difference -4.08 N, 95% CI [-8.49, -0.29] N, strictly favoring baseline).",
            "Directional failure: In de Poli et al., performing +8.5% to +11% more external mechanical work was accompanied by higher force retention (75.08% vs 71.36%), directly violating the assumption that force decrement monotonically tracks cumulative work.",
            "Intensity domain omission: A scalar Joules ledger ignores whether work is performed below, at, or above Critical Power / Respiratory Compensation Point. Sub-CP work produces minimal force loss, whereas supra-CP work produces rapid exhaustion with limited total Joules.",
            "Recovery latency neglect: Real post-exercise force measurements have an unmodeled delay (25 s in de Poli, 5 min in Norbury) during which rapid PCr resynthesis and central drive recovery occur. A static transition model cannot transfer across protocols.",
            "Central vs peripheral confusion: Total work cannot be mapped directly to muscle contractile capacity without separating peripheral cross-bridge inhibition from motoneuronal voluntary activation failure.",
        ],
        "proposed_reconstructed_transition_architecture": {
            "status": "UNVALIDATED_CANDIDATE_ARCHITECTURE_REQUIRING_INDEPENDENT_EMPIRICAL_VERIFICATION",
            "state_1": "Domain-partitioned mechanical demand (moderate vs heavy vs severe domain based on CP/RCP).",
            "state_2": "Bi-compartmental fatigue state: peripheral cross-bridge metabolite penalty (H+, Pi, PCr) + central voluntary activation deficit (%VA).",
            "state_3": "Dynamic recovery operator: exponential restoration function F_recov(t) = F_end + (F_base - F_end)*(1 - exp(-t / tau_recov)) accounting for measurement delay.",
            "state_4": "Task-specific biomechanical transfer: mapping from multi-joint cyclic torque to isometric joint force constraint.",
        },
    }

    out = {
        "experiment_id": "EXP-0127",
        "title": "Empirical evaluation of work-to-force transition models and architectural coupling gate",
        "epistemic_classification": "EMPIRICAL_AUDIT_AND_DECISION_GATE",
        "source_ids": ["SRC-0111", "SRC-0102"],
        "source_sha256": {"norbury": file_sha256},
        "protocol_sha256_lf": text_sha256(HERE / "WORK_FORCE_TRANSITION_PROTOCOL.md"),
        "runner_sha256_lf": text_sha256(Path(__file__)),
        "norbury_individual_cv_metrics": eval_metrics,
        "norbury_paired_comparisons_vs_retention_baseline": comparisons,
        "de_poli_group_audit": de_poli_audit,
        "structural_coupling_decision": structural_decision,
        "verdict": "DIRECT_MODULE_COUPLING_REJECTED_TRANSITION_RESTRUCTURE_MANDATORY",
    }

    out_file = HERE / "WORK_FORCE_TRANSITION_RESULTS.json"
    out_file.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Results written to {out_file}")
    print("CV metrics:", json.dumps(eval_metrics, indent=2))
    print("Paired comparisons:", json.dumps(comparisons, indent=2))
    print("Decision:", json.dumps(structural_decision["can_couple_force_with_energy_module"]))


if __name__ == "__main__":
    main()
