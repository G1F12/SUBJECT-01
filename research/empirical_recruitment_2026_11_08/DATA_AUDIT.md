# DATA AUDIT — RESEARCH CYCLE 9
## EMPIRICAL HUMAN DATASETS, RECRUITMENT OBSERVABILITY, AND PREFLIGHT RESOLUTIONS

Дата аудита: 2026-11-08  
Область: эмпирические измерения двигательных единиц (HD-sEMG), динамической магнитно-резонансной спектроскопии ($^{31}\text{P}$-MRS), анатомической томографии (3D MRI) и термодинамическая калибровка.

---

## 1. Этап 0 — Preflight Resolutions

### 1.1. Вопрос 1: Разграничение энергетической ёмкости фосфокреатина ($\Delta_R H$ vs $\Delta G_{\text{ATP}}$)

В ходе аудита Cycle 8 и начала Cycle 9 выявлено параллельное использование величины $21.0\text{ кДж/моль}$ и диапазона $50.0\text{--}64.0\text{ кДж/моль}$ (номинал $54.0\text{ кДж/моль}$). Установлено строгое физическое разграничение:

1. **Калориметрическая реакционная энтальпия гидролиза фосфокреатина и ресинтеза ATP ($\Delta_R H_{\text{CK}} \approx -21.0\text{ кДж/моль}$)**:
   - *Первоисточник*: Kodama (1985), Woledge et al. (1985).
   - *Физический смысл*: чистое выделение теплоты при изотермическом распаде PCr и сопряжённом ресинтезе ATP в мышечной ткани.
   - *Область применения*: термокалориметрия, тепловыделение и тепловой баланс мышцы:
     $$\dot{Q}_{\text{heat}} = v_{\text{ATP}} \cdot (-\Delta_R H_{\text{CK}})$$
   - *Энтальпийная ёмкость пула*: $E_{\text{heat}} = V_{\text{active}} \cdot [\text{PCr}] \cdot (-\Delta_R H_{\text{CK}})$. Для номинального объёма $V_{\text{anat}} = 380\text{ мл}$ и $[\text{PCr}] = 33.6\text{ мМ}$ составляет $268.1\text{ Дж}$.

2. **Свободная энергия Гиббса гидролиза ATP ($\Delta G_{\text{ATP}} \approx -50.0\dots -64.0\text{ кДж/моль}$, номинально $-54.0\text{ кДж/моль}$)**:
   - *Первоисточник*: Meyerspeer et al. (2021), Kushmerick (1998).
   - *Физический смысл*: максимальная термодинамическая работа, доступная для совершения актомиозиновыми поперечными мостиками и ионными насосами ($-\Delta G = -\Delta H + T\Delta S$).
   - *Область применения*: механическая мощность и электромеханическое сопряжение:
     $$P_{\text{mech}} = \eta_{\text{loc}} \cdot v_{\text{ATP}} \cdot (-\Delta G_{\text{ATP}})$$
   - *Потенциальная ёмкость механической работы*: $E_{\text{work,max}} = V_{\text{active}} \cdot [\text{PCr}] \cdot (-\Delta G_{\text{ATP}})$. Для номинального объёма $V_{\text{anat}} = 380\text{ мл}$ составляет $689.5\text{ Дж}$.

3. **Согласование**:
   - Отношение $\frac{-\Delta G_{\text{ATP}}}{-\Delta_R H_{\text{CK}}} = \frac{54.0}{21.0} \approx 2.5714$ отражает термодинамический вклад энтропийного слагаемого $T\Delta S$.
   - В коде и реестрах формулы строго разделены: механическая мощность всегда масштабируется через $\Delta G_{\text{ATP}}$ ($54.0\text{ кДж/моль}$), а тепловыделение — через $\Delta_R H$ ($21.0\text{ кДж/моль}$). Никакого смешения понятий не допускается.

---

### 1.2. Вопрос 2: Происхождение значений покоя $2.4\text{ мл}/100\text{ г}/\text{мин}$ и $58\text{ мл/л}$ в Andersen & Saltin (1985)

Проведён детальный аудит оригинальной публикации:
- *Статья*: Andersen, P., & Saltin, B. (1985). *Maximal perfusion of skeletal muscle in man*. The Journal of Physiology, 366, 233–249. DOI: `10.1113/jphysiol.1985.sp015794`.
- *Результаты постраничной проверки*:
  1. Испытуемые: 8 здоровых мужчин (Table 1, стр. 236: антропометрия, масса четырёхглавой мышцы бедра по КТ $\sim 2.3\text{ кг}$).
  2. Текст на стр. 237: *"Resting leg blood flow in the sitting position varied between 0.15 and 0.40 l min-1"*.
  3. Таблица 2 (стр. 240): приводит измерения кровотока, артериовенозной разницы $O_2$, $\text{VO}_2$, АД и ЧСС исключительно при активных динамических нагрузках: **10 Вт, 20 Вт, 30 Вт, 40 Вт, 50 Вт, 60 Вт**. **Строка покоя (0 Вт) в Таблице 2 отсутствует**.
  4. Значения $2.4\text{ мл}/100\text{ г}/\text{мин}$ и $(C_a - C_v)O_2 = 58\text{ мл/л}$ не являются табличными данными Andersen & Saltin (1985). Они представляют собой вторичную экстраполяцию кровотока покоя всей конечности ($0.24\text{ л/мин} / 10\text{ кг} = 2.4\text{ мл}/100\text{ г}/\text{мин}$) и типичной артериовенозной разницы ($200 - 142 = 58\text{ мл/л}$), цитируемую в более поздних обзорах (Jorfeldt & Wahren 1971, Radegran & Saltin 1998).
- *Вердикт*: статус этих численных значений как первичного табличного измерения покоя в [SRC-0066](file:///d:/SUBJECT-01/registry/sources.json) **понижен** до:
  `DOWNGRADED_NOT_PRIMARY_RESTING_TABLE` / `LITERATURE_REVIEW_TRANSFER_ASSUMPTION`.

---

## 2. Реестр новых эмпирических источников Cycle 9

| ID | Название источника | DOI / Репозиторий | Тип данных | Число людей | Статус верификации |
|---|---|---|---|---|---|
| SRC-0068 | Hug et al. (2021) / Figshare HD-sEMG | DOI: 10.1016/j.jelekin.2021.102548, Figshare: 10.6084/m9.figshare.13695937 | 64-канальная HD-sEMG сетка (2048 Гц), спайковые поезда ДЕ (gCKC) GM, GL, TA при 10, 30, 50, 70% MVC | $n=8$ операторов / когорта добровольцев | metadata_and_scope_checked_only |
| SRC-0069 | Rehman et al. (2024) / Dryad 31P-MRS | DOI: 10.1016/j.dib.2024.111114, Dryad: 10.5061/dryad.08kprr59v, PMC11617988 | Динамическая $^{31}\text{P}$-MRS (TR=1 с, кадр 6 с) квадрицепса на немагнитном эргометре 3T Siemens, 3 повторных триала, нейтральный pH | $n=1$ человек (3 полных триала) | metadata_and_scope_checked_only |
| SRC-0070 | MuscleMap Open Dataset (2023–2024) | Zenodo: 10.5281/zenodo.10077847 / GitHub MuscleMap | 3D Dixon / T1-MRI маски сегментации индивидуальных объёмов мышц голени и бедра | $n=48$ здоровых людей | metadata_and_scope_checked_only |
| SRC-0071 | Cenni et al. (2018–2020) / Figshare Calf Volumetry | Figshare: 10.6084/m9.figshare.5971480 | Анатомические объёмы мышц голени и толщина подкожного жирового слоя (SAT) по 3D MRI и УЗИ | $n=16$ участников | metadata_and_scope_checked_only |
| SRC-0072 | Radegran & Saltin (1998) | DOI: 10.1152/ajpheart.1998.274.1.H314 | Допплерография бедренного кровотока в покое ($\approx 250\text{ мл/мин}$) и на первой секунде сокращений | $n=7$ здоровых людей | metadata_and_scope_checked_only |

---

## 3. Криптографические хеши и артефакты данных

| Файл / Артефакт | Путь к файлу | Размер, байт | SHA256 |
|---|---|---|---|
| Rehman 2024 PMC XML | `research/empirical_recruitment_2026_11_08/pmc11617988.xml` | 42,708 | `835dbe48440f1b7139108c7a17673b1bb0664efc8c9d692fd01431a3276d5d2c` |
| Empirical Datasets JSON | `research/empirical_recruitment_2026_11_08/empirical_datasets_cycle9.json` | 7,096 | генерируется динамически |
| Biophysical Recruitment JSON | `research/empirical_recruitment_2026_11_08/recruitment_biophysical_results.json` | 5,597 | генерируется динамически |
| Identifiability Results JSON | `research/empirical_recruitment_2026_11_08/identifiability_recruitment_results.json` | 1,377 | генерируется динамически |
| LOSO Validation JSON | `research/empirical_recruitment_2026_11_08/validation_loso_results.json` | 2,252 | генерируется динамически |
| Master Experiment Results JSON | `research/empirical_recruitment_2026_11_08/experiment_results.json` | 11,574 | генерируется динамически |
