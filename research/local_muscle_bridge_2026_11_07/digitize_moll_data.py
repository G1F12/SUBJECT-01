"""Digitization and extraction of experimental measurements from
Kevin Moll's research (Moll et al. 2017, Dissertation 2018, Stutzig et al. 2016/2017)
and Cannon et al. (2014, PMC4262339).

SCIENTIFIC AUDIT & PROVENANCE CLARIFICATION:
1. Exact published table numbers (Table 2-1, 3-1, 3-2, 4-1..4-3, 5-1 of Moll 2018
   and Table 1 of Cannon et al. 2014) are transcribed directly from source documents.
2. Published statistical correlations (R2 = 0.73, R2 = 0.55, R2 = 0.65) are published
   literature findings by Moll et al. (2017), NOT new discoveries of this repository.
3. The 10 individual data coordinates for Fig 3-5 are APPROXIMATE GRAPHICAL DIGITIZATIONS
   from scatter plots; linear regressions on them yield inflated R2 (0.919, 0.978)
   due to manual graphical placement bias. They must NOT be cited as empirical findings.
4. Cannon et al. (2014) is openly available on PubMed Central (PMC4262339).
"""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent

def build_extracted_dataset():
    data = {
        'metadata': {
            'audit_date': '2026-11-07',
            'audit_cycle': 'Cycle 7 Final Consistency Audit',
            'description': 'Extracted and verified experimental measurements from Kevin Moll (2017, 2018) and Daniel T. Cannon et al. (2014)',
            'data_categories': {
                'PUBLISHED_TABLE_DATA': 'Exact numbers transcribed from published tables in peer-reviewed literature or doctoral dissertation',
                'PUBLISHED_STATISTICAL_CORRELATIONS': 'Exact statistical coefficients (R2, p-values) published by study authors',
                'APPROXIMATE_GRAPHICAL_DIGITIZATION': 'Visual estimates from published figures; APPROXIMATE ONLY; not primary numerical tables',
                'PMC_FULL_TEXT_TABLE': 'Verified numbers from PMC open access full text (PMC4262339)'
            },
            'physiological_concept_separation': {
                'atp_turnover': 'Instantaneous rate of actomyosin and ion transport ATPase consumption (mM/min or mmol/s). In steady-state exercise, matched by total resynthesis rate: ATP_turnover = Q_ox + L_glyc + D_pcr.',
                'atp_resynthesis': 'Biochemical replenishment pathways of ATP: mitochondrial oxidative phosphorylation (Q), anaerobic glycolysis (L), and net creatine kinase flux (D).',
                'pcr_pool_capacity': 'Static total resting chemical stock of phosphocreatine: [PCr]_rest * V_active * dG_PCr (205-1021 J in human gastrocnemius). This is a capacity stock, not a continuous power flux.',
                'net_pcr_depletion': 'Net difference between pre-exercise and end-exercise [PCr]: Delta[PCr] ~ 20-25 mM (60-85% depletion).',
                'chemical_free_energy': 'Thermodynamic Gibbs free energy of hydrolysis: dG_ATP ~ -50 to -64 kJ/mol, dG_PCr ~ -34 to -45 kJ/mol.',
                'external_mechanical_work': 'Integrated power delivered to the ergometer: W_ext = integral P(t) dt (e.g. 18 W * 180 s = 3240 J).',
                'whole_body_metabolic_cost': 'Total systemic energy consumed across all organ systems (locomotor muscle, diaphragm, intercostals, myocardium, postural stabilizers): integral Delta_VO2 * kappa_O2 dt (~34 kJ).'
            },
            'line_count_note': 'File contains structured JSON records across multiple studies. It does NOT represent hundreds of independent participant cohorts.'
        },

        # 1. MOLL 2017 / 2018 DISSERTATION CHAPTER 2 (Table 2-1)
        'moll2018_chapter2_ergometer_pilot': {
            'status': 'PUBLISHED_TABLE_DATA',
            'source': 'Moll 2018 Dissertation Table 2-1, p. 30',
            'design': 'Plantar flexion at 1 Hz, 35 deg deflection, 3 min duration, 1 subject, 3 repetitions each load level',
            'loads': [
                {
                    'load_level': '15% FMVC',
                    'power_W': {'mean': 15.5, 'range': [14.4, 16.5]},
                    'cadence_Hz': {'mean': 0.92, 'range': [0.91, 0.94]},
                    'pH_rest': {'mean': 6.93, 'range': [6.93, 6.97]},
                    'pH_load_end': {'mean': 6.77, 'range': [6.77, 6.84]},
                    'delta_pH': 0.16,
                    'tau_PCr_depletion_s': {'mean': 56.2, 'range': [49.5, 61.1]},
                    'tau_Pi_accumulation_s': {'mean': 43.6, 'range': [36.7, 49.1]}
                },
                {
                    'load_level': '25% FMVC',
                    'power_W': {'mean': 21.8, 'range': [21.5, 22.2]},
                    'cadence_Hz': {'mean': 0.95, 'range': [0.94, 0.97]},
                    'pH_rest': {'mean': 6.92, 'range': [6.87, 6.92]},
                    'pH_load_end': {'mean': 6.55, 'range': [6.51, 6.59]},
                    'delta_pH': 0.37,
                    'tau_PCr_depletion_s': {'mean': 23.5, 'range': [19.3, 25.9]},
                    'tau_Pi_accumulation_s': {'mean': 25.0, 'range': [23.9, 26.3]}
                }
            ]
        },

        # 2. MOLL 2017 / 2018 CHAPTER 3 (Table 3-1, Table 3-2, p. 38-40)
        'moll2017_chapter3_combined_study': {
            'status': 'PUBLISHED_TABLE_DATA',
            'source': 'Moll et al. 2017 (NMR Biomed) and Moll 2018 Dissertation Table 3-1, 3-2',
            'participants': {'n': 10, 'sex': 'male', 'age_years': {'mean': 29.0, 'sd': 5.0}},
            'exercise_protocol': 'Right calf plantar flexion, 80 bpm, 25 deg sector, 0.6 bar resistance, peak force 163 +/- 23 N, ~18 W external power. 10 min rest, 3 min load, 20 min recovery.',
            'instrumentation': {
                'mrs': 'Siemens Magnetom Tim Trio (3T), 1H/31P surface coil, DRESS localized MRS, GM, TR=5s',
                'spirometry': 'Ganshorn PowerCube with 5m sampling line outside magnet',
                'line_delay_measured_ta_s': 2.075,
                'line_dispersion_measured_t10_90_s': 0.307
            },
            'published_group_means': {
                'pH_rest': {'mean': 7.03, 'sd': 0.02},
                'pH_load_end': {'mean': 6.45, 'sd': 0.22},
                'tau_PCr_fast_s': {'mean': 93.0, 'sd': 39.0},
                'tau_PCr_slow_s': {'mean': 460.0, 'sd': 241.0},
                'f_PCr_fast': {'mean': 0.71, 'sd': 0.10},
                'VO2_rest_L_min': {'mean': 0.28, 'sd': 0.05},
                'VCO2_rest_L_min': {'mean': 0.22, 'sd': 0.05},
                'VO2_load_L_min': {'mean': 1.05, 'sd': 0.30},
                'VCO2_load_L_min': {'mean': 1.11, 'sd': 0.33},
                'VE_rest_L_min': {'mean': 7.6, 'sd': 1.8},
                'VE_load_L_min': {'mean': 29.8, 'sd': 8.1},
                'excess_CO2_L': {'mean': 2.24, 'sd': 1.67},
                'tau_VO2_fast_s': {'mean': 56.0, 'sd': 10.0},
                'tau_VO2_slow_s': {'mean': 330.0, 'sd': 153.0},
                'tau_VCO2_fast_s': {'mean': 86.0, 'sd': 33.0},
                'tau_VCO2_slow_s': {'mean': 260.0, 'sd': 105.0},
                'f_VO2_fast': {'mean': 0.93, 'sd': 0.13},
                'f_VCO2_fast': {'mean': 0.86, 'sd': 0.15}
            },
            'published_statistical_correlations': {
                'tau_PCr_fast_vs_pH_end': {
                    'source': 'Moll et al. 2017, p. 51',
                    'R2': 0.73,
                    'p_val': 0.005,
                    'sign': 'negative',
                    'interpretation': 'Strong inverse correlation between post-exercise pH and fast PCr recovery time constant'
                },
                'tau_VO2_fast_vs_tau_PCr_fast': {
                    'source': 'Moll et al. 2017, p. 51',
                    'R2': 0.55,
                    'p_val': 0.01,
                    'sign': 'positive',
                    'interpretation': 'Moderate positive coupling between local muscle PCr resynthesis and pulmonary VO2 recovery fast component'
                },
                'excess_CO2_vs_pH_end': {
                    'source': 'Moll et al. 2017, p. 51',
                    'R2': 0.65,
                    'p_val': 0.01,
                    'sign': 'negative',
                    'n_evaluated': 9,
                    'outlier_note': 'One subject excluded due to hyperventilation (VO2-VCO2 peak difference 0.4 L/min)',
                    'interpretation': 'Significant inverse correlation between expired excess non-metabolic CO2 and end-exercise muscle pH'
                }
            },
            'approximate_graphical_digitization_fig3_5': {
                'status': 'APPROXIMATE_DIGITIZATION',
                'warning': 'These coordinates were estimated visually from scatter plot Fig 3-5 in Moll 2017. They are NOT primary numeric table values. Regressions on these points yield inflated R2 values (0.919 and 0.978) due to manual graphical placement bias. DO NOT cite regressions from these points as empirical findings.',
                'estimated_points': [
                    {'subject': 1, 'pH_end_est': 6.12, 'tau_PCr_fast_s_est': 135.0, 'tau_VO2_fast_s_est': 70.0, 'excess_CO2_L_est': 4.9},
                    {'subject': 2, 'pH_end_est': 6.20, 'tau_PCr_fast_s_est': 128.0, 'tau_VO2_fast_s_est': 65.0, 'excess_CO2_L_est': 4.1},
                    {'subject': 3, 'pH_end_est': 6.25, 'tau_PCr_fast_s_est': 148.0, 'tau_VO2_fast_s_est': 70.0, 'excess_CO2_L_est': 3.7},
                    {'subject': 4, 'pH_end_est': 6.35, 'tau_PCr_fast_s_est': 105.0, 'tau_VO2_fast_s_est': 61.0, 'excess_CO2_L_est': 3.1},
                    {'subject': 5, 'pH_end_est': 6.42, 'tau_PCr_fast_s_est': 90.0,  'tau_VO2_fast_s_est': 55.0, 'excess_CO2_L_est': 2.4},
                    {'subject': 6, 'pH_end_est': 6.50, 'tau_PCr_fast_s_est': 85.0,  'tau_VO2_fast_s_est': 52.0, 'excess_CO2_L_est': 2.0},
                    {'subject': 7, 'pH_end_est': 6.60, 'tau_PCr_fast_s_est': 75.0,  'tau_VO2_fast_s_est': 50.0, 'excess_CO2_L_est': 1.6},
                    {'subject': 8, 'pH_end_est': 6.68, 'tau_PCr_fast_s_est': 55.0,  'tau_VO2_fast_s_est': 47.0, 'excess_CO2_L_est': 1.0},
                    {'subject': 9, 'pH_end_est': 6.75, 'tau_PCr_fast_s_est': 60.0,  'tau_VO2_fast_s_est': 45.0, 'excess_CO2_L_est': 0.8},
                    {'subject': 10, 'pH_end_est': 6.80, 'tau_PCr_fast_s_est': 49.0, 'tau_VO2_fast_s_est': 42.0, 'excess_CO2_L_est': 0.5}
                ]
            }
        },

        # 3. MOLL 2018 DISSERTATION CHAPTER 4 (ATHLETE COMPARISON, Tables 4-1, 4-2, 4-3, p. 62-67)
        'moll2018_chapter4_athlete_comparison': {
            'status': 'PUBLISHED_TABLE_DATA',
            'source': 'Moll 2018 Dissertation Tables 4-1, 4-2, 4-3',
            'cohort': {
                'sprinters': {'n': 11, 'age_years': {'mean': 22.0, 'sd': 4.0}, 'VO2peak_mL_min_kg': {'mean': 48.0, 'sd': 5.0}},
                'endurance': {'n': 10, 'age_years': {'mean': 26.0, 'sd': 5.0}, 'VO2peak_mL_min_kg': {'mean': 61.0, 'sd': 5.0}}
            },
            'mrs_kinetics_by_muscle': {
                'GM': {
                    'sprinters': {'tau_PCr_s': {'mean': 48.0, 'sd': 16.0}, 'pH_end': {'mean': 6.78, 'sd': 0.15}, 'delta_PCr_pct': {'mean': 67.0, 'sd': 11.0}},
                    'endurance': {'tau_PCr_s': {'mean': 32.0, 'sd': 9.0},  'pH_end': {'mean': 6.88, 'sd': 0.10}, 'delta_PCr_pct': {'mean': 58.0, 'sd': 12.0}}
                },
                'SOL': {
                    'sprinters': {'tau_PCr_s': {'mean': 35.0, 'sd': 12.0}, 'pH_end': {'mean': 6.92, 'sd': 0.08}, 'delta_PCr_pct': {'mean': 44.0, 'sd': 14.0}},
                    'endurance': {'tau_PCr_s': {'mean': 24.0, 'sd': 7.0},  'pH_end': {'mean': 6.98, 'sd': 0.05}, 'delta_PCr_pct': {'mean': 38.0, 'sd': 10.0}}
                }
            }
        },

        # 4. MOLL 2018 DISSERTATION CHAPTER 5 (NMES & Pi SPLITTING, Table 5-1, p. 80-84)
        'moll2018_chapter5_nmes_heterogeneity': {
            'status': 'PUBLISHED_TABLE_DATA',
            'source': 'Moll 2018 Dissertation Table 5-1',
            'participants': {'n': 8, 'intervention': 'Neuromuscular electrical stimulation (NMES) of calf muscle'},
            'pi_splitting': {
                'n_components': 3,
                'description': 'Three distinct Pi peaks observed reflecting spatial/fiber-type activation heterogeneity',
                'pH_pools': {
                    'Pi_1_high_acidosis': {'pH': {'mean': 6.22, 'sd': 0.14}, 'fraction_pct': 38.0},
                    'Pi_2_moderate':      {'pH': {'mean': 6.61, 'sd': 0.12}, 'fraction_pct': 42.0},
                    'Pi_3_minimal':       {'pH': {'mean': 6.94, 'sd': 0.06}, 'fraction_pct': 20.0}
                }
            }
        },

        # 5. CANNON ET AL. 2014 (PMC4262339 Table 1)
        'cannon2014_pmc4262339_atp_turnover': {
            'status': 'PMC_FULL_TEXT_TABLE',
            'source': 'Cannon et al. (2014) J Physiol 592:5287-5300, PMC4262339, Table 1',
            'open_access': True,
            'pmcid': 'PMC4262339',
            'doi': '10.1113/jphysiol.2014.279174',
            'participants': {'n': 14, 'males': 13, 'females': 1, 'age_years': {'mean': 27.0, 'sd': 8.0}, 'mass_kg': {'mean': 75.0, 'sd': 12.0}},
            'exercise': 'Bilateral knee extension inside 1.5T scanner, 40 rpm, moderate (90% GET) and heavy (GET + 50% Delta) constant work rates',
            'cross_study_isolation_warning': 'STUDY ISOLATION: Cannon et al. (2014) investigated bilateral knee extension (quadriceps femoris), NOT plantarflexion (calf/gastrocnemius). The quantitative ATP turnover flux rates (mM/min) and oxidative fractions cannot be quantitatively transferred or equated to Moll\'s plantarflexion cohort due to differences in muscle group, mass, fiber composition, and biomechanics. It serves solely as a qualitative/mechanistic demonstration that steady dynamic exercise ATP turnover is predominantly sustained by oxidative phosphorylation rather than PCr buffer depletion.',
            'atp_turnover_rates_mM_per_min': {
                'moderate_3min': {'Q_oxidative': {'mean': 23.0, 'sd': 14.0}, 'D_PCr': {'mean': 0.6, 'sd': 1.2}, 'L_glycolytic': {'mean': 1.0, 'sd': 1.3}, 'ATP_tot': {'mean': 24.0, 'sd': 14.0}},
                'moderate_8min': {'Q_oxidative': {'mean': 17.0, 'sd': 13.0}, 'D_PCr': {'mean': 0.2, 'sd': 1.0}, 'L_glycolytic': {'mean': 0.3, 'sd': 0.6}, 'ATP_tot': {'mean': 17.0, 'sd': 14.0}},
                'heavy_3min':    {'Q_oxidative': {'mean': 35.0, 'sd': 17.0}, 'D_PCr': {'mean': 1.1, 'sd': 2.6}, 'L_glycolytic': {'mean': 1.5, 'sd': 1.3}, 'ATP_tot': {'mean': 38.0, 'sd': 16.0}},
                'heavy_8min':    {'Q_oxidative': {'mean': 42.0, 'sd': 13.0}, 'D_PCr': {'mean': 0.7, 'sd': 0.9}, 'L_glycolytic': {'mean': 1.3, 'sd': 1.7}, 'ATP_tot': {'mean': 44.0, 'sd': 14.0}}
            },
            'key_insight': 'Oxidative phosphorylation (Q) provides 88% to 95% of ATP turnover during constant-rate exercise at 3 min and 8 min; PCr breakdown (D) provides only 1.5% to 3.0% of steady-state turnover flux.'
        }
    }
    return data

def main():
    print("Building extracted experimental dataset...")
    data = build_extracted_dataset()
    out_file = BASE / 'moll2018_extracted_measurements.json'
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Dataset successfully written to {out_file} ({out_file.stat().st_size} bytes)")

if __name__ == '__main__':
    main()
