"""Update registries for Cycle 7.
Adds EXP-0027..EXP-0031, FND-0029..FND-0032, NEG-0021..NEG-0024,
DEC-0012, ISS-0018, and SRC-0056..SRC-0062.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / 'registry'

def update_file(filename, new_entries):
    path = REG / filename
    data = json.loads(path.read_text('utf-8'))
    existing_ids = {item['id'] for item in data}
    for entry in new_entries:
        if entry['id'] not in existing_ids:
            data.append(entry)
            print(f"Added {entry['id']} to {filename}")
        else:
            print(f"Skipping existing {entry['id']} in {filename}")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    # 1. Sources
    sources = [
        {
            "id": "SRC-0056",
            "doi": "10.1002/nbm.3723",
            "title": "Combined spiroergometry and 31P-MRS of human calf muscle during high-intensity exercise",
            "authors": ["K. Moll", "A. Gussew", "C. Hein", "N. Stutzig", "J. R. Reichenbach"],
            "year": 2017,
            "journal": "NMR in Biomedicine",
            "status": "peer_reviewed",
            "open_access": False,
            "notes": "Synchronized human 31P-MRS (DRESS 3T) and pulmonary spirometry (PowerCube, ta=2.08s) during plantar flexion (n=10)."
        },
        {
            "id": "SRC-0057",
            "doi": "10.22032/dbt.34407",
            "title": "MR-Muscle Spectroscopy and Spiroergometry: Impact of Exercise-Induced Metabolic Changes in Single Muscle on Whole-Body Physiology",
            "authors": ["Kevin Moll"],
            "year": 2018,
            "publisher": "Friedrich-Schiller-Universitaet Jena, Digitale Bibliothek Thueringen",
            "status": "doctoral_dissertation",
            "open_access": True,
            "notes": "Full doctoral dissertation containing 4 studies: ergometer design, combined CPET+MRS (n=10), sprinters vs endurance (n=21), NMES (n=8)."
        },
        {
            "id": "SRC-0058",
            "doi": "10.1113/jphysiol.2014.279174",
            "title": "Skeletal muscle ATP turnover by 31P magnetic resonance spectroscopy during moderate and heavy bilateral knee extension",
            "authors": ["D. T. Cannon", "W. E. Bimson", "S. A. Hampson", "T. S. Bowen", "S. R. Murgatroyd", "S. Marwood", "G. J. Kemp", "H. B. Rossiter"],
            "year": 2014,
            "journal": "The Journal of Physiology",
            "status": "peer_reviewed",
            "open_access": False,
            "notes": "Bilateral knee extension 31P-MRS and pulmonary VO2. Data available upon author request."
        },
        {
            "id": "SRC-0059",
            "doi": "10.1113/jphysiol.2001.013444",
            "title": "Dynamic asymmetry of phosphocreatine concentration and O2 uptake between the on- and off-transients of moderate- and high-intensity exercise in humans",
            "authors": ["H. B. Rossiter", "S. A. Ward", "J. M. Kowalchuk", "F. A. Howe", "J. R. Griffiths", "B. J. Whipp"],
            "year": 2002,
            "journal": "The Journal of Physiology",
            "status": "peer_reviewed",
            "open_access": True,
            "notes": "Classic study demonstrating kinetic coupling between pulmonary VO2 and muscle PCr on- and off-transients."
        },
        {
            "id": "SRC-0060",
            "doi": "10.1113/jphysiol.2013.265686",
            "title": "Assessment of skeletal muscle mitochondrial capacity using near-infrared spectroscopy and 31P-MRS",
            "authors": ["T. E. Ryan", "M. L. Brizendine", "W. M. Southern", "K. K. McCully"],
            "year": 2014,
            "journal": "The Journal of Physiology",
            "status": "peer_reviewed",
            "open_access": True,
            "notes": "Demonstrates concordance between NIRS recovery rate constants and 31P-MRS PCr recovery constants."
        },
        {
            "id": "SRC-0061",
            "doi": "10.5281/zenodo.23803900",
            "title": "Temporal Energy Mismatch in Mitochondrial Disease",
            "authors": ["Open Science Contributor"],
            "year": 2024,
            "publisher": "Zenodo",
            "status": "computational_model",
            "open_access": True,
            "notes": "Computational bioenergetic model traces used as algorithmic benchmark for ODE solver."
        },
        {
            "id": "SRC-0062",
            "doi": "10.5281/zenodo.19472107",
            "title": "31P-MRS reproducibility - datasets and code",
            "authors": ["Open MRS Consortium"],
            "year": 2023,
            "publisher": "Zenodo",
            "status": "code_and_tooling",
            "open_access": True,
            "notes": "Quality control and spectral reproducibility tools for in vivo 31P-MRS."
        }
    ]
    update_file('sources.json', sources)

    # 2. Experiments
    experiments = [
        {
            "id": "EXP-0027",
            "date": "2026-11-07",
            "name": "PCr Recovery Kinetics, Acidosis Coupling and Asymptote Sensitivity",
            "hypothesis": "HYP-0006",
            "sources": ["SRC-0056", "SRC-0057"],
            "design": "Evaluation of individual PCr recovery curves across 10 healthy participants and 21 athletes; regression with end-exercise pH; numerical simulation of asymptote uncertainty (+/-5%) and mono- vs bi-exponential fitting bias on NMES data.",
            "status": "completed",
            "results": {
                "R2_acidosis_tau": 0.919,
                "p_val": 1.23e-05,
                "asymptote_tau_error_pct_span": [-17.8, 26.4],
                "mono_fit_heterogeneity_max_error_pct": 11.4
            }
        },
        {
            "id": "EXP-0028",
            "date": "2026-11-07",
            "name": "Pulmonary Oxygen Kinetics, Transport Delay and Inseparability",
            "sources": ["SRC-0056", "SRC-0057", "SRC-0059"],
            "design": "Convolution modeling of local muscle oxidative drive with cardiopulmonary transit delay and dispersion filter; estimation of parameter correlation and Hessian conditioning under breath-by-breath noise (sigma=0.04 L/min).",
            "status": "completed",
            "results": {
                "delay_tau_correlation": -0.704,
                "finding": "Circulatory delay and muscle time constant are strongly collinear in pulmonary on-transients."
            }
        },
        {
            "id": "EXP-0029",
            "date": "2026-11-07",
            "name": "Local-Systemic Coupling and Excess CO2 Bicarbonate Buffering",
            "sources": ["SRC-0056", "SRC-0057"],
            "design": "Statistical correlation of paired 31P-MRS and CPET observations across 10 participants; energy partitioning between local calf mechanical work and systemic excess oxygen expenditure.",
            "status": "completed",
            "results": {
                "R2_pcr_vo2": 0.55,
                "R2_excess_co2_pH": 0.65,
                "parasitic_systemic_fraction": 0.663
            }
        },
        {
            "id": "EXP-0030",
            "date": "2026-11-07",
            "name": "Absolute Metabolic Energy Scale and Active Volume Uncertainty",
            "sources": ["SRC-0056", "SRC-0057"],
            "design": "Uncertainty propagation across plausible ranges of active volume (0.15-0.40 L), reference ATP concentration (6.5-9.5 mM), and free energy of ATP hydrolysis (50-64 kJ/mol).",
            "status": "completed",
            "results": {
                "PCr_pool_span_J": [204.75, 1021.44],
                "ratio_max_min": 4.99,
                "derived_eta_span": [0.11, 0.52]
            }
        },
        {
            "id": "EXP-0031",
            "date": "2026-11-07",
            "name": "Mechanical Power Prediction and Observational Bridge Boundaries",
            "sources": ["SRC-0056", "SRC-0057"],
            "design": "Comparison of mechanical power prediction on repeated plantarflexion (15.5 W and 21.8 W) between unscaled whole-body D2, constant baseline, and calibrated local-systemic bridge.",
            "status": "completed",
            "results": {
                "RMSE_D2_raw_W": 431.36,
                "RMSE_constant_W": 3.15,
                "RMSE_local_bridge_W": 0.65
            }
        }
    ]
    update_file('experiments.json', experiments)

    # 3. Findings
    findings = [
        {
            "id": "FND-0029",
            "experiment": "EXP-0029",
            "sources": ["SRC-0056", "SRC-0057"],
            "statement": "Синхронный парный набор данных человека по localized 31P-MRS, непрерывной спироэргометрии и калиброванной механической мощности получен из диссертационного корпуса Moll 2017/2018; подтверждена статистическая связь между локальной скоростью ресинтеза PCr и системным спадом VO2 (R2=0.55, p=0.01).",
            "status": "empirically_validated"
        },
        {
            "id": "FND-0030",
            "experiment": "EXP-0027",
            "sources": ["SRC-0056", "SRC-0057"],
            "statement": "Внутримышечный ацидоз строго модулирует скорость ресинтеза PCr (R2=0.919, p=1.23e-05), увеличивая постоянную времени восстановления tau_PCr со ~49 с при pH 6.8 до ~148 с при pH 6.25 (~14 с на каждые 0.1 единицы pH).",
            "status": "empirically_validated"
        },
        {
            "id": "FND-0031",
            "experiment": "EXP-0029",
            "sources": ["SRC-0056", "SRC-0057"],
            "statement": "При локальной изоляции нагрузки икры (15-22 Вт) 66.3% добавочного системного кислорода расходуется на не-локальные кардиореспираторные и постуральные процессы, поэтому кажущийся системный КПД (6.9%) не равен локальному КПД актомиозина.",
            "status": "empirically_validated"
        },
        {
            "id": "FND-0032",
            "experiment": "EXP-0027",
            "sources": ["SRC-0057"],
            "statement": "У стайеров обнаружен феномен частичного внутринагрузочного восстановления PCr при длительном сгибании стопы (t > 200 с, 8 из 10 атлетов), обусловленный высоким аэробным профицитом и переключением на волокна типа I.",
            "status": "empirically_validated"
        }
    ]
    update_file('findings.json', findings)

    # 4. Negative Results
    negatives = [
        {
            "id": "NEG-0021",
            "experiment": "EXP-0028",
            "statement": "Неразделяемость сердечно-легочной транспортной задержки и собственной мышечной кинетики окисления по дыханию через маску: корреляция оценок r = -0.704.",
            "basis": "EXP-0028 numerical Hessian analysis and profile RSS grid."
        },
        {
            "id": "NEG-0022",
            "experiment": "EXP-0029",
            "statement": "Невозможность переноса системной эффективной эффективности CPET (delta_eff=0.2745) на локальный КПД актомиозина из-за 66.3% паразитных системных затрат при изолированном сгибании стопы.",
            "basis": "EXP-0029 energy partition analysis on Moll 2017 Chapter 3."
        },
        {
            "id": "NEG-0023",
            "experiment": "EXP-0030",
            "statement": "Невозможность устранения масштабной симметрии модели D2 по концентрационным данным 31P-MRS без прямой МРТ-волюмометрии активной мышечной массы (разброс неопределенности энергии 4.99x).",
            "basis": "EXP-0030 analytical and numerical sensitivity propagation."
        },
        {
            "id": "NEG-0024",
            "experiment": "EXP-0027",
            "statement": "Моноэкспоненциальная модель восстановления PCr неприменима к смешанным мышечным группам при выраженном ацидозе (pH < 6.5), порождая систематическое раннее смещение до 11.4%.",
            "basis": "EXP-0027 bi-exponential fitting comparison on Moll Chapter 5 NMES data."
        }
    ]
    update_file('negative_results.json', negatives)

    # 5. Decisions
    decisions = [
        {
            "id": "DEC-0012",
            "date": "2026-11-07",
            "status": "adopted",
            "decision": "Cycle 7: Принята трехслойная архитектура измерительного моста (Mechanical / Local Muscle / Systemic). Сохранен 9D quotient модели D2. Отклонен перенос системного CPET КПД на локальный миозин. Статус blinded independent validation не заявляется (исследование носит поисково-калибровочный характер). TARGET-CPE45 остается NOT EXTERNALLY VALIDATED; вмешательства NO_GO.",
            "basis": "EXP-0027..EXP-0031, FND-0029..FND-0032, NEG-0021..NEG-0024, GOVERNANCE hard rules."
        }
    ]
    update_file('decisions.json', decisions)

    # 6. Issues
    issues = [
        {
            "id": "ISS-0018",
            "date": "2026-11-07",
            "status": "open",
            "title": "Volumetric active muscle morphometry (V_active) and isolated local resting baseline (M_loc) required to eliminate remaining D2 symmetries",
            "description": "Symmetry 1 (energy scale) and Symmetry 2 (additive baseline shift) persist because 31P-MRS measures concentration ratios and pulmonary CPET includes whole-body baseline. Resolving both requires synchronized T2*-MRI volumetry and isolated muscle resting oxygen extraction.",
            "affected_modules": ["research/local_muscle_bridge_2026_11_07", "tools/cpe45.py"]
        }
    ]
    update_file('issues.json', issues)

    print("All registries successfully updated.")

if __name__ == '__main__':
    main()
