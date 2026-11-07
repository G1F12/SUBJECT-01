# SUBJECT-01 — состояние после Research Cycle 7, 07.11.2026

База f8e6761d5f58e71ff8bdf304741414d974359d8a; ветка research/local-muscle-bridge-20261107.
[Отчёт EXP-0027..0031](research/local_muscle_bridge_2026_11_07/REPORT.md),
[математика и симметрии](research/local_muscle_bridge_2026_11_07/MATHEMATICS.md),
[модель измерений](research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md),
[ограничения](research/local_muscle_bridge_2026_11_07/LIMITATIONS.md),
[reproduction](research/local_muscle_bridge_2026_11_07/README.md).

Построен трёхслойный измерительный мост: Механическая мощность -> Локальная мышечная энергетика -> Системный газообмен.
Получены и оцифрованы реальные синхронные данные человека:
- Moll 2017 (SRC-0056) / Moll 2018 (SRC-0057, 163-стр. диссертация DBT, 11.1 МБ, SHA256 82e1d09d...): 10 парных участников с синхронными 3T localized ³¹P-MRS (TR=5 с), спироэргометрией (PowerCube, ta=2.075 с, t10-90=0.307 с) и калиброванной подошвенной механикой (15.5 Вт и 21.8 Вт); 21 атлет (11 спринтеров vs 10 стайеров); 8 участников NMES (3-fold Pi splitting).
- Cannon 2014 (SRC-0058): закрытый полнотекстовый доступ, открытых числовых рядов нет (REQUEST_REQUIRED).
- Дополнительные источники: Rossiter 2002 (SRC-0059), Ryan 2014 (SRC-0060), Zenodo (SRC-0061, SRC-0062).

Математический анализ идентифицируемости и симметрий:
- Симметрия 1 (масштаб энергии c·E_met и η/c) сохраняется точно: RSS профильного правдоподобия плоский до <1.5e-32. Относительный PCr (ratio) не фиксирует абсолютный масштаб в Джоулях без активного мышечного объёма V_active и абсолютной концентрации [PCr].
- Симметрия 2 (аддитивный сдвиг окислительного расхода Q_ox+Δ и фонового обмена M_tot+Δ) сохраняется точно: RSS плоский до <7.5e-32. Системный VO2 включает немышечный/паразитарный метаболизм и не фиксирует локальный фоновый расход M_loc.
- Ранги FIM: механический слой M1 — rank 1/1; локальный M2 — rank 2/2; системный M3 — rank 2/2; сквозной калиброванный мост M4 — rank 5/5. При неизвестных калибровочных параметрах rank падает до 3/5.

Ключевые экспериментальные результаты (EXP-0027..EXP-0031):
- EXP-0027: Кинетика PCr строго связана с ацидозом: R² = 0.919, p = 1.23e-05 между end-exercise pH и τ_PCr; падение pH на 0.1 удлиняет τ на ~14 с. Ошибка асимптоты покоя ±5% искажает τ на -17.8%..+26.4%. Моноэкспоненциальный фит гетерогенной мышцы даёт до 11.4% смещения.
- EXP-0028: Транспортная кардиопульмональная задержка и тканевая постоянная времени окисления сильно коллинеарны в легочных on-transients (r = -0.704).
- EXP-0029: Доказана статистически значимая связь между локальной τ_PCr,fast и легочной τ_VO2,fast (R² = 0.55, p = 0.01) и между excess CO2 и pH (R² = 0.65, p < 0.01). При подошвенном сгибании 18 Вт доля немышечного паразитарного расхода в системном приросте VO2 составляет 66.3%.
- EXP-0030: Неопределённость активного объёма мышцы (0.15-0.40 л) и референтного пула PCr создаёт 4.99-кратный диапазон абсолютного запаса энергии (205-1021 Дж) и эффективного КПД (0.11-0.52).
- EXP-0031: Калиброванный локальный мост даёт RMSE 0.65 Вт против константы 3.15 Вт; неадаптированная модель D2 всего тела даёт RMSE 431.36 Вт. Мост является диагностической наблюдательной моделью, а не автономным предиктором механической мощности.

Ответы на три главных вопроса цикла:
- Вопрос A: Локальная стоимость сокращения НЕ может быть определена однозначно из PCr, VO2 и работы без независимого измерения активного анатомического объёма мышцы V_active и разделения паразитарного системного VO2.
- Вопрос B: Для устранения Симметрии 1 необходимы измерения V_active (напр. T2*-MRI) и референтного пула [PCr] в Дж; для Симметрии 2 — прямое измерение локального изолированного покоящегося обмена M_loc (напр. венозная окклюзия / артериовенозная разница).
- Вопрос C: Доступные данные улучшают проверяемость модуля CPE45, ограничивая допустимые постоянные времени ресинтеза (τ_rec ≥ 20-30 с) и запрещая предположения о мгновенной перезарядке, но TARGET-CPE45 остаётся NOT EXTERNALLY VALIDATED.

Биологические вмешательства: NO_GO.
Преимущества архитектур I/II/III на 2700 секундах: NOT DEMONSTRATED.
Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=12, ISS=18, SRC=62.
История Cycle 6 и Cycle 5 сохранена ниже.

---

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
