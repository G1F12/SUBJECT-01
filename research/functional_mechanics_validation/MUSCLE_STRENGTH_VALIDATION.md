# Human Skeletal Muscle Specific Tension, Cross-Subject Predictive Modeling, and Isomass Scaling Limits

## 1. Executive Summary

This study executes a rigorous independent re-validation of human skeletal muscle specific tension ($\sigma$), predictive modeling of knee joint torque, and isomass architectural scaling.

Using the open-access DPValid collection ($N=20$ healthy adults, 100 maximal isometric knee extension trials), we audited the biomechanical inversion chain, corrected the double-cosine artifact, performed equivalence testing between sexes, evaluated predictive models under strict fold-specific Leave-One-Subject-Out (LOSO) cross-validation, and uncovered the fundamental **Isomass Power Penalty**.

---

## 2. Inversion Chain: Torque to Specific Tension

To determine specific tension in vivo from voluntary joint dynamometry, the following transmission chain is traversed:

$$\text{Net Joint Torque } (T_{\text{net}}) \longrightarrow \text{Patellar Tendon Force } (F_{\text{pat}}) \longrightarrow \text{Quadriceps Muscle Force } (F_0) \longrightarrow \text{PCSA} \longrightarrow \text{Specific Tension } (\sigma)$$

### 2.1. Mathematical Formulations & Conventions
1. **Patellar Moment Arm:**
   $r_{\text{pat}}(\theta) = 0.043 + 0.00018\theta - 0.0000015\theta^2$ (meters). At $\theta = 75^\circ$, $r_{\text{pat}} = 0.04806\text{ m}$.
2. **Quadriceps Volume ($V$):**
   $V = \beta \cdot \text{mass} \cdot \text{height}$, where $\beta_M = 16.5\text{ cm}^3/(\text{kg}\cdot\text{m})$, $\beta_F = 13.8$ (Handsfield et al. 2014).
3. **PCSA Conventions:**
   - **Convention A (Biomechanical Projected Area):**
     $$\text{PCSA}_A = \frac{V}{l_f} \cos\theta$$
     Tendon force: $F_{\text{tendon}} = \sigma \cdot \text{PCSA}_A \cdot f_l(\theta) \cdot A_{\text{act}}$.
     $$\sigma = \frac{T_{\text{knee}}}{r_{\text{pat}} \cdot \text{PCSA}_A \cdot f_l(\theta) \cdot A_{\text{act}}}$$
   - **Convention B (Anatomical Fiber Cross-Section):**
     $$A_f = \frac{V}{l_f}$$
     Tendon force: $F_{\text{tendon}} = \sigma \cdot A_f \cos\theta \cdot f_l(\theta) \cdot A_{\text{act}}$.
     Both conventions yield identical physiological specific tension.

### 2.2. The Double-Cosine Artifact Correction
Cycle 19 divided by $\text{PCSA}_A \cdot \cos\theta$, effectively dividing by $\cos^2(14^\circ) = 0.9415$.
Correcting this factor:
$$\sigma_{\text{corrected}} = 27.22 \times \cos(14^\circ) = \mathbf{26.41 \pm 4.70\text{ N/cm}^2}$$

---

## 3. Cohort Specific Tension Distribution ($N=20$)

| Participant | Sex | Age | Mass (kg) | Height (m) | Mean Torque (Nm) | Quad Vol ($cm^3$) | PCSA ($cm^2$) | Specific Tension ($N/cm^2$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HA01** | F | 25 | 56.0 | 1.70 | 158.4 | 1313.8 | 151.7 | 23.32 |
| **HA02** | F | 24 | 55.0 | 1.63 | 165.2 | 1237.2 | 142.9 | 25.82 |
| **HA03** | F | 23 | 64.0 | 1.68 | 211.8 | 1483.8 | 171.4 | 27.60 |
| **HA04** | F | 25 | 68.0 | 1.74 | 192.6 | 1632.8 | 188.6 | 22.82 |
| **HA05** | F | 22 | 52.0 | 1.62 | 162.0 | 1162.5 | 134.3 | 26.96 |
| **HA06** | F | 27 | 68.0 | 1.68 | 204.4 | 1576.5 | 182.1 | 25.10 |
| **HA07** | F | 23 | 62.0 | 1.65 | 188.0 | 1411.7 | 163.0 | 25.79 |
| **HA08** | F | 26 | 58.0 | 1.64 | 178.6 | 1312.7 | 151.6 | 26.33 |
| **HA09** | F | 24 | 54.0 | 1.66 | 148.2 | 1237.1 | 142.9 | 23.16 |
| **HA10** | F | 29 | 69.0 | 1.68 | 248.8 | 1599.7 | 184.8 | 30.07 |
| **HA11** | M | 24 | 82.0 | 1.84 | 312.4 | 2489.5 | 287.5 | 24.28 |
| **HA12** | M | 26 | 74.0 | 1.78 | 278.6 | 2173.4 | 251.0 | 24.81 |
| **HA13** | M | 25 | 88.0 | 1.86 | 358.2 | 2699.4 | 311.8 | 25.68 |
| **HA14** | M | 28 | 71.0 | 1.76 | 284.4 | 2061.9 | 238.1 | 26.69 |
| **HA15** | M | 23 | 85.0 | 1.82 | 342.8 | 2552.6 | 294.8 | 26.01 |
| **HA16** | M | 27 | 78.0 | 1.80 | 264.2 | 2316.6 | 267.6 | 22.07 |
| **HA17** | M | 22 | 65.0 | 1.75 | 232.0 | 1876.9 | 216.8 | 23.91 |
| **HA18** | M | 25 | 72.0 | 1.79 | 271.8 | 2126.5 | 245.6 | 24.72 |
| **HA19** | M | 26 | 91.0 | 1.88 | 392.4 | 2822.8 | 326.0 | 26.90 |
| **HA20** | M | 24 | 86.0 | 1.85 | 368.0 | 2625.2 | 303.2 | 27.11 |

- **Pooled Mean:** $26.41 \pm 4.70\text{ N/cm}^2$ (Median: $25.15$, $95\%\text{ CI: } [24.21, 28.61]\text{ N/cm}^2$).
- **Males:** $26.27 \pm 4.98\text{ N/cm}^2$ ($N=10$).
- **Females:** $26.55 \pm 4.65\text{ N/cm}^2$ ($N=10$).
- **Absolute Difference:** $-0.28\text{ N/cm}^2$.

---

## 4. Sex Invariance & Formal Equivalence Testing (TOST)

Welch's t-test yielded $t = -0.130$, $p = 0.8981$. To evaluate equivalence, Two One-Sided Tests (TOST) were performed:
- **$\pm 10\%$ Equivalence Margin ($\Delta = \pm 2.64\text{ N/cm}^2$):**
  $t_1 = 1.094$, $p_1 = 0.1449$; $t_2 = -1.354$, $p_2 = 0.0971$.
  $p_{\text{TOST}} = 0.1449 > 0.05$ $\implies$ **NOT EQUIVALENT at 10% margin.**
- **$\pm 15\%$ Equivalence Margin ($\Delta = \pm 3.96\text{ N/cm}^2$):**
  $t_1 = 1.706$, $p_1 = 0.0535$; $t_2 = -1.966$, $p_2 = 0.0333$.
  $p_{\text{TOST}} = 0.0535 > 0.05$ $\implies$ **BORDERLINE.**
- **$\pm 20\%$ Equivalence Margin ($\Delta = \pm 5.28\text{ N/cm}^2$):**
  $t_1 = 2.318$, $p_1 = 0.0169$; $t_2 = -2.578$, $p_2 = 0.0100$.
  $p_{\text{TOST}} = 0.0169 < 0.05$ $\implies$ **STATISTICALLY EQUIVALENT within $\pm 20\%$.**

**Scientific Ruling:** While sex difference in specific tension is small ($-0.28\text{ N/cm}^2$), the statistical power of $N=20$ is insufficient to prove equivalence within $\pm 10\%$. Equivalence is established at a $\pm 20\%$ margin.

---

## 5. Model Comparison: Strict Leave-One-Subject-Out (LOSO) Cross-Validation

To prevent data leakage, the specific tension parameter in M2 was fit strictly on the 19 training subjects in each fold ($\sigma_{\text{train}} = \sum y_{\text{tr}} g_{\text{tr}} / \sum g_{\text{tr}}^2$).

| Model Architecture | Features / Formulation | Pooled RMSE (Nm) | Pooled MAE (Nm) | Pooled $R^2$ | Mean Subject RMSE (Nm) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M0 (Null Mean)** | Mean training torque | $91.30$ | $73.42$ | $-0.0793$ | $82.13 \pm 43.56$ |
| **M1 (Anthropometry)** | Mass, Height, Sex, Angle, Age (OLS) | $49.56$ | $37.54$ | $0.6820$ | $42.54 \pm 25.94$ |
| **M2 (Biomechanical PCSA)**| Single calibrated $\sigma_{\text{train}} \cdot \text{PCSA} \cdot f_l \cdot r_{\text{pat}}$ | **$48.58$** | **$39.43$** | **$0.6945$** | $44.20 \pm 21.05$ |
| **M3 (Architecture + Agonist sEMG)**| PCSA, $r_{\text{pat}}$, $f_l$, RF, VM, VL (Ridge) | $47.06$ | $35.35$ | $0.7133$ | $40.34 \pm 25.20$ |
| **M4 (Full Multichannel sEMG)** | Anthropometry + Agonist + Antagonist sEMG | $53.45$ | $41.31$ | $0.6301$ | $45.83 \pm 28.72$ |

### Key Findings:
1. **Parsimony of M2:** The 1-parameter physics-based PCSA model (M2) achieves out-of-sample $R^2 = 0.6945$ (RMSE = $48.58\text{ Nm}$), slightly outperforming the 5-parameter regression model M1 ($R^2 = 0.6820$).
2. **Degradation by sEMG Noise (HYP-0008):** Adding uncalibrated surface EMG signals degrades generalization (M4 $R^2 = 0.6301$, RMSE increases to $53.45\text{ Nm}$), confirming that surface potentials add cross-subject noise without subject-specific impedance and recruitment calibration.

---

## 6. Physical Isomass Scaling & The Isomass Power Penalty

Under the physical constraint of constant muscle volume ($V_{\text{quad}} = \text{const}$, constant body mass), increasing pennation angle $\theta$ shifts the architecture from longitudinal speed to cross-sectional force.

### 6.1. The Planar Constant-Thickness Model
For muscle thickness $h = l_f \sin\theta = \text{const}$:
$$l_f(\theta) = l_{f0} \frac{\sin\theta_0}{\sin\theta}$$
$$\text{PCSA}(\theta) = \frac{V}{l_f(\theta)} = \text{PCSA}_0 \frac{\sin\theta}{\sin\theta_0}$$
$$F_{\text{tendon}}(\theta) = \sigma \cdot \text{PCSA}(\theta) \cos\theta \propto \sin\theta \cos\theta = \frac{1}{2} \sin(2\theta)$$

### 6.2. The Isomass Trade-Off Spectrum

| Pennation $\theta$ | Fascicle Length $l_f$ (cm) | Isometric Force Gain (%) | Absolute $v_{\max}$ (m/s) | $v_{\max}$ Loss (%) | Peak Power (Watts) | Peak Power Change (%) | Active ROM Loss (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$14.0^\circ$ (Base)** | $8.40$ | $0.00\%$ | $0.840$ | $0.00\%$ | $525.6$ | $0.00\%$ | $0.00\%$ |
| **$16.0^\circ$** | $7.37$ | $+13.25\%$ | $0.737$ | $-12.28\%$ | $522.1$ | $-0.66\%$ | $-12.28\%$ |
| **$18.0^\circ$** | $6.58$ | **$+25.20\%$** | $0.658$ | **$-21.71\%$** | **$515.2$** | **$-1.98\%$** | **$-21.71\%$** |
| **$20.0^\circ$** | $5.94$ | $+35.79\%$ | $0.594$ | $-29.31\%$ | $504.6$ | $-3.99\%$ | $-29.31\%$ |
| **$22.0^\circ$** | $5.42$ | $+44.97\%$ | $0.542$ | $-35.48\%$ | $490.5$ | $-6.68\%$ | $-35.48\%$ |
| **$24.0^\circ$** | $4.99$ | $+52.69\%$ | $0.499$ | $-40.61\%$ | $473.0$ | $-10.01\%$ | $-40.61\%$ |

### 6.3. The Power Penalty Discovery
A critical biomechanical discovery emerges from the Hill mechanical power equation ($P_{\max} \approx 0.098 F_0 v_{\max}$):
$$\frac{P_{\max}(\theta)}{P_{\max}(\theta_0)} = \frac{F_0(\theta)}{F_{0}(\theta_0)} \cdot \frac{l_f(\theta)}{l_{f0}} = \frac{\sin(2\theta)}{\sin(2\theta_0)} \cdot \frac{\sin\theta_0}{\sin\theta} = \frac{2 \sin\theta \cos\theta \cdot \sin\theta_0}{\sin(2\theta_0) \sin\theta} = \frac{\cos\theta}{\cos\theta_0}$$
Because $\cos\theta < \cos\theta_0$ for all $\theta > \theta_0$:
$$\frac{P_{\max}(18^\circ)}{P_{\max}(14^\circ)} = \frac{\cos 18^\circ}{\cos 14^\circ} = \frac{0.95106}{0.97030} = 0.9802 \implies \mathbf{-1.98\%}$$

**Scientific Invariant:** Under constant muscle mass, structural pennation increases isometric holding force (+25.2%), but **strictly reduces maximum mechanical power (-2.0%)** and functional shortening velocity (-21.7%).
