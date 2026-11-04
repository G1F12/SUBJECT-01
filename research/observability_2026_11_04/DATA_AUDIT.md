# Реальные данные и публичный доступ — EXP-0020

Дата04.11.2026. Целевой углублённый поиск, не исчерпывающий systematic review.
`retrieval.json`: URL, запросы API, HTTP status, версия metadata, размер,
SHA256 полученных ответов. `sources.json`: DOI/title/year и limited notices.
`data_inventory.json`: прочитанные числовые members, их SHA256, формат,
содержимое, временные шкалы и ограничения. `inspect_data.py --check` повторяет
чтение pinned members. Один неизменённый PeerJ XLS с подтверждённой CC BY 4.0 включён в licensed_data с атрибуцией; поля имён пустые. Остальные raw не публикуются.

| ID | Источник | Фактически получено | Разрешённый вывод |
|---|---|---|---|
| SRC-0043 | Wang et al., [PNAS2023](https://doi.org/10.1073/pnas.2302738120); [Figsharev1](https://doi.org/10.25444/nhlbi.23681013.v1) | 174701bytes source archive, MD5 совпал; Figure1A.xlsx прочитан. Два человека, шесть scan curves,87×6=522 относительных PCr cells,7.5s по methods | Реальная relative PCr recovery, не chemicalJ; нет simultaneous human VO2/power. Другие листы OCR относятся к fibroblasts/другим моделям, не pulmonary gas. |
| SRC-0044 | Haeufle et al., [2020](https://doi.org/10.3389/fbioe.2020.00622) | EuropePMC supplemental archive и внутренний Data_Sheet_1.ZIP получены; четыре MATv7.3 прочитаны HDF5.144time/PCr/Pi/ATP/pH points, t−113.04..600.26s,142интервала5s и один3.3s. Kinematics/normalizedEMG240001samples за60s | Один человек. Отдельные MRI/EMG/MRS trials,20%MVC. `paradigm1` — индикатор0/1, не ватт. PCr_mmol_l использует assumedATP8.2mmol/l. Energy_exp11points — PCr-derivedJ/kg, не независимая стоимость. |
| SRC-0045 | [PeerJ2016](https://doi.org/10.7717/peerj.2259) | 47.7MB EuropePMCwrapper; исходный XLS224256bytes прочитан,130×229 layout,17uniqueCW labels. Получены также spectral-image archives | 10мужчин/7женщин.25%MVC knee extension300s,rest300s; MRS50s blocks,6exercise/6recovery. Дубли sex summaries не новые люди. Нет continuousVO2/W. mmol/kg и kPCr — derived, не independently absolute reserve. |
| SRC-0046 | [arm crank2021](https://doi.org/10.3389/fphys.2021.599514) | Publisher HTML/методы/availability и bibliography получены | Релевантная платформа для same-subject metabolism/mechanics/calorimetry; raw «от авторов». Числовой dataset не получен; обещание не считается successful access. |
| SRC-0047 | [interleavedMRS/MRI2026](https://doi.org/10.1002/mrm.70337) | FullXML, supplementary file listing | Nominal2s PCr + blood flow и staged W, но blood flow не VO2. Raw upon request; приложения PDF/video, числовой time-series dataset не получен. |
| SRC-0048 | [pH-resolved2026](https://doi.org/10.3390/diagnostics16050744) | Supplemental archive скачан и раскрыт: только PDF | n5,2sMRS из methods; no numeric timeseries file. Data upon request. Не считать извлечение ZIP успешным получением raw kinetics. |
| SRC-0049 | [InSight2013](https://doi.org/10.1038/srep01182) | FullXML и bibliography; исследование87человек с MRS/VO2max/DE | Интересен same-participant дизайн; VO2max не continuousVO2 при MRS. Совместный числовой raw не получен. |
| SRC-0041 | [Dryad08kprr59v](https://doi.org/10.5061/dryad.08kprr59v) | Повторно получены datasetmetadata/files; knownfile3450615 | API download401,publicfile_stream403. Публичный поиск поDOI/XLSX не дал подтверждённого numericmirror. По metadata один человек/три опыта,6s,42sload/360srest. Ни одной новой PCrячейки из этого файла не прочитано. |

Источники поиска: PubMed через EuropePMC indexed records и первичные PubMed
страницы; PMC/EuropePMC fullTextXML и supplementaryFiles; Crossref; OpenAlex;
ZenodoAPI; FigshareAPI; OSFAPI; DryadAPI; publisher pages; институциональные
York/Manchester/Stuttgart/UniMi candidates и Mendeley. Поисковый запрос PhysioNet
не вернул применимого набора; полный каталог PhysioNet не выгружался.
OSF title-query phosphocreatine вернул пустой ответ, это не доказательство
отсутствия datasets с иными названиями. Биovis/York lead проверен:
DOI10.17632/3r7kmfmpyj.1 — brain MT-MRS, исключён; исходные brain файлы не нужны.
Zenodo первые15hits содержали reviews, assay/neural/prosthetic материалы,
не подтверждённый joint exercise dataset. Figshare search30hits просмотрены по
названиям; многие publication records, не raw. Нет утверждения «все raw закрыты».

Лицензии: FigshareWASF3v1 явно PublicDomainMark1.0, хотя статья PNAS
CCBY-NC-ND4.0; права отдельного datarecord не подменяем лицензией статьи.
PeerJ CCBY4.0. Plantar статьяCCBY, код supplement содержит BSD-style3-clause;
границы rawdata-license не расширяем автоматически. Кроме явно лицензированного PeerJ XLS (см. licensed_data/ATTRIBUTION.md), raw в ignored
`tmp/observability_raw`; в Git только наш audit/recipe/hashes/derived summaries.
Downloads сохраняют publisher source archives; новый ZIP/репозиторий не создаётся.
EuropePMC wrapper ZIP может зависеть от упаковки: воспроизводимость проверяет
внутренние numeric-member SHA256; wrapperSHA остаётся снимком доступа.

Технические ошибки сохранены: biovis direct timeout; Crossref отдельные429,
fallback EuropePMC; h5py3.16.0 зависал на import в Windows,3.15.1 работает;
SciPy loadmat не поддерживает MATv7.3 — чтение выполнено h5py. Первый вывод
retrieval в cp1251 завершился UnicodeEncodeError **после сохранения** JSON;
console summary исправлен на ASCII. Это не потеря числового файла.

## Ограниченный эмпирический анализ PCr

После просмотра Figure1A выполнен **exploratory in-sample** fit,
не preregistered validation: 29послеусилийных точек каждой из6кривых,
r(t)=a−d exp(−t/τ). Methods7.5s использованы; Excel даёт только indices1..87,
сумма180+120+360s предполагает88точек. Принято начало recovery послеindex40;
последняя fittedpoint217.5s, текст описывает3.75min — timing mismatch открыт.
Временной сдвиг при свободной amplitude поглощается amplitude, но неверный
sampling interval непосредственно масштабирует τ. Полного synchronized ledger нет.

При свободной asymptote τ≈31.7..32.5s для S2 и77.3..85.9s для S1 (две visits).
При forcedasymptote1 диапазон S1≈97.0..163.6s. Это контрпример автоматическому
отождествлению baseline-normalization с известной asymptote. MAE/RMSE/bias
по каждой кривой сохранены в inventory, в relativePCr units. Они **не W-errors**,
не population inference и не независимое преимущество модели. Индивидуальные
данные дают observability kinetics при оговорках, но не идентифицируют η,Cfast,
окислительный масштаб и энергетическую цену отдыха. Никакого fit D2 по этим
участникам и никакого искусственного нового holdout не создано.

## Проверка CI и стабильность доступа

Первый GitHub push-run41869707575 завершился HTTP500 EuropePMC при повторной сборке PeerJ supplementaryFiles (47.7MB), до проверки численного дизайна. Это отказ сервиса, не несовпадение источника. Повторные publicfile URLs дали403,HTML вместоXLS,404; HTML не признан числовым файлом. Поэтому точный ранее полученный XLS224256bytes с подтверждённойCCBY4.0, атрибуцией, SHA256 и пустымиNamefields сохранён вlicensed_data. CI читает его напрямую и отвергает изменениехэша; исходныйwrapperSHA и recipe сохранены. Изменения научныхуравнений/численныхрезультатов не потребовались.
