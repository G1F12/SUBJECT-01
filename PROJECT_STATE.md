# SUBJECT-01 — состояние после EXP-0042 Final Numerical Lock & Cycle 10 Multi-Subject CPET Validation (EXP-0043), 09.11.2026

База: 7ee8c127dad2a56bef4427c8e9e5777bdc385b8c;
Ветка: feature/exp-0042-lock-and-cycle10-data-acquisition (слияние в main).

Ключевые артефакты Cycle 10:
- [Отчёт по валидации CPET PhysioNet ACTES (N=18)](research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md),
- [Канонический JSON валидации ACTES (EXP-0043)](research/cpet_cycloergometer_2026_11_09/actes_validation_results.json),
- [Систематический рейтинг и аудит датасетов](research/cpet_cycloergometer_2026_11_09/DATASET_RANKING.md),
- [Матрица остаточных барьеров и неидентифицируемости M3](research/cpet_cycloergometer_2026_11_09/REMAINING_BARRIERS_MATRIX.md),
- [Движок мультисубъектной валидации CPET](tools/evaluate_actes_models.py),
- [Тесты валидации ACTES CPET](tests/test_actes_cpet_validation.py),
- [Реестр эмпирических датасетов Cycle 10](research/cpet_cycloergometer_2026_11_09/empirical_datasets_cycle10.json),
- [Канонический отчёт валидации Rehman 2024 (EXP-0042 Locked)](research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md),
- [Канонический JSON валидации Rehman (EXP-0042 Locked)](research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json),
- [Генератор структурных таблиц Rehman](tools/generate_rehman_report_tables.py),
- [Сквозной аудит Evidence Gate V2](tools/verify_data_provenance.py).

Главные итоги:
1. **EXP-0042 Final Numerical Lock**:
   - Канонические значения базового PCr зафиксированы: Trial 1 = $2481.43 \pm 74.26$, Trial 2 = $1679.00 \pm 38.71$, Trial 3 = $1675.57 \pm 34.21$.
   - Канонические значения M2 $k$: Trial 1 = $1.2979\text{ мин}^{-1}$, Trial 2 = $1.1469\text{ мин}^{-1}$, Trial 3 = $0.9696\text{ мин}^{-1}$.
   - Примитивный `assertIn` заменён глубоким структурным парсером Markdown $\leftrightarrow$ JSON с 3 негативными тестами на перестановку строк, подмену метрик и посторонние цифры в тексте.
   - Статус: `EXP-0042_NUMERICALLY_LOCKED`.
2. **Cycle 10 Data Acquisition (PhysioNet ACTES Cycloergometer, SRC-0073)**:
   - Преодолён барьер единичного субъекта ($N=1$): получен датасет из $N = 18$ независимых спортсменов-подростков (фехтование, гребля на байдарках, триатлон).
   - 52,062 синхронизированных beat-to-beat наблюдений механической мощности ($P_{\text{mech}}$ в Вт), потребления кислорода ($\dot{V}\text{O}_2$ в л/мин) и кардиоинтервалов ($RR$ в мс).
   - Полное байтовое совпадение SHA256: `test_measure.csv` (`14a9df02...`), `subject-info.csv` (`5ac7cdd4...`), `LICENSE.txt` (`86c0ad30...`). Лицензия ODC-By v1.0.
3. **Первая независимая мультисубъектная верификация (EXP-0043)**:
   - Проведён строгий Leave-One-Subject-Out (LOSO) кросс-валидационный тест на всех 18 участниках без утечки таргета.
   - Динамическая биоэнергетическая ОДУ с аллометрическим масштабированием по массе тела ($P/M \to \dot{V}\text{O}_2/M$) показала кросс-субъектный $R^2_{\text{LOSO}} = 0.7371 \pm 0.1770$ (RMSE $= 0.290 \pm 0.059\text{ л/мин}$), значительно превосходя эмпирическую статическую линейную M1 ($R^2 = 0.4045$, RMSE $= 0.416\text{ л/мин}$) и константную M0 ($R^2 = -0.8343$, RMSE $= 0.773\text{ л/мин}$).
4. **Матрица остаточных барьеров (`REMAINING_BARRIERS_MATRIX`)**:
   - Валидация макроскопического аэробного сопряжения ($\dot{E}_{\text{met}} = P_{\text{mech}} / \eta$) НЕ означает валидацию внутриклеточных микросостояний ([PCr], [Pi], [ATP], pH) и рекрутирования двигательных единиц.
   - В силу проблемы «многие-к-одному» (entanglement fallacy), системный $\dot{V}\text{O}_2$ не идентифицирует компартментные профили.
5. **Незыблемые эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`** (15-минутный ступенчатый тест до отказа не валидирует 45-минутный экстремальный стресс).
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=43, FND=43, NEG=36, DEC=17, ISS=19, SRC=73.
   - Тесты: 74/74 PASS (включая 13 тестов Rehman и 7 тестов ACTES CPET), Evidence Gate V2 (8/8 негативных проверок).

---

# SUBJECT-01 — состояние после EXP-0042 Scientific Corrigendum & Model Integrity, 09.11.2026

База b98c3eb68654dc8f22ce1dd64be70c3b45528623;
ветка fix/exp-0042-scientific-corrigendum (слияние в main).
[Научный отчёт по валидации и заморозке реальных данных (Corrigendum)](research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md),
[канонический артефакт валидации](research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json),
[движок валидации моделей Rehman](tools/evaluate_rehman_models.py),
[тесты валидации моделей Rehman](tests/test_rehman_model_validation.py),
[Отчёт EXP-0037..0042](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[извлечённый канонический временной ряд Rehman 2024](research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Завершён научный корригендум EXP-0042, устранивший несоответствия между отчётами и каноническим JSON:
1. **Числовая сверка отчёта и JSON**: проверенные амплитуды PCr на 90 с: T1=1920.0, T2=1291.0, T3=1277.0; в надире: T1=1670.0 (144 с), T2=1245.0 (108 с), T3=1231.0 (108 с). Фактические in-sample RMSE: M0=(230.88, 120.21, 141.69); M1=(26.05, 15.73, 14.70); M2=(31.72, 37.67, 32.80). Для M0 $R^2$ строго отрицательный (-0.553, -1.130, -0.962). Добавлен автоматический тест `test_report_markdown_json_consistency`.
2. **Аудит тайминга и физиологических меток**: номинальные $t_{\text{start}}=48\text{ с}$ и $t_{\text{stop}}=90\text{ с}$ классифицированы как `INFERRED_TIMING_ASSUMPTION` (аудиокоманды оператора, отсутствие аппаратного TTL). Надир классифицирован как `OBSERVED_SPECTRAL_MINIMUM_DISTINCT_FROM_MECHANICAL_STOP`. Термины «ишемический/гиперемический лаг» исключены из категорических выводов при отсутствии данных плетизмографии/кровотока.
3. **Ретракция утверждения о pH**: утверждение «$\text{pH} \ge 6.86$ во всех триалах» официально отозвано как устаревшее; фактический минимум pH составляет 6.7932 в триале 1 (диапазон расчётного pH: $6.7932\dots 7.0228$). Статус `PH_CALIBRATION_PARTIAL` сохранён без искусственных поправок. Категорические утверждения о нулевом протонном ингибировании без анализа газов крови и лактата запрещены.
4. **Реклассификация модели M2 и статус M3**: M2 реклассифицирована в `CONSTRAINED_MONOEXPONENTIAL_BASELINE` ($d\text{PCr}/dt = k \cdot (\text{PCr}_{\text{rest}} - \text{PCr})$). Запрещены утверждения о валидации баланса энергий, кислородного транспорта или двигательных единиц на M2. Полная физиологическая модель M3 получила статус `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS` из-за отсутствия механической мощности, момента силы, объёма мышцы и спирометрии в Rehman 2024.
5. **Разграничение режимов переноса**: Сценарий A (`CONDITIONAL_TRAJECTORY_RECONSTRUCTION`, при известных надире и базовом уровне) подтверждён (M2 средний переносный $R^2 = 0.8566$, M1 — $0.8268$). Сценарий B (`PROSPECTIVE_PREDICTION`, прогноз от 90 с без знания будущего надира и динамики истощения) строго заблокирован: `PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS`.
6. **Кросс-субъектный LOSO**: на $N=1$ строго запрещён (`LosoProhibitedError`).

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=42, FND=42, NEG=35, DEC=16, ISS=19, SRC=72.
- Тесты: 207/207 PASS (включая 10 тестов валидации моделей Rehman).

---

# SUBJECT-01 — состояние после Rehman 2024 Real XLSX Format Hotfix, 09.11.2026

База 5f2846cbf025efe7a747dbcf6a2355dedabcb5b6;
ветка fix/rehman-real-xlsx-format-hotfix.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[модуль OOXML stdlib](tools/rehman_ooxml.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[извлечённый канонический временной ряд Rehman 2024](research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Адаптация процессора к реальному формату Dryad XLSX и извлечение временных рядов:
- Файл `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18,136 байт, SHA256 `ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`) получен по owner-assisted протоколу.
- Реализован разбор структуры листа `2024_829_DiB_Raw` с 18 колонками, сгруппированными тремя блоками по 6 колонок (`1.*`, `2.*`, `3.*`).
- Извлечены 222 спектра (3 триала по 74 валидные точки с шагом 6.0 с, диапазон 12.0–450.0 с; предскановый спектр 1 исключён).
- Фит кинетики восстановления фосфокреатина:
  * Trial 1: $k = 1.393 \pm 0.119\text{ мин}^{-1}$ (опубликовано $1.43$, расхождение $-2.57\%$), $\tau = 43.07\text{ с}$, $R^2 = 0.9802$, RMSE = $26.05$, надир в спектре 24 ($144\text{ с}$).
  * Trial 2: $k = 1.686 \pm 0.180\text{ мин}^{-1}$ (опубликовано $1.62$, расхождение $+4.09\%$), $\tau = 35.58\text{ с}$, $R^2 = 0.9635$, RMSE = $15.73$, надир в спектре 18 ($108\text{ с}$).
  * Trial 3: $k = 1.480 \pm 0.121\text{ мин}^{-1}$ (опубликовано $1.53$, расхождение $-3.24\%$), $\tau = 40.53\text{ с}$, $R^2 = 0.9789$, RMSE = $14.70$, надир в спектре 18 ($108\text{ с}$).
  * Среднее: $k = 1.520 \pm 0.151\text{ мин}^{-1}$ (опубликовано $1.53 \pm 0.10\text{ мин}^{-1}$, расхождение $-0.65\%$), $\tau = 39.72\text{ с}$, CV% = $9.90\%$ (опубликованная ошибка: $\pm 6.5\%$).
- Внутриклеточный pH рассчитан из химических сдвигов ($\delta_o = \delta_{\text{Pi}} - \delta_{\text{PCr}}$) по уравнению PMC11617988 Fig. 7 без искусственных констант (покой $6.91\dots 6.96$, конец нагрузки $6.92\dots 6.98$, конец восстановления $6.86\dots 6.93$).
- Канонический артефакт извлечения `rehman2024_extracted_timeseries.json` сохранён в репозитории (SHA256: `af6a396b006a6cb791844742085701c6782b4eb706a8f768b1bd87dfa7e8de5b`, 41,368 байт). Бинарный XLSX файл оставлен в `.gitignore` до разрешения лицензии.
- Батарея тестов `tests/test_rehman_xlsx_processor.py` расширена до 17 тестов (100% PASS).
- Кросс-субъектный LOSO на когорте $N=1$ строго запрещён.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 197/197 PASS (все тестовые наборы репозитория, включая 17 тестов процессора Rehman и 12 тестов Evidence Gate V2).

---

# SUBJECT-01 — состояние после Research Cycle 9 (CI Failure, Strict JSON & Real-Data Pipeline Repair), 09.11.2026

База 19402484b0295c46ae03d5dab47a363f89cf5795;
ветка fix/ci-failure-and-real-data-pipeline-repair.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[модуль OOXML stdlib](tools/rehman_ooxml.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Ремонт CI, байтового происхождения, строгого JSON и процессора первичных данных:
- CI Failure & Byte Provenance Repair (GitHub Actions run 42654714327):
  * Выявлена первопричина падения шага `Structural and hash audit`: расхождение окончаний строк CRLF на Windows и LF в Git/Linux из-за отсутствия конфигурации `.gitattributes` для Циклов 7, 8, 9, `registry/`, `tools/`, `tests/`.
  * `.gitattributes` дополнен правилом `* text eol=lf` для всех репозиторных текстовых файлов с сохранением binary-маркировки (`-text`) для исторических CSV Foundation.
  * Файлы приведены к каноническим байтам:
    - Franke 2020 JSON: 3049 байт (LF), SHA256 `0345c4a8b36c95d9641c52bc96b759a43e6f899d186159606481060fbb437fa2`, классифицирован как `DERIVED_EXTRACTION_JSON` (извлечённые координаты 3D МРТ-сегментации, а не сырой MAT-файл).
    - Rehman 2024 XML: 42824 байта (LF), SHA256 `d8f1df9664c94b4846da3c015ced45310bc17ea1f48b58ce287c61db6bd1ed2c`, классифицирован как `PUBLISHED_TABLE_DATA`.

- Завершение процессора сырых данных Rehman 2024 (`tools/process_rehman_xlsx.py`):
  * Разработан легковесный OOXML-модуль `tools/rehman_ooxml.py` на базе `zipfile` и `xml.etree.ElementTree` (zero external dependencies, независим от отсутствующего `openpyxl`).
  * При отсутствии оригинального файла возвращает `PENDING_RAW_DATA` (без ложного PASS).
  * При наличии файла выполняет: проверку байтового SHA256 (`ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`), разбор структуры листов и колонок, извлечение 3 триалов по 75 спектральных точек (разрешение 6 с), моноэкспоненциальный фит кинетики PCr и Pi с 95% доверительными интервалами, сравнение с опубликованными Table 1 константами $k = 1.43, 1.62, 1.53\text{ мин}^{-1}$, оценку внутрисубъектной воспроизводимости (repeatability CV%) и строгий запрет кросс-субъектного LOSO при $N=1$.
  * Создан полный тестовый набор `tests/test_rehman_xlsx_processor.py` (8 тестов, включая негативные проверки на пустую книгу, повреждённые колонки, неверный хеш и неполные триалы). Тест добавлен в `.github/workflows/validate.yml`.

- Модернизация Evidence Gate V2 (`tools/verify_data_provenance.py`):
  * Установлено правило сквозной верификации байтового хеша: если запись ссылается на локальный файл и указывает SHA256, байтовый хеш проверяется независимо от категории данных.
  * Введены типизированные категории: `ORIGINAL_BINARY_FILE`, `DERIVED_EXTRACTION_JSON`, `PUBLISHED_TABLE_DATA`, `LITERATURE_REFERENCE_WITHOUT_FILE`, `SYNTHETIC_MODEL_SIMULATION`.
  * Реализован глобальный аудит на соответствие RFC 8259: токены `Infinity`, `-Infinity` и `NaN` устранены во всех JSON-файлах репозитория (неопределённые числа обусловленности заменены на `null` со статусом `"INFINITE"`).
  * Отрицательная батарея тестов расширена до 7 проверок (добавлены подмена хеша в `PUBLISHED_TABLE_DATA` и обнаружение невалидных токенов JSON).

- Уточнение статуса научных утверждений TARGET-CPE45:
  * Значения 3300 кДж окислительного ресинтеза и 75 кДж гликолитического вклада строго задокументированы как `ESTIMATED_SCENARIO_BALANCE_NOT_MEASURED` (сценарный расчёт при допущении $\eta_{\text{gross}} = 20\%$, а не эмпирическое измерение в CPE45).
  * Аэробная фракция зафиксирована как `measured_empirical_aerobic_fraction: null`, статус: `NOT_EMPIRICALLY_MEASURED_IN_CPE45`.
  * Статус `TARGET-CPE45` неизменен: `NOT EXTERNALLY VALIDATED`, биологические вмешательства — `NO_GO`.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 188/188 PASS (все тестовые наборы репозитория, включая 8 тестов процессора Rehman и 12 тестов Evidence Gate V2).

---

# SUBJECT-01 — состояние после Research Cycle 9 (Data Integrity Repair & Evidence Gate Installation), 08.11.2026

База 9271a1eabbd8405f7152c151c52047ce54312c38;
ветка correction/cycle9-raw-data-integrity-gate.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[постоянный гейт данных](tools/verify_data_provenance.py),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Устранение синтетической валидации, аудит первичных данных и установка Evidence Gates:
- Этап 0 (Preflight): строго разграничены свободная энергия Гиббса Delta_G_ATP = 54.0 кДж/моль (максимальная механическая работа мостиков) и калориметрическая энтальпия Delta_R H = 21.0 кДж/моль (тепловыделение). Отношение 2.5714 отражает энтропийный вклад. Статус значений покоя (2.4 мл/100г/мин и 58 мл/л) в SRC-0066 понижен до DOWNGRADED_NOT_PRIMARY_RESTING_TABLE / LITERATURE_REVIEW_TRANSFER_ASSUMPTION (Таблица 2 Andersen & Saltin 1985 начинается с 10 Вт, строки 0 Вт нет).
- Аудит первичных данных человека (EXP-0037):
  1) Матричная HD-sEMG (Hug et al. 2021, Figshare 10.6084/m9.figshare.13695937, SRC-0068): литературные агрегаты частот разряда ДЕ по 8 операторам (9.8-19.8 Гц) для 1 испытуемого (8 операторов != 8 испытуемых). Программная загрузка архива 444 МБ заблокирована Cloudflare R2 (HTTP 403 Forbidden).
  2) Динамическая 31P-MRS квадрицепса (Rehman et al. 2024, PMC11617988, SRC-0069): опубликованы 3 скалярные кинетические константы в Таблице 1 (tau = 39.2 +- 2.5 с, pH = 7.01 +- 0.03). Программная загрузка спектрального файла 2024_829_Ergometer_Dryad_Raw_V3.xlsx заблокирована AWS WAF бот-челленджем (HTTP 403 Forbidden). Статус: RAW_TIMESERIES_UNAVAILABLE. Синтетических заменителей не создавалось.
  3) Томография: когортные таблицы SRC-0070 (MuscleMap) и SRC-0071 (Cenni) отозваны; статус EMPIRICALLY_BOUNDED_DISTRIBUTION аннулирован. Верифицирован первичный объём GM Subject 01 Franke 2020 (379.89 мл).
- Биофизическая модель рекрутирования (EXP-0038): статус COMPUTATIONAL_SIMULATION_HYPOTHESIS. Сценарные параметры (500 ДЕ, -35% силы) строго отделены от модельных следствий (+14% sEMG RMS при утомлении, 40.9x диапазон чувствительности a_eff к жировому слою 3-10 мм).
- 4-уровневая идентифицируемость (EXP-0039): Уровень 1 (структурный ранг P8 = 7/7); Уровень 2 (локальный ранг дефектен); Уровень 3 (с 12 мешающими параметрами эффективный ранг 5/12, дефект = 7); Уровень 4 (NOT_EMPIRICALLY_IDENTIFIED_CROSS_STUDY_DISCONNECTION).
- Ликвидация фейковой валидации LOSO (EXP-0040): отозвана эмпирическая валидация человека, так как кривые генерировались через np.random.RandomState. EXP-0040 и FND-0040 переведены в SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED, эмпирическая валидация переведена в BLOCKED_PENDING_RAW_DATA.
- Физический баланс энергии CPE45 (EXP-0041): строго разделены внешняя работа (250 Вт * 2700 с = 675 кДж), валовой метаболический расход (~3375 кДж при eta_gross ~20%), локальный буфер PCr (0.11-0.39 кДж в активном объёме голени; 0.62 кДж во всей GM) и тепловыделение (Delta_R H = 21.0 кДж/моль). Устранено бессмысленное прямое деление локального буфера на внешнюю работу. Экстраполяция на всё тело заблокирована.
- Постоянный гейт происхождения данных: внедрён tools/verify_data_provenance.py (проверка 11 обязательных полей, запрет EXTERNALLY_VALIDATED для синтетических данных, аудит скриптов на генерацию y_true). Интегрирован в tools/validate_repository.py.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=32, DEC=15, ISS=19, SRC=72.
- Тесты: 171/171 PASS (все тестовые наборы репозитория).

---

# SUBJECT-01 — состояние после Research Cycle 8 (Empirical Validity Correction), 08.11.2026

База 9bf0468754a756cca283fd41a84036b4d0c78cf3;
ветка correction/cycle8-validity-repair-20261108.
[Отчёт EXP-0032..0036](research/empirical_anchors_2026_11_08/REPORT.md),
[математика и физические отображения](research/empirical_anchors_2026_11_08/MATHEMATICS.md),
[модель измерений](research/empirical_anchors_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_anchors_2026_11_08/DATA_AUDIT.md),
[ограничения и протокол отзыва](research/empirical_anchors_2026_11_08/LIMITATIONS.md),
[reproduction](research/empirical_anchors_2026_11_08/README.md).

Эмпирические физиологические якоря и аудит научной достоверности:
- Первичные данные 3D T1-МРТ (Franke et al. 2020, PMC7332772, DOI 10.3389/fbioe.2020.00622): анатомический объём медиальной икроножной мышцы строго измерен и равен 379.89 мл (масса 0.3587 кг, PCSA 58.98 см2, F_max = 1474 Н).
- Экспериментальное разделение и аудит sEMG: МРТ, кинематика с sEMG (снаружи томографа при 2 кГц, интерполировано до 4 кГц в MAT) и 31P-MRS (внутри томографа) измерялись в отдельных сессиях. Доказано, что sEMG RMS=12.7% не измеряет долю активных волокон. Диапазон V_active in [83.6, 144.4] мл является сценарной гипотезой (SCENARIO_HYPOTHESIS). Подмена V_active анатомическим объёмом в рамках сценария занижает плотность потока АТФ в 2.63-4.55 раза.
- Когортное распределение фосфагенов покоя: Edwards et al. 2013 (PMC3560356, DOI 10.1038/srep01182, InSight trial, n=89; первый автор Edwards LM, а не Sleigh): PCr/gamma-ATP = 4.10 +/- 0.03. Принятие консенсуса [ATP]_ref in [6.5, 9.5] мМ (Meyerspeer et al. 2021, PMC8243949, DOI 10.1002/nbm.4246) даёт [PCr]_rest in [26.7, 39.0] мМ.
- Термодинамическая метрология: строго разграничены тепловая энтальпия реакции Delta_R H (21.0 кДж/моль, Kodama 1985) и свободная энергия Гиббса Delta_G_ATP (-54.0 кДж/моль). Множитель 2.5714 отражает отношение потенциалов, но не переводит автоматически тепло в мощность без аудита модели. Синхронизирована ёмкость буфера PCr: строго 111.4-947.0 Дж (8.50-кратный размах).
- Базовый расход покоя M_loc: значения 2.4 мл/100г/мин и (Ca - Cv)O2 = 58 мл/л измерены на четырёхглавой мышце бедра (Andersen & Saltin 1985, DOI 10.1113/jphysiol.1985.sp015794). Их перенос на икроножную мышцу реклассифицирован как MODEL_ASSUMED_QUADRICEPS_TRANSFER. Некалиброванные ASL (2.25x) и NIRS (6.67x) изолировать M_loc не способны.
- Физическая идентифицируемость (3 уровня): идеализированные скалярные каналы y = theta_j удалены. Уровень 1: условный математический полный ранг (P8 = 7/7, kappa_eff = 15.39 при замороженных константах). Уровень 2: при неизвестных nuisance-параметрах (a_eff, g_nirs, b_nirs, k_spec) 11D система имеет эффективный ранг 7/11 (дефект = 4) с плоскими хребтами. Уровень 3: на реальных человеческих данных модель NOT_EMPIRICALLY_IDENTIFIED из-за отсутствия синхронных мультимодальных записей.
- Изоляция макромодели D2: прямой перенос параметров отвергнут (отношение масс 50.2, отношение BMR 1543). 9D quotient модели D2 сохранён в неизменном виде.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: HYP=7, EXP=36, FND=37, NEG=28, DEC=14, ISS=19, SRC=67.
- Тесты: 162/162 PASS (все suites репозитория).

---

# SUBJECT-01 — состояние после Research Cycle 7 (Identifiability Repair & Final Consistency Audit), 08.11.2026

База c1e75ca293ad385efa25a74843431870dda162ad;
ветка correction/cycle7-identifiability-repair-20261108.
[Отчёт EXP-0027..0031](research/local_muscle_bridge_2026_11_07/REPORT.md),
[математика и симметрии](research/local_muscle_bridge_2026_11_07/MATHEMATICS.md),
[модель измерений](research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md),
[ограничения и протокол отзыва](research/local_muscle_bridge_2026_11_07/LIMITATIONS.md),
[reproduction](research/local_muscle_bridge_2026_11_07/README.md).

Ремонт модели идентифицируемости и согласование рангов:
- Устранено критическое несоответствие между математической документацией Cycle 7 (заявлявшей ранг 9/9 на девяти параметрах) и фактически вычисленными рангами: модель измерительного моста `LocalBridgeModel` параметризована 7 физиологическими параметрами ($\theta \in \mathbb{R}^7$), а не 9 эффективными параметрами макромодели D2 (Cycle 5).
- Механическая мощность $P_{\text{ext}}$ верифицирована как заданный вход эргометра ($\text{rank } M1 = 0/7$, так как $\partial P_{\text{ext}} / \partial \theta \equiv 0$).
- Устранён баг пропуска активного объёма в M6 (несовпадение ключа `_vol_` и `volume`) через переход на явные структуры каналов наблюдения `TOPOLOGY_CHANNELS`.
- Введена поблочная масштабная нормировка матрицы Якоби (dimensionless RMS sensitivity), устранившая численное подавление одиночных параметров ($M_{\text{loc}}$).
- Точные воспроизводимые ранги: M1 = 0/7, M2 = 3/7, M3 = 4/7, M4 = 3/7, M5 = 4/7, M6 = 5/7, M7 = 6/7. Ранг 6/7 в конфигурации M7 математически обусловлен неустранимой скалярной коллинеарностью $(\eta_{\text{loc}} \cdot \Delta G_{\text{ATP}})$ в механическом спросе АТФ.

Энергетическая метрология и термодинамика:
- Строго разграничены энергетические эквиваленты: $\Delta G_{\text{ATP}}$ ($-50 \dots -64$ кДж/моль, номинал $-54$ кДж/моль), $\Delta G_{\text{PCr}}$ ($-34 \dots -45$ кДж/моль) и креатинкиназное равновесие $\Delta G_{\text{CK}} = \Delta G_{\text{PCr}} - \Delta G_{\text{ATP}} \approx -10 \dots -15$ кДж/моль.
- Буферная ёмкость PCr: $204.8 \dots 1021.4$ Дж выражает доступный метаболический эквивалент через сопряжённую систему CK-ATPase ($|\Delta G_{\text{ATP}}| \in [50, 64]$ кДж/моль). При расчёте по чистому гидролизу PCr пул составляет $139 \dots 718$ Дж.
- Импульсное отношение работы 5 с к распаду PCr ($0.44 \dots 1.50$) классифицировано как диагностический артефакт неполного баланса и занижения активного объёма, а не нарушение закона сохранения энергии или КПД $> 100\%$.
- Зафиксирована мультимодальность калибровки: $V_{\text{active}}$ ($T_2^*$-МРТ, DCE-МРТ, УЗИ + HD-sEMG); $M_{\text{loc}}$ (катетеризация $(C_a - C_v)O_2$, ASL-МРТ, окклюзионный NIRS).
- Доказана структурная идентифицируемость задержки транспорта и постоянной времени ткани ($\kappa_{\text{FIM}} = 6.89$). Отрицательная корреляция $r = -0.709$ является фактором расширения доверительных интервалов под действием дыхательного шума.

Финальный аудит согласованности и устранение расхождений:
- Устранены числовые противоречия между отчётом и кодом: чувствительность асимптоты строго [-22.9%, +20.9%] (точно: -22.867%..+20.862%); смещение от гетерогенности волокон строго 10.6% (точно: 10.5996%); детерминированный сценарный диапазон паразитарных затрат строго 42.8%-77.1% (номинал 66.3%). Термин «доверительный интервал» исключён.
- Неверифицированные эмпирические заявления R2=0.919, R2=0.978 и наклон регрессии «14 с / 0.1 pH» ОТОЗВАНЫ как артефакты ручной графической оцифровки Fig 3-5. Восстановлены рецензированные литературные результаты Moll et al. 2017: R2=0.73 (p<0.005, n=10) для tau_PCr vs pH; R2=0.55 (p=0.01, n=10) для tau_VO2 vs tau_PCr; R2=0.65 (p<0.01, n=9) для excess CO2 vs pH.
- Изоляция исследований: данные Cannon et al. 2014 Table 1 (PMC4262339) получены на четырёхглавой мышце при bilateral knee extension (двустороннее разгибание коленей) и качественно доказывают преобладание окислительного ресинтеза (88-95%) над гидролизом PCr (1.5-3.0%); количественные скорости оборота (мМ/мин) не переносятся на икроножную мышцу когорты Moll без калибровки.
- EXP-0031 ОТОЗВАН: заявление о превосходстве локальной модели по RMSE 0.65 Вт аннулировано из-за захардкоженных прогнозов, in-sample константы и выборки N=2.
- Параметры D2 не объявляются идентифицированными через наблюдение коррелятов в мосту; математические тесты рангов не объявляются физиологической валидацией на людях.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=13, ISS=18, SRC=62.
- Тесты: 155/155 PASS (14 тестов Cycle 7 Local Muscle Bridge + все suites репозитория).

---

# SUBJECT-01 — состояние после Research Cycle 6, 04.11.2026

База a4d3a04ab8ef0fc056815989f4b775cf9773f3ca; ветка research/metabolic-anchors-20261104.
[Отчёт EXP-0023..0026](research/calibration_2026_11_04/REPORT.md),
[метрология](research/calibration_2026_11_04/DATA_AUDIT.md),
[reproduction](research/calibration_2026_11_04/README.md).

Получены реальные CPET VO2/VCO2/W:66cycling people Lendt, отдельный WEEE17VO2
и BUT-CGM1 exploratory person. CC BY4, native memberSHA, без публикации raw.
Независимый системный gas scale найден, localATPscale/localbaseline не найдены.
Условные systemic a153.853W,b3.64333W/W, effectiveδeff .274474 не равны D2M/η.
51development/216stages, published lock726772f; новые13test/56stages:
selectedquadratic RMSE26.56W vs constant135.40W vs historic equilibrium40.58W.
Ограниченная systemic-cost validation прошла; это не power/CPE45 validation.
9D quotient сохранён. Localparams не идентифицированы; pulmonaryτ30finite/51fits
только effective. Gain/offset/timing/volume остаются существенными.
Старые10+7 и новые13test просмотрены, повторное независимое claim запрещено.
TARGET-CPE45 NOT EXTERNALLY VALIDATED; interventions NO_GO; архитектуры без новых преимуществ.
Реестры EXP26/FND28/NEG20/DEC11/ISS17/SRC55. История Cycle5 ниже сохранена.
