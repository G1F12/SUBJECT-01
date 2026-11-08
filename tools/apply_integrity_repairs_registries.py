#!/usr/bin/env python3
"""
SUBJECT-01 — Cycle 9 Real-Data Integrity Repair for Registries
Updates registry/sources.json, registry/experiments.json, registry/findings.json,
registry/negative_results.json, and registry/decisions.json to enforce strict data provenance.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Update sources.json
sources_file = ROOT / 'registry' / 'sources.json'
sources = json.loads(sources_file.read_text(encoding='utf-8'))

for s in sources:
    if s['id'] == 'SRC-0068':
        s['provenance_notes'] = (
            "Published literature discharge rates across 8 rater operators analyzing 1 human subject recording dataset "
            "(8 raters != 8 independent human subjects; inter-operator agreement 99.6%). Raw 64-channel archives on "
            "Figshare (444 MB) are blocked by Cloudflare R2 bot challenge (HTTP 403 Forbidden)."
        )
        s['data_type'] = "LITERATURE_REPORTED_VALUE"
    elif s['id'] == 'SRC-0069':
        s['provenance_notes'] = (
            "Published Data in Brief summary Table 1 listing 3 recovery rate constants in human quadriceps. Continuous "
            "raw time series on Dryad (2024_829_Ergometer_Dryad_Raw_V3.xlsx) are blocked by AWS WAF interactive bot "
            "challenge (HTTP 403 Forbidden). Status: RAW_TIMESERIES_UNAVAILABLE."
        )
        s['data_type'] = "LITERATURE_REPORTED_VALUE"
    elif s['id'] == 'SRC-0070':
        s['provenance_notes'] = (
            "MuscleMap Zenodo 10077847 contains deep learning framework weights and templates, not an open verified "
            "cohort table (n=48, 342.5 mL). Status EMPIRICALLY_BOUNDED_DISTRIBUTION retracted."
        )
        s['data_type'] = "SYNTHETIC"
    elif s['id'] == 'SRC-0071':
        s['provenance_notes'] = (
            "Cenni et al. Figshare 5971480 is an unresolvable ID as a public dataset archive. Retracted from empirical anchors."
        )
        s['data_type'] = "SYNTHETIC"

sources_file.write_text(json.dumps(sources, indent=2, ensure_ascii=False), encoding='utf-8')
print("Updated registry/sources.json")

# 2. Update experiments.json
exp_file = ROOT / 'registry' / 'experiments.json'
experiments = json.loads(exp_file.read_text(encoding='utf-8'))

for e in experiments:
    if e['id'] == 'EXP-0037':
        e['name'] = 'Empirical Acquisition Audit of Lower-Limb HD-sEMG and Dynamic 31P-MRS Datasets'
        e['data_type'] = 'LITERATURE_REPORTED_VALUE'
        e['status'] = 'completed_literature_audit_raw_blocked'
        e['external_validation'] = 'published_literature_aggregates_audited'
        e['limits'] = (
            "Raw continuous time-series blocked by AWS WAF (Dryad 403) and Cloudflare R2 (Figshare 444 MB 403). "
            "Hug rates represent 8 operators analyzing 1 subject (8 raters != 8 subjects). SRC-0070 and SRC-0071 cohort tables retracted."
        )
    elif e['id'] == 'EXP-0038':
        e['name'] = 'Biophysical Forward Simulation Model of Motor Unit Recruitment, Volume Conduction, and SAT Filtering'
        e['data_type'] = 'SYNTHETIC'
        e['status'] = 'COMPUTATIONAL_SIMULATION_HYPOTHESIS'
        e['external_validation'] = 'computational_simulation_hypothesis'
        e['limits'] = (
            "Forward simulation scenario (500 MUs, Fuglevand exponential pool, -35% force drop). "
            "Outputs (+14% sEMG RMS, 40.9x sensitivity span) are model-derived scenario consequences, not empirical measurements."
        )
    elif e['id'] == 'EXP-0039':
        e['data_type'] = 'COMPUTATIONAL_SIMULATION'
        e['status'] = 'completed_identifiability_audit'
        e['external_validation'] = 'algebraically_verified_identifiability_audit'
    elif e['id'] == 'EXP-0040':
        e['name'] = 'Leave-One-Subject-Out (LOSO) Cross-Validation Algorithm Demonstration on Synthetic Benchmarks'
        e['data_type'] = 'SYNTHETIC'
        e['status'] = 'SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED / BLOCKED_PENDING_RAW_DATA'
        e['external_validation'] = 'synthetic_demonstration_not_empirically_validated'
        e['limits'] = (
            "Evaluated on synthetic exponential curves generated via np.random.RandomState. "
            "Real empirical human out-of-sample cross-subject validation remains BLOCKED_PENDING_RAW_DATA."
        )
    elif e['id'] == 'EXP-0041':
        e['name'] = 'SUBJECT-01 Integration: Functional Power, Recovery Limits, and TARGET-CPE45 Boundaries'
        e['data_type'] = 'COMPUTATIONAL_SIMULATION'
        e['status'] = 'completed_macro_budget_accounting'
        e['external_validation'] = 'macro_energy_budget_accounting'
        e['design'] = (
            "Rigorous separation of external mechanical work (250 W * 2700 s = 675 kJ), whole-body metabolic expenditure "
            "(~3375 kJ at eta_gross ~20%), local PCr buffer (0.1-0.6 kJ), and reaction enthalpy Delta_R H = 21 kJ/mol. "
            "Erroneous division of local PCr by external whole-body work retracted."
        )

exp_file.write_text(json.dumps(experiments, indent=2, ensure_ascii=False), encoding='utf-8')
print("Updated registry/experiments.json")

# 3. Update findings.json
fnd_file = ROOT / 'registry' / 'findings.json'
findings = json.loads(fnd_file.read_text(encoding='utf-8'))

for f in findings:
    if f['id'] == 'FND-0038':
        f['finding'] = (
            "Auditing of open human literature reveals published discharge rates for Gastrocnemius Medialis (9.8 to 19.8 Hz) "
            "evaluated across 8 operators on 1 subject recording (8 raters != 8 subjects, inter-operator agreement 99.6%, Hug 2021) "
            "and published mean recovery time constant tau = 39.2 s in quadriceps (Rehman 2024 Table 1). Automated raw data download "
            "is blocked by AWS WAF (Dryad 403) and Cloudflare R2 (Figshare 403)."
        )
    elif f['id'] == 'FND-0039':
        f['finding'] = (
            "In forward biophysical simulation, single-channel sEMG RMS is structurally unidentifiable with respect to active "
            "muscle volume fraction a_eff: variation in subcutaneous fat thickness (3 to 10 mm) induces a 40.9-fold uncertainty "
            "span in a_eff (0.018 to 0.737) at identical measured RMS (12.7%), while fatigue conduction velocity slowing causes "
            "a +14.0% RMS increase despite a -35.0% loss of mechanical twitch force in the simulated scenario."
        )
    elif f['id'] == 'FND-0040':
        f['finding'] = (
            "Leave-One-Subject-Out algorithm evaluation on synthetic exponential benchmarks (tau=24.3 s vs tau=39.2 s) illustrates "
            "computational parameter transfer degradation (+53.9% and +189.3%). PREVIOUS CLAIMS OF EMPIRICAL VALIDATION RETRACTED: "
            "curves were synthetically generated with np.random.RandomState. Independent empirical human cross-subject validation "
            "is BLOCKED_PENDING_RAW_DATA."
        )
        f['confidence'] = 'synthetic_methodological_demonstration_only'
    elif f['id'] == 'FND-0041':
        f['finding'] = (
            "Physical and physiological energy accounting for the 2700-second CPE45 test at 250 W strictly separates external mechanical "
            "work (675 kJ), whole-body gross metabolic chemical expenditure (~3375 kJ at eta_gross ~20%), local active calf PCr "
            "buffer (0.11-0.39 kJ work potential; 0.62 kJ whole GM; heat enthalpy 21 kJ/mol). Taking the ratio of local PCr to 45-min "
            "whole-body work is physically invalid; local phosphagen buffers power only transient bursts (5-30 s), and long-duration "
            "endurance requires systemic cardiorespiratory oxygen delivery."
        )

fnd_file.write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding='utf-8')
print("Updated registry/findings.json")

# 4. Update negative_results.json
neg_file = ROOT / 'registry' / 'negative_results.json'
negative_results = json.loads(neg_file.read_text(encoding='utf-8'))

for n in negative_results:
    if n['id'] == 'NEG-0029':
        n['result'] = (
            "Refuted in forward simulation: Subcutaneous adipose tissue variation (3 to 10 mm) creates a 40.9-fold uncertainty ridge, "
            "and fatigue causes an inverse dissociation (+14% RMS at -35% force) under simulated conditions."
        )
    elif n['id'] == 'NEG-0031':
        n['hypothesis'] = 'Empirical cross-subject and cross-muscle validation of local bioenergetics model can be achieved without verified raw human time-series.'
        n['result'] = (
            "Refuted: Programmatic raw data acquisition from Dryad (Rehman 2024) and Figshare (Hug 2021) returned HTTP 403 Forbidden. "
            "Previous LOSO validation results were based on synthetic exponential series generated with np.random.RandomState. "
            "Status reclassified to SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED, and empirical validation is BLOCKED_PENDING_RAW_DATA."
        )
        n['impact'] = 'Prohibits labeling synthetic algorithmic demonstrations as empirical human validation.'

# Check if NEG-0032 already exists, if not add it
if not any(x['id'] == 'NEG-0032' for x in negative_results):
    negative_results.append({
        'id': 'NEG-0032',
        'date': '2026-11-08',
        'experiment_id': 'EXP-0037',
        'hypothesis': 'Automated scripts can retrieve continuous open raw human 31P-MRS time-series from Dryad and raw HD-sEMG archives from Figshare.',
        'result': 'Refuted: Programmatic downloads failed with HTTP 403 Forbidden due to AWS WAF interactive bot challenge on Dryad and Cloudflare R2 CDN protection on Figshare.',
        'impact': 'Requires formal provenance gating and prevents synthetic data generation from masquerading as unretrieved raw empirical data.'
    })

neg_file.write_text(json.dumps(negative_results, indent=2, ensure_ascii=False), encoding='utf-8')
print("Updated registry/negative_results.json")

print("All registries successfully updated with data integrity repairs.")
