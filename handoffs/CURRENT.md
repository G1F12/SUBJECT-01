# SUBJECT-01 — handoff Research Cycle 9 (CI Failure, Strict JSON & Real-Data Pipeline Repair)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
База: 19402484b0295c46ae03d5dab47a363f89cf5795.
Ветка: fix/ci-failure-and-real-data-pipeline-repair.
Итоговый main SHA фиксируется после локального merge и пуша.

Ключевые документы и инструменты:
- research/empirical_recruitment_2026_11_08/REPORT.md (полный научный отчёт Cycle 9 с обязательной таблицей достоверности CLAIM / REAL MEASUREMENT / MODEL ASSUMPTION / VALIDATION STATUS и ответами на 9 вопросов)
- research/empirical_recruitment_2026_11_08/MATHEMATICS.md (биофизика рекрутирования 500 ДЕ по Ханнеману, объёмный проводник, фильтр SAT, 4 уровня идентифицируемости)
- research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md (физические измерительные карты для HD-sEMG, 31P-MRS, 3D MRI, NIRS)
- research/empirical_recruitment_2026_11_08/DATA_AUDIT.md (метрология и аудит источников SRC-0068..0072, фиксация HTTP 403 WAF/CDN блокировок Dryad и Figshare, канонические байтовые хеши, исправление частот Hug по Таблице 2 и когорты Andersen по PMID 4057091)
- research/empirical_recruitment_2026_11_08/LIMITATIONS.md (барьер доступности первичных данных, физический баланс CPE45, статус TARGET-CPE45 и NO_GO)
- tools/verify_data_provenance.py (постоянный автоматический гейт Evidence Gate V2 со сквозным контролем SHA256, аудитом строгого JSON RFC 8259 и 7 отрицательными тестами)
- tools/process_rehman_xlsx.py (автономный инструмент owner-assisted загрузки и обработки XLSX Rehman et al. 2024 с расчётом моноэкспоненциальной кинетики и проверкой SHA256)
- tools/rehman_ooxml.py (модуль чтения и записи OOXML XLSX на стандартной библиотеке Python без сторонних зависимостей)
- tests/test_rehman_xlsx_processor.py (8 юнит-тестов процессора Rehman XLSX, включая 5 отрицательных тестов на повреждение данных)
- tests/test_evidence_gate_v2.py (12 юнит-тестов Evidence Gate V2, включая 7 отрицательных тестов на повреждение данных)
- research/empirical_recruitment_2026_11_08/test_empirical_recruitment.py (9 юнит-тестов регрессионной и научной достоверности Cycle 9)

Результаты ремонта CI, байтового происхождения и строгого JSON:
1. CI Failure & Byte Provenance Repair (GitHub Actions run 42654714327):
   - Устранена первопричина падения шага Structural and hash audit: настроен `.gitattributes` с явным правилом `text eol=lf` для всех репозиторных файлов при сохранении `-text` для бинарных CSV.
   - Franke 2020 JSON приведен к каноническим LF байтам: 3049 байт, SHA256 `0345c4a8b36c95d9641c52bc96b759a43e6f899d186159606481060fbb437fa2`, тип `DERIVED_EXTRACTION_JSON`.
   - Rehman 2024 XML: 42824 байта, SHA256 `d8f1df9664c94b4846da3c015ced45310bc17ea1f48b58ce287c61db6bd1ed2c`, тип `PUBLISHED_TABLE_DATA`.
2. Завершение процессора сырых данных Rehman 2024 (`tools/process_rehman_xlsx.py`):
   - Реализован легковесный OOXML движок `tools/rehman_ooxml.py` (zipfile + xml.etree).
   - При отсутствии файла возвращает `PENDING_RAW_DATA` (без ложного PASS).
   - При наличии файла выполняет валидацию байтового SHA256 (`ae7876d1...`), парсинг 3 триалов по 75 спектральных точек (6 с), моноэкспоненциальный фит кинетики PCr/Pi с 95% ДИ, сопоставление с опубликованными $k = 1.43, 1.62, 1.53\text{ мин}^{-1}$ и оценку test-retest repeatability. Метод LOSO при $N=1$ строго запрещён.
   - Добавлены тесты `tests/test_rehman_xlsx_processor.py` (8 тестов) и шаг в `.github/workflows/validate.yml`.
3. Модернизация Evidence Gate V2 (`tools/verify_data_provenance.py`):
   - Сквозная проверка байтового хеша SHA256 для любого локального файла независимо от категории данных.
   - Введены типы: `ORIGINAL_BINARY_FILE`, `DERIVED_EXTRACTION_JSON`, `PUBLISHED_TABLE_DATA`, `LITERATURE_REFERENCE_WITHOUT_FILE`, `SYNTHETIC_MODEL_SIMULATION`.
   - Устранены токены `Infinity`, `-Infinity`, `NaN` во всех JSON-файлах репозитория по RFC 8259 (неопределённые числа обусловленности заменены на `null` со статусом `"INFINITE"`).
   - Отрицательная батарея расширена до 7 тестов (добавлены подмена хеша в таблице и строгий аудит JSON).
4. Уточнение статуса научных утверждений TARGET-CPE45:
   - Значения 3300 кДж окислительного ресинтеза и 75 кДж гликолитического вклада строго задокументированы как `ESTIMATED_SCENARIO_BALANCE_NOT_MEASURED`.
   - Аэробная фракция зафиксирована как `measured_empirical_aerobic_fraction: null`, статус: `NOT_EMPIRICALLY_MEASURED_IN_CPE45`.
   - `TARGET-CPE45` сохраняет статус `NOT EXTERNALLY VALIDATED`, биологические вмешательства — `NO_GO`.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 188/188 PASS (все тестовые наборы репозитория, включая 8 тестов процессора Rehman и 12 тестов Evidence Gate V2).
