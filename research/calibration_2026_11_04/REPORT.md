# Cycle 6 — physiological calibration без ложного локального масштаба

Результат: получен независимый **системный** metabolic anchor и ограниченная
проверка systemic-cost predictor. Локальные энергетические параметры D2 не
калиброваны. TARGET-CPE45 — **NOT EXTERNALLY VALIDATED**, interventions **NO_GO**.
Новые состояния и преимущества архитектур I/II/III не вводились.

## Реальные данные и протокол

EXP-0023: фактически получены 135 CPET CSV Lendt (66 cycling participants),
17 VO2 CSV WEEE и один CPET BUT-CGM (531 строка). Подробности/лицензии,
точные файлы и blockers в DATA_AUDIT.md. Это три отдельные выборки, не83/84
синтетических совместных людей. Нового joint PCr с абсолютной active mass нет.

Preregistration опубликована commit0446eaadcecb7c4ebea3613d20527a6d3fd94897
до чтения новых CPET outcomes. Test IDs n%5==0, все trials человека вместе.
Model/code/development/source lock опубликован
726772fd50a5e13ea6c71f211dee500f16b4a676 до открытия test. Эти commits доступны
в истории PR. 51 development person/216 eligible stages; 13 новых test people/
56 identical eligible stages. Model selection только development participant LOPO.
Одна итоговая test evaluation; дальнейший replay проверяет фиксированный результат
во временной директории без настройки и без перезаписи locked outcome.

## Идентификация

EXP-0024: условная systemic affine карта E=a+bP даёт a=153.853W,
b=3.64333W/W, effective δeff=.274474. Participant-bootstrap95%:
a[144.176,163.828]W, b[3.55988,3.72523], δeff[.268440,.280908]. Это
статистические интервалы условной карты, без неизвестной ошибки прибора и
транспорта. Нельзя назвать a локальным M или δeff физиологическим ηD2.
51 per-person affine fits,45 с конечным положительным efficiency interval,
6 недостаточно определены. 51 pulmonary onset fit,30 конечных conditional τ
profiles и21 boundary/flat. Эти τ — EFFECTIVE ONLY, не PCr recovery или
mitochondrial capacity. Все FIM/SVD/correlation/profile/multistart outputs
сохранены. Gaussian/profile coverage условно; первичная uncertainty стоимости
учитывает участников, а не выдаёт breaths за независимых людей.

MEASURED: лёгочный VO2/VCO2 и recorded prescribed load. IDENTIFIED: только
условные эмпирические systemic coefficients. EFFECTIVE ONLY: gas-derived cost,
δeff, pulmonary τ. BOUNDED: WEEE cost при принятом RER range. UNIDENTIFIABLE:
ηD2,Cf,Cs,Lf,Ls,Q,M,recharge efficiency/recovery constants. NOT OBSERVED в новых
cohorts: PCr/ATP/Pi/pH/active muscle volume/MVC/twitch. Ни одна из девяти D2
комбинаций не получает здесь нового физиологического измерения.

## Независимая проверка ограниченного endpoint

EXP-0025: endpoint — системная стоимость заданной ступени в W, не output power.

| Predictor | RMSE W | MAE W | bias W |
|---|---:|---:|---:|
| Constant |135.40|113.74|−2.96|
| Affine |26.40|21.64|+.48|
| Quadratic, selected до test |26.56|22.29|+.58|
| Measured-posture baseline + slope |29.72|24.77|−10.47|
| Fixed historical D2 equilibrium observation hypothesis |40.58|35.02|−30.90|

Selected quadratic RMSE95%[20.42,33.73]W; paired participant-bootstrap difference
vs constant[−125.33,−90.21]W, vs historical equilibrium[−23.93,−1.26]W.
Заранее установленный критерий ограниченного улучшения выполнен. Affine чуть
лучше test, winner после просмотра не меняется; преимущество quadratic над
affine не заявляется. Selected calibration slope .98043, intercept8.44W;
constant calibration rank1, сохранённые minimum-norm coefficients не имеют
раздельного смысла. Полные participant errors и uncertainty в independent_test.json.

Historical comparator — фиксированная равновесная гипотеза systemic=local
M+P/η, а не новый прогон неизменённого sprint D2 по подходящему power endpoint.
9D reduced power model не задаёт absolute systemic cost: NOT DEFINED, без
искусственного η=1. Поэтому новой общей five-model power validation **нет**.
Старые negative RMSE126.54/361.71W воспроизведены, не переоценены на новую
независимость. Старые10+7 и новые13 test people теперь просмотрены.

## Фальсификация и метрология

EXP-0026: VO2 gain±10% меняет effective δeff .2980↔.2544, намного шире
условного bootstrap interval. VO2 offset±.1L/min сдвигает intercept±27.196W,
не slope. Неизвестные gain/offset дают ранг2 из4 observation parameters.
Сдвиг окна +5s оставляет155 вместо216 eligible stages, +15s только20:
экспортные разрывы не восполняются интерполяцией. Изменение оценок при этом
не является физиологическим эффектом. Active volume×.5/2 и ATP reference±20%
проверены как алгебраические факторы метрологии, не придуманные human records.

Проверены interindividual variation, task mismatch, nonaffine discrepancy,
incomplete recovery и active rest. Только один development recovery window
не позволяет оценить population recovery. BUT-CGM cooldown75W опровергает
его интерпретацию как пассивного отдыха. Неизмеренный transport/local allocation
сохраняет обе D2 ambiguities. Плоский профиль означает недостаток информации,
а не отсутствие физиологического процесса. Две exact symmetries не опровергнуты.

## Решение

A — REAL METABOLIC ANCHOR FOUND только whole-body gas scale;
B — PHYSIOLOGICAL PARAMETER IDENTIFIED не присваивается локальным D2 параметрам;
C — INDEPENDENT VALIDATION PASSED только systemic-cost predictor, не CPE45;
D — PARTIAL IDENTIFICATION и E — EMPIRICAL ACCESS BLOCKER для локальной модели.
Historical systemic=local equilibrium transfer существенно недооценивает cost;
это ограниченный отрицательный результат, не универсальное опровержение D2.

Честный baseline остаётся 9D quotient плюс отдельно обозначенная systemic
observation layer. Масштаб/размерности SI, positivity, paid recovery и energy
conservation проверяются неизменённым engine. Новые данные приближают метрологию,
но не позволяют научно обоснованно улучшить прогноз 2700s мощности.

Следующий приоритет: получить на одних людях синхронные PCr–VO2/VCO2–W с
независимым active-volume/absolute-reference и local-baseline calibration;
BUT-CGM можно использовать для отдельного будущего preregistered transport audit,
не выдавая его за недостающий PCr anchor.
