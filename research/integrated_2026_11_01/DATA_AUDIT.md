# Аудит данных калибровки

Дата доступа и снимка: **01.11.2026**. Полные записи DOI, PMCID, версии, URLs,
SHA256 полученных XML/метаданных и результаты notices находятся в sources.json.
Повторный сетевой доступ: `python research/integrated_2026_11_01/fetch_sources.py`.
Сырые ответы остаются в игнорируемой tmp; текущие числовые факты и SHA сохранены
в Git. Обновившийся XML/индекс может иметь другой hash — это требует сверки,
а не перезаписи калибровки. Репликация модели работает без сети.

| ID | Выборка и метод | Использование и ограничения |
|---|---|---|
| SRC-0001 | 30 исследований; косвенная in-vivo оценка specific tension | 268 kPa, IQR 200–430; targeted discussion/table, вариабельность методик не CI. |
| SRC-0018 | 41 взрослый; 35/60/85 W по 4 мин, 60 rpm, indirect calorimetry; выбран trained-young-men n=6 | Gross efficiency для fit 35/60 W, 85 W отложено; full-text methods/tables/limitations; не running. |
| SRC-0002 | Клеточный трикультурный конструкт | Проверены методика и endpoint; только контекст архитектуры, +43% не используется как human uplift. |
| SRC-0022 | 9 спринтеров, force plates vs inverse dynamics; 6 для reliability | F0/v0/Pmax mean±SD из аннотации; F0/v0 — intercepts, не мгновенная сила/достигнутая скорость; полный текст не получен. |
| SRC-0023 | 37 человек; young n=11; MRI + ultrasound/ramp MVC | Таблицы 2/3 и методика; mean±SE; площадь и касательная stiffness, peak stress не rupture/fatigue. Проверены целевые фрагменты индексируемого текста. |
| SRC-0024 | RT experiment1 n=1469; replication n=189 | XML, methods/tables/discussion; ms→s; межличностный SD отдельно от trial SD; hardware correction 18 ms (округлено). Компоненты задержки не измерены раздельно. |
| SRC-0025 | 17 активных взрослых; 5 SJ и 5 CMJ; dynamometer/ultrasound/motion capture | XML methods/tables; mean±SD; SI длины/скорости/момента. Контекст, не calibration sprint FV. |
| SRC-0026 | Статистический синтез catheter studies, Table3: 12 статей/117 участников | XML methods/table3/limitations; средние/SD, Ca в ml/L→dimensionless, Q/VO2 L/min→m3/s; pooled, не новый raw cohort. |
| SRC-0027 | 65 здоровых: young/old men/women; treadmill, acetylene uptake Q | Аннотация и индексируемая Table2; 4 группы mean±SD; внешний transport check; полного XML нет. |
| SRC-0028 | 85 мужчин, young n=18; 4×15 мин cycling +15 мин rest, 35 °C/20% RH | XML methods/tables; mean±SE; calorimeter 400 W heat. Heat storage kJ→J; WBSR — испарённая вода, не весь выделенный пот. |

## Контроль ошибок и прав

Для всех десяти источников получены Europe PMC core и Crossref DOI records,
проверены доступные commentCorrection/relation/update-to/updated-by. Обнаружена
**Comment in** у SRC-0027 (PMID 20019158), не erratum/retraction.
У SRC-0024 издатель также указывает commentary DOI 10.3389/fnhum.2015.00452
о межпоколенческом сравнении RT. Это не поправка к выбранным числам;
историческое сравнение не используется. Сам факт полемики сохранён в sources.json. В полученных
списках не найдено уведомления, меняющего выбранные числа. Поле isRetracted
не предоставлено API; нельзя трактовать его отсутствие как false. Дополнительно
выполнен целевой поиск notices для sprint, cycling, RT и cardiovascular работы.
Crossmark, reverse citation notices и все издательские supplements не проверены
исчерпывающе. Это выполненная ограниченная проверка, **не clearance ретракций**.
Старое замечание о поправке SRC-0003 остаётся в Foundation audit; источник не
используется для новых числовых параметров.

Числа вручную перенесены/преобразованы из названных таблиц, проверены по единицам
и локаторам. Публикуются числовые факты и собственные производные данные,
без перепубликации статей, изображений и индивидуальных данных.
XML источников имеет собственные условия: reaction/jump/thermal — открытые
статьи с лицензией в XML; tri-culture — CC BY-NC 4.0. Это не выдаёт права
перераспространения иных материалов. DOI/PMCID и retrieval recipe сохраняются.
calibration.csv не является исходным индивидуальным датасетом авторов.

## Отсутствующие данные и неидентифицируемость

- Индивидуальные cycling данные доступны по reasonable request, не получены.
- Harvard Dataverse Normative Gait Data DOI 10.7910/DVN/M0NKN9, V4, 100 healthy
  walking participants, CC0: найден, API вернул HTTP403. Не включён в расчёты.
  Даже успешная загрузка walking не валидировала бы sprint.
- Для APS fullTextXML источников muscle/cycling/tendon/primary cardiovascular
  API вернул HTTP500; использовались доступные страницы/таблицы и аннотации.
- Нет измеренной PCSA полного агрегата, геометрии шести ветвей, костной
  усталостной прочности, межсуставной координации, безопасного stress,
  коэффициентов обслуживания дополнительного органа, anaerobic reserve,
  нейронного разложения RT, closed-loop error curve и перфузии нового органа.
  Значения в parameters.json отмечены как допущения; sensitivity не заменяет данные.
- Не получена полная декомпозиция metrology error/interindividual/model error.
  SD, SE, IQR и сценарные интервалы сохраняются раздельно. SE не назван SD.

Успешные holdout-проверки не означают независимую валидацию всего организма;
отрицательные сравнения перечислены в REPORT.md и registry/negative_results.json.
