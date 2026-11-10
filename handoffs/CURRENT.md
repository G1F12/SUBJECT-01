# SUBJECT-01 — handoff: Cycle 12 Human Muscle Force, Fatigue & Biomechanical Validation (EXP-0045)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 9911e1e476138fb339510be0e21a7d7e0ff55a33.
Ветка: feature/cycle12-human-muscle-force-and-fatigue (слияние в main).

Ключевые документы и инструменты:
- research/muscle_force_biomechanics_2026_11_10/BIOMECHANICAL_VALIDATION_REPORT.md (мастер-отчёт биомеханической валидации силы мышц и утомления Bird et al. 2026)
- research/muscle_force_biomechanics_2026_11_10/biomechanics_validation_results.json (канонический JSON валидации биомеханики Bird 2026, EXP-0045)
- research/muscle_force_biomechanics_2026_11_10/observed_variables_registry.json (реестр онтологии наблюдаемых и расчётных переменных)
- research/muscle_force_biomechanics_2026_11_10/empirical_datasets_cycle12.json (реестр эмпирических датасетов Cycle 12)
- research/muscle_force_biomechanics_2026_11_10/sources.json (реестр источников Cycle 12, SRC-0076)
- tools/generate_biomechanics_report_tables.py (генератор структурных таблиц Markdown из JSON для биомеханики)
- tools/evaluate_bird_biomechanics.py (движок сократительной биомеханики, декуплинга, утомления и мультимасштабного моста)
- tests/test_bird_biomechanics_validation.py (13 юнит-тестов биомеханики: криптография SHA-256, когорты, декуплинг, иерархия моделей, утомление, 4 негативных теста)
- tools/evaluate_malaga_treadmill.py (движок Malaga с агрегацией по 846 участникам и кластерным бутстрепом)
- research/treadmill_cpet_2026_11_09/malaga_validation_results.json (канонический JSON Malaga с участник-уровневой статистикой)
- tests/test_malaga_cpet_validation.py (20 юнит-тестов Malaga, включая контроль псевдорепликации df)
- registry/experiments.json (EXP-0045: валидация биомеханики мышц и утомления)
- registry/findings.json (FND-0045: динамический декуплинг и нейромышечная компенсация +26%)
- registry/negative_results.json (NEG-0038: запрет экстраполяции момента одного сустава на выносливость TARGET-CPE45)
- registry/decisions.json (DEC-0020: утверждение онтологии и приоритизация архитектур аугментации)
- tools/verify_data_provenance.py / tools/validate_repository.py (сквозные валидаторы целостности реестров)

Результаты этапов (Cycle 12 Human Muscle Force, Fatigue & Biomechanical Validation):
1. **Закрытие остаточного статистического аудита Cycle 11 (Stage 0, EXP-0044)**:
   - Ликвидирована псевдорепликация в t-тестах: агрегация переведена на 846 участников ($df=845$). Превосходство M4 подтверждено ($p = 2.41 \times 10^{-22}$).
   - Кластерный бутстреп подтвердил $\Delta\text{RMSE}(\text{M4}-\text{M3}) = -66.0$ мл/мин (95% ДИ $[-75.5, -56.3]$).
   - Раздельно вычислены participant-weighted и test-weighted метрики (RMSE $= 404.0$ мл/мин, $R^2 = 0.665$).
   - Добавлены 4 теста, проверяющие корректность степеней свободы. Референс $\tau=35$ с и `ISS-0020` сохранены.
2. **Первоисточник Bird et al. 2026 (Stage 1, SRC-0076)**:
   - Dryad DOI `10.5061/dryad.sbcc2frmh`, Science Robotics DOI `10.1126/scirobotics.aed5865`, arXiv:2510.20866.
   - Извлечены официальные SHA-256 для 13 файлов архива из API. Защита Anubis BotStopper / OAuth не обходилась.
   - Полный препринт манускрипта получен из arXiv (5.5 МБ, SHA-256 проверен).
3. **Онтология переменных (Stage 2)**:
   - Разграничены измеренные переменные (момент, угол, скорость, sEMG, УЗИ пучков, радар), расчётные (плечо силы, нормализованное напряжение, MVC) и ненаблюдаемые (сила отдельной мышцы, фосфаты, pH, импульсация ДЕ).
   - Инвариант: суставной момент динамометра не равен силе отдельной мышцы квадрицепса.
4. **Биомеханика сокращения и декуплинг (Stage 3, NEG-0038)**:
   - Подтверждён декуплинг момента от статических прокси в динамике ($R^2 < 0.25$ против sEMG, деформации пучков и скорости деформации).
   - Динамические модели: M4 SUBJECT-01 ($R^2 = 0.748 \pm 0.062$, NRMSE $= 8.9\%$) и M3 Hill ($R^2 = 0.612 \pm 0.084$) превосходят M1 ($R^2 = 0.185$) и M0 ($R^2 = -0.452$).
   - Для $N=6$ зафиксирован широкий 95% ДИ ($[0.68, 0.81]$).
5. **Динамика утомления (Stage 4, FND-0045)**:
   - 20-минутный тест ($N=18$) выявил рост sEMG-активации на $+26 \pm 15\%$ ($p = 0.0008$, 17 утомлены, 1 резистентен).
   - Биофизическая модель утомления M2 ($R^2 = 0.812$, RMSE $= 5.9\%$) превосходит линейный дрейф M1 ($R^2 = 0.654$) и M0 ($R^2 = -0.842$).
   - sEMG-дрейф не является прямым измерением фосфатов и не валидирует `TARGET-CPE45`.
6. **Мультимасштабный мост (Stage 5)**:
   - Установлено концептуальное отображение: Rehman (MRS) $\leftrightarrow$ Bird (механика) $\leftrightarrow$ ACTES/Malaga (системная вентиляция).
7. **Архитектуры аугментации (Stage 6, DEC-0020)**:
   - Архитектура A (биологическая) приоритизирована с барьерами метаболизма массы и прочности связок.
   - Архитектуры B и C заблокированы барьерами иннервации, фиксации к кости, перфузии и пространства.
8. **Эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=45, FND=45, NEG=38, DEC=20, ISS=20, SRC=76.
