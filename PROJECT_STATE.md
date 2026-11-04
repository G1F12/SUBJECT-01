# SUBJECT-01 — состояние после recovery-cycle,04.11.2026

Канонический публичный G1F12/SUBJECT-01. Проверенная база текущего цикла:
c7a7c9caa7f619f64c88b9e0430a6b1f83148807. Итоговый GitHub mainHEAD проверять
через remote/API после PR/CI. Ветка research/cpe45-recovery-identification-20261104.

[Отчёт EXP-0015..0018](research/recovery_2026_11_04/REPORT.md),
[causal matrix](research/recovery_2026_11_04/DIAGNOSTIC_MATRIX.md),
[аудит данных](research/recovery_2026_11_04/DATA_AUDIT.md).

- Foundation EXP1..6,Integrated EXP7..10,CPE45 EXP11..14 и NEG1..9 сохранены.
  СтарыйRMSE378.543770W воспроизведён; старые10holdout остаются просмотренными.
- Новая работаSRC-0040:21человек,три паузы12/18/24s,10×6s. РеальныеPower/VO2
  файлы скачаны. 630meanpower cells,1260VO2phaseextrema,безPCr/continuousgas.
  OSF node_license=null: raw не вGit; pinnedURL/version/SHA256/recipe сохранены.
- Prereg9f25664 до extraction; lock8319168 до test. Все условия одного человека
  в одной группе:14development/7test,378/189endpoints;groupedLOPOCV выбралconstant.
- Новый закрытый test:D1RMSE350.70W,D2corrected361.71W,constant126.54W;
  mono118.29W,ноpairedbootstrapinterval пересекает0 и модель до test не выбрана.
  D4conditional134.46W тоже хуже. Новое физическое улучшение НЕ валидировано.
- Exactη–metabolic-scale symmetry;scenarioJacobian rank7/11; recoveryprofile
  flat1..600s приdepletion0. Ни один новый physiological recoveryparameter
  не идентифицирован. Syntheticrecovery отдельно softwarecontrol.
- Матрица причин разделяет software/structure/parameters/data/transfer.
  Ledger и единицы согласованы;dtbias мал. Единственная физиологическая причина
  старой ошибки не установлена;posthoclatentfit на test не выполнен.
- 24pause/depletioncases,14perturbations,64epistemicUQ,4dt×2structures,
  2700sstability с conservation. Не прогноз новых возможностей человека.
- 26новых+70прежних=96unit tests;Foundationhashes/CSV/arithmetic,все3reproduction
  suites иCI. Численные outputs/2PNG/sourcehashes/lockedparams сохранены.

Реестры EXP18/HYP6/FND20/NEG12/DEC9/ISS15/SRC42; всеHYP unverified.
ISS-0014:missingPCr jointdata/exactconfounding;ISS-0015:baseline/loss/rawlicence.
ISS-0011 остаётся open;ISS-0001resolved,остальные прежниеopen сохраняются.
CPE45 not_assessed,NOT EXTERNALLY VALIDATED;NO_GO для вмешательств неизменён.
АрхитектурыI/II/III не перерангированы на неподтверждённой новой модели.

Следующий приоритет: совместныеPCr–continuousVO2–power данные с независимым
metabolic-cost anchor для разрываη–capacitysymmetry. Текущие7test теперь
просмотрены и не могут снова служить новой независимой проверкой.

SHA research: git log -1 --format=%H -- research/recovery_2026_11_04/REPORT.md.
Команды воспроизведения в REPORT.md/.github/workflows/validate.yml.
