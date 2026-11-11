# SUBJECT-01 — handoff: Cycle 12 Human Muscle Force, Fatigue & Biomechanical Empirical Validation (EXP-0045) — Final Scientific Audit

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 64668170f2eece8e96fad6349a92ab5175725e4d (origin/main).
Ветка: feature/cycle12-bird-raw-empirical-validation.

Ключевые документы и инструменты:
- research/muscle_force_biomechanics_2026_11_10/BIOMECHANICAL_VALIDATION_REPORT.md (мастер-отчёт биомеханической валидации силы мышц и утомления Bird et al. 2026)
- research/muscle_force_biomechanics_2026_11_10/biomechanics_validation_results.json (канонический JSON валидации биомеханики Bird 2026, EXP-0045)
- research/muscle_force_biomechanics_2026_11_10/bird2026_empirical_validation.json (канонический JSON независимой эмпирической валидации, аудита данных и LOSO по сырым массивам)
- research/muscle_force_biomechanics_2026_11_10/observed_variables_registry.json (реестр онтологии наблюдаемых и расчётных переменных)
- research/muscle_force_biomechanics_2026_11_10/empirical_datasets_cycle12.json (реестр эмпирических датасетов Cycle 12)
- research/muscle_force_biomechanics_2026_11_10/sources.json (реестр источников Cycle 12, SRC-0076)
- tools/process_bird_raw_data.py (пайплайн верификации SHA-256, воспроизведения авторских моделей, проверки чувствительности радара и фальсификации M4)
- tools/generate_biomechanics_report_tables.py (генератор структурных таблиц Markdown из JSON для биомеханики)
- tools/evaluate_bird_biomechanics.py (движок сократительной биомеханики, декуплинга, утомления, 4-уровневой таксономии и аудита ограничений)
- tests/test_bird_biomechanics_validation.py (25 юнит-тестов биомеханики: криптография, аудит наблюдений, схемы CV, сьют чувствительности радара, фальсификация M4, 4 негативных теста)
- registry/experiments.json (EXP-0045: статус completed_empirical_raw_data_and_loso_evaluated)
- registry/findings.json (FND-0045: эмпирический декуплинг, воспроизведение авторских моделей, коллапс обобщения UWB радара в LOSO, фальсификация M4)
- registry/negative_results.json (NEG-0038: запрет экстраполяции момента одного сустава на TARGET-CPE45; NEG-0039: коллапс UWB-радара и фальсификация M4 против sEMG)
- registry/decisions.json (DEC-0020: утверждение онтологии, 4-уровневой таксономии, аудита физических ограничений и приоритизации архитектур аугментации)
- tools/verify_data_provenance.py / tools/validate_repository.py (сквозные валидаторы целостности реестров)

Результаты этапов (Cycle 12 Финальный научный аудит эмпирической валидации):
1. **Аудит сырых данных и устранение расхождения наблюдений (Stage 1)**:
   - Полностью проверены и подтверждены 3 226 строк динамических наблюдений в `DATA_Dynamic_Knee.mat`:
     * 1 382 пассивных наблюдения (момент $T = 0.0$ Н·м по определению);
     * 1 821 активное положительное сокращение ($T > 0.0$ Н·м);
     * 23 наблюдения отрицательного дрейфа датчика динамометра ($[-0.0207, -0.00066]$ Н·м около угла $84\dots 90^\circ$ у участников 1, 3, 4, 5).
     * Сумма: $1382 + 1821 + 23 = 3226$ (100% учёт, 0 NaN по всем каналам).
   - Разделение «со всеми точками» и «только активные»: пассивные нули создают искусственный якорь около нуля, завышая видимый $R^2$ (M1 $R^2 = 0.463$, M4 $R^2 = 0.325$); строго на активных точках без калибровки все модели уходят в отрицательный $R^2$ (M1 $R^2 = -0.088$, M3 $R^2 = -0.162$, M4 $R^2 = -0.141$, UWB $R^2 = -6.663$).
2. **Аудит схем кросс-валидации и исключение утечек (Stage 2)**:
   - Разделены 5 категорий: `INTRA_SUBJECT_CV` (авторское перемежение 1-из-5 точек с автокорреляционной утечкой $\pm 100$ мс), `BLOCKED_TEMPORAL_CV`, `LEAVE_ONE_SUBJECT_OUT` (тест на отложенном человеке), `AUTHOR_REPORTED_PRECOMPUTED_OUTPUTS` (LME $R^2 = 0.9844$, LSTM $R^2 = 0.9882$) и `FULL_MODEL_RETRAINING`.
   - Масштабирование признаков выполняется строго внутри обучающих фолдов; модель M4 не использует информацию удержанного участника.
3. **Подтверждение коллапса UWB-радара и сьют чувствительности (Stage 3, NEG-0039)**:
   - Коллапс UWB Ridge LOSO подтверждён: $R^2 = -2.4457 \pm 2.2077$ (NRMSE $= 47.25\%$).
   - Сьют чувствительности (15 конфигураций) подтвердил отрицательный $R^2$ во всех вариантах (регуляризация $\alpha \in [10^{-3}, 10^3]$, StandardScaler, RobustScaler, частотные каналы S11/S21/Mag/Phase, активные условия).
4. **Фальсификация превосходства модели SUBJECT-01 M4 (Stage 4, NEG-0039)**:
   - M1 sEMG LOSO $R^2 = 0.4628 \pm 0.0651$, M3 Hill LOSO $R^2 = 0.3103 \pm 0.0819$, M4 SUBJECT-01 LOSO $R^2 = 0.3251 \pm 0.0946$.
   - Преимущество M4 над M3 ($+0.0148$) статистически недостоверно ($p = 0.3294$).
   - M4 **достоверно уступает простому sEMG-бейзлайну M1** ($\Delta R^2 = -0.1377$, $p = 0.0571$).
   - Статус M4 как «лучшей архитектуры» отвергнут (`NEG-0039`).
5. **Целостность реестров и инварианты (Stage 5)**:
   - `NEG-0038` сохранён строго о запрете экстраполяции на TARGET-CPE45.
   - `NEG-0039` создан для коллапса UWB и фальсификации M4.
   - Реестры: HYP=8, EXP=45, FND=45, NEG=39, DEC=20, ISS=20, SRC=76.
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Cycle 13 не начинался. Все 125 тестов пройдены.
