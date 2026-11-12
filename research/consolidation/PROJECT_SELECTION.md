# Карта доказательств и отбор

Проверены 24 явно перечисленные директории. Уровень покрытия различается: исходный расчёт Bird повторён, для пяти импортов сверены исходные производные таблицы, для прочих кандидатов выполнен целевой скрининг локальных артефактов и карточек двух фаз аудита. Статистику и эксперименты этих проектов целиком не пересчитывали. Каталоги с копиями релизов, рабочего дерева или данных не считаются независимыми репликациями. Никакие дополнительные проекты из каталога 76 не допущены: аудит не указал для них уникального измерения с прямой связью с функциональной целью.

Для локаторов Pxxx см. `D:/PROJECT_PORTFOLIO_AUDIT/projects/Pxxx-*.md` и `D:/PROJECT_PORTFOLIO_AUDIT/PHASE_2_REAL_VALUE/projects/Pxxx-*.md`. Критерии применены качественно: прямота к A–E, тип и независимость доказательства, новизна относительно канона и литературы, измеримый параметр, совместимость с ограничениями, возможность следующей проверки и риск экстраполяции. Числовой рейтинг из портфельного аудита не используется как научный вес.

| Проект | Аудит | Решение | Цель | Гипотеза, данные и метод | Статус | Надёжность, независимость и возможный вклад | Литература |
|---|---|---|---|---|---|---|---|
| SUBJECT-01 | P072 | DUPLICATE | A–E | EXP-0042–0046, реестры и сырой Bird. Пересчёт LOSO и симуляции выделен в NEG-0044. | REPRODUCED | 6 людей в динамике, один набор. CPET и коленный момент измеряют разные исходы. | L1, L3, L8 |
| SUBJECT-01-wt-pr9 | P075 | DUPLICATE | E/D | Git 8fb92aa, AEGIS и docs/cycle13/AEGIS_INTEGRATION_DECISION.md в каноне. | MODEL_ONLY | Worktree и AEGIS имеют общий lineage. На проверенном HEAD отслеживаются семь .bundle. CONDITIONAL HOLD по DEC-0021. | L8 |
| force_frontier | P031 | RESEARCH_BACKLOG | A/C | force_frontier/reports/SCIENTIFIC_REAUDIT.md. Литературная карта силы, упорядочивание механистических гипотез. | UNVERIFIED | Нет новой человеческой когорты. Переоценка SILA ослабила исходную карту. | L2, L3 |
| SILA | P029 | RESEARCH_BACKLOG | A/C | outputs/force_frontier_final_adjudication/FORCE_FRONTIER_FINAL_EVIDENCE_REPORT.md. Переоценены 92 назначения, все 21 прежних R4 понижены. | OBSERVED | Проверка качества кодирования, эмпирического эффекта нет. Одна публикация может связывать несколько стрелок. | L2, L3 |
| PLOTNOST | P028 | RESEARCH_BACKLOG | A | outputs/muscle_density_review и outputs/biotech_density_hypotheses_2026-07-15. Обзор и эвристические рейтинги архитектуры и синхронизации. | UNVERIFIED | Плотность, PCSA и удельное напряжение различны. Нет добавочного калибруемого эффекта. | L2 |
| PLOTNOST1 | P027 | RESEARCH_BACKLOG | A | new_evidence_matrix.csv и second_generation_dossier.md. Сравнительные карточки и расширение гипотез удельной силы. | UNVERIFIED | Повторное использование литературы и смежные endpoints. Независимые измерения эффекта отсутствуют. | L2 |
| mega-myshca | P032 | REJECT | A | Каталог пуст при проверке. | INSUFFICIENT_DATA | Научный артефакт для оценки отсутствует. | — |
| MTJCore | P062 | EVIDENCE_IMPORT | B/E | Stage 5, 6 и 7. Парные донорские псевдобалки, замороженная сигнатура, отдельный протеомный контраст. | REPRODUCED | FND-0047, NEG-0041, FND-0048. Различия в анатомии, конфаундинг и малое n. Эффект на нагрузку и прочность отсутствует в измерениях. | L4–L6 |
| MTJFidelityGate0 | P067 | EVIDENCE_IMPORT | B | native_112_coverage.tsv, sample_metadata.tsv и DECISION.txt. Допуск engineered PXD072245 по нативной панели. | NEGATIVE | NEG-0042. Гейт качества входов, возможные ненаблюдаемые белки и неопределённая независимость повторов. | L6, L7 |
| MTJ Fidelity | P068 | REJECT | B | Каталог пуст при проверке. | INSUFFICIENT_DATA | Данные Gate0 учтены под собственным источником. | — |
| LOXDockAudit | P022 | RESEARCH_BACKLOG | B | REPRODUCING_ROUND5.md и examples/real_hdock_round5. Геометрические фильтры HDOCK с контрольными позами. | MODEL_ONLY | Сопоставление рангов внутри набора, нет внешней оценки по каталитической активности. Связь с функциональной механикой непрямая. | L9 |
| LOXEvoScan | P021 | RESEARCH_BACKLOG | B | results/tree, results/selection и README.md. Межвидовая филогения и классификация нагрузки. | MODEL_ONLY | Клада, качество ортологов и множественные тесты ограничивают вывод. Модель коэффициентов человеческого сухожилия не калибруется. | L9 |
| belok | P020 | RESEARCH_BACKLOG | B | decorin_screen_v1/06_tables, SILY_screen_v1/06_tables. Вычислительный скрининг targeting-кандидатов. | MODEL_ONLY | Сравниваются позы. Данные о сшивках, усталости, прочности и независимая репликация отсутствуют. | L9 |
| belok_al | P017 | RESEARCH_BACKLOG | B | fresh_tendon_strength_design/round5/reports/R5_final_decision.md. R5-04 rank 4 при пороге ≤3, R5-03 остановлен QC. | NEGATIVE | Провал гейта конкретной серии докинга. Активность, Cu/LTQ и механический выигрыш не измерены. | L9 |
| SomaBranch | P045 | EVIDENCE_IMPORT | C/D | Phase 11A.1. Пары silent→vocalized EMG, ретроспектива с разделением сессий, сравнение ridge и контролей. | NEGATIVE | NEG-0043. Одна validation-сессия и ранее экспонированный источник. Использование ограничено принципом допуска модели. | L10 |
| AEGIS-01 | P071 | DUPLICATE | D/E | CLAIMS_RETRACTION_REGISTER.md и ARCHITECTURE_BIOLOGICAL_FEASIBILITY.md. Сценарии защиты, теплоотведения и частные механические оценки. | MODEL_ONLY | Границы уже рассмотрены в Cycle 13. INV-0017/0018 ретрагировали искусственную когорту и круговую проверку. Комплексный функциональный исход не установлен. | L8 |
| AXO-PIRA | P060 | RESEARCH_BACKLOG | E | AXO-PIRA_Codex_Bundle_v1.1/reviewer_revision_v1.1/docs/R3_FINAL_EVIDENCE_RECLASSIFICATION_REPORT.md и v2.2 report. Duerr, 236 генов. | OBSERVED | ROAST p≈0,043, exact 2/20 односторонний и 4/20 двусторонний. C3-R зависим, v2.2 не достигла биологического исхода. Аксолотль. | L11 |
| MORPH | P025 | REJECT | E | Каталог пуст при проверке. | INSUFFICIENT_DATA | Научный артефакт для оценки отсутствует. | — |
| SOMA | P023 | REJECT | — | soma/docs и demo_output. Многоролевой генератор гипотез и протоколов. | UNVERIFIED | Нет независимого функционального результата или проверенного преимущества научной методики. | — |
| NEXUS-BIO | P011 | REJECT | — | docs/NEXUS_BIO_TECHNICAL_AUDIT.md. Поиск, граф и предметные маршруты. | UNVERIFIED | Биоинформатические выводы не прошли слепой биологический эталон. Запуск API не валидирует результат. | — |
| NEXUS-MONEY | P012 | REJECT | — | docs/NEXUS_BIO_TECHNICAL_AUDIT.md и структура baseline/modules. Общая агентная линия. | INSUFFICIENT_DATA | Вариант P011 с 94 общими хешами по Phase 1. Хеш технического аудита также совпал с P011. Есть био-API и генератор отчёта о биоматериалах, независимого проверенного вывода нет. | — |
| ThymusLOXScan | P041 | RESEARCH_BACKLOG | E | reports/baran_gale_mousethymusageing_lox_reanalysis.md и cross_dataset_lox_analysis.md. Pseudobulk и межкогортные сопоставления стромы. | OBSERVED | Возрастные ассоциации, малые группы, age–batch и прокси образцов. Ткань и вид не совпадают с функциональной гипотезой сухожилия. | L12 |
| NEUROFORGE-01 | P070 | REJECT | C | EXPERIMENT_REGISTRY.md и NEGATIVE_RESULTS.md. Нейронные схемы дрозофилы и отдельный рыночный holdout. | MODEL_ONLY | Рыночный Δ Brier +0,001553 касается прогноза рынка. Человеческой сенсомоторной проверки нет. | L13 |
| neuroquery | P035 | REJECT | C | docs/EVALUATION_PROTOCOL.md и P035 phase 2. CTC на лицевой EMG и replay. | OBSERVED | Validation CER 0,7350, WER 1,1478, test закрыт. Разные исходы и задачи по сравнению с силой и реакцией. | L10 |

## Статусы

`OBSERVED` — артефакт или измерение найдено. `REPRODUCED` — пересчитана заявленная величина с описанным уровнем воспроизведения. `INDEPENDENTLY_VALIDATED` — отдельное независимое испытание той же величины с согласованным endpoint. `MODEL_ONLY` — вычислительное следствие предпосылок. `UNVERIFIED` — гипотеза без достаточной проверки. `NEGATIVE` — заранее оговорённый гейт или сравнение не пройдены. `CONTRADICTED` — определённое утверждение противоречит данным в указанной области. `INSUFFICIENT_DATA` — данных для вердикта нет. Статусы относятся к конкретному утверждению. Внешние доноры дают независимость данных; расчёт на их основе всё ещё принадлежит MTJCore.

## Аналоги в первичной литературе

- L1. Bird и соавт. Исходные динамические и изометрические данные и опубликованные модели. [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.sbcc2frmh)
- L2. Erskine и соавт. Вариабельность оценок удельного напряжения, PCSA и момента у людей. [Статья](https://pubmed.ncbi.nlm.nih.gov/20703498/)
- L3. Lloyd и Besier. EMG-управляемая модель мышечных сил и коленного момента. [Статья](https://doi.org/10.1016/S0021-9290(03)00010-1)
- L4. Karlsen и соавт. Миоядерные домены человеческого MTJ. [Статья](https://pubmed.ncbi.nlm.nih.gov/36924352/) · [Данные E-MTAB-12529](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-12529)
- L5. Møbjerg и соавт. Ранний транскрипционный ответ MTJ и компартментов человеческой мышцы. [Статья](https://doi.org/10.1152/ajpcell.00700.2025) · [Данные E-MTAB-15400](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-15400)
- L6. Нативный протеом MTJ человека. [Статья](https://pmc.ncbi.nlm.nih.gov/articles/PMC8851264/) · [PXD029307](https://www.ebi.ac.uk/pride/archive/projects/PXD029307)
- L7. Протеом биопечатной модели человеческого MTJ. [Депозит авторов](https://doi.org/10.18150/01FQQG) · [PXD072245](https://www.ebi.ac.uk/pride/archive/projects/PXD072245)
- L8. Kongsgaard и соавт. Региональная адаптация площади и жёсткости сухожилия надколенника. Для системного метаболизма см. отдельные протоколы ACTES и Malaga. [Статья](https://pubmed.ncbi.nlm.nih.gov/17524067/) · [ACTES](https://doi.org/10.13026/2qs3-kh43) · [Malaga](https://doi.org/10.13026/7ezk-j442)
- L9. Эксперименты по LOX-зависимым сшивкам и модулю в развивающемся сухожилии цыплёнка. [Marturano и соавт.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3631620/) · [Исследование рекомбинантной LOX](https://pmc.ncbi.nlm.nih.gov/articles/PMC9389157/)
- L10. Gaddy и Klein. Декодирование немой речи из лицевой EMG. [Данные и публикация](https://zenodo.org/records/4064409)
- L11. Duerr и соавт. Позиционная идентичность при регенерации конечности аксолотля. [Статья](https://www.nature.com/articles/s41467-025-59497-5)
- L12. Мышиная строма тимуса и возраст. GSE132278 является микрочиповым контекстом. [GEO](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132278)
- L13. Функциональная модель коннектома дрозофилы. [Shiu и соавт.](https://doi.org/10.1038/s41586-024-07763-9)

Консолидация выделяет собственные межнаборные сопоставления, критерии допуска и результаты вычислительных проверок. Известные тканевые домены, LOX-зависимая химия и методы EMG-моделирования относятся к указанным работам.
