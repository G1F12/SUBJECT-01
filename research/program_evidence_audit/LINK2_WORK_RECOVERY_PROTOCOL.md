# PRE-REGISTRATION PROTOCOL: EXP-0130 — Link 2 (Work Done → Residual Force → Recovery)

## 1. Scientific Objective & Target Link
- **Target Link**: Link 2 (Work Done → Residual Force → Recovery).
- **Core Scientific Inquiry**: Can cumulative external mechanical work (Joules or kg·reps) predict post-exercise residual force capacity, or does empirical evidence refute monotonic scalar work-depletion equations ($F = F_0(1 - f(W))$) in favor of domain-partitioned, recovery-dependent multi-component models?
- **Hypothesis**: Simple scalar work models fail out-of-sample against naive retention baselines and are falsified by training adaptations where higher mechanical work co-occurs with superior force retention. Valid prediction requires a 4-component transition model incorporating intensity domains (Critical Power), bi-compartmental fatigue, recovery kinetics, and task specificity.

---

## 2. Cohort Provenance, Data Hygiene & Admission Gates

### 2.1 Audited Datasets
1. **Norbury et al. 2024 (`SRC-0111`)**:
   - Source: Open repository (`tmp/norbury_24156741.xlsx`, SHA-256: `295cbe90ebb84e7bfa3cd2804d81f87663b16088bdc06021256343d6f57acb9e`).
   - Task: Bilateral leg press in 12 healthy males under Low Load (LL, 30% 1RM) and High Load (HL, 70% 1RM) conditions (24 paired trials).
   - Measurements: Pre-exercise MVC force, 5-min post-exercise MVC, 45-min post-exercise MVC, 24-h post-exercise MVC, and load volume in kg·reps.
2. **de Poli et al. 2026 (`SRC-0102`, DOI: 10.1002/ejsc.70089)**:
   - Source: Published group-level data (Table 3) from Eur J Sport Sci.
   - Task: Constant work rate (CWR) cycling at 150% RCP-PO to task failure in 21 active males (11 Sprint Interval Training [SIT], 10 Control), measuring pre- and post-exercise isometric knee extension force ($25 \pm 7$ s latency) before and after 5 weeks of training.
   - Status: Scope restricted strictly to published group means; individual continuous series are available only upon author request (governance-blocked).
3. **McLaughlin et al. 2025 (`SRC-0086`, Figshare 29120024.v1)**:
   - Source: Open dataset (`tmp/mclaughlin_29120024.xlsx`, SHA-256: `499f546648822d99465c476702183cd3e37bdbaa6274de383f542708b052d531`).
   - Task: Constant-load cycling in heat over 45 minutes (2700 s), 23 eligible participants, measuring power output (W), total work (kJ), and body mass.

---

## 3. Evaluated Models

### 3.1 Candidate Models for Post-Exercise Force (Leave-One-Subject-Out CV)
1. **Persistence Baseline (Zero Loss)**:
   $$\hat{F}_{\text{post}, i} = F_{\text{pre}, i}$$
2. **Mean Retention Baseline**:
   $$\hat{F}_{\text{post}, i} = F_{\text{pre}, i} \cdot \bar{r}_{-i}, \quad \bar{r}_{-i} = \frac{1}{N-1} \sum_{j \neq i} \frac{F_{\text{post}, j}}{F_{\text{pre}, j}}$$
3. **Mean Loss Baseline**:
   $$\hat{F}_{\text{post}, i} = F_{\text{pre}, i} - \bar{\Delta}_{-i}, \quad \bar{\Delta}_{-i} = \frac{1}{N-1} \sum_{j \neq i} (F_{\text{pre}, j} - F_{\text{post}, j})$$
4. **Volume Linear Model**:
   $$\hat{F}_{\text{post}, i} = F_{\text{pre}, i} \cdot (a_{-i} + b_{-i} \cdot \text{Vol}_i)$$
5. **Volume Proportional D2-Type Model**:
   $$\hat{F}_{\text{post}, i} = F_{\text{pre}, i} \cdot \max(0, 1 - k_{-i} \cdot \text{Vol}_i)$$
6. **4-Component Candidate Transition Model**:
   $$\hat{F}(t) = F_{\text{pre}} \cdot [ 1 - d_{\text{peripheral}}(W, \text{domain}) - d_{\text{central}}(W, \text{domain}) ] + R(t_{\text{latency}})$$
   accounting for intensity domain thresholding, peripheral metabolite vs central drive fatigue, and exponential recovery operator $R(t) = (F_{\text{pre}} - F_{\text{end}})(1 - e^{-t/\tau_{\text{recov}}})$.

---

## 4. Evaluation Metrics & Success Criteria
- Primary Error Metric: Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and Mean Signed Bias (Bias).
- Paired Difference: $\Delta\text{MAE} = \text{MAE}_{\text{baseline}} - \text{MAE}_{\text{model}}$ (positive favors model).
- Inferential Test: Participant-clustered bootstrap ($B = 10,000$ resamples with paired LL and HL conditions locked by subject ID).
- Benchmark Criteria:
  * Rejection threshold: $\Delta\text{MAE} < 0$ with 95% CI strictly $< 0$ indicates model defeat by trivial baseline.
  * Directional concordance check: Increasing mechanical work must predict greater force drop; opposite observed direction refutes monotonic scalar equations.

---

## 5. Partitioning & Cross-Validation
- Norbury: Leave-One-Subject-Out cross-validation across 12 subjects (24 paired observations); bootstrap clustering grouped by participant ID (`reshape(12, 2)`).
- de Poli: Formal comparison of pre- vs post-training work and force retention shifts in SIT vs Control groups.
- McLaughlin: Cumulative work calculation ($W = P \cdot 2700\text{ s}$) and intensity domain cross-comparison.
