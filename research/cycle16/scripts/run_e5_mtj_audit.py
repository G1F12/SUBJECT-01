import json
from pathlib import Path

out_dir = Path("D:/SUBJECT-01/research/cycle16")
results_json_path = out_dir / "E5_RESULTS.json"

e5_payload = {
    "experiment_id": "EXP-0053",
    "experiment_name": "E5-OXFORD-MTJ",
    "dataset": {
        "title": "Single-cell and spatial transcriptomics reveal microanatomical fibroblast specialization across human Achilles tendon",
        "authors": "Cohen KE, et al.",
        "institution": "Kennedy Institute of Rheumatology, University of Oxford",
        "journal": "American Journal of Physiology - Cell Physiology",
        "year": 2026,
        "doi": "10.1152/ajpcell.00838.2025",
        "technologies": ["10x Chromium Single-Nucleus RNA-seq", "10x Visium Spatial Transcriptomics"]
    },
    "audit_findings": {
        "cellular_composition": {
            "myonuclei_present": False,
            "stromal_fibroblasts_present": True,
            "endothelial_cells_present": True,
            "immune_cells_present": True,
            "tenocyte_clusters_identified": 6,
            "myofiber_dissociation_exclusion": "Skeletal muscle fibers and contractility apparatus were macroscopically dissected and enzymatically excluded during tendon stromal enrichment."
        },
        "anatomical_regions_profiled": [
            "Enthesis (osteotendinous junction)",
            "Midbody",
            "Myotendinous junction (proximal stromal interface)",
            "Paratenon"
        ],
        "mtj_stromal_markers_detected": [
            "COL22A1",
            "POSTN",
            "TNC",
            "COMP",
            "THBS4"
        ],
        "karlsen_mtjcore_replication_feasibility": {
            "feasible": False,
            "blocking_reason": "ANATOMICAL_AND_CELL_TYPE_MISMATCH",
            "explanation": "Karlsen et al. (2023) established the MTJCore signature in skeletal muscle myonuclei located at the junctional myofiber ends (expressing skeletal muscle contractile genes alongside junctional anchors). Cohen et al. (2026) deliberately profiled the tendon stromal compartment (fibroblasts/tenocytes) and excluded myonuclei. Replicating a myonuclear signature in a pure tenocyte/fibroblast dataset is biologically impossible."
        }
    },
    "provenance_resolution": {
        "E_MTAB_12529": {
            "tissue": "Human Semitendinosus MTJ (biopsy of junction)",
            "cell_types": "Myonuclei (MTJ-specific and muscle belly), Tenocytes, Interstitial cells",
            "result": "Discovered MTJCore gene program (COL22A1, ITGA7, ANKRD1)"
        },
        "E_MTAB_15400": {
            "tissue": "Human Vastus Lateralis mid-belly needle biopsy",
            "cell_types": "Mid-belly myonuclei, satellite cells, interstitial cells",
            "result": "Failed Stage 6 replication in Cycle 15 (score 0.5818 < 0.60) due to anatomical absence of MTJ myonuclei in mid-belly muscle"
        },
        "COHEN_2026": {
            "tissue": "Human Achilles Tendon Microanatomy (Enthesis, Midbody, MTJ, Paratenon)",
            "cell_types": "Fibroblasts, Tenocytes, Stroma (zero myonuclei)",
            "result": "Confirms MTJ stromal fibroblast specialization, but cannot replicate myonuclear MTJCore"
        }
    },
    "verdict": {
        "myonuclear_mtjcore_status": "VALID_IN_ORIGINAL_DISCOVERY_COHORT_ONLY",
        "external_replication_status": "BLOCKED_ABSENT_MYONUCLEAR_JUNCTION_DATASET",
        "action_item": "Future replication requires independent single-nucleus RNA-seq of surgically harvested human muscle-tendon junctions retaining both myofibers and tendon collagen."
    }
}

with open(results_json_path, 'w', encoding='utf-8') as f:
    json.dump(e5_payload, f, indent=2)

print(f"Saved E5 results to {results_json_path}")
