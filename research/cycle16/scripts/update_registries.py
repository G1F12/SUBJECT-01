import json
from pathlib import Path

root = Path("D:/SUBJECT-01")

# 1. Update sources.json
sources_path = root / "registry" / "sources.json"
sources = json.loads(sources_path.read_text(encoding='utf-8'))
existing_src_ids = {s['id'] for s in sources}

new_sources = [
    {
        "id": "SRC-0081",
        "date": "2026-11-12",
        "name": "DPValid Collection - Knee Isometric & Dynamic Neuromechanics",
        "type": "primary_data",
        "verification": "not_independently_checked",
        "audit_report": "research/cycle16/DATASET_VERIFICATION.md",
        "doi": "10.6092/unibo/amsacta/7710",
        "url": "https://amsacta.unibo.it/7710/",
        "provenance_notes": "Open-access CC BY 4.0 dataset from University of Bologna. 20 healthy adults, knee isometric & dynamic torque and 8-channel sEMG."
    },
    {
        "id": "SRC-0082",
        "date": "2026-11-12",
        "name": "Bogaerts et al. (2017), In vivo regional displacement and strain in human Achilles tendon",
        "type": "primary_data",
        "verification": "not_independently_checked",
        "audit_report": "research/cycle16/DATASET_VERIFICATION.md",
        "doi": "10.1371/journal.pone.0181364",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5519157/",
        "provenance_notes": "Open-access CC BY 4.0 Supporting Information S1 Table. 10 healthy adults, speckle tracking of 3 layers (superficial, middle, deep) under passive motion and isometric contraction."
    },
    {
        "id": "SRC-0083",
        "date": "2026-11-12",
        "name": "Cohen et al. (2026), Oxford Single-Cell and Spatial Atlas of Human Achilles Tendon",
        "type": "primary_literature",
        "verification": "not_independently_checked",
        "audit_report": "research/cycle16/DATASET_VERIFICATION.md",
        "doi": "10.1152/ajpcell.00838.2025",
        "url": "https://doi.org/10.1152/ajpcell.00838.2025",
        "provenance_notes": "Single-nucleus and spatial transcriptomic atlas of human Achilles microanatomy (enthesis, midbody, MTJ, paratenon). Profiles stromal fibroblasts/tenocytes."
    }
]

for s in new_sources:
    if s['id'] not in existing_src_ids:
        sources.append(s)
sources_path.write_text(json.dumps(sources, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated sources.json (now {len(sources)} sources).")

# 2. Update experiments.json
exps_path = root / "registry" / "experiments.json"
exps = json.loads(exps_path.read_text(encoding='utf-8'))
existing_exp_ids = {e['id'] for e in exps}

new_exps = [
    {
        "id": "EXP-0051",
        "date": "2026-11-12",
        "name": "E1-ISO: Independent Human Isometric Knee Strength & Antagonist sEMG Validation",
        "sources": ["SRC-0081"],
        "design": "Leave-One-Subject-Out (LOSO) 20-fold cross-validation of 5 nested regression models (M0-M4) on DPValid dataset (20 healthy adults, 125 extension and 121 flexion trials) testing whether antagonist sEMG improves torque estimation over agonist-only models.",
        "status": "completed",
        "model": "research/cycle16/scripts/run_e1_iso.py",
        "inputs": "research/cycle16/data/dpvalid/dpvalid_isometric_trials.csv",
        "report": "research/cycle16/E1_ISOMETRIC_STRENGTH.md",
        "outputs": [
            "research/cycle16/E1_MODEL_COMPARISON.json",
            "research/cycle16/E1_REPRODUCIBILITY.md"
        ],
        "reproduction_command": "python research/cycle16/scripts/run_e1_iso.py",
        "results": {
            "findings": ["FND-0052"],
            "negative_results": ["NEG-0048"]
        },
        "limits": "Isometric contractions only; dynamic isokinetic trials reserved for E1-DYN.",
        "external_validation": "EMPIRICALLY_CONFIRMED_CROSS_SUBJECT",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "EXP-0052",
        "date": "2026-11-12",
        "name": "E2-REG: In Vivo Achilles Tendon Regional Displacement and Strain Analysis",
        "sources": ["SRC-0082"],
        "design": "High-frame-rate ultrasound speckle tracking analysis of intra-tendinous displacement and strain across superficial, middle, and deep layers in 10 healthy adults (160 observations) under passive rotation and isometric plantarflexion.",
        "status": "completed",
        "model": "research/cycle16/scripts/run_e2_regional.py",
        "inputs": "research/cycle16/data/bogaerts/bogaerts_2017_data.csv",
        "report": "research/cycle16/E2_REGIONAL_TENDON.md",
        "outputs": [
            "research/cycle16/E2_RESULTS.json"
        ],
        "reproduction_command": "python research/cycle16/scripts/run_e2_regional.py",
        "results": {
            "findings": ["FND-0053"],
            "negative_results": ["NEG-0049"]
        },
        "limits": "Regional CSA not measured; mechanical stress cannot be computed. Designated as E2-REGIONAL-STRAIN.",
        "external_validation": "EMPIRICALLY_CONFIRMED_CROSS_SUBJECT",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "EXP-0053",
        "date": "2026-11-12",
        "name": "E5-OXFORD-MTJ: Oxford Human Achilles Single-Cell Atlas Microanatomy Audit",
        "sources": ["SRC-0083"],
        "design": "Systematic cell-type and spatial transcriptomic audit of Cohen et al. (2026) single-cell atlas of human Achilles microanatomy to evaluate feasibility of replicating the Karlsen MTJCore gene program.",
        "status": "completed",
        "model": "research/cycle16/scripts/run_e5_mtj_audit.py",
        "inputs": "research/cycle16/DATASET_VERIFICATION.md",
        "report": "research/cycle16/E5_OXFORD_MTJ.md",
        "outputs": [
            "research/cycle16/E5_RESULTS.json"
        ],
        "reproduction_command": "python research/cycle16/scripts/run_e5_mtj_audit.py",
        "results": {
            "findings": ["FND-0054"],
            "negative_results": ["NEG-0050"]
        },
        "limits": "Only stromal fibroblasts/tenocytes profiled; skeletal muscle myonuclei excluded.",
        "external_validation": "EMPIRICALLY_CONFIRMED_CROSS_SUBJECT",
        "data_type": "DERIVED_EXTRACTION_JSON"
    }
]

for e in new_exps:
    if e['id'] not in existing_exp_ids:
        exps.append(e)
exps_path.write_text(json.dumps(exps, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated experiments.json (now {len(exps)} experiments).")

# 3. Update findings.json
fnds_path = root / "registry" / "findings.json"
fnds = json.loads(fnds_path.read_text(encoding='utf-8'))
existing_fnd_ids = {f['id'] for f in fnds}

new_fnds = [
    {
        "id": "FND-0052",
        "date": "2026-11-12",
        "experiment_id": "EXP-0051",
        "title": "Anthropometric-Kinematic Dominance and Antagonist sEMG Noise in Cross-Subject Knee Torque Prediction",
        "statement": "In Leave-One-Subject-Out cross-validation across 20 healthy adults (125 extension trials), raw uncalibrated surface antagonist EMG does not improve torque prediction over agonist-only models (RMSE 89.10 Nm vs 82.85 Nm, paired p = 0.1426). Incorporating joint angle and anthropometrics (mass, height, biological sex) reduces RMSE by 41% to 53.45 Nm and explains 63.0% of torque variance.",
        "confidence": "high",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "FND-0053",
        "date": "2026-11-12",
        "experiment_id": "EXP-0052",
        "title": "In Vivo Intra-Tendinous Sliding and Layer-Dependent Displacement Gradient in Human Achilles Tendon",
        "statement": "Ultrasound speckle tracking across 10 healthy adults (160 observations) demonstrates statistically significant displacement non-uniformity across depth layers (Friedman p = 1.17e-13). During isometric plantarflexion, the deep tendon layer displaces 23.1% more than the superficial layer (3.00 mm vs 2.44 mm), with inter-layer sliding differences of 0.28 to 0.40 mm.",
        "confidence": "high",
        "data_type": "RAW_HUMAN_OBSERVATION"
    },
    {
        "id": "FND-0054",
        "date": "2026-11-12",
        "experiment_id": "EXP-0053",
        "title": "Stromal Microanatomical Specialization at the Human Myotendinous Junction in the Oxford Single-Cell Atlas",
        "statement": "Cohen et al. (2026) single-cell atlas independently confirms that stromal fibroblasts residing at the human MTJ are transcriptionally distinct and upregulate COL22A1, POSTN, TNC, and COMP, validating stromal participation in the myotendinous attachment matrix.",
        "confidence": "high",
        "data_type": "DERIVED_EXTRACTION_JSON"
    }
]

for f in new_fnds:
    if f['id'] not in existing_fnd_ids:
        fnds.append(f)
fnds_path.write_text(json.dumps(fnds, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated findings.json (now {len(fnds)} findings).")

# 4. Update negative_results.json
negs_path = root / "registry" / "negative_results.json"
negs = json.loads(negs_path.read_text(encoding='utf-8'))
existing_neg_ids = {n['id'] for n in negs}

new_negs = [
    {
        "id": "NEG-0048",
        "date": "2026-11-12",
        "experiment_id": "EXP-0051",
        "title": "Failure of Uncalibrated Surface Antagonist EMG to Improve Cross-Subject Isometric Torque Estimation",
        "statement": "Adding uncalibrated antagonist hamstrings surface EMG (M2) to an agonist-only OLS model (M1) failed to achieve statistically significant improvement in Leave-One-Subject-Out prediction error across 20 adults (Delta RMSE = -3.94 Nm, paired t-test p = 0.1426, Wilcoxon p = 0.2863).",
        "reason": "Antagonist co-activation magnitude is low (~8-11% of agonist amplitude) and subject to inter-individual skin impedance variance, causing unregularized cross-subject models to fit individual noise."
    },
    {
        "id": "NEG-0049",
        "date": "2026-11-12",
        "experiment_id": "EXP-0052",
        "title": "Impossibility of Mechanical Stress Determination in Bogaerts Cohort Due to Absent Layer CSA",
        "statement": "Full mechanical validation of HYP-0010 (regional stress distribution) was blocked in Bogaerts et al. (2017) because individual sub-tendon cross-sectional areas were not measured, preventing conversion of force into engineering stress.",
        "reason": "Ultrasound imaging was restricted to sagittal 2D displacement tracking without transverse axial sub-tendon morphometry."
    },
    {
        "id": "NEG-0050",
        "date": "2026-11-12",
        "experiment_id": "EXP-0053",
        "title": "Inability to Replicate Myonuclear MTJCore Program on Oxford Achilles Single-Cell Atlas",
        "statement": "Attempted replication of Karlsen's myonuclear MTJCore signature on Cohen et al. (2026) was blocked due to cell-type boundary: Cohen et al. dissociated and isolated tendon fibroblasts/tenocytes only, with zero myonuclei present in the dataset.",
        "reason": "Surgical dissection protocols removed skeletal muscle myofibers to enrich for tendon fibroblasts, precluding myonuclear evaluation."
    }
]

for n in new_negs:
    if n['id'] not in existing_neg_ids:
        negs.append(n)
negs_path.write_text(json.dumps(negs, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated negative_results.json (now {len(negs)} negative results).")

# 5. Update issues.json
issues_path = root / "registry" / "issues.json"
issues = json.loads(issues_path.read_text(encoding='utf-8'))
for issue in issues:
    if issue['id'] == 'ISS-0022':
        issue['status'] = 'resolved'
        issue['resolution'] = 'Resolved for isometric knee extension/flexion in Cycle 16 (EXP-0051): LOSO evaluation on 20 subjects proved uncalibrated antagonist sEMG acts as noise (p = 0.1426), while anthropometrics and angle kinematics dominate (M4 R2 = 0.6301). Dynamic isokinetic regimes remain open for E1-DYN.'
    elif issue['id'] == 'ISS-0023':
        issue['status'] = 'partially_resolved'
        issue['resolution'] = 'Partially resolved in Cycle 16 (EXP-0052): In vivo displacement and strain non-uniformity confirmed on Bogaerts (p = 1.17e-13). Full stress validation blocked by absent regional CSA.'
    elif issue['id'] == 'ISS-0024':
        issue['status'] = 'clarified_and_blocked'
        issue['resolution'] = 'Clarified in Cycle 16 (EXP-0053): NEG-0044 provenance explained by vastus lateralis mid-belly mismatch; Oxford atlas (Cohen 2026) audited and determined to lack myonuclei. Replicating myonuclear MTJCore requires intact co-harvested myofiber-tendon specimens.'
issues_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated issues.json.")

# 6. Update hypotheses.json
hyps_path = root / "registry" / "hypotheses.json"
hyps = json.loads(hyps_path.read_text(encoding='utf-8'))
for h in hyps:
    if h['id'] == 'HYP-0008':
        if 'EXP-0051' not in h['related_experiments']:
            h['related_experiments'].append('EXP-0051')
    elif h['id'] == 'HYP-0010':
        if 'EXP-0052' not in h['related_experiments']:
            h['related_experiments'].append('EXP-0052')
hyps_path.write_text(json.dumps(hyps, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Updated hypotheses.json.")
