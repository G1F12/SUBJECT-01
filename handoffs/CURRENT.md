# SUBJECT-01 — handoff: Cycle 11 Scientific Corrigendum & Subject-Level GroupKFold Validation (EXP-0044)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 68ed5137492525ddf487be8bfc629586a853250d.
Ветка: correction/cycle11-subject-level-validation-corrigendum (слияние в main).

Ключевые документы и инструменты:
- research/treadmill_cpet_2026_11_09/TREADMILL_CPET_REPORT.md (мастер-отчёт валидации беговой локомоции Malaga Treadmill CPET с GroupKFold, N=846)
- research/treadmill_cpet_2026_11_09/malaga_validation_results.json (канонический JSON валидации Malaga GroupKFold, EXP-0044)
- tools/generate_malaga_report_tables.py (генератор структурных таблиц Markdown из JSON для Malaga и валидатор 1:1 соответствия)
- tools/evaluate_malaga_treadmill.py (движок 5-фолдового GroupKFold без утечек, бутстрепа и парных тестов)
- tests/test_malaga_cpet_validation.py (16 юнит-тестов Malaga: 0-утечка GroupKFold, негативный тест на утечку, 3 теста структурной согласованности, запрет прямого калориметрического вывода, негативный запрет чистой ODC-By)
- research/treadmill_cpet_2026_11_09/empirical_datasets_cycle11.json (реестр эмпирических датасетов с фиксацией ISS-0020)
- research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md (мастер-отчёт мультисубъектной валидации CPET ACTES)
- research/cpet_cycloergometer_2026_11_09/actes_validation_results.json (канонический JSON ACTES с анализом чувствительности эффективности)
- tools/evaluate_actes_models.py (движок анализа ACTES и оценки чувствительности параметров эффективности)
- tests/test_actes_cpet_validation.py (13 тестов ACTES: структурная согласованность, 4 негативных теста, исправление 37.49% кажущейся эффективности)
- registry/decisions.json (DEC-0019: утверждение научного корригендума)
- registry/issues.json (ISS-0020: отслеживание лицензионного конфликта PhysioNet Malaga)
- tools/verify_data_provenance.py / tools/validate_repository.py (сквозные валидаторы целостности реестров)

Результаты этапов (Cycle 11 Scientific Corrigendum & Subject-Level Validation):
1. **Ликвидация групповой утечки данных (GroupKFold по subject_id, EXP-0044)**:
   - Устранена биологическая утечка: случайное разбиение тестов заменено на строго детерминированный `GroupKFold(n_splits=5, groups=subject_id)`.
   - Программно доказано: $\text{intersection}(\text{train\_subject\_ids}, \text{val\_subject\_ids}) == \emptyset$ для всех фолдов.
   - Из 857 уникальных участников после фильтрации допущены 846 участников (981 тест, 11 отсеяно).
   - Все 116 повторных участников (251 тест) сохранены строго внутри фолдов.
   - Фолды: F0 (169/197), F1 (169/196), F2 (169/196), F3 (169/196), F4 (170/196).
   - Историческое случайное разбиение сохранено как legacy-бенчмарк с меткой `SUBJECT_LEAKAGE_RISK_NOT_GROUPED`.
2. **Реконсилиация отчётов и автогенерация (Stage 2)**:
   - Создан `tools/generate_malaga_report_tables.py`, синхронизирующий таблицы Markdown на 100% с JSON.
   - Внедрены проверки целостности и негативные тесты на подмену $n$, RMSE, $R^2$, bias, `model_id`.
3. **Коррекция энергетической эффективности ACTES (Stage 3, DEC-0019)**:
   - Исправлена арифметика: $\beta_1 = 0.00765744$ л/мин/Вт, $c_{\text{ox}} = 20.9$ кДж/л $\implies \eta_{\text{apparent}} \approx 37.49\%$ (не 25.5%).
   - Проведён анализ чувствительности ($\tau = 0\dots 60$ с, базовый интерцепт покоя $0.35$ л/мин $\to 28.52\%$).
   - Установлен статус `DELTA_EFFICIENCY_NOT_IDENTIFIABLE_FROM_UNLAGGED_RAMP`.
4. **Физический аудит межмодального переноса (Stage 4, NEG-0037, DEC-0019)**:
   - Формула `560.0 + (7.657 * 25.0) * speed` переклассифицирована в `AD_HOC_CROSS_MODAL_MAPPING_FAILURE`.
   - Присвоен статус `PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE` ввиду отсутствия измеренной механической мощности бега.
5. **Метрологический аудит оксикалорического эквивалента (Stage 5)**:
   - $\dot{V}\text{O}_2, \dot{V}\text{CO}_2, \text{RER}$ классифицированы как `MEASURED`; $c_{\text{ox}}$ — `DERIVED_MODEL_DEPENDENT`; нестационарные субстраты — `NOT INDEPENDENTLY VALIDATED`.
   - 46.8% точек с $\text{RER} > 1.0$ отражают гипервентиляцию и буферизацию лактата $\text{HCO}_3^-$, а не прямое окисление.
   - Расхождение 2.26% признано артефактом клиппирования RER.
6. **Научная генерализация и статистика (Stage 6)**:
   - Превосходство M4 (аллометрическая ОДУ) подтверждено: RMSE $= 404.0 \pm 175.1$ мл/мин, $R^2 = 0.6648 \pm 0.7374$, с парным t-тестом $p = 6.78 \times 10^{-26}$ против M3.
   - Персистентный бейзлайн (RMSE $= 96.6$ мл/мин) признан авторегрессионным с информационным преимуществом.
   - Разделены уровни валидации A (ACTES), B (Malaga), C (межмодальный перенос — неидентифицируем).
7. **Аудит лицензий (Stage 7, ISS-0020)**:
   - Зафиксирован тройственный конфликт условий PhysioNet Malaga v1.0.1 (PhysioNet License vs CC BY-NC-SA 4.0 vs ODC-By v1.0), открыт `ISS-0020`.
8. **Эпистемические инварианты**:
   - TARGET-CPE45: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=44, FND=44, NEG=37, DEC=19, ISS=20, SRC=75.
