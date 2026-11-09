#!/usr/bin/env python3
"""
SUBJECT-01 — Research Cycle 9
Master Experiments Execution: EXP-0037 through EXP-0041 (Evidence Gate V2 Compliant).
"""

import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CYCLE_DIR = Path(__file__).resolve().parent

from extract_empirical_data import extract_rehman_2024, extract_hug_2021, extract_anatomical_volumetry
from biophysical_recruitment_model import run_recruitment_experiments
from identifiability_recruitment import analyze_identifiability
from validation_loso import run_loso_cross_validation

def run_all_experiments():
    print("=" * 60)
    print("SUBJECT-01 — RESEARCH CYCLE 9 EXPERIMENTS EXECUTION (V2)")
    print("=" * 60)
    
    # -----------------------------------------------------------------
    # Stage 0: Preflight Verification Record
    # -----------------------------------------------------------------
    preflight = {
        "status": "COMPLETED",
        "question_1_pcr_capacity_reconciliation": {
            "enthalpy_delta_H_kJ_mol": 21.0,
            "enthalpy_definition": "Reaction enthalpy of phosphocreatine hydrolysis and ATP resynthesis (Kodama 1985). Quantifies purely calorimetric heat exchange.",
            "gibbs_delta_G_ATP_nominal_kJ_mol": 54.0,
            "gibbs_delta_G_ATP_span_kJ_mol": [50.0, 64.0],
            "gibbs_definition": "Thermodynamic Gibbs free energy of ATP hydrolysis under physiological intracellular conditions (Meyerspeer 2021). Quantifies maximum mechanical cross-bridge work potential.",
            "ratio_delta_G_to_delta_H": round(54.0 / 21.0, 4), # 2.5714
            "harmonization_verdict": "Formulas strictly segregated: P_mech = eta_loc * v_ATP * (-dG_ATP) uses 54.0 kJ/mol; Q_heat = v_ATP * (-dH_CK) uses 21.0 kJ/mol. Capacity in work units vs heat units explicitly distinct.",
            "buffer_pool_capacity_J": {
                "gibbs_work_capacity_nominal_anat_J": round(0.380 * 33.6 * 54.0, 1), # 689.5 J
                "calorimetric_heat_capacity_nominal_anat_J": round(0.380 * 33.6 * 21.0, 1), # 268.1 J
                "gibbs_work_active_scenario_span_J": [round(0.0836 * 25.4 * 50.0, 1), round(0.1444 * 42.1 * 64.0, 1)] # [106.2, 389.1] J
            }
        },
        "question_2_andersen_saltin_1985_audit": {
            "source_id": "SRC-0066",
            "citation": "Andersen & Saltin (1985), J Physiol 366:233-249",
            "pmid": "4057091",
            "paper_muscle": "Human quadriceps femoris (knee-extensor dynamic model, 5 males)",
            "n_biological_participants": 5,
            "primary_resting_data_in_paper": "Text on page 237 states femoral venous blood flow at rest in sitting position was 0.15 to 0.40 L/min. Table 1 lists subject mass/anthropometry for 5 subjects. Table 2 tabulates exercise from 10 W to 60 W (NO resting row).",
            "audit_verdict_2_4_ml_and_58_ml": "The exact numbers 2.4 mL/100g/min and 58 mL/L do NOT exist as a tabulated resting baseline in Andersen & Saltin 1985. They originate from secondary textbook limb-level approximations (0.24 L/min / 10 kg limb = 2.4 mL/100g/min). N=5 participants confirmed by PubMed.",
            "status_downgrade": "DOWNGRADED_NOT_PRIMARY_RESTING_TABLE / LITERATURE_REVIEW_TRANSFER_ASSUMPTION"
        }
    }

    # -----------------------------------------------------------------
    # EXP-0037: Empirical Acquisition of HD-sEMG & 31P-MRS
    # -----------------------------------------------------------------
    print("\n--- Running EXP-0037: Empirical Acquisition Audit ---")
    rehman_data = extract_rehman_2024()
    hug_data = extract_hug_2021()
    anat_data = extract_anatomical_volumetry()
    
    exp_0037 = {
        "experiment_id": "EXP-0037",
        "title": "Empirical Acquisition Audit of Lower-Limb HD-sEMG Motor Unit Spike Trains and Dynamic 31P-MRS Bioenergetics",
        "data_type": "LITERATURE_REPORTED_VALUE",
        "validation_status": "COMPLETED_LITERATURE_AUDIT_RAW_BLOCKED",
        "datasets": {
            "rehman_2024_31p_mrs": {
                "source_id": "SRC-0069",
                "pmcid": rehman_data["pmcid"],
                "muscle": rehman_data["muscle_group"],
                "protocol": rehman_data["protocol"],
                "n_biological_participants": 1,
                "n_operators": 1,
                "n_trials": len(rehman_data["trials"]),
                "n_records": rehman_data["n_records"],
                "trials_n": len(rehman_data["trials"]),
                "mean_pcr_drop_percent": round(rehman_data["aggregate_statistics"]["pcr_depletion_mean"] * 100, 1),
                "mean_tau_rec_s": rehman_data["aggregate_statistics"]["tau_rec_mean_s"],
                "ph_status": rehman_data["aggregate_statistics"]["acidosis_status"],
                "data_type": rehman_data["data_type"],
                "raw_download_status": rehman_data["raw_timeseries_status"],
                "raw_download_blocker": rehman_data["raw_download_audit"]["conclusion"]
            },
            "hug_2021_hd_semg": {
                "source_id": "SRC-0068",
                "figshare_doi": hug_data["figshare_doi"],
                "muscles": hug_data["muscles_studied"],
                "grid_channels": 64,
                "sampling_hz": 2048,
                "data_type": "LITERATURE_REPORTED_VALUE",
                "storage_type": "LITERATURE_CITATION",
                "source_file": None,
                "sha256": None,
                "n_biological_participants": "UNKNOWN",
                "independent_subjects_n": "UNKNOWN",
                "n_operators": 8,
                "raters_n": 8,
                "n_trials": 11,
                "n_records": 126,
                "note_on_subjects": "Published discharge rates are literature aggregate values from Table 2 evaluated by 8 operators on data reused across 2 prior studies from different male participants (8 raters != 8 subjects).",
                "inter_operator_agreement": hug_data["inter_operator_agreement_median"],
                "gastrocnemius_medialis_rates_hz": {
                    "10_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_medialis"]["10_percent_mvc"]["mean_discharge_rate_hz"],
                    "30_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_medialis"]["30_percent_mvc"]["mean_discharge_rate_hz"],
                    "50_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_medialis"]["50_percent_mvc"]["mean_discharge_rate_hz"],
                    "70_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_medialis"]["70_percent_mvc"]["mean_discharge_rate_hz"]
                },
                "gastrocnemius_lateralis_rates_hz": {
                    "10_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_lateralis"]["10_percent_mvc"]["mean_discharge_rate_hz"],
                    "30_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_lateralis"]["30_percent_mvc"]["mean_discharge_rate_hz"],
                    "50_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_lateralis"]["50_percent_mvc"]["mean_discharge_rate_hz"],
                    "70_mvc": hug_data["table_2_characteristics_after_manual_editing"]["gastrocnemius_lateralis"]["70_percent_mvc"]["mean_discharge_rate_hz"]
                },
                "retracted_historical_rates_hz": hug_data["retracted_historical_unconfirmed_rates"]["historical_values"],
                "raw_download_status": "RAW_ARCHIVE_BLOCKED_BY_CDN_CHALLENGE",
                "raw_download_blocker": "Figshare storage (Experimental_data_Raw.zip, 444 MB) blocked by Cloudflare R2 bot challenge (HTTP 403 Forbidden)"
            },
            "mri_volumetry": {
                "franke_2020_single_subject_gastrocnemius_mL": 379.89,
                "franke_source": "VERIFIED_PRIMARY_3D_SEGMENTATION_MAT_FILE",
                "andersen_saltin_1985_quadriceps_estimate_mL": 2170.0,
                "andersen_saltin_1985_participants_n": 5,
                "quadriceps_to_gastrocnemius_volume_ratio": 5.71,
                "zenodo_musclemap_src0070_status": "RETRACTED_UNVERIFIED_COHORT_TABLE",
                "figshare_cenni_src0071_status": "RETRACTED_INVALID_DATASET_ID"
            }
        }
    }

    # -----------------------------------------------------------------
    # EXP-0038: Forward Biophysical Simulation of MU Recruitment
    # -----------------------------------------------------------------
    print("\n--- Running EXP-0038: Forward Recruitment Simulation ---")
    rec_results = run_recruitment_experiments()
    
    exp_0038 = {
        "experiment_id": "EXP-0038",
        "title": "Biophysical Forward Simulation Model of Motor Unit Recruitment, Volume Conductor Filtering, and SAT Attenuation",
        "data_type": "SYNTHETIC",
        "validation_status": "COMPUTATIONAL_SIMULATION_HYPOTHESIS",
        "scenario_parameters": rec_results["scenario_parameters"],
        "simulation_derived_outputs": rec_results["simulation_derived_outputs"],
        "franke_operating_point_analysis": rec_results["franke_point_analysis"],
        "fatigue_force_emg_dissociation": rec_results["fatigue_dissociation"],
        "core_findings": [
            "At 12.7% measured sEMG RMS, variation in subcutaneous fat thickness (3 to 10 mm) induces a 40.9-fold uncertainty span in true active muscle volume fraction a_eff (0.018 to 0.737) in forward simulation.",
            "During simulated muscle fatigue, sEMG RMS paradoxically increases by +14.0% while mechanical twitch force drops by -35.0% due to conduction velocity slowing and intracellular action potential widening.",
            "Single-channel sEMG RMS is structurally unidentifiable with respect to active muscle volume fraction without high-density multi-channel arrays and independent subcutaneous tissue morphometry."
        ]
    }

    # -----------------------------------------------------------------
    # EXP-0039: Four-Level Identifiability Resolution
    # -----------------------------------------------------------------
    print("\n--- Running EXP-0039: Four-Level Identifiability Resolution ---")
    ident_results = analyze_identifiability()
    
    exp_0039 = {
        "experiment_id": "EXP-0039",
        "title": "Real-Data Identifiability and Profile Likelihood of Local Energy Model with Recruitment Nuisance Parameters",
        "data_type": "COMPUTATIONAL_SIMULATION",
        "validation_status": "IDENTIFIABILITY_AUDITED_NO_IDENTITY_CHANNELS",
        "level_1_structural_conditional_rank": ident_results["level_1_structural_conditional_rank"],
        "level_2_numerical_rank_with_recruitment": ident_results["level_2_numerical_rank_with_recruitment"],
        "level_3_practical_identifiability_with_nuisances": ident_results["level_3_practical_identifiability_with_nuisances"],
        "level_4_empirical_identifiability": ident_results["level_4_empirical_identifiability"]
    }

    # -----------------------------------------------------------------
    # EXP-0040: LOSO Cross-Validation Algorithm Demonstration
    # -----------------------------------------------------------------
    print("\n--- Running EXP-0040: LOSO Demonstration & Blocker Audit ---")
    loso_results = run_loso_cross_validation()
    
    exp_0040 = {
        "experiment_id": "EXP-0040",
        "title": "Leave-One-Subject-Out (LOSO) Cross-Validation Algorithm Demonstration on Synthetic Benchmarks",
        "data_type": "SYNTHETIC",
        "validation_status": "SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED",
        "empirical_validation_status": "BLOCKED_PENDING_RAW_DATA",
        "retraction_note": "PREVIOUS CLAIMS OF EMPIRICAL VALIDATION RETRACTED: evaluated on synthetic exponential curves generated via np.random.RandomState. Real empirical out-of-sample validation requires continuous raw time-series from independent cohorts.",
        "cross_subject_loso_summary": loso_results
    }

    # -----------------------------------------------------------------
    # EXP-0041: SUBJECT-01 Integration & TARGET-CPE45 Boundaries
    # -----------------------------------------------------------------
    print("\n--- Running EXP-0041: SUBJECT-01 Integration & CPE45 Energy Accounting ---")
    # Rigorous physical and physiological energy accounting:
    # 1. External mechanical work: 250 W * 2700 s = 675,000 J (675 kJ).
    # 2. Whole-body metabolic chemical energy expenditure:
    #    Assuming human gross mechanical efficiency eta_gross ~ 20% (0.18 - 0.23):
    #    E_met = W_mech / eta_gross = 675 kJ / 0.20 = 3375 kJ.
    # 3. Whole-body ATP turnover:
    #    With Delta_G_ATP ~ 54 kJ/mol: 3375 kJ / 54 kJ/mol = 62.5 mol ATP.
    # 4. Metabolic resynthesis pathways:
    #    Oxidative phosphorylation: ~3300 kJ (~61.1 mol ATP).
    #    Glycolytic substrate-level phosphorylation (glycogenolysis): ~75 kJ (~1.4 mol ATP during surges/sprints).
    # 5. Local single-muscle phosphocreatine (PCr) buffer capacity:
    #    Active calf muscle volume scenario (V_active = 83.6 - 144.4 mL): 0.106 - 0.389 kJ work potential.
    #    Whole anatomical gastrocnemius medialis (342.5 mL at 33.6 mM and 54 kJ/mol): 0.621 kJ.
    # 6. Calorimetric heat dissipation from PCr hydrolysis:
    #    Reaction enthalpy Delta_R H = 21.0 kJ/mol (Kodama 1985). Heat capacity = 0.242 kJ.
    # 7. CATEGORY ERROR INVARIANT:
    #    Taking the ratio of a static single-muscle local PCr buffer (0.62 kJ) to whole-body 45-min
    #    external work (675 kJ) to deduce '>99% oxidative contribution' is strictly prohibited.
    #    It commits a category error between static local buffer capacity and multi-muscle systemic flux,
    #    confounds mechanical work with metabolic turnover, and ignores anaerobic glycolysis.
    exp_0041 = {
        "experiment_id": "EXP-0041",
        "title": "SUBJECT-01 Integration: Functional Power, Recovery Limits, and TARGET-CPE45 Boundaries",
        "data_type": "COMPUTATIONAL_SIMULATION",
        "validation_status": "COMPLETED_MACRO_BUDGET_ACCOUNTING",
        "cpe45_energy_accounting": {
            "scenario_status": "ESTIMATED_SCENARIO_BALANCE_NOT_MEASURED",
            "external_mechanical_work_kJ": 675.0,
            "external_work_description": "250 W maintained over 2700 s (45 minutes) = 675 kJ. Illustrative test scenario.",
            "whole_body_metabolic_cost_nominal_kJ": 3375.0,
            "whole_body_metabolic_cost_span_kJ": [2934.8, 3750.0],
            "assumed_gross_mechanical_efficiency_eta_gross": 0.20,
            "whole_body_atp_turnover_moles": 62.5,
            "oxidative_resynthesis_nominal_kJ": 3300.0,
            "glycolysis_contribution_nominal_kJ": 75.0,
            "measured_empirical_aerobic_fraction": None,
            "measured_aerobic_fraction_status": "NOT_EMPIRICALLY_MEASURED_IN_CPE45",
            "scenario_assumptions": "Theoretical scenario balance calculated at assumed nominal gross efficiency eta_gross = 20% and standard literature endurance partitioning. Not empirically measured in CPE45.",
            "local_pcr_chemical_buffer_work_capacity_kJ": {
                "active_calf_volume_scenario_kJ": [0.106, 0.389],
                "anatomical_whole_gm_kJ": 0.621
            },
            "local_pcr_hydrolysis_reaction_enthalpy_delta_R_H_kJ_mol": 21.0,
            "local_heat_dissipation_capacity_anat_kJ": 0.242,
            "category_error_static_pcr_to_external_work_prohibited": True,
            "scaling_barrier_explanation": (
                "Local single-muscle PCr buffer is a rapid transient energy store (duration ~5-30 s). "
                "45-minute continuous endurance work requires systemic aerobic ATP resynthesis (metabolic expenditure ~3375 kJ), "
                "constrained by cardiac output, pulmonary gas exchange, and whole-body vascular distribution. "
                "Inferring >99% oxidative contribution solely by dividing single-muscle static PCr buffer by 45-min whole-body "
                "external work is scientifically invalid: it confuses static local stock with dynamic systemic flux, "
                "confounds mechanical work with metabolic cost, and ignores systemic glycolysis."
            )
        },
        "target_cpe45_status": "NOT EXTERNALLY VALIDATED",
        "biological_interventions": "NO_GO_MAINTAINED"
    }

    all_results = {
        "cycle": 9,
        "date": "2026-11-09",
        "preflight": preflight,
        "experiments": {
            "EXP-0037": exp_0037,
            "EXP-0038": exp_0038,
            "EXP-0039": exp_0039,
            "EXP-0040": exp_0040,
            "EXP-0041": exp_0041
        }
    }

    out_file = CYCLE_DIR / 'experiment_results.json'
    out_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    print(f"\nSuccessfully executed all Cycle 9 experiments!")
    print(f"Results written to: {out_file} ({out_file.stat().st_size} bytes)")
    return all_results

if __name__ == '__main__':
    run_all_experiments()
