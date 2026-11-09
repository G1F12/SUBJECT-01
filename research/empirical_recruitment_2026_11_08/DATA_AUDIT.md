# DATA AUDIT — RESEARCH CYCLE 9
## RIGOROUS PROVENANCE AUDIT OF HUMAN RECRUITMENT, VOLUMETRY, AND METABOLIC BENCHMARKS

---

## 1. Аудит термодинамических и физиологических первоисточников (Stage 0)

### 1.1. Вопрос 1: Разграничение энтальпии $\Delta_R H$ и свободной энергии $\Delta G_{\text{ATP}}$
1. **Калориметрическая энтальпия гидролиза фосфокреатина ($\Delta_R H_{\text{CK}}$)**:
   - Значение: $\mathbf{-21.0\text{ кДж/моль}}$ ($\sim -21\text{ to } -25\text{ кДж/моль}$).
   - Источник: Kodama (1985), *Physiological Reviews* 65(2):467–551.
   - Физический смысл: мера тепловыделения экзотермической реакции при постоянном давлении ($\Delta H = \Delta U + P\Delta V$). Используется в термокалориметрии мышц для расчёта теплового баланса ($Q_{\text{heat}}$).
2. **Термодинамическая свободная энергия Гиббса гидролиза АТФ ($\Delta G_{\text{ATP}}$)**:
   - Значение: $\mathbf{-50.0\dots -64.0\text{ кДж/моль}}$ (номинально $-54.0\text{ кДж/моль}$ в покое; снижается до $-50\text{ кДж/моль}$ при глубоком истощении).
   - Источники: Meyerspeer et al. (2021) PMC8243949, Kushmerick (1983).
   - Физический смысл: термодинамический потенциал, определяющий максимальную механическую работу актомиозиновых мостиков ($W_{\text{mech}} \le -\Delta G_{\text{ATP}}$).
3. **Физическое согласование**:
   - Отношение $\frac{-\Delta G_{\text{ATP}}}{-\Delta_R H_{\text{CK}}} = \frac{54.0}{21.0} \approx 2.5714$ отражает термодинамический вклад энтропийного слагаемого $T\Delta S$.
   - В коде и реестрах формулы строго разделены: механическая мощность всегда масштабируется через $\Delta G_{\text{ATP}}$ ($54.0\text{ кДж/моль}$), а тепловыделение — через $\Delta_R H$ ($21.0\text{ кДж/моль}$). Никакого смешения понятий не допускается.

---

### 1.2. Вопрос 2: Происхождение значений покоя $2.4\text{ мл}/100\text{ г}/\text{мин}$ и $58\text{ мл/л}$ в Andersen & Saltin (1985)

Проведён детальный аудит оригинальной публикации:
- *Статья*: Andersen, P., & Saltin, B. (1985). *Maximal perfusion of skeletal muscle in man*. The Journal of Physiology, 366, 233–249. DOI: `10.1113/jphysiol.1985.sp015794`. PubMed PMID: `4057091`.
- *Результаты постраничной проверки*:
  1. Испытуемые: **5 здоровых мужчин** (PubMed явно указывает: *"Five subjects exercised with the knee extensor of one limb at work loads ranging from 10 to 60 W"*; антропометрия, масса четырёхглавой мышцы бедра по КТ $\sim 2.3\text{ кг}$). Число 8 являлось ошибкой прежнего черновика.
  2. Текст на стр. 237: *"Resting leg blood flow in the sitting position varied between 0.15 and 0.40 l min-1"*.
  3. Таблица 2 (стр. 240): приводит измерения кровотока, артериовенозной разницы $O_2$, $\text{VO}_2$, АД и ЧСС исключительно при активных динамических нагрузках: **10 Вт, 20 Вт, 30 Вт, 40 Вт, 50 Вт, 60 Вт**. **Строка покоя (0 Вт) в Таблице 2 отсутствует**.
  4. Значения $2.4\text{ мл}/100\text{ г}/\text{мин}$ и $(C_a - C_v)O_2 = 58\text{ мл/л}$ не являются табличными данными Andersen & Saltin (1985). Они представляют собой вторичную экстраполяцию кровотока покоя всей конечности ($0.24\text{ л/мин} / 10\text{ кг} = 2.4\text{ мл}/100\text{ г}/\text{мин}$) и типичной артериовенозной разницы ($200 - 142 = 58\text{ мл/л}$), цитируемую в более поздних обзорах (Jorfeldt & Wahren 1971, Radegran & Saltin 1998).
- *Вердикт*: статус этих численных значений как первичного табличного измерения покоя в [SRC-0066](file:///d:/SUBJECT-01/registry/sources.json) **понижен** до:
  `DOWNGRADED_NOT_PRIMARY_RESTING_TABLE` / `LITERATURE_REVIEW_TRANSFER_ASSUMPTION`.

---

## 2. Реестр новых источников Cycle 9 и статус доступности первичных данных

| ID | Название источника | DOI / Репозиторий | Тип данных | Первичная доступность (Raw Data) | Статус верификации |
|---|---|---|---|---|---|
| SRC-0068 | Hug et al. (2021) / Figshare HD-sEMG | DOI: 10.1016/j.jelekin.2021.102548, Figshare: 10.6084/m9.figshare.13695937, bioRxiv: 10.1101/2021.02.19.431376 | Опубликованные характеристики Таблицы 2 (GM: 8.1, 8.1, 7.6, 12.2 имп./с; GL: 8.1, 8.2, 11.3, 14.0 имп./с); 8 операторов-экспертов; биологические испытуемые = UNKNOWN | Заблокировано (Cloudflare R2, HTTP 403) | `PUBLISHED_LITERATURE_RATES_SEPARATED` |
| SRC-0069 | Rehman et al. (2024) / Dryad 31P-MRS | DOI: 10.1016/j.dib.2024.111114, Dryad: 10.5061/dryad.08kprr59v, PMC11617988 | Опубликованные кинетические константы в Таблице 1 (1 субъект, 3 триала, $\tau = 39.4\text{ с}$, $\text{pH} = 7.01$). Сырой XLSX: 18.14 КБ, SHA256: `ae7876d1...` | Заблокировано (AWS WAF / Anubis challenge, HTTP 403; REST API HTTP 401) | `PUBLISHED_AGGREGATE_METRICS_ONLY` / `RAW_TIMESERIES_UNAVAILABLE` (готов к owner-assisted загрузке) |
| SRC-0070 | MuscleMap Open Dataset (2023–2024) | Zenodo: 10.5281/zenodo.10077847 | Репозиторий кода и весов нейросети, без подтверждённой открытой таблицы когорты | Отсутствует когортная таблица | `UNVERIFIED_PRIMARY_TABLES_RETRACTED` |
| SRC-0071 | Cenni et al. (2018–2020) / Figshare Calf Volumetry | Figshare: 10.6084/m9.figshare.5971480 | Идентификатор неразрешим как открытый архив датасета | Неразрешимый URL | `UNVERIFIED_PRIMARY_TABLES_RETRACTED` |
| SRC-0072 | Radegran & Saltin (1998) | DOI: 10.1152/ajpheart.1998.274.1.H314 | Допплерография бедренного кровотока в покое ($\approx 250\text{ мл/мин}$) | Статья рецензируемого журнала | `metadata_and_scope_checked_only` |

---

## 3. Аудит блокировок доступа к raw data (HTTP Audit)

### 3.1. Rehman et al. 2024 (Dryad)
- Целевой файл: `2024_829_Ergometer_Dryad_Raw_V3.xlsx` (18.14 КБ).
- Официальный REST API Dryad подтверждает SHA256: `ae7876d1464b994614714d123b448f71d238d02c92f2a8acebff553e1f0986cf`.
- Dryad Share URL: `https://datadryad.org/stash/share/LKj22wpyxIQguzk5GCQgsMBwY6hccwEKj77L2nXXXb0`.
- Ответ сервера при прямой программной загрузке: **HTTP 403 Forbidden** (интерактивный JS-челлендж Anubis / BotStopper Proof-of-Work `<title>Validating...</title>`), а REST API download требует авторизации (**HTTP 401 Unauthorized**).
- Обход механизмов безопасности сервера или имитация человека запрещены политикой целостности.
- Подготовлен owner-assisted контур `tools/process_rehman_xlsx.py`: пользователь загружает оригинальный XLSX через браузер в проект, после чего скрипт автоматически валидирует SHA256, извлекает 3 триала по 75 спектров и восстанавливает кинетику.

### 3.2. Hug et al. 2021 (Figshare)
- Целевой файл: `Experimental_data_Raw.zip` (444 МБ) и `Experimental_data_edited.zip` (3.7 ГБ).
- Ответ сервера: **HTTP 403 Forbidden** с заголовком блокировки хранилища Cloudflare R2 (`CF-RAY` block).
- В открытом доступе опубликована Таблица 2 с верифицированными характеристиками после ручного редактирования операторами:
  - Gastrocnemius Medialis (GM): 10% MVC = $8.1 \pm 1.1\text{ имп./с}$; 30% MVC = $8.1 \pm 1.0\text{ имп./с}$; 50% MVC = $7.6 \pm 1.2\text{ имп./с}$; 70% MVC = $12.2 \pm 0.6\text{ имп./с}$.
  - Gastrocnemius Lateralis (GL): 10% MVC = $8.1 \pm 0.9\text{ имп./с}$; 30% MVC = $8.2 \pm 1.3\text{ имп./с}$; 50% MVC = $11.3 \pm 1.3\text{ имп./с}$; 70% MVC = $14.0 \pm 1.5\text{ имп./с}$.
  - Tibialis Anterior (TA): 35% MVC = $12.0 \pm 1.2\text{ имп./с}$; 50% MVC = $15.5 \pm 1.4\text{ имп./с}$; 75% MVC = $17.4 \pm 1.5\text{ имп./с}$.
  - Неподтверждённые частоты разряда (9.8, 12.6, 15.4, 19.8 Гц) **отозваны (RETRACTED/SUPERSEDED)**.
- **Эпистемическое разграничение**: авторы сообщают, что данные переиспользованы из двух разных экспериментов и разных участников. Число независимых участников невозможно точно установить; зафиксирован статус **`UNKNOWN`** вместо произвольного $N=1$. Восемь операторов-соавторов — это эксперты-оценщики, а не 8 независимых биологических испытуемых. Статус: **`RAW_ARCHIVE_BLOCKED_BY_CDN_CHALLENGE / PUBLISHED_LITERATURE_RATES_SEPARATED`**.

### 3.3. Аудит МРТ-волюметрии
- Franke et al. 2020: объём икроножной мышцы $V_{\text{anat}} = 379.89\text{ мл}$ верифицирован по первичному файлу `research/empirical_anchors_2026_11_08/franke2020_extracted_measurements.json` (SHA256: `c08748c08d2649cb69a535c1914c3844fb8497288aebb2d006274fdcddfcba83`).
- Источники SRC-0070 (MuscleMap) и SRC-0071 (Cenni) не содержат верифицированных таблиц первичных измерений; статус `EMPIRICALLY_BOUNDED_DISTRIBUTION` отозван.

---

## 4. Ретракция синтетической валидации LOSO

В скрипте `validation_loso.py` ранее использовались функции `generate_rehman_time_series()` и `generate_franke_time_series()`, которые генерировали экспоненциальные кривые с добавлением нормального шума через `np.random.RandomState(42)` и `np.random.RandomState(123)`.
- Утверждения о независимой эмпирической валидации человека с RMSE 0.837 мМ и 2.424 мМ признаны **научно некорректными** и **полностью отозваны**.
- Эксперимент EXP-0040 и вывод FND-0040 переведены в статус **`SYNTHETIC_DEMONSTRATION_NOT_EMPIRICALLY_VALIDATED`**.
- Независимая эмпирическая валидация переведена в статус **`BLOCKED_PENDING_RAW_DATA`**.
- При одном участнике (Rehman $N=1$) кросс-субъектная валидация методом Leave-One-Subject-Out (LOSO) физически невозможна и строго запрещена Evidence Gate V2.
