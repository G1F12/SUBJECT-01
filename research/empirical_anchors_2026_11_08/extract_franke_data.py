import io, zipfile
from pathlib import Path
import h5py
import numpy as np
import json

ROOT = Path(__file__).resolve().parents[2]
supp_zip = ROOT / 'tmp' / 'observability_raw' / 'plantar_supp.bin'

with zipfile.ZipFile(supp_zip, 'r') as z:
    inner_zip_bytes = z.read('Data_Sheet_1.ZIP')
    with zipfile.ZipFile(io.BytesIO(inner_zip_bytes), 'r') as z2:
        # Load energy
        tmp_energy = ROOT / 'tmp' / 'temp_energy_extract.mat'
        tmp_energy.write_bytes(z2.read('ElectronicSupplementaryMaterial/experimental_data_energy.mat'))
        with h5py.File(tmp_energy, 'r') as f:
            energy_exp = np.array(f['Energy_exp']).flatten().tolist()
        if tmp_energy.exists(): tmp_energy.unlink()

        # Load EMG (gm_norm_MVC)
        tmp_emg = ROOT / 'tmp' / 'temp_emg_extract.mat'
        tmp_emg.write_bytes(z2.read('ElectronicSupplementaryMaterial/experimental_data_gm_norm_MVC.mat'))
        with h5py.File(tmp_emg, 'r') as f:
            emg_arr = np.array(f['gm_norm_MVC']).flatten()
            emg_stats = {
                'count': int(len(emg_arr)),
                'min': float(np.min(emg_arr)),
                'max': float(np.max(emg_arr)),
                'mean': float(np.mean(emg_arr)),
                'std': float(np.std(emg_arr)),
                'rms': float(np.sqrt(np.mean(emg_arr**2))),
                'median': float(np.median(emg_arr)),
                'p25': float(np.percentile(emg_arr, 25)),
                'p75': float(np.percentile(emg_arr, 75))
            }
        if tmp_emg.exists(): tmp_emg.unlink()

        # Load Kinematics (ankle_angle_60sec)
        tmp_ang = ROOT / 'tmp' / 'temp_ang_extract.mat'
        tmp_ang.write_bytes(z2.read('ElectronicSupplementaryMaterial/experimental_data_ankle_angle_60sec.mat'))
        with h5py.File(tmp_ang, 'r') as f:
            ang_arr = np.array(f['ankle_angle_60sec']).flatten()
            ang_stats = {
                'count': int(len(ang_arr)),
                'min_deg': float(np.min(ang_arr)),
                'max_deg': float(np.max(ang_arr)),
                'mean_deg': float(np.mean(ang_arr)),
                'std_deg': float(np.std(ang_arr)),
                'rom_deg': float(np.max(ang_arr) - np.min(ang_arr))
            }
        if tmp_ang.exists(): tmp_ang.unlink()

out_data = {
    'source': 'Franke et al. (2020) Front. Bioeng. Biotechnol. 8:622, PMC7332772',
    'doi': '10.3389/fbioe.2020.00622',
    'subject_info': {
        'n': 1,
        'exercise_modality': 'Dynamic submaximal plantarflexion (1 Hz metronome, 60 s active phase)',
        'target_muscle': 'M. gastrocnemius medialis (right calf)',
        'experimental_separation_note': 'In Franke 2020, 3D MRI, sEMG+kinematics, and 31P-MRS were recorded in separate experimental trials, not simultaneously.'
    },
    'mri_anatomical_parameters': {
        'sequence': '3D T1-weighted VIBE, isotropic 0.8 mm^3, 160 sagittal slices',
        'software': 'OsiriX MD (manual segmentation)',
        'volume_m3': 379.89e-6,
        'volume_L': 0.37989,
        'volume_mL': 379.89,
        'muscle_mass_kg': 0.3587,
        'muscle_density_kg_m3': 1059.7,
        'optimal_fiber_length_m': 0.0574,
        'tendon_slack_length_m': 0.2573,
        'pennation_angle_deg': 27.0,
        'lever_arm_m': -0.064,
        'pcsa_m2': 0.005898,
        'pcsa_cm2': 58.98,
        'f_max_isometric_N': 1474.4
    },
    'mrs_dynamic_energy_accumulation': {
        'sequence': 'MUSCLE (TR=5 s, 16 mm slice, OVS, GM localization)',
        'time_points_s': [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
        'energy_exp_J_per_kg': energy_exp,
        'linear_fit_rate_early_burst_J_per_kg_s': 5.8,
        'linear_fit_rate_ci95_J_per_kg_s': 1.8,
        'assumed_enthalpy_Delta_H_kJ_mol': 21.0,
        'thermodynamic_work_Delta_G_ATP_nominal_kJ_mol': 54.0,
        'water_conversion_L_per_kg': 0.68,
        'energy_definition_caveat': 'Energy in Franke et al. was computed via cross-bridge model heat/work decomposition; multiplying by 54/21 is not a trivial conversion to true total metabolic power without auditing model equations.'
    },
    'semg_activation_statistics': {
        **emg_stats,
        'hardware_sampling_rate_hz': 2000,
        'supplementary_grid_sampling_rate_hz': 4000,
        'grid_time_step_s': 0.00025,
        'sampling_note': 'Hardware sEMG acquisition was at 2000 Hz; the 240,001 points in supplementary MAT file reflect 4 kHz upsampling / interpolation.',
        'physiological_interpretation': 'sEMG RMS (12.7%) is a normalized surface electrical signal, not a direct measurement of recruited fiber fraction or active 3D muscle volume.'
    },
    'kinematics_ankle_angle_statistics': ang_stats
}

out_file = ROOT / 'research' / 'empirical_anchors_2026_11_08' / 'franke2020_extracted_measurements.json'
out_file.write_text(json.dumps(out_data, indent=2), encoding='utf-8')
print(f'Wrote extracted Franke 2020 measurements to {out_file}')
