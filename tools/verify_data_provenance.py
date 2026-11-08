#!/usr/bin/env python3
"""
SUBJECT-01 — Automated Data Provenance & Evidence Gate
Verification tool to enforce rigorous empirical integrity across all cycles:
1. Validates schema and required metadata fields for empirical datasets.
2. Enforces allowed data_type enum: RAW_HUMAN_OBSERVATION, LITERATURE_REPORTED_VALUE, COMPUTATIONAL_SIMULATION, SYNTHETIC.
3. Disallows EXTERNALLY_VALIDATED or EMPIRICALLY_VALIDATED statuses for synthetic data or zero real observations.
4. Scans validation scripts to ensure no synthetic generators pretend to be empirical ground truth (y_true).
5. Returns exit code 0 on success, non-zero on failure.
"""

import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_DATA_TYPES = {
    'RAW_HUMAN_OBSERVATION',
    'LITERATURE_REPORTED_VALUE',
    'COMPUTATIONAL_SIMULATION',
    'SYNTHETIC'
}

DISALLOWED_EMPIRICAL_STATUSES_FOR_SYNTHETIC = [
    'EXTERNALLY_VALIDATED',
    'EMPIRICALLY_VALIDATED',
    'INDEPENDENT_HUMAN_DATA_TESTED',
    'EMPIRICAL_RAW_DATA_VERIFIED',
    'BIOPHYSICALLY_CONFIRMED'
]

MANDATORY_DATASET_FIELDS = [
    'source_id',
    'dataset_id',
    'source_url_or_doi',
    'data_type',
    'source_file',
    'sha256',
    'number_of_real_observations',
    'independent_participants_n',
    'measurement_units',
    'validation_status'
]

def audit_dataset_provenance_records():
    problems = []
    
    # 1. Audit Cycle 9 empirical datasets registry file
    c9_datasets_file = ROOT / 'research' / 'empirical_recruitment_2026_11_08' / 'empirical_datasets_cycle9.json'
    if not c9_datasets_file.is_file():
        problems.append(f"Missing empirical datasets file: {c9_datasets_file}")
        return problems
    
    try:
        data = json.loads(c9_datasets_file.read_text(encoding='utf-8'))
    except Exception as e:
        problems.append(f"Failed to parse {c9_datasets_file}: {e}")
        return problems
    
    # Check audits inside empirical_datasets_cycle9.json
    records_to_check = []
    if 'rehman_2024_audit' in data:
        records_to_check.append(('rehman_2024_audit', data['rehman_2024_audit']))
    if 'hug_2021_audit' in data:
        records_to_check.append(('hug_2021_audit', data['hug_2021_audit']))
        
    for name, rec in records_to_check:
        for field in MANDATORY_DATASET_FIELDS:
            if field not in rec:
                problems.append(f"Dataset {name} missing mandatory field: {field}")
        
        dtype = rec.get('data_type')
        if dtype not in ALLOWED_DATA_TYPES:
            problems.append(f"Dataset {name} invalid data_type: '{dtype}'. Allowed: {ALLOWED_DATA_TYPES}")
            
        status = rec.get('validation_status', '')
        if dtype == 'SYNTHETIC':
            for forbidden in DISALLOWED_EMPIRICAL_STATUSES_FOR_SYNTHETIC:
                if forbidden in status.upper() and f"NOT_{forbidden}" not in status.upper():
                    problems.append(f"Dataset {name} cannot have empirical status '{status}' with data_type 'SYNTHETIC'")
            
        n_obs = rec.get('number_of_real_observations', 0)
        if n_obs == 0:
            for forbidden in DISALLOWED_EMPIRICAL_STATUSES_FOR_SYNTHETIC:
                if forbidden in status.upper() and f"NOT_{forbidden}" not in status.upper():
                    problems.append(f"Dataset {name} claims empirical status '{status}' but has 0 real observations")
            
    return problems

def audit_registry_experiments():
    problems = []
    exp_file = ROOT / 'registry' / 'experiments.json'
    if not exp_file.is_file():
        problems.append("Missing registry/experiments.json")
        return problems
        
    try:
        experiments = json.loads(exp_file.read_text(encoding='utf-8'))
    except Exception as e:
        problems.append(f"Failed to parse registry/experiments.json: {e}")
        return problems
        
    for exp in experiments:
        exp_id = exp.get('id', '')
        status = exp.get('status', '').upper()
        dtype = exp.get('data_type', '')
        
        # Check rule: synthetic data cannot claim positive empirical validation
        if dtype == 'SYNTHETIC' or 'synthetic' in exp.get('model', '').lower():
            for forbidden in DISALLOWED_EMPIRICAL_STATUSES_FOR_SYNTHETIC:
                if forbidden in status and f"NOT_{forbidden}" not in status:
                    problems.append(f"Experiment {exp_id} has synthetic model/data but claims empirical status '{status}'")
                    
        # Check specific Cycle 9 experiments
        if exp_id == 'EXP-0040':
            if 'SYNTHETIC_DEMONSTRATION' not in status:
                problems.append(f"EXP-0040 must be classified as SYNTHETIC_DEMONSTRATION, got '{status}'")
            if 'BLOCKED_PENDING_RAW_DATA' not in status and 'NOT_EMPIRICALLY_VALIDATED' not in status:
                problems.append(f"EXP-0040 must document empirical blocker, got '{status}'")
                
        if exp_id == 'EXP-0038':
            if 'COMPUTATIONAL_SIMULATION' not in status and 'SYNTHETIC' not in status:
                problems.append(f"EXP-0038 must be classified as COMPUTATIONAL_SIMULATION_HYPOTHESIS, got '{status}'")
                
    return problems

def audit_validation_scripts():
    problems = []
    
    # Search for validation scripts in research directories
    validation_scripts = list(ROOT.glob('research/**/validation_*.py'))
    
    for script_path in validation_scripts:
        content = script_path.read_text(encoding='utf-8')
        rel_path = script_path.relative_to(ROOT)
        
        # Rule: If a script uses random generators (np.random) or analytical formulas to make target data (y_true),
        # it must NOT claim to be real empirical validation, and must explicitly document its synthetic nature.
        has_random_gen = bool(re.search(r'np\.random|RandomState|random\.', content))
        claims_empirical_validation = bool(re.search(r'validation_status\s*=\s*["\'](EMPIRICAL|INDEPENDENT_HUMAN|EXTERNALLY_VALIDATED)', content))
        
        if has_random_gen and claims_empirical_validation:
            problems.append(f"Validation script {rel_path} uses random generators but claims empirical validation status!")
            
        # Ensure that if generate_* functions exist with random generators, they are explicitly named synthetic
        for match in re.finditer(r'def\s+(generate_\w+)\s*\(', content):
            func_name = match.group(1)
            # Find body of function up to next def or 30 lines
            start_pos = match.start()
            func_snippet = content[start_pos:start_pos+1500]
            if ('np.random' in func_snippet or 'RandomState' in func_snippet) and 'synthetic' not in func_name.lower():
                problems.append(f"Validation script {rel_path} contains generator function '{func_name}' using random numbers without 'synthetic' in name")
                
    return problems

def run_evidence_gate():
    print("=" * 60)
    print("SUBJECT-01 — DATA PROVENANCE & EVIDENCE GATE")
    print("=" * 60)
    
    all_problems = []
    
    p1 = audit_dataset_provenance_records()
    all_problems.extend(p1)
    if not p1:
        print("[PASS] Empirical dataset schema and metadata completeness verified.")
    else:
        for p in p1:
            print(f"[FAIL] {p}")
            
    p2 = audit_registry_experiments()
    all_problems.extend(p2)
    if not p2:
        print("[PASS] Experiment registry statuses aligned with empirical vs synthetic reality.")
    else:
        for p in p2:
            print(f"[FAIL] {p}")
            
    p3 = audit_validation_scripts()
    all_problems.extend(p3)
    if not p3:
        print("[PASS] Validation scripts inspected: No fake empirical ground truths detected.")
    else:
        for p in p3:
            print(f"[FAIL] {p}")
            
    if all_problems:
        print("\nDATA PROVENANCE GATE FAILED with", len(all_problems), "violations.")
        sys.exit(1)
    else:
        print("\nDATA PROVENANCE GATE PASSED: All scientific provenance invariants satisfied.")
        sys.exit(0)

if __name__ == '__main__':
    run_evidence_gate()
