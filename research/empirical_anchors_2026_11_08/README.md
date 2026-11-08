# Research Cycle 8: Empirical Local Energy Anchors (CORRECTED)

## Воспроизведение результатов (Reproduction Instructions)

### 1. Извлечение исходных данных Franke et al. 2020 (PMC7332772):
```bash
python research/empirical_anchors_2026_11_08/extract_franke_data.py
```
Извлекает 3D T1-МРТ анатомический объём gastrocnemius medialis ($379.89$ мл), временные ряды ³¹P-MRS динамического накопления тепла реакции (`Energy_exp`, 11 точек) и sEMG статистику из архива `plantar_supp.bin` в файл `franke2020_extracted_measurements.json`.

### 2. Расчёт физической модели идентифицируемости (3-Level Measurement Maps):
```bash
python research/empirical_anchors_2026_11_08/identifiability_physical.py
```
Вычисляет матрицы Якоби, SVD-ранги, обусловленность и базисы нуль-пространств на трёх уровнях:
- Уровень 1: Условный математический полный ранг (P8 = 7/7, $\kappa_{\text{eff}} = 15.39$).
- Уровень 2: Практическая идентифицируемость с неизвестными nuisance-параметрами (ранг 7/11, дефект = 4).
- Уровень 3: Эмпирическая идентифицируемость на данных человека (`NOT_EMPIRICALLY_IDENTIFIED`).

### 3. Выполнение научных экспериментов EXP-0032..EXP-0036:
```bash
python research/empirical_anchors_2026_11_08/experiments.py
```
Производит расчёт:
- EXP-0032: Анатомическая МРТ волюметрия vs сценарный активный объём и искажение плотности потока АТФ.
- EXP-0033: Абсолютная спектроскопия покоя (Edwards et al. 2013), энтальпия $\Delta_R H = 21.0$ кДж/моль vs потенциал Гиббса $\Delta G = -54.0$ кДж/моль и синхронизированная ёмкость фосфагенового пула ($111.4$–$947.0$ Дж, размах $8.50$).
- EXP-0034: Физиологический базовый расход $M_{\text{loc}}$ (квадрицепсный катетеризационный эталон $0.0064 \pm 0.0017$ ммоль/л/с с пометкой `MODEL_ASSUMED_QUADRICEPS_TRANSFER` vs $2.25\times$ неопределённость ASL и $6.67\times$ неопределённость NIRS).
- EXP-0035: Разрешение нуль-пространства $(\eta_{\text{loc}} \cdot \Delta G_{\text{ATP}})$ через спектроскопический канал свободной энергии (условный ранг 7/7; практический дефект ранга 4 в 11D системе; эмпирически не идентифицирован).
- EXP-0036: Аудит масштабирования и сохранение изоляции 9D quotient D2; TARGET-CPE45: NOT EXTERNALLY VALIDATED.

### 4. Запуск тестов Cycle 8:
```bash
python -m unittest discover -s research/empirical_anchors_2026_11_08 -p "test_*.py"
```
