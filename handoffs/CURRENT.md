# SUBJECT-01 — handoff: Real PCr Validation & Scientific Freeze

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: fd1793623eee8ac6bf9df8f96378d177198fbe91.
Ветка: main (слияние feature/real-pcr-validation-and-scientific-freeze).
Итоговый main SHA: 32adefce36801c6357836f60541f3ea3e0d70131.

Ключевые документы и инструменты:
- research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md (мастер-отчёт научной валидации и эпистемической заморозки реальных данных Rehman 2024)
- research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json (канонический артефакт валидации: тайминг, чувствительность, аудит pH, сравнение M0/M1/M2, внутрисубъектный перенос, идентифицируемость; SHA256 b88e82c2...)
- research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json (извлечённые временные ряды PCr/Pi, 222 спектра, 3 триала, SHA256 af6a396b...)
- tools/evaluate_rehman_models.py (сквозной движок 5 этапов научной валидации)
- tests/test_rehman_model_validation.py (9 тестов валидации моделей Rehman: лаг тайминга, чувствительность, аудит pH, перенос M2, запрет LOSO, идентифицируемость)
- tools/process_rehman_xlsx.py (процессор сырых данных Rehman 2024)
- tests/test_rehman_xlsx_processor.py (17 тестов процессора Rehman XLSX)
- tools/verify_data_provenance.py (постоянный автоматический гейт Evidence Gate V2)
- tests/test_evidence_gate_v2.py (12 тестов Evidence Gate V2)

Результаты завершённой научной валидации:
1. **Реконструкция тайминга**:
   - Преднагрузочный покой: $12.0\dots 48.0\text{ с}$ (спектры 2–8).
   - Номинальная нагрузка 42 с: $48.0\dots 90.0\text{ с}$ (спектры 9–15).
   - Фактический надир PCr: $144.0\text{ с}$ в триале 1 (лаг $+54\text{ с}$, фаза затяжного истощения), $108.0\text{ с}$ в триалах 2 и 3 (лаг $+18\text{ с}$).
   - Опубликованные константы $k$ получены расчётом строго от надира; принудительный фит от номинальных 90 с даёт занижение $k$ на ~30%. Статус: `PROTOCOL_TIMING_DISCREPANCY_IDENTIFIED`.
2. **Чувствительность кинетики**:
   - Сдвиги от $-18\text{ с}$ до $+18\text{ с}$ выявили систематическую неопределённость фазовой разметки $\Delta k_{\text{sys}} = \pm 0.044\dots 0.172\text{ мин}^{-1}$, сопоставимую с ковариационной погрешностью $\text{CI}_{95} = \pm 0.12\dots 0.18\text{ мин}^{-1}$.
   - Донадирные сдвиги искажают релаксацию активным расходом PCr, снижая $k$ на 20–33%. Статус: `PHASE_SELECTION_SENSITIVITY_QUANTIFIED`.
3. **Аудит pH**:
   - Смещение $\Delta\text{pH} = -0.055 \pm 0.010$ единиц относительно Таблицы 1 статьи объяснено различиями в константах $pK_a$ в литературе ($6.75$ vs $6.80$ при $37^\circ\text{C}$), смещением референтного нуля в jMRUI AMARES и округлением в Excel.
   - Эмпирические подгоночные поправки в код отвергнуты; статус: `PH_CALIBRATION_PARTIAL`.
   - Внутриклеточный pH остаётся $\ge 6.86$, подтверждая неацидотический аэробный профиль восстановления.
4. **Сравнение моделей и внутрисубъектный перенос**:
   - In-sample подгонки строго маркированы `IN_SAMPLE_FIT_NOT_VALIDATION`.
   - Физиологическая модель M2 (1-параметрическая ODE с фиксацией PCr покоя) при кросс-триальном переносе (6 пар $i \to j$) достигла среднего $R^2 = 0.8566$ (диапазон $0.7696\dots 0.9603$, снижение RMSE на 60% по сравнению с M0).
   - Статус: `WITHIN_SUBJECT_TRIAL_TRANSFER_COMPLETED`.
   - Кросс-субъектная валидация LOSO на $N=1$ строго запрещена (`LosoProhibitedError`).
5. **Матрица идентифицируемости**:
   - Идентифицированы: $\tau = 39.72 \pm 3.81\text{ с}$, $k = 1.520 \pm 0.151\text{ мин}^{-1}$, $\text{CV}\% = 9.90\%$, доля истощения $28.36\%$, неацидотический pH.
   - Строго неидентифицируемы: $[\text{PCr}]_{\text{rest}}$, $V_{\text{active}}$, $J_{\text{ATP}}$, $\eta_{\text{loc}}$, $Q_{\text{max}}$, $\text{TARGET-CPE45}$.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=42, FND=42, NEG=35, DEC=16, ISS=19, SRC=72.
- Тесты: 206/206 PASS (включая 9 новых тестов валидации моделей Rehman).
