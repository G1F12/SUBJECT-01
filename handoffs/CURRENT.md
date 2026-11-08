# SUBJECT-01 — handoff Research Cycle 9 (Data Integrity Repair & Evidence Gate Installation)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
Cycle 9 база: 9271a1eabbd8405f7152c151c52047ce54312c38.
Ветка цикла: correction/cycle9-raw-data-integrity-gate.
Итоговый main SHA проверяется через GitHub после PR и merge.

Ключевые документы Cycle 9:
- research/empirical_recruitment_2026_11_08/REPORT.md (полный научный отчёт Cycle 9 с обязательной таблицей достоверности CLAIM / REAL MEASUREMENT / MODEL ASSUMPTION / VALIDATION STATUS и ответами на 9 вопросов)
- research/empirical_recruitment_2026_11_08/MATHEMATICS.md (биофизика рекрутирования 500 ДЕ по Ханнеману, объёмный проводник, фильтр SAT, 4 уровня идентифицируемости)
- research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md (физические измерительные карты для HD-sEMG, 31P-MRS, 3D MRI, NIRS)
- research/empirical_recruitment_2026_11_08/DATA_AUDIT.md (метрология и аудит источников SRC-0068..0072, фиксация HTTP 403 WAF/CDN блокировок Dryad и Figshare, ретракция фейкового LOSO)
- research/empirical_recruitment_2026_11_08/LIMITATIONS.md (барьер доступности первичных данных, физический баланс CPE45, статус TARGET-CPE45 и NO_GO)
- tools/verify_data_provenance.py (постоянный автоматический гейт происхождения данных)
- research/empirical_recruitment_2026_11_08/biophysical_recruitment_model.py (биофизическая модель рекрутирования ДЕ)
- research/empirical_recruitment_2026_11_08/validation_loso.py (синтетическая алгоритмическая демонстрация LOSO)
- research/empirical_recruitment_2026_11_08/experiments.py (мастер-скрипт экспериментов EXP-0037..0041)
- research/empirical_recruitment_2026_11_08/test_empirical_recruitment.py (9 юнит-тестов регрессионной и научной достоверности)

Результаты Cycle 9 Integrity Repair:
1. Ликвидация фейковой валидации LOSO (EXP-0040):
   - Устранена выдача искусственных экспоненциальных рядов из np.random.RandomState за реальные измерения человека. Прежние заявления об эмпирической валидации отозваны.
   - EXP-0040 и FND-0040 реклассифицированы в SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED, эмпирическая валидация переведена в BLOCKED_PENDING_RAW_DATA.
2. Аудит доступности первичных данных (EXP-0037):
   - Rehman et al. 2024: 3 опубликованные константы в Таблице 1 верифицированы; непрерывный файл 2024_829_Ergometer_Dryad_Raw_V3.xlsx на Dryad возвращает HTTP 403 Forbidden (AWS WAF). Статус: RAW_TIMESERIES_UNAVAILABLE.
   - Hug et al. 2021: опубликованы литературные агрегаты по 8 операторам для 1 испытуемого (8 операторов != 8 испытуемых). Архив 444 МБ на Figshare возвращает HTTP 403 Forbidden (Cloudflare R2).
   - Томография: когортные таблицы SRC-0070 и SRC-0071 отозваны; Franke 2020 single-subject 3D MRI (379.89 мл) верифицирован по MAT.
3. Биофизическая модель рекрутирования (EXP-0038):
   - Сценарные параметры пула (500 ДЕ, -35% силы) отделены от модельных результатов (+14% sEMG RMS, 40.9x чувствительность a_eff к жиру). Статус: COMPUTATIONAL_SIMULATION_HYPOTHESIS.
4. Физический баланс энергии CPE45 (EXP-0041):
   - Строго разделены внешняя работа (250 Вт * 2700 с = 675 кДж), валовой метаболический расход (~3375 кДж при eta_gross ~20%), локальный буфер PCr (0.11-0.39 кДж в активном объёме голени; 0.62 кДж во всей GM) и тепловыделение (Delta_R H = 21.0 кДж/моль). Устранено прямое деление локального буфера на внешнюю работу.
5. Постоянный Evidence Gate (tools/verify_data_provenance.py):
   - Интегрирован в tools/validate_repository.py, проверяет 11 обязательных метаданных полей, блокирует статус EXTERNALLY_VALIDATED для синтетических данных и сканирует скрипты на синтетические генераторы y_true.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=32, DEC=15, ISS=19, SRC=72.
- Тесты: 171/171 PASS (все тестовые наборы репозитория).
