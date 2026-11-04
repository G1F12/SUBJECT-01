# Матрица наблюдаемости

Каждая ячейка характеризует **параметр**, а не наличие прибора. D — прямой
показатель указанного endpoint; I — косвенное ограничение; A — требует
дополнительных предпосылок; N — отдельно неидентифицируемо этим каналом.
D/A не означает, что модельный параметр уже измерен. Ошибка и перенос
каждой ячейки задаются соответствующей строкой E1..E9 и столбцом T1..T7 ниже.
Никакой fitted state не маркируется прямым измерением.

| Наблюдение | Ёмкости T1 | КПД T2 | Oxidative kinetics T3 | Release power T4 | Recovery rate T5 | Peripheral fatigue T6 | Rest cost T7 |
|---|---|---|---|---|---|---|---|
| Power E1 | I/A | N | I/A | I/A | I/A | I/A | N |
| Relative PCr E2 | N | N | I/A | I/A | D/A | N | N |
| Absolute PCr concentration E3 | I/A | I/A | I/A | I/A | D/A | N | N |
| Continuous VO2 E4 | I/A | I/A | D/A | I/A | I/A | N | I/A |
| Independent total metabolic cost E5 | I/A | I/A | I/A | I/A | I/A | N | D/A |
| Active muscle mass/volume E6 | I/A | N | I/A | N | N | N | I/A |
| MVC/twitch E7 | N | N | N | I/A | I/A | D/A | N |
| Temperature E8 | N | N | N | N | I/A | I/A | I/A |
| Recovery kinetics E9 | I/A | N | I/A | N | D/A | I/A | I/A |

E1: W, timing/cadence/ergometer calibration и baseline noise. Нет chemical scale
или наблюдения латентного demand. Только сопоставимая механическая задача.
E2: coil sensitivity, saturation, motion и partial volume; dimensionless.
Прямая форма PCr recovery — endpoint, τD2 требует observation map и pH control.
E3: добавляются ATP/reference calibration, active water volume и ΔG/enthalpy.
Концентрация не равна totalJ; другой voxel не гарантирует whole-limb reserve.
E4: gas calibration, breath noise, cardiopulmonary delay, oxygen storage,
RER и locality. Pulmonary kinetics непосредственно наблюдаемы; muscle τo условна.
E5: calorimetry/integration/baseline/internal work и анаэробные составляющие.
Cost рассчитанная из PCr или того же fit не создаёт независимого канала.
E6: MRI segmentation, recruitment, cell-water fraction; anatomical volume
не всегда active volume. Ошибка gain систематическая и не исчезает от повторов.
E7: stimulation calibration, potentiation, electrode placement и voluntary
activation. Twitch предпочтительнее одного voluntary MVC для периферического
endpoint; central contribution и task transfer требуют отдельной проверки.
E8: sensor/site lag, skin/core/muscle mismatch и heat transport. Температура
не равна heat production и не измеряет energy reserve/η.
E9: sampling/window truncation, initial depletion, asymptote, timing и pH.
Output recovery, PCr recovery, VO2 off-kinetics и twitch recovery — разные endpoints.

T1: интеграция flux и абсолютный запас, разграничение fast/slow pathways;
S(k) исключает отдельные Ci без anchor. T2: нужен независимый total cost при
известной mechanical/internal work; transfer η между задачами не задан.
T3: нужны onset/off transitions и известная tissue allocation/measurement delay.
T4: нужны depletion/release-limited участки и временное разрешение внутри усилия;
mean-power не равна peak cap. T5: нужны разные известные дефициты и rest windows,
разделение surplus-limited и deficit-limited восстановления. T6: независимая
contractile measure, отделение активации и энергетики, валидная fatigue map.
T7: absolute resting flux и совпадающая активная/пассивная задача; B(b) сохраняется
по power/PCr даже при абсолютном Ef. Эти условия применяются ко **всем** ячейкам
соответствующего столбца; N не получает finite measurement error или CI.

Минимум информации зависит от вопроса: для power prediction достаточно
проверяемых effective combinations при информативном протоколе. Для раздельной
физиологии нужны два абсолютных anchors (scale и baseline), а для механизма —
также независимые state trajectories. Ни одна таблица не утверждает, что такие
каналы уже доступны совместно в полученных человеческих данных.
