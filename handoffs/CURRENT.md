# SUBJECT-01 — handoff: EXP-0042 Final Numerical Lock & Cycle 10 Multi-Subject CPET Validation

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 7ee8c127dad2a56bef4427c8e9e5777bdc385b8c.
Ветка: feature/exp-0042-numerical-lock-cycle10 (слияние в main).

Ключевые документы и инструменты:
- research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md (мастер-отчёт Rehman 2024 с числовым локом EXP-0042)
- research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json (канонический JSON валидации Rehman, тег EXP-0042_NUMERICALLY_LOCKED)
- tools/generate_rehman_report_tables.py (генератор структурных таблиц Markdown из JSON и валидатор 1:1 соответствия)
- tests/test_rehman_model_validation.py (13 тестов: структурная сверка Markdown/JSON, негативные тесты перестановки и подмены)
- research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md (мастер-отчёт мультисубъектной валидации CPET ACTES, N=18)
- research/cpet_cycloergometer_2026_11_09/actes_validation_results.json (канонический JSON валидации ACTES, EXP-0043)
- research/cpet_cycloergometer_2026_11_09/DATASET_RANKING.md (систематический рейтинг кандидатов Cycle 10 по 10 критериям)
- research/cpet_cycloergometer_2026_11_09/REMAINING_BARRIERS_MATRIX.md (матрица остаточных барьеров и неидентифицируемости M3)
- tools/evaluate_actes_models.py (движок строгой кросс-валидации Leave-One-Subject-Out на 18 участниках)
- tests/test_actes_cpet_validation.py (7 тестов валидации ACTES CPET: целостность хэшей, иерархия моделей, негативные тесты)
- tools/validate_repository.py (сквозной валидатор целостности реестров и доказательного гейта Evidence Gate V2)

Результаты этапов A, B, C, D (Cycle 10):
1. **Этап A — EXP-0042 Final Numerical Lock**:
   - Канонические значения базового PCr:
     * Trial 1: mean = 2481.4286, SD = 74.2582
     * Trial 2: mean = 1679.0000, SD = 38.7126
     * Trial 3: mean = 1675.5714, SD = 34.2143
   - Канонические значения константы M2 $k$:
     * Trial 1: 1.2978707 мин^-1
     * Trial 2: 1.1468669 мин^-1
     * Trial 3: 0.9696332 мин^-1
   - Подтверждено 100% совпадение с исходными наблюдениями (`rehman2024_extracted_timeseries.json`).
   - Примитивный `assertIn` заменён структурным сравнением (`tools/generate_rehman_report_tables.py`).
   - Добавлены 3 негативных теста (перестановка триалов, подмена столбцов метрик, число в постороннем тексте).
   - Зафиксирован тег `EXP-0042_NUMERICALLY_LOCKED`.
2. **Этап B & C — Поиск и строгое ранжирование датасетов Cycle 10**:
   - Проведён систематический аудит открытых репозиториев (PhysioNet, Dryad, Figshare, Zenodo, OpenNeuro).
   - Ранжированы ведущие кандидаты:
     1. PhysioNet ACTES Cycloergometer (SRC-0073, DOI: 10.13026/2qs3-kh43, N=18) — ВЫБРАН для валидации.
     2. Dryad Hug et al. 2015 (DOI: 10.5061/dryad.h3b27, N=21) — квадрицепс МРТ/УЗИ архитектура + динамометрия.
     3. Dryad Rehman et al. 2024 (SRC-0069, DOI: 10.5061/dryad.08kprr59v, N=1) — локальная 31P-МРС кинетика.
     4. PhysioNet Malaga Treadmill (DOI: 10.13026/7ezk-j442, N=992) — тредмил-спирометрия спортсменов.
     5. Figshare InSight Trial (DOI: 10.1038/srep01182, N>100) — институциональный доступ.
3. **Этап D — Первая независимая мультисубъектная проверка (EXP-0043, N=18)**:
   - Приобретён датасет PhysioNet ACTES: 18 участников-спортсменов, 52,062 beat-to-beat измерения (мощность, VO2, RR).
   - Байтовое совпадение SHA256 проверено (`14a9df02...`, `5ac7cdd4...`).
   - Проведена строгая Leave-One-Subject-Out (LOSO) кросс-валидация на 18 фолдах с замороженными параметрами:
     * M0 (константа): R2 = -0.8343, RMSE = 0.773 л/мин
     * M1 (статическая линейная): R2 = 0.4045, RMSE = 0.416 л/мин
     * M2_pop (динамическая ОДУ, tau = 35 с): R2 = 0.6059, RMSE = 0.317 л/мин
     * M2_allometric (аллометрическая ОДУ, W/кг -> мл/мин/кг): R2 = 0.7371 +/- 0.1770, RMSE = 0.290 +/- 0.059 л/мин.
   - Ратифицирована матрица остаточных барьеров (`REMAINING_BARRIERS_MATRIX.md`): макроскопический VO2 НЕ валидирует внутриклеточные фосфаты ([PCr], [Pi], [ATP]), pH или рекрутирование ДЕ из-за проблемы «многие-к-одному».

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=43, FND=43, NEG=36, DEC=17, ISS=19, SRC=73.
- Тесты: 74/74 PASS, Evidence Gate V2 PASS.
