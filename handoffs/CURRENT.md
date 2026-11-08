# SUBJECT-01 — handoff Research Cycle 9 (Empirical Data Acquisition & Recruitment Observability)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
Cycle 9 база: 07ae4767d2e8ee1ec84e714514ba07c9ad35d2e0.
Ветка цикла: feature/cycle9-empirical-recruitment-acquisition.
Итоговый main SHA проверяется через GitHub после PR и merge.

Ключевые документы Cycle 9:
- research/empirical_recruitment_2026_11_08/REPORT.md (полный научный отчёт Cycle 9 с обязательной таблицей достоверности CLAIM / REAL MEASUREMENT / MODEL ASSUMPTION / VALIDATION STATUS и ответами на 7 вопросов)
- research/empirical_recruitment_2026_11_08/MATHEMATICS.md (биофизика рекрутирования 500 ДЕ по Ханнеману, объёмный проводник, фильтр SAT, 4 уровня идентифицируемости)
- research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md (физические измерительные карты для HD-sEMG, 31P-MRS, 3D MRI, NIRS)
- research/empirical_recruitment_2026_11_08/DATA_AUDIT.md (метрология и аудит новых источников SRC-0068..0072, префлайт-разграничение энтальпии/свободной энергии, понижение статуса покоя Andersen & Saltin 1985)
- research/empirical_recruitment_2026_11_08/LIMITATIONS.md (барьер межмышечного переноса, диссоциация sEMG/сила при утомлении, статус TARGET-CPE45 и NO_GO)
- research/empirical_recruitment_2026_11_08/README.md (инструкция по воспроизведению)
- research/empirical_recruitment_2026_11_08/biophysical_recruitment_model.py (биофизическая модель рекрутирования ДЕ и объемной фильтрации)
- research/empirical_recruitment_2026_11_08/identifiability_recruitment.py (расчёт 4-уровневой идентифицируемости и профильного правдоподобия)
- research/empirical_recruitment_2026_11_08/validation_loso.py (межсубъектная валидация Leave-One-Subject-Out)
- research/empirical_recruitment_2026_11_08/experiments.py (мастер-скрипт экспериментов EXP-0037..0041)
- research/empirical_recruitment_2026_11_08/test_empirical_recruitment.py (8 юнит-тестов регрессионной и научной достоверности)

Результаты Cycle 9:
1. Этап 0 (Preflight):
   - Термодинамика: разграничены свободная энергия Гиббса Delta_G_ATP = 54.0 кДж/моль (максимальная механическая работа) и калориметрическая энтальпия Delta_R H = 21.0 кДж/моль (тепловыделение). Отношение 2.5714 отражает энтропийный вклад.
   - Источник покоя: статус значений покоя (2.4 мл/100г/мин и 58 мл/л) в SRC-0066 понижен до DOWNGRADED_NOT_PRIMARY_RESTING_TABLE / LITERATURE_REVIEW_TRANSFER_ASSUMPTION (Таблица 2 Andersen & Saltin 1985 начинается с 10 Вт, строки 0 Вт нет).
2. Захват эмпирических данных (EXP-0037):
   - 64-канальная HD-sEMG (Hug et al. 2021, Figshare 10.6084/m9.figshare.13695937, SRC-0068): спайковые поезда ДЕ Gastrocnemius Medialis (9.8-19.8 Гц) и Lateralis (9.4-18.9 Гц) при 10-70% MVC, межэкспертная надёжность 99.6%.
   - Динамическая 31P-MRS квадрицепса (Rehman et al. 2024, PMC11617988, SRC-0069): 3 полных триала внутри томографа Siemens 3T на немагнитном эргометре (tau = 39.2 +- 2.5 с, pH = 7.01 +- 0.03).
   - Анатомическая томография (MuscleMap SRC-0070, Cenni SRC-0071): популяционные объёмы икроножной (342.5 мл), камбаловидной (580.4 мл) и четырёхглавой мышцы (2340 мл) с толщиной жирового слоя SAT (3-11 мм).
3. Биофизическая модель рекрутирования ДЕ (EXP-0038):
   - При фиксированном измеренном sEMG RMS = 12.7% вариация толщины жира SAT (3-10 мм) создаёт 40.9-кратный диапазон неопределённости истинной доли активной ткани a_eff (0.018-0.737).
   - При утомлении замедление скорости проведения возбуждения увеличивает sEMG RMS на +14.0% при падении механической силы на -35.0% (диссоциация sEMG/сила). Одиночная sEMG RMS структурно не идентифицирует a_eff.
4. 4-уровневая идентифицируемость (EXP-0039):
   - Уровень 1 (структурный ранг P8 = 7/7); Уровень 2 (локальный ранг при неизвестном a_eff дефектен); Уровень 3 (с 12 мешающими параметрами эффективный ранг 5/12, дефект = 7, плоский хребет profile likelihood); Уровень 4 (NOT_EMPIRICALLY_IDENTIFIED_CROSS_STUDY_DISCONNECTION из-за отсутствия синхронных мультимодальных измерений на одном субъекте).
5. Независимая межсубъектная валидация (EXP-0040):
   - Cross-muscle перенос кинетики между икроножной мышцей (Franke, tau = 24.3 с) и четырёхглавой мышцей (Rehman, tau = 39.2 с) деградирует RMSE прогноза на +53.9% (Fold 1) и +189.3% (Fold 2), с общим ростом ошибки с 0.691 мМ до 1.631 мМ.
6. Интеграция в SUBJECT-01 и TARGET-CPE45 (EXP-0041):
   - Пул фосфокреатина икроножной мышцы (0.62 кДж) составляет 0.092% от бюджета 2700-секундного теста критической мощности при 250 Вт (675 кДж), а квадрицепса — 0.629%. Локальный фосфаген лимитирует только ультракороткие разгоны (0-30 с); тест на 99.3% обеспечивается системным кислородным потоком. Перенос модели на всё тело заблокирован.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=31, DEC=15, ISS=19, SRC=72.
- Тесты: 170/170 PASS (все тестовые наборы репозитория).
