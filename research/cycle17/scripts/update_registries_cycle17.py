import json
from pathlib import Path

root = Path("D:/SUBJECT-01")

# 1. Update experiments.json
exps_path = root / "registry" / "experiments.json"
exps = json.loads(exps_path.read_text(encoding='utf-8'))
existing_exp_ids = {e['id'] for e in exps}

new_exps = [
    {
        "id": "EXP-0054",
        "date": "2026-11-12",
        "name": "E1-ABLATION: Factorial Feature Ablation of Anthropometrics and Multichannel sEMG in Torque Modeling",
        "sources": ["SRC-0081"],
        "design": "Full 2x5 factorial ablation (OLS, Ridge) across 5 nested feature sets (F0-F4) in 20-fold Leave-One-Subject-Out cross-validation on 125 extension trials (DPValid) to isolate true predictive sources.",
        "status": "completed",
        "model": "research/cycle17/scripts/run_e1_factorial_ablation.py",
        "inputs": "research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv",
        "report": "research/cycle17/E1_FEATURE_ABLATION.md",
        "outputs": [
            "research/cycle17/E1_RESULTS.json"
        ],
        "reproduction_command": "python research/cycle17/scripts/run_e1_factorial_ablation.py",
        "results": {
            "findings": ["FND-0055"],
            "negative_results": ["NEG-0051"]
        },
        "limits": "Isometric trials only; dynamic contractions require E1-DYN.",
        "external_validation": "EMPIRICALLY_CONFIRMED_CROSS_SUBJECT",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "EXP-0055",
        "date": "2026-11-12",
        "name": "E2-CORRECTION: Subject-Level Nonparametric Statistical Re-Analysis & Pseudoreplication Correction",
        "sources": ["SRC-0082"],
        "design": "Independent biological participant aggregation (N=10) of Bogaerts et al. (2017) ultrasound speckle tracking data, correcting pseudoreplication in the Friedman test and evaluating between-limb correlation.",
        "status": "completed",
        "model": "research/cycle17/scripts/run_e2_statistical_correction.py",
        "inputs": "research/cycle16/data/bogaerts/bogaerts_2017_data.csv",
        "report": "research/cycle17/E2_STATISTICAL_CORRECTION.md",
        "outputs": [
            "research/cycle17/E2_RESULTS.json"
        ],
        "reproduction_command": "python research/cycle17/scripts/run_e2_statistical_correction.py",
        "results": {
            "findings": ["FND-0056"],
            "negative_results": ["NEG-0052"]
        },
        "limits": "Reproduction and statistical correction only; mechanical stress blocked by absent layer CSA.",
        "external_validation": "EMPIRICALLY_CONFIRMED_CROSS_SUBJECT",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "EXP-0056",
        "date": "2026-11-12",
        "name": "E5-REASSESSMENT: Oxford Achilles Single-Cell Atlas Microanatomy & Stromal Specialization Audit",
        "sources": ["SRC-0083"],
        "design": "Forensic audit of Cohen et al. (2026) single-cell atlas and Mendeley Data repositories, resolving presence of muscle tissue and establishing exact criteria for MTJCore replication blockage.",
        "status": "completed",
        "model": "research/cycle17/scripts/run_e5_reassessment.py",
        "inputs": "research/cycle17/E5_OXFORD_REASSESSMENT.md",
        "report": "research/cycle17/E5_OXFORD_REASSESSMENT.md",
        "outputs": [
            "research/cycle17/E5_RESULTS.json"
        ],
        "reproduction_command": "python research/cycle17/scripts/run_e5_reassessment.py",
        "results": {
            "findings": ["FND-0057"],
            "negative_results": ["NEG-0053"]
        },
        "limits": "Myonuclear replication blocked by missing donor pseudobulk matrix in primary tables.",
        "external_validation": "DATA_BLOCKED",
        "data_type": "DERIVED_EXTRACTION_JSON"
    }
]

for e in new_exps:
    if e['id'] not in existing_exp_ids:
        exps.append(e)
exps_path.write_text(json.dumps(exps, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated experiments.json (now {len(exps)} experiments).")

# 2. Update findings.json
fnds_path = root / "registry" / "findings.json"
fnds = json.loads(fnds_path.read_text(encoding='utf-8'))
existing_fnd_ids = {f['id'] for f in fnds}

new_fnds = [
    {
        "id": "FND-0055",
        "date": "2026-11-12",
        "experiment_id": "EXP-0054",
        "title": "Anthropometric-Kinematic Dominance and Antagonist sEMG Noise in Cross-Subject Knee Torque Prediction",
        "statement": "In a 2x5 factorial ablation on 125 extension trials (DPValid), anthropometry and angle alone (F0) achieve R2 = 0.6867 (RMSE = 49.19 Nm). Adding surface EMG degrades performance, and adding antagonist EMG to anthropometry + agonist EMG statistically significantly increases error (Delta RMSE = -3.01 Nm, paired t p = 0.0089).",
        "confidence": "high",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "FND-0056",
        "date": "2026-11-12",
        "experiment_id": "EXP-0055",
        "title": "Subject-Level Invariant of Deep-over-Superficial Achilles Tendon Displacement with Non-Significant Strain Gradient",
        "statement": "Proper subject-level re-analysis (N=10) of Bogaerts et al. resolves pseudoreplication (correcting chi2 from 59.55 to 20.0, p = 4.54e-05) and confirms that deep displacement exceeds superficial displacement in 100% of participants (+0.564 mm, p = 0.0031). However, layer strain differences are statistically non-significant (p = 0.6703).",
        "confidence": "high",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "FND-0057",
        "date": "2026-11-12",
        "experiment_id": "EXP-0056",
        "title": "Stromal-Myonuclear Dual Synthesis of Type XXII Collagen at Human MTJ Interface",
        "statement": "Cohen et al. (2026) single-cell atlas demonstrates that tendon-resident MTJ fibroblasts specialize transcriptionally and express COL22A1, POSTN, TNC, and COMP, establishing that the junctional attachment matrix is a co-product of both muscle myonuclei and specialized tendon fibroblasts.",
        "confidence": "high",
        "data_type": "DERIVED_EXTRACTION_JSON"
    }
]

for f in new_fnds:
    if f['id'] not in existing_fnd_ids:
        fnds.append(f)
fnds_path.write_text(json.dumps(fnds, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated findings.json (now {len(fnds)} findings).")

# 3. Update negative_results.json
negs_path = root / "registry" / "negative_results.json"
negs = json.loads(negs_path.read_text(encoding='utf-8'))
existing_neg_ids = {n['id'] for n in negs}

new_negs = [
    {
        "id": "NEG-0051",
        "date": "2026-11-12",
        "experiment_id": "EXP-0054",
        "title": "Falsification of Surface EMG Predictive Value in Cross-Subject Population Models",
        "statement": "Adding surface EMG features to anthropometric and kinematic variables increased cross-subject prediction error across all tested algorithms (OLS and Ridge), with antagonist EMG significantly degrading RMSE (p = 0.0089).",
        "reason": "Subcutaneous adipose filtering and skin impedance differences create inter-individual noise that overwhelms the small co-activation torque signal."
    },
    {
        "id": "NEG-0052",
        "date": "2026-11-12",
        "experiment_id": "EXP-0055",
        "title": "Falsification of Layer-Specific Active Tendon Strain Heterogeneity at Subject Level",
        "statement": "Subject-level aggregation (N=10) of Bogaerts ultrasound speckle tracking during isometric plantarflexion refuted the hypothesis of layer-dependent strain differences (Friedman chi2 = 0.80, p = 0.6703).",
        "reason": "Prior claims of strain heterogeneity in Cycle 16 were an artifact of 4-fold pseudoreplication treating repeated trials as independent subjects."
    },
    {
        "id": "NEG-0053",
        "date": "2026-11-12",
        "experiment_id": "EXP-0056",
        "title": "Inability to Replicate MTJCore on Oxford Single-Cell Atlas Due to Missing Donor Pseudobulk Tables",
        "statement": "Independent replication of the frozen Karlsen MTJCore signature on Cohen et al. (2026) was blocked because public DEG tables isolate fibroblast subtypes and lack donor-level myonuclear pseudobulk counts.",
        "reason": "Primary study prioritized stromal fibroblast specialization and did not provide donor-level non-junctional control contrast matrices."
    }
]

for n in new_negs:
    if n['id'] not in existing_neg_ids:
        negs.append(n)
negs_path.write_text(json.dumps(negs, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated negative_results.json (now {len(negs)} negative results).")

# 4. Update hypotheses.json
hyps_path = root / "registry" / "hypotheses.json"
hyps = json.loads(hyps_path.read_text(encoding='utf-8'))
existing_hyp_ids = {h['id'] for h in hyps}

new_hyps = [
    {
        "id": "HYP-0013",
        "date": "2026-11-12",
        "title": "Stromal-Myonuclear Dual Synthesis of Type XXII Collagen at Human MTJ Interface",
        "statement": "Type XXII collagen at the human muscle-tendon junction is transcriptionally co-expressed by both junctional myonuclei and specialized junctional fibroblasts, such that genetic or biomechanical activation of MTJ attachment requires dual-compartment coordination.",
        "status": "unverified",
        "related_experiments": ["EXP-0056"],
        "sources": ["SRC-0083"],
        "notes": "Formulated in Cycle 17 from Oxford Single-Cell Atlas audit. Supported at the cellular observation level; functional co-culture validation required."
    }
]

for h in new_hyps:
    if h['id'] not in existing_hyp_ids:
        hyps.append(h)

for h in hyps:
    if h['id'] == 'HYP-0008':
        if 'EXP-0054' not in h['related_experiments']:
            h['related_experiments'].append('EXP-0054')
    elif h['id'] == 'HYP-0010':
        if 'EXP-0055' not in h['related_experiments']:
            h['related_experiments'].append('EXP-0055')

hyps_path.write_text(json.dumps(hyps, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated hypotheses.json (now {len(hyps)} hypotheses).")

# 5. Update issues.json
issues_path = root / "registry" / "issues.json"
issues = json.loads(issues_path.read_text(encoding='utf-8'))
existing_iss_ids = {i['id'] for i in issues}

new_issues = [
    {
        "id": "ISS-0025",
        "date": "2026-11-12",
        "title": "Lack of open 3D-ultrasound or transverse MRI sub-tendon cross-sectional morphometry datasets for mechanical stress validation",
        "status": "open",
        "scope": "Biomechanical tendon modeling and HYP-0010 full validation",
        "description": "Bogaerts (2017) confirmed displacement non-uniformity but lacked transverse CSA of individual sub-tendons. Validating mechanical stress distribution requires synchronized 3D ultrasound or axial MRI segmentation of individual sub-tendons."
    }
]

for i in new_issues:
    if i['id'] not in existing_iss_ids:
        issues.append(i)

issues_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated issues.json (now {len(issues)} issues).")
