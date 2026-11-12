#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SUBJECT-01 Cycle 15: Independent Validation
Verifies artifact integrity, schema conformance, registry updates, and core invariants.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CYCLE15_DIR = REPO_ROOT / "research" / "cycle15"
REGISTRY_DIR = REPO_ROOT / "registry"


def test_cycle15_artifacts_exist():
    """Verify all mandatory Cycle 15 documents and scripts exist."""
    required_files = [
        "DATASET_DISCOVERY.md",
        "dataset_registry.json",
        "E1_STRENGTH_VALIDATION.md",
        "e1_analysis.py",
        "e1_results.json",
        "E2_TENDON_MECHANICS.md",
        "e2_analysis.py",
        "e2_results.json",
        "E5_MTJ_REPLICATION.md",
        "e5_analysis.py",
        "e5_results.json",
        "CROSS_EXPERIMENT_ANALYSIS.md",
        "SCIENTIFIC_NOVELTY.md",
        "PUBLICATION_READINESS.md",
        "CYCLE15_FINAL_REPORT_RU.md",
        "VERIFICATION_REPORT.md",
    ]
    for filename in required_files:
        path = CYCLE15_DIR / filename
        assert path.is_file(), f"Missing required Cycle 15 file: {filename}"
        assert path.stat().st_size > 0, f"File is empty: {filename}"


def test_cycle15_dataset_registry_schema():
    """Verify dataset_registry.json contains valid candidate records for E1, E2, E5."""
    with open(CYCLE15_DIR / "dataset_registry.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["cycle"] == 15
    assert "E1" in data["audited_experiments"]
    assert "E2" in data["audited_experiments"]
    assert "E5" in data["audited_experiments"]
    assert len(data["datasets"]) >= 6
    assert data["experiment_decisions"]["E1"]["status"] == "DATA_BLOCKED"
    assert data["experiment_decisions"]["E2"]["status"] == "DATA_BLOCKED"
    assert data["experiment_decisions"]["E5"]["status"] == "DATA_BLOCKED"


def test_cycle15_experiment_results_json():
    """Verify individual experiment JSON results match DATA_BLOCKED status."""
    for exp_id, filename in [("E1", "e1_results.json"), ("E2", "e2_results.json"), ("E5", "e5_results.json")]:
        with open(CYCLE15_DIR / filename, "r", encoding="utf-8") as f:
            res = json.load(f)
        assert res.get("status") == "DATA_BLOCKED" or res.get("decision") == "DATA_BLOCKED", (
            f"{exp_id} result does not report DATA_BLOCKED: {res}"
        )


def test_cycle15_registries_updated():
    """Verify registry entries for EXP, NEG, FND, and ISS were added sequentially."""
    # Experiments
    with open(REGISTRY_DIR / "experiments.json", "r", encoding="utf-8") as f:
        exps = json.load(f)
    exp_ids = {e["id"] for e in exps}
    assert "EXP-0048" in exp_ids
    assert "EXP-0049" in exp_ids
    assert "EXP-0050" in exp_ids

    # Negative results
    with open(REGISTRY_DIR / "negative_results.json", "r", encoding="utf-8") as f:
        negs = json.load(f)
    neg_ids = {n["id"] for n in negs}
    assert "NEG-0045" in neg_ids
    assert "NEG-0046" in neg_ids
    assert "NEG-0047" in neg_ids

    # Findings
    with open(REGISTRY_DIR / "findings.json", "r", encoding="utf-8") as f:
        fnds = json.load(f)
    fnd_ids = {fn["id"] for fn in fnds}
    assert "FND-0049" in fnd_ids
    assert "FND-0050" in fnd_ids
    assert "FND-0051" in fnd_ids

    # Issues
    with open(REGISTRY_DIR / "issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)
    iss_ids = {i["id"] for i in issues}
    assert "ISS-0023" in iss_ids
    assert "ISS-0024" in iss_ids


def test_core_invariants_preserved():
    """Verify that inviolable project boundaries are maintained in report and state."""
    report_text = (CYCLE15_DIR / "CYCLE15_FINAL_REPORT_RU.md").read_text(encoding="utf-8")
    state_text = (REPO_ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")

    assert "CPE45_EXTERNALLY_VALIDATED = NO" in report_text
    assert "BIOLOGICAL_AUGMENTATION_GO = NO" in report_text
    assert "STRENGTH_PLUS_20_VALIDATED = NO" in report_text

    assert "TARGET-CPE45 = NOT EXTERNALLY VALIDATED" in state_text
    assert "BIOLOGICAL INTERVENTIONS = NO_GO" in state_text
