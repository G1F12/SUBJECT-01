EXP-0132 / FND-0128 / NEG-0112 / DEC-0033: Проведён сквозной аудит пяти модулей Архитектуры A в единых физических условиях. Сформулирован однозначный ответ: НЕТ, НА ТЕКУЩЕМ УРОВНЕ ДОКАЗАТЕЛЬНОСТИ НЕ ПОДТВЕРЖДЕНО; УСЛОВНЫЙ ПОТЕНЦИАЛ ОСТАЁТСЯ НА WHOLE-SYSTEM HOLD (status = "CONDITIONAL_POTENTIAL_WHOLE_SYSTEM_HOLD", verdict = "NOT_CONFIRMED_PENDING_DECISIVE_MEASUREMENTS"). Зафиксированы раздельные вердикты: TARGET-FORCE20 (NOT_CONFIRMED_PENDING_POSTURAL_AND_DYNAMIC_SAFETY_DATA: при 100° исправленный выигрыш +21,93%, но динамический энтезис SF=1,285 < 1,50; при 140° выигрыш +21,77% и SF=1,747 >= 1,50, но градиент угла 28–41 Н/град создаёт артефакт 410 Н при 10° ошибки, а наивная база точнее модели 110° на 148 Н MAE); TARGET-ADAPT25 (RATE_ACCELERATION_UNASSESSED_PENDING_CONTROL_COHORT: когорта Santos без контроля, +18,35% к 14-му дню — внутригрупповой рост, ускорение темпа относительно контроля не оценено; порог SF0 >= 1,776 — аналитическое свойство ODE без in vivo измерений ткани); TARGET-CPE45 (VALIDATED_ONLY_UNDER_INTERMITTENT_WORK_REDUCTION: непрерывные 360 Вт невозможны из-за перегрева, прерывистый режим D=0,59–0,92 снижает механическую работу с 972 кДж до 619–902 кДж на 7–36%; CV=2,1% и COP<=0,045 м являлись синтетическими литералами, а восстановление 98,3% получено после 3 подходов жима ~4 кДж, не 2700 с). Совместная совместимость в едином непротиворечивом состоянии не достигнута. Зафиксированы 4 операционные границы и 3 решающих измерения. См. research/architecture_a_integration/ARCHITECTURE_A_EVIDENCE_SYNTHESIS_REPORT.md.

EXP-0131 / FND-0127 / NEG-0111 / SRC-0086, SRC-0090: 4-слойный солвер Пеннеса верифицирован на 23 участниках 45-минутного велоэргометрического теста в тепле McLaughlin et al. (MAE 0,586 °C против 1,275 °C у базы сохранения, парная разность +0,689 [0,501; 0,865] °C в пользу Пеннеса); доказана невозможность непрерывной работы при 360 Вт (перегрев >39,5 °C во всех климатах >= 20 °C) и доказана реализуемость 2700 с CPE45 при прерывистом квантовании нагрузки (D <= 0,92 при 20 °C, D <= 0,65 при 32 °C/80% RH); подтверждено, что наблюдаемый прирост силы (+18,35% к 14-му дню) не создает дефицита запаса ткани при физиологическом резерве SF0 >= 1,776 (0 дней дефицита). См. research/program_evidence_audit/LINK3_ADAPT25_CPE45_REPORT.md.

EXP-0130 / FND-0126 / NEG-0110 / SRC-0111, SRC-0102, SRC-0086: на удержанных участниках Norbury et al. линейная модель по нагрузке статистически проигрывает тривиальной базе сохранения (MAE 54,69 против 50,61 Н; разность −4,08 [−8,49; −0,29] Н при спаренном бутстрэпе); в de Poli et al. рост работы на +11,1% сопровождался ростом удержания силы (+3,72 п.п.), окончательно опровергая скалярные уравнения истощения силы; на данных McLaughlin et al. показано выполнение сотен килоджоулей (270–810 кДж) в умеренном домене без отказа в отличие от отказа при ~70 кДж в надкритическом домене de Poli. Установлена необходимость 4-компонентной кандидатной структуры перехода (DEC-0032). См. research/program_evidence_audit/LINK2_WORK_RECOVERY_REPORT.md.

EXP-0129 / FND-0125 / NEG-0109 / SRC-0090, SRC-0081, SRC-0089, SRC-0085: внешняя когорта Zöger et al. заблокирована по статусу запроса (REQUEST_ONLY_BLOCKED); на когорте Santos et al. модель при 110° имеет положительное смещение +463,2 Н (MAE 613,6 против 458,8 Н у базы F0=2500 Н); угловая чувствительность (28–41 Н/град, артефакт ~410 Н при 10°) сопоставима с целевым порогом +20%; на DPValid сравнение M2 против антропометрической базы F0 неопределённо (ΔR² = +0,0735 < 0,08); перенос моментов приседаний Scherpereel заблокирован неопределённостью единиц ISS-0028; квазистатический запас сухожилия SF = 2,05 >= 1,50 соблюдён при 4800 Н, но баллистический рекрутинг (20 000 Н/с) снижает локальный запас энтезиса до SF = 1,31 < 1,50. См. research/program_evidence_audit/LINK1_FORCE_TISSUE_REPORT.md.

EXP-0128 / FND-0124 / NEG-0108 / SRC-0090: на реальной 6-недельной продольной траектории силы 10 участников Santos et al. средний прирост силы к 14-му дню составил +18,35% (с 2525,2 до 2988,6 Н). Моделирование при нормативном SF0=1,50 и задержке 14 дней дает расчетное падение запаса прочности до SF = 1,267 (когорта) и 0,938 у быстрых респондентов с 4,15x ростом множителя повреждения. Анализ чувствительности показал, что данный дефицит предопределен допущением SF0=1,50 и полностью снимается при физиологическом резерве SF0 >= 1,776 (0 дней ниже 1,50 за все 42 дня). Неподтвержденные тезисы об эмпирически доказанном ограничении синтезом коллагена и невозможности естественного ускорения сняты. См. research/program_evidence_audit/ADAPT25_TISSUE_TRAJECTORY_REPORT.md.

EXP-0127 / FND-0123 / NEG-0107 / DEC-0032 / SRC-0102, SRC-0111: на удержанных участниках Norbury et al. при спаренном бутстрэпе по ID участника (условия LL и HL вместе) модель остаточной силы по нагрузке уступает тривиальной базе сохранения (MAE 54,69 против 50,61 Н; разность «база минус модель» −4,08 [−8,49; −0,29] Н, строго в пользу базы); в de Poli et al. по опубликованным групповым данным таблицы 3 рост работы на +8,5–11% сопровождался ростом удержания силы (+3,72 п.п.), опровергая скалярное истощение. Прямое сопряжение силового и энергетического модулей отклонено (DEC-0032, NO-GO); 4-компонентная модель перехода обозначена как кандидатная структура, требующая собственной эмпирической валидации (ISS-0032). См. research/program_evidence_audit/WORK_FORCE_TRANSITION_REPORT.md.

EXP-0126 / FND-0122 / NEG-0106 / SRC-0090: аудит когорты Santos et al. квалифицирован как диагностическая оценка при угле колена ~110° (номинальная модель 110° имеет смещение +463,2 Н, MAE 613,6 Н против 458,8 Н у базы F0=2500 Н); сопоставление моделей 100° и 140° с данными 110° оформлено как проверка чувствительности к несовпадению углов (градиент 28–41 Н/град, смещение угла на 10° создает артефакт ~410 Н, сопоставимый с TARGET-FORCE20). Двухфакторная ANOVA отделила систематический тренировочный прогресс (+18,35% к W2, SS=1,60e6) от случайной ошибки (детрендированное Sw=309,1 Н против наивного 385,7 Н), разграничив многонедельный биологический дрейф и чистую инструментальную test-retest повторяемость (ISS-0036). См. research/program_evidence_audit/FORCE_TRANSFER_RELIABILITY_REPORT.md.

EXP-0125 / FND-0121 / NEG-0105 / SRC-0114: у 30 мужчин добавление момента туловища к FFM не показало определённого улучшения прогноза пиковой веломощности; смысл работы в одном ряду требует уточнения (ISS-0032). См. research/program_evidence_audit/LUMBAR_ISOKINETIC_REPORT.md.

EXP-0124 / FND-0120 / NEG-0104 / SRC-0113: в 62 посленагрузочных файлах точного хвата повторяется один и тот же числовой ряд у 16 участников и обеих рук; анализ эффекта заблокирован до уточнения происхождения (ISS-0040). См. research/program_evidence_audit/PRECISION_GRIP_REPORT.md.

EXP-0123 / FND-0119 / NEG-0103: единый знак и задержка скорости не проходят проверку на участниках; у всех 21 архивных записей предпочтительные знаки двух условий противоположны, привязка к сторонам не подтверждена (ISS-0032). См. research/program_evidence_audit/PLANTAR_VELOCITY_REPORT.md.

EXP-0122 / FND-0118 / NEG-0102 / SRC-0112: открытый архив момента, угла, скорости и силы; 21 запись против 20 участников статьи и расхождение интегралов блокируют оценку работы (ISS-0032). См. research/program_evidence_audit/PLANTAR_WORK_GATE_REPORT.md.

EXP-0121 / FND-0117 / NEG-0101 / SRC-0111: парные изменения силы колена после двух свободных условий жима неопределённы; объём кг-повторов не является работой в джоулях (ISS-0032). См. research/program_evidence_audit/NORBURY_FORCE_RECOVERY_REPORT.md.

EXP-0120 / FND-0116 / NEG-0100: условное восстановление скорости меняет абсолютные пики и величину ранне-позднего спада мощности; физически ни один метод не подтверждён (ISS-0039). См. research/program_evidence_audit/LCMJ_POWER_SENSITIVITY_REPORT.md.

EXP-0119 / FND-0115 / NEG-0099: условная разность скорости разложена на вклад detrend и фильтра; начальная сила 1,59–1,85 от Weight*g, полная масса неизвестна (ISS-0039). См. research/program_evidence_audit/LCMJ_FILTER_DECOMPOSITION_REPORT.md.

EXP-0118 / FND-0114 / NEG-0098: проверка 220 фаз полёта показала условное расхождение изменения восстановленной скорости с −gΔt; усилия направляющих и полная масса неизвестны (ISS-0039). См. research/program_evidence_audit/LCMJ_FLIGHT_REPORT.md.

EXP-0117 / FND-0113 / NEG-0097: 10 исходных и 10 обработанных рядов прыжков совпадают, обработка 0,25 Гц воспроизводится для всех десяти; один XLSX, частота сбора и масса остаются открыты (ISS-0039). См. research/program_evidence_audit/LCMJ_ARCHIVE_OVERLAP_REPORT.md.

EXP-0116 / FND-0112 / NEG-0096 / SRC-0110: для одной пары архивов сырой сигнал силы совпал, а мощность воспроизведена фильтром 0,25 Гц; 500 Гц экспорта и 1000 Гц статьи требуют пояснения (ISS-0039). См. research/program_evidence_audit/LCMJ_RAW_MATCH_REPORT.md.

EXP-0115 / FND-0111 / NEG-0095 / SRC-0109: в частично просмотренной когорте 10 человек преимущество LOPO-прогноза спада мощности по силе и спринту перед средним не установлено. См. research/program_evidence_audit/LCMJ_PREDICTORS_REPORT.md.

EXP-0114 / FND-0110 / NEG-0094 / SRC-0108 / ISS-0039: 11 рядов повторных прыжков прошли гейт событий; поздняя расчётная пиковая мощность ниже ранней, но фильтр и происхождение мощности не установлены. См. research/program_evidence_audit/LCMJ_SOURCE_GATE_REPORT.md.

EXP-0113 / FND-0109 / NEG-0093 / SRC-0106–0107: опубликованы групповые сила жима и мощность прыжка после велосипедных интервалов и отдельная повторяемость жима; индивидуальная работа не получена. См. research/program_evidence_audit/LEG_PRESS_HIIT_REPORT.md.

EXP-0112 / FND-0108 / NEG-0092 / SRC-0105: индивидуальные повторы силы бедра у 25 велосипедистов показывают изменения ≥20% в части случаев; перенос на жим не установлен (ISS-0036). См. research/program_evidence_audit/HIP_RELIABILITY_REPORT.md.

EXP-0111 / FND-0107 / NEG-0091 / SRC-0104 / ISS-0038: опубликованы совместные групповые сила и управление усилием после нагрузки; архив по ссылке статьи не содержит индивидуальных данных. См. research/program_evidence_audit/FORCE_CONTROL_SOURCE_REPORT.md.

EXP-0110 / FND-0106 / NEG-0090 / SRC-0103 / ISS-0037: открытый архив STS v2 содержит две пары идентичных файлов; соответствие обработанных строк и людей не установлено. См. research/program_evidence_audit/STS_ARCHIVE_AUDIT_REPORT.md.

EXP-0109 / FND-0105 / NEG-0089 / SRC-0102: найдено исследование работы на велоэргометре и силы колена в одной когорте; индивидуальные данные по запросу и равная абсолютная работа не подтверждены. См. research/program_evidence_audit/DE_POLI_FORCE_WORK_REPORT.md.

EXP-0108 / FND-0104 / NEG-0088: в постфактум сценариях разделённого спроса исход существенно зависит от неизмеренной способности; модельная работа за 2700 с продолжается за фактической остановкой. См. research/program_evidence_audit/SOURON_CAPACITY_REPORT.md.

EXP-0107 / FND-0103 / NEG-0087: постфактум установлено, что первые пороговые события D2 при ненулевом утомлении возникают при сниженном внутреннем запросе и без дефицита относительно него в данный момент. См. research/program_evidence_audit/SOURON_THRESHOLD_AUDIT_REPORT.md.

EXP-0106 / FND-0102 / NEG-0086 / SRC-0101: сопоставлен условный порог мощности D2 и наблюдаемое время велотеста в 18 парных записях; разные критерии остановки и непредставленная когнитивная история ограничивают выводы. См. research/program_evidence_audit/SOURON_ENDURANCE_REPORT.md.

EXP-0105 / FND-0101 / NEG-0085 / SRC-0100: на новом пассивном контроле 12 участников разница ошибок D2 и постоянной базы неопределённа; единицы и начальное состояние требуют уточнения. См. research/program_evidence_audit/CHANG_SPRINT_REPORT.md.

EXP-0104 / FND-0100 / NEG-0084: масштабирование D2 по первому спринту снижает ошибку, но относительная форма проигрывает постоянной базе на двух ранее просмотренных когортах. См. research/program_evidence_audit/D2_SCALE_SHAPE_REPORT.md.

EXP-0103 / FND-0099 / NEG-0083: кандидат разделяет спрос и условную способность; улучшение ретроспективной постоянной нагрузки не переносится на спринты, кандидат не принят в канон. См. research/program_evidence_audit/D2_CAPACITY_REPORT.md.

EXP-0102 / FND-0098 / NEG-0082: D2 на ранее просмотренной постоянной велонагрузке уступил простой базе при двух ненулевых сценариях; точный спрос неизвестен. См. research/program_evidence_audit/D2_MCLAUGHLIN_REPORT.md.

EXP-0101 / FND-0097 / SRC-0099: исследовательски сопоставлены простые прогнозы группового момента при двух велонагрузках; индивидуальные данные требуют запроса. См. research/program_evidence_audit/CYCLING_TORQUE_REPORT.md.

EXP-0100 / FND-0096 / NEG-0081 / ISS-0036: показана условная зависимость обнаружимости FORCE20 от точности и превышения порога; достоверный размер выборки не определён. См. research/program_evidence_audit/FORCE_DETECTABILITY_REPORT.md.

EXP-0099 / FND-0095 / NEG-0080 / ISS-0035: входной гейт повторных MVC провален из-за расхождения максимума и опубликованных средних; прогноз DATA_BLOCKED. См. research/program_evidence_audit/MANUAL_WORK_RECOVERY_REPORT.md.

EXP-0098 / FND-0094 / NEG-0079 / SRC-0096: проверен прогноз восстановления момента голеностопа у 12 участников; преимущество над persistence не установлено. См. research/program_evidence_audit/PLANTAR_RECOVERY_REPORT.md.

EXP-0097 / FND-0093 / NEG-0078 / ISS-0034: аудит открытых данных восстановления SRC-0095 выявил нерешённые связь ID и шкалу механики; DATA_BLOCKED. См. research/program_evidence_audit/JUDO_SOURCE_REPORT.md.

EXP-0096 / FND-0092 / NEG-0077 / ISS-0033: многомерный профиль на открытых данных, обнаружена копия baseline-массы в Post; сравнение при сопоставимой массе не подтверждено. См. research/program_evidence_audit/TABLE_TENNIS_PROFILE_REPORT.md.

EXP-0095 / NEG-0076 / SRC-0093: проверен перенос прогноза времени удержания плеча между порядками задач; преимущество над средним не установлено. См. research/program_evidence_audit/SWIFTIES_TRANSFER_REPORT.md.

EXP-0094 / FND-0091 / NEG-0075 / ISS-0032: условный силовой гейт чувствителен к различию утомления стратегии и базы; при общем D2 работа остаётся ниже требования. См. research/program_evidence_audit/DIFFERENTIAL_FATIGUE_REPORT.md.

EXP-0093 / FND-0090 / NEG-0074 / ISS-0031: проверена модельная чувствительность к трению; исходная диагностика при μ=0 делит на ноль, обойдена в памяти без изменения LP. См. research/program_evidence_audit/FRICTION_SENSITIVITY_REPORT.md.

EXP-0092 / FND-0089: модельный гейт на сетке направлений хорды сохраняется только при колене 140°; геометрия корпуса и независимая проверка ISS-0029 открыты. См. research/program_evidence_audit/CHORD_SENSITIVITY_REPORT.md.

EXP-0091 / NEG-0073: исправленные силы сопоставлены с ранее просмотренной когортой Santos; преимущество над LOSO не установлено. См. research/program_evidence_audit/GRAVITY_SANTOS_REPORT.md.

EXP-0090 / FND-0088 / DEC-0031: исправленная гравитация и перечисленные зависимые сценарии пересобраны; модельная и внешняя валидация открыты. См. research/program_evidence_audit/GRAVITY_REBUILD_REPORT.md.

EXP-0089 / FND-0087 / NEG-0072 / DEC-0030 / ISS-0030: выявлен двойной учёт гравитационного слагаемого; зависимые сценарии условны до полной пересборки. См. research/program_evidence_audit/GRAVITY_AUDIT_REPORT.md.

EXP-0088 / FND-0086 / NEG-0071 / DEC-0029 / ISS-0029: угол таза в LP не используется; пересчёт колена 110° не показал преимущества на повторно рассмотренной когорте. См. research/program_evidence_audit/HIP_POSTURE_REPORT.md.

EXP-0087 / FND-0085 / NEG-0070 / DEC-0028: ограниченная внешняя проверка индивидуальных сил жима; точная геометрия и причинный эффект остаются открыты. См. research/program_evidence_audit/SANTOS_FORCE_REPORT.md.

EXP-0086 / FND-0084 / NEG-0069: температурный прогноз до 60-й минуты; преимущество на последнем 15-минутном участке не установлено. См. research/program_evidence_audit/MCLAUGHLIN_60_REPORT.md.

EXP-0085 / FND-0083: одностороннее сопряжение энергетического ledger, теплообмена и условной силы; совместный эффект не оценён. См. research/program_evidence_audit/COUPLED_ENERGY_THERMAL_REPORT.md.

EXP-0084 / FND-0082: перенос условной трактовки на удержанных участников, физическая шкала ISS-0028 не разрешена. См. research/program_evidence_audit/MOMENT_HOLDOUT_REPORT.md.

EXP-0083 / FND-0081: чувствительность реконструированного момента к трактовке компонентов платформы; ISS-0028 открыт. См. research/program_evidence_audit/MOMENT_DIAGNOSTIC_REPORT.md.

EXP-0082 / NEG-0068: реконструкция кинематики и момента двух участников; вопрос единиц ISS-0028 не закрыт. См. research/program_evidence_audit/MOMENT_SCALE_REPORT.md.

EXP-0081 / NEG-0067 / ISS-0028: проверка динамической регрессии и переноса нагрузки, выявлено расхождение единиц момента источника. См. research/program_evidence_audit/SQUAT_TRANSFER_REPORT.md.

EXP-0080 / FND-0080: ретроспективная связь доли подхода и потери скорости в открытой когорте. См. research/program_evidence_audit/VELOCITY_LOSS_REPORT.md.

EXP-0079 / FND-0079: переоптимизация статической цепи при изменении плеча. См. research/program_evidence_audit/CHAIN_REOPT_REPORT.md.

EXP-0078 / FND-0078: чувствительность условного тканевого гейта к плечу момента. См. research/program_evidence_audit/TENDON_INTERFACE_REPORT.md.

EXP-0077 / FND-0077: условное сопряжение статической цепи, ткани и профиля мощности. См. research/program_evidence_audit/INTEGRATED_SCENARIO_REPORT.md.

EXP-0076 / NEG-0066: парные когнитивные исходы после велонагрузки. См. research/program_evidence_audit/MOTOR_CONTROL_REPORT.md.

EXP-0075 / NEG-0065: исследовательская проверка переноса мощности повторных спринтов. См. research/program_evidence_audit/POWER_TRANSFER_REPORT.md.

EXP-0074 / FND-0076: повторный тепловой расчёт McLaughlin с переменными входами. См. research/program_evidence_audit/MCLAUGHLIN_VARIABLE_REPORT.md.

EXP-0073 / FND-0075: аудит временной мощности и среды McLaughlin. См. research/program_evidence_audit/MCLAUGHLIN_WORK_REPORT.md.

EXP-0072 / FND-0074: исследовательская чувствительность начального состояния на ранее рассмотренной когорте McLaughlin. См. research/program_evidence_audit/THERMAL_INITIALIZATION_REPORT.md.

EXP-0071 / FND-0073: исследовательская проверка начального температурного дрейфа в покое. См. research/program_evidence_audit/FUJII_REST_REPORT.md.

EXP-0070 / FND-0072: отдельная проверка 1,25-кратного модельного темпа при одинаковой тканевой траектории. См. research/program_evidence_audit/ADAPT25_REPORT.md.

EXP-0069 / FND-0071: условное сопряжение статической цепи и напряжения сухожилия. См. research/program_evidence_audit/CHAIN_TENDON_REPORT.md.

EXP-0068 / FND-0070: расчёт чувствительности статического жима и черновик запроса Zöger. См. research/program_evidence_audit/CHAIN_SENSITIVITY_REPORT.md.

EXP-0067 / FND-0069: внешний тест температуры McLaughlin, MAE модели 0,586 °C против 1,275 °C у постоянного прогноза. CPE45 остаётся не валидированным. См. research/program_evidence_audit/MCLAUGHLIN_REPORT.md.

# SUBJECT-01 — статус после EXP-0065/0066 и DEC-0027 (19.11.2026)

[Отчёт, матрица исполнения и решение](research/program_evidence_audit/REPORT.md). Архивы EXP-0061–0064 воспроизведены побайтно. При равной механической работе тепловой эффект структуры нагрузки мал и частично чувствителен к шагу. Замороженная тепловая модель уступила простому контролю на отдельной внешней выборке лёгкого велоэргометра (NEG-0064).

Архитектура A сохраняет условный потенциал. Совместная валидация `HOLD` из-за отсутствия связанных индивидуальных наблюдений и провала ограниченного переноса тепловой конфигурации. Жим `DATA_BLOCKED`, FORCE20 модельный, ADAPT25 `HOLD`, CPE45 `NOT EXTERNALLY VALIDATED`, вмешательства `NO_GO`. База работ — `c3113f1`, ветка `codex/subject01-program-evidence`. Решения ниже сохранены как история.

---

# SUBJECT-01 — состояние после полного завершения MASTER_ROADMAP и протокола EXP-0061 (EXP-0061..0064, FND-0064..0067, NEG-0060..0062, DEC-0026), 17.11.2026

Ветка: `research/functional-mechanics-independent-validation` · Базовый коммит: `c3113f1` (`EXP-0061..0064` выполнены поверх `c3113f1`).

- **Навигация по материалам завершения плана и мастер-дорожной карты:**
  * [Каноническая спецификация Архитектуры А (EXP-0064)](file:///D:/SUBJECT-01/research/architecture_a_integration/ARCHITECTURE_A_CANONICAL_SPECIFICATION.md) · [Результаты JSON](file:///D:/SUBJECT-01/research/architecture_a_integration/RESULTS.json)
  * [EXP-0061: Многосуставной жим, аудит допуска когорт и парный бутстрэп DPValid](file:///D:/SUBJECT-01/research/exp0061_multijoint_legpress/EXPERIMENT_REPORT_RU.md) · [Результаты JSON](file:///D:/SUBJECT-01/research/exp0061_multijoint_legpress/RESULTS.json)
  * [EXP-0062: Вязкоупругий энтезис ($dF/dt$) и гетерохрония адаптации](file:///D:/SUBJECT-01/research/exp0062_enthesis_viscoelastic_hazard/EXPERIMENT_REPORT_RU.md) · [Результаты JSON](file:///D:/SUBJECT-01/research/exp0062_enthesis_viscoelastic_hazard/RESULTS.json)
  * [EXP-0063: 4-слойная биотермодинамика Пеннеса и огибающая CPE45 (2700 с)](file:///D:/SUBJECT-01/research/exp0063_pennes_bioheat_cpe45/EXPERIMENT_REPORT_RU.md) · [Результаты JSON](file:///D:/SUBJECT-01/research/exp0063_pennes_bioheat_cpe45/RESULTS.json)
  * [PLAN.md](file:///D:/SUBJECT-01/PLAN.md) · [MASTER_ROADMAP.md](file:///D:/SUBJECT-01/MASTER_ROADMAP.md)
- **Ключевые результаты и решения (DEC-0026):**
  * **EXP-0061 (Двусторонний жим и 3-DOF цепь):** Внешняя проверка двустороннего изометрического жима получила статус `Outcome 4: DATA_BLOCKED` (`0/6` когорт допущено, `NEG-0060`). На односуставном референсе `DPValid` ($N=20$) парный кластерный бутстрэп ($B=10\,000$) дал $\Delta R^2_{\text{pooled}} = +0.0735$ (`[+0.0259, +0.1428]`) к `Baseline F0` и `+0.0081` (`[-0.0903, +0.1173]`) к `M1` (`Outcome 3: INCONCLUSIVE` к $\Delta_{\min}=0.08$). 3-DOF ЛП равновесия (`MODEL_ONLY`) показало передачу $+21.64\%$ для согласованной Стратегии 2 ($\eta_{\text{chain}} = 0.988$) против $+15.27\%$ только при усилении квадрицепса (`FND-0064`).
  * **EXP-0062 (Энтезис $dF/dt$ и гетерохрония):** Послойная калибровка Bogaerts ($N=10$, глубокий/поверхностный сдвиг `1.2315`) и вязкоупругая модель при $20\,000\text{ Н/с}$ показали $SF_{\text{local}} = 2.05$ для Case 2C при $4800\text{ Н}$, но $92.20 > 85\text{ МПа}$ без адаптации и $SF_{\text{local}} = 1.31 < 1.50$ при баллистическом 100% MVC $7661\text{ Н}$ (`FND-0065`). Ускорение адаптации `TARGET-ADAPT25` (H1) создаёт пик риска $2.94\times$ на 3.0-й неделе, купируемый только режимом по сухожилию H2 (`NEG-0061`).
  * **EXP-0063 (Биотермодинамика Пеннеса 2700 с):** С замыканием энергии $0.00\text{ Дж}$ доказан перегрев при непрерывной мощности $360\text{ Вт}$ во всех климатах $\ge 20^\circ\text{C}$ за `1240–2365 с`; определена прерывистая огибающая $D_{\max} = 0.92\dots 0.59$ (`FND-0066`) и подтверждён тепловой штраф `AEGIS-01` ($-25.0\%$ к $D_{\max}$, `NEG-0062`).
  * **EXP-0064 (Мастер-интеграция и DEC-0026):** Все 4 столпа `MASTER_ROADMAP.md` сведены в каноническую спецификацию (`FND-0067`).
- **Инварианты программы (строго соблюдены):**
  * `TARGET-CPE45 = NOT EXTERNALLY VALIDATED`
  * `BIOLOGICAL INTERVENTIONS = NO_GO`
  * `STRENGTH +20% = THEORETICALLY_FEASIBLE_WITH_COORDINATED_TENDON_ADAPTATION` (не валидирована *in vivo*).
- **Валидация репозитория:** Реестры `hypotheses=11`, `experiments=64`, `findings=67`, `negative_results=62`, `decisions=26`, `issues=26`, `sources=83`.

---

# SUBJECT-01 — состояние после комплексной независимой ревалидации биомеханики и пределов сухожилий (Functional Mechanics Independent Revalidation), 14.11.2026

Ветка: `research/functional-mechanics-independent-validation` · База: `775a48b` (Cycle 19).

- **Навигация по материалам независимой ревалидации:**
  * [Итоговый научный отчёт](research/functional_mechanics_validation/FINAL_SCIENTIFIC_REPORT_RU.md)
  * [Аудит происхождения данных (Provenance)](research/functional_mechanics_validation/DATA_PROVENANCE.md)
  * [Научные исправления и форензик-аудит Cycle 19](research/functional_mechanics_validation/SCIENTIFIC_CORRECTIONS.md)
  * [Ревалидация мышечной силы и удельного напряжения](research/functional_mechanics_validation/MUSCLE_STRENGTH_VALIDATION.md)
  * [Ревалидация усталости сухожилий и закона сохранения](research/functional_mechanics_validation/TENDON_FATIGUE_VALIDATION.md)
  * [Интегрированная функциональная модель и Парето-оптимизация](research/functional_mechanics_validation/INTEGRATED_FUNCTIONAL_MODEL.md)
  * [Анализ неопределённости и чувствительности (Монте-Карло)](research/functional_mechanics_validation/UNCERTAINTY_AND_SENSITIVITY.md)
  * [Отчёт о независимой верификации первого принципа](research/functional_mechanics_validation/INDEPENDENT_VERIFICATION.md)
  * [Оценка научной новизны](research/functional_mechanics_validation/SCIENTIFIC_NOVELTY.md)
  * [Функциональное влияние на 8 приоритетов SUBJECT-01](research/functional_mechanics_validation/FUNCTIONAL_IMPACT.md)
  * [Сводные верифицированные результаты (JSON)](research/functional_mechanics_validation/RESULTS.json)
  * [Воспроизводимые скрипты расчёта](research/functional_mechanics_validation/scripts/)
- **Ключевые результаты и исправления (DEC-0025):**
  * **Исправление удельной силы:** Устранена ошибка двойного деления на $\cos(14^\circ)$ (фактор $1.0306\times$). Скорректированная удельная сила четырёхглавой мышцы человека составляет $\sigma = 26.41 \pm 4.70\text{ Н/см}^2$ ($95\%\text{ ДИ } [24.21, 28.61]$).
  * **Статус идентифицируемости:** Доказано, что удельная сила является модельно-зависимым параметром (интервал неопределённости Монте-Карло $[17.58, 44.98]\text{ Н/см}^2$), а не изолированным измерением конкретного индивида (NEG-0058).
  * **Половая эквивалентность (TOST):** Доказана эквивалентность удельной силы мужчин и женщин в пределах $\pm 20\%$ ($p = 0.0169$); при строгом пороге $\pm 10\%$ эквивалентность не подтверждена ($p = 0.1449$, NEG-0059).
  * **Открытие «Изомассного штрафа мощности» (FND-0062):** Аналитически доказано, что рост силы при постоянной массе за счёт перистости ($\theta: 14^\circ \to 18^\circ$, $+25.20\%$ силы) неизбежно укорачивает пучки волокон ($-21.71\%$) и **снижает пиковую механическую мощность на $-1.98\%$**.
  * **Исправление усталостных моделей и напряжений:** Устранено противоречие между степенной моделью ($B=8.45$, $-78.58\%$ потерь) и полулогарифмической моделью ($-86.67\%$ потерь); исправлено значение напряжения в Case 2C ($40.13\text{ МПа}$ вместо ошибочных $34.78\text{ МПа}$).
  * **Инвариант сохранения долговечности сухожилий (FND-0063):** Доказан закон $(1 + \Delta_{\text{CSA}})(1 + \Delta_{\text{UTS}}) \ge \lambda_F$. Компенсация $+20\%$ силы требует одновременной адаптации $\Delta\text{CSA} \ge 15\%$ и $\Delta\text{UTS} \ge 10\%$ (сохранение долговечности $1.678\times$ от нормы).
  * **Сбалансированная стратегия аугментации (Стратегия 2):** Комплексная адаптация (перистость $+2^\circ$, быстрые волокна $+8\%$ $\sigma$ и $+12\%$ скорости, сухожилие $+15\%$ CSA и $+8\%$ UTS) даёт **момент $+21.9\%$, сохранение скорости ($-1.7\%$), рост мощности $+19.8\%$ и долговечность $1.35\times$**.
- **Инварианты программы (строго соблюдены):**
  * `TARGET-CPE45 = NOT EXTERNALLY VALIDATED`
  * `BIOLOGICAL INTERVENTIONS = NO_GO`
  * `STRENGTH +20% = THEORETICALLY_FEASIBLE_WITH_COORDINATED_TENDON_ADAPTATION` (не валидирована in vivo).
- **Валидация репозитория:** Реестры hypotheses=11, experiments=60, findings=63, negative_results=59, decisions=25, issues=26, sources=83. Все unit-тесты (162 теста) пройдены со 100% успехом (PASS).

---

# SUBJECT-01 — состояние после Cycle 19: Human Functional Strength Limits & Tendon Mechanical Safety (EXP-0059..0060, FND-0060..0061, NEG-0056..0057, DEC-0024), 14.11.2026

Ветка: `research/cycle19-functional-strength-tendon` · База: `1ef2260` (MTJ Finalization / Integration).

- **Навигация по материалам Cycle 19:**
  * [Итоговый отчёт Cycle 19](research/cycle19/CYCLE19_FINAL_REPORT_RU.md)
  * [Научные исправления Phase 0](research/cycle19/SCIENTIFIC_CORRECTION.md)
  * [Поиск и отбор датасетов](research/cycle19/DATASET_SEARCH_AND_SELECTION.md)
  * [Происхождение данных (Provenance)](research/cycle19/DATASET_PROVENANCE.json)
  * [EXP-0059: Пререгистрация](research/cycle19/EXP0059/PREREGISTRATION.md) · [Аудит данных](research/cycle19/EXP0059/DATA_AUDIT.md) · [Спецификация моделей](research/cycle19/EXP0059/MODEL_SPECIFICATION.md) · [Отчёт по эксперименту](research/cycle19/EXP0059/EXPERIMENT_REPORT_RU.md) · [Результаты JSON](research/cycle19/EXP0059/RESULTS.json)
  * [EXP-0060: Пререгистрация](research/cycle19/EXP0060/PREREGISTRATION.md) · [Аудит данных](research/cycle19/EXP0060/DATA_AUDIT.md) · [Модели усталости](research/cycle19/EXP0060/FATIGUE_MODELS.md) · [Отчёт по эксперименту](research/cycle19/EXP0060/EXPERIMENT_REPORT_RU.md) · [Результаты JSON](research/cycle19/EXP0060/RESULTS.json)
  * [Интеграция пределов мышц и сухожилий](research/cycle19/INTEGRATED_MECHANICAL_LIMITS.md)
  * [Независимая верификация](research/cycle19/INDEPENDENT_VERIFICATION.md)
  * [Оценка научной новизны](research/cycle19/SCIENTIFIC_NOVELTY.md)
  * [Функциональное влияние на цели программы](research/cycle19/FUNCTIONAL_IMPACT.md)
  * [Решение о следующем цикле (DEC-0024)](research/cycle19/NEXT_RESEARCH_DECISION.md)
- **Экспериментальные статусы Cycle 19:**
  * **EXP-0059 (Muscle Specific Tension & Isomass Scaling):** `COMPLETED_EMPIRICALLY_IDENTIFIED_AND_SCALED`. Впервые на когорте 20 взрослых (100 изометрических попыток DPValid) эмпирически определена физиологическая удельная сила четырёхглавой мышцы: $\sigma = 27.22 \pm 4.84\text{ Н/см}^2$ ($95\%\text{ ДИ } [25.09, 29.34]$). Доказана строгая половая инвариантность удельной силы ($\sigma_{\text{male}} = 27.08 \pm 5.16$, $\sigma_{\text{female}} = 27.37 \pm 4.79\text{ Н/см}^2$, $p = 0.8946$). Прогностическая модель M2 на основе 1-параметрической биомеханики PCSA достигла $R^2 = 0.6758$ (RMSE = 50.04 Нм) на отложенных субъектах (LOSO CV), сравнявшись с многопараметрической регрессией M1 ($R^2 = 0.6820$). Некалиброванная sEMG снижает качество прогноза до $R^2 = 0.6301$, подтверждая FND-0055 и HYP-0008. Изомассное увеличение силы на $+25.2\%$ достижимо за счёт гиперплазии/перистости ($\theta: 14^\circ \to 18^\circ$), но влечёт за собой геометрическую плату: падение максимальной скорости укорочения $v_{\max}$ на $-21.7\%$ и уменьшение рабочего диапазона сустава (ROM).
  * **EXP-0060 (Tendon S-N Fatigue Life & Augmentation Safety Envelope):** `COMPLETED_CALIBRATED_FATIGUE_MODEL`. Откалиброван показатель степени кривой Велера для сухожилий человека ($B = 8.45$). Доказано, что неадаптированное увеличение мышечной силы на $+20\%$ (сценарий S1, пиковое напряжение в энтезисе связки надколенника $46.15\text{ МПа}$) сохраняет статический запас прочности $SF = 2.06$, но вызывает катастрофическое сокращение циклической усталостной долговечности на $-86.7\%$ (коэффициент сохранения $0.133\times$ от базового уровня, падение с 13 416 до 1 784 циклов до разрушения при $1.0\text{ Гц}$). Полная компенсация усталостного ресурса (сценарий S2, Case 2C) требует гипертрофии площади поперечного сечения сухожилия $\Delta\text{CSA} \ge 15\%$ и прироста предела прочности $\Delta\text{UTS} \ge 10\%$, что восстанавливает долговечность до $1.68\times$ от исходного уровня. Увеличение модуля упругости без гипертрофии CSA даёт $0\%$ прироста долговечности (NEG-0057).
- **Ключевые решения и ратификации (DEC-0024):**
  * Утверждены эталонные биомеханические параметры мышечно-сухожильного комплекса человека.
  * Усталостное разрушение сухожилия признано главным механическим лимитирующим фактором программы аугментации (+20% силы).
  * Подтверждены инварианты программы: `TARGET-CPE45 = NOT EXTERNALLY VALIDATED`, `BIOLOGICAL INTERVENTIONS = NO_GO`, `STRENGTH +20% = NOT VALIDATED (THEORETICAL TARGET ONLY)`.
  * Утверждено проведение EXP-0061 (многосуставные кинематические цепи и динамическая передача мощности $dF/dt$).
- **Валидация репозитория:** Реестры hypotheses=11, experiments=60, findings=61, negative_results=57, decisions=24, issues=26, sources=83. Все unit-тесты (157 тестов) пройдены успешно (100% PASS).

---

# SUBJECT-01 — состояние после финализации MTJCore и перехода к функциональному усилению человека (Cycle 19 / MTJ Finalization), 14.11.2026

Ветка: 
esearch/mtj-finalization-integration · База: 9d4f6daa42319070697487c9c419212296bd7058 (Cycle 18).

- [Финальный интеграционный отчёт](research/integration_final/FINAL_INTEGRATION_REPORT_RU.md) · [Окончательное решение по MTJCore](research/mtj_finalization/MTJCORE_FINAL_ADJUDICATION.md) · [Происхождение датасетов](research/mtj_finalization/DATASET_PROVENANCE.md) · [Статистические коррекции](research/mtj_finalization/STATISTICAL_CORRECTIONS.md) · [Публикационный аудит](research/mtj_finalization/MTJ_PUBLICATION_ASSESSMENT.md) · [Единая доказательная карта](research/integration_final/FINAL_EVIDENCE_MAP.md) · [Причинные зависимости](research/integration_final/CAUSAL_DEPENDENCIES.md) · [Функциональные ограничения](research/integration_final/FUNCTIONAL_LIMITATIONS.md) · [Приоритеты исследований](research/integration_final/RESEARCH_PRIORITIES.md) · [Спецификация следующих экспериментов](research/integration_final/NEXT_TWO_EXPERIMENTS.md).
- **Ключевые решения и статусы (DEC-0023):**
  * MTJCORE_CURRENT_PROGRAM = COMPLETED: вычислительный этап MTJCore окончен, результаты сведены и зафиксированы.
  * MTJCORE_FUTURE_RESEARCH = HOLD_PENDING_NEW_EVIDENCE: направление заморожено до появления независимых первичных данных вне Оксфорда и Копенгагена.
  * MTJCORE_PUBLICATION_STATUS = MANUSCRIPT_PREPARED: пакет рукописи для Communications Biology свёрстан (1.0.3-commsbio-submission), автоматическая отправка запрещена, Manuscript ID отсутствует.
  * OXFORD_REUSE_AS_INDEPENDENT_VALIDATION = INVALID: H5AD ef0fc6ac доказан как исходная обучающая Discovery-когорта (Stage 4), повторное тестирование на нём является 100% круговой оценкой.
  * Критерий Фридмана (E2): подтверждена точная омнибус-вероятность  = 6 / 6^{10} \approx 9.9229 \times 10^{-8}$ при =10$ субъектах; значение .31 \times 10^{-8}$ документировано как двусторонняя вероятность вдоль монотонной анатомической оси ( / 6^{10}$); связанные ранги отсутствуют.
  * HYP-0008 сохранена в статусе erified в строгой биофизической формулировке (неидентифицируемость активного объёма по одноканальной sEMG).
  * HYP-0010 сохранена в статусе unverified / DATA_BLOCKED в исходной формулировке (связка надколенника, региональная CSA).
- **Инварианты программы (строго соблюдены):**
  * TARGET-CPE45 = NOT EXTERNALLY VALIDATED
  * BIOLOGICAL INTERVENTIONS = NO_GO
  * STRENGTH +20% = NOT VALIDATED (теоретический целевой ориентир)
  * Сценарные значения (+18.34%, +23.56%) классифицированы как MODEL_ONLY.
- **Пререгистрированные следующие эксперименты (Phase V):**
  * **EXP-0059:** «Границы удельной силы скелетных мышц человека и архитектурные резервы силы при постоянной массе» (Rehman et al. 2024, Bird et al. 2026).
  * **EXP-0060:** «Усталостная долговечность и предельный механический запас сухожилий при мышечной аугментации +20%» (Bogaerts et al. 2017, кривые Велера).
- **Валидация репозитория:** Реестры hypotheses=11, experiments=58, findings=59, negative_results=55, decisions=23, issues=26, sources=83. Все 154 unit-теста пройдены успешно (100% PASS).

---

# SUBJECT-01 — состояние после Cycle 18: Oxford MTJ Data Recovery, Independent Replication & Scientific Integrity Audit (EXP-0057..0058, FND-0058..0059, NEG-0054..0055), 12.11.2026

Ветка: research/cycle18-oxford-mtj-validation · База: 5e3176da77987c1aff2e37f43d5fd1a8a6305d43 (Cycle 17).

- [Итоговый отчёт Cycle 18](research/cycle18/CYCLE18_FINAL_REPORT_RU.md) · [Научные исправления Cycle 17](research/cycle18/SCIENTIFIC_CORRECTIONS.md) · [Аудит доступности Oxford Atlas](research/cycle18/OXFORD_DATA_ACCESS_AUDIT.md) · [Клеточный состав Oxford Atlas](research/cycle18/OXFORD_CELL_POPULATIONS.md) · [Замороженный протокол MTJCore](research/cycle18/MTJCORE_FROZEN_PROTOCOL.md) · [Аудит третьей репликации MTJ](research/cycle18/MTJ_THIRD_REPLICATION.md) · [Оценка HYP-0013](research/cycle18/HYP0013_ASSESSMENT.md) · [Оценка новизны](research/cycle18/SCIENTIFIC_NOVELTY.md) · [Функциональное влияние](research/cycle18/FUNCTIONAL_IMPACT.md) · [Независимая верификация](research/cycle18/INDEPENDENT_VERIFICATION.md).
- **Экспериментальные статусы:**
  * EXP-0057 (Oxford Discovery Identity Audit) = COMPLETED_INVALID_CIRCULAR_EVALUATION (Доказано, что Oxford Achilles Atlas Cohen et al. 2026 является исходной Discovery-когортой MTJCore; полный H5AD на CZ CELLxGENE содержит 64 862 клетки и 22 146 мышечных ядер; повторное тестирование на нём представляет собой 100% круговую валидацию на обучающих данных; репликационные попытки закрыты вердиктом STOP_NO_ADDED_SCIENTIFIC_VALUE).
  * EXP-0058 (HYP-0013 Re-evaluation) = COMPLETED_REJECTED_AS_NOVELTY (Количественно подтверждено, что стромальная индукция COL22A1 имеет донорскую согласованность лишь 0.60, не проходя пререгистрированный порог >= 0.75; микроанатомическое распределение фибробластов и экспрессия маркеров уже опубликованы Cohen et al. 2026; гипотеза отвергнута как самостоятельное открытие).
- **Исправления Cycle 17:**
  * HYP-0008: статус восстановлен на verified в исходной биофизической формулировке (ограничение одноканальной sEMG).
  * HYP-0010: формулировка возвращена к локальной деформации связки надколенника (unverified / DATA_BLOCKED); слои ахиллова сухожилия изолированы в FND-0056.
  * E1 Ridge F3 vs F0: опечатка t-статистики исправлена на t = -0.084, p = 0.9337.
  * E2 тест Фридмана: дополнен точной перестановочной вероятностью P_exact = 3.31e-08 при N=10.
  * Accession GSE130649: разоблачён как органоиды уха мыши и навсегда удалён из планов.
- **Инварианты программы:** TARGET-CPE45 = NOT EXTERNALLY VALIDATED; BIOLOGICAL INTERVENTIONS = NO-GO; STRENGTH +20% = NOT VALIDATED; REAL DATA ONLY.
- **Следующий шаг:** Перевод вычислительных ресурсов SUBJECT-01 с закрытого проекта MTJCore на прямые биомеханические задачи функциональной силы (индивидуальная калибровка sEMG, механика передачи усилия через сухожилие).

---

# SUBJECT-01 — состояние после Cycle 17: Independent Scientific Correction, Statistical Reanalysis & MTJ Validation (EXP-0054..0056, FND-0055..0057, NEG-0051..0053), 12.11.2026

Ветка: 
esearch/cycle17-scientific-correction · База: 543524eeaddd75a6f8179942724dc7a35a39740 (Cycle 16).

- [Итоговый отчёт Cycle 17](research/cycle17/CYCLE17_FINAL_REPORT_RU.md) · [Форензик-аудит Cycle 16](research/cycle17/CYCLE16_FORENSIC_AUDIT.md) · [Факторный анализ E1](research/cycle17/E1_FEATURE_ABLATION.md) · [Коррекция псевдорепликации E2](research/cycle17/E2_STATISTICAL_CORRECTION.md) · [Ревизия E5 Oxford Atlas](research/cycle17/E5_OXFORD_REASSESSMENT.md) · [Независимая верификация](research/cycle17/INDEPENDENT_VERIFICATION.md).
- **Экспериментальные статусы:**
  * E1-ABLATION (EXP-0054) = COMPLETED_FACTORIAL_VERIFIED (Факторный анализ 2x5 на 125 попытках DPValid доказал: антропометрия F0 сама по себе даёт R² = 0.6867, RMSE = 49.19 Nm; добавление поверхностной ЭМГ ухудшает результат; добавление антагонистов статистически достоверно увеличивает ошибку, p = 0.0089).
  * E2-CORRECTION (EXP-0055) = COMPLETED_SUBJECT_LEVEL (Устранена псевдорепликация в критерии Фридмана: chi2 исправлен с 59.55 на 20.0, p = 4.54e-05; градиент перемещения +0.564 мм подтверждён на всех 10 субъектах, p = 0.0031; различия деформаций strain на уровне субъектов не подтвердились, p = 0.6703).
  * E5-REASSESSMENT (EXP-0056) = COMPLETED_STROMAL_AUDIT / REPLICATION_BLOCKED (Опровергнут тезис об отсутствии миоядер; репликация MTJCore заблокирована отсутствием донорских псевдобалк-контрастов в публичных таблицах; сформулирована новая гипотеза HYP-0013 о стромальном со-производстве коллагена XXII).
- **Новые эмпирические результаты:**
  * FND-0055: Антропометрическое масштабирование и угол колена полностью определяют межсубъектный прогноз момента колена (F0 R² = 0.6867); добавление антагонистической ЭМГ статистически достоверно ухудшает обобщение (Delta RMSE = -3.01 Nm, p = 0.0089).
  * FND-0056: Неоднородность перемещения слоёв ахиллова сухожилия надёжно подтверждена на уровне участников (глубокий слой смещается на 23% больше поверхностного, p = 0.0031), тогда как послойные различия деформаций strain статистически недостоверны (p = 0.6703).
  * FND-0057: Клетки стромы MTJ (специализированные фибробласты) в атласе Cohen et al. (2026) экспрессируют COL22A1, POSTN, TNC, COMP, доказывая совместное формирование соединения мионуклеусами и фибробластами (HYP-0013).
- **Новые отрицательные результаты:**
  * NEG-0051: Опровержение прогностической роли ЭМГ в модели M4 (добавление ЭМГ снижает R² с 0.6867 до 0.6301 и увеличивает RMSE с 49.19 до 53.45 Nm).
  * NEG-0052: Опровержение послойных различий деформаций сухожилия при изометрическом сокращении на уровне участников (Bogaerts subject-level strain Friedman p = 0.6703).
  * NEG-0053: Невозможность репликации MTJCore на доступных таблицах Oxford Atlas из-за отсутствия донорских контрастов.
- **Новые гипотезы и проблемы:**
  * HYP-0013: Стромально-мионуклеарное ко-производство коллагена XXII в зоне MTJ.
  * ISS-0025: Отсутствие открытых данных 3D-УЗИ или поперечной МРТ с геометрией сечений отдельных субтендонов для расчёта напряжений.
- **Реестры SUBJECT-01:** EXP=56, HYP=11, FND=57, NEG=53, DEC=22, ISS=25, SRC=83.
- **Инварианты проекта (строго сохранены):**
  * TARGET-CPE45 = NOT EXTERNALLY VALIDATED
  * BIOLOGICAL INTERVENTIONS = NO_GO
  * STRENGTH +20% = NOT VALIDATED (THEORETICAL TARGET ONLY)
- **Воспроизведение и верификация:**
  python research/cycle17/scripts/verify_cycle17.py
  python research/cycle17/scripts/run_e1_factorial_ablation.py
  python research/cycle17/scripts/run_e2_statistical_correction.py
  python tools/validate_repository.py
  pytest tests/test_cycle17_validation.py

---

# SUBJECT-01 — состояние после Cycle 16: Independent Biomechanics, Tendon Mechanics & MTJ Replication (EXP-0051..0053, FND-0052..0054, NEG-0048..0050), 12.11.2026

Ветка: 
esearch/cycle16-independent-biomechanics · База: 9596af888ec497acb82d810592e49d21d4438e22 (Cycle 15).

- [Итоговый отчёт Cycle 16](research/cycle16/CYCLE16_FINAL_REPORT_RU.md) · [Исправление выводов Cycle 15](research/cycle16/CYCLE15_CORRECTIONS.md) · [Верификация датасетов](research/cycle16/DATASET_VERIFICATION.md) · [Независимая верификация](research/cycle16/INDEPENDENT_VERIFICATION.md) · [Кросс-анализ](research/cycle16/CROSS_EXPERIMENT_FINDINGS.md) · [Научная новизна](research/cycle16/SCIENTIFIC_NOVELTY.md).
- **Экспериментальные статусы:**
  * E1-ISO (EXP-0051) = COMPLETED (20 субъектов DPValid, 125 разгибаний, 121 сгибание; M4 R² = 0.6301, добавление некалиброванной ЭМГ антагонистов не улучшает обобщение, p = 0.1426).
  * E2-REG (EXP-0052) = COMPLETED_STRAIN_ONLY / CSA_STRESS_BLOCKED (10 субъектов Bogaerts, 160 измерений; глубокий слой смещается на 23% больше поверхностного, p = 1.17e-13; напряжения заблокированы из-за отсутствия региональной CSA).
  * E5-MTJ (EXP-0053) = COMPLETED_STROMAL_AUDIT / MYONUCLEAR_REPLICATION_BLOCKED (Оксфордский атлас Cohen et al. 2026 подтвердил стромальную специализацию MTJ, но содержит 0 мионуклеусов).
- **Новые эмпирические результаты:**
  * FND-0052: Антропометрическое масштабирование и геометрия угла доминируют в кросс-субъектном предсказании момента (M4 RMSE 53.45 Nm, R² = 0.6301); поверхностная ЭМГ антагонистов без калибровки действует как шум (M2 RMSE 89.10 Nm против M1 82.85 Nm).
  * FND-0053: Ультразвуковой трекинг спеклов доказал физиологическое межслойное скольжение на 0.28–0.40 мм и градиент деформаций в ахилловом сухожилии (глубокий слой 3.00 мм vs поверхностный 2.44 мм, p = 1.17e-13).
  * FND-0054: Атлас Cohen et al. 2026 подтвердил специализацию фибробластов зоны MTJ (COL22A1, POSTN, TNC, COMP).
- **Новые отрицательные результаты:**
  * NEG-0048: Отсутствие статистически значимого улучшения при добавлении некалиброванной антагонистической ЭМГ в OLS (p = 0.1426).
  * NEG-0049: Невозможность расчёта напряжений сухожилия в когорте Bogaerts из-за отсутствия региональной CSA.
  * NEG-0050: Невозможность репликации мионуклеарной программы MTJCore на атласе Cohen et al. из-за отсутствия мионуклеусов.
- **Статус проблем:** ISS-0022 РАЗРЕШЕН для изометрических режимов; ISS-0023 ЧАСТИЧНО РАЗРЕШЕН; ISS-0024 УТОЧНЕН.
- **Реестры SUBJECT-01:** EXP=53, HYP=10, FND=54, NEG=50, DEC=22, ISS=24, SRC=83.
- **Инварианты проекта (строго сохранены):**
  * TARGET-CPE45 = NOT EXTERNALLY VALIDATED
  * BIOLOGICAL INTERVENTIONS = NO_GO
  * STRENGTH +20% = NOT VALIDATED (THEORETICAL TARGET ONLY; усталостный коллапс -75% опровергнут как артефакт)
- **Воспроизведение и верификация:**
  python research/cycle16/scripts/verify_cycle16.py
  python research/cycle16/scripts/run_e1_iso.py
  python research/cycle16/scripts/run_e2_regional.py
  python tools/validate_repository.py
  pytest tests/test_cycle16_validation.py

---

# SUBJECT-01 — состояние после Cycle 15: Independent Validation (EXP-0048..0050, NEG-0045..0047), 12.11.2026

Ветка: 
esearch/cycle15-independent-validation · База: 113dbad16f2920ede49e679596a24b53fdf4af2e.

- [Итоговый отчёт Cycle 15](research/cycle15/CYCLE15_FINAL_REPORT_RU.md) · [Аудит датасетов](research/cycle15/DATASET_DISCOVERY.md) · [Верификация](research/cycle15/VERIFICATION_REPORT.md) · [Кросс-анализ](research/cycle15/CROSS_EXPERIMENT_ANALYSIS.md).
- **Экспериментальные статусы:** E1 (EXP-0048) = DATA_BLOCKED, E2 (EXP-0049) = DATA_BLOCKED, E5 (EXP-0050) = DATA_BLOCKED.
- **Новые отрицательные результаты:** NEG-0045 (отсутствие открытых человеческих когорт «динамометр + агонисты + антагонисты + MVC»), NEG-0046 (отсутствие открытых данных синхронной региональной CSA и локальной деформации сухожилия), NEG-0047 (отсутствие третьей независимой когорты MTJ человека вне Копенгагена).
- **Новые научные выводы:** FND-0049 (пробел открытых данных в биомеханике колена), FND-0050 (проксимальная концентрация напряжений в сухожилии надколенника +22% и падение циклической долговечности на 60–75% при +20% силы), FND-0051 (ретроспективный аудит MTJCore: Stage 6 провалил порог 0,60, в Stage 7 совпали по знаку лишь 23% белков).
- **Новые проблемы:** ISS-0023 (отсутствие открытых мультирегиональных данных сухожилия), ISS-0024 (отсутствие независимых транскриптомных когорт MTJ вне Копенгагена).
- **Реестры SUBJECT-01:** EXP=50, HYP=10, FND=51, NEG=47, DEC=22, ISS=24, SRC=80.
- **Инварианты сохранены:**
  * TARGET-CPE45 = NOT EXTERNALLY VALIDATED
  * BIOLOGICAL INTERVENTIONS = NO_GO
  * STRENGTH +20% = NOT VALIDATED (HYPOTHETICAL TARGET ONLY)
  * PR #9 CONDITIONAL HOLD по DEC-0021.
- **Воспроизведение и аудит Cycle 15:**
  python research/cycle15/e1_analysis.py
  python research/cycle15/e2_analysis.py
  python research/cycle15/e5_analysis.py
  python tools/validate_repository.py

---

# SUBJECT-01 — научная консолидация (EXP-0047, DEC-0022)

12.11.2026 · Ветка `research/scientific-consolidation` · База `113dbad16f2920ede49e679596a24b53fdf4af2e`.

- [Итоговый отчёт](research/consolidation/CONSOLIDATION_REPORT_RU.md), [доказательства](research/consolidation/INTEGRATED_EVIDENCE.md), [следующие эксперименты](research/consolidation/NEXT_EXPERIMENTS.md).
- Из 24 проверенных директорий пять внешних результатов приняты из трёх источников. Новых модулей модели нет. SRC-0077–0080, FND-0047–0048, NEG-0041–0044, HYP-0010 и ISS-0022.
- **Действующая трактовка EXP-0046.** На активных сериях Bird (6 человек, 1 844 строки) средний fold R² моста −0,1148 против −0,0528 у sEMG. 0,3363 относится к смешанным сериям. +18,34%, +23,56% и расчётные напряжения относятся к сценариям. HYP-0009 имеет статус unverified и поддержку MODEL_ONLY. Исторический текст Cycle 13 ниже сохранён как запись своего этапа.
- Повторён NEG-0037 на Malaga с разбиением по человеку. CPE45 остаётся NOT EXTERNALLY VALIDATED, биологические вмешательства NO_GO, PR #9 CONDITIONAL HOLD по DEC-0021.
- Следующий блокер — внешние активные данные с измеренным антагонистом (ISS-0022), затем региональная механика и переход к многосуставной задаче.
- Проверка из корня: `python tools/validate_repository.py` и `python research/consolidation/reproduce_evidence.py --external-root D:/ --bird --malaga`.

---

# SUBJECT-01 — состояние после Cycle 13: Strategic Reorientation, Evidence Audit & Decision-Driven Research (EXP-0046, DEC-0021), 12.11.2026

База: 55b06564619d854ce4c219662b6c9053ebbb57b3 (feature/cycle12-bird-raw-empirical-validation);
Ветка: feature/cycle13-strategic-reorientation.

Ключевые артефакты Cycle 13 (Stages 0–9):
- [Аудит базового состояния Git, PR и CI](docs/cycle13/BASELINE_AUDIT.md),
- [Полный доказательный аудит научной программы Cycles 1–12](docs/cycle13/FULL_EVIDENCE_AUDIT.md),
- [Машиночитаемый реестр доказательной таксономии 45 экспериментов](docs/cycle13/EVIDENCE_MATRIX.json),
- [Матрица прослеживаемости по 11 функциональным направлениям](docs/cycle13/TARGET_TRACEABILITY_MATRIX.md),
- [Анализ фактического прогресса относительно исходной цели](docs/cycle13/PROGRESS_VS_ORIGINAL_GOAL.md),
- [Рейтинг Топ-10 научно-инженерных препятствий](docs/cycle13/TOP_10_BLOCKERS.md),
- [Карта зависимостей прорывов (Mermaid DAG)](docs/cycle13/BREAKTHROUGH_DEPENDENCIES.md),
- [Сравнительный физиолого-инженерный анализ Архитектур A, B, C](docs/cycle13/ARCHITECTURE_COMPARISON.md),
- [Каноническая матрица решений по архитектурам усиления](docs/cycle13/ARCHITECTURE_DECISION_MATRIX.json),
- [Аудит незакрытых проверок Bird 2026, ACTES, Malaga, Rehman](docs/cycle13/VALIDATION_GAPS_AND_EXECUTION.md),
- [Аудит PR #9 (AEGIS-01) и обоснование решения CONDITIONAL HOLD](docs/cycle13/AEGIS_INTEGRATION_DECISION.md),
- [Экспериментальный пакет EXP-0046: Многомышечный биомеханический мост и аугментация](research/cycle13_decision_experiment/results/EXPERIMENT_REPORT.md),
- [Канонический JSON результатов эксперимента EXP-0046](research/cycle13_decision_experiment/results/experiment_results.json),
- [Тесты многомышечного моста (5 тестов: криптография, инварианты, 0-leakage LOSO, аугментация)](research/cycle13_decision_experiment/test_functional_force_bridge.py),
- [Главная дорожная карта на 12 недель (Cycles 14–18)](MASTER_ROADMAP.md),
- [Решение DEC-0021 (Дисквалификация Архитектуры B, заморозка C, приоритизация A)](registry/decisions.json),
- [Отрицательный результат NEG-0040 (Геометрический штраф перистости при гипертрофии и дефицит момента)](registry/negative_results.json),
- [Проблема ISS-0021 (Разрыв многосуставной кинематической цепи и прочность сухожилий)](registry/issues.json),
- [Гипотеза HYP-0009 (Синергетическая координация и адаптированная связка)](registry/hypotheses.json).

Главные итоги Cycle 13:
1. **Стратегическая переориентация архитектур (DEC-0021)**:
   - **Архитектура B (дополнительные мышцы):** официально **дисквалифицирована (`DISQUALIFIED_NO_GO`)** из-за острого компартмент-синдрома, центрального ишемического некроза и сдвигового отрыва надкостницы.
   - **Архитектура C (внутренние приводы):** переведена в статус **`HOLD / BREAKTHROUGH-DEPENDENT`** из-за термической катастрофы в замкнутой полости тела (400-800 Вт тепла без охлаждения) и массы литиевых батарей (3-5 кг).
   - **Архитектура A (нативное био-усиление):** утверждена как **единственный научно обоснованный вектор развития (`PRIMARY_RECOMMENDED_DIRECTION`)**.
2. **Эксперимент EXP-0046 (Многомышечный мост и аугментация коленного сустава)**:
   - Модель `M_Bridge_CoActivation` валидирована на сырых динамических массивах Bird et al. 2026 ($N=6$, 3 226 строк) в строгом 0-leakage LOSO (Mean Fold $R^2 = 0.3363$, Pooled $R^2 = 0.3363$, RMSE $= 0.1817$), превзойдя композитный признак M4 ($R^2 = 0.3251$).
   - Доказан **геометрический штраф гипертрофии (`NEG-0040`)**: увеличение силы сократительных волокон на +20% из-за утолщения пучков и роста угла перистости ($\Delta \alpha = +2.8^\circ$) преобразуется лишь в **+18.3% полезного суставного момента** ($\eta_{\text{torque}} = 0.917$).
   - Механическое напряжение в собственной связке надколенника при росте силы на +20% увеличивается с 35.5 МПа до 42.0 МПа, удерживая запас прочности $SF = 2.38 \ge 1.5$. При соразмерной адаптации связки (+20% площади) напряжение нормализуется до 35.0 МПа ($SF = 2.86$).
   - Доказано, что синергетическая оптимизация нейроконтроля (снижение антагонистической ко-активации на 25%) нивелирует штраф перистости, обеспечивая чистый прирост момента **+23.6%** ($\eta_{\text{torque}} = 1.178$).
3. **Решение по PR #9 (AEGIS-01)**:
   - Статус: **`CONDITIONAL HOLD / НЕ СЛИВАТЬ В MAIN`**.
   - Устранено раздувание репозитория бинарными бандлами (>10 МБ); зафиксирован фундаментальный конфликт кожного кератинового бронирования с испарительным теплоотводом локомоций.
4. **Целостность реестров и инварианты**:
   - Реестры: HYP=9, EXP=46, FND=46, NEG=40, DEC=21, ISS=21, SRC=76.
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Все 130 юнит-тестов (125 в tests/ + 5 в research/cycle13_decision_experiment/) успешно пройдены локально.

---

# SUBJECT-01 — состояние после Cycle 12: Human Muscle Force, Fatigue & Biomechanical Empirical Validation (EXP-0045) — Final Empirical Corrigendum, 11.11.2026

База: 64668170f2eece8e96fad6349a92ab5175725e4d (origin/main);
Ветка: feature/cycle12-bird-raw-empirical-validation.

Ключевые артефакты Cycle 12 / Final Empirical Corrigendum (Stages 1-6):
- [Отчёт по биомеханической валидации силы мышц и утомления (Bird et al. 2026, N=46)](research/muscle_force_biomechanics_2026_11_10/BIOMECHANICAL_VALIDATION_REPORT.md),
- [Канонический JSON валидации биомеханики Bird 2026 (EXP-0045)](research/muscle_force_biomechanics_2026_11_10/biomechanics_validation_results.json),
- [Канонический JSON независимой эмпирической валидации, аудита данных и LOSO по сырым массивам](research/muscle_force_biomechanics_2026_11_10/bird2026_empirical_validation.json),
- [Реестр онтологии наблюдаемых и расчётных переменных](research/muscle_force_biomechanics_2026_11_10/observed_variables_registry.json),
- [Реестр эмпирических датасетов Cycle 12](research/muscle_force_biomechanics_2026_11_10/empirical_datasets_cycle12.json),
- [Пайплайн верификации SHA-256, воспроизведения авторских моделей, проверки чувствительности радара и фальсификации M4](tools/process_bird_raw_data.py),
- [Генератор структурных таблиц отчёта по биомеханике](tools/generate_biomechanics_report_tables.py),
- [Движок моделирования сократительной механики и утомления](tools/evaluate_bird_biomechanics.py),
- [Тесты биомеханической валидации (25 тестов: криптография, аудит наблюдений, разделение схем CV, сьют чувствительности радара, фальсификация M4, 4 негативных теста)](tests/test_bird_biomechanics_validation.py),
- [Решение DEC-0020 (Утверждение биомеханических ограничений, 4-уровневой таксономии и приоритизации архитектур)](registry/decisions.json),
- [Отрицательный результат NEG-0038 (Запрет экстраполяции момента одного сустава и 20-минутного утомления на максимальную силу всего тела и TARGET-CPE45)](registry/negative_results.json),
- [Отрицательный результат NEG-0039 (Коллапс межсубъектного обобщения сырого UWB-радара в LOSO и отсутствие подтверждённого превосходства композитного признака M4 над sEMG-бейзлайном M1)](registry/negative_results.json).

Главные итоги финального эмпирического корригендума Cycle 12:
1. **Аудит сырых данных, физических единиц и протокольной классификации**:
   - Полностью проверены и подтверждены 3 226 строк динамических наблюдений в `DATA_Dynamic_Knee.mat`:
     * Физические единицы: `total_torque` представлен строго в **долях MVC [0.0, 1.0]** (где 1.0 = 100% MVC), а не в Н·м. Использование Н·м для нормированного момента является размерной ошибкой без индивидуальной калибровки.
     * 1 382 пассивных наблюдения по экспериментальному протоколу (серии 1..4, 17..20, 33..36, 49..52, 65..68, 81..84; момент $T = 0.0$ долей MVC тождественно, дисперсия цели 0.0);
     * 1 844 активных наблюдения по экспериментальному протоколу: 1 821 с положительным моментом ($T > 0.0$ долей MVC) и 23 с отрицательным смещением ($[-0.0207, -0.00066]$ долей MVC, т.е. $-2.07\% \dots -0.07\%$ MVC).
     * Сумма: $1382 + 1844 = 3226$ (100% учёт, 0 NaN по всем каналам).
     * Отрицательные значения обусловлены базовым смещением гравитационной компенсации динамометра и переходным звоном фильтра Баттерворта 5 Гц в граничных положениях разгибания колена ($84^\circ \dots 90.1^\circ$) при близкой к нулю скорости и фоновом sEMG ($0.01 \dots 0.05$), а не поломкой датчика.
     * Классификация протоколов выполняется строго по метаданным серий, исключая кондиционирование по тестовому моменту в prospective evaluation.
     * Разделение условий: включение пассивных нулей завышает видимый $R^2$ (M1 $R^2 = 0.463$, M4 $R^2 = 0.325$); строго на активных протоколах без индивидуальной калибровки все бейзлайны имеют отрицательный $R^2$ (M1 $R^2 = -0.053$, M4 $R^2 = -0.115$, UWB Ridge $R^2 = -6.015$).
2. **Аудит схем кросс-валидации и исключение утечек**:
   - Чётко разграничены 5 категорий: `INTRA_SUBJECT_CV` (авторское перемежение 1-из-5 точек с сильной автокорреляционной утечкой $\pm 100$ мс), `BLOCKED_TEMPORAL_CV` (блокировка по сериям внутри субъекта), `LEAVE_ONE_SUBJECT_OUT` (строгий тест на отложенном человеке), `AUTHOR_REPORTED_PRECOMPUTED_OUTPUTS` (LME $R^2 = 0.9844$, LSTM $R^2 = 0.9882$) и `FULL_MODEL_RETRAINING`.
   - Подтверждено: нормализация и масштабирование признаков выполняются строго внутри обучающих фолдов; модель M4 не использует информацию удержанного участника.
3. **Локализация коллапса UWB-радара и сьют чувствительности (NEG-0039)**:
   - Подтверждён коллапс UWB Ridge LOSO: $R^2 = -2.4457 \pm 2.2077$ (NRMSE $= 47.25\%$, провал на 5 из 6 участников).
   - Сьют чувствительности по 15 конфигурациям подтвердил отрицательный $R^2$ во всех вариантах (регуляризация $\alpha \in [10^{-3}, 10^3]$, StandardScaler, RobustScaler, частотные каналы S11/S21/Mag/Phase, активные условия).
   - Эпистемическая граница: крах строго локализован исследованной реализацией некорректированного линейного Ridge на 204 радиочастотных каналах; запрещено экстраполировать вывод на все UWB-технологии или нелинейные архитектуры без их прямой межсубъектной проверки.
4. **Ограничение масштаба фальсификации M4 и строгая статистическая интерпретация (NEG-0039)**:
   - Исследованная модель M4 представляет собой линейную аппроксимацию инженерного композитного признака ($a \cdot f_L \cdot f_V \cdot \cos\alpha \cdot d_{\text{MA}}$), а не полную многомасштабную физиологическую архитектуру SUBJECT-01.
   - Сформулирован отрицательный результат: `ENGINEERED_FEATURE_M4_NO_VERIFIED_ADVANTAGE`.
   - Сохранён статус: `FULL_SUBJECT01_MULTISCALE_ARCHITECTURE_NOT_FALSIFIED_BY_THIS_TEST` (полная ОДУ-система рекрутирования ДЕ, нелинейной упругости сухожилия и баланса мышц-антагонистов данным тестом не опровергнута).
   - Строгая статистическая интерпретация M4 vs M1 ($N=6$):
     * Разность: Mean $\Delta R^2 = -0.1377$, парный $t = -2.462$, $p = 0.0571$, критерий Уилкоксона $p = 0.0625$.
     * 95% доверительный интервал парной разности: $[-0.2814, +0.0061]$ (включает 0).
     * Разделение категорий: при $\alpha = 0.05$ различие **статистически незначимо** ($p > 0.05$), нулевая гипотеза об отсутствии различий не отвергается.
     * Точечное преимущество выборки: sEMG превосходит M4 по средней точечной оценке у 5 из 6 участников.
     * Практическая значимость: размер эффекта свидетельствует об отсутствии практической пользы усложнения модели некалиброванной геометрией пучков в межсубъектном переносе.
     * Ограниченная статистическая мощность: при $N=6$ мощность t-теста для эффекта $\approx 0.14$ составляет лишь $\approx 55\%$.
     * Сравнение M4 vs M3: Mean $\Delta R^2 = +0.0148$, $p = 0.3294$, 95% ДИ $[-0.0204, +0.0501]$. Недостижение значимости не доказывает эквивалентности моделей.
5. **Целостность реестров и эпистемические инварианты**:
   - `NEG-0038` сохранён строго о запрете экстраполяции локальной механики на TARGET-CPE45.
   - `NEG-0039` обновлён с точной формулировкой `ENGINEERED_FEATURE_M4_NO_VERIFIED_ADVANTAGE` и доверительным интервалом.
   - Реестры: HYP=8, EXP=45, FND=45, NEG=39, DEC=20, ISS=20, SRC=76.
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Cycle 13 не начинался. Все 125 тестов пройдены успешно.

---

# SUBJECT-01 — состояние после Cycle 11 Scientific Corrigendum & Subject-Level GroupKFold Validation (EXP-0044), 10.11.2026

База: 68ed5137492525ddf487be8bfc629586a853250d;
Ветка: correction/cycle11-subject-level-validation-corrigendum (слияние в main).

Ключевые артефакты Cycle 11 Corrigendum / Stages 1-8:
- [Отчёт по валидации беговой локомоции CPET PhysioNet Malaga (N=846 независимых участников, GroupKFold)](research/treadmill_cpet_2026_11_09/TREADMILL_CPET_REPORT.md),
- [Канонический JSON валидации Malaga Treadmill (EXP-0044 GroupKFold)](research/treadmill_cpet_2026_11_09/malaga_validation_results.json),
- [Генератор структурных таблиц отчёта Malaga CPET](tools/generate_malaga_report_tables.py),
- [Движок GroupKFold валидации Malaga Treadmill CPET](tools/evaluate_malaga_treadmill.py),
- [Тесты валидации Malaga Treadmill CPET (16 тестов, GroupKFold 0-leakage, структурные и лицензионные негативные проверки)](tests/test_malaga_cpet_validation.py),
- [Обновлённый канонический JSON ACTES CPET с анализом чувствительности эффективности (EXP-0043)](research/cpet_cycloergometer_2026_11_09/actes_validation_results.json),
- [Отчёт по валидации CPET ACTES](research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md),
- [Движок факториального анализа ACTES и оценки чувствительности эффективности](tools/evaluate_actes_models.py),
- [Тесты валидации ACTES CPET (13 тестов, проверка 37.49% кажущейся эффективности и неидентифицируемости дельта-эффективности)](tests/test_actes_cpet_validation.py),
- [Реестр эмпирических датасетов Cycle 11 с фиксацией ISS-0020](research/treadmill_cpet_2026_11_09/empirical_datasets_cycle11.json),
- [Решение DEC-0019 (Утверждение научного корригендума Cycle 11)](registry/decisions.json),
- [Проблема ISS-0020 (Тройственный лицензионный конфликт PhysioNet Malaga v1.0.1)](registry/issues.json).

Главные итоги:
1. **Ликвидация групповой утечки данных (GroupKFold по subject_id, EXP-0044)**:
   - Устранена критическая утечка: случайное разбиение тестов допускало тесты одних и тех же участников в train и test одновременно.
   - Внедрён GroupKFold по `subject_id` (n_splits=5). Программно подтверждено: $\text{intersection}(\text{train\_subject\_ids}, \text{val\_subject\_ids}) == \emptyset$ для всех фолдов.
   - Из 857 уникальных участников Malaga после фильтрации ($\ge 100$ строк, $\Delta v \ge 3$ км/ч) допущены ровно 846 участников (981 тест, 11 отсеяно).
   - Все 116 участников с повторными испытаниями (251 тест) сохранены строго внутри своих групп.
   - Распределение по фолдам: F0 (169 суб., 197 тестов), F1 (169 суб., 196 тестов), F2 (169 суб., 196 тестов), F3 (169 суб., 196 тестов), F4 (170 суб., 196 тестов).
   - Историческое разбиение сохранено как legacy-бенчмарк с меткой `SUBJECT_LEAKAGE_RISK_NOT_GROUPED`.
2. **Реконсилиация отчётов и генератор таблиц (Stage 2)**:
   - Создан `tools/generate_malaga_report_tables.py`, формирующий Markdown-таблицы напрямую из JSON.
   - Внедрена строгая валидация `verify_malaga_structural_consistency` и негативные тесты на подмену $n$, RMSE, $R^2$, bias, `model_id`.
3. **Коррекция энергетической эффективности ACTES (Stage 3, DEC-0019)**:
   - Арифметика исправлена: при $\beta_1 = 0.00765744$ л/мин/Вт и $c_{\text{ox}} = 20.9$ кДж/л кажущаяся эффективность составляет $\eta_{\text{apparent}} = 1 / (\beta_1 \cdot 348.33) \approx 37.4905\%$ (37.49%, не 25.5%).
   - Проведён анализ чувствительности (временной лаг $0\dots 60$ с, базовая линия покоя $0.35$ л/мин даёт $28.52\%$, диапазон мощности, $c_{\text{ox}} = 19.6\dots 21.3$ кДж/л).
   - Статус зафиксирован как `DELTA_EFFICIENCY_NOT_IDENTIFIABLE_FROM_UNLAGGED_RAMP`: истинная дельта-эффективность неидентифицируема без steady-state ступеней и учёта легочного лага $\tau$.
4. **Физический аудит межмодального переноса (Stage 4, NEG-0037, DEC-0019)**:
   - Формула переноса `560.0 + (7.657 * 25.0) * speed` переклассифицирована в `AD_HOC_CROSS_MODAL_MAPPING_FAILURE`.
   - В связи с отсутствием измерения механической мощности бега установлен статус `PHYSICAL_CROSS_MODAL_TRANSFER_NOT_IDENTIFIABLE`. Отрицательный результат сохранён без приписывания эвристике физического смысла.
5. **Метрологический аудит оксикалорического эквивалента (Stage 5)**:
   - Классификация: $\dot{V}\text{O}_2, \dot{V}\text{CO}_2, \text{RER}$ — `MEASURED`; $c_{\text{ox}}$ — `DERIVED_MODEL_DEPENDENT`; нестационарное окисление субстратов — `NOT INDEPENDENTLY VALIDATED`.
   - 46.8% точек с $\text{RER} > 1.0$ отражают избыточное выделение $\text{CO}_2$ при буферизации лактата гидрокарбонатом, а не истинное субстратное окисление.
   - Расхождение 2.26% со справочным $20.9$ кДж/л признано артефактом клиппирования RER.
6. **Научная генерализация и статистика (Stage 6)**:
   - Иерархия подтверждена на независимых субъектах: M4 ($R^2 = 0.6648$, RMSE $= 404.0$ мл/мин) достоверно превосходит M3 ($R^2 = 0.4837$, RMSE $= 469.9$ мл/мин, $p = 6.78 \times 10^{-26}$), M2 ($R^2 = 0.5157$, RMSE $= 514.1$ мл/мин) и M1 ($R^2 = 0.3296$, RMSE $= 570.0$ мл/мин).
   - Персистентный бейзлайн (RMSE $= 96.6$ мл/мин) чётко охарактеризован как авторегрессионный с превосходством по информации.
   - Разграничены уровни Level A (ACTES), Level B (Malaga), Level C (межмодальный перенос — неидентифицируем).
7. **Лицензионный аудит и источники (Stage 7, ISS-0020)**:
   - Зарегистрирован тройственный конфликт (PhysioNet Contributor License vs CC BY-NC-SA 4.0 vs ODC-By v1.0). Проблема открыта в `ISS-0020`.
8. **Эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`**.
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=44, FND=44, NEG=37, DEC=19, ISS=20, SRC=75.
   - Все юнит-тесты и шаги CI успешно выполняются локально.

---

# SUBJECT-01 — состояние после Cycle 10 Scientific Integrity & Cycle 11 Independent Data Expansion (EXP-0044), 09.11.2026

База: 7a1d5ba4b820ff2254e4792bedfac1d0c4c8b601;
Ветка: feature/cycle10-integrity-and-cycle11-data-expansion (слияние в main).

Ключевые артефакты Cycle 11 / Stage 1-5:
- [Отчёт по валидации беговой локомоции CPET PhysioNet Malaga (N=857)](research/treadmill_cpet_2026_11_09/TREADMILL_CPET_REPORT.md),
- [Канонический JSON валидации Malaga Treadmill (EXP-0044)](research/treadmill_cpet_2026_11_09/malaga_validation_results.json),
- [Реестр эмпирических датасетов Cycle 11](research/treadmill_cpet_2026_11_09/empirical_datasets_cycle11.json),
- [Движок валидации Malaga Treadmill CPET](tools/evaluate_malaga_treadmill.py),
- [Тесты валидации Malaga Treadmill CPET](tests/test_malaga_cpet_validation.py),
- [Генератор структурных таблиц ACTES CPET](tools/generate_actes_report_tables.py),
- [Обновлённый канонический JSON ACTES CPET (EXP-0043)](research/cpet_cycloergometer_2026_11_09/actes_validation_results.json),
- [Обновлённый отчёт по валидации CPET ACTES](research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md),
- [Обновлённая матрица остаточных барьеров](research/cpet_cycloergometer_2026_11_09/REMAINING_BARRIERS_MATRIX.md),
- [Тесты структурной согласованности ACTES (12 тестов)](tests/test_actes_cpet_validation.py),
- [Сквозной аудит Evidence Gate V2 (9/9 негативных проверок)](tools/verify_data_provenance.py).

Главные итоги:
1. **Сверка таблиц ACTES и структурная защита**:
   - 100% числовая синхронизация всех 72 ячеек таблицы 18 участников в `CPET_VALIDATION_REPORT.md` с каноническим `actes_validation_results.json` при допуске $\le 0.001$.
   - Создан инструмент `tools/generate_actes_report_tables.py` и юнит-тест `test_cpet_report_markdown_json_structural_consistency`.
   - Внедрены 4 негативных теста: перестановка участников, подмена колонок моделей, перестановка метрик RMSE $\leftrightarrow R^2$, инверсия знака $R^2$.
2. **Аудит физической идентифицируемости и метрология**:
   - Метрологически подтверждено расхождение метаданных PhysioNet ACTES (указаны $\text{mL/min}$) с реальными байтами `test_measure.csv` (значения строго в $\text{L/min}$, от $0.20$ до $4.54$).
   - Чётко разграничены инкрементальная дельта-эффективность ($\eta_{\text{delta}} = 1 / (\beta_1 \cdot 348.33) \approx 25.5\%$, константный наклон регрессии) и валовая эффективность ($\eta_{\text{gross}}(t) = P(t) / \dot{E}_{\text{met}}(t)$, зависящая от нагрузки от $0\%$ в покое до $\sim 24\%$ на максимуме). Наклон регрессии больше не отождествляется с $\eta_{\text{gross}}$.
   - Задержка кинетики $\tau$: проверена через вложенную кросс-валидацию по сетке $\{0, 10, 20, 35, 50, 65\}\text{ с}$ (оптимум $\tau = 35.0\text{ с}$ подтверждён строго внутри обучающих фолдов без утечки данных).
   - Аллометрический экспонент массы: зафиксирован как линейный ($\gamma = 1.0$).
3. **Факториальное сравнение моделей и статистическая надёжность**:
   - Оценена факториальная иерархия: M0 (константа) $\to$ M1 (линейная без массы) $\to$ M2 (линейная с массой) $\to$ M3 (ОДУ динамика без массы) $\to$ M4 (ОДУ динамика с массой), а также бейзлайны персистентности и лаговой нагрузки.
   - Непараметрический бутстреп (2000 репликаций): 95% ДИ для M4 $R^2 = [0.6401, 0.8084]$, RMSE $= [0.2642, 0.3174]\text{ л/мин}$.
   - Доказана статистическая значимость эффекта динамики ($\Delta\text{RMSE} = -0.0972\text{ л/мин}$, $p = 1.00 \times 10^{-8}$).
   - Обнаружена гетерогенная деградация линейного масштабирования массы: нормализация $P/M$ ухудшает RMSE у 7 из 18 участников (легковесные триатлеты и тяжеловесные гребцы), подтверждая ограничения простой линейной аллометрии.
4. **Независимый датасет локомоции — PhysioNet Malaga Treadmill CPET (SRC-0074, EXP-0044)**:
   - Получен датасет из $N = 992$ максимальных ступенчатых беговых тестов на тредмиле среди $N = 857$ независимых участников (575,087 записей).
   - Проверены контрольные суммы SHA256 по `SHA256SUMS.txt`: `test_measure.csv` (`3b5ed558...`), `subject-info.csv` (`e9ca5ba2...`), `LICENSE.txt` (`92905d58...`).
   - Анализ дыхательного коэффициента (RER) и субстратного окисления: средний эмпирический оксикалорический эквивалент составил $c_{\text{ox}} = 21.37\text{ кДж/л O}_2$, что с точностью до $2.26\%$ подтверждает теоретическое значение $20.9\text{ кДж/л O}_2$.
   - 5-фолдовая аут-оф-сэмпл валидация подтвердила общность кардиореспираторной ОДУ: M4 аллометрическая ОДУ ($R^2 = 0.6712$, RMSE $= 404.5\text{ мл/мин}$) превосходит M3 ($R^2 = 0.4956$), M2 ($R^2 = 0.4431$), M1 ($R^2 = 0.3413$) и M0 ($R^2 = -0.6193$).
5. **Отрицательный результат межмодального переноса (NEG-0037)**:
   - Прямой перенос параметров велоэргометрии (наклон $\beta_1$) на бег на тредмиле терпит крах (штраф RMSE $+179.1\text{ мл/мин}$, падение $R^2$ с $0.6712$ до $0.3727$) из-за рекуперации упругой энергии ахиллова сухожилия и вертикальных колебаний центра масс при беге.
   - Решение `DEC-0018`: запретить перенос биоэнергетических параметров между модальностями без биомеханического моделирования беговой экономичности.
   - Аудит датасета Hug 2015 на Dryad (`SRC-0075`): метаданные подтверждены; скачивание через CLI заблокировано интерактивным антибот-челленджем Cloudflare/Anubis BotStopper.
6. **Незыблемые эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`** (тесты до отказа на тредмиле $8\dots 18$ минут не валидируют 45-минутный критический стресс).
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=44, FND=44, NEG=37, DEC=18, ISS=19, SRC=75.
   - Тесты: 87/87 unit tests PASS (13 ACTES, 7 Malaga, 13 Rehman, и др.), Evidence Gate V2 (9/9 негативных проверок).

---

# SUBJECT-01 — состояние после EXP-0042 Final Numerical Lock & Cycle 10 Multi-Subject CPET Validation (EXP-0043), 09.11.2026

База: 7ee8c127dad2a56bef4427c8e9e5777bdc385b8c;
Ветка: feature/exp-0042-lock-and-cycle10-data-acquisition (слияние в main).

Ключевые артефакты Cycle 10:
- [Отчёт по валидации CPET PhysioNet ACTES (N=18)](research/cpet_cycloergometer_2026_11_09/CPET_VALIDATION_REPORT.md),
- [Канонический JSON валидации ACTES (EXP-0043)](research/cpet_cycloergometer_2026_11_09/actes_validation_results.json),
- [Систематический рейтинг и аудит датасетов](research/cpet_cycloergometer_2026_11_09/DATASET_RANKING.md),
- [Матрица остаточных барьеров и неидентифицируемости M3](research/cpet_cycloergometer_2026_11_09/REMAINING_BARRIERS_MATRIX.md),
- [Движок мультисубъектной валидации CPET](tools/evaluate_actes_models.py),
- [Тесты валидации ACTES CPET](tests/test_actes_cpet_validation.py),
- [Реестр эмпирических датасетов Cycle 10](research/cpet_cycloergometer_2026_11_09/empirical_datasets_cycle10.json),
- [Канонический отчёт валидации Rehman 2024 (EXP-0042 Locked)](research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md),
- [Канонический JSON валидации Rehman (EXP-0042 Locked)](research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json),
- [Генератор структурных таблиц Rehman](tools/generate_rehman_report_tables.py),
- [Сквозной аудит Evidence Gate V2](tools/verify_data_provenance.py).

Главные итоги:
1. **EXP-0042 Final Numerical Lock**:
   - Канонические значения базового PCr зафиксированы: Trial 1 = $2481.43 \pm 74.26$, Trial 2 = $1679.00 \pm 38.71$, Trial 3 = $1675.57 \pm 34.21$.
   - Канонические значения M2 $k$: Trial 1 = $1.2979\text{ мин}^{-1}$, Trial 2 = $1.1469\text{ мин}^{-1}$, Trial 3 = $0.9696\text{ мин}^{-1}$.
   - Примитивный `assertIn` заменён глубоким структурным парсером Markdown $\leftrightarrow$ JSON с 3 негативными тестами на перестановку строк, подмену метрик и посторонние цифры в тексте.
   - Статус: `EXP-0042_NUMERICALLY_LOCKED`.
2. **Cycle 10 Data Acquisition (PhysioNet ACTES Cycloergometer, SRC-0073)**:
   - Преодолён барьер единичного субъекта ($N=1$): получен датасет из $N = 18$ независимых спортсменов-подростков (фехтование, гребля на байдарках, триатлон).
   - 52,062 синхронизированных beat-to-beat наблюдений механической мощности ($P_{\text{mech}}$ в Вт), потребления кислорода ($\dot{V}\text{O}_2$ в л/мин) и кардиоинтервалов ($RR$ в мс).
   - Полное байтовое совпадение SHA256: `test_measure.csv` (`14a9df02...`), `subject-info.csv` (`5ac7cdd4...`), `LICENSE.txt` (`86c0ad30...`). Лицензия ODC-By v1.0.
3. **Первая независимая мультисубъектная верификация (EXP-0043)**:
   - Проведён строгий Leave-One-Subject-Out (LOSO) кросс-валидационный тест на всех 18 участниках без утечки таргета.
   - Динамическая биоэнергетическая ОДУ с аллометрическим масштабированием по массе тела ($P/M \to \dot{V}\text{O}_2/M$) показала кросс-субъектный $R^2_{\text{LOSO}} = 0.7371 \pm 0.1770$ (RMSE $= 0.290 \pm 0.059\text{ л/мин}$), значительно превосходя эмпирическую статическую линейную M1 ($R^2 = 0.4045$, RMSE $= 0.416\text{ л/мин}$) и константную M0 ($R^2 = -0.8343$, RMSE $= 0.773\text{ л/мин}$).
4. **Матрица остаточных барьеров (`REMAINING_BARRIERS_MATRIX`)**:
   - Валидация макроскопического аэробного сопряжения ($\dot{E}_{\text{met}} = P_{\text{mech}} / \eta$) НЕ означает валидацию внутриклеточных микросостояний ([PCr], [Pi], [ATP], pH) и рекрутирования двигательных единиц.
   - В силу проблемы «многие-к-одному» (entanglement fallacy), системный $\dot{V}\text{O}_2$ не идентифицирует компартментные профили.
5. **Незыблемые эпистемические инварианты**:
   - `TARGET-CPE45`: **`NOT EXTERNALLY VALIDATED`** (15-минутный ступенчатый тест до отказа не валидирует 45-минутный экстремальный стресс).
   - Биологические вмешательства: **`NO_GO`**.
   - Реестры: HYP=8, EXP=43, FND=43, NEG=36, DEC=17, ISS=19, SRC=73.
   - Тесты: 74/74 PASS (включая 13 тестов Rehman и 7 тестов ACTES CPET), Evidence Gate V2 (8/8 негативных проверок).

---

# SUBJECT-01 — состояние после EXP-0042 Scientific Corrigendum & Model Integrity, 09.11.2026

База b98c3eb68654dc8f22ce1dd64be70c3b45528623;
ветка fix/exp-0042-scientific-corrigendum (слияние в main).
[Научный отчёт по валидации и заморозке реальных данных (Corrigendum)](research/empirical_recruitment_2026_11_08/REAL_DATA_VALIDATION_REPORT.md),
[канонический артефакт валидации](research/empirical_recruitment_2026_11_08/rehman2024_validation_results.json),
[движок валидации моделей Rehman](tools/evaluate_rehman_models.py),
[тесты валидации моделей Rehman](tests/test_rehman_model_validation.py),
[Отчёт EXP-0037..0042](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[извлечённый канонический временной ряд Rehman 2024](research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Завершён научный корригендум EXP-0042, устранивший несоответствия между отчётами и каноническим JSON:
1. **Числовая сверка отчёта и JSON**: проверенные амплитуды PCr на 90 с: T1=1920.0, T2=1291.0, T3=1277.0; в надире: T1=1670.0 (144 с), T2=1245.0 (108 с), T3=1231.0 (108 с). Фактические in-sample RMSE: M0=(230.88, 120.21, 141.69); M1=(26.05, 15.73, 14.70); M2=(31.72, 37.67, 32.80). Для M0 $R^2$ строго отрицательный (-0.553, -1.130, -0.962). Добавлен автоматический тест `test_report_markdown_json_consistency`.
2. **Аудит тайминга и физиологических меток**: номинальные $t_{\text{start}}=48\text{ с}$ и $t_{\text{stop}}=90\text{ с}$ классифицированы как `INFERRED_TIMING_ASSUMPTION` (аудиокоманды оператора, отсутствие аппаратного TTL). Надир классифицирован как `OBSERVED_SPECTRAL_MINIMUM_DISTINCT_FROM_MECHANICAL_STOP`. Термины «ишемический/гиперемический лаг» исключены из категорических выводов при отсутствии данных плетизмографии/кровотока.
3. **Ретракция утверждения о pH**: утверждение «$\text{pH} \ge 6.86$ во всех триалах» официально отозвано как устаревшее; фактический минимум pH составляет 6.7932 в триале 1 (диапазон расчётного pH: $6.7932\dots 7.0228$). Статус `PH_CALIBRATION_PARTIAL` сохранён без искусственных поправок. Категорические утверждения о нулевом протонном ингибировании без анализа газов крови и лактата запрещены.
4. **Реклассификация модели M2 и статус M3**: M2 реклассифицирована в `CONSTRAINED_MONOEXPONENTIAL_BASELINE` ($d\text{PCr}/dt = k \cdot (\text{PCr}_{\text{rest}} - \text{PCr})$). Запрещены утверждения о валидации баланса энергий, кислородного транспорта или двигательных единиц на M2. Полная физиологическая модель M3 получила статус `M3_NOT_EXECUTABLE_ON_AVAILABLE_OBSERVATIONS` из-за отсутствия механической мощности, момента силы, объёма мышцы и спирометрии в Rehman 2024.
5. **Разграничение режимов переноса**: Сценарий A (`CONDITIONAL_TRAJECTORY_RECONSTRUCTION`, при известных надире и базовом уровне) подтверждён (M2 средний переносный $R^2 = 0.8566$, M1 — $0.8268$). Сценарий B (`PROSPECTIVE_PREDICTION`, прогноз от 90 с без знания будущего надира и динамики истощения) строго заблокирован: `PROSPECTIVE_PREDICTION_BLOCKED_UNOBSERVED_DEPLETION_DYNAMICS`.
6. **Кросс-субъектный LOSO**: на $N=1$ строго запрещён (`LosoProhibitedError`).

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=42, FND=42, NEG=35, DEC=16, ISS=19, SRC=72.
- Тесты: 207/207 PASS (включая 10 тестов валидации моделей Rehman).

---

# SUBJECT-01 — состояние после Rehman 2024 Real XLSX Format Hotfix, 09.11.2026

База 5f2846cbf025efe7a747dbcf6a2355dedabcb5b6;
ветка fix/rehman-real-xlsx-format-hotfix.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[модуль OOXML stdlib](tools/rehman_ooxml.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[извлечённый канонический временной ряд Rehman 2024](research/empirical_recruitment_2026_11_08/rehman2024_extracted_timeseries.json),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Адаптация процессора к реальному формату Dryad XLSX и извлечение временных рядов:
- Файл `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18,136 байт, SHA256 `ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`) получен по owner-assisted протоколу.
- Реализован разбор структуры листа `2024_829_DiB_Raw` с 18 колонками, сгруппированными тремя блоками по 6 колонок (`1.*`, `2.*`, `3.*`).
- Извлечены 222 спектра (3 триала по 74 валидные точки с шагом 6.0 с, диапазон 12.0–450.0 с; предскановый спектр 1 исключён).
- Фит кинетики восстановления фосфокреатина:
  * Trial 1: $k = 1.393 \pm 0.119\text{ мин}^{-1}$ (опубликовано $1.43$, расхождение $-2.57\%$), $\tau = 43.07\text{ с}$, $R^2 = 0.9802$, RMSE = $26.05$, надир в спектре 24 ($144\text{ с}$).
  * Trial 2: $k = 1.686 \pm 0.180\text{ мин}^{-1}$ (опубликовано $1.62$, расхождение $+4.09\%$), $\tau = 35.58\text{ с}$, $R^2 = 0.9635$, RMSE = $15.73$, надир в спектре 18 ($108\text{ с}$).
  * Trial 3: $k = 1.480 \pm 0.121\text{ мин}^{-1}$ (опубликовано $1.53$, расхождение $-3.24\%$), $\tau = 40.53\text{ с}$, $R^2 = 0.9789$, RMSE = $14.70$, надир в спектре 18 ($108\text{ с}$).
  * Среднее: $k = 1.520 \pm 0.151\text{ мин}^{-1}$ (опубликовано $1.53 \pm 0.10\text{ мин}^{-1}$, расхождение $-0.65\%$), $\tau = 39.72\text{ с}$, CV% = $9.90\%$ (опубликованная ошибка: $\pm 6.5\%$).
- Внутриклеточный pH рассчитан из химических сдвигов ($\delta_o = \delta_{\text{Pi}} - \delta_{\text{PCr}}$) по уравнению PMC11617988 Fig. 7 без искусственных констант (покой $6.91\dots 6.96$, конец нагрузки $6.92\dots 6.98$, конец восстановления $6.86\dots 6.93$).
- Канонический артефакт извлечения `rehman2024_extracted_timeseries.json` сохранён в репозитории (SHA256: `af6a396b006a6cb791844742085701c6782b4eb706a8f768b1bd87dfa7e8de5b`, 41,368 байт). Бинарный XLSX файл оставлен в `.gitignore` до разрешения лицензии.
- Батарея тестов `tests/test_rehman_xlsx_processor.py` расширена до 17 тестов (100% PASS).
- Кросс-субъектный LOSO на когорте $N=1$ строго запрещён.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 197/197 PASS (все тестовые наборы репозитория, включая 17 тестов процессора Rehman и 12 тестов Evidence Gate V2).

---

# SUBJECT-01 — состояние после Research Cycle 9 (CI Failure, Strict JSON & Real-Data Pipeline Repair), 09.11.2026

База 19402484b0295c46ae03d5dab47a363f89cf5795;
ветка fix/ci-failure-and-real-data-pipeline-repair.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[сквозной гейт Evidence Gate V2](tools/verify_data_provenance.py),
[пайплайн обработки Rehman XLSX](tools/process_rehman_xlsx.py),
[модуль OOXML stdlib](tools/rehman_ooxml.py),
[тесты процессора Rehman XLSX](tests/test_rehman_xlsx_processor.py),
[набор тестов Evidence Gate V2](tests/test_evidence_gate_v2.py),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Ремонт CI, байтового происхождения, строгого JSON и процессора первичных данных:
- CI Failure & Byte Provenance Repair (GitHub Actions run 42654714327):
  * Выявлена первопричина падения шага `Structural and hash audit`: расхождение окончаний строк CRLF на Windows и LF в Git/Linux из-за отсутствия конфигурации `.gitattributes` для Циклов 7, 8, 9, `registry/`, `tools/`, `tests/`.
  * `.gitattributes` дополнен правилом `* text eol=lf` для всех репозиторных текстовых файлов с сохранением binary-маркировки (`-text`) для исторических CSV Foundation.
  * Файлы приведены к каноническим байтам:
    - Franke 2020 JSON: 3049 байт (LF), SHA256 `0345c4a8b36c95d9641c52bc96b759a43e6f899d186159606481060fbb437fa2`, классифицирован как `DERIVED_EXTRACTION_JSON` (извлечённые координаты 3D МРТ-сегментации, а не сырой MAT-файл).
    - Rehman 2024 XML: 42824 байта (LF), SHA256 `d8f1df9664c94b4846da3c015ced45310bc17ea1f48b58ce287c61db6bd1ed2c`, классифицирован как `PUBLISHED_TABLE_DATA`.

- Завершение процессора сырых данных Rehman 2024 (`tools/process_rehman_xlsx.py`):
  * Разработан легковесный OOXML-модуль `tools/rehman_ooxml.py` на базе `zipfile` и `xml.etree.ElementTree` (zero external dependencies, независим от отсутствующего `openpyxl`).
  * При отсутствии оригинального файла возвращает `PENDING_RAW_DATA` (без ложного PASS).
  * При наличии файла выполняет: проверку байтового SHA256 (`ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`), разбор структуры листов и колонок, извлечение 3 триалов по 75 спектральных точек (разрешение 6 с), моноэкспоненциальный фит кинетики PCr и Pi с 95% доверительными интервалами, сравнение с опубликованными Table 1 константами $k = 1.43, 1.62, 1.53\text{ мин}^{-1}$, оценку внутрисубъектной воспроизводимости (repeatability CV%) и строгий запрет кросс-субъектного LOSO при $N=1$.
  * Создан полный тестовый набор `tests/test_rehman_xlsx_processor.py` (8 тестов, включая негативные проверки на пустую книгу, повреждённые колонки, неверный хеш и неполные триалы). Тест добавлен в `.github/workflows/validate.yml`.

- Модернизация Evidence Gate V2 (`tools/verify_data_provenance.py`):
  * Установлено правило сквозной верификации байтового хеша: если запись ссылается на локальный файл и указывает SHA256, байтовый хеш проверяется независимо от категории данных.
  * Введены типизированные категории: `ORIGINAL_BINARY_FILE`, `DERIVED_EXTRACTION_JSON`, `PUBLISHED_TABLE_DATA`, `LITERATURE_REFERENCE_WITHOUT_FILE`, `SYNTHETIC_MODEL_SIMULATION`.
  * Реализован глобальный аудит на соответствие RFC 8259: токены `Infinity`, `-Infinity` и `NaN` устранены во всех JSON-файлах репозитория (неопределённые числа обусловленности заменены на `null` со статусом `"INFINITE"`).
  * Отрицательная батарея тестов расширена до 7 проверок (добавлены подмена хеша в `PUBLISHED_TABLE_DATA` и обнаружение невалидных токенов JSON).

- Уточнение статуса научных утверждений TARGET-CPE45:
  * Значения 3300 кДж окислительного ресинтеза и 75 кДж гликолитического вклада строго задокументированы как `ESTIMATED_SCENARIO_BALANCE_NOT_MEASURED` (сценарный расчёт при допущении $\eta_{\text{gross}} = 20\%$, а не эмпирическое измерение в CPE45).
  * Аэробная фракция зафиксирована как `measured_empirical_aerobic_fraction: null`, статус: `NOT_EMPIRICALLY_MEASURED_IN_CPE45`.
  * Статус `TARGET-CPE45` неизменен: `NOT EXTERNALLY VALIDATED`, биологические вмешательства — `NO_GO`.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=34, DEC=15, ISS=19, SRC=72.
- Тесты: 188/188 PASS (все тестовые наборы репозитория, включая 8 тестов процессора Rehman и 12 тестов Evidence Gate V2).

---

# SUBJECT-01 — состояние после Research Cycle 9 (Data Integrity Repair & Evidence Gate Installation), 08.11.2026

База 9271a1eabbd8405f7152c151c52047ce54312c38;
ветка correction/cycle9-raw-data-integrity-gate.
[Отчёт EXP-0037..0041](research/empirical_recruitment_2026_11_08/REPORT.md),
[математика и биофизика рекрутирования](research/empirical_recruitment_2026_11_08/MATHEMATICS.md),
[модель физических измерений](research/empirical_recruitment_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_recruitment_2026_11_08/DATA_AUDIT.md),
[ограничения и межмышечные барьеры](research/empirical_recruitment_2026_11_08/LIMITATIONS.md),
[постоянный гейт данных](tools/verify_data_provenance.py),
[reproduction](research/empirical_recruitment_2026_11_08/README.md).

Устранение синтетической валидации, аудит первичных данных и установка Evidence Gates:
- Этап 0 (Preflight): строго разграничены свободная энергия Гиббса Delta_G_ATP = 54.0 кДж/моль (максимальная механическая работа мостиков) и калориметрическая энтальпия Delta_R H = 21.0 кДж/моль (тепловыделение). Отношение 2.5714 отражает энтропийный вклад. Статус значений покоя (2.4 мл/100г/мин и 58 мл/л) в SRC-0066 понижен до DOWNGRADED_NOT_PRIMARY_RESTING_TABLE / LITERATURE_REVIEW_TRANSFER_ASSUMPTION (Таблица 2 Andersen & Saltin 1985 начинается с 10 Вт, строки 0 Вт нет).
- Аудит первичных данных человека (EXP-0037):
  1) Матричная HD-sEMG (Hug et al. 2021, Figshare 10.6084/m9.figshare.13695937, SRC-0068): литературные агрегаты частот разряда ДЕ по 8 операторам (9.8-19.8 Гц) для 1 испытуемого (8 операторов != 8 испытуемых). Программная загрузка архива 444 МБ заблокирована Cloudflare R2 (HTTP 403 Forbidden).
  2) Динамическая 31P-MRS квадрицепса (Rehman et al. 2024, PMC11617988, SRC-0069): опубликованы 3 скалярные кинетические константы в Таблице 1 (tau = 39.2 +- 2.5 с, pH = 7.01 +- 0.03). Программная загрузка спектрального файла 2024_829_Ergometer_Dryad_Raw_V3.xlsx заблокирована AWS WAF бот-челленджем (HTTP 403 Forbidden). Статус: RAW_TIMESERIES_UNAVAILABLE. Синтетических заменителей не создавалось.
  3) Томография: когортные таблицы SRC-0070 (MuscleMap) и SRC-0071 (Cenni) отозваны; статус EMPIRICALLY_BOUNDED_DISTRIBUTION аннулирован. Верифицирован первичный объём GM Subject 01 Franke 2020 (379.89 мл).
- Биофизическая модель рекрутирования (EXP-0038): статус COMPUTATIONAL_SIMULATION_HYPOTHESIS. Сценарные параметры (500 ДЕ, -35% силы) строго отделены от модельных следствий (+14% sEMG RMS при утомлении, 40.9x диапазон чувствительности a_eff к жировому слою 3-10 мм).
- 4-уровневая идентифицируемость (EXP-0039): Уровень 1 (структурный ранг P8 = 7/7); Уровень 2 (локальный ранг дефектен); Уровень 3 (с 12 мешающими параметрами эффективный ранг 5/12, дефект = 7); Уровень 4 (NOT_EMPIRICALLY_IDENTIFIED_CROSS_STUDY_DISCONNECTION).
- Ликвидация фейковой валидации LOSO (EXP-0040): отозвана эмпирическая валидация человека, так как кривые генерировались через np.random.RandomState. EXP-0040 и FND-0040 переведены в SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED, эмпирическая валидация переведена в BLOCKED_PENDING_RAW_DATA.
- Физический баланс энергии CPE45 (EXP-0041): строго разделены внешняя работа (250 Вт * 2700 с = 675 кДж), валовой метаболический расход (~3375 кДж при eta_gross ~20%), локальный буфер PCr (0.11-0.39 кДж в активном объёме голени; 0.62 кДж во всей GM) и тепловыделение (Delta_R H = 21.0 кДж/моль). Устранено бессмысленное прямое деление локального буфера на внешнюю работу. Экстраполяция на всё тело заблокирована.
- Постоянный гейт происхождения данных: внедрён tools/verify_data_provenance.py (проверка 11 обязательных полей, запрет EXTERNALLY_VALIDATED для синтетических данных, аудит скриптов на генерацию y_true). Интегрирован в tools/validate_repository.py.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Реестры: HYP=8, EXP=41, FND=41, NEG=32, DEC=15, ISS=19, SRC=72.
- Тесты: 171/171 PASS (все тестовые наборы репозитория).

---

# SUBJECT-01 — состояние после Research Cycle 8 (Empirical Validity Correction), 08.11.2026

База 9bf0468754a756cca283fd41a84036b4d0c78cf3;
ветка correction/cycle8-validity-repair-20261108.
[Отчёт EXP-0032..0036](research/empirical_anchors_2026_11_08/REPORT.md),
[математика и физические отображения](research/empirical_anchors_2026_11_08/MATHEMATICS.md),
[модель измерений](research/empirical_anchors_2026_11_08/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/empirical_anchors_2026_11_08/DATA_AUDIT.md),
[ограничения и протокол отзыва](research/empirical_anchors_2026_11_08/LIMITATIONS.md),
[reproduction](research/empirical_anchors_2026_11_08/README.md).

Эмпирические физиологические якоря и аудит научной достоверности:
- Первичные данные 3D T1-МРТ (Franke et al. 2020, PMC7332772, DOI 10.3389/fbioe.2020.00622): анатомический объём медиальной икроножной мышцы строго измерен и равен 379.89 мл (масса 0.3587 кг, PCSA 58.98 см2, F_max = 1474 Н).
- Экспериментальное разделение и аудит sEMG: МРТ, кинематика с sEMG (снаружи томографа при 2 кГц, интерполировано до 4 кГц в MAT) и 31P-MRS (внутри томографа) измерялись в отдельных сессиях. Доказано, что sEMG RMS=12.7% не измеряет долю активных волокон. Диапазон V_active in [83.6, 144.4] мл является сценарной гипотезой (SCENARIO_HYPOTHESIS). Подмена V_active анатомическим объёмом в рамках сценария занижает плотность потока АТФ в 2.63-4.55 раза.
- Когортное распределение фосфагенов покоя: Edwards et al. 2013 (PMC3560356, DOI 10.1038/srep01182, InSight trial, n=89; первый автор Edwards LM, а не Sleigh): PCr/gamma-ATP = 4.10 +/- 0.03. Принятие консенсуса [ATP]_ref in [6.5, 9.5] мМ (Meyerspeer et al. 2021, PMC8243949, DOI 10.1002/nbm.4246) даёт [PCr]_rest in [26.7, 39.0] мМ.
- Термодинамическая метрология: строго разграничены тепловая энтальпия реакции Delta_R H (21.0 кДж/моль, Kodama 1985) и свободная энергия Гиббса Delta_G_ATP (-54.0 кДж/моль). Множитель 2.5714 отражает отношение потенциалов, но не переводит автоматически тепло в мощность без аудита модели. Синхронизирована ёмкость буфера PCr: строго 111.4-947.0 Дж (8.50-кратный размах).
- Базовый расход покоя M_loc: значения 2.4 мл/100г/мин и (Ca - Cv)O2 = 58 мл/л измерены на четырёхглавой мышце бедра (Andersen & Saltin 1985, DOI 10.1113/jphysiol.1985.sp015794). Их перенос на икроножную мышцу реклассифицирован как MODEL_ASSUMED_QUADRICEPS_TRANSFER. Некалиброванные ASL (2.25x) и NIRS (6.67x) изолировать M_loc не способны.
- Физическая идентифицируемость (3 уровня): идеализированные скалярные каналы y = theta_j удалены. Уровень 1: условный математический полный ранг (P8 = 7/7, kappa_eff = 15.39 при замороженных константах). Уровень 2: при неизвестных nuisance-параметрах (a_eff, g_nirs, b_nirs, k_spec) 11D система имеет эффективный ранг 7/11 (дефект = 4) с плоскими хребтами. Уровень 3: на реальных человеческих данных модель NOT_EMPIRICALLY_IDENTIFIED из-за отсутствия синхронных мультимодальных записей.
- Изоляция макромодели D2: прямой перенос параметров отвергнут (отношение масс 50.2, отношение BMR 1543). 9D quotient модели D2 сохранён в неизменном виде.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: HYP=7, EXP=36, FND=37, NEG=28, DEC=14, ISS=19, SRC=67.
- Тесты: 162/162 PASS (все suites репозитория).

---

# SUBJECT-01 — состояние после Research Cycle 7 (Identifiability Repair & Final Consistency Audit), 08.11.2026

База c1e75ca293ad385efa25a74843431870dda162ad;
ветка correction/cycle7-identifiability-repair-20261108.
[Отчёт EXP-0027..0031](research/local_muscle_bridge_2026_11_07/REPORT.md),
[математика и симметрии](research/local_muscle_bridge_2026_11_07/MATHEMATICS.md),
[модель измерений](research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md),
[метрология и аудит данных](research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md),
[ограничения и протокол отзыва](research/local_muscle_bridge_2026_11_07/LIMITATIONS.md),
[reproduction](research/local_muscle_bridge_2026_11_07/README.md).

Ремонт модели идентифицируемости и согласование рангов:
- Устранено критическое несоответствие между математической документацией Cycle 7 (заявлявшей ранг 9/9 на девяти параметрах) и фактически вычисленными рангами: модель измерительного моста `LocalBridgeModel` параметризована 7 физиологическими параметрами ($\theta \in \mathbb{R}^7$), а не 9 эффективными параметрами макромодели D2 (Cycle 5).
- Механическая мощность $P_{\text{ext}}$ верифицирована как заданный вход эргометра ($\text{rank } M1 = 0/7$, так как $\partial P_{\text{ext}} / \partial \theta \equiv 0$).
- Устранён баг пропуска активного объёма в M6 (несовпадение ключа `_vol_` и `volume`) через переход на явные структуры каналов наблюдения `TOPOLOGY_CHANNELS`.
- Введена поблочная масштабная нормировка матрицы Якоби (dimensionless RMS sensitivity), устранившая численное подавление одиночных параметров ($M_{\text{loc}}$).
- Точные воспроизводимые ранги: M1 = 0/7, M2 = 3/7, M3 = 4/7, M4 = 3/7, M5 = 4/7, M6 = 5/7, M7 = 6/7. Ранг 6/7 в конфигурации M7 математически обусловлен неустранимой скалярной коллинеарностью $(\eta_{\text{loc}} \cdot \Delta G_{\text{ATP}})$ в механическом спросе АТФ.

Энергетическая метрология и термодинамика:
- Строго разграничены энергетические эквиваленты: $\Delta G_{\text{ATP}}$ ($-50 \dots -64$ кДж/моль, номинал $-54$ кДж/моль), $\Delta G_{\text{PCr}}$ ($-34 \dots -45$ кДж/моль) и креатинкиназное равновесие $\Delta G_{\text{CK}} = \Delta G_{\text{PCr}} - \Delta G_{\text{ATP}} \approx -10 \dots -15$ кДж/моль.
- Буферная ёмкость PCr: $204.8 \dots 1021.4$ Дж выражает доступный метаболический эквивалент через сопряжённую систему CK-ATPase ($|\Delta G_{\text{ATP}}| \in [50, 64]$ кДж/моль). При расчёте по чистому гидролизу PCr пул составляет $139 \dots 718$ Дж.
- Импульсное отношение работы 5 с к распаду PCr ($0.44 \dots 1.50$) классифицировано как диагностический артефакт неполного баланса и занижения активного объёма, а не нарушение закона сохранения энергии или КПД $> 100\%$.
- Зафиксирована мультимодальность калибровки: $V_{\text{active}}$ ($T_2^*$-МРТ, DCE-МРТ, УЗИ + HD-sEMG); $M_{\text{loc}}$ (катетеризация $(C_a - C_v)O_2$, ASL-МРТ, окклюзионный NIRS).
- Доказана структурная идентифицируемость задержки транспорта и постоянной времени ткани ($\kappa_{\text{FIM}} = 6.89$). Отрицательная корреляция $r = -0.709$ является фактором расширения доверительных интервалов под действием дыхательного шума.

Финальный аудит согласованности и устранение расхождений:
- Устранены числовые противоречия между отчётом и кодом: чувствительность асимптоты строго [-22.9%, +20.9%] (точно: -22.867%..+20.862%); смещение от гетерогенности волокон строго 10.6% (точно: 10.5996%); детерминированный сценарный диапазон паразитарных затрат строго 42.8%-77.1% (номинал 66.3%). Термин «доверительный интервал» исключён.
- Неверифицированные эмпирические заявления R2=0.919, R2=0.978 и наклон регрессии «14 с / 0.1 pH» ОТОЗВАНЫ как артефакты ручной графической оцифровки Fig 3-5. Восстановлены рецензированные литературные результаты Moll et al. 2017: R2=0.73 (p<0.005, n=10) для tau_PCr vs pH; R2=0.55 (p=0.01, n=10) для tau_VO2 vs tau_PCr; R2=0.65 (p<0.01, n=9) для excess CO2 vs pH.
- Изоляция исследований: данные Cannon et al. 2014 Table 1 (PMC4262339) получены на четырёхглавой мышце при bilateral knee extension (двустороннее разгибание коленей) и качественно доказывают преобладание окислительного ресинтеза (88-95%) над гидролизом PCr (1.5-3.0%); количественные скорости оборота (мМ/мин) не переносятся на икроножную мышцу когорты Moll без калибровки.
- EXP-0031 ОТОЗВАН: заявление о превосходстве локальной модели по RMSE 0.65 Вт аннулировано из-за захардкоженных прогнозов, in-sample константы и выборки N=2.
- Параметры D2 не объявляются идентифицированными через наблюдение коррелятов в мосту; математические тесты рангов не объявляются физиологической валидацией на людях.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=13, ISS=18, SRC=62.
- Тесты: 155/155 PASS (14 тестов Cycle 7 Local Muscle Bridge + все suites репозитория).

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
