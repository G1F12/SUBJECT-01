"""
Unit tests for Research Cycle 18:
Oxford MTJ Data Recovery, Independent Replication & Scientific Integrity Audit.
"""

import json
from pathlib import Path
import pytest
import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def test_cycle18_artifacts_exist():
    required = [
        'research/cycle18/SCIENTIFIC_CORRECTIONS.md',
        'research/cycle18/OXFORD_DATA_ACCESS_AUDIT.md',
        'research/cycle18/OXFORD_CELL_POPULATIONS.md',
        'research/cycle18/MTJCORE_FROZEN_PROTOCOL.md',
        'research/cycle18/MTJ_THIRD_REPLICATION.md',
        'research/cycle18/MTJ_REPLICATION_RESULTS.json',
        'research/cycle18/HYP0013_ASSESSMENT.md',
        'research/cycle18/HYP0013_EVALUATION.json',
        'research/cycle18/SCIENTIFIC_NOVELTY.md',
        'research/cycle18/FUNCTIONAL_IMPACT.md',
        'research/cycle18/INDEPENDENT_VERIFICATION.md',
        'research/cycle18/data_manifest.json',
        'research/cycle18/OXFORD_AUDIT_SUMMARY.json'
    ]
    for rel in required:
        p = ROOT / rel
        assert p.is_file(), f"Missing required Cycle 18 artifact: {rel}"

def test_oxford_atlas_cell_counts():
    audit_json = json.loads((ROOT / 'research/cycle18/OXFORD_AUDIT_SUMMARY.json').read_text('utf-8'))
    assert audit_json['cell_counts']['total_cells'] == 64862
    assert audit_json['cell_counts']['skeletal_muscle_cells']['total'] == 22146
    assert len(audit_json['cell_counts']['donors']) == 5
    assert 'MSK1556' in audit_json['cell_counts']['donors']

def test_oxford_discovery_identity_and_circularity():
    rep_res = json.loads((ROOT / 'research/cycle18/MTJ_REPLICATION_RESULTS.json').read_text('utf-8'))
    assert rep_res['replication_status'] == 'INVALID_CIRCULAR_EVALUATION'
    assert rep_res['decision'] == 'STOP_NO_ADDED_SCIENTIFIC_VALUE'

def test_hyp0013_evaluation_and_donor_consistency():
    hyp13 = json.loads((ROOT / 'research/cycle18/HYP0013_EVALUATION.json').read_text('utf-8'))
    assert hyp13['verdict'] == 'NOT_SUPPORTED_AS_ORIGINAL_DISCOVERY'
    col22_fib = hyp13['genes']['COL22A1']['fibroblast']
    assert col22_fib['donor_consistency'] == 0.60
    assert col22_fib['in_signature'] is False

def test_registry_consistency_cycle18():
    hyps = json.loads((ROOT / 'registry/hypotheses.json').read_text('utf-8'))
    hyp_map = {h['id']: h for h in hyps}
    
    assert hyp_map['HYP-0008']['status'] == 'verified'
    assert 'EXP-0054' in hyp_map['HYP-0008']['notes']
    
    assert hyp_map['HYP-0010']['status'] == 'unverified'
    assert 'patellar tendon' in hyp_map['HYP-0010']['title'].lower()
    
    assert hyp_map['HYP-0013']['status'] == 'rejected'

    exps = json.loads((ROOT / 'registry/experiments.json').read_text('utf-8'))
    exp_ids = {e['id'] for e in exps}
    assert 'EXP-0057' in exp_ids
    assert 'EXP-0058' in exp_ids

    fnds = json.loads((ROOT / 'registry/findings.json').read_text('utf-8'))
    fnd_ids = {f['id'] for f in fnds}
    assert 'FND-0058' in fnd_ids
    assert 'FND-0059' in fnd_ids

    negs = json.loads((ROOT / 'registry/negative_results.json').read_text('utf-8'))
    neg_ids = {n['id'] for n in negs}
    assert 'NEG-0054' in neg_ids
    assert 'NEG-0055' in neg_ids

def test_statistical_corrections_cycle18():
    e1_res = json.loads((ROOT / 'research/cycle17/E1_RESULTS.json').read_text('utf-8'))
    contrast = e1_res['algorithms']['Ridge']['contrasts']['F3_minus_F0_agonist_incremental']
    assert abs(contrast['paired_ttest_stat'] - (-0.08435)) < 0.001
    assert abs(contrast['paired_ttest_pvalue'] - 0.93366) < 0.001

    p_exact = 2.0 / (6.0 ** 10)
    assert abs(p_exact - 3.30759e-08) < 1e-12
