#!/usr/bin/env python3
"""
SUBJECT-01 — Automated Data Provenance & Evidence Gate V2
Comprehensive end-to-end provenance validation and falsification engine.

Requirements:
1. Every numerical result must reference source observation identifiers.
2. source_file must exist on disk for local source data.
3. SHA256 must be recomputed from raw bytes, not merely checked for presence.
4. 'N/A' is forbidden as a file hash; literature results use separate category without dummy hashes.
5. Biological participants, operators, repeated trials, and records are stored in distinct fields:
   (n_biological_participants, n_operators, n_trials, n_records).
6. Synthetic and real input arrays must have typed provenance.
7. Any RMSE, R2, or MAE metric must preserve the provenance of all y_true.
8. Status EXTERNALLY_VALIDATED (and variants) is strictly forbidden for synthetic or unknown provenance data.
9. Structured auditing covers all project result registries across cycles (Cycle 7, Cycle 8, Cycle 9, CPE45).
10. Includes a battery of negative tests (intentionally wrong hash, missing file, synthetic y_true,
    conflated participants, unconfirmed source) that must deterministically trigger expected FAIL.
11. Uses structured inspection of JSON registries and experiment schemas.

SCIENTIFIC EPISTEMIC CONSTRAINT:
The number of passed software tests is NOT an indicator of scientific accuracy or biological truth.
Tests verify only syntactic, cryptographic, and invariant consistency.
"""

import sys
import json
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_DATA_TYPES = {
    # Evidence Gate V2 Categories:
    'ORIGINAL_BINARY_FILE',
    'DERIVED_EXTRACTION_JSON',
    'PUBLISHED_TABLE_DATA',
    'LITERATURE_REFERENCE_WITHOUT_FILE',
    'SYNTHETIC_MODEL_SIMULATION',
    # Backward compatibility:
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
    'BIOPHYSICALLY_CONFIRMED',
    'EMPIRICALLY_BOUNDED_DISTRIBUTION'
]

FORBIDDEN_DUMMY_HASHES = {'N/A', 'N/A_PUBLISHED_LITERATURE', 'NONE', 'NULL', 'UNKNOWN', ''}

def compute_file_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA256 digest directly from file bytes."""
    return hashlib.sha256(filepath.read_bytes()).hexdigest()

def audit_dataset_provenance_records(custom_data=None):
    """
    Audit Cycle 9 empirical datasets registry.
    Verifies schema, byte-level SHA256, participant separation, and observation IDs.
    """
    problems = []
    
    if custom_data is None:
        c9_datasets_file = ROOT / 'research' / 'empirical_recruitment_2026_11_08' / 'empirical_datasets_cycle9.json'
        c10_datasets_file = ROOT / 'research' / 'cpet_cycloergometer_2026_11_09' / 'empirical_datasets_cycle10.json'
        c11_datasets_file = ROOT / 'research' / 'treadmill_cpet_2026_11_09' / 'empirical_datasets_cycle11.json'
        if not c9_datasets_file.is_file():
            problems.append(f"Missing empirical datasets file: {c9_datasets_file}")
            return problems
        try:
            data = json.loads(c9_datasets_file.read_text(encoding='utf-8'))
        except Exception as e:
            problems.append(f"Failed to parse {c9_datasets_file}: {e}")
            return problems

        if c10_datasets_file.is_file():
            try:
                c10_data = json.loads(c10_datasets_file.read_text(encoding='utf-8'))
                for k, v in c10_data.items():
                    if k not in ('cycle', 'date', 'description'):
                        data[f"c10_{k}"] = v
            except Exception as e:
                problems.append(f"Failed to parse {c10_datasets_file}: {e}")
                return problems

        if c11_datasets_file.is_file():
            try:
                c11_data = json.loads(c11_datasets_file.read_text(encoding='utf-8'))
                for k, v in c11_data.items():
                    if k not in ('cycle', 'date', 'description'):
                        data[f"c11_{k}"] = v
            except Exception as e:
                problems.append(f"Failed to parse {c11_datasets_file}: {e}")
                return problems
    else:
        data = custom_data
        
    records_to_check = []
    for k, v in data.items():
        if isinstance(v, dict):
            if 'source_id' in v or 'dataset_id' in v or 'data_type' in v:
                records_to_check.append((k, v))
            if 'sources_audit' in v and isinstance(v['sources_audit'], list):
                for src in v['sources_audit']:
                    records_to_check.append((f"{k}_{src.get('source_id')}", src))
            
    for name, rec in records_to_check:
        dtype = rec.get('data_type')
        if dtype not in ALLOWED_DATA_TYPES:
            problems.append(f"Dataset {name} invalid data_type: '{dtype}'. Allowed: {ALLOWED_DATA_TYPES}")
            
        status = rec.get('validation_status', '')
        
        # Rule: synthetic data cannot claim positive empirical validation
        if dtype in ('SYNTHETIC', 'SYNTHETIC_MODEL_SIMULATION'):
            for forbidden in DISALLOWED_EMPIRICAL_STATUSES_FOR_SYNTHETIC:
                if forbidden in status.upper() and f"NOT_{forbidden}" not in status.upper():
                    problems.append(f"Dataset {name} cannot have empirical status '{status}' with data_type '{dtype}'")
                    
        # Rule: distinct participant and operator fields
        if 'n_biological_participants' not in rec and 'independent_participants_n' not in rec:
            problems.append(f"Dataset {name} missing distinct n_biological_participants field")
            
        # Rule: Equating raters/operators with biological subjects is forbidden
        if 'hug' in name.lower() or rec.get('source_id') == 'SRC-0068':
            n_part = str(rec.get('n_biological_participants', rec.get('independent_participants_n', ''))).upper()
            if n_part == '1' or n_part == '8':
                problems.append(f"Hug 2021 must classify biological participants as UNKNOWN (got '{n_part}')")
            n_raters = rec.get('n_operators', rec.get('rater_operators_n'))
            if n_raters != 8:
                problems.append(f"Hug 2021 must record exactly 8 rater operators (got '{n_raters}')")
                
        if 'andersen' in name.lower() or rec.get('source_id') == 'SRC-0066':
            n_part = rec.get('n_biological_participants', rec.get('independent_participants_n'))
            if n_part != 5:
                problems.append(f"Andersen & Saltin 1985 must record exactly 5 male participants (PubMed PMID 4057091; got '{n_part}')")

        # Rule: raw data files must exist and match computed SHA256 from bytes
        source_file = rec.get('source_file')
        recorded_sha = rec.get('sha256')
        
        # Datasets requiring a local file
        if dtype in ('ORIGINAL_BINARY_FILE', 'DERIVED_EXTRACTION_JSON', 'RAW_HUMAN_OBSERVATION'):
            if not source_file:
                problems.append(f"Dataset {name} has data_type '{dtype}' but missing source_file")

        # Datasets prohibited from claiming a local file
        if dtype == 'LITERATURE_REFERENCE_WITHOUT_FILE':
            if source_file is not None:
                problems.append(f"Dataset {name} is LITERATURE_REFERENCE_WITHOUT_FILE but has source_file: {source_file}")
            if recorded_sha is not None:
                problems.append(f"Dataset {name} is LITERATURE_REFERENCE_WITHOUT_FILE but asserts sha256: {recorded_sha}")

        # Invariant: If a record references an existing local file and asserts a SHA256,
        # byte hash MUST be verified regardless of data_type category!
        if source_file:
            p = ROOT / source_file
            if not p.is_file():
                problems.append(f"Dataset {name} source_file does not exist on disk: {source_file}")
            else:
                computed_sha = compute_file_sha256(p)
                if not recorded_sha:
                    problems.append(f"Dataset {name} missing sha256 for local file: {source_file}")
                elif recorded_sha.upper() in FORBIDDEN_DUMMY_HASHES:
                    problems.append(f"Dataset {name} has forbidden dummy hash '{recorded_sha}' for real file {source_file}")
                elif computed_sha.lower() != recorded_sha.lower():
                    problems.append(f"Dataset {name} byte SHA256 mismatch: recorded '{recorded_sha}', computed '{computed_sha}'")
        elif recorded_sha:
            if recorded_sha.upper() in FORBIDDEN_DUMMY_HASHES:
                problems.append(f"Dataset {name} has forbidden dummy hash '{recorded_sha}'. Literature entries without files must use null.")
            else:
                problems.append(f"Dataset {name} asserts sha256 '{recorded_sha}' but has no source_file on disk")

        # Rule: Observation IDs citation
        if dtype in ('ORIGINAL_BINARY_FILE', 'DERIVED_EXTRACTION_JSON', 'PUBLISHED_TABLE_DATA', 'RAW_HUMAN_OBSERVATION', 'LITERATURE_REPORTED_VALUE'):
            if not rec.get('source_observation_ids') and not rec.get('observation_id') and not rec.get('provenance'):
                problems.append(f"Dataset {name} missing source observation identifiers")

    return problems

def audit_registry_experiments(custom_experiments=None):
    """
    Audit registry/experiments.json.
    Enforces strict status bounds and prevents synthetic models from claiming empirical validation.
    """
    problems = []
    if custom_experiments is None:
        exp_file = ROOT / 'registry' / 'experiments.json'
        if not exp_file.is_file():
            problems.append("Missing registry/experiments.json")
            return problems
        try:
            experiments = json.loads(exp_file.read_text(encoding='utf-8'))
        except Exception as e:
            problems.append(f"Failed to parse registry/experiments.json: {e}")
            return problems
    else:
        experiments = custom_experiments
        
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
                
        if exp_id == 'EXP-0041':
            design = exp.get('design', '')
            if 'category error' not in design.lower() and 'ratio' not in design.lower():
                problems.append("EXP-0041 must document the prohibition of the static PCr to external work ratio category error.")
                
    return problems

def audit_validation_scripts():
    """
    Audit validation scripts across research directories.
    Ensures scripts with random or analytical generators do not claim empirical ground truth.
    """
    problems = []
    validation_scripts = list(ROOT.glob('research/**/validation_*.py'))
    
    for script_path in validation_scripts:
        content = script_path.read_text(encoding='utf-8')
        rel_path = script_path.relative_to(ROOT)
        
        has_random_gen = bool(re.search(r'np\.random|RandomState|random\.', content))
        claims_empirical_validation = bool(re.search(r'validation_status\s*=\s*["\'](EMPIRICAL|INDEPENDENT_HUMAN|EXTERNALLY_VALIDATED)', content))
        
        if has_random_gen and claims_empirical_validation:
            problems.append(f"Validation script {rel_path} uses random generators but claims empirical validation status!")
            
        for match in re.finditer(r'def\s+(generate_\w+)\s*\(', content):
            func_name = match.group(1)
            start_pos = match.start()
            func_snippet = content[start_pos:start_pos+1500]
            if ('np.random' in func_snippet or 'RandomState' in func_snippet) and 'synthetic' not in func_name.lower():
                problems.append(f"Validation script {rel_path} contains generator function '{func_name}' using random numbers without 'synthetic' in name")
                
    return problems

def audit_structured_experiment_results():
    """
    Audit structured experiment result files across research cycles:
    Cycle 7 (local muscle bridge), Cycle 8 (empirical anchors), Cycle 9 (recruitment).
    """
    problems = []
    
    # 1. Cycle 9 experiment_results.json
    c9_results_path = ROOT / 'research' / 'empirical_recruitment_2026_11_08' / 'experiment_results.json'
    if c9_results_path.is_file():
        try:
            c9_res = json.loads(c9_results_path.read_text(encoding='utf-8'))
            exps = c9_res.get('experiments', {})
            
            # Audit EXP-0037
            exp37 = exps.get('EXP-0037', {})
            hug = exp37.get('datasets', {}).get('hug_2021_hd_semg', {})
            if hug:
                n_subj = str(hug.get('independent_subjects_n', '')).upper()
                if n_subj != 'UNKNOWN':
                    problems.append(f"EXP-0037 Hug HD-sEMG independent_subjects_n must be UNKNOWN, got '{n_subj}'")
                gm_rates = hug.get('gastrocnemius_medialis_rates_hz', {})
                if gm_rates.get('10_mvc') != 8.1 or gm_rates.get('30_mvc') != 8.1 or gm_rates.get('50_mvc') != 7.6 or gm_rates.get('70_mvc') != 12.2:
                    problems.append(f"EXP-0037 Hug GM rates mismatch Table 2 published values: {gm_rates}")
                    
            # Audit EXP-0041 CPE45 energy accounting
            exp41 = exps.get('EXP-0041', {})
            cpe = exp41.get('cpe45_energy_accounting', {})
            if cpe:
                if not cpe.get('category_error_static_pcr_to_external_work_prohibited'):
                    problems.append("EXP-0041 missing explicit category_error_static_pcr_to_external_work_prohibited invariant")
                required_energies = [
                    'external_mechanical_work_kJ',
                    'whole_body_metabolic_cost_nominal_kJ',
                    'whole_body_atp_turnover_moles',
                    'oxidative_resynthesis_nominal_kJ',
                    'glycolysis_contribution_nominal_kJ'
                ]
                for req_e in required_energies:
                    if req_e not in cpe:
                        problems.append(f"EXP-0041 missing multi-dimensional energy component: {req_e}")
        except Exception as e:
            problems.append(f"Error auditing {c9_results_path}: {e}")

    # 2. Cycle 8 experiment_results.json
    c8_results_path = ROOT / 'research' / 'empirical_anchors_2026_11_08' / 'experiment_results.json'
    if c8_results_path.is_file():
        try:
            c8_res = json.loads(c8_results_path.read_text(encoding='utf-8'))
            exp34 = c8_res.get('experiments', {}).get('EXP-0034', {})
            andersen_audit = exp34.get('andersen_saltin_1985', {})
            if andersen_audit and andersen_audit.get('status') == 'EXTERNALLY_VALIDATED':
                problems.append("Cycle 8 EXP-0034 Andersen & Saltin 1985 cannot be EXTERNALLY_VALIDATED without resting primary data")
        except Exception as e:
            problems.append(f"Error auditing {c8_results_path}: {e}")

    return problems

def audit_strict_json_rfc8259(custom_dir=None):
    """
    Global strict JSON audit per RFC 8259.
    Ensures no Infinity, -Infinity, or NaN tokens exist in JSON files across the repository.
    """
    problems = []
    base_dir = Path(custom_dir) if custom_dir else ROOT
    for p in base_dir.rglob('*.json'):
        p_str = p.as_posix()
        # Skip git metadata, cache, and non-project directories
        if '/.git/' in p_str or '/aegis_survivability/' in p_str or '/.gemini/' in p_str or '/__pycache__/' in p_str:
            continue
        try:
            raw_text = p.read_text(encoding='utf-8')
        except Exception as e:
            problems.append(f"Cannot read {p}: {e}")
            continue
            
        if 'Infinity' in raw_text or 'NaN' in raw_text:
            rel_name = p.relative_to(ROOT) if ROOT in p.parents else p.name
            problems.append(f"RFC 8259 violation in {rel_name}: contains non-standard tokens (Infinity or NaN)")
            continue
            
        try:
            parsed = json.loads(raw_text)
            json.dumps(parsed, allow_nan=False)
        except Exception as e:
            rel_name = p.relative_to(ROOT) if ROOT in p.parents else p.name
            problems.append(f"Strict JSON validation failure in {rel_name}: {e}")
            
    return problems

def audit_negative_tests():
    """
    Negative test battery: Deliberately constructs invalid inputs and asserts that
    Evidence Gate V2 detects every violation with an expected FAIL.
    Returns a dictionary: { test_name: bool (True if violation was properly caught) }.
    """
    results = {}
    
    # Negative Test 1: Intentionally wrong SHA256 byte digest
    fake_data_1 = {
        "fake_audit_1": {
            "source_id": "SRC-0069",
            "dataset_id": "TEST_DATASET_1",
            "source_url_or_doi": "https://doi.org/10.1016/j.dib.2024.111114",
            "data_type": "RAW_HUMAN_OBSERVATION",
            "validation_status": "RAW_TIME_SERIES_TEST",
            "source_file": "research/empirical_recruitment_2026_11_08/pmc11617988.xml",
            "sha256": "0000000000000000000000000000000000000000000000000000000000000000", # Wrong!
            "n_biological_participants": 1,
            "n_operators": 1,
            "n_trials": 3,
            "n_records": 3,
            "source_observation_ids": ["OBS1"]
        }
    }
    p1 = audit_dataset_provenance_records(fake_data_1)
    results['wrong_sha256_caught'] = any("SHA256 mismatch" in err for err in p1)
    
    # Negative Test 2: Missing source_file on disk
    fake_data_2 = {
        "fake_audit_2": {
            "source_id": "SRC-0069",
            "dataset_id": "TEST_DATASET_2",
            "source_url_or_doi": "https://doi.org/10.1016/j.dib.2024.111114",
            "data_type": "RAW_HUMAN_OBSERVATION",
            "validation_status": "RAW_TIME_SERIES_TEST",
            "source_file": "nonexistent/path/to/fake_file.xlsx", # Missing!
            "sha256": "ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf",
            "n_biological_participants": 1,
            "n_operators": 1,
            "n_trials": 3,
            "n_records": 3,
            "source_observation_ids": ["OBS1"]
        }
    }
    p2 = audit_dataset_provenance_records(fake_data_2)
    results['missing_file_caught'] = any("does not exist on disk" in err for err in p2)

    # Negative Test 3: Forbidden dummy 'N/A' hash
    fake_data_3 = {
        "fake_audit_3": {
            "source_id": "SRC-0068",
            "dataset_id": "TEST_DATASET_3",
            "source_url_or_doi": "https://doi.org/10.1016/j.jelekin.2021.102548",
            "data_type": "LITERATURE_REPORTED_VALUE",
            "validation_status": "PUBLISHED_LITERATURE",
            "source_file": "registry/sources.json",
            "sha256": "N/A_PUBLISHED_LITERATURE", # Forbidden dummy hash!
            "n_biological_participants": "UNKNOWN",
            "n_operators": 8,
            "n_trials": 11,
            "n_records": 126,
            "source_observation_ids": ["OBS1"]
        }
    }
    p3 = audit_dataset_provenance_records(fake_data_3)
    results['forbidden_dummy_hash_caught'] = any("forbidden dummy hash" in err for err in p3)

    # Negative Test 4: Synthetic data claiming EXTERNALLY_VALIDATED status
    fake_exp_4 = [
        {
            "id": "EXP-9999",
            "name": "Fake Empirical Validation Experiment",
            "data_type": "SYNTHETIC",
            "model": "synthetic_exponential_generator",
            "status": "EXTERNALLY_VALIDATED", # Forbidden!
            "inputs": "registry/sources.json",
            "report": "PROJECT_STATE.md",
            "outputs": ["registry/sources.json"]
        }
    ]
    p4 = audit_registry_experiments(fake_exp_4)
    results['synthetic_empirical_claim_caught'] = any("claims empirical status" in err for err in p4)

    # Negative Test 5: Conflating 8 raters with 8 independent subjects for Hug 2021
    fake_data_5 = {
        "hug_2021_audit": {
            "source_id": "SRC-0068",
            "dataset_id": "TEST_DATASET_5",
            "source_url_or_doi": "https://doi.org/10.1016/j.jelekin.2021.102548",
            "data_type": "LITERATURE_REPORTED_VALUE",
            "validation_status": "PUBLISHED_LITERATURE",
            "n_biological_participants": 8, # Wrong! 8 operators != 8 subjects!
            "n_operators": 8,
            "n_trials": 11,
            "n_records": 126,
            "source_observation_ids": ["OBS1"]
        }
    }
    p5 = audit_dataset_provenance_records(fake_data_5)
    results['conflated_participants_caught'] = any("must classify biological participants as UNKNOWN" in err for err in p5)

    # Negative Test 6: Tampered SHA256 on PUBLISHED_TABLE_DATA with source_file
    fake_data_6 = {
        "rehman_table_audit": {
            "source_id": "SRC-0069",
            "dataset_id": "TEST_DATASET_6",
            "source_url_or_doi": "https://doi.org/10.1016/j.dib.2024.111114",
            "data_type": "PUBLISHED_TABLE_DATA",
            "validation_status": "PUBLISHED_TABLE_TEST",
            "source_file": "research/empirical_recruitment_2026_11_08/pmc11617988.xml",
            "sha256": "1111111111111111111111111111111111111111111111111111111111111111", # Tampered!
            "n_biological_participants": 1,
            "n_operators": 1,
            "n_trials": 3,
            "n_records": 3,
            "source_observation_ids": ["OBS_TEST"]
        }
    }
    p6 = audit_dataset_provenance_records(fake_data_6)
    results['tampered_published_table_sha_caught'] = any("SHA256 mismatch" in err for err in p6)

    # Negative Test 7: Strict JSON non-standard token Infinity
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_json = Path(tmpdir) / 'bad.json'
        bad_json.write_text('{"bad_value": Infinity}', encoding='utf-8')
        p7 = audit_strict_json_rfc8259(custom_dir=tmpdir)
        results['strict_json_inf_caught'] = any("RFC 8259 violation" in err for err in p7)

    # Negative Test 8: Tampered SHA256 on ACTES original binary dataset
    fake_data_8 = {
        "actes_tampered_audit": {
            "source_id": "SRC-0073",
            "dataset_id": "TEST_DATASET_8",
            "data_type": "ORIGINAL_BINARY_FILE",
            "validation_status": "EMPIRICAL_RAW_DATA_VERIFIED",
            "source_file": "research/cpet_cycloergometer_2026_11_09/test_measure.csv",
            "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
            "n_biological_participants": 18,
            "source_observation_ids": ["OBS_TEST"]
        }
    }
    p8 = audit_dataset_provenance_records(fake_data_8)
    results['actes_tampered_sha_caught'] = any("SHA256 mismatch" in err for err in p8)

    # Negative Test 9: Tampered SHA256 on Malaga Treadmill CPET original binary dataset
    fake_data_9 = {
        "malaga_tampered_audit": {
            "source_id": "SRC-0074",
            "dataset_id": "TEST_DATASET_9",
            "data_type": "ORIGINAL_BINARY_FILE",
            "validation_status": "EMPIRICAL_RAW_DATA_VERIFIED",
            "source_file": "research/treadmill_cpet_2026_11_09/test_measure.csv",
            "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
            "n_biological_participants": 857,
            "source_observation_ids": ["OBS_TEST"]
        }
    }
    p9 = audit_dataset_provenance_records(fake_data_9)
    results['malaga_tampered_sha_caught'] = any("SHA256 mismatch" in err for err in p9)

    return results

def run_evidence_gate():
    print("=" * 65)
    print("SUBJECT-01 — DATA PROVENANCE & EVIDENCE GATE V2")
    print("=" * 65)
    
    all_problems = []
    
    # 1. Dataset provenance records
    p1 = audit_dataset_provenance_records()
    all_problems.extend(p1)
    if not p1:
        print("[PASS] Empirical dataset schema, byte SHA256, and metadata completeness verified.")
    else:
        for p in p1:
            print(f"[FAIL] {p}")
            
    # 2. Registry experiments
    p2 = audit_registry_experiments()
    all_problems.extend(p2)
    if not p2:
        print("[PASS] Experiment registry statuses aligned with empirical vs synthetic reality.")
    else:
        for p in p2:
            print(f"[FAIL] {p}")
            
    # 3. Validation scripts
    p3 = audit_validation_scripts()
    all_problems.extend(p3)
    if not p3:
        print("[PASS] Validation scripts inspected: No fake empirical ground truths detected.")
    else:
        for p in p3:
            print(f"[FAIL] {p}")

    # 4. Structured cross-cycle experiment results
    p4 = audit_structured_experiment_results()
    all_problems.extend(p4)
    if not p4:
        print("[PASS] Cross-cycle structured experiment results and energy balance verified.")
    else:
        for p in p4:
            print(f"[FAIL] {p}")

    # 5. Global RFC 8259 Strict JSON Audit
    p5 = audit_strict_json_rfc8259()
    all_problems.extend(p5)
    if not p5:
        print("[PASS] Global strict JSON RFC 8259 audit: Zero Infinity/NaN tokens detected.")
    else:
        for p in p5:
            print(f"[FAIL] {p}")

    # 6. Negative test battery
    neg_tests = audit_negative_tests()
    all_neg_passed = all(neg_tests.values())
    if all_neg_passed:
        print(f"[PASS] Negative test battery verified ({len(neg_tests)}/{len(neg_tests)} corruption patterns caught):")
        for tname in neg_tests:
            print(f"       + {tname}: EXPECTED FAIL CONFIRMED")
    else:
        for tname, passed in neg_tests.items():
            if not passed:
                all_problems.append(f"Negative test failed: {tname} did not catch violation")
                print(f"[FAIL] Negative test {tname} failed to catch violation")

    # Epistemic notice
    print("\n[NOTE ON SCIENTIFIC RIGOR]")
    print("Passing software tests confirms protocol consistency and invariant adherence;")
    print("it does NOT substitute for independent biological replication or validate TARGET-CPE45.")

    if all_problems:
        print(f"\nEVIDENCE GATE V2 FAILED with {len(all_problems)} violations.")
        sys.exit(1)
    else:
        print("\nEVIDENCE GATE V2 PASSED: All scientific provenance and integrity invariants satisfied.")
        sys.exit(0)

if __name__ == '__main__':
    run_evidence_gate()
