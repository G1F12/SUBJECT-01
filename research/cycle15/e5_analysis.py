#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUBJECT-01 — CYCLE 15: EXPERIMENT E5
Third Independent MTJ Cohort Replication & Myonuclear Transcriptomic Robustness Audit

Pre-Registration Protocol & Data Gate for MTJCore Stage 8:
  - Evaluation of the frozen MTJCore myonuclear transcriptional signature against an
    independent, external human adult musculotendinous junction (MTJ) transcriptomic cohort.

Prior Experimental Evidence (Consolidation Baseline):
  - Stage 5 (E-MTAB-12529): 1,083 / 1,176 concordant directions (92.09%), 3 external donors.
    CRITICAL LIMITATION: Discovery donor 1 contributed 51.2% of myonuclei.
  - Stage 6 (E-MTAB-15400): 0.5818 concordant fraction vs fixed 0.60 threshold.
    VERDICT: NO_CLEAR_CONDITION_ASSOCIATION (NEG-0041). Sex confounded with exercise.
  - Stage 7 (PRIDE Proteomics): Proteomic enrichment p ~= 0.00047, but only 50/216 concordant
    directions in protein space. Fibroblast component unconfirmed.
  CRITICAL: Stages 5, 6, and 7 do NOT constitute three successful replications. Stage 6 FAILED.

Integrity Rules:
  - E-MTAB-12529 is DISQUALIFIED (circular reuse of discovery data).
  - E-MTAB-15400 is DISQUALIFIED (already analyzed and failed in Stage 6).
  - Pre-registration must lock all gene panels, null models, and thresholds before data inspection.
  - RNA direction concordance does NOT equal mechanical tendon/MTJ strength.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CYCLE15_DIR = ROOT / "research" / "cycle15"
RESULTS_JSON = CYCLE15_DIR / "e5_results.json"
REPORT_MD = CYCLE15_DIR / "E5_MTJ_REPLICATION.md"


def get_pre_registration_protocol() -> Dict[str, Any]:
    """Return locked pre-registration protocol for Experiment E5."""
    return {
        "experiment_id": "EXP-0050",
        "cycle": 15,
        "date_locked": "2026-11-12",
        "hypothesis": (
            "The frozen 1,176-gene human myonuclear MTJ transcriptional program maintains directional "
            "concordance (> 60%) in an independent adult human skeletal muscle MTJ-vs-mature contrast."
        ),
        "panel_definition": {
            "source": "MTJCore Frozen Panel (Stage 5 derived from E-MTAB-12529)",
            "n_genes": 1176,
            "anchor_genes": [
                "COL22A1", "ABI3BP", "ABLIM1", "SPARC", "TNC", "ITGB1",
                "LAMB2", "COL6A1", "COL6A2", "COL6A3", "VCL", "PXN", "TLN1"
            ],
            "marker_guard": "Exclusion of top 6 annotation markers to prevent circular clustering bias",
        },
        "statistical_specification": {
            "gene_inclusion_criterion": "Count >= 10 in >= 2 donors in held-out dataset",
            "missing_marker_handling": "Excluded from test; if coverage < 50%, declare INCONCLUSIVE",
            "donor_independence_strategy": "Donor-paired generalized linear model (edgeR QLF / DESeq2)",
            "null_distribution": "Correlation-preserving gene-set permutation (accounting for inter-gene covariance)",
            "primary_endpoint": "Concordant direction fraction S_rep = N_concordant / N_tested",
            "fixed_decision_threshold": 0.60,
            "decision_rules": {
                "REPLICATED": "S_rep >= 0.60 AND p_null < 0.05 with >= 3 independent donors",
                "NOT_REPLICATED": "S_rep < 0.60 OR p_null >= 0.05",
                "INCONCLUSIVE": "Gene panel coverage < 50% or donor N < 3",
                "DATA_BLOCKED": "Absence of fully independent public human MTJ transcriptomic dataset",
            },
        },
    }


def audit_candidate_cohorts() -> Dict[str, Any]:
    """Audit candidates specifically against E5 required criteria."""
    candidates = {
        "E-MTAB-12529": {
            "name": "Karlsen et al. (2023) — ArrayExpress",
            "sample_type": "Human adult semitendinosus MTJ vs belly snRNA-seq",
            "n_donors": 3,
            "previous_use": "MTJCore Discovery and Stage 5 validation",
            "verdict": "DISQUALIFIED_CIRCULAR_REUSE",
            "reason": "Discovery cohort. Donor 1 provided 51.2% of myonuclei. Reusing discovery data as independent validation is circular.",
        },
        "E-MTAB-15400": {
            "name": "Møbjerg et al. (2025) — ArrayExpress",
            "sample_type": "Human adult vastus lateralis MTJ biopsies snRNA-seq",
            "n_donors": 8,
            "previous_use": "MTJCore Stage 6 loading-context test (EXP-0047, NEG-0041)",
            "verdict": "DISQUALIFIED_ALREADY_EVALUATED_AND_FAILED",
            "reason": "Already evaluated in Stage 6. Result was 0.5818 concordant fraction (< 0.60 threshold). Re-labeling it as a new test is prohibited.",
        },
        "E-MTAB-12530": {
            "name": "Karlsen et al. (2023) 10x Visium — ArrayExpress",
            "sample_type": "Human MTJ spatial transcriptomics",
            "n_donors": 3,
            "previous_use": "None",
            "verdict": "DISQUALIFIED_IDENTICAL_DONORS",
            "reason": "Uses biopsy sections from the exact same 3 donors as E-MTAB-12529 (Copenhagen). Violates donor biological independence.",
        },
        "HRA002803": {
            "name": "Zhao et al. (2022) — GSA-Human (NGDC China)",
            "sample_type": "Human MTJ single-cell transcriptomics",
            "n_donors": 4,
            "previous_use": "None",
            "verdict": "DATA_BLOCKED_CONTROLLED_ACCESS",
            "reason": "Controlled-access repository requiring Data Access Committee (DAC) application and institutional ethics transfer; not accessible via open download.",
        },
        "Jakobsen_2021": {
            "name": "Jakobsen et al. (2021) — AJP-Cell Physiol",
            "sample_type": "Horse and human MTJ bulk RNA-seq",
            "n_donors": "Human hamstring biopsies",
            "previous_use": "None",
            "verdict": "DISQUALIFIED_SAME_LABORATORY_AND_NO_OPEN_ACCESSION",
            "reason": "Same laboratory (Mackey/Kjær, Copenhagen). Raw count matrices were not deposited under a public open repository accession number.",
        },
    }
    return candidates


def run_e5_audit_and_evaluation() -> Dict[str, Any]:
    """Execute complete E5 audit pipeline."""
    protocol = get_pre_registration_protocol()
    candidates = audit_candidate_cohorts()

    qualified = [c for c, d in candidates.items() if d.get("verdict") == "QUALIFIED"]

    if len(qualified) == 0:
        verdict = "DATA_BLOCKED"
        notes = (
            "No qualified third independent human adult MTJ transcriptomic dataset exists in open "
            "repositories. E-MTAB-12529 is discovery; E-MTAB-15400 failed Stage 6 (0.5818 < 0.60); "
            "E-MTAB-12530 has identical donors; HRA002803 is controlled-access. "
            "Experiment E5 is DATA_BLOCKED."
        )
    else:
        verdict = "INCONCLUSIVE"
        notes = "Qualified cohort found but pending analysis."

    results = {
        "experiment_id": "EXP-0050",
        "title": "E5: Third Independent Human MTJ Cohort Replication",
        "protocol": protocol,
        "candidate_audit": candidates,
        "n_qualified_cohorts": len(qualified),
        "status": verdict,
        "decision": verdict,
        "negative_result_ref": "NEG-0047",
        "rationale": notes,
        "prior_replications_audit": {
            "Stage_5": {
                "accession": "E-MTAB-12529",
                "donors": 3,
                "concordance": "1,083 / 1,176 (92.09%)",
                "vulnerability": "Donor 1 contributed 51.2% of myonuclei",
            },
            "Stage_6": {
                "accession": "E-MTAB-15400",
                "donors": 8,
                "concordance": "0.5818 (FAILED fixed 0.60 threshold)",
                "verdict": "NO_CLEAR_CONDITION_ASSOCIATION (NEG-0041)",
                "confounder": "Biological sex confounded with training condition",
            },
            "Stage_7": {
                "accession": "PXD029307 / PXD072245",
                "modality": "Proteomics",
                "concordance": "50 / 216 concordant directions",
                "verdict": "PARTIAL_PROTEOMIC_ENRICHMENT_FIBROBLAST_UNCONFIRMED",
            },
        },
        "biological_boundaries": [
            "RNA direction replication does NOT equal mechanical force transmission.",
            "Transcriptional presence of COL22A1/ABI3BP does NOT prove tendon tensile strength.",
            "No evidence that MTJ myonuclear program can be artificially induced without pathological fibrosis.",
        ],
    }

    CYCLE15_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"E5 results written to {RESULTS_JSON}")
    print(f"Verdict: {verdict}")
    return results


if __name__ == "__main__":
    run_e5_audit_and_evaluation()
