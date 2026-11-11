# AEGIS-01 — Human Thermoregulation Matched Holdout Test
**Research Cycle 6 — Question C: Multi-Node Model vs Simple Baseline**  
**Document ID:** `AEGIS-DOC-C6-THERMAL-TEST`  
**Execution Date:** 2026-11-10  
**Test Module:** `aegis.cycle6_validation`  
**Experiment ID:** `EXP-0083` | **Finding ID:** `FND-0094` | **Negative Result:** `NEG-0079` | **Hypothesis ID:** `HYP-0037`

---

## 1. Research Question & Physical Scope

### Research Question C
> *Can a 3-node dynamic thermal model (Core, Active Muscle, Skin) incorporating convective blood flow and vasodilation kinetics predict core temperature heating rates ($dT_{\text{re}}/dt$) significantly more accurately than a simple 1-node lumped-capacitance baseline under strictly matched human experimental conditions?*

### Physical Problem Setting
In uncompensable heat stress—where ambient temperature is high and personal protective encapsulation (clothing/armor) prevents evaporative sweat cooling—the human body acts as a heat accumulator:
$$\frac{dS}{dt} = M - W_{\text{mech}} - (H_{\text{dry}} + E_{\text{evap}} + Q_{\text{res}}) > 0$$
Under standard military chemical overgarments (BDO / MOPP-4, $I_{\text{cl}} = 1.5\text{ clo}$, $i_m = 0.38$) or dense whole-body biological armor, maximum evaporative capacity $E_{\text{max}}$ is restricted to $< 110\text{ W}$, while metabolic heat production during walking ranges from $380\text{ W}$ to $540\text{ W}$.

---

## 2. Experimental Holdout Dataset: Montain et al. (1994)

To prevent parameter overfitting and synthetic leakage, models were evaluated on the published empirical human trial dataset from **Montain, Sawka, Cadarette, Quigley, and McKay (1994)** (*J Appl Physiol* 77(1):216–222):
- **Ambient Temperature ($T_a$):** $35.0^\circ\text{C}$ (matched tropical climate)
- **Relative Humidity ($\text{RH}$):** $50.0\%$ (water vapor pressure $P_a = 2.81\text{ kPa}$)
- **Airflow Velocity ($v$):** $1.0\text{ m/s}$
- **Clothing Ensemble:** Battle dress overgarment ($I_{\text{cl}} = 1.5\text{ clo}$, $i_m = 0.38$)
- **Subject Characteristics:** Mass $73.0\text{ kg}$, Body surface area $A_D = 1.88\text{ m}^2$
- **Trial Duration:** $50\text{ min}$ ($3000\text{ s}$)
- **Workloads Evaluated:**
  - Case 1: Moderate Walking ($M = 425\text{ W}$, $v_{\text{walk}} = 1.34\text{ m/s}$)
  - Case 2: Heavy Walking ($M = 600\text{ W}$, $v_{\text{walk}} = 1.78\text{ m/s}$)
- **Observed Rectal Heating Rates:**
  - $425\text{ W}$: $dT_{\text{re}}/dt = 0.0324 \pm 0.0050^\circ\text{C/min}$ (final rise $\Delta T_{\text{re}} = 1.62^\circ\text{C}$)
  - $600\text{ W}$: $dT_{\text{re}}/dt = 0.0460 \pm 0.0065^\circ\text{C/min}$ (final rise $\Delta T_{\text{re}} = 2.30^\circ\text{C}$)

---

## 3. Evaluated Model Formulations

### 3.1 Model 1: Simple 1-Node Lumped Capacitance Baseline
Assumes the entire body is an isothermal lumped thermal capacitor ($C_{\text{body}} = 253,310\text{ J/K}$):
$$C_{\text{body}} \frac{dT}{dt} = M - W_{\text{mech}} - \left[ \frac{A_D(T - T_a)}{R_{\text{cl}} + R_a} + \frac{A_D (P_{\text{sat}}(T) - P_a)}{R_{\text{evap}}} + Q_{\text{res}} \right]$$

### 3.2 Model 2: 3-Node Dynamic Thermal Model
Divides the body into Core ($50\%$ mass), Active Skeletal Muscle ($40\%$ mass), and Skin ($10\%$ mass):
$$\begin{aligned}
C_m \frac{dT_m}{dt} &= H_m - \dot{V}_{b,m} \rho_b c_b (T_m - T_c) - K_{mc}(T_m - T_c) \\
C_c \frac{dT_c}{dt} &= H_c + \dot{V}_{b,m} \rho_b c_b (T_m - T_c) + K_{mc}(T_m - T_c) - \dot{V}_{b,s} \rho_b c_b (T_c - T_s) - K_{cs}(T_c - T_s) - Q_{\text{res}} \\
C_s \frac{dT_s}{dt} &= \dot{V}_{b,s} \rho_b c_b (T_c - T_s) + K_{cs}(T_c - T_s) - H_{\text{dry}} - E_{\text{max}}
\end{aligned}$$
where metabolic heat is split $85\%$ muscle / $15\%$ core, and skin blood flow $\dot{V}_{b,s}$ vasodilates with core hyperthermia.

---

## 4. Quantitative Holdout Comparison

```
========================================================================================
CONDITION      OBSERVED RATE        1-NODE BASELINE      3-NODE MODEL        DISCREPANCY
========================================================================================
425 W Workload 0.0324 C/min         0.0439 C/min         0.0425 C/min        +0.0101 C/min
600 W Workload 0.0460 C/min         0.0750 C/min         0.0739 C/min        +0.0279 C/min
----------------------------------------------------------------------------------------
MAE            --                   0.02025 C/min        0.01899 C/min       -6.2% error
========================================================================================
```

---

## 5. Epistemic Audit & Negative Result (`NEG-0079`)

1. **Marginal Improvement:** The 3-node dynamic model yields only a **6.2% error reduction** over the 1-node baseline (MAE $0.01899$ vs $0.02025^\circ\text{C/min}$).
2. **Physical Causes of Divergence:**
   - **Rectal Sensor Lag:** Clinical rectal thermistors lag arterial blood temperature by $10\text{--}15\text{ minutes}$ during exercise transitions. Both models track true core blood temperature, which rises faster than rectal temperature in early exercise.
   - **Clothing Sweat Microclimate:** In live subjects, unevaporated liquid sweat pools in undergarments and on the skin surface, increasing thermal conduction and transiently buffering early heat rise.
3. **Formal Negative Result:** Per Cycle 6 research rules (*"Если новая модель не уменьшает ошибку прогноза [существенно], оставь прежнюю простую модель и зарегистрируй отрицательный результат"*), adding 3-node complexity without empirical clothing sweat-pumping dynamics does not justify discarding the simple baseline.
4. **Epistemic Verdict:** `THERMAL_EXTERNAL_VALIDATION = PARTIAL` (1-node baseline retained as the primary parsimonious model; negative result `NEG-0079` registered).
