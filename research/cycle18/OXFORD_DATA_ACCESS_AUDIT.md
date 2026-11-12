# Окончательный аудит доступности данных Oxford Achilles Atlas (Cohen et al. 2026)

## 1. Введение и цели аудита

В Исследовательских циклах 15, 16 и 17 проект SUBJECT-01 неоднократно обращался к публикации **Cohen et al. (2026)** под названием «Oxford Achilles Tendon Atlas» как к потенциальной третьей независимой когорте для валидации молекулярной программы мышечно-сухожильного перехода (**MTJCore**).

В ходе предыдущих циклов возникали взаимоисключающие утверждения:
- В Cycle 16 утверждалось, что в атласе «полностью отсутствуют мионуклеи» (0 мышечных клеток).
- В Cycle 17 было признано, что мышечная ткань исследовалась, но репликация MTJCore была объявлена заблокированной (`DATA_BLOCKED`) из-за отсутствия донорских псевдобалк-таблиц мионуклеов в репозитории Mendeley Data.

Цель настоящего аудита — провести исчерпывающую проверку всех официальных репозиториев данных, установить фактическую доступность файлов, матриц экспрессии, метаданных доноров и выяснить истинную роль этого набора данных в контексте MTJCore.

---

## 2. Исходная публикация и идентификаторы

- **Авторы:** Carla J. Cohen, Jolet Y. Mimpen, Alina Kurjan, Claudia Paul, Shreeya Sharma, Lorenzo Ramos-Mucci, Chinemerem T. Ikwuanusi, Ali Cenk Aksu, Tracy Boakye Serebour, Marina Nikolic, Kevin Rue-Albrecht, Christopher Gibbons, Duncan Whitwell, Tom Cosker, Steven Gwilym, Ather Siddiqi, Raja Bhaskara Rajasekaran, Harriet Branford-White, Adam P. Cribbs, Philippa A. Hulley, David Sims, Mathew J. Baldwin, Sarah J. B. Snelling.
- **Название статьи:** *Fibroblast specialisation across microanatomy in a single-cell atlas of healthy human Achilles tendon*.
- **Журнал:** *American Journal of Physiology - Cell Physiology*, Volume 330, Issue 5, May 2026, Pages C1460–C1473.
- **DOI:** [10.1152/ajpcell.00838.2025](https://doi.org/10.1152/ajpcell.00838.2025)
- **PubMed ID:** 41920776

---

## 3. Аудит публичных репозиториев данных

Проведена независимая проверка четырёх официальных источников данных, указанных авторами публикации.

### 3.1. Mendeley Data
- **URL:** [https://data.mendeley.com/datasets/vfzd93y7dv/1](https://data.mendeley.com/datasets/vfzd93y7dv/1)
- **Доступные файлы:** `fibroblasts.rds` (Seurat-объект, содержащий 24 179 клеток).
- **Содержимое:** Исключительно субкластеризованные фибробласты сухожилия (NEGR1+, COMP+, PRG4+).
- **Присутствие мионуклеов:** **Отсутствуют.**
- **Причина путаницы в Cycle 16:** Исследователи Cycle 16 ограничились загрузкой только этого файла из Mendeley Data, ошибочно экстраполировав отсутствие мионуклеов в файле `fibroblasts.rds` на всё исследование Cohen et al.

### 3.2. CZ CELLxGENE Discover
- **URL коллекции:** [https://cellxgene.cziscience.com/collections/a7e81820-297d-4086-8123-cc7dde64e495](https://cellxgene.cziscience.com/collections/a7e81820-297d-4086-8123-cc7dde64e495)
- **Идентификатор датасета:** `ef0fc6ac-4872-40e1-ab24-e445b19ca6e3`
- **Файл:** `ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad`
- **Размер файла:** 1 124 490 595 байт (~1.12 ГБ).
- **Локальное размещение:** Файл сохранён локально в репозитории по пути:
  `D:/MTJCore/data/raw/achilles/ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad`
- **Содержимое матрицы:**
  - Общее количество клеток/ядер: **64 862**.
  - Количество генов/признаков: **60 330** (включая 36 601 основной ген).
  - Слой сырых отсчётов (`raw/X`): **Присутствует в полном объёме** (формат CSR sparse matrix).
  - Метаданные доноров (`donor_id`): **Присутствуют** для каждого ядра (всего 5 независимых человеческих доноров: `MSK1556`, `MSK1691`, `MSK1687`, `MSK1250`, `MSK0785`).
  - Анатомическая разметка (`microanatomical_site`): **Присутствует** (`MTJ`, `MB` [midbody], `muscle`, `Enth` [enthesis]).
  - Мышечные ядра: **Присутствуют в количестве 22 146 ядер** (15 126 медленных, 5 447 быстрых, 1 491 переходных/MTJ-ассоциированных).

### 3.3. GitHub авторов
- **URL:** [https://github.com/Botnar-MSK-Atlas/achilles_tendon_atlas](https://github.com/Botnar-MSK-Atlas/achilles_tendon_atlas)
- **Коммит:** `ab8b1e1301c338f881f70c32b4387987045beebb`
- **Содержимое:** Исходные аналитические скрипты (R Markdown), включая пайплайн деконтаминации фоновой РНК (SoupX), интеграции (Harmony), кластеризации (Louvain) и аннотации мышечных клеток (`Annotation/Achilles_Muscle_Fine-annotation_harmony_louvain_0.1_soupX.Rmd`).
- **Значение:** Позволяет полностью восстановить логику разметки переходных миоцитов.

### 3.4. Human Cell Atlas (HCA) Data Portal
- **URL проекта:** [https://explore.data.humancellatlas.org/projects/893c8fb6-bf65-4527-b83b-8233de59244c](https://explore.data.humancellatlas.org/projects/893c8fb6-bf65-4527-b83b-8233de59244c)
- **Статус:** Официальная регистрация проекта в глобальном консорциуме Human Cell Atlas.

---

## 4. Ключевое открытие аудита: Тождество с Discovery-когортой MTJCore

При сопоставлении метаданных и конфигураций проекта MTJCore (`D:\MTJCore\configs\analysis_plan.yaml`, `data/metadata/dataset_inventory.tsv`) установлен фундаментальный методологический факт:

> **Атлас Oxford Achilles Tendon Atlas (Cohen et al. 2026, CELLxGENE `ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad`) ЯВЛЯЛСЯ ИСХОДНОЙ DISCOVERY-КОГОРТОЙ ПРОЕКТА MTJCORE!**

В архитектуре MTJCore:
1. **Discovery-когорта (Achilles):** Cohen et al., 2026 (`data/raw/achilles/ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad`). Именно на этих 5 донорах и 1 491 переходных ядрах в Stage 4 была выведена замороженная 1 718-генная сигнатура MTJCore (`frozen_myonuclear_signature.tsv`).
2. **Replication-когорта 1 (Semitendinosus):** E-MTAB-12529 (Karlsen et al., 2023, J. Cell Sci., 3 донора). На ней в Stage 5 была проведена независимая биологическая репликация (`STRONG_PROGRAMME_CONCORDANCE`, эмпирический $p = 10^{-5}$, направление конкордантности $92.1\%$).
3. **Secondary Loading-когорта:** E-MTAB-15400 (8 доноров).
4. **Proteomics-когорта:** PXD029307 (Karlsen et al., 2022, iScience).

### Методологическое следствие
Попытка использовать атлас Cohen et al. (2026) в качестве «третьей независимой репликации MTJCore» представляла собой **грубейшую ошибку круговой логики (100% утечка обучающих данных / train-test contamination)**. Нельзя независимо реплицировать молекулярную сигнатуру на том же самом наборе данных, на котором эта сигнатура была открыта и сформирована.

---

## 5. Сводная классификация статусов данных

В соответствии с правилами аудита зафиксированы следующие статусы:

| Компонент данных | Статус | Комментарий |
|---|---|---|
| Наличие в оригинальном исследовании | `PRESENT_IN_ORIGINAL_STUDY` | Все 64 862 клетки, включая 22 146 мионуклеов, получены из образцов Cohen et al. |
| Доступность в публичной матрице | `AVAILABLE_IN_PUBLIC_MATRIX` | Доступны на CZ CELLxGENE (`ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad`) со слоем сырых отсчётов |
| Доступность метаданных доноров | `AVAILABLE_WITH_DONOR_METADATA` | 5 доноров (`MSK0785`, `MSK1250`, `MSK1556`, `MSK1687`, `MSK1691`) с полной разметкой тканей |
| Пригодность для независимой репликации MTJCore | **NOT_SUITABLE_FOR_REPLICATION** | **НЕДОПУСТИМО.** Датасет является обучающей (Discovery) когортой MTJCore. Саморепликация запрещена. |
