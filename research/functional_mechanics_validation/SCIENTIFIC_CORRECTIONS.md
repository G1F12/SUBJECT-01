# Scientific Corrections and Mathematical Rectifications: Research Cycle 19

## 1. Executive Summary

A forensic audit of Research Cycle 19 was executed on the primary codebases (`run_exp0059_muscle_models.py`, `run_exp0060_tendon_fatigue.py`), results registries, and technical reports. The audit identified seven significant methodological, mathematical, and epistemic discrepancies.

This document formally records each error, reconstructs its numerical origin, provides the mathematically rigorous correction, and specifies the revised scientific status.

---

## 2. Comprehensive Inventory of Rectified Errors

### Correction 1: Conflation of Power-Law and Semi-Log Tendon Fatigue Models (EXP-0060)
- **Identified Discrepancy:**
  Cycle 19 text reported:
  - Wöhler power-law exponent: $B = 8.45$.
  - Load increase: $+20\%$ ($F_1 / F_0 = 1.20$).
  - Fatigue life reduction: $-86.7\%$ (retention ratio $0.133\times$).
- **Mathematical Inconsistency:**
  Under a pure power-law formulation ($N_f = C \cdot \sigma^{-B}$):
  $$\frac{N_1}{N_0} = \left(\frac{\sigma_1}{\sigma_0}\right)^{-B} = (1.20)^{-8.45} \approx 0.2144 \implies -78.56\%$$
  A reduction of $-78.6\%$ cannot equal $-86.7\%$.
- **Numerical Origin:**
  The $-86.7\%$ reduction was computed in code using the **Semi-Log (Basquin / Exponential) model**:
  $$\log_{10}(N_f) = 9.875 - 10.808 \cdot \left(\frac{\sigma}{\text{UTS}}\right)$$
  When stress increases from $\sigma_0 = 38.46\text{ MPa}$ ($S_0 = 0.4048$) to $\sigma_1 = 46.15\text{ MPa}$ ($S_1 = 0.4858$), $\Delta S = +0.0810$.
  $$\log_{10}\left(\frac{N_1}{N_0}\right) = -10.808 \times 0.0810 = -0.8754 \implies \frac{N_1}{N_0} = 10^{-0.8754} = 0.1332 \implies \mathbf{-86.68\%}$$
  The author cited $B = 8.45$ from comparative literature but pasted the output of the semi-log model, conflating two incompatible model forms.
- **Rectification:**
  Both models are now explicitly separated and reported:
  1. Semi-log Basquin model ($k = 10.808$): $N_1 / N_0 = 0.1333$ ($-86.67\%$ loss).
  2. Literature Power-law model ($B = 8.45$): $N_1 / N_0 = 0.2142$ ($-78.58\%$ loss).
  3. Benchmark-fitted Power-law model ($B = 13.27$): $N_1 / N_0 = 0.0889$ ($-91.11\%$ loss).

---

### Correction 2: Stress Calculation Error in Adaptive Hypertrophy Case 2C (EXP-0060)
- **Identified Discrepancy:**
  Cycle 19 reports claimed that under $+20\%$ force with $+15\%$ tendon CSA hypertrophy and $+10\%$ UTS maturation (Case 2C), the peak proximal stress was reduced to **$34.78\text{ MPa}$**.
- **Mathematical Inconsistency:**
  $$\sigma = \frac{F}{\text{CSA}} = \frac{4800\text{ N}}{104\text{ mm}^2 \times 1.15} = \frac{4800\text{ N}}{119.6\text{ mm}^2} = \mathbf{40.13\text{ MPa}}$$
  The stress is $40.13\text{ MPa}$, NOT $34.78\text{ MPa}$.
- **Numerical Origin:**
  Forensic reconstruction revealed that $34.78\text{ MPa}$ was obtained by taking the **unaugmented baseline force** ($4000\text{ N}$) and dividing it by an adapted area ($115\text{ mm}^2$):
  $$\frac{4000\text{ N}}{115\text{ mm}^2} = 34.7826\text{ MPa}$$
  The author inadvertently applied the adapted cross-sectional area to the unaugmented baseline force instead of the $+20\%$ augmented force ($4800\text{ N}$).
- **Rectification:**
  The exact tensile stress in Case 2C is $40.13\text{ MPa}$.
  The stress ratio relative to adapted UTS ($104.5\text{ MPa}$) is:
  $$S_{\text{adapted}} = \frac{40.13\text{ MPa}}{104.5\text{ MPa}} = 0.3841$$
  Because $S_{\text{adapted}} < S_{\text{baseline}} (0.4048)$, baseline fatigue life is fully preserved and increased by $1.678\times$ (semi-log) or $1.564\times$ (power-law $B=8.45$).

---

### Correction 3: Misattribution of Bogaerts et al. (2017) as S-N Fatigue Source
- **Identified Discrepancy:**
  Registry entry `EXP-0060` listed `research/cycle16/data/bogaerts/bogaerts_2017_data.csv` as the sole inputs for the fatigue model.
- **Empirical Reality:**
  Bogaerts et al. (2017) measured in vivo ultrasound speckle displacements and strains during submaximal isometric contractions ($N=10$). **They did not conduct cyclic mechanical testing to failure.**
- **Rectification:**
  Primary S-N fatigue to failure data is attributed to:
  - Schechtman & Bader (1997, 2002) ($N=42$ human tendon specimens).
  - Wren et al. (2001, 2003) ($N=38$ human Achilles specimens).
  Bogaerts et al. (2017) is retained strictly as the source of in vivo inter-layer shear gradient kinematics ($+23.1\%$ deep displacement).

---

### Correction 4: Unqualified Null Effect of Tendon Young's Modulus (NEG-0057)
- **Identified Discrepancy:**
  NEG-0057 stated that a $+15\%$ increase in elastic modulus $E$ provides $0\%$ fatigue life improvement.
- **Physical Boundary Limitation:**
  In uniaxial force-controlled loading, nominal stress $\sigma = F / A$ is independent of $E$. However:
  1. Under displacement-controlled or strain-controlled cyclic deformation, $\sigma = E \cdot \epsilon$. Stiffening increases stress by $+15\%$, reducing fatigue life by $-71\%$.
  2. Elastic strain energy density per cycle is $U = \frac{1}{2} \sigma^2 / E$. Stiffening decreases energy storage by $-13.0\%$, diminishing elastic catapult power amplification in locomotion.
  3. At the osteotendinous enthesis, uncoordinated stiffening increases shear stress concentration at the unmineralized fibrocartilage boundary.
- **Rectification:**
  NEG-0057 is explicitly scoped to **uniaxial force-controlled loading**. The biological effect of elastic modulus is documented as multi-axial, displacement-dependent, and non-neutral.

---

### Correction 5: Double-Cosine Scaling Factor in Specific Tension (EXP-0059)
- **Identified Discrepancy:**
  Cycle 19 reported empirical specific tension $\sigma = 27.22 \pm 4.84\text{ N/cm}^2$.
- **Mathematical Inconsistency:**
  In `run_exp0059_muscle_models.py`:
  - Line 46: `pcsa = (V / lf) * cos(theta)` (Convention A: PCSA is already projected onto tendon line of action).
  - Line 54: `sigma = torque / (rpat * pcsa * cos(theta) * fl * act)`.
  The script divided by $\cos(14^\circ)$ twice ($\cos^2(14^\circ) = 0.9415$).
- **Rectification:**
  With single cosine projection, the corrected physiological specific tension is:
  $$\sigma_{\text{corrected}} = 27.22 \times \cos(14^\circ) = \mathbf{26.41 \pm 4.70\text{ N/cm}^2}$$
  The discrepancy is exactly $1 / \cos(14^\circ) = 1.0306\times$.

---

### Correction 6: Fallacy of Equivalence via High P-Value in Student's T-Test
- **Identified Discrepancy:**
  Cycle 19 asserted: "Sex invariance of specific tension confirms normalized cross-sectional force generation is identical between men and women" because Welch's t-test yielded $p = 0.8946$.
- **Methodological Error:**
  A high p-value merely fails to reject the null hypothesis $H_0: \mu_M - \mu_F = 0$. It does not provide evidence for equivalence (Absence of evidence is not evidence of absence).
- **Rectification:**
  Formal Two One-Sided Tests (TOST) were conducted:
  - At margin $\Delta = \pm 10\%$ ($2.64\text{ N/cm}^2$): $p_{\text{TOST}} = 0.1449$ ($\mathbf{NOT\ EQUIVALENT}$ at $\alpha = 0.05$).
  - At margin $\Delta = \pm 15\%$ ($3.96\text{ N/cm}^2$): $p_{\text{TOST}} = 0.0535$ (borderline).
  - At margin $\Delta = \pm 20\%$ ($5.28\text{ N/cm}^2$): $p_{\text{TOST}} = 0.0169$ ($\mathbf{EQUIVALENT}$ at $\alpha = 0.05$).
  Conclusion: Male and female specific tensions are statistically equivalent within a $\pm 20\%$ margin, but strict fine-scale biological equivalence cannot be asserted from $N=20$.

---

### Correction 7: Isomass Geometry, Speed, and Mechanical Power Trade-Off
- **Identified Discrepancy:**
  Cycle 19 reported $+25.2\%$ force gain from pennation shift ($14^\circ \to 18^\circ$) with fascicle shortening from $8.40$ to $6.71\text{ cm}$, calling it a $-21.7\%$ reduction in "normalized speed".
- **Mathematical Clarification:**
  1. In the planar constant-thickness aponeurosis model ($h = l_f \sin\theta = \text{const}$):
     $$l_f(18^\circ) = 8.40 \cdot \frac{\sin 14^\circ}{\sin 18^\circ} = \mathbf{6.58\text{ cm}}\quad (-21.71\%)$$
     The force ratio along the tendon is:
     $$\frac{\sin(2 \times 18^\circ)}{\sin(2 \times 14^\circ)} = \frac{\sin 36^\circ}{\sin 28^\circ} = 1.2520 \implies \mathbf{+25.20\%}$$
  2. If fascicle length shortens to $6.71\text{ cm}$ ($-20.1\%$, where $6.71 = 8.40 / 1.252$ under constant PCSA without thickness constraint):
     $$\text{Force Ratio} = 1.252 \times \frac{\cos 18^\circ}{\cos 14^\circ} = 1.2270 \implies \mathbf{+22.70\%}$$
  3. Shortening Velocity: Intrinsic normalized cross-bridge speed ($\tilde{v}_{\max} \approx 10\text{ s}^{-1}$) is **unchanged** if fiber type does not alter. It is the **absolute velocity** $v_{\max} = \tilde{v}_{\max} \cdot l_f$ that drops from $0.840$ to $0.658\text{ m/s}$ ($-21.71\%$).
  4. **The Power Penalty Discovery:**
     Hill's peak mechanical power $P_{\max} \approx 0.098 F_0 v_{\max}$. Under isomass pennation shift:
     $$\frac{P_{\max,1}}{P_{\max,0}} = 1.2520 \times (1 - 0.2171) = 1.2520 \times 0.7829 = 0.9802 \implies \mathbf{-1.98\%}$$
     Increasing pennation angle under fixed muscle volume **increases static holding strength but DECREASES maximum dynamic mechanical power**!
