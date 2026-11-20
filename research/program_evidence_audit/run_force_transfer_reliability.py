"""EXP-0126: Diagnostic evaluation of force model transfer, bias, repeatability and angle transfer on Santos cohort."""
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

EXPECTED_SHA256 = "8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe"


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def compute_icc(matrix: np.ndarray):
    """Compute two-way mixed ICC(3,1) consistency and agreement.
    matrix: shape (n_subjects, k_sessions)
    """
    n, k = matrix.shape
    grand_mean = np.mean(matrix)
    row_means = np.mean(matrix, axis=1)
    col_means = np.mean(matrix, axis=0)

    ss_total = np.sum((matrix - grand_mean) ** 2)
    ss_rows = k * np.sum((row_means - grand_mean) ** 2)
    ss_cols = n * np.sum((col_means - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    df_rows = n - 1
    df_cols = k - 1
    df_error = (n - 1) * (k - 1)

    ms_rows = ss_rows / df_rows
    ms_cols = ss_cols / df_cols
    ms_error = ss_error / df_error

    icc_consistency = (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error)
    icc_agreement = (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error + (k / n) * (ms_cols - ms_error))

    # Within-subject SD
    sw = np.sqrt(np.mean(np.var(matrix, axis=1, ddof=1)))
    cv_percent = (sw / grand_mean) * 100.0

    return {
        "n_subjects": int(n),
        "k_sessions": int(k),
        "icc_3_1_consistency": float(icc_consistency),
        "icc_3_1_agreement": float(icc_agreement),
        "within_subject_sd_N": float(sw),
        "cv_percent": float(cv_percent),
        "grand_mean_N": float(grand_mean),
    }


def main():
    parser = argparse.ArgumentParser(description="EXP-0126 force transfer & repeatability audit.")
    parser.add_argument("xlsx_path", nargs="?", default=str(ROOT / "tmp" / "data_repository_santos.xlsx"))
    args = parser.parse_args()

    xlsx_file = Path(args.xlsx_path)
    if not xlsx_file.exists():
        print(f"File not found: {xlsx_file}", file=sys.stderr)
        sys.exit(1)

    raw_bytes = xlsx_file.read_bytes()
    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if file_sha256 != EXPECTED_SHA256:
        raise ValueError(f"SHA-256 mismatch: expected {EXPECTED_SHA256}, got {file_sha256}")

    wb = openpyxl.load_workbook(xlsx_file, data_only=True, read_only=True)
    ws = wb["Mechanical+EMG"]
    rows = list(ws.values)

    assert rows[1][2] == "PF'", f"Expected column PF', got {rows[1][2]}"

    records = {}
    current_subject = None
    for r in rows[2:]:
        if r[0] is not None:
            current_subject = str(r[0]).strip()
        sess = r[1]
        if sess is not None:
            pf = r[2]
            rfd = r[7]
            if current_subject and isinstance(pf, (int, float)) and pf > 0:
                records.setdefault(current_subject, {})[str(sess).strip()] = {
                    "PF": float(pf),
                    "RFDmax": float(rfd) if isinstance(rfd, (int, float)) else None,
                }

    # W0 baseline forces
    subjects_w0 = sorted([s for s in records if "W0" in records[s]])
    assert len(subjects_w0) == 11, f"Expected 11 subjects with W0, got {len(subjects_w0)}"
    w0_forces = np.array([records[s]["W0"]["PF"] for s in subjects_w0])

    n = len(w0_forces)
    w0_mean = float(np.mean(w0_forces))
    w0_sd = float(np.std(w0_forces, ddof=1))

    # Define candidate models
    loso_mean = (np.sum(w0_forces) - w0_forces) / (n - 1)
    grand_mean = np.full(n, w0_mean)
    fixed_const = np.full(n, 2500.0)

    # Rebuilt EXP-0090 forces
    corrected100 = np.full(n, 2567.0)
    corrected110 = np.full(n, 2976.8)
    corrected140 = np.full(n, 3804.5)

    strategy2_100 = np.full(n, 3130.0)
    strategy2_110 = np.full(n, 3629.6)
    strategy2_140 = np.full(n, 4632.6)

    models = {
        "loso_mean": loso_mean,
        "grand_mean": grand_mean,
        "fixed_const_2500N": fixed_const,
        "corrected_model_100deg": corrected100,
        "corrected_model_110deg": corrected110,
        "corrected_model_140deg": corrected140,
        "strategy2_chain_100deg": strategy2_100,
        "strategy2_chain_110deg": strategy2_110,
        "strategy2_chain_140deg": strategy2_140,
    }

    metrics = {}
    for name, pred in models.items():
        errors = np.abs(pred - w0_forces)
        signed_errors = pred - w0_forces
        sq_errors = (pred - w0_forces) ** 2
        metrics[name] = {
            "predicted_force_N": float(np.mean(pred)),
            "mae_N": float(np.mean(errors)),
            "rmse_N": float(np.sqrt(np.mean(sq_errors))),
            "bias_N": float(np.mean(signed_errors)),
            "relative_mae_percent": float(np.mean(errors / w0_forces) * 100.0),
        }

    # Bootstrap paired comparisons vs LOSO mean
    rng = np.random.default_rng(20261121)
    boot_indices = rng.integers(0, n, size=(10000, n))

    comparisons = {}
    baseline_err = np.abs(loso_mean - w0_forces)
    for name in ["grand_mean", "fixed_const_2500N", "corrected_model_100deg", "corrected_model_110deg", "corrected_model_140deg"]:
        model_err = np.abs(models[name] - w0_forces)
        diff = baseline_err - model_err  # positive means model has lower MAE (improvement)
        boot_diffs = np.mean(diff[boot_indices], axis=1)
        ci95 = np.quantile(boot_diffs, [0.025, 0.975]).tolist()
        comparisons[f"loso_mean_minus_{name}"] = {
            "paired_mae_difference_N": float(np.mean(diff)),
            "ci95_N": ci95,
            "favors": "model" if ci95[0] > 0 else ("baseline" if ci95[1] < 0 else "inconclusive"),
        }

    # Angle transfer penalty
    angle_transfer = {
        "100deg_to_110deg_test": {
            "target_experimental_angle": "~110 deg",
            "model_configured_angle": "100 deg",
            "model_force_N": 2567.0,
            "bias_N": metrics["corrected_model_100deg"]["bias_N"],
            "mae_N": metrics["corrected_model_100deg"]["mae_N"],
        },
        "110deg_to_110deg_test": {
            "target_experimental_angle": "~110 deg",
            "model_configured_angle": "110 deg",
            "model_force_N": 2976.8,
            "bias_N": metrics["corrected_model_110deg"]["bias_N"],
            "mae_N": metrics["corrected_model_110deg"]["mae_N"],
        },
        "140deg_to_110deg_test": {
            "target_experimental_angle": "~110 deg",
            "model_configured_angle": "140 deg",
            "model_force_N": 3804.5,
            "bias_N": metrics["corrected_model_140deg"]["bias_N"],
            "mae_N": metrics["corrected_model_140deg"]["mae_N"],
        },
        "angle_sensitivity_summary": "Model force increases by +409.8 N from 100° to 110°, and +827.7 N from 110° to 140°. Because experimental mean at ~110° is 2513.6 N, the 100° model fortuitously matches cohort mean (bias +53.4 N), while the matched 110° model has substantial positive bias (+463.2 N, MAE 613.6 N), demonstrating that posture transfer without individual subject geometry calibration introduces severe systematic bias.",
    }

    # Repeatability analysis across sessions
    # 10 subjects have W0, W2, W4, POS
    complete_sub_10 = sorted([s for s in records if all(sess in records[s] for sess in ["W0", "W2", "W4", "POS"])])
    mat_10 = np.array([[records[s][sess]["PF"] for sess in ["W0", "W2", "W4", "POS"]] for s in complete_sub_10])
    icc_all_4 = compute_icc(mat_10)

    # 11 subjects have W0, W4, POS
    complete_sub_11 = sorted([s for s in records if all(sess in records[s] for sess in ["W0", "W4", "POS"])])
    mat_11 = np.array([[records[s][sess]["PF"] for sess in ["W0", "W4", "POS"]] for s in complete_sub_11])
    icc_3_sessions = compute_icc(mat_11)

    # Pairwise adjacent visit stability
    w0_vals = np.array([records[s]["W0"]["PF"] for s in complete_sub_10])
    w2_vals = np.array([records[s]["W2"]["PF"] for s in complete_sub_10])
    w4_vals = np.array([records[s]["W4"]["PF"] for s in complete_sub_10])
    pos_vals = np.array([records[s]["POS"]["PF"] for s in complete_sub_10])

    diff_w2_w0 = w2_vals - w0_vals
    diff_w4_w2 = w4_vals - w2_vals
    diff_pos_w4 = pos_vals - w4_vals

    pairwise_stability = {
        "W2_minus_W0": {
            "mean_diff_N": float(np.mean(diff_w2_w0)),
            "mean_abs_diff_N": float(np.mean(np.abs(diff_w2_w0))),
            "relative_mean_change_percent": float(np.mean(diff_w2_w0 / w0_vals) * 100.0),
        },
        "W4_minus_W2": {
            "mean_diff_N": float(np.mean(diff_w4_w2)),
            "mean_abs_diff_N": float(np.mean(np.abs(diff_w4_w2))),
            "relative_mean_change_percent": float(np.mean(diff_w4_w2 / w2_vals) * 100.0),
        },
        "POS_minus_W4": {
            "mean_diff_N": float(np.mean(diff_pos_w4)),
            "mean_abs_diff_N": float(np.mean(np.abs(diff_pos_w4))),
            "relative_mean_change_percent": float(np.mean(diff_pos_w4 / w4_vals) * 100.0),
        },
    }

    protocol_path = HERE / "FORCE_TRANSFER_RELIABILITY_PROTOCOL.md"
    out = {
        "experiment_id": "EXP-0126",
        "title": "Diagnostic evaluation of force model transfer, bias, repeatability and angle transfer on Santos cohort",
        "epistemic_classification": "DIAGNOSTIC_REUSED_COHORT_AUDIT",
        "source_id": "SRC-0090",
        "source_sha256": file_sha256,
        "protocol_sha256_lf": text_sha256(protocol_path),
        "runner_sha256_lf": text_sha256(Path(__file__)),
        "cohort_baseline_summary": {
            "n_subjects": n,
            "mean_force_N": w0_mean,
            "sd_force_N": w0_sd,
            "min_force_N": float(np.min(w0_forces)),
            "max_force_N": float(np.max(w0_forces)),
        },
        "model_performance_at_w0": metrics,
        "paired_comparisons_vs_loso_mean": comparisons,
        "angle_transfer_evaluation": angle_transfer,
        "longitudinal_repeatability": {
            "four_sessions_10_subjects": icc_all_4,
            "three_sessions_11_subjects": icc_3_sessions,
            "pairwise_adjacent_transitions": pairwise_stability,
        },
        "verdict": {
            "model_advantage_over_baseline": "NOT_ESTABLISHED",
            "angle_transfer_validity": "UNRELIABLE_WITHOUT_SUBJECT_GEOMETRY",
            "task_repeatability": "MODERATE_TO_HIGH_WITHIN_PERSON_STABILITY_BUT_TRAINING_DRIFT_PRESENT",
            "tissue_safety_assessment": "NOT_ASSESSED_FROM_EXTERNAL_FORCE",
            "gate_status": "DATA_BLOCKED_FOR_CONFIRMATORY_FORCE20",
        },
        "limitations": [
            "Cohort previously viewed in EXP-0087, EXP-0088, EXP-0091; diagnostic status only.",
            "Single nominal experimental angle (~110°); no direct 100° or 140° trials in Santos.",
            "Individual body mass, height, segment lengths and COP unrecorded in published table.",
            "Within-day repeated trials unrecorded; longitudinal repeatability confounded by training effect.",
            "Peak force alone does not identify internal patellar tendon force or tissue safety factor.",
        ],
    }

    out_file = HERE / "FORCE_TRANSFER_RELIABILITY_RESULTS.json"
    out_file.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Results written to {out_file}")
    print(json.dumps(out["model_performance_at_w0"], indent=2))
    print("Paired comparisons:", json.dumps(out["paired_comparisons_vs_loso_mean"], indent=2))
    print("Repeatability:", json.dumps(out["longitudinal_repeatability"]["four_sessions_10_subjects"], indent=2))


if __name__ == "__main__":
    main()
