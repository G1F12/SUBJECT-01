# SUBJECT-01 — handoff: Cycle 12 Human Muscle Force, Fatigue & Biomechanical Empirical Validation (EXP-0045)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 64668170f2eece8e96fad6349a92ab5175725e4d (origin/main).
Ветка: feature/cycle12-bird-raw-empirical-validation.

Ключевые документы и инструменты:
- research/muscle_force_biomechanics_2026_11_10/BIOMECHANICAL_VALIDATION_REPORT.md (мастер-отчёт биомеханической валидации силы мышц и утомления Bird et al. 2026)
- research/muscle_force_biomechanics_2026_11_10/biomechanics_validation_results.json (канонический JSON валидации биомеханики Bird 2026, EXP-0045)
- research/muscle_force_biomechanics_2026_11_10/bird2026_empirical_validation.json (канонический JSON независимой эмпирической валидации и LOSO по сырым массивам)
- research/muscle_force_biomechanics_2026_11_10/observed_variables_registry.json (реестр онтологии наблюдаемых и расчётных переменных)
- research/muscle_force_biomechanics_2026_11_10/empirical_datasets_cycle12.json (реестр эмпирических датасетов Cycle 12)
- research/muscle_force_biomechanics_2026_11_10/sources.json (реестр источников Cycle 12, SRC-0076)
- tools/process_bird_raw_data.py (пайплайн верификации SHA-256, воспроизведения авторских моделей и расчёта LOSO)
- tools/generate_biomechanics_report_tables.py (генератор структурных таблиц Markdown из JSON для биомеханики)
- tools/evaluate_bird_biomechanics.py (движок сократительной биомеханики, декуплинга, утомления, 4-уровневой таксономии и аудита ограничений)
- tests/test_bird_biomechanics_validation.py (20 юнит-тестов биомеханики: криптография SHA-256, таксономия, ограничения, воспроизведение LME/LSTM, коллапс радара в LOSO, 4 негативных теста)
- registry/experiments.json (EXP-0045: статус completed_empirical_raw_data_and_loso_evaluated)
- registry/findings.json (FND-0045: эмпирический декуплинг, воспроизведение авторских моделей, коллапс обобщения UWB радара в LOSO R2=-2.45)
- registry/negative_results.json (NEG-0038: коллапс межсубъектного обобщения UWB-радара без индивидуальной калибровки, запрет экстраполяции момента одного сустава на выносливость TARGET-CPE45)
- registry/decisions.json (DEC-0020: утверждение онтологии, 4-уровневой таксономии, аудита физических ограничений и приоритизации архитектур аугментации)
- tools/verify_data_provenance.py / tools/validate_repository.py (сквозные валидаторы целостности реестров)

Результаты этапов (Cycle 12 Эмпирическая валидация сырых данных):
1. **Криптографическая верификация сырых файлов (Dryad API v2)**:
   - Получены и проверены 4 приоритетных файла Dryad:
     * `DATA_Isometric_Knee.xlsx` (19 879 байт, SHA-256 `1c415188ba7008586d05e5c4f0a0794c2858fe63e8a4f176d4b653630a7ac37f`) — `ACQUIRED_AND_VERIFIED`.
     * `LME_Data_Outputs.mat` (40 628 байт, SHA-256 `f532559ce51352342503d776821b13cf78cee81e52d6ba8f2ac48860642199b7`) — `ACQUIRED_AND_VERIFIED`.
     * `DATA_Dynamic_Knee.mat` (5 212 093 байт, SHA-256 `7cb256a8eadf621b9822266c473b620b8121e40fb62ed7615cdfbb32024da7f9`) — `ACQUIRED_AND_VERIFIED`.
     * `LSTM_Data_Outputs.zip` (8 939 260 байт, SHA-256 `863307becd150259a2bdeb685eceee2be65e5c24d206cceebb4162d7e7e471f0`) — `ACQUIRED_AND_VERIFIED`.
   - В `.gitignore` добавлены правила исключения бинарных архивов `raw_data/*.xlsx`, `raw_data/*.mat`, `raw_data/*.zip` для предотвращения несанкционированной публикации сырых данных.
2. **Независимое воспроизведение авторских моделей Bird 2026**:
   - `LME_Data_Outputs.mat`: средний $R^2 = 0.9844 \pm 0.0046$, NRMSE $= 3.28 \pm 0.58\%$ (в точности совпадает с опубликованными $R^2 = 0.984 \pm 0.005$, NRMSE $= 3.3\%$).
   - `LSTM_Data_Outputs.zip`: средний $R^2 = 0.9882 \pm 0.0059$, RMSE $= 2.74 \pm 0.67\%$ (в точности совпадает с опубликованными $R^2 = 0.988 \pm 0.005$, NRMSE $= 2.7\%$).
   - `DATA_Dynamic_Knee.mat` (активные условия, 1 821 точка): декуплинг момента от статических прокси подтверждён:
     * Момент vs sEMG: $R^2 = 0.1180$ (в публикации: 0.13)
     * Момент vs деформация пучков: $R^2 = 0.0161$ (в публикации: 0.01)
     * Момент vs скорость деформации: $R^2 = 0.0270$ (в публикации: 0.03)
3. **Межсубъектная валидация Leave-One-Subject-Out (LOSO) и обнаружение коллапса радара**:
   - Авторский сплит intra-participant 5-fold CV (с перемежением каждой 5-й точки непрерывного временного ряда 10 Гц) даёт искусственно завышенный $R^2 = 0.9763 \pm 0.0097$ (NRMSE $= 4.19\%$).
   - При строгой межсубъектной валидации **Leave-One-Subject-Out (LOSO across N=6)** модель UWB-радара **полностью коллапсирует**:
     * Средний LOSO $R^2 = -2.4457 \pm 2.0154$, NRMSE $= 47.25\%$ (на 5 из 6 участников $R^2 < 0$).
     * Причина: сырые радиочастотные сигналы радара (204 канала) запоминают индивидуальный диэлектрический импеданс тканей, толщину подкожного жира и геометрию контакта антенны конкретного человека, не обладая инвариантным физиологическим переносом.
   - Физиологические модели сохраняют устойчивое межсубъектное обобщение:
     * Модель M1 sEMG: LOSO $R^2 = 0.4628 \pm 0.0594$, NRMSE $= 19.50\%$.
     * Модель M3 Hill: LOSO $R^2 = 0.3103 \pm 0.0748$, NRMSE $= 22.19\%$.
     * Модель M4 SUBJECT-01: LOSO $R^2 = 0.3251 \pm 0.0863$, NRMSE $= 21.93\%$.
4. **Эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=45, FND=45, NEG=38, DEC=20, ISS=20, SRC=76.
   - Cycle 13 не начинался.
