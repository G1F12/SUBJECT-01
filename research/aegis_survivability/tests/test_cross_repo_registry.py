#!/usr/bin/env python3
"""Automated cross-repository registry collision and reconciliation tests.

Validates that AEGIS-01 registries have ZERO collisions with SUBJECT-01 (HEAD 9271a1e),
verifies ID migration map integrity, checks migration idempotency, and confirms graph connectivity.
"""

from pathlib import Path
import json
import pytest
import subprocess
import sys

AEGIS_ROOT = Path(__file__).resolve().parent.parent
AEGIS_REG_DIR = AEGIS_ROOT / "registry"
SUBJECT01_ROOT = AEGIS_ROOT.parent.parent if (AEGIS_ROOT.parent.parent / "registry").is_dir() else Path("D:/SUBJECT-01")
SUBJECT01_REG_DIR = SUBJECT01_ROOT / "registry"

COMMON_REGISTRIES = [
    "decisions.json",
    "experiments.json",
    "findings.json",
    "hypotheses.json",
    "issues.json",
    "negative_results.json",
    "sources.json",
]


def test_cross_repo_zero_collisions():
    """Verify that no ID in AEGIS-01 collides with any ID in SUBJECT-01."""
    assert SUBJECT01_REG_DIR.is_dir(), f"SUBJECT-01 registry directory not found at {SUBJECT01_REG_DIR}"
    
    aegis_all_ids = {}
    subject_all_ids = {}
    
    for filename in COMMON_REGISTRIES:
        af = AEGIS_REG_DIR / filename
        sf = SUBJECT01_REG_DIR / filename
        assert af.is_file(), f"Missing AEGIS-01 registry: {filename}"
        assert sf.is_file(), f"Missing SUBJECT-01 registry: {filename}"
        
        a_data = json.loads(af.read_text(encoding="utf-8"))
        s_data = json.loads(sf.read_text(encoding="utf-8"))
        
        for item in a_data:
            if "id" in item:
                aegis_all_ids[item["id"]] = filename
                
        for item in s_data:
            if "id" in item:
                subject_all_ids[item["id"]] = filename
                
    collisions = set(aegis_all_ids.keys()) & set(subject_all_ids.keys())
    assert len(collisions) == 0, f"Found {len(collisions)} cross-repo ID collisions: {sorted(list(collisions))}"


def test_id_migration_map_consistency():
    """Verify ID_MIGRATION_MAP.json exists and accurately reflects renumbering."""
    map_file = AEGIS_ROOT / "ID_MIGRATION_MAP.json"
    assert map_file.is_file(), "Missing ID_MIGRATION_MAP.json"
    
    data = json.loads(map_file.read_text(encoding="utf-8"))
    assert "metadata" in data
    assert "id_map" in data
    assert "collisions_reconciled" in data
    
    assert data["metadata"]["collisions_resolved_count"] == 19
    assert len(data["collisions_reconciled"]) == 19
    
    # Check that each renumbered record in AEGIS has the original_id recorded
    hyps = json.loads((AEGIS_REG_DIR / "hypotheses.json").read_text(encoding="utf-8"))
    for h in hyps:
        if h.get("original_id") and h["original_id"] in data["id_map"]:
            expected_new = data["id_map"][h["original_id"]]
            assert h["id"] == expected_new


def test_migration_idempotency():
    """Verify that executing migrate_registry_ids.py repeatedly does not corrupt or alter IDs."""
    script_path = AEGIS_ROOT / "tools" / "migrate_registry_ids.py"
    res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "ALREADY migrated" in res.stdout
    assert "Exactly 0 cross-repo ID collisions" in res.stdout


def test_internal_reference_graph_integrity():
    """Verify that all cross-references (findings -> exps, negs -> exps, hyps -> exps, sources -> hyps)
    resolve to valid, existing IDs within AEGIS-01.
    """
    exps = {e["id"] for e in json.loads((AEGIS_REG_DIR / "experiments.json").read_text(encoding="utf-8"))}
    hyps = {h["id"] for h in json.loads((AEGIS_REG_DIR / "hypotheses.json").read_text(encoding="utf-8"))}
    
    # Findings reference valid experiments
    for f in json.loads((AEGIS_REG_DIR / "findings.json").read_text(encoding="utf-8")):
        assert f["experiment_id"] in exps, f"Finding {f['id']} references unknown experiment {f['experiment_id']}"
        
    # Negative results reference valid experiments
    for n in json.loads((AEGIS_REG_DIR / "negative_results.json").read_text(encoding="utf-8")):
        assert n["experiment_id"] in exps, f"Negative result {n['id']} references unknown experiment {n['experiment_id']}"
        
    # Hypotheses reference valid experiments
    for h in json.loads((AEGIS_REG_DIR / "hypotheses.json").read_text(encoding="utf-8")):
        for ref_exp in h.get("related_experiments", []):
            assert ref_exp in exps, f"Hypothesis {h['id']} references unknown experiment {ref_exp}"
            
    # Sources reference valid hypotheses
    for s in json.loads((AEGIS_REG_DIR / "sources.json").read_text(encoding="utf-8")):
        for ref_hyp in s.get("supports_hypotheses", []):
            assert ref_hyp in hyps, f"Source {s['id']} references unknown hypothesis {ref_hyp}"
