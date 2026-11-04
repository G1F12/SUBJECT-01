# Источники и фактически полученное содержимое

| ID | Первичный источник | Числовые файлы / ограничение |
|---|---|---|
| SRC-0050 | Lendt et al., 10.1186/s12966-024-01646-y; Zenodo 10.5281/zenodo.13477128 v1.0.0 | 135 native CSV: 66 cycle,69 walk; VO2,VCO2 L/min, prescribed W,rpm,time. CC BY4.0. 66 cycling participants, не 135 независимых людей. |
| SRC-0051 | Gashi et al., 10.1038/s41597-022-01643-5; Zenodo 10.5281/zenodo.6420886 | 17 DataAverage.csv + Study_Information.csv. VO2 mL/min,1s averaged/interpolated output; нет VCO2/механических W. CC BY4.0. |
| SRC-0052 | Hayden et al., 10.14814/phy2.70528 | Full XML/методы получены; n7, MRS и ambulatory task раздельно; raw по запросу авторам, публичные числовые файлы не получены. |
| SRC-0053 | 10.1113/jp291176 | EuropePMC metadata получены; full XML дважды HTTP500. Нет полученных numeric files. Local oxygen method использует assumed myoglobin concentration; не независимая абсолютная калибровка нашего cohort. |
| SRC-0054 | Weir, 10.1113/jphysiol.1949.sp004363 | Библиографическая/стехиометрическая основа; не новый набор людей. |
| SRC-0055 | BUT CGM, 10.13026/hv8f-3w60, PhysioNet v1.0.0 | Получены CPET_data.csv и CPET_summary.csv одного участника101,531 строка, median interval2.10s; VO2/VCO2 L/min,W. CC BY4.0 license и publisher SHA256SUMS получены, оба CSV сверены. CoolDown75W, не passive recovery. |

Полные URL, версии, SHA256 отдельных файлов/HTTP-ответов: sources.json,
access_initial.json,search_access.json,lendt_listing.json,cpet_retrieval.json,
schema_retrieval.json,weee_listing.json,weee_retrieval.json,physionet_probe.json.
Сохранённые SHA относятся к реально полученным байтам. Whole-archive MD5
Zenodo только объявлен издателем, **не проверен**: архивы 6.50GB/651.56MB
полностью не скачивались. ZIP central directory и нужные members получены
HTTP206 Range, CRC32 проверен zipfile, затем SHA256. Первая попытка мелких
параллельных запросов получила429; последующее последовательное чтение с
кэшем1MiB успешно, без обхода доступа. Raw хранятся только в ignored cache.

Lendt: Metalyzer3B, ergoselect100; source methods сообщают manufacturer
calibration перед сессией. Последние60s шестиминутной ступени, coverage≥80%,
observed≥30s, no interpolation через gap>15s. Primary RER .7..1 и targetW±2.
5min rest обычно отсутствует в экспортированном газе. Единственное пригодное
development recovery window имеет cadence4.15rpm и cost158.37W с большим SE;
это не оценка универсального passiveM. Standing/sitting baseline из walking
файла — другой task того же человека, не fastingRMR. Source notebook/source
headers исследованы до test; его numeric outputs не использовались.

WEEE: 85/102 пригодных phase windows,17 людей. VO2 без VCO2 допускает только
условный energy interval при RER .7..1. Cycling speed km/h не заменяет W.
Индивидуальные IDs имеют namespace cohort; параметры людей разных работ
не сшиваются. Групповые данные не превращаются в индивидуальные. Hierarchical
physiology transfer не выполнялся. Данные автора, полученные через ту же газовую
формулу (EE), не используются как независимый calorimeter.

PhysioNet probe: источник содержит65records/60people,154/155 повторяются с
одним CPET. Получен только один человек, не весь набор. Он exploratory/viewed;
никакой новой настройки/независимого теста на нём нет. Источник найден после
основного locked test; это отдельный retrieval audit, не расширение test.

Проверены PubMed/EuropePMC/PMC, Crossref, OpenAlex, Zenodo, Figshare, OSF,
Dryad и PhysioNet. Точные запросы/HTTP outcomes сохранены; это целевой поиск,
не заявление об исчерпывающем systematic review. Figshare broad search дал
ложные химические совпадения; OSF не дал подтверждённого joint numeric source.
Dryad file3450615 повторно HTTP401: легальный public raw недоступен; обход
не выполнялся. Старые PCr файлы Cycle5 сохранены, но не fusion с новыми людьми.
Полноценный PCr–continuous VO2–power–independent local calibration не получен.
Notices/retractions не проверены исчерпывающе; metadata audit не означает
экспертную верификацию всей статьи.
