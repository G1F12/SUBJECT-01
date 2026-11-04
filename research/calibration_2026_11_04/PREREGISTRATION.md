# Cycle 6 — первичная фиксация до чтения новых числовых исходов

База a4d3a04ab8ef0fc056815989f4b775cf9773f3ca. EXP-0023..0026 свободны
после проверки всех registry. Один агент OpenAI Codex, без внешнего рецензента.
Просмотрены metadata/описания и имена/размеры ZIP members Zenodo13477128,
но не новые числовые CPET/log_master/EE значения. Metadata: version1.0.0,
CCBY4.0, independent cohort relative to previous sprint studies; no guaranteed
cross-study identity key. Public byte-range retrieval is supported and recorded.

Цели: measured pulmonary flux / whole-body cost / task-specific effective
efficiency and baseline. Не подменять local oxidativeATP ими. Сохраняем9D
редукцию; никаких новых D2states или universalphysiology constants.

## Разделение и endpoints

Все trials/tasks участника вместе. IDs по native CPET paths Pn.
Test: n%5==0; development: остальные. До immutable model lock test numerical
outcomes не используются в fitting/selection, audit distributions или графиках.
Schema/header/source-code inspection разрешены. Test raw могут храниться в
ignored cache; программный фильтр предшествует чтению outcome rows.

Power здесь может быть prescribed workload. Тогда не объявляем его независимым
output для CPE45/sprint validation и не создаём фиктивное сравнение power RMSE.
Возможная заранее объявленная ограниченная проверка — whole-body calorimetric
cost при заданном W, отдельно от TARGET-CPE45. Primary: participant-balanced
stage-mean W-equivalent metabolic-cost RMSE; secondaryMAE,bias,participant errors,
calibration и paired participant bootstrap2000 seed20261106. Success: paired95%
RMSE difference interval below0 vs constant and historical transfer; no claim
about sprint power/2700s or identifying localATP scale from this alone.

Данные принимаются при явных VO2/VCO2 units и временной/нагрузочной связи.
Если нет VCO2: energy not directly measured, допускается только caloric-equivalent
bound, не silently fixedRER. Если power отсутствует: noefficiency, анализ только
baseline/pulmonarykinetics. RERoutside.7..1 при steady-state исключается из primary
efficiency fit, но число/исходные diagnostics сохраняются. Никакой imputation.
Protocol source defines stages; final60s steady window, минимум30validseconds и
80%coverage; при stage<120s primary steady inference unavailable. BaselinezeroW
не считается истинным passiveRMR без posture/cadence документации.

Модели same endpoint costW: development meanconstant; affine a+bW (systemic
effective cost); историческая D2 equilibrium M+W/η со старыми фиксированными
parameters и явной, проверяемой гипотезой systemic=local;9D reduction alone
doesnot define absolute cost and is reported NOTPREDICTABLE, not assigned fakeη1.
Calibrated hierarchy (subject baseline + common slope) only if subject baseline
is truly observed, baseline supplied consistently to all applicable candidates.
No test-driven model addition. Affine vs quadratic nonnegative range selected
only by development participantLOPO, primary participant-balanced RMSE.

До test: source/member hashes, codeSHA, developmentdigest, modelparameters,
metrics, endpoint eligibility and winner locked in Git; one explicit evaluation.
Если числовые данные/метрология не поддержат этот endpoint — VALIDATIONNOTDONE,
законченный calibration/identification audit вместо ложного внешнего успеха.

## Калибровка и фальсификация

Weir-type calorimetry: chemical fuel turnover estimate from measured pulmonary
VO2,VCO2 and stated stoichiometry, не independently measured heat/ATP flux.
Task-specific delta efficiency is effective slope reciprocal; baseline intercept
не автоматически restingcost. Perparticipant multistart/LOPO/profile/SVD/FIM,
условная noise model и block uncertainty; no flat-profile IDENTIFIED labels.

Обязательные tests: gain±5/10%,offset±.1L/min,timing±5/15s,activevolume×.5/2,
ATP reference±20%,task mismatch, incomplete recovery, activebaseline, individual
variation, unknown transport and nonaffine discrepancy. These are sensitivity
perturbations on real observations, not invented human data or new interventions.
Новые PCr/VO2 partially joint sources — distinct evidence, not synthetic persons.
Old10/7holdouts и viewedCycle5PCr не дают нового independent improvement claim.
