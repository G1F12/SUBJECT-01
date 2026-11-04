# SUBJECT-01 — передача, 04.11.2026

Начать с git fetch origin, статуса рабочего дерева, GitHub main/PR/Actions.
Публичный G1F12/SUBJECT-01 — единственный источник истины.
База070a7343e522ca9fdbe37d3c0f7e3e0894bc7e30;
ветка research/cpe45-dynamics-20261104. SHA research commit:
git log -1 --format=%H -- research/cpe45_2026_11_04/REPORT.md.
Итоговый HEAD проверять напрямую, не выводить из handoff.

Читать research/cpe45_2026_11_04/REPORT.md и DATA_AUDIT.md до интерпретации.
EXP-0011..0014: динамика2700s,15 сценариев,64 UQ,16 perturbations,4dt,4negative.
8 первичных источников, CC BY исходный XLSX v1,44 строки/26 missing MeanP,
нет подтверждённого межклиматического pairing; Qatar исключён из holdout.
11 fit/10 пригодных holdout NC участников,99/90 endpoints; Lp18 исключён.
Первый sprint supplied. Coupled RMSE378.54W против constant115.34W:
провал переноса, не validation успех. Не подгонять заново на этих holdout.
PCr exponential temporal holdout +11.60pp (та же выборка).

Thermal diagnostic без motor feedback и cold regulation; deltaT не core temperature.
Реакция/accuracy/coordination/damage/central activation/post45 test неизвестны.
I/II/III условные; II больше работа, хуже humid heat; III neural gain не заявлен.
TARGET-CPE45 not_assessed, model not_empirically_validated, NO_GO сохранён.
Foundation/Integrated исторические файлы не изменены.

26 новых+25measurement+19integrated=70 unit tests; hashes/reproduction/CI отдельно.
Команды — в REPORT.md. Реестры:EXP14/HYP6/FND16/NEG9/DEC8/ISS13/SRC39.
ISS-0011 открыт несмотря на выполненный код; ISS-0012/13 новые ограничения.
Следующий приоритет: индивидуальные совместные PCr–VO2–power данные, recovery
identification, затем новый заранее фиксированный participant holdout.
