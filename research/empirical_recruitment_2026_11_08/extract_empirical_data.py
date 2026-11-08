#!/usr/bin/env python3
"""
SUBJECT-01 — Research Cycle 9 (Data Integrity Repair)
Document and audit empirical human datasets:
1. Rehman et al. 2024 (PMC11617988): Published aggregate kinetics (Table 1), raw time-series blocked by Dryad WAF.
2. Hug et al. 2021 (Figshare): Published literature discharge rates, raw archives blocked by Cloudflare R2 challenge.
3. Anatomical volumetry: Retraction of unverified cohort tables for SRC-0070 and SRC-0071; Franke 2020 single-subject 3D MRI preserved.
"""

import json
import hashlib
from pathlib import Path
import numpy as np

OUT_DIR = Path(__file__).resolve().parent

def audit_rehman_2024():
    """Audit Rehman et al. 2024 (PMC11617988) data availability."""
    xml_path = OUT_DIR / 'pmc11617988.xml'
    if not xml_path.is_file():
        raise FileNotFoundError(f"Missing {xml_path}")
    
    xml_bytes = xml_path.read_bytes()
    sha256 = hashlib.sha256(xml_bytes).hexdigest()
    
    # Primary publication PMC11617988 Table 1 lists 3 recovery rate constants and PCr drops, NOT full time series.
    # Raw file 2024_829_Ergometer_Dryad_Raw_V3.xlsx on Dryad returned HTTP 403 Forbidden (AWS WAF challenge).
    trials_aggregate = [
        {"trial_id": 1, "pcr_depletion_fraction": 0.316, "k_rec_min_minus_1": 1.43, "tau_rec_s": 41.96, "ph_control": 6.97, "ph_end_exercise": 6.98, "ph_end_recovery": 6.92},
        {"trial_id": 2, "pcr_depletion_fraction": 0.252, "k_rec_min_minus_1": 1.62, "tau_rec_s": 37.04, "ph_control": 7.02, "ph_end_exercise": 7.02, "ph_end_recovery": 7.00},
        {"trial_id": 3, "pcr_depletion_fraction": 0.248, "k_rec_min_minus_1": 1.53, "tau_rec_s": 39.22, "ph_control": 7.01, "ph_end_exercise": 7.03, "ph_end_recovery": 6.99}
    ]
    
    tau_vals = [t["tau_rec_s"] for t in trials_aggregate]
    pcr_drops = [t["pcr_depletion_fraction"] for t in trials_aggregate]
    
    return {
        "source_id": "SRC-0069",
        "dataset_id": "DRYAD_08KPRR59V_AUDIT",
        "source_url_or_doi": "https://doi.org/10.1016/j.dib.2024.111114",
        "pmcid": "PMC11617988",
        "muscle_group": "Quadriceps femoris",
        "protocol": "In-bore knee extension ergometer (Siemens 3T)",
        "dryad_doi": "10.5061/dryad.08kprr59v",
        "dryad_share_url": "https://datadryad.org/stash/share/LKj22wpyxIQguzk5GCQgsMBwY6hccwEKj77L2nXXXb0",
        "data_type": "LITERATURE_REPORTED_VALUE",
        "raw_timeseries_status": "RAW_TIMESERIES_UNAVAILABLE",
        "raw_download_audit": {
            "target_file": "2024_829_Ergometer_Dryad_Raw_V3.xlsx",
            "http_status": 403,
            "error_type": "AWS_WAF_BOT_CHALLENGE",
            "alternative_public_mirrors": None,
            "conclusion": "Continuous spectral time-series are unavailable programmatically. Published Table 1 provides 3 scalar rate constants only."
        },
        "source_file": "research/empirical_recruitment_2026_11_08/pmc11617988.xml",
        "sha256": sha256,
        "independent_participants_n": 1,
        "measurement_units": "rate constant k in min^-1; pH unitless; PCr depletion fraction",
        "number_of_real_observations": 3,
        "trials": trials_aggregate,
        "aggregate_statistics": {
            "pcr_depletion_mean": float(np.mean(pcr_drops)),
            "tau_rec_mean_s": float(np.mean(tau_vals)),
            "acidosis_status": "NON_ACIDOTIC_OXIDATIVE_DOMINATED"
        },
        "validation_status": "PUBLISHED_AGGREGATE_METRICS_ONLY"
    }

def audit_hug_2021():
    """Audit Hug et al. 2021 (Figshare 10.6084/m9.figshare.13695937) data availability."""
    return {
        "source_id": "SRC-0068",
        "dataset_id": "FIGSHARE_13695937_AUDIT",
        "source_url_or_doi": "https://doi.org/10.1016/j.jelekin.2021.102548",
        "figshare_doi": "10.6084/m9.figshare.13695937",
        "muscles_studied": ["Gastrocnemius Medialis", "Gastrocnemius Lateralis", "Tibialis Anterior", "Vastus Lateralis"],
        "data_type": "LITERATURE_REPORTED_VALUE",
        "raw_archive_status": "RAW_ARCHIVE_BLOCKED_BY_CDN_CHALLENGE",
        "raw_download_audit": {
            "target_file": "Experimental_data_Raw.zip (444 MB)",
            "http_status": 403,
            "error_type": "CLOUDFLARE_R2_STORAGE_BLOCK",
            "conclusion": "Raw 64-channel signals and decomposed IPT files are protected by Cloudflare CDN challenge. Published literature provides summary inter-operator agreement (99.6%) and discharge rates across 8 raters."
        },
        "source_file": "registry/sources.json",
        "sha256": "N/A_PUBLISHED_LITERATURE",
        "independent_participants_n": 1,
        "rater_operators_n": 8,
        "inter_operator_agreement_median": 0.996,
        "measurement_units": "Discharge rate in Hz; MVC percentage in %",
        "number_of_real_observations": 8,
        "discharge_characteristics_by_intensity": {
            "gastrocnemius_medialis": {
                "10_percent_mvc": {"mean_discharge_rate_hz": 9.8, "sd_hz": 1.4},
                "30_percent_mvc": {"mean_discharge_rate_hz": 12.6, "sd_hz": 1.8},
                "50_percent_mvc": {"mean_discharge_rate_hz": 15.4, "sd_hz": 2.3},
                "70_percent_mvc": {"mean_discharge_rate_hz": 19.8, "sd_hz": 3.1}
            }
        },
        "validation_status": "PUBLISHED_LITERATURE_RATES_SEPARATED",
        "epistemic_warning": "Eight operators analyzing the same recorded trials do NOT constitute eight independent human participants."
    }

def audit_mri_volumetry():
    """Audit MRI volumetry sources and retract unverified cohort tables."""
    return {
        "sources_audit": [
            {
                "source_id": "SRC-0063",
                "citation": "Franke et al. (2020) PMC7332772",
                "data_type": "RAW_HUMAN_OBSERVATION",
                "muscle": "Gastrocnemius Medialis",
                "independent_participants_n": 1,
                "V_anat_mL": 379.89,
                "verification_status": "VERIFIED_PRIMARY_MEASUREMENT",
                "provenance": "3D T1-MRI VIBE segmentation of Subject 01 right calf."
            },
            {
                "source_id": "SRC-0066",
                "citation": "Andersen & Saltin (1985) J Physiol 366:233-249",
                "data_type": "LITERATURE_REPORTED_VALUE",
                "muscle": "Quadriceps femoris",
                "independent_participants_n": 8,
                "V_anat_mL_estimate": 2170.0,
                "verification_status": "ESTIMATED_FROM_QUADRICEPS_MASS",
                "provenance": "Table 1 quadriceps mass ~2.3 kg (density 1.06 g/mL -> ~2170 mL)."
            },
            {
                "source_id": "SRC-0070",
                "citation": "MuscleMap Zenodo 10.5281/zenodo.10077847",
                "data_type": "SYNTHETIC",
                "verification_status": "UNVERIFIED_PRIMARY_TABLES_RETRACTED",
                "audit_verdict": "Zenodo 10077847 contains deep learning model weights and template files, not a verified open cohort table of n=48 subjects with mean 342.5 mL. Retracted from empirical anchors."
            },
            {
                "source_id": "SRC-0071",
                "citation": "Cenni et al. Figshare 10.6084/m9.figshare.5971480",
                "data_type": "SYNTHETIC",
                "verification_status": "UNVERIFIED_PRIMARY_TABLES_RETRACTED",
                "audit_verdict": "Figshare ID 5971480 is invalid/unresolvable as a public dataset archive. Retracted from empirical anchors."
            }
        ],
        "scaling_ratio_quadriceps_to_gastrocnemius": round(2170.0 / 379.89, 2), # 5.71
        "verdict": "Only Franke et al. 2020 (Subject 01, V_anat = 379.89 mL) is a verified primary volumetric measurement. Cohort distributions from SRC-0070 and SRC-0071 are retracted; status EMPIRICALLY_BOUNDED_DISTRIBUTION is removed."
    }

# Backward compatibility aliases
extract_rehman_2024 = audit_rehman_2024
extract_hug_2021 = audit_hug_2021
extract_anatomical_volumetry = audit_mri_volumetry

def main():
    print("Auditing Cycle 9 empirical datasets and enforcing raw data integrity...")
    rehman = audit_rehman_2024()
    hug = audit_hug_2021()
    mri = audit_mri_volumetry()
    
    out_data = {
        "cycle": 9,
        "date": "2026-11-08",
        "description": "Rigorous data provenance audit for Cycle 9 human measurements",
        "rehman_2024_audit": rehman,
        "hug_2021_audit": hug,
        "mri_volumetry_audit": mri
    }
    
    out_file = OUT_DIR / 'empirical_datasets_cycle9.json'
    out_file.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Saved: {out_file} ({out_file.stat().st_size} bytes)")

if __name__ == '__main__':
    main()
