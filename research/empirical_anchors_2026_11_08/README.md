# Research Cycle 8: Empirical Local Energy Anchors

## Воспроизведение результатов (Reproduction Instructions)

### 1. Извлечение исходных данных Franke et al. 2020 (PMC7332772):
```bash
python research/empirical_anchors_2026_11_08/extract_franke_data.py
```
Извлекает 3D T1-МРТ анатомический объём gastrocnemius medialis ($379.89$ мл), временные ряды ³¹P-MRS динамического накопления тепла реакции (`Energy_exp`, 11 точек) и sEMG статистику из архива `plantar_supp.bin` в файл `franke2020_extracted_measurements.json`.

### 2. Расчёт физической модели идентифицируемости (Measurement Maps P1–P8):
```bash
python research/empirical_anchors_2026_11_08/identifiability_physical.py
```
Вычисляет матрицы Якоби, SVD-ранги, обусловленность и базисы нуль-пространств для идеализированных топологий Cycle 7 (M1–M7) и реалистичных физических измерительных карт (P1–P8).

### 3. Выполнение научных экспериментов EXP-0032..EXP-0036:
```bash
python research/empirical_anchors_2026_11_08/experiments.py
```
Производит расчёт:
- EXP-0032: Анатомическая МРТ волюметрия vs активный объём и искажение плотности потока АТФ.
- EXP-0033: Абсолютная спектроскопия покоя, энтальпия $\Delta_R H = 21$ кДж/моль vs потенциал Гиббса $\Delta G = -54$ кДж/моль (множитель $2.57$) и ёмкость фосфагенового пула ($111.2$–$945.8$ Дж).
- EXP-0034: Физиологический базовый расход $M_{\text{loc}}$ (инвазивный катетеризационный эталон $0.0064 \pm 0.0017$ ммоль/л/с vs $2.25\times$ неопределённость ASL и $6.67\times$ неопределённость NIRS).
- EXP-0035: Разрешение нуль-пространства $(\eta_{\text{loc}} \cdot \Delta G_{\text{ATP}})$ через спектроскопический канал свободной энергии (ранг 7/7, $\kappa_{\text{eff}} = 15.39$).
- EXP-0036: Аудит масштабирования и сохранение изоляции 9D quotient D2; TARGET-CPE45: NOT EXTERNALLY VALIDATED.

### 4. Запуск тестов Cycle 8:
```bash
python -m unittest discover -s research/empirical_anchors_2026_11_08 -p "test_*.py"
```
