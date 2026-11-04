# EXP-0015..0018 — восстановление, фальсификация и независимый тест

04.11.2026. Продолжение SUBJECT-01, база
c7a7c9caa7f619f64c88b9e0430a6b1f83148807. Работа выполнена одним OpenAI Codex;
внешней научной рецензии/второго независимого агента нет. Проверены Gitfetch,
HEAD, governing files, семь реестров и предыдущий цикл. Исторические файлы
Foundation/Integrated/CPE45 не изменены. NO_GO для вмешательств сохранён.

**Содержательный результат:** новая независимая выборка снова фальсифицирует
энергетические прогнозы. Восстановительная tau по доступной мощности не
идентифицируется; установлены точные масштабные симметрии latent энергетики.
Физиологические коэффициенты не подгонялись ради положительного вывода.
Критерии успеха этого цикла — C и D, частично A на уровне модельных механизмов,
**не B** (нет подтверждённого преимущества новой физической модели).

## Данные и предварительная фиксация — EXP-0016

Три новых источника SRC-0040..0042; аудит DOI/PMID/версий/методик/лицензий,
hashes и ограниченных notices — [DATA_AUDIT](DATA_AUDIT.md), sources.json.
Получены реальные Power/VO2 XLSXv1 новой работы Jutlah et al.2026 (OSFdb3sk):
21 человек,10×6s, три active-rest условия12/18/24s. В MeanPower630чисел,
пропусков нет. VO2 —1260 **экстремумов фаз**, без continuous gas traces;
PCr отсутствует. Совместные PCr–VO2–power временные ряды не получены.
DryadPCr файл описан, но API401/public403 не позволили получить numeric cells.
Это access failure, не отрицательный физиологический результат.

Отдельная лицензия OSFraw не установлена(node_license=null): XLSX остаются в
игнорируемом cache; опубликованы pinnedURL/version/SHA256/retrieval recipe,
наш код/прогнозы/статистика. Открытая статья не автоматически лицензирует raw.

Правила [PREREGISTRATION](PREREGISTRATION.md) опубликованы коммитом9f25664 до
extraction;14development/7test участников с группировкой всех их условий.
Первый sprint — baseline input; оцениваются378development/189test endpoint2..10.
LOPOCV на14development выбрал **константу** до открытия test. Код/параметры/
sourceSHA/trainingSHA зафиксированы и опубликованы коммитом
8319168dde19d3cfa0b8b69aadeeab03963c855a. Затем отдельная команда --test открыла7
участников. Модели после этого не менялись; новый test тоже теперь просмотрен.
Старые10holdout остались только диагностикой, не второй независимой проверкой.

## Причина провала — EXP-0015

[Причинно-диагностическая матрица](DIAGNOSTIC_MATRIX.md) разделяет software,
структуру, параметры, недостаток данных, статистику и protocol transfer.
Старый RMSE378.543770W воспроизведён новой инструментированной копией алгоритма;
parity с неизменённым оригиналом проверен автоматически.

В исходном виртуальном nominal1000W цикле первая фактическая mean513.12W,
десятая358.33W. Затем shape умножается на measured baseline другого масштаба.
Такой bridge — baseline-conditioned statistical prediction, **не** независимо
согласованный индивидуальный metabolic ledger. Закон release=E/tau одновременно
задаёт расход и спад доступной мощности; восстановления90s недостаточно для
возврата выбранных surrogate запасов. Эти механизмы вычислительно установлены.

Контрфактические старые RMSE: demand500W→291.17W; double capacity→310.99W;
fast recovery10s→227.92W; independent releasecap→294.48W. Ни один не доказал
физиологические значения и не достиг simplebaseline115.34W. Разминка только
через initialoxygen800W ухудшила результат до582.94W. Это отвергает конкретную
попытку исправления, а не эффект реальной warm-up/potentiation.

Ledger/единицы W↔J согласованы; dt bias мал. Независимая проверка на новых
участниках исключает объяснение всего провала только старой missing/ID-проблемой.
**Единственная истинная физиологическая причина не установлена.** Мощность не
позволяет отделить ёмкости, η, oxidative scale, восстановление и моторный demand.

## Конкурирующие модели

- **D1 existing:** неизменённая структура старого cycling_shape,rate0;
  для новых задач только заданная пауза заменяет90s. Исторический контроль
 90s воспроизводит прежние значения без переписывания файлов.
- **D2 corrected:** отдельные finite energy capacities и release-power caps;
  paid recovery, finite reserves; oxidative energy за шаг интегрируется
  аналитически, а не right-end rectangle. Demand задаётся actual firstbaseline;
  прогноз вW берётся напрямую из ledger без posthoc масштабирующего множителя.
  Параметры ёмкости8000/22000J,ratecaps2000/733.33W metabolic,η и oxygen из старой
  модели остаются **сценарными**, не новыми измерениями. Это физически согласованная
  структурная альтернатива, не доказанное исправление физиологии.
- **D3 empirical:** constant; signedlinear; monoexponential episode response;
  эффективная двухпараметрическая recurrence depletion/recovery.
  Development estimates: linear+.0097097/rep; mono amplitude+.101674,tau1rep.
  Recurrence выбрала depletion0; всеtau1..600s даютconstant. Tie-breaktau1s
  не является физиологической оценкой.
- **D4 hybrid conditional:** D2 с effective outputtau из D3 в fast recovery.
  Заранее исключён из выбора deployableмодели: outputtau не равнаPCr tau.
  Расчёт нужен для фальсификации соблазнительного «улучшения» за счёт1s recovery.

Новых центральных/тепловых/damageсостояний нет: источники их не идентифицируют.
Within-bout energy discharge сохраняется, но rawwithin-bout power не получена.

Отдельное ограничение переноса: новая работа использует unloaded **active** rest.
В зафиксированном cycling-модуле внешний demand в паузе равен нулю, остаётся
унаследованный cycling-intercept128.70W. Это не индивидуальная оценка цены
активного педалирования: cadence и непрерывный metabolic flux неизвестны.
Поддержание активности в паузах может менять одновременно расход и oxygen
priming; по фазовым экстремумам эти эффекты не разделены. После test это
предположение не заменялось новым подогнанным коэффициентом rest-cost.

## Новая независимая проверка мощности

Все модели оценены на **одинаковых189cells семи новых test участников**.
Первый baseline известен; это прогноз повторений, не zero-shot absolute capacity.
Таблицы errors/calibration/participant/protocol/recoverychanges и модельные
прогнозы каждой строки сохранены в results/test_*.csv. Calibration — диагностическая
регрессия observed на predicted, не последующая коррекция прогнозов.

| Модель | MAE W | RMSE W | Bias W | Participant bootstrap RMSE 2.5..97.5% W |
|---|---:|---:|---:|---:|
| Constant, выбран до test |100.94|126.54|−62.42|110.11..150.65|
| Linear |99.57|123.33|−33.55|105.35..146.09|
| Monoexponential |96.57|118.29|−5.87|96.35..141.82|
| D1 existing |340.71|350.70|−340.71|321.25..381.91|
| D2 corrected |347.18|361.71|−347.18|314.80..409.37|
| Empirical recovery |100.94|126.54|−62.42|110.11..150.65|
| D4 conditional hybrid |108.49|134.46|−85.92|118.65..158.54|

2000cluster bootstrap,resampling участников,seed20261104. Для mono RMSEminusconstant
95%bootstrap−19.22..+5.01W: уверенного преимущества не установлено. Нельзя после
просмотра test выбратьmono как новый подтверждённый winner. D4 хужеconstant:
pairedRMSEdifference+4.45..+11.03W. Smalln7 и selection/model-discrepancy
не исчерпываются этими intervals. Gaussian или population independence не заявлены.

По паузам12/18/24s RMSE:constant147.64/130.63/95.79W;
D1 358.07/378.86/311.80W;D2 353.25/382.40/348.55W. Структурная замена не
улучшает перенос согласованно. Все варианты плохо откалиброваны; например
mono calibration slope.254,intercept491.89W. Межэпизодная Δpower error не
выдаётся за PCr recovery error: самой PCr здесь не измерено.

Fit форм использует normalizedMSE, primary CV/test metric —W-RMSE. Это меняет
веса людей с разным baseline; исходный prereg не фиксировал более точную loss.
Несоответствие описано как ограничение, после test не исправлялось. Baseline
variability и regression-to-mean могут имитировать potentiation; физиологический
и измерительный механизмы не разделены. Последующий test не использовать снова
для заявления независимого преимущества исправленной loss/model.

## Идентифицируемость — EXP-0017

Finite-difference log-Jacobian по11энергетическим параметрам,36outputshapeточек
(4rest×9повторов),relativeSVDthreshold1e−6: **rank7/11** в проверенном scenario.
Сохранены весь Jacobian, singularvalues и cosine correlations sensitivities.
Localrank не является глобальным доказательством для каждого возможного режима.

Более сильный аналитический результат: при η→kη и одновременном делении всех
метаболических Cfast,Cslow,Pfast,Pslow,oxidativecap,maintenance наk механическая
мощность неизменна, пока преобразованные параметры допустимы. Rechargeefficiency
и timeconstants сохраняются. Численно максимальная разница<1e−12W.
Поэтому даже абсолютная мощность не даёт раздельно абсолютные ёмкости/КПД
без независимого metabolic anchor. Для normalizedshape есть дополнительная
общая энергетическая scale symmetry. Неизвестную η нельзя «определить» одним fit.

Реальный development profile effective recoverytau1..600s совершенно плоский
при оптимальном depletion0: derivative output поtau=0. Никакого конечного
confidence bound дляtau не получено. Не назначаем physiological posterior.
Profilechi-square использует рабочее constant-normalized-noise предположение;
flatness от него не зависит. Synthetic software control с depletion.18/tau60s
восстанавливает их точно на собственной информативной grid: алгоритм способен
recover при наличии сигнала; это не экспериментальные данные человека.

Фактически оценены только empirical outputcoefficients; **ни один новый
физиологический recovery parameter не идентифицирован**. Нужны independent
efficiency/metabolic cost и active muscle PCr concentration/mass дляабсолютногоC,
continuousVO2 с phase timing для on/offkinetics, одновременная мощность/PCr
на разных паузах/depletion, стимуляционные MVC/twitch/VA дляperipheral fatigue.

## Вычислительная проверка и CPE45 — EXP-0018

Paid-reserve ledger за каждый шаг: oxidative+initial−final=external+heat.
Release ограничен remainingenergy и independentpowercap. Recharge≤surplus×ηrec;
rate bound exponentialdeficit. Нулевой input/reserve даёт0работы. Химическое
топливо окисления явно внешний input, без заявления конечной glycogenёмкости.

Проверены24pause/depletionсценария (rest0/6/12/24/90/300s,initial0/.25/.75/1),
14локальных±20%perturbations,64epistemicUQ,4dt×2structures. UQ интервалы —
uniformmultipliers.75..1.25,не humanpopulation/CI. Work p05/50/95 при6/18s
14.68/19.69/25.58kJ для10эпизодов. Modeldiscrepancy значительно важнее
численного precision и не включена в эти parameter-only интервал.

Corrected firstmean612.985W при всех шагах. Lastmean453.512→453.470W при
dt.5→.0625; discrete recharge/targets дают residual dtdependence. Старый lastmean
358.327→356.067W. Convergence проверяет уменьшение difference при halving.
Нет заявления об exact solution всей coupled системы.

150циклов6/12s на2700s: конечные резервы1093.35/435.63J,работа200.58kJ,
heatgenerated1541.93kJ,energyresidual−3.31e−8J. Это **тест численной устойчивости**
изолированного cyclingмодуля с hypothetical parameters иrate0, не прогноз человека
или воспроизведение полного mixedCPE45. Heatgenerated не равно bodyheatstorage:
новая thermoregulation не калибрована. SourceVO2extrema не интегрируются как flux.

Перенос физической модели **не подтверждён**. АрхитектурыI/II/III не ранжировались
заново и не получили заявлений об улучшении. Падение мощности/retention/recovery
не предсказываются достоверно; энергетические состояния условны; тепло и
последовательные взрывные эпизоды пригодны лишь для scenarioverification.
TARGET-CPE45 not_assessed, интегрированная система NOT EXTERNALLY VALIDATED.

## Новые отрицательные результаты

- NEG-0010: физическаяD2 не превосходитconstant на новом lockedparticipanttest;
  даже D4 с неидентифицированной1s recovery хужеconstant.
- NEG-0011: outputrecoverytau flatprofile; capacity/η/oxidativescale имеют exact
  symmetry. Низкий fiterror не превращается в физиологическую идентификацию.
- NEG-0012: initialoxygenwarm-up alone ухудшает старый normalizedforecast;
  smallerdt/нулевойbasalintercept не устраняют провал. Это counterexamples
  отдельных model fixes, не доказательства отсутствия warm-up/BMReffects.

Следующий один приоритет: **получить доступный числовой PCr recovery файл с
continuousVO2 и synchronizedpower либо документированный независимый metabolic
anchor**, чтобы разорвать доказанную η–C–oxidative масштабную симметрию;
не подгонять мощности на уже открытых7test участниках заново.

## Воспроизведение

Python3.12/numpy2.5.4/matplotlib3.11.2, существующие requirements.txt. Rawcache
публично загружается с OSF и hash-pinned; networkavailability/licensing остаются
операционными ограничениями. Выполнить fetch_data.py только для первоначального
source retrieval; обычные tests автоматически получают pinnedbytes при отсутствииcache.
Не запускать --lock поверх существующего model_lock: защита от перезаписи.
Для полного computationalreplay использовать временную директорию/--check.

```text
python tools/validate_repository.py
python tools/reproduce_foundation.py
python tools/audit_foundation.py
python research/integrated_2026_11_01/test_model.py
python research/integrated_2026_11_01/experiments.py --check
python -m unittest discover -s tests -p test_cpe45.py
python research/cpe45_2026_11_04/test_model.py
python research/cpe45_2026_11_04/experiments.py --check
python research/recovery_2026_11_04/test_recovery.py
python research/recovery_2026_11_04/reproduce.py --check
git diff --check
```

26новыхtests +70прежних =96unit tests; Foundation13hashes/7CSV/45arithmeticrows
и обе historicalreproduction suites отдельно. Source/outputmanifest,modelcodeSHA,
groupedsplit,mutationleakage,missinghandling,oldparity,SIsymmetry,syntheticcontrol,
stepconvergence,paidrecovery и2700sstability автоматизированы. Все новые проверки
добавлены в Actions. ПрограммныйPASS не назван физиологическимPASS.
