# AEGIS-01 — CROSS-REPOSITORY ID AUDIT & RECONCILIATION REPORT
## Межрепозиторный аудит реестров, устранение 19 коллизий ID и детерминированная миграция
**Исследовательский цикл:** Cycle 2B  
**Репозитории:** `D:\AEGIS-01` (ветка `research/cycle-2b-reconciliation-advancement`) и `D:\SUBJECT-01` (ветка `main`, HEAD `9271a1eabbd8405f7152c151c52047ce54312c38`)  
**Статус проверки коллизий:** `REGISTRY_INTEGRITY: PASS` (0 коллизий)  
**Инструмент миграции:** [`tools/migrate_registry_ids.py`](file:///D:/AEGIS-01/tools/migrate_registry_ids.py)  
**Машинно-читаемая карта:** [`ID_MIGRATION_MAP.json`](file:///D:/AEGIS-01/ID_MIGRATION_MAP.json)  
**Автоматический тест:** [`tests/test_cross_repo_registry.py`](file:///D:/AEGIS-01/tests/test_cross_repo_registry.py)

---

## 1. Контекст проблемы и генезис коллизий

В ходе независимого аудита репозиториев на дату 8 ноября 2026 г. было обнаружено, что при создании трека AEGIS-01 в цикле 1 нумерация записей была начата непосредственно за пределами тогдашнего состояния `SUBJECT-01` (Cycle 7):
- Гипотезы начинались с `HYP-0008`
- Эксперименты начинались с `EXP-0037`
- Находки начинались с `FND-0038`
- Негативные результаты начинались с `NEG-0029`
- Решения начинались с `DEC-0015`
- Источники начинались с `SRC-0068`

Тем временем родительский репозиторий `D:\SUBJECT-01` продолжил собственную автономную исследовательскую работу (циклы 8 и 9, коммиты `07ae476`, `0870567`, `9271a1e`), выделив точно те же номера под задачи нервно-мышечной декомпозиции и валидации LOSO.

В результате возникло **19 критических межрепозиторных коллизий**, при которых одинаковые идентификаторы соответствовали совершенно разному научному содержанию.

---

## 2. Полный реестр выявленных коллизий (19 записей)

| Тип сущности | Коллидирующий ID | Содержимое в SUBJECT-01 (HEAD 9271a1e) | Содержимое в AEGIS-01 (Legacy) | Статус конфликта |
| :--- | :---: | :--- | :--- | :--- |
| **Решение** | `DEC-0015` | Adoption of Multi-Modal HD-sEMG Recruitment Model, Downgrade of Andersen & Saltin 1985 | Establish AEGIS-01 as an autonomous, scientifically rigorous survivability track | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Эксперимент** | `EXP-0037` | Cross-Participant sEMG Generalization and Feature Sensitivity Under Spatial Shift | Tissue Mechanics & Puncture/Cut Resistance Across Biological Composites | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Эксперимент** | `EXP-0038` | HD-sEMG Motor Unit Decomposition Reliability Across Force Levels | Acoustic Impedance Mismatch & Stress Wave Attenuation in Biomimetic Armor | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Эксперимент** | `EXP-0039` | Volume Conduction Forward Model vs Point-Electrode Spatial Selectivity | Sensorimotor Latency, Motor Acceleration & Ballistic Dodge Horizon | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Эксперимент** | `EXP-0040` | Intramuscular PCr Resynthesis and Capillary Proximity Correlation | Ballistic Energy Transfer, Viscous Criterion & Behind-Armor Blunt Trauma | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Эксперимент** | `EXP-0041` | Dynamic Oxygen Desaturation During Local Intermittent Ischemia | Hemodynamic Stability, Dynamic Vasospasm & Arterial Laceration Limits | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Находка** | `FND-0038` | Open empirical 64-channel HD-sEMG decomposition reveals motor unit firing rate saturation | Bioengineered osteoderm-collagen composite provides 5.4x sharp puncture resistance | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Находка** | `FND-0039` | Single-channel sEMG RMS is structurally unidentifiable with respect to active motor units | Tri-layer acoustic impedance mismatched composite attenuates shock pulses by 91.2% | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Находка** | `FND-0040` | Leave-One-Subject-Out cross-validation demonstrates severe generalization degradation | Reactive bullet dodging is physically and neurophysiologically impossible | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Находка** | `FND-0041` | Maximum free-energy capacity of gastrocnemius PCr pool (0.62 kJ) constrains power | Stopping penetration is insufficient: unbacked flexible armor causes lethal BABT | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Гипотеза** | `HYP-0008` | Biophysical Motor Unit Decomposition and Volume Conduction as Identifiability Preconditions | Hierarchical Bio-Mineral and Cross-Linked Dermal Armor Resistance | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Негативный рез.**| `NEG-0029` | Single-channel RMS surface EMG amplitude provides a linear proxy for neural drive | Organisms can reactively dodge already-fired supersonic or handgun bullets | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Негативный рез.**| `NEG-0030` | Spatial averaging across multi-channel arrays eliminates volume-conduction crosstalk | Flexible biological armor that stops projectile penetration guarantees survival | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Негативный рез.**| `NEG-0031` | Rapid high-power force development is unconstrained by motor unit recruitment order | Chemical or enzymatic hypercoagulation can prevent fatal aortic hemorrhage | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Источник** | `SRC-0068` | Hug et al. 2021 (Analysis of motor unit spike trains from HD-sEMG) | Wang et al. 2016 (Pangolin armor: keratinous scales structure and mechanics) | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Источник** | `SRC-0069` | Kemp et al. 2020 (Ergometer dataset to measure muscle bioenergetics with 31P-MRS) | Chen et al. 2011 (Armadillo armor: mechanical testing and microstructure) | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Источник** | `SRC-0070` | Caillet et al. 2023 (MuscleMap: automated deep-learning MU decomposition) | Meyers et al. 2008 (Biological materials: structure and mechanical properties) | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Источник** | `SRC-0071` | Charles et al. 2022 (Multi-modality lower leg imaging dataset: MRI/US volume) | Viano & Lau 1988 (A viscous tolerance criterion for soft tissue injury assessment) | **РЕАЛЬНЫЙ КОНФЛИКТ** |
| **Источник** | `SRC-0072` | Richardson et al. 2019 (Muscle blood flow at onset of dynamic exercise) | Roberts et al. 2007 (Numerical evaluation of BABT to human thorax) | **РЕАЛЬНЫЙ КОНФЛИКТ** |

---

## 3. Детерминированная схема перенумерации и ликвидации конфликтов

В строгом соответствии с требованием приоритета 0 («не менять уже опубликованные ID в SUBJECT-01, основная система учёта остаётся в SUBJECT-01»), реестры AEGIS-01 были сдвинуты детерминированным смещением за пределы максимальных ID родительского проекта:

| Префикс | Диапазон в SUBJECT-01 | Исходный диапазон AEGIS-01 | Смещение (Offset) | Новый диапазон AEGIS-01 | Число устраненных коллизий |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **HYP** | `HYP-0001` .. `HYP-0008` | `HYP-0008` .. `HYP-0019` | **+1** | `HYP-0009` .. `HYP-0020` | **1** |
| **EXP** | `EXP-0001` .. `EXP-0041` | `EXP-0037` .. `EXP-0057` | **+5** | `EXP-0042` .. `EXP-0062` | **5** |
| **FND** | `FND-0001` .. `FND-0041` | `FND-0038` .. `FND-0062` | **+4** | `FND-0042` .. `FND-0066` | **4** |
| **NEG** | `NEG-0001` .. `NEG-0031` | `NEG-0029` .. `NEG-0051` | **+3** | `NEG-0032` .. `NEG-0054` | **3** |
| **DEC** | `DEC-0001` .. `DEC-0015` | `DEC-0015` .. `DEC-0021` | **+1** | `DEC-0016` .. `DEC-0022` | **1** |
| **SRC** | `SRC-0001` .. `SRC-0072` | `SRC-0068` .. `SRC-0098` | **+5** | `SRC-0073` .. `SRC-0103` | **5** |
| **ISS** | `ISS-0001` .. `ISS-0019` | `ISS-0020` .. `ISS-0026` | **0** | `ISS-0020` .. `ISS-0026` | **0 (нет коллизий)** |
| **MOD** | *Отсутствует* | `MOD-0001` .. `MOD-0011` | **0** | `MOD-0001` .. `MOD-0011` | **0 (нет коллизий)** |
| **ИТОГО**| — | — | — | — | **19 КОЛЛИЗИЙ $\to$ 0** |

---

## 4. Сохранение истории и обратная совместимость (Traceability)

Для предотвращения потери исторического контекста применены следующие меры:
1. **Поле `original_id`:** В каждый модифицированный объект в файлах `hypotheses.json`, `experiments.json`, `findings.json`, `negative_results.json`, `decisions.json`, `sources.json` записано исходное поле `"original_id": "<old_id>"`.
2. **Файл [`ID_MIGRATION_MAP.json`](file:///D:/AEGIS-01/ID_MIGRATION_MAP.json):** Содержит полную взаимно-однозначную таблицу отображения, доступную для скриптов валидации.
3. **Обновление графа связей:**
   - Поле `experiment_id` в `findings.json` и `negative_results.json` перепривязано к новым номерам экспериментов (`EXP-0042..0052`).
   - Поле `related_experiments` в `hypotheses.json` обновлено.
   - Поле `supports_hypotheses` в `sources.json` перепривязано к новым номерам гипотез (`HYP-0009..0020`).

---

## 5. Доказательство идемпотентности и автоматический контроль

Создан скрипт миграции [`tools/migrate_registry_ids.py`](file:///D:/AEGIS-01/tools/migrate_registry_ids.py).
При повторном запуске он определяет, что реестры уже находятся в мигрированном состоянии, предотвращая вторичное смещение индексов:
```
[MIGRATION NOTICE] Registries are ALREADY migrated. Running in idempotent verification mode.
[VERIFICATION] Checking cross-repo collisions against SUBJECT-01...
[VERIFICATION PASS] Exactly 0 cross-repo ID collisions found with SUBJECT-01!
```

Автоматический тест [`tests/test_cross_repo_registry.py`](file:///D:/AEGIS-01/tests/test_cross_repo_registry.py) запускается в общем тестовом комплексе и гарантирует, что в будущем ни один коммит не сможет создать пересечений с `D:\SUBJECT-01`.
