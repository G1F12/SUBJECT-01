# Предварительная фиксация анализа восстановления

Дата 04.11.2026; база c7a7c9caa7f619f64c88b9e0430a6b1f83148807.
Фиксируется до загрузки и чтения численных ячеек новых экспериментальных файлов.
Просмотрены описания доступности/методик Dryad08kprr59v и Frontiers692622,
но не новые raw measurements. Старый SRC-0035 целиком считается просмотренным.
Никакой старый участник не становится новым external test. Отрицательные EXP11..14
и их файлы неизменны. Протокол будет закреплён отдельным Git commit до extraction.

## Включение, разделение и остановка

- Принимаются открытые лицензированные реальные индивидуальные PCr recovery
  или повторные мощности с явными effort/rest, time units и participant key.
- Чужие агрегаты, цифры из графиков и synthetic controls не выдаются за raw people.
- Все условия/сессии одного участника принадлежат одному group. Если ключ
  сопоставления неясен, не делить условия между training/test; набор исключается
  из independent-participant efficacy claim.
- Пропуски остаются пропусками. Для power prediction требуется первый baseline;
  для PCr известные baseline и recovery origin, без экстраполяции неизвестного времени.
- При ≥12 достоверных участниках: сортированный ID, каждый третий — locked test;
  остальные — development. Выбор формы/гиперпараметров только grouped leave-one-
  participant-out CV внутри development. При 4..11 — nested grouped CV, без
  заявления об отдельном внешнем test. При <4 — только individual/session/temporal
  diagnostics, NOT EXTERNALLY VALIDATED по участникам.
- Внешний test открывается отдельной командой только после lock выбранной модели,
  её параметров и хэша training inputs. Не подстраивать модель после результата.
- Если совместные PCr–VO2–power отсутствуют в самих файлах, состояние всей системы
  не идентифицируется. Продолжаются подсистемные эксперименты; отсутствие данных
  не заменяется синтетическими наблюдениями и не маскируется большим числом прогонов.

## Заранее выбранные сравнения и метрики

D1: неизменённый historical cycling_shape(rate=0), старые прогнозы и RMSE.
D2: rate-limited paid-recovery physical ledger с разделением мощности release
от энергетической ёмкости; неизвестные параметры исследуются как сценарии,
а не одновременно подгоняются по одной мощности.
D3: constant; signed linear episode response; monoexponential recovery/response.
Для PCr: fixed baseline100%, observed initial depletion, одна tau (s), диапазон
1..600s; расширенная amplitude+tau — диагностическая альтернатива, не автоматический
победитель. Для power: baseline-conditioned shape; никакого fit будущего baseline.
D4: эмпирическая recovery tau внутри D2 только если однозначно оценивается на
своих development data; совместный physiological transfer остаётся условным.

RMSE — primary; MAE, signed bias, recovery error, participant errors, calibration
intercept/slope — secondary. Только одинаковые observed cells, first baseline не
входит в scoring. Bootstrap участников (2000, seed20261104); при одном человеке
participant CI не вычисляется. Temporal validation допускается, но не называется
participant validation. Для single-person повторных PCr sessions: первая сессия
development, последующие — locked session tests; unknown same-day carryover noted.

Численная верификация: energy residual ≤1e-6 относительной энергии и ≤1e-4J
абсолютного floor, резервы bounded, recharge paid; dt halving, adversarial cases,
2700s stability. Идентифицируемость: finite-difference Jacobian/SVD (relative
threshold1e-6), профили SSE с явной noise assumption; exact symmetry проверяется
аналитически. Synthetic parameter recovery — только software control.

Успех: установленный механизм ошибки или доказанная неидентифицируемость также
принимаются. Архитектуры I/II/III не пересчитываются как улучшение человека при
неподтверждённом переносе. CPE45 not_assessed, NO_GO неизменны.
