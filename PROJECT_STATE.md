# SUBJECT-01 — состояние после Research Cycle 6, 04.11.2026

База a4d3a04ab8ef0fc056815989f4b775cf9773f3ca; ветка research/metabolic-anchors-20261104.
[Отчёт EXP-0023..0026](research/calibration_2026_11_04/REPORT.md),
[метрология](research/calibration_2026_11_04/DATA_AUDIT.md),
[reproduction](research/calibration_2026_11_04/README.md).

Получены реальные CPET VO2/VCO2/W:66cycling people Lendt, отдельный WEEE17VO2
и BUT-CGM1 exploratory person. CC BY4, native memberSHA, без публикации raw.
Независимый системный gas scale найден, localATPscale/localbaseline не найдены.
Условные systemic a153.853W,b3.64333W/W, effectiveδeff .274474 не равны D2M/η.
51development/216stages, published lock726772f; новые13test/56stages:
selectedquadratic RMSE26.56W vs constant135.40W vs historic equilibrium40.58W.
Ограниченная systemic-cost validation прошла; это не power/CPE45 validation.
9D quotient сохранён. Localparams не идентифицированы; pulmonaryτ30finite/51fits
только effective. Gain/offset/timing/volume остаются существенными.
Старые10+7 и новые13test просмотрены, повторное независимое claim запрещено.
TARGET-CPE45 NOT EXTERNALLY VALIDATED; interventions NO_GO; архитектуры без новых преимуществ.
Реестры EXP26/FND28/NEG20/DEC11/ISS17/SRC55. История Cycle5 ниже сохранена.

---

# SUBJECT-01 — состояние после Research Cycle 5, 04.11.2026

Канон: публичный G1F12/SUBJECT-01. База цикла:
4e900fbb337cf59efff8b75f473528485c7cc045. Ветка:
research/observability-design-20261104. Итоговый mainSHA проверяется через
GitHub/remote после PR и CI, не выводится из этой записи.

[Отчёт EXP-0019..0022](research/observability_2026_11_04/REPORT.md),
[формулы](research/observability_2026_11_04/MATHEMATICS.md),
[матрица](research/observability_2026_11_04/OBSERVABILITY_MATRIX.md),
[данные](research/observability_2026_11_04/DATA_AUDIT.md).

- Решение A/C/D: условное улучшение observability, девятипараметрическая
  редукция D2 и точный экспериментальный блокер. B не достигнут.
- Две D2 power-симметрии: η/metabolic scale и additive oxidative baseline.
  Power-only и relativePCr не определяют абсолютные η,Ci,Q,M.
  Инварианты ηCi,ηLi,η(Q−M),τfast,τslow,e,τoxygen сохраняют всю мощность.
- Богатые virtual traces: M1/M3 rank9/11, M4 rank10/11; M2/M5/M6/M7energy11/11
  только при известной абсолютной localO calibration и observation map.
  UnknownVO2gain возвращает scale ambiguity. Это не ранги человеческих данных.
- Full calibrated M5 finite-grid robustD предпочитает 30/60s, E —6/30s.
  Sampling12s теряет направления. Exact quotient power parity<1.6e−11W.
  Низкая ошибка мощности не гарантирует recovery параметров: даже clean
  nonlinear inverse имеет 1.2% maxparametererror; drift/noise ухудшают recovery.
- Реально получены и прочитаны: Figshare relativePCr2 людей/6scans/522cells;
  plantarflexionMAT1 человек/144MRSpoints; PeerJXLS17 людей/50sblocks.
  Joint synchronized PCr–continuousVO2–mechanicalW не получен. PCr_mmol_l
  с assumedATP8.2mmol/l и PCr-derivedenergy не независимые metabolic anchors.
  Dryad повторно 401/403. Raw ignored, кроме лицензированного PeerJ XLS; pinnedURL/memberSHA/recipes в Git.
- Новые exploratoryPCr fits только in-sample; неизвестная asymptote меняетτ.
  Ни один новый D2 physiological coefficient не установлен на людях.
- Foundation/Integrated/CPE45/Recovery артефакты и lockedtestresults сохранены.
  Старый RMSE378.543770W воспроизведён. Recovery constant126.54W,D2361.71W,
  mono118.29W без подтверждённого преимущества. Старые 10 и 7test просмотрены,
  не используются для новой настройки или independent improvement claim.
- Все прежние 96unit tests и 19 новых, historical replays, hashes, source-content
  check и Cycle5 numeric replay включены в verify.py/Actions. Фактические
  exitcodes: research/observability_2026_11_04/verification.json.

Реестры: EXP22/HYP6/FND24/NEG15/DEC10/ISS16/SRC49. HYP unverified.
ISS-0011/0014 открыты; ISS-0016 — calibration/locality/timing maps.
CPE45 NOT EXTERNALLY VALIDATED, TARGET-CPE45 not_assessed,
биологические вмешательства NO_GO. Архитектуры I/II/III не получают новых
доказанных преимуществ на 2700s.

Один следующий приоритет: доступный same-participant synchronizedpower–
continuousVO2–PCr набор с независимой scale/baseline calibration до новой
preregistered participant-disjoint validation.
