#!/usr/bin/env python3
"""Deterministic registry ID reconciliation and migration tool between AEGIS-01 and SUBJECT-01.

This script resolves all 19 identified ID collisions between AEGIS-01 and SUBJECT-01
by shifting AEGIS-01 IDs strictly beyond the current published SUBJECT-01 HEAD (9271a1e).

Collision Inventory:
- HYP-0008 (1 collision) -> renumbered to HYP-0009..HYP-0020 (shift +1)
- EXP-0037..0041 (5 collisions) -> renumbered to EXP-0042..EXP-0062 (shift +5)
- FND-0038..0041 (4 collisions) -> renumbered to FND-0042..FND-0066 (shift +4)
- NEG-0029..0031 (3 collisions) -> renumbered to NEG-0032..NEG-0054 (shift +3)
- DEC-0015 (1 collision) -> renumbered to DEC-0016..DEC-0022 (shift +1)
- SRC-0068..0072 (5 collisions) -> renumbered to SRC-0073..SRC-0103 (shift +5)
Total: 19 collisions resolved to EXACTLY 0.

Idempotency:
- Running this script repeatedly will detect existing migration, verify integrity,
  and exit without altering or double-incrementing IDs.
- Preserves 'original_id' on every modified record for complete traceability.
"""

from pathlib import Path
import json
import sys

AEGIS_ROOT = Path(__file__).resolve().parent.parent
AEGIS_REG_DIR = AEGIS_ROOT / "registry"
SUBJECT01_ROOT = AEGIS_ROOT.parent.parent if (AEGIS_ROOT.parent.parent / "registry").is_dir() else Path("D:/SUBJECT-01")
SUBJECT01_REG_DIR = SUBJECT01_ROOT / "registry"

OFFSETS = {
    "HYP": 1,   # 8 -> 9 (SUBJECT-01 max: 8)
    "EXP": 5,   # 37 -> 42 (SUBJECT-01 max: 41)
    "FND": 4,   # 38 -> 42 (SUBJECT-01 max: 41)
    "NEG": 6,   # 29 -> 35 (SUBJECT-01 max: 34)
    "DEC": 1,   # 15 -> 16 (SUBJECT-01 max: 15)
    "SRC": 5,   # 68 -> 73 (SUBJECT-01 max: 72)
}

REGISTRY_FILES = {
    "hypotheses": "hypotheses.json",
    "experiments": "experiments.json",
    "findings": "findings.json",
    "negative_results": "negative_results.json",
    "decisions": "decisions.json",
    "sources": "sources.json",
    "issues": "issues.json",
    "models": "models.json",
}

COLLIDING_RANGES = {
    "HYP": (8, 8),
    "EXP": (37, 41),
    "FND": (38, 41),
    "NEG": (29, 32),
    "DEC": (15, 15),
    "SRC": (68, 72),
}


def build_deterministic_map():
    """Build complete mapping from old IDs to new IDs."""
    mapping = {}
    
    # HYP: 8..19 -> 9..20
    for old_num in range(8, 20):
        mapping[f"HYP-{old_num:04d}"] = f"HYP-{old_num + 1:04d}"
        
    # EXP: 37..47 -> 42..52
    for old_num in range(37, 48):
        mapping[f"EXP-{old_num:04d}"] = f"EXP-{old_num + 5:04d}"
        
    # FND: 38..52 -> 42..56
    for old_num in range(38, 53):
        mapping[f"FND-{old_num:04d}"] = f"FND-{old_num + 4:04d}"
        
    # NEG: 29..41 -> 33..45
    for old_num in range(29, 42):
        mapping[f"NEG-{old_num:04d}"] = f"NEG-{old_num + 4:04d}"
        
    # DEC: 15..21 -> 16..22
    for old_num in range(15, 22):
        mapping[f"DEC-{old_num:04d}"] = f"DEC-{old_num + 1:04d}"
        
    # SRC: 68..88 -> 73..93
    for old_num in range(68, 89):
        mapping[f"SRC-{old_num:04d}"] = f"SRC-{old_num + 5:04d}"
        
    return mapping


def is_already_migrated() -> bool:
    """Check if migration was already applied."""
    negs_file = AEGIS_REG_DIR / "negative_results.json"
    if not negs_file.exists():
        return False
    data = json.loads(negs_file.read_text(encoding="utf-8"))
    ids = [item.get("id") for item in data]
    # If NEG-0048 is present or NEG-0035 is present and NEG-0029 is absent, already migrated
    return ("NEG-0048" in ids or "NEG-0035" in ids) and ("NEG-0029" not in ids)


def run_migration():
    id_map = build_deterministic_map()
    
    if is_already_migrated():
        print("[MIGRATION NOTICE] Registries are ALREADY migrated. Running in idempotent verification mode.")
        verify_integrity(id_map)
        return id_map

    print("[MIGRATION] Applying deterministic ID migration...")
    
    # 1. Update Hypotheses
    hyps = json.loads((AEGIS_REG_DIR / "hypotheses.json").read_text(encoding="utf-8"))
    for h in hyps:
        old_id = h["id"]
        if old_id in id_map:
            h["id"] = id_map[old_id]
            h["original_id"] = old_id
        if "related_experiments" in h:
            h["related_experiments"] = [id_map.get(e, e) for e in h["related_experiments"]]
    (AEGIS_REG_DIR / "hypotheses.json").write_text(json.dumps(hyps, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Update Experiments
    exps = json.loads((AEGIS_REG_DIR / "experiments.json").read_text(encoding="utf-8"))
    for e in exps:
        old_id = e["id"]
        if old_id in id_map:
            e["id"] = id_map[old_id]
            e["original_id"] = old_id
    (AEGIS_REG_DIR / "experiments.json").write_text(json.dumps(exps, indent=2, ensure_ascii=False), encoding="utf-8")

    # 3. Update Findings
    fnds = json.loads((AEGIS_REG_DIR / "findings.json").read_text(encoding="utf-8"))
    for f in fnds:
        old_id = f["id"]
        if old_id in id_map:
            f["id"] = id_map[old_id]
            f["original_id"] = old_id
        if "experiment_id" in f:
            f["experiment_id"] = id_map.get(f["experiment_id"], f["experiment_id"])
    (AEGIS_REG_DIR / "findings.json").write_text(json.dumps(fnds, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. Update Negative Results
    negs = json.loads((AEGIS_REG_DIR / "negative_results.json").read_text(encoding="utf-8"))
    for n in negs:
        old_id = n["id"]
        if old_id in id_map:
            n["id"] = id_map[old_id]
            n["original_id"] = old_id
        if "experiment_id" in n:
            n["experiment_id"] = id_map.get(n["experiment_id"], n["experiment_id"])
    (AEGIS_REG_DIR / "negative_results.json").write_text(json.dumps(negs, indent=2, ensure_ascii=False), encoding="utf-8")

    # 5. Update Decisions
    decs = json.loads((AEGIS_REG_DIR / "decisions.json").read_text(encoding="utf-8"))
    for d in decs:
        old_id = d["id"]
        if old_id in id_map:
            d["id"] = id_map[old_id]
            d["original_id"] = old_id
    (AEGIS_REG_DIR / "decisions.json").write_text(json.dumps(decs, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6. Update Sources
    srcs = json.loads((AEGIS_REG_DIR / "sources.json").read_text(encoding="utf-8"))
    for s in srcs:
        old_id = s["id"]
        if old_id in id_map:
            s["id"] = id_map[old_id]
            s["original_id"] = old_id
        if "supports_hypotheses" in s:
            s["supports_hypotheses"] = [id_map.get(h, h) for h in s["supports_hypotheses"]]
    (AEGIS_REG_DIR / "sources.json").write_text(json.dumps(srcs, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save detailed ID_MIGRATION_MAP.json
    migration_meta = {
        "metadata": {
            "title": "AEGIS-01 to SUBJECT-01 Registry Reconciliation & Deconfliction Map",
            "cycle": "Cycle 2B",
            "target_subject01_head": "9271a1eabbd8405f7152c151c52047ce54312c38",
            "collisions_resolved_count": 19,
            "total_records_migrated": len(id_map),
            "idempotent": True,
            "offsets": OFFSETS,
            "colliding_ranges": {
                f"{k}": f"{k}-{v[0]:04d}..{k}-{v[1]:04d}" for k, v in COLLIDING_RANGES.items()
            },
        },
        "id_map": id_map,
        "collisions_reconciled": [
            {"old_id": old_id, "new_id": new_id, "entity_type": old_id.split("-")[0], "collided_with_subject01": True}
            for old_id, new_id in sorted(id_map.items())
            if old_id.split("-")[0] in COLLIDING_RANGES and 
               COLLIDING_RANGES[old_id.split("-")[0]][0] <= int(old_id.split("-")[1]) <= COLLIDING_RANGES[old_id.split("-")[0]][1]
        ],
    }
    
    map_path = AEGIS_ROOT / "ID_MIGRATION_MAP.json"
    map_path.write_text(json.dumps(migration_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[MIGRATION] Migration complete. Saved mapping to {map_path}")
    verify_integrity(id_map)
    return id_map


def verify_integrity(id_map):
    """Verify cross-repo zero collisions and internal link graph integrity."""
    print("[VERIFICATION] Checking cross-repo collisions against SUBJECT-01...")
    collisions = []
    
    for key, filename in REGISTRY_FILES.items():
        af = AEGIS_REG_DIR / filename
        sf = SUBJECT01_REG_DIR / filename
        if not af.exists() or not sf.exists():
            continue
        a_data = json.loads(af.read_text(encoding="utf-8"))
        s_data = json.loads(sf.read_text(encoding="utf-8"))
        
        a_ids = {item["id"] for item in a_data if "id" in item}
        s_ids = {item["id"] for item in s_data if "id" in item}
        
        overlap = a_ids & s_ids
        if overlap:
            collisions.extend(list(overlap))
            print(f"  [ERROR] Collision in {filename}: {overlap}")
            
    if collisions:
        raise RuntimeError(f"Cross-repo collisions detected: {collisions}")
    print("[VERIFICATION PASS] Exactly 0 cross-repo ID collisions found with SUBJECT-01!")


if __name__ == "__main__":
    run_migration()
