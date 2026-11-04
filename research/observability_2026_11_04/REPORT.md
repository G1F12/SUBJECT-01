# SUBJECT-01 — cycle5, EXP-0019..0022

**Решение: A (условное улучшение идентифицируемости), C (математическая
редукция), D (сохраняющийся эмпирический блокер). B не достигнут.**
База 4e900fbb337cf59efff8b75f473528485c7cc045,04.11.2026. Один агент OpenAI
Codex; новый вывод из исходного кода не называется независимой внешней рецензией.
Задача: установить измеримость до дальнейшей настройки 2700s модели.

## Сохранённая отрицательная база

До новой работы выполнены fetch/main/origin/main/status и чтение governance,
реестров, Recovery и CPE45 code/data/reports. Исторические pipeline/lock/results
не изменены. Recovery replay воспроизводит 189test endpoints: constant
RMSE126.54135W, D2361.70574W, mono118.29488W, преимущество mono не подтверждено.
Старый RMSE378.543770W, прежний Jacobian rank7/11 для normalized bout means и
плоский τ1..600s при depletion0 сохранены. Старые 10 и 7test — просмотренные.
Новые настройки не читают их outcome values: audit.py зависит только от engine.

## Доказанные математические результаты

[Полный вывод](MATHEMATICS.md) подтверждает масштаб S(k), а также обнаруживает
дополнительную точную baseline-симметрию B(b):

```
η′=kη; (Cfast,Cslow,Efast,Eslow,Lfast,Lslow)′=(...)/k
(oxidative cap,maintenance,oxidative state)′=(...)/k+b
recharge efficiency и все timeconstants неизменны
```

При допустимых параметрах и Oinitial=M это сохраняет механическую мощность
для **любого** известного нагрузочного протокола D2. Относительный PCr сохраняет
обе симметрии; абсолютный fast-reserve — только baseline-симметрию. При 8designs
ошибка scale≤2.53e−11W, baseline-shift≤6.3e−13W. Изменение rest или увеличение
повторов не устраняет exact confounding. Это утверждение об этой структуре,
не о невозможности экспериментальной физиологии вообще.

Ёмкости/отдача измеримы лишь через ηCi,ηLi; oxidative excess через η(Q−M).
Вместе сτfast,τslow,e,τoxygen это **9 эффективных параметров**, не 11 отдельных
физиологических чисел. Редуцированный представительη=1,M=0 — координаты,
не физиологическое измерение. Power parity≤1.58e−11W и energy ledger bounds
проверены. Totalheat и rest metabolic cost из reduced model не предсказываются.
Остаются возможными дополнительные глобальные неоднозначности в иных режимах;
rank9 показывает локальный, а не доказанный глобальный inverse.

## Минимальные наборы измерений — условные вычислительные результаты

11 энергетических параметров; объединение 8virtual protocols, известный demand,
известный initial fraction,2s samples, заданный Gaussian noise. Для O подразумевается
**абсолютный локальный oxidativeW**, для PCr — fast-state observation map.
Это не ранги реальных полученных наборов.

| Набор | Ранг /11 | Nullity | Condition number estimable subspace | Ограничение |
|---|---:|---:|---:|---|
| M1 power |9|2|184.7|Только 9 эффективных комбинаций при достаточно богатых traces |
| M2 power+calibratedO |11|0|56.1|Полноранговый local inverse только с известными gain,offset,allocation и delay |
| M3 power+relativePCr |9|2|181.8|Улучшает conditioning отдельных направлений, scale/baseline сохраняются |
| M4 power+absolutePCr+activevolume |10|1|232.3|Абсолютный energy scale снимается лишь с известным mol→J и activevolume; baseline остаётся |
| M5 power+O+relativePCr |11|0|55.8|Дополнительная проверка fast trajectory, но не гарантия правильности структуры |
| M6 M5+independentη |11|0|55.5|Не добавляет новый energy rank в идеальном M5; реально полезен для калибровки/опровержения VO2map |
| M7 M6+peripheralmeasure |11|0|55.5|Та же energy submodel; независимая twitch модель демонстрирует 2/2 своих rate/tau, не полную идентификацию CPE45 |

Полные spectra,FIM,sensitivity cosines,projected parameter correlations,
null vectors и threshold1e−4/1e−6/1e−8 сохранены в measurement_sets.json.
Condition_full=null при nullity>0. Pseudoinverse correlations не дают marginal
confidence intervals неидентифицируемых физиологических параметров.

На отдельном protocol ранги ниже: calibratedM5 имеет rank10 для short_long,
long_rest,predepleted,low_power; даже абсолютные каналы не гарантируют excitation.
Исторический 7/11 не «опровергнут»: новый 9/11 относится к совсем другим output
traces и протоколам. Точность прогнозов не следует из этих рангов.

Неизвестный gainO восстанавливает масштабную null direction; относительный
residual Jacobian вдоль неё≈2.48e−7 (finite-difference error). Неизвестный
offsetO дополнительно сохраняет baseline symmetry аналитически. PCr mmol/l
без независимых activevolume,ATP-reference и energyconversion не равна absoluteJ.
Реальное pulmonaryVO2 содержит транспорт, oxygenstores идругие ткани.
[Матрица наблюдаемости](OBSERVABILITY_MATRIX.md) перечисляет 63 связи с ошибками,
предпосылками и ограничениями переноса. Ни один fitted state не назван measured.

**Наименьшее наиболее полезное добавление:** для разрушения scale нужен один
независимый абсолютный metabolic/η/PCr-energy anchor; для отделения rest cost
нужен второй baseline anchor. В идеальном virtual model один изменяющийся
калиброванный O(t) канал содержит оба типа информации: rank9→11. При заданном
шуме он повышает weakest common-subspace FIM eigenvalue≈30.9→436.5, тогда как
четыре независимых power повтора дают≈123.5 и не меняют nullity2. Но это не
доказательство, что обычный pulmonaryVO2 способен заменить локальную калибровку.
Практический набор для различения механизмов: synchronizedpower+continuousVO2
+PCr trajectory и независимая проверка метаболического масштаба/baseline;
activevolume,pH и timing нужны для интерпретации PCr; twitch — для fatigue claim.

## Реальные полученные измерения

[Аудит источников](DATA_AUDIT.md),retrieval.json,sources.json,data_inventory.json.
Получены и **прочитаны** PCrFigure1A.xlsx (2 человека,6scans,522relativecells),
четыре plantarflexionMAT с PCr/Pi/ATP/pH144points и EMG/kinematics одного человека,
PeerJXLS17 человек,50sMRS blocks. Доступны pinned recipes/memberSHA256; raw
не публикуются, кроме явно лицензированного PeerJ XLS с атрибуцией. Дополнительный скачанный Diagnostics supplement содержит только PDF.
Dryad3450615 вновь 401/403, ни одной numericcell не получено.

Ни один полученный источник не содержит пригодный synchronized individual
PCr–continuousVO2–mechanicalW набор. PCr/mmol в plantar source использует
assumedATP8.2mmol/l,energy11points вычислена из PCr: это **не независимый cost**.
FigshareOCR — клеточный поток, не VO2 человека. PeerJload/WE не Wtimeseries.
Проверены PubMed/EuropePMC/PMC,Crossref,OpenAlex,Zenodo,Figshare,Dryad,OSF,
publisher и institutional leads; PhysioNetquery без подходящего результата.
Проверка ограниченная, отсутствие доступного jointdata не объявлено универсальным.

ExploratoryPCr fit нановых 2 людях — in-sample diagnostic, не validation:
при freeasymptoteτ31.7..32.5s у S2 и 77.3..85.9s у S1;forcedasymptote1 даёт
S1τ97.0..163.6s. Прямое наблюдение формы recovery возможно, но tau зависит
от asymptote/window/timing. Разница 87indices vs88expected и 217.5vs225s
не скрыта. Это не новая физиологическая оценкаτD2. W-MAE/RMSE/bias и новый
participant-level powertest не рассчитываются без соответствующих наблюдений.
Старые Werrors сохранены, новая test выборка не создана.

## Оптимальный virtual design — EXP-0021

GaussianFIM criterion выведен из likelihood, conditions описаны в MATHEMATICS.
8protocols:3/90s×6;6/12s×10;6/30s×10;6/180s×5;6/30s×10 с initial.35;
30/60s×5;15/45s×6 при 500W и 1800W. Остальные 1400W. Разные power series
сравниваются как отдельно начинающиеся trials; изменения demand внутри одной
непрерывной серии не моделируются. Initial.35 —known virtual input, не measured
human depletion. Active recovery не оптимизируется: в D2 нет независимо
оценённой cadence/rest-cost модели. Пассивный/rest-zero-demand сценарий не
объявляется эквивалентом activepedalling из SRC-0040.

Номинал и два corners(.8,1.2) совместно меняют обе capacity и recoveryτ.
Это ограниченный robustness audit, не покрытие всех physiologicaluncertainties.
В полном calibratedM5,11 параметров, по worst-caseD:
**30/60s →15/45s1800W →6/30s →6/12s**.
По worst-caseE: **6/30s →6/12s →30/60s →15/45s1800W**.
Остальные designs не имеют fullrank во всех corners и не получают determinant score.
Нормирование на 600s observation budget (без setup/reset cost) сохраняет лидеров,
но меняет третье/четвёртое D место. Это approximateinformationrate, не физический
план бесплатного восстановления. На общей 9D проекции дополнительно приведены
все 8 ранжирований, но не смешаны с full11 determinant.

В простом effective recurrence профиле knowntruthτ60s приσ=.02:
паузы 6/18s дают grid95support≈49..76s;90s —≈32..348s.
Длинная пауза почти стирает outputdecrement. Поэтому profile-design критерий
может предпочитать короткую паузу, тогда как D2 полная FIM предпочитает другой
баланс. Это зависимость отструктуры и endpoint, а не «лучший протокол» вообще.

## EXP-0022: шум, восстановление параметров и численная надёжность

Выполнены все 12 классов вычислительных проверок иззадания:

1. Аналитика +8protocol numericalchecks обеих exactsymmetries.
2. Независимо собранный Jacobian/SVD/FIM,condition/correlations,epsconvergence.
3.56protocol×measurementset audits,7combinedsets,calibrationnuisance test.
4. Multi-start nonlinear effective-recurrence recovery и 9combinationD2recovery.
5.σrelative0/.02/.05 и FIMnoise×.5/1/2,knownGaussian model.
6.MCAR10/30/50% sensitivity loss;30%missing nonlinearstress. Пропуски не imput ируются.
7.Sampling1/2/6/12s:common9Dλmin≈3.15/1.65/9.61e−5/0;12srank7.
8. Protocol rest timing+2s effective recurrence stress и cross-channel O/PCr lag .5/2/5s относительно power; сохраняются first-order logparameter bias и residualχ². Это не полноценный pulmonary delay estimator.
9.D/E/profile и 3cornerrobustdesign,channelsvs4repeats,observationduration correction.
10.9parameterquotient exactpowerparity и energybounds,nonlinearrecovery.
11.Unmodelledpotentiation/drift и AR1ρ.7whitening; commonλmin1.65→.59.
12.dt.5/.25/.125s идетерминированный replay/hashes. Work21712.33→21710.44→21709.49J,
rankcalibratedM5 остаётся 11. Discreteevents и recharge порождают residualdtbias.

36 effective-recurrence stress fits (6 условий×6draws,по 2starts):безшумаτ60s
восстановлена;σ.02 даёт 58.1..64.3s вконкретных draws;σ.05 —51.9..73.1s.
Потенциация.04 приσ.02 смещаетτдо 46.2..50.6s. Не строим coverageclaim из 6draws.

Девять D2combinations,3trainingvirtualdesigns,по 2starts на 4 условия: даже clean
optimizer завершилсяс maxparametererror≈1.2% при powerRMSE≈.015W. Это
**отрицательный результат практической оптимизации**, не доказательство ещё
одной точнойсимметрии: switching ималая чувствительность мешают inverse.
При 20Wnoise maxparametererror≈21.2%,powerRMSE≈2.08W;30%missing≈7.5%/2.37W
(один draw,не «пропускипомогают»);unmodelleddrift≈29.2%/9.49W.
Слабый parameterrecovery может сочетаться с accuratepower. Предсказательная
точность нановыхлюдях **не улучшена и не проверена**. Минимальный trainRMSE
не использовался длявыбора deployablemodel.

## Решение для TARGET-CPE45

Математическая неопределённость уточнена: две доказанные symmetries,9 честных
effectivecombinations,каналы икалибровки,способные ихразрушить,условные designs.
Эмпирически ниодинновый D2physiologicalparameter неидентифицирован. Новые
relativePCr наблюдения поддерживают анализ kinetics, но не whole-body2700sledger.
Дальнейшее научнообоснованноеулучшение — observationmaps и retrievable independent
measurements; увеличение 2700sperformance за счётподборакоэффициентовнеобоснованно.
CPE45 **NOT EXTERNALLY VALIDATED**,biologicalinterventions **NO_GO**,
архитектуры I/II/III безновогодоказанного 45min преимущества.

Следующийодинприоритет: **получить один same-participant synchronizedpower–
continuousVO2–PCr числовойнабор с independentmetabolic scale/baseline calibration**,
прежде чемфиксироватьновую participant-disjointvalidation. Сначалапроверить gain,
offset,activevolume и timing, затемобъявлять идентификацию.

## Воспроизведение

Python3.12,numpy2.5.4,scipy1.18.1,h5py3.15.1,xlrd2.0.2;matplotlib из requirements.
`PLAN.md` фиксирует computationalscope до analysis; это не humanvalidationprereg.
`configuration.json` —snapshot условий,immutablehistoricalenginebytehashes
в manifest. `verify.py` запускаетвсе Foundation/Integrated/measurementCPE45/
dynamicCPE45/Recovery suites,новые tests,numericreplay и sourceinspection.

```
python research/observability_2026_11_04/inspect_data.py --check
python research/observability_2026_11_04/test_observability.py
python research/observability_2026_11_04/audit.py --check
python research/observability_2026_11_04/verify.py
git diff --check
```

Дляпервоначальногопоиска:retrieve.py,затем audit_sources.py; это новыйснимок
изменяемых metadata,необычный replay. Для pinnednumericreplay неперезаписывать
retrieval.json:inspect_data.py --check скачиваетнужные publicbytes приотсутствии
cache ипроверяет memberhashes. В results —толькосинтетические outputs; в inventory —
наш derivedaudit.Исторические lockedtestfiles нетронуты. Итогпроверокв verification.json;
GitHubPR/CI/mainSHA проверяютсяпослепубликации,изсамогоэтогоотчётанеследуют.

Исправление воспроизводимости CI: после HTTP500 внешнего EuropePMC wrapper-сервиса точный PeerJ DataS3 XLS включён под подтверждённойCCBY4.0 с атрибуцией и проверкой пустыхNamefields. Остальные raw остаютсяignored. Добавлен19-йtest дляSHA256/пустыхNamefields. Научныеoutputs иисторическиелоки не менялись.

CI source replay limitation: run41871865726 also failed on a plantar archive read timeout. Main validation now explicitly checks retained licensed XLS content and archived source-audit hashes offline; it does NOT claim a fresh replay of unavailable raw. Manual workflow source-access.yml retains full live retrieval/content replay. Full content replay passed locally from obtained pinned cache. Scientific numeric replay remains mandatory.
