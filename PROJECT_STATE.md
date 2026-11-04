# SUBJECT-01 — состояние на 04.11.2026

Канонический публичный репозиторий G1F12/SUBJECT-01 (DEC-0005).
Базовый main:070a7343e522ca9fdbe37d3c0f7e3e0894bc7e30. Новый цикл публикуется
через research/cpe45-dynamics-20261104; итоговый GitHub HEAD проверять напрямую.

Foundation EXP-0001..0006 и Integrated EXP-0007..0010 сохранены без изменений:
13 исходных hashes,7 CSV,45 arithmetic rows и прежние отрицательные результаты.
Исторические Pareto по CPE45 по-прежнему not_assessed.

Выполнен EXP-0011..0014: [отчёт](research/cpe45_2026_11_04/REPORT.md),
[аудит](research/cpe45_2026_11_04/DATA_AUDIT.md).

- Раздельная динамика резервов, oxidative/slow kinetics, peripheral state,
  механики, восстановления и тепла2700s; подключён tools/cpe45.py.
- 8 первичных источников SRC-0032..0039, ограниченный notice audit; CC BY XLSX v1,
  44 строки условий,414 MeanP чисел/26 пропусков, исходные bytes и SHA256.
- 11 fit/10 пригодных holdout участников,99/90 endpoints; первый sprint — вход.
  Проверка переноса отрицательная: coupled RMSE378.54W, constant115.34W.
- 15 сценариев,64 epistemic UQ,16 perturbations,4dt,4negative. CSV/JSON/2PNG,
  trace/episodes/recovery/retention, seed20261104, параметры и hashes сохранены.
- Baseline:86.38kJ работы, max-task early/late175.86/114.08W, конечные резервы
  2758/2439J. Это модель, не измерения45-минутной работоспособности человека.
- I/II/III сравнены в3средах; II больше условная работа, но больше humid heat.
  III без данных не получает neural benefit. Ни одна архитектура не достигла CPE45.
- Thermal one-node без motor feedback/cold regulation; реакция/accuracy,
  coordination/damage/central activation и post45 test неизвестны.
- 26 новых+25measurement+19integrated=70 unit tests; Foundation checks отдельно.
  CI включает dynamic invariants и numerical reproduction.

Реестры:EXP14/HYP6/FND16/NEG9/DEC8/ISS13/SRC39. Все HYP unverified.
ISS-0011 остаётся открытым: код создан, эмпирической CPE45 validation нет.
ISS-0012 dataset ambiguity/failed transfer; ISS-0013 thermal/neural/damage gaps.
ISS-0002..0010 сохранены; ISS-0001 resolved. Один агент OpenAI Codex, внешнего
независимого научного рецензирования нет. Model not_empirically_validated;
TARGET-CPE45 not_assessed; вмешательства NO_GO.

Следующий приоритет: совместные индивидуальные PCr–VO2–power ряды для
идентификации восстановления и новый заранее фиксированный participant holdout.
Команды всех проверок — в REPORT.md и .github/workflows/validate.yml.
SHA research commit: git log -1 --format=%H -- research/cpe45_2026_11_04/REPORT.md.
