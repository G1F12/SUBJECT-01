# SUBJECT-01 — handoff: EXP-0042 Scientific Corrigendum & Model Integrity

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: b98c3eb68654dc8f22ce1dd64be70c3b45528623.
Ветка: fix/exp-0042-scientific-corrigendum (слияние в main).

Ключевые документы и инструменты:
- research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md (мастер-отчёт научной валидации с корригендумом: сверка чисел, реклассификация M2, статус M3, ретракция pH, разделение сценариев переноса)
- research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json (канонический артефакт валидации: проверенные амплитуды PCr, точные RMSE и R2, перенос, идентифицируемость)
- research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json (извлечённые временные ряды PCr/Pi, 222 спектра, 3 триала, SHA256 af6a396b...)
- tools/evaluate_rehman_models.py (сквозной движок 5 этапов научной валидации)
- tests/test_rehman_model_validation.py (10 тестов: лаг тайминга, чувствительность, аудит pH, перенос M2/M1, запрет LOSO, идентифицируемость, сверка отчёта и JSON)
- tools/process_rehman_xlsx.py (процессор сырых данных Rehman 2024)
- tests/test_rehman_xlsx_processor.py (17 тестов процессора Rehman XLSX)
- tools/verify_data_provenance.py (постоянный автоматический гейт Evidence Gate V2)
- tests/test_evidence_gate_v2.py (12 тестов Evidence Gate V2)

Результаты завершённого научного корригендума EXP-0042:
1. **Числовая сверка отчёта и канонического JSON**:
   - Амплитуды PCr на 90 с: Trial 1 = 1920.0, Trial 2 = 1291.0, Trial 3 = 1277.0.
   - Амплитуды PCr в надире: Trial 1 = 1670.0 (144 с, лаг +54 с), Trial 2 = 1245.0 (108 с, лаг +18 с), Trial 3 = 1231.0 (108 с, лаг +18 с).
   - In-sample RMSE:
     * M0: T1 = 230.8789, T2 = 120.2115, T3 = 141.6887 (R2 отрицательный: -0.553, -1.130, -0.962).
     * M1: T1 = 26.0469, T2 = 15.7271, T3 = 14.7023 (R2: 0.9802, 0.9639, 0.9789).
     * M2: T1 = 31.7198, T2 = 37.6714, T3 = 32.7989 (R2: 0.9706, 0.7928, 0.8951).
   - Внедрён автоматический тест `test_report_markdown_json_consistency`.
2. **Аудит тайминга и физиологических терминов**:
   - $t_{\text{start}}=48\text{ с}$ и $t_{\text{stop}}=90\text{ с}$ классифицированы как `INFERRED_TIMING_ASSUMPTION` (аудиокоманды оператора, отсутствие аппаратного TTL).
   - Надир классифицирован как `OBSERVED_SPECTRAL_MINIMUM_DISTINCT_FROM_MECHANICAL_STOP`.
   - Термины «ишемический/гиперемический лаг» исключены из категорических выводов при отсутствии данных плетизмографии/кровотока.
3. **Аудит pH и научная ретракция**:
   - Утверждение о повсеместном «$\text{pH} \ge 6.86$» официально отозвано как устаревшее.
   - Минимальный расчётный pH: Trial 1 = 6.7932, Trial 2 = 6.8840, Trial 3 = 6.8911 (диапазон $6.7932\dots 7.0228$).
   - Статус `PH_CALIBRATION_PARTIAL` сохранён без искусственных поправок. Категорические утверждения о сугубо аэробном метаболизме без газов крови запрещены.
4. **Реклассификация моделей и статус M3**:
   - M2 реклассифицирована в `CONSTRAINED_MONOEXPONENTIAL_BASELINE` ($d\text{PCr}/dt = k \cdot (\text{PCr}_{\text{rest}} - \text{PCr})$).
   - Утверждения о валидации баланса энергий, кислородного транспорта, оборота АТФ или двигательных единиц на M2 сняты.
   - Полная физиологическая модель M3 получила статус `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS` (отсутствие механической мощности, крутящего момента, PCSA и спирометрии).
5. **Разграничение режимов переноса**:
   - Сценарий A (`CONDITIONAL_TRAJECTORY_RECONSTRUCTION`, при известных надире и базовом уровне): M2 переносит параметр $k$ со средним $R^2 = 0.8566$ (диапазон $0.7696\dots 0.9603$), M1 — со средним $R^2 = 0.8268$ (диапазон $0.7552\dots 0.8872$).
   - Сценарий B (`PROSPECTIVE_PREDICTION`, прогноз от 90 с без знания будущего надира и лага): заблокирован (`PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS`).
   - Кросс-субъектная валидация LOSO на $N=1$ строго запрещена (`LosoProhibitedError`).
6. **Матрица идентифицируемости**:
   - Идентифицированы: $\tau = 39.72 \pm 3.81\text{ с}$, $k = 1.520 \pm 0.151\text{ мин}^{-1}$, $\text{CV}\% = 9.90\%$, доля истощения $28.36\%$, динамика pH ($6.7932\dots 7.0228$).
   - Строго неидентифицируемы: $[\text{PCr}]_{\text{rest}}$, $V_{\text{active}}$, $J_{\text{ATP}}$, $\eta_{\text{loc}}$, $Q_{\text{max}}$, $\text{TARGET-CPE45}$.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=42, FND=42, NEG=35, DEC=16, ISS=19, SRC=72.
- Тесты: 207/207 PASS (включая 10 тестов валидации моделей Rehman).
