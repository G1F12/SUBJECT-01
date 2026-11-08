# SUBJECT-01 — состояние после Research Cycle 7 (Final Consistency Audit), 07.11.2026

База f8e6761d5f58e71ff8bdf304741414d974359d8a; merge 9157ba75efbe7b24ab2fcbd3b4c21f978cec67e8;
ветка correction/cycle7-final-consistency-20261107.
[Отчёт EXP-0027..0031](research/local_muscle_bridge_2026_11_07/REPORT.md),
[математика и симметрии](research/local_muscle_bridge_2026_11_07/MATHEMATICS.md),
[модель измерений](research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md),
[ограничения и протокол отзыва](research/local_muscle_bridge_2026_11_07/LIMITATIONS.md),
[reproduction](research/local_muscle_bridge_2026_11_07/README.md).

Финальный аудит согласованности и устранение расхождений:
- Устранены числовые противоречия между отчётом и кодом: чувствительность асимптоты строго [-22.9%, +20.9%] (точно: -22.867%..+20.862%); смещение от гетерогенности волокон строго 10.6% (точно: 10.5996%); детерминированный сценарный диапазон паразитарных затрат строго 42.8%-77.1% (номинал 66.3%). Термин «доверительный интервал» исключён.
- Неверифицированные эмпирические заявления R2=0.919, R2=0.978 и наклон регрессии «14 с / 0.1 pH» ОТОЗВАНЫ как артефакты ручной графической оцифровки Fig 3-5. Восстановлены рецензированные литературные результаты Moll et al. 2017: R2=0.73 (p<0.005, n=10) для tau_PCr vs pH; R2=0.55 (p=0.01, n=10) для tau_VO2 vs tau_PCr; R2=0.65 (p<0.01, n=9) для excess CO2 vs pH.
- Изоляция исследований: данные Cannon et al. 2014 Table 1 (PMC4262339) получены на четырёхглавой мышце при bilateral knee extension (двустороннее разгибание коленей) и качественно доказывают преобладание окислительного ресинтеза (88-95%) над гидролизом PCr (1.5-3.0%); количественные скорости оборота (мМ/мин) не переносятся на икроножную мышцу когорты Moll без калибровки.
- В EXP-0030 отношение 0.44-1.50 обозначено диагностическим артефактом неполного энергобаланса и занижения активного объёма, а не физиологически допустимым КПД.
- EXP-0031 ОТОЗВАН: заявление о превосходстве локальной модели по RMSE 0.65 Вт аннулировано из-за захардкоженных прогнозов, in-sample константы и выборки N=2.
- Параметры D2 не объявляются идентифицированными через наблюдение коррелятов в мосту; математические тесты рангов не объявляются физиологической валидацией на людях.

Математический анализ идентифицируемости и симметрий:
- Симметрия 1 (масштаб энергии c·E_met и η/c) сохраняется точно: RSS профильного правдоподобия плоский до <1.5e-32. Относительный PCr (ratio) не фиксирует абсолютный масштаб в Джоулях без активного мышечного объёма V_active и абсолютной концентрации [PCr].
- Симметрия 2 (аддитивный сдвиг окислительного расхода Q_ox+Δ и фонового обмена M_tot+Δ) сохраняется точно: RSS плоский до <7.5e-32. Системный VO2 включает немышечный/паразитарный метаболизм (42.8-77.1%) и не фиксирует локальный фоновый расход M_loc.
- FIM трёхслойной модели: подтверждена коллинеарность задержки кровотока и тканевой tau (r=-0.709, cond=6.89).

Итоги проверенных вычислительных экспериментов (EXP-0027..EXP-0031):
- EXP-0027: Литературный бенчмарк R2=0.73 (Moll 2017). Вычислительно подтверждено: ошибка асимптоты покоя +/-5% даёт [-22.9%, +20.9%] искажения tau; гетерогенность NMES даёт до 10.6% смещения.
- EXP-0028: 4 компонента задержки (магистраль 2.08 с, дисперсия 0.31 с, кровоток 10-20 с, активация 20-40 с). Коллинеарность r=-0.709 подтверждена.
- EXP-0029: Литературные связи R2=0.55 и R2=0.65 подтверждены. Сценарный паразитарный расход 42.8-77.1% (номинал 66.3%).
- EXP-0030: Буфер PCr 204.8-1021.4 Дж (размах 4.99). Оборот ATP Cannon 2014 (knee extension): окисление 88-95%, PCr 1.5-3.0%.
- EXP-0031: ОТОЗВАН (RETRACTED_INVALID_COMPARISON). Превосходство локальной модели не подтверждено.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=13, ISS=18, SRC=62.
- Тесты: 153/153 PASS. История Cycle 6 сохранена ниже.

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
