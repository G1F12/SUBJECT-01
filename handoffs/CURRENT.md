# SUBJECT-01 — handoff Research Cycle 9 (Final Source Repair, Evidence Gate V2 & Real Data Unlock)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
Cycle 9 Final база: 95640071c38b25d2abb7c908892d5a74e3452184.
Ветка цикла: fix/cycle9-final-source-repair-and-evidence-gate-v2.
Итоговый main SHA фиксируется после локального merge и пуша.

Ключевые документы Cycle 9:
- research/empirical_recruitment_2026_11_08/REPORT.md (полный научный отчёт Cycle 9 с обязательной таблицей достоверности CLAIM / REAL MEASUREMENT / MODEL ASSUMPTION / VALIDATION STATUS и ответами на 9 вопросов)
- research/empirical_recruitment_2026_11_08/MATHEMATICS.md (биофизика рекрутирования 500 ДЕ по Ханнеману, объёмный проводник, фильтр SAT, 4 уровня идентифицируемости)
- research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md (физические измерительные карты для HD-sEMG, 31P-MRS, 3D MRI, NIRS)
- research/empirical_recruitment_2026_11_08/DATA_AUDIT.md (метрология и аудит источников SRC-0068..0072, фиксация HTTP 403 WAF/CDN блокировок Dryad и Figshare, ретракция фейкового LOSO, исправление частот Hug по Таблице 2 и когорты Andersen по PMID 4057091)
- research/empirical_recruitment_2026_11_08/LIMITATIONS.md (барьер доступности первичных данных, физический баланс CPE45, статус TARGET-CPE45 и NO_GO)
- tools/verify_data_provenance.py (постоянный автоматический гейт Evidence Gate V2 со сквозным контролем SHA256 и отрицательными тестами)
- tools/process_rehman_xlsx.py (автономный инструмент owner-assisted загрузки и обработки XLSX Rehman et al. 2024 с расчётом моноэкспоненциальной кинетики)
- tests/test_evidence_gate_v2.py (9 юнит-тестов Evidence Gate V2, включая 5 отрицательных тестов на повреждение данных)
- research/empirical_recruitment_2026_11_08/test_empirical_recruitment.py (9 юнит-тестов регрессионной и научной достоверности Cycle 9)

Результаты Cycle 9 Final Source Repair & Real Data Unlock:
1. TASK A — Исправление первоисточника Hug et al. 2021 (SRC-0068, DOI 10.1016/j.jelekin.2021.102548, bioRxiv 10.1101/2021.02.19.431376):
   - По Таблице 2 установлены официальные частоты разряда ДЕ:
     GM: 10% MVC = 8.1 ± 1.1 имп./с; 30% MVC = 8.1 ± 1.0 имп./с; 50% MVC = 7.6 ± 1.2 имп./с; 70% MVC = 12.2 ± 0.6 имп./с.
     GL: 10% MVC = 8.1 ± 0.9 имп./с; 30% MVC = 8.2 ± 1.3 имп./с; 50% MVC = 11.3 ± 1.3 имп./с; 70% MVC = 14.0 ± 1.5 имп./с.
   - Неподтверждённые частоты (9.8, 12.6, 15.4, 19.8 Гц) отозваны (NEG-0033).
   - Число биологических участников переведено в UNKNOWN (данные объединены из двух разных исследований Del Vecchio 2019 и Hug 2021; 8 операторов != 8 испытуемых).
2. TASK B — Получение и пайплайн Rehman et al. 2024 (SRC-0069, Dryad doi:10.5061/dryad.08kprr59v):
   - Файл `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18,136 байт, SHA256 `ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`).
   - Зафиксировано объективное препятствие: прямой поток защищён AWS WAF / Anubis BotStopper JS-челленджем (HTTP 403), REST API требует Bearer OAuth token (HTTP 401). Автоматический обход средств защиты запрещён.
   - Подготовлен owner-assisted инструмент `tools/process_rehman_xlsx.py`: пользователь скачивает файл браузером в репозиторий или Downloads, после чего скрипт автоматически валидирует SHA256, извлекает 3 триала по 75 спектров (6 с), фитит моноэкспоненту восстановления PCr и сохраняет проверенные метрики.
   - Введён строгий запрет кросс-субъектного LOSO при одном участнике ($N=1$).
3. TASK C — Evidence Gate V2:
   - Обновлён `tools/verify_data_provenance.py`: физическая проверка существования `source_file`, байтовый пересчёт SHA256, запрет dummy-хеша `N/A`, строгое разделение `n_biological_participants`, `n_operators`, `n_trials`, `n_records`, запрет `EXTERNALLY_VALIDATED` для синтетических данных, аудит скриптов.
   - Созданы unit-тесты `tests/test_evidence_gate_v2.py` (9 тестов, в т.ч. 5 negative tests: bad SHA256, missing file, synthetic y_true, dummy hash, conflated participants).
4. TASK D — Финальная научная согласованность:
   - Andersen & Saltin 1985 (SRC-0066, PMID 4057091): строго подтверждено 5 участников-мужчин (не 8).
   - Сохранено отсутствие прямого покоя GM (DOWNGRADED_NOT_PRIMARY_RESTING_TABLE).
   - Введён запрет категорической ошибки `category_error_static_pcr_to_external_work_prohibited = True`: запрещено делать вывод о >99% окислительном обеспечении сопоставлением статического буфера PCr одной мышцы (0.62 кДж) с общей внешней работой 45 минут (675 кДж).
   - Утверждено пятиуровневое разделение: механическая работа (675 кДж), валовой метаболизм (~3375 кДж), оборот АТФ (~62.5 моль АТФ), окислительный ресинтез (~3300 кДж / 61.1 моль), гликолиз (~75 кДж / 1.4 моль) и локальный буфер PCr (0.11-0.62 кДж).

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 180/180 PASS (все тестовые наборы репозитория).
