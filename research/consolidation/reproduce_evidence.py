"""Read-only verification of consolidated evidence and the existing Bird benchmark."""
import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def external_evidence(drive_root, manifest):
    paths = {}
    for name, record in manifest["external_artifacts"].items():
        path = drive_root / record["path"]
        if sha256(path) != record["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {path}")
        paths[name] = path

    correspondence = read_tsv(paths["mtj_correspondence"])
    concordant = sum(row["direction_concordant"] == "True" for row in correspondence)
    replication = read_json(paths["mtj_enrichment"])
    if len(correspondence) != replication["overlap_total"] or not math.isclose(
        concordant / len(correspondence), replication["direction_concordance"]
    ):
        raise ValueError("MTJ correspondence and enrichment disagree")

    camera = read_tsv(paths["mtj_camera"])
    loading, = read_tsv(paths["mtj_loading"])
    myonuclear, = read_tsv(paths["mtj_myoproteome"])
    fibroblast, = read_tsv(paths["mtj_fibroproteome"])
    coverage = read_tsv(paths["gate_coverage"])
    usable = sum(row["usable_for_cross_study_comparison"] == "YES" for row in coverage)
    engineered = [
        row for row in read_tsv(paths["gate_samples"])
        if row["dataset"] == "PXD072245" and row["condition"].startswith("3DBP-")
    ]
    if not engineered:
        raise ValueError("Missing engineered sample metadata")
    primary = read_json(paths["soma_metrics"])["primary"]
    controls = read_json(paths["soma_controls"])["controls"]

    return {
        "FND-0047": {
            "concordant": concordant,
            "overlap": len(correspondence),
            "biological_n": replication["biological_n_donors"],
            "S_rep": replication["S_rep"],
            "gene_label_p": replication["primary_empirical_p"],
            "camera_expected_tail_bh": {
                row["component"]: float(row["expected_direction_bh_fdr_two_components"])
                for row in camera
            },
        },
        "NEG-0041": {
            "biological_n": int(loading["biological_n"]),
            "overlap": int(loading["signature_overlap"]),
            "direction_concordance": float(loading["direction_concordance"]),
            "threshold": manifest["loading_direction_threshold"],
            "classification": loading["interpretation_category"],
        },
        "FND-0048": {
            row["compartment"]: {
                "overlap": int(row["primary_overlap_total"]),
                "concordant": int(row["direction_concordant"]),
                "gene_label_p": float(row["primary_empirical_p"]),
                "classification": row["programme_label"],
            }
            for row in (myonuclear, fibroblast)
        },
        "NEG-0042": {
            "usable": usable,
            "total": len(coverage),
            "minimum": math.ceil(len(coverage) * manifest["gate_minimum_fraction"]),
            "coverage": usable / len(coverage),
            "engineered_columns": len(engineered),
            "engineered_columns_documented_independent": sum(
                row["biological_replicate"] == "YES" for row in engineered
            ),
            "decision": paths["gate_decision"].read_text(encoding="utf-8-sig").splitlines()[0],
        },
        "NEG-0043": {
            "model_mse": primary["mse"],
            "global_mean_mse": controls["global_target_mean"]["mse"],
            "mean_delta_mse": controls["global_mean_delta"]["mse"],
            "decision": read_json(paths["soma_decision"])["readiness_decision"],
        },
    }


def bird_evidence():
    sys.path.insert(0, str(ROOT))
    from research.cycle13_decision_experiment.functional_force_bridge import FunctionalForceBridge

    engine = FunctionalForceBridge()
    if not engine.verify_cryptographic_digest():
        raise ValueError("Bird dynamic knee SHA-256 mismatch")
    results = {}
    for condition in ("all", "active_only"):
        run = engine.evaluate_loso_cross_validation(condition)
        models = {}
        for model, values in run["models_summary"].items():
            models[model] = {
                metric: values[metric]
                for metric in ("mean_fold_r2", "pooled_r2", "pooled_rmse", "fold_r2_values")
            }
        results[condition] = {
            "observations": run["total_observations_evaluated"],
            "subjects": run["held_out_subjects_count"],
            "models": models,
        }
    scenarios = engine.simulate_augmentation_and_tendon_stress()
    results["model_only"] = {
        name: {key: row[key] for key in (
            "net_torque_gain_percent", "tendon_stress_MPa", "safety_factor", "cos_pennation"
        )}
        for name, row in scenarios.items()
    }
    return results


def verify(expected, actual, path="results"):
    """Require exact structure and tolerate platform-level floating point roundoff."""
    if isinstance(expected, dict) and isinstance(actual, dict) and expected.keys() == actual.keys():
        for key, value in expected.items():
            verify(value, actual[key], f"{path}.{key}")
    elif isinstance(expected, list) and isinstance(actual, list) and len(expected) == len(actual):
        for index, value in enumerate(expected):
            verify(value, actual[index], f"{path}[{index}]")
    elif isinstance(expected, float) and isinstance(actual, (int, float)):
        if not math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-10):
            raise ValueError(f"{path}: expected {expected}, got {actual}")
    elif expected != actual:
        raise ValueError(f"{path}: expected {expected}, got {actual}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external-root", type=Path, help="Root containing original research projects")
    parser.add_argument("--bird", action="store_true", help="Rerun the existing Bird benchmark")
    parser.add_argument("--malaga", action="store_true", help="Rerun the existing Malaga comparison")
    args = parser.parse_args()
    if args.external_root is None and not (args.bird or args.malaga):
        parser.error("select --external-root, --bird, or --malaga")
    expected = read_json(HERE / "evidence_results.json")
    if args.external_root is not None:
        manifest = read_json(HERE / "evidence_inputs.json")
        verify(expected["external"], external_evidence(args.external_root, manifest))
        print("PASS: external checksums and five linked evidence results")
    if args.bird:
        verify(expected["bird"], bird_evidence())
        print("PASS: Bird all-condition and active-only LOSO plus scenario arithmetic")
    if args.malaga:
        sys.path.insert(0, str(ROOT))
        from tools import evaluate_malaga_treadmill as malaga

        malaga.verify_malaga_sha256()
        tests = malaga.load_malaga_dataset()["tests"]
        folds = malaga.get_group_kfold_splits(tests, n_splits=5)
        comparison = malaga.run_cross_validation_evaluation(tests, folds, is_grouped=True)
        transfer = comparison["ad_hoc_cycling_transfer_summary"]
        m4 = comparison["M4_dynamic_allometric_summary"]
        canonical = read_json(malaga.TREADMILL_RESULTS_JSON)["cross_modality_transfer_barrier"]
        expected_transfer = canonical["ad_hoc_cycling_transfer_result"]
        verify(expected_transfer["classification"], transfer["status"])
        verify(expected_transfer["rmse_ml_min"], transfer["rmse_mean"])
        verify(expected_transfer["rmse_penalty_vs_m4_ml_min"], transfer["rmse_mean"] - m4["rmse_mean"])
        print("PASS: Malaga subject-grouped ad hoc transfer failure (NEG-0037)")


if __name__ == "__main__":
    main()
