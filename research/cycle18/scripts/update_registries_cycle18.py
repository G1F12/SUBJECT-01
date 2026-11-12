"""
Update Registries for Cycle 18 with exact validate_repository.py schema.
SUBJECT-01.
"""

import json
import os

def update_registries():
    # 1. Update hypotheses.json
    hyp_path = 'D:/SUBJECT-01/registry/hypotheses.json'
    with open(hyp_path, 'r', encoding='utf-8') as f:
        hyps = json.load(f)

    for h in hyps:
        if h['id'] == 'HYP-0008':
            h['status'] = 'verified'
            h['notes'] = 'Formulated and confirmed in Cycle 9 via biophysical modeling and empirical HD-sEMG / 31P-MRS cross-validation. EXP-0054 (Cycle 17) confirms that single-channel uncalibrated sEMG cannot identify motor drive across subjects.'
        elif h['id'] == 'HYP-0010':
            h['status'] = 'unverified'
            h['title'] = 'Regional patellar tendon geometry improves prediction of local strain'
            h['statement'] = 'At the same inferred tendon force, using segmental CSA rather than a single nominal CSA reduces held-out local strain prediction RMSE by at least 10% under an otherwise fixed material model.'
            h['notes'] = 'Unverified (MODEL_ONLY). Evaluated in EXP-0049 (NEG-0046, DATA_BLOCKED). Literature means cannot be substituted as individual data. Distinct from Achilles tendon layer findings (Bogaerts FND-0056).'

    # Check if HYP-0013 exists
    hyp13_exists = False
    for h in hyps:
        if h['id'] == 'HYP-0013':
            hyp13_exists = True
            h['status'] = 'rejected'
            h['related_experiments'] = ['EXP-0056', 'EXP-0058']
            h['notes'] = 'Rejected as a novel finding in Cycle 18. Microanatomical distribution was already published by Cohen et al. (2026). Stromal COL22A1 upregulation fails the preregistered donor consistency threshold (0.60 vs 0.75, elevated in only 3 of 5 donors).'
    if not hyp13_exists:
        hyps.append({
            'id': 'HYP-0013',
            'date': '2026-11-12',
            'title': 'Stromal-Myonuclear Dual Synthesis of Collagen XXII & MTJ Anchoring Complex',
            'statement': 'Collagen XXII (COL22A1) and key anchoring proteins of the MTJ (POSTN, TNC, COMP, ITGA7, LAMA2, PXN) are synthesized co-operatively by MTJ-specific fibroblasts and transitional myonuclei, increasing interface shear resistance.',
            'status': 'rejected',
            'related_experiments': ['EXP-0056', 'EXP-0058'],
            'sources': ['SRC-0082'],
            'notes': 'Rejected as a novel finding in Cycle 18. Microanatomical distribution was already published by Cohen et al. (2026). Stromal COL22A1 upregulation fails the preregistered donor consistency threshold (0.60 vs 0.75, elevated in only 3 of 5 donors).'
        })

    with open(hyp_path, 'w', encoding='utf-8') as f:
        json.dump(hyps, f, indent=2, ensure_ascii=False)
    print(f"Updated hypotheses.json: {len(hyps)} hypotheses.")

    # 2. Update experiments.json
    exp_path = 'D:/SUBJECT-01/registry/experiments.json'
    with open(exp_path, 'r', encoding='utf-8') as f:
        exps = json.load(f)

    # Filter out existing EXP-0057, EXP-0058 if present to re-add cleanly
    exps = [e for e in exps if e['id'] not in ('EXP-0057', 'EXP-0058')]

    exps.append({
        'id': 'EXP-0057',
        'date': '2026-11-12',
        'name': 'Oxford Achilles Atlas Data Recovery and MTJCore Discovery Identity Audit',
        'sources': ['SRC-0082'],
        'design': 'Cross-repository audit of Oxford Achilles Atlas across Mendeley, CELLxGENE, GitHub, and HCA, verifying cell populations, counts, and proven identity with the MTJCore discovery cohort.',
        'status': 'completed',
        'model': 'research/cycle18/scripts/audit_oxford_atlas.py',
        'inputs': 'research/cycle18/data_manifest.json',
        'report': 'research/cycle18/OXFORD_DATA_ACCESS_AUDIT.md',
        'outputs': [
            'research/cycle18/OXFORD_AUDIT_SUMMARY.json',
            'research/cycle18/MTJ_REPLICATION_RESULTS.json'
        ],
        'reproduction_command': 'python research/cycle18/scripts/audit_oxford_atlas.py',
        'results': {
            'findings': ['FND-0058', 'FND-0059'],
            'negative_results': ['NEG-0054']
        },
        'limits': 'Dataset was the original discovery cohort of MTJCore; circular re-evaluation prohibited.',
        'external_validation': 'CIRCULARITY_PROVEN_REPLICATION_PROHIBITED',
        'data_type': 'DERIVED_EXTRACTION_JSON'
    })

    exps.append({
        'id': 'EXP-0058',
        'date': '2026-11-12',
        'name': 'Re-evaluation of Stromal-Myonuclear Dual Synthesis (HYP-0013)',
        'sources': ['SRC-0082'],
        'design': 'Quantification of differential expression for MTJ components in myonuclear and fibroblast compartments; donor-consistency stress test and novelty audit.',
        'status': 'completed',
        'model': 'research/cycle18/scripts/evaluate_hyp0013.py',
        'inputs': 'research/cycle18/data_manifest.json',
        'report': 'research/cycle18/HYP0013_ASSESSMENT.md',
        'outputs': [
            'research/cycle18/HYP0013_EVALUATION.json'
        ],
        'reproduction_command': 'python research/cycle18/scripts/evaluate_hyp0013.py',
        'results': {
            'findings': [],
            'negative_results': ['NEG-0055']
        },
        'limits': 'Transcriptomic abundance in snRNA-seq does not demonstrate extracellular secretion or mechanical force resistance.',
        'external_validation': 'FALSIFIED_DONOR_CONSISTENCY',
        'data_type': 'DERIVED_EXTRACTION_JSON'
    })

    with open(exp_path, 'w', encoding='utf-8') as f:
        json.dump(exps, f, indent=2, ensure_ascii=False)
    print(f"Updated experiments.json: {len(exps)} experiments.")

    # 3. Update findings.json
    fnd_path = 'D:/SUBJECT-01/registry/findings.json'
    with open(fnd_path, 'r', encoding='utf-8') as f:
        fnds = json.load(f)

    fnds = [fn for fn in fnds if fn['id'] not in ('FND-0058', 'FND-0059')]
    fnds.append({
        'id': 'FND-0058',
        'date': '2026-11-12',
        'experiment_id': 'EXP-0057',
        'title': 'Oxford Achilles Atlas Provenance Identity with MTJCore Discovery Cohort',
        'statement': 'The Oxford Achilles Tendon Atlas (Cohen et al. 2026, CZ CELLxGENE ef0fc6ac-4872-40e1-ab24-e445b19ca6e3) is the original discovery dataset of the MTJCore project, containing 64,862 cells (22,146 muscle nuclei, 24,179 fibroblasts) across 5 human donors. Evaluating MTJCore on this dataset constitutes complete training-data leakage (circular self-validation) and cannot serve as an independent replication.',
        'confidence': 'high',
        'data_type': 'DERIVED_EXTRACTION_JSON'
    })

    fnds.append({
        'id': 'FND-0059',
        'date': '2026-11-12',
        'experiment_id': 'EXP-0057',
        'title': 'Correction of Cycle 17 Methodological Errors and Erroneous GEO Accession',
        'statement': 'Forensic audit rectified four critical issues from Cycle 17: (1) HYP-0008 verified status preserved under its original biophysical scope, as EXP-0054 confirms uncalibrated sEMG unidentifiability; (2) HYP-0010 restored to patellar tendon segmental CSA; (3) Ridge F3 vs F0 t-statistic typo corrected to t = -0.084, p = 0.9337; (4) accession GSE130649 (mouse inner ear organoids) falsified and permanently eliminated from human muscle plans.',
        'confidence': 'high',
        'data_type': 'DERIVED_EXTRACTION_JSON'
    })

    with open(fnd_path, 'w', encoding='utf-8') as f:
        json.dump(fnds, f, indent=2, ensure_ascii=False)
    print(f"Updated findings.json: {len(fnds)} findings.")

    # 4. Update negative_results.json
    neg_path = 'D:/SUBJECT-01/registry/negative_results.json'
    with open(neg_path, 'r', encoding='utf-8') as f:
        negs = json.load(f)

    negs = [n for n in negs if n['id'] not in ('NEG-0054', 'NEG-0055')]
    negs.append({
        'id': 'NEG-0054',
        'date': '2026-11-12',
        'experiment_id': 'EXP-0057',
        'title': 'Oxford Achilles Atlas Ineligible for Third Independent Replication of MTJCore',
        'statement': 'Independent biological replication of MTJCore on the Oxford Achilles Atlas is invalid due to dataset identity with the discovery training cohort (100% data leakage). In the global public domain, no third independent snRNA-seq cohort with donor-level adult human MTJ contrasts exists. MTJCore replication attempts on Cohen et al. are closed with decision STOP_NO_ADDED_SCIENTIFIC_VALUE.',
        'reason': 'Data provenance audit proved that Cohen et al. (2026) was the original discovery cohort of MTJCore.'
    })

    negs.append({
        'id': 'NEG-0055',
        'date': '2026-11-12',
        'experiment_id': 'EXP-0058',
        'title': 'Stromal COL22A1 Upregulation Fails Preregistered Donor Consistency Threshold',
        'statement': 'In the Achilles MTJ-vs-midbody fibroblast contrast, COL22A1 upregulation achieved a donor direction consistency of only 0.60 (elevated in 3 of 5 donors), failing the preregistered threshold of >= 0.75 and resulting in rejection from the frozen fibroblast signature. Hypothesis HYP-0013 lacks novelty as cellular distributions were already published in Cohen et al. (2026).',
        'reason': 'Inter-donor inconsistency in stromal COL22A1 expression and lack of originality relative to published literature.'
    })

    with open(neg_path, 'w', encoding='utf-8') as f:
        json.dump(negs, f, indent=2, ensure_ascii=False)
    print(f"Updated negative_results.json: {len(negs)} negative results.")

    # 5. Update issues.json
    iss_path = 'D:/SUBJECT-01/registry/issues.json'
    with open(iss_path, 'r', encoding='utf-8') as f:
        isss = json.load(f)

    isss = [i for i in isss if i['id'] != 'ISS-0026']
    isss.append({
        'id': 'ISS-0026',
        'date': '2026-11-12',
        'title': 'Resolution of MTJCore Oxford Discovery Identity and Accession GSE130649',
        'status': 'resolved',
        'severity': 'medium',
        'description': 'Cycle 15-17 proposed using Oxford Achilles Atlas (Cohen et al. 2026) as a third independent replication of MTJCore and proposed GSE130649 for muscle atlas analysis. Audited in Cycle 18: Oxford Atlas is the MTJCore discovery dataset (circular replication prohibited), and GSE130649 is mouse inner ear organoids. Both issues fully resolved and corrected.',
        'resolution': 'Classified Oxford evaluation as INVALID_CIRCULAR_EVALUATION; closed MTJCore replication on Cohen et al. with STOP_NO_ADDED_SCIENTIFIC_VALUE; purged GSE130649 from scientific proposals.'
    })

    with open(iss_path, 'w', encoding='utf-8') as f:
        json.dump(isss, f, indent=2, ensure_ascii=False)
    print(f"Updated issues.json: {len(isss)} issues.")

if __name__ == '__main__':
    update_registries()
