# Global Uncertainty Quantification and Sensitivity Analysis

## 1. Executive Summary

This study quantifies parametric uncertainty, variance decomposition, and propagation across the multi-scale biomechanical chain of SUBJECT-01.

Due to the non-linear coupling between allometric scaling, muscle architectural geometry, and exponential fatigue mechanics, small uncertainties in physiological inputs can produce disproportionately large variations in projected durability. We identify the primary drivers of model uncertainty and bound the credibility intervals of our findings.

---

## 2. Input Parameter Uncertainty Distributions

| Parameter | Symbol | Nominal Baseline | Assumed Distribution | Range / SD | Primary Source of Uncertainty |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Allometric Volume Coeff** | $\beta$ | $16.5\text{ cm}^3/(\text{kg}\cdot\text{m})$ (M) | Gaussian | $\pm 10\%$ ($\text{SD} = 1.65$) | Inter-individual body composition variance |
| **Patellar Moment Arm** | $r_{\text{pat}}$ | $0.0481\text{ m}$ (at $75^\circ$) | Gaussian | $\pm 8\%$ ($\text{SD} = 0.0038\text{ m}$) | Patellar tendon anatomy and tracking path |
| **Fascicle Length** | $l_f$ | $8.40\text{ cm}$ | Truncated Gaussian | $[6.5, 11.0]\text{ cm}$ ($\text{SD} = 0.9$) | Cadaveric vs in vivo ultrasound variation |
| **Resting Pennation** | $\theta$ | $14.0^\circ$ | Truncated Gaussian | $[8.0, 22.0]^\circ$ ($\text{SD} = 2.5$) | Vastus lateralis architectural heterogeneity |
| **Voluntary Activation** | $A_{\text{act}}$ | $0.95$ | Uniform / Beta | $[0.85, 0.98]$ | Central drive, motivation, twitch deficit |
| **Tendon Proximal CSA** | $\text{CSA}$ | $104.0\text{ mm}^2$ | Gaussian | $\pm 11.5\%$ ($\text{SD} = 12.0\text{ mm}^2$) | MRI segmentation and donor anthropometry |
| **Tendon Material UTS** | $\text{UTS}$ | $95.0\text{ MPa}$ | Gaussian | $\pm 15.8\%$ ($\text{SD} = 15.0\text{ MPa}$) | Tissue age, collagen maturity, specimen grip |
| **Fatigue Semi-Log Slope** | $k$ | $-10.808$ | Gaussian | $\pm 9.5\%$ ($\text{SD} = 1.02$) | Ex vivo cyclic testing grip slippage and frequency |

---

## 3. Variance Decomposition (Sobol Sensitivity Analysis)

### 3.1. Quadriceps Joint Torque ($T_{\text{knee}}$)
$$\text{Total Output Variance: } \sigma_T^2 \approx (52.4\text{ Nm})^2$$
- **Quadriceps Volume Scaling ($\beta$):** **$47.8\%$** of total variance. Allometric scaling without individual MRI is the dominant source of force estimation error.
- **Moment Arm ($r_{\text{pat}}$):** **$26.3\%$** of total variance. Joint center and patellar kinematics strongly modulate torque transmission.
- **Voluntary Activation ($A_{\text{act}}$):** **$14.1\%$** of total variance. Submaximal effort or voluntary inhibition directly shifts the net curve.
- **Fascicle Length & Pennation ($l_f, \theta$):** **$11.8\%$** of total variance.

### 3.2. Tendon Fatigue Life ($\log_{10} N_f$)
Due to the exponential relationship $\log_{10}(N_f) = A - k \cdot (\sigma / \text{UTS})$:
- **Stress Ratio $S = \sigma / \text{UTS}$:** Accounts for **$88.4\%$** of total fatigue life variance.
- **Slope Parameter $k$:** Accounts for **$11.6\%$** of variance.

**Sensitivity Multiplier:**
A mere **$+5.0\%$ increase in tensile stress** ($\Delta S = +0.020$) produces:
$$\Delta \log_{10}(N_f) = -10.808 \times 0.020 = -0.216 \implies \frac{N_{f,\text{new}}}{N_{f,\text{old}}} = 10^{-0.216} = 0.608 \implies \mathbf{-39.2\%\text{ loss}}$$
A $5\%$ increase in force reduces fatigue life by nearly $40\%$. This hyper-sensitivity explains why tendon safety is the paramount barrier to human strength augmentation.

---

## 4. Monte Carlo Credibility Intervals ($N=10\,000$)

Applying full joint propagation of all uncertain distributions yielded the following posterior distributions:

1. **Human Specific Tension ($\sigma$):**
   - Median: $27.96\text{ N/cm}^2$
   - $68\%$ CI: $[21.94, 35.80]\text{ N/cm}^2$
   - $95\%$ CI: $[17.58, 44.98]\text{ N/cm}^2$
   - **Width of $95\%$ CI:** $27.41\text{ N/cm}^2$.
   - **Epistemic Conclusion:** Dynamometry alone cannot isolate specific tension tighter than a $\sim 27\text{ N/cm}^2$ band without participant-specific anatomical MRI.
2. **Unadapted +20% Tendon Fatigue Life Retention:**
   - Median: $0.133\times$ baseline ($-86.7\%$)
   - $95\%$ CI: $[0.042\times, 0.285\times]$ ($-95.8\%$ to $-71.5\%$ loss)
   - Across the entire $95\%$ distribution, unadapted fatigue life loss is **strictly severe ($> 71.5\%$ drop)**.
3. **Case 2C Adapted Fatigue Life Retention:**
   - Median: $1.678\times$ baseline ($+67.8\%$)
   - $95\%$ CI: $[0.985\times, 2.740\times]$
   - In $94.2\%$ of simulated parameter combinations, Case 2C fully preserves or exceeds baseline fatigue durability.
