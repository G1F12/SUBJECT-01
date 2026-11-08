# Research Cycle 9 — Empirical Data Acquisition, Recruitment Observability & Validation Design

**Рабочая директория**: `research/empirical_recruitment_2026_11_08`  
**Дата**: 2026-11-08  
**Цель**: переход к реальным эмпирическим данным человека, биофизическое разрешение ненаблюдаемости доли рекрутирования двигательных единиц $a_{\text{eff}}$, и независимая кросс-субъектная валидация (LOSO).

---

## Структура файлов цикла

- [`REPORT.md`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/REPORT.md): полный научный отчёт Cycle 9 с ответами на 7 вопросов и обязательной таблицей эпистемического аудита.
- [`DATA_AUDIT.md`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/DATA_AUDIT.md): аудит первоисточников SRC-0068..0072, понижение статуса покоя Andersen & Saltin 1985, разграничение энтальпии $\Delta_R H$ и свободной энергии $\Delta G_{\text{ATP}}$.
- [`MATHEMATICS.md`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/MATHEMATICS.md): уравнения пула ДЕ по Ханнеману, частотного кодирования, объемного проводника, фильтра подкожного жира, фазового гашения и 4-уровневой идентифицируемости.
- [`MEASUREMENT_MODEL.md`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md): физические измерительные карты для HD-sEMG, 31P-MRS, 3D MRI, NIRS.
- [`LIMITATIONS.md`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/LIMITATIONS.md): границы применимости, барьеры межмышечного переноса, статус TARGET-CPE45 и NO_GO.
- [`sources.json`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/sources.json): локальный реестр первоисточников Cycle 9.
- [`experiments.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/experiments.py): мастер-скрипт запуска экспериментов EXP-0037..0041.
- [`experiment_results.json`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/experiment_results.json): структурированные результаты всех экспериментов.
- [`extract_empirical_data.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/extract_empirical_data.py): извлечение и валидация данных Rehman 2024, Hug 2021 и MuscleMap.
- [`biophysical_recruitment_model.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/biophysical_recruitment_model.py): биофизическая модель рекрутирования 500 ДЕ и объемной фильтрации.
- [`identifiability_recruitment.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/identifiability_recruitment.py): расчёт 4-уровневой идентифицируемости и профильного правдоподобия.
- [`validation_loso.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/validation_loso.py): независимая межсубъектная валидация Leave-One-Subject-Out.
- [`test_empirical_recruitment.py`](file:///d:/SUBJECT-01/research/empirical_recruitment_2026_11_08/test_empirical_recruitment.py): 8 регрессионных тестов контроля качества.
