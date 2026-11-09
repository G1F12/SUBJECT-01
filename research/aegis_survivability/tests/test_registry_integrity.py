"""Test suite for AEGIS-01 registry integrity, ID convention, and cross-reference consistency."""

from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parent.parent
REG_DIR = ROOT / "registry"

PREFIXES = {
    "hypotheses.json": "HYP",
    "experiments.json": "EXP",
    "findings.json": "FND",
    "negative_results.json": "NEG",
    "decisions.json": "DEC",
    "issues.json": "ISS",
    "sources.json": "SRC",
    "models.json": "MOD",
}

# Known SUBJECT-01 maximum ID numbers to verify zero collision (as of HEAD 9271a1e)
SUBJECT01_MAX_IDS = {
    "HYP": 8,
    "EXP": 41,
    "FND": 41,
    "NEG": 31,
    "DEC": 15,
    "ISS": 19,
    "SRC": 72,
}


def test_registry_files_exist_and_are_lists():
    for filename in PREFIXES.keys():
        p = REG_DIR / filename
        assert p.is_file(), f"Missing registry file: {filename}"
        data = json.loads(p.read_text("utf-8"))
        assert isinstance(data, list), f"{filename} must be a JSON array"
        assert len(data) > 0, f"{filename} cannot be empty"


def test_id_formatting_and_no_duplicates():
    all_ids = set()
    for filename, prefix in PREFIXES.items():
        data = json.loads((REG_DIR / filename).read_text("utf-8"))
        for item in data:
            item_id = item.get("id")
            assert item_id is not None, f"Missing id in {filename}"
            assert item_id.startswith(f"{prefix}-"), f"Bad prefix for {item_id} in {filename}"
            assert len(item_id) == 8, f"ID must be 8 characters: {item_id}"
            num_part = item_id[4:]
            assert num_part.isdigit(), f"ID suffix must be numeric: {item_id}"
            assert item_id not in all_ids, f"Duplicate ID found: {item_id}"
            all_ids.add(item_id)


def test_zero_collision_with_subject01():
    for filename, prefix in PREFIXES.items():
        if prefix not in SUBJECT01_MAX_IDS:
            continue
        max_sub01 = SUBJECT01_MAX_IDS[prefix]
        data = json.loads((REG_DIR / filename).read_text("utf-8"))
        for item in data:
            num = int(item["id"][4:])
            assert num > max_sub01, (
                f"Collision risk with SUBJECT-01! {item['id']} <= max SUBJECT-01 ID {prefix}-{max_sub01:04d}"
            )


def test_cross_references():
    all_exp_ids = {e["id"] for e in json.loads((REG_DIR / "experiments.json").read_text("utf-8"))}
    all_hyp_ids = {h["id"] for h in json.loads((REG_DIR / "hypotheses.json").read_text("utf-8"))}

    # Findings reference valid experiments
    findings = json.loads((REG_DIR / "findings.json").read_text("utf-8"))
    for f in findings:
        assert f["experiment_id"] in all_exp_ids, f"Finding {f['id']} references unknown experiment {f['experiment_id']}"

    # Negative results reference valid experiments
    negs = json.loads((REG_DIR / "negative_results.json").read_text("utf-8"))
    for n in negs:
        assert n["experiment_id"] in all_exp_ids, f"Negative result {n['id']} references unknown experiment {n['experiment_id']}"

    # Hypotheses reference valid experiments
    hyps = json.loads((REG_DIR / "hypotheses.json").read_text("utf-8"))
    for h in hyps:
        for ref_exp in h.get("related_experiments", []):
            assert ref_exp in all_exp_ids, f"Hypothesis {h['id']} references unknown experiment {ref_exp}"
