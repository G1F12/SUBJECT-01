"""
Functional Biomechanical Multi-Muscle Bridge and Augmentation Feasibility Engine
Experiment: EXP-0046 (Cycle 13)
Governing Canonical Data: Bird et al. (2026) DATA_Dynamic_Knee.mat (N=6 dynamic, 3226 rows)
Cryptographic Standard: SHA-256 verification against official Dryad REST API digest
"""

import os
import json
import hashlib
import numpy as np
import scipy.io as sio
from typing import Dict, Any, Tuple, List


class FunctionalForceBridge:
    def __init__(self, config_path: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if config_path is None:
            config_path = os.path.join(base_dir, "config.json")
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
        self.raw_data_path = os.path.join(self.project_root, self.config["dataset"]["file_path"])
        self.expected_sha256 = self.config["dataset"]["expected_sha256"]
        
    def verify_cryptographic_digest(self) -> bool:
        """Verify the SHA-256 digest of the primary data file."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Primary data file not found at: {self.raw_data_path}")
            
        hasher = hashlib.sha256()
        with open(self.raw_data_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
                
        actual_digest = hasher.hexdigest()
        if actual_digest != self.expected_sha256:
            raise ValueError(
                f"Cryptographic digest mismatch for {self.raw_data_path}!\n"
                f"Expected: {self.expected_sha256}\n"
                f"Actual:   {actual_digest}"
            )
        return True

    def load_data(self) -> Dict[str, np.ndarray]:
        """Load and extract dynamic arrays from DATA_Dynamic_Knee.mat."""
        self.verify_cryptographic_digest()
        mat = sio.loadmat(self.raw_data_path)
        
        # Keys in DATA_Dynamic_Knee.mat:
        # total_part: Participant ID (1 to 6)
        # total_run: Series / Run ID
        # total_angle: Knee angle (deg)
        # total_vel: Angular velocity (deg/s)
        # total_torque: Torque (fraction of MVC, [0.0, 1.0])
        # total_emg: sEMG Vastus Lateralis
        # total_len: Fascicle Length (mm)
        # total_pen: Pennation Angle (deg)
        # total_uwb: UWB radar frequency channels (204, 3226)
        
        subject_id = mat['total_part'].flatten().astype(int) - 1 # 0-indexed: 0..5
        series_id = mat['total_run'].flatten().astype(int)
        angle = mat['total_angle'].flatten()
        velocity = mat['total_vel'].flatten()
        torque = mat['total_torque'].flatten()
        semg = mat['total_emg'].flatten()
        fascicle_length = mat['total_len'].flatten()
        pennation_angle = mat['total_pen'].flatten()
        
        # Anatomical knee extensor moment arm as function of knee angle
        # d_ma(theta) = 0.04 * (1.0 + 0.2 * sin(theta_rad)) in meters
        moment_arm = 0.04 * (1.0 + 0.2 * np.sin(np.radians(angle)))
        
        # Protocol classification by series metadata
        passive_series = {1, 2, 3, 4, 17, 18, 19, 20, 33, 34, 35, 36, 49, 50, 51, 52, 65, 66, 67, 68, 81, 82, 83, 84}
        is_passive = np.isin(series_id, list(passive_series))
        
        return {
            "subject_id": subject_id,
            "series_id": series_id,
            "angle": angle,
            "velocity": velocity,
            "torque": torque,
            "semg": semg,
            "fascicle_length": fascicle_length,
            "pennation_angle": pennation_angle,
            "moment_arm": moment_arm,
            "is_passive": is_passive,
            "is_active": ~is_passive
        }

    def compute_contractile_state(self, semg: np.ndarray, fascicle_length: np.ndarray, 
                                  velocity: np.ndarray, pennation_angle: np.ndarray) -> np.ndarray:
        """
        Compute in vivo Vastus Lateralis contractile state:
        q(t) = a(t) * f_L(L) * f_V(v) * cos(alpha)
        matching canonical Bird 2026 Dryad feature definitions.
        """
        # Activation proxy from sEMG
        a = semg
        
        # Force-length relationship from delta fascicle length
        L_norm = 1.0 + fascicle_length / 100.0
        f_L = np.maximum(0.1, 1.0 - ((L_norm - 1.0) / 0.5) ** 2)
        
        # Force-velocity relationship
        v_norm = velocity / 500.0
        f_V = np.where(v_norm >= 0, 1.0 / (1.0 + 2.0 * v_norm), 1.0 - 0.5 * np.maximum(-1.0, v_norm))
        
        # Pennation angle cosine factor (axial force transmission)
        cos_alpha = np.cos(np.radians(pennation_angle))
        
        return a * f_L * f_V * cos_alpha

    def compute_multi_muscle_torque(self, emg: np.ndarray, f_l: np.ndarray, f_v: np.ndarray,
                                   pennation_angle: np.ndarray, moment_arm: np.ndarray, 
                                   antagonist_gamma_base: float = 0.08,
                                   antagonist_gamma_slope: float = 0.14) -> np.ndarray:
        """
        Bridge from Vastus Lateralis to whole quadriceps tendon force and net knee torque:
        1. VL represents 32% of total quadriceps PCSA. Total quadriceps force:
           F_quad = F_VL / 0.32
        2. Agonist tendon torque: T_agonist = F_quad * moment_arm
        3. Dynamic antagonist hamstring co-activation:
           In vivo co-activation scales non-linearly with effort to stabilize the joint:
           gamma(t) = gamma_base + gamma_slope * a(t)
           T_net(t) = T_agonist(t) * (1 - gamma(t))
        """
        w_vl = self.config["physiological_constants"]["quadriceps_pcsa_fractions"]["vastus_lateralis"]
        cos_alpha = np.cos(np.radians(pennation_angle))
        
        # Agonist contractile force proxy
        f_agonist_vl = emg * f_l * f_v * cos_alpha
        f_quad_proxy = f_agonist_vl / w_vl
        
        # Agonist torque proxy (normalized moment arm relative to 40 mm reference)
        d_ma_norm = moment_arm / 0.04
        t_agonist = f_quad_proxy * d_ma_norm
        
        # Dynamic antagonist hamstring co-activation:
        gamma_dyn = np.clip(antagonist_gamma_base + antagonist_gamma_slope * np.clip(emg, 0.0, 1.0), 0.05, 0.35)
        
        # Net joint torque after antagonist co-activation
        t_net = t_agonist * (1.0 - gamma_dyn)
        return t_net

    def evaluate_loso_cross_validation(self, condition: str = "all") -> Dict[str, Any]:
        """
        Perform strict Leave-One-Subject-Out (LOSO) cross-validation across the 6 subjects.
        Evaluates:
        - M0: Mean baseline
        - M1: Single sEMG linear model (Bird M1)
        - M3: Single Hill model (Bird M3)
        - M_Bridge: Multi-muscle bridge with antagonist co-activation (Cycle 13 EXP-0046)
        """
        data = self.load_data()
        
        if condition == "active_only":
            mask = data["is_active"]
        else:
            mask = np.ones_like(data["torque"], dtype=bool)
            
        sub_ids = data["subject_id"][mask]
        torque = data["torque"][mask]
        semg = data["semg"][mask]
        flen = data["fascicle_length"][mask]
        vel = data["velocity"][mask]
        penn = data["pennation_angle"][mask]
        m_arm = data["moment_arm"][mask]
        
        # Feature calculations
        L_norm = 1.0 + flen / 100.0
        f_l = np.maximum(0.1, 1.0 - ((L_norm - 1.0) / 0.5) ** 2)
        v_norm = vel / 500.0
        f_v = np.where(v_norm >= 0, 1.0 / (1.0 + 2.0 * v_norm), 1.0 - 0.5 * np.maximum(-1.0, v_norm))
        cos_alpha = np.cos(np.radians(penn))
        d_ma_norm = m_arm / 0.04
        
        # Feature 1: sEMG (M1 baseline)
        feat_m1 = semg
        
        # Feature 2: Hill single muscle (M3: a * f_L * f_V)
        feat_m3 = semg * f_l * f_v
        
        # Feature 3: Standard composite Hill feature (M4: a * f_L * f_V * cos(alpha) * d_MA)
        feat_m4 = semg * f_l * f_v * cos_alpha * d_ma_norm
        
        # Feature 4: Multi-muscle bridge with dynamic antagonist co-activation (EXP-0046)
        feat_bridge = self.compute_multi_muscle_torque(semg, f_l, f_v, penn, m_arm)
        
        unique_subjects = np.unique(sub_ids)
        n_subjects = len(unique_subjects)
        
        models = ["M0_Mean", "M1_sEMG", "M3_Hill", "M4_Hill_Composite", "M_Bridge_CoActivation"]
        fold_results = {m: {"r2": [], "rmse": [], "nrmse": [], "pearson_r": []} for m in models}
        y_true_all = []
        y_pred_all = {m: [] for m in models}
        
        for held_out in unique_subjects:
            train_mask = (sub_ids != held_out)
            test_mask = (sub_ids == held_out)
            
            y_train, y_test = torque[train_mask], torque[test_mask]
            y_true_all.extend(y_test)
            
            # Target variance on held-out subject
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            y_range = np.max(y_test) - np.min(y_test) if np.max(y_test) > np.min(y_test) else 1.0
            
            # --- Model M0: Mean predictor ---
            pred_m0 = np.full_like(y_test, np.mean(y_train))
            y_pred_all["M0_Mean"].extend(pred_m0)
            ss_res_m0 = np.sum((y_test - pred_m0) ** 2)
            r2_m0 = 1.0 - (ss_res_m0 / ss_tot) if ss_tot > 0 else 0.0
            rmse_m0 = np.sqrt(np.mean((y_test - pred_m0) ** 2))
            fold_results["M0_Mean"]["r2"].append(float(r2_m0))
            fold_results["M0_Mean"]["rmse"].append(float(rmse_m0))
            fold_results["M0_Mean"]["nrmse"].append(float(rmse_m0 / y_range * 100))
            fold_results["M0_Mean"]["pearson_r"].append(0.0)
            
            # Helper for 1D linear regression fit strictly on train fold
            def fit_predict_linear(x_tr, y_tr, x_te):
                x_mean, y_mean = np.mean(x_tr), np.mean(y_tr)
                denom = np.sum((x_tr - x_mean) ** 2)
                if denom > 1e-12:
                    slope = np.sum((x_tr - x_mean) * (y_tr - y_mean)) / denom
                    intercept = y_mean - slope * x_mean
                else:
                    slope = 0.0
                    intercept = y_mean
                return slope * x_te + intercept

            # --- Model M1: sEMG baseline ---
            pred_m1 = fit_predict_linear(feat_m1[train_mask], y_train, feat_m1[test_mask])
            pred_m1 = np.clip(pred_m1, 0.0, None)
            y_pred_all["M1_sEMG"].extend(pred_m1)
            ss_res_m1 = np.sum((y_test - pred_m1) ** 2)
            r2_m1 = 1.0 - (ss_res_m1 / ss_tot) if ss_tot > 0 else 0.0
            rmse_m1 = np.sqrt(np.mean((y_test - pred_m1) ** 2))
            r_m1 = np.corrcoef(pred_m1, y_test)[0, 1] if np.std(pred_m1) > 0 and np.std(y_test) > 0 else 0.0
            fold_results["M1_sEMG"]["r2"].append(float(r2_m1))
            fold_results["M1_sEMG"]["rmse"].append(float(rmse_m1))
            fold_results["M1_sEMG"]["nrmse"].append(float(rmse_m1 / y_range * 100))
            fold_results["M1_sEMG"]["pearson_r"].append(float(r_m1))
            
            # --- Model M3: Hill single muscle ---
            pred_m3 = fit_predict_linear(feat_m3[train_mask], y_train, feat_m3[test_mask])
            pred_m3 = np.clip(pred_m3, 0.0, None)
            y_pred_all["M3_Hill"].extend(pred_m3)
            ss_res_m3 = np.sum((y_test - pred_m3) ** 2)
            r2_m3 = 1.0 - (ss_res_m3 / ss_tot) if ss_tot > 0 else 0.0
            rmse_m3 = np.sqrt(np.mean((y_test - pred_m3) ** 2))
            r_m3 = np.corrcoef(pred_m3, y_test)[0, 1] if np.std(pred_m3) > 0 and np.std(y_test) > 0 else 0.0
            fold_results["M3_Hill"]["r2"].append(float(r2_m3))
            fold_results["M3_Hill"]["rmse"].append(float(rmse_m3))
            fold_results["M3_Hill"]["nrmse"].append(float(rmse_m3 / y_range * 100))
            fold_results["M3_Hill"]["pearson_r"].append(float(r_m3))
            
            # --- Model M4: Standard composite Hill feature ---
            pred_m4 = fit_predict_linear(feat_m4[train_mask], y_train, feat_m4[test_mask])
            pred_m4 = np.clip(pred_m4, 0.0, None)
            y_pred_all["M4_Hill_Composite"].extend(pred_m4)
            ss_res_m4 = np.sum((y_test - pred_m4) ** 2)
            r2_m4 = 1.0 - (ss_res_m4 / ss_tot) if ss_tot > 0 else 0.0
            rmse_m4 = np.sqrt(np.mean((y_test - pred_m4) ** 2))
            r_m4 = np.corrcoef(pred_m4, y_test)[0, 1] if np.std(pred_m4) > 0 and np.std(y_test) > 0 else 0.0
            fold_results["M4_Hill_Composite"]["r2"].append(float(r2_m4))
            fold_results["M4_Hill_Composite"]["rmse"].append(float(rmse_m4))
            fold_results["M4_Hill_Composite"]["nrmse"].append(float(rmse_m4 / y_range * 100))
            fold_results["M4_Hill_Composite"]["pearson_r"].append(float(r_m4))
            
            # --- Model M_Bridge_CoActivation: Multi-muscle bridge with dynamic co-activation ---
            pred_bridge = fit_predict_linear(feat_bridge[train_mask], y_train, feat_bridge[test_mask])
            pred_bridge = np.clip(pred_bridge, 0.0, None)
            y_pred_all["M_Bridge_CoActivation"].extend(pred_bridge)
            ss_res_br = np.sum((y_test - pred_bridge) ** 2)
            r2_br = 1.0 - (ss_res_br / ss_tot) if ss_tot > 0 else 0.0
            rmse_br = np.sqrt(np.mean((y_test - pred_bridge) ** 2))
            r_br = np.corrcoef(pred_bridge, y_test)[0, 1] if np.std(pred_bridge) > 0 and np.std(y_test) > 0 else 0.0
            fold_results["M_Bridge_CoActivation"]["r2"].append(float(r2_br))
            fold_results["M_Bridge_CoActivation"]["rmse"].append(float(rmse_br))
            fold_results["M_Bridge_CoActivation"]["nrmse"].append(float(rmse_br / y_range * 100))
            fold_results["M_Bridge_CoActivation"]["pearson_r"].append(float(r_br))

        # Overall pooled metrics across subjects
        y_true_all = np.array(y_true_all)
        ss_tot_pooled = np.sum((y_true_all - np.mean(y_true_all)) ** 2)
        y_range_pooled = np.max(y_true_all) - np.min(y_true_all)
        
        summary = {}
        for m in models:
            preds = np.array(y_pred_all[m])
            ss_res = np.sum((y_true_all - preds) ** 2)
            pooled_r2 = 1.0 - (ss_res / ss_tot_pooled)
            pooled_rmse = np.sqrt(np.mean((y_true_all - preds) ** 2))
            pooled_nrmse = pooled_rmse / y_range_pooled * 100
            pooled_r = np.corrcoef(preds, y_true_all)[0, 1] if np.std(preds) > 0 else 0.0
            
            mean_fold_r2 = np.mean(fold_results[m]["r2"])
            std_fold_r2 = np.std(fold_results[m]["r2"])
            mean_fold_rmse = np.mean(fold_results[m]["rmse"])
            mean_fold_nrmse = np.mean(fold_results[m]["nrmse"])
            mean_fold_r = np.mean(fold_results[m]["pearson_r"])
            
            summary[m] = {
                "pooled_r2": float(pooled_r2),
                "pooled_rmse": float(pooled_rmse),
                "pooled_nrmse_percent": float(pooled_nrmse),
                "pooled_pearson_r": float(pooled_r),
                "mean_fold_r2": float(mean_fold_r2),
                "std_fold_r2": float(std_fold_r2),
                "mean_fold_rmse": float(mean_fold_rmse),
                "mean_fold_nrmse_percent": float(mean_fold_nrmse),
                "mean_fold_pearson_r": float(mean_fold_r),
                "fold_r2_values": fold_results[m]["r2"]
            }
            
        return {
            "condition": condition,
            "total_observations_evaluated": int(len(y_true_all)),
            "held_out_subjects_count": n_subjects,
            "models_summary": summary
        }

    def simulate_augmentation_and_tendon_stress(self) -> Dict[str, Any]:
        """
        Simulate functional torque enhancement (+20% target) and compute 
        patellar tendon mechanical stress under physiological antagonist co-activation.
        """
        pcsa_tot = self.config["physiological_constants"]["nominal_quadriceps_pcsa_cm2"]
        sigma_spec = self.config["physiological_constants"]["specific_tension_N_per_cm2"]
        tendon_nominal_csa = self.config["physiological_constants"]["patellar_tendon"]["nominal_csa_mm2"]
        uts = self.config["physiological_constants"]["patellar_tendon"]["ultimate_tensile_strength_MPa"]
        
        # Nominal maximal isometric quadriceps fiber force (N):
        # F_max = PCSA (cm^2) * specific tension (N/cm^2) = 140 * 27.5 = 3850 N
        nominal_fiber_fmax = pcsa_tot * sigma_spec
        nominal_moment_arm = 0.045 # meters (typical patellar tendon moment arm at 60 deg)
        nominal_pennation = self.config["physiological_constants"]["pennation_angle"]["nominal_rest_deg"]
        nominal_gamma = self.config["physiological_constants"]["antagonist_coactivation"]["nominal_fraction_gamma"]
        
        scenarios = self.config["augmentation_scenarios"]
        sim_results = {}
        
        for sc_name, sc_params in scenarios.items():
            f_mult = sc_params["force_multiplier"]
            penn_delta = sc_params.get("pennation_delta_deg", 0.0)
            t_csa_mult = sc_params.get("tendon_csa_multiplier", 1.0)
            antag_supp = sc_params.get("antagonist_suppression_factor", 1.0)
            
            # Augmented fiber force
            f_fiber = nominal_fiber_fmax * f_mult
            
            # Effective pennation angle (hypertrophy increases fiber angle relative to aponeurosis)
            eff_penn = nominal_pennation + penn_delta
            cos_penn = np.cos(np.radians(eff_penn))
            
            # Axial force transmitted to the patellar tendon (N)
            f_tendon = f_fiber * cos_penn
            
            # Patellar tendon cross-sectional area (mm^2)
            tendon_csa = tendon_nominal_csa * t_csa_mult
            
            # Mechanical tensile stress (MPa = N / mm^2)
            stress_mpa = f_tendon / tendon_csa
            
            # Safety factor against ultimate tensile strength (UTS)
            safety_factor = uts / stress_mpa
            
            # Agonist torque produced at the joint (N*m)
            t_agonist = f_tendon * nominal_moment_arm
            
            # Antagonist hamstring co-activation counter-torque (N*m)
            eff_gamma = nominal_gamma * antag_supp
            t_antag = t_agonist * eff_gamma
            
            # Net functional joint torque (N*m)
            t_net = t_agonist - t_antag
            
            sim_results[sc_name] = {
                "fiber_force_N": float(f_fiber),
                "pennation_angle_deg": float(eff_penn),
                "cos_pennation": float(cos_penn),
                "patellar_tendon_force_N": float(f_tendon),
                "patellar_tendon_csa_mm2": float(tendon_csa),
                "tendon_stress_MPa": float(stress_mpa),
                "safety_factor": float(safety_factor),
                "safety_threshold_met": bool(safety_factor >= 1.5),
                "agonist_torque_Nm": float(t_agonist),
                "antagonist_torque_Nm": float(t_antag),
                "net_joint_torque_Nm": float(t_net),
                "description": sc_params.get("description", "")
            }
            
        # Calculate net gains relative to nominal
        nominal_tnet = sim_results["nominal"]["net_joint_torque_Nm"]
        for sc_name in sim_results:
            tnet = sim_results[sc_name]["net_joint_torque_Nm"]
            net_gain_pct = (tnet - nominal_tnet) / nominal_tnet * 100.0
            
            # Useful transmission efficiency: net torque gain % / fiber force gain %
            fiber_gain_pct = (sim_results[sc_name]["fiber_force_N"] - nominal_fiber_fmax) / nominal_fiber_fmax * 100.0
            if fiber_gain_pct > 0:
                transmission_efficiency = net_gain_pct / fiber_gain_pct
            else:
                transmission_efficiency = 1.0
                
            sim_results[sc_name]["net_torque_gain_percent"] = float(net_gain_pct)
            sim_results[sc_name]["torque_transmission_efficiency"] = float(transmission_efficiency)

        return sim_results

    def run_full_experiment(self) -> Dict[str, Any]:
        """Execute complete pipeline: cryptographic audit, LOSO cross-validation, and augmentation stress test."""
        print("=== EXP-0046: FUNCTIONAL MULTI-MUSCLE BIOMECHANICAL BRIDGE & AUGMENTATION FEASIBILITY ===")
        print("Step 1: Cryptographic check of raw arrays...")
        self.verify_cryptographic_digest()
        print(f"PASS: Primary array verified with SHA-256: {self.expected_sha256[:16]}...")
        
        print("\nStep 2: Executing strict LOSO cross-validation across all dynamic observations (N=3226)...")
        loso_all = self.evaluate_loso_cross_validation(condition="all")
        
        print("\nStep 3: Executing strict LOSO cross-validation across active protocols only (N=1844)...")
        loso_active = self.evaluate_loso_cross_validation(condition="active_only")
        
        print("\nStep 4: Simulating TARGET-FORCE20 augmentation scenarios and patellar tendon stress...")
        aug_results = self.simulate_augmentation_and_tendon_stress()
        
        full_results = {
            "experiment_id": "EXP-0046",
            "experiment_title": "Functional Biomechanical Multi-Muscle Bridge and Augmentation Feasibility Under Dynamic Antagonist Co-Activation",
            "cycle": 13,
            "dataset_provenance": "Bird et al. (2026) Science Robotics / Dryad, CC0-1.0",
            "loso_cross_validation_all_conditions": loso_all,
            "loso_cross_validation_active_only": loso_active,
            "augmentation_feasibility_simulation": aug_results
        }
        
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        results_path = os.path.join(results_dir, "experiment_results.json")
        
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False)
            
        print(f"\nAll results successfully generated and saved to: {results_path}")
        return full_results


if __name__ == "__main__":
    engine = FunctionalForceBridge()
    engine.run_full_experiment()
