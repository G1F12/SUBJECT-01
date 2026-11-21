# PRE-REGISTRATION PROTOCOL: EXP-0131 — Link 3 (ADAPT25, Speed, Motor Control, CPE45)

## 1. Scientific Objective & Target Link
- **Target Link**: Link 3 (ADAPT25, Speed, Motor Control, CPE45).
- **Core Scientific Inquiry**: Can the 4-layer Pennes bioheat model reliably predict thermal accumulation against open human exercise data, can 2700-second CPE45 thermal feasibility be achieved via intermittent pacing ($D \le 0.65\text{--}0.92$) vs continuous 360 W breach ($> 39.5^\circ\text{C}$), and can rapid longitudinal strength adaptation (+18.35% at day 14 in Santos cohort) be reconciled with connective tissue safety factor dynamics?
- **Hypothesis**: The 4-layer Pennes bioheat solver demonstrates superior predictive accuracy over persistence and lumped baselines on human cycling heat data. Continuous 360 W induces hyperthermia ($T_{\text{core}} > 39.5^\circ\text{C}$), whereas intermittent duty-cycle pacing maintains thermal equilibrium. Furthermore, rapid neuromuscular adaptation (+18.35% in 14 days) does not cause structural tissue failure when native baseline reserve $SF_0 \ge 1.78$ is present or when progression is tendon-paced.

---

## 2. Cohort Provenance, Data Hygiene & Admission Gates

### 2.1 Audited Datasets
1. **McLaughlin et al. 2025 (`SRC-0086`, Figshare 29120024.v1)**:
   - Source: Open XLSX (`tmp/mclaughlin_29120024.xlsx`, SHA-256: `499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531`).
   - Task: 45-min constant-load cycling in heat across 23 eligible participants, measuring baseline and minute-45 esophageal temperature ($T_{\text{es}}$), ambient temperature, relative humidity, and power.
2. **Santos et al. 2024 (`SRC-0090`)**:
   - Source: Open XLSX (`tmp/data_repository_santos.xlsx`, SHA-256: `8f5b401960c467777ea16d99b6b819476bfe45d1589b14e7b6c05eb50c79ddfe`).
   - Task: 6-week longitudinal leg press training across 10 complete participants measured at W0 (Day 0), W2 (Day 14), W4 (Day 28), and POS (Day 42).
3. **Pennes 4-Layer Bioheat Solver (`EXP-0063`)**:
   - Source: `research/exp0063_pennes_bioheat_cpe45/run_exp0063_pennes_envelope.py`.
   - Method: 4-layer concentric cylinder PDE (core, muscle, fat, skin) with central arterial blood pool, dynamic vasodilation, and sweat evaporation.

---

## 3. Evaluated Models

### 3.1 Thermal Models for McLaughlin 45-Min Heat Data
1. **Persistence Baseline**: $\Delta T_{\text{core}} = 0^\circ\text{C}$.
2. **Lumped-Capacitance Baseline**: Single-compartment whole-body heat balance with constant sweat efficiency.
3. **4-Layer Pennes Bioheat PDE**: Concentric multilayer bioheat equation with arterial perfusion and dynamic thermoregulation.

### 3.2 2700-s CPE45 Thermal Envelope
- Power: 360 W mechanical output ($+20\%$ power, metabolic heat $\sim 1276$ W at $\eta = 0.22$).
- Continuous Mode ($D = 1.00$) vs Intermittent Duty-Cycle Pacing ($D \le 0.92\dots 0.59$) across 4 climate envelopes:
  * Temperate ($20^\circ\text{C}$, 50% RH)
  * Warm ($28^\circ\text{C}$, 50% RH)
  * Hot-Dry ($35^\circ\text{C}$, 20% RH)
  * Hot-Humid ($32^\circ\text{C}$, 80% RH)
- Failure threshold: $T_{\text{core}} > 39.5^\circ\text{C}$.

### 3.3 Tendon Safety Factor & Adaptation Kinetics
- Observed Santos trajectory: $F_{\text{obs}}(t)$ with $+18.35\%$ gain at Day 14.
- Tendon capacity: $C(t) = C_0 [1 + \Delta C_{\max} \frac{\max(0, t - \tau_d)}{\tau_t + \max(0, t - \tau_d)}]$, $C_0 = SF_0 \cdot F_0$.
- Parametric sensitivity across $SF_0 \in [1.20, 2.00]$, $\tau_d \in [0, 21]$ d, $\tau_t \in [42, 126]$ d, and damage exponent $B \in [3, 12]$.

---

## 4. Evaluation Metrics & Success Criteria
- Thermal error: MAE, RMSE, and Bias in $^\circ\text{C}$.
- Paired difference: $\Delta\text{MAE} = \text{MAE}_{\text{baseline}} - \text{MAE}_{\text{Pennes}}$ (positive favors Pennes).
- Bootstrap test: $B = 10,000$ resamples of participants.
- Success criteria: Pennes model strictly superior to persistence ($\Delta\text{MAE} > 0.30^\circ\text{C}$, 95% CI $> 0$).
- Safety factor invariant: $SF(t) \ge 1.50$ (critical threshold $SF_0 \ge 1.776$ for 0-day deficit).
