# Исследовательский модуль: Local Muscle Energetics & PCr–VO₂ Bridge (Cycle 7)

**Директория:** `research/local_muscle_bridge_2026_11_07/`  
**Канонический репозиторий:** `G1F12/SUBJECT-01`  
**Ветка:** `research/local-muscle-bridge-20261107`  

---

## 1. Назначение и состав модуля

Модуль реализует трёхслойный измерительный мост между механической мощностью, локальной энергетикой мышцы (³¹P-MRS) и системным газообменом (CPET), математический анализ идентифицируемости и воспроизводимые вычислительные эксперименты на основе реальных данных (Moll et al. 2017, Dissertation 2018).

### Структура файлов:
- `PLAN.md` — План исследования Cycle 7 и перечень задач.
- `REPORT.md` — Итоговый научный отчёт Cycle 7.
- `DATA_AUDIT.md` — Метрологический аудит источников данных и открытых лицензий.
- `MATHEMATICS.md` — Строгие аналитические доказательства симметрий и рангов Якобиана.
- `MEASUREMENT_MODEL.md` — Архитектура трёхслойного измерительного моста.
- `LIMITATIONS.md` — Физиологические, измерительные и модельные ограничения.
- `acquire.py` — Скрипт воспроизводимого сбора метаданных и аудита источников.
- `digitize_moll_data.py` — Оцифровка и структурирование измерений диссертации Moll 2018.
- `moll2018_extracted_measurements.json` — Оцифрованные данные экспериментов (Ch 2, 3, 4, 5).
- `identifiability.py` — Численный анализ SVD, Якобиана, FIM и Profile Likelihood.
- `identifiability_results.json` — Результаты анализа идентифицируемости M1–M7.
- `experiments.py` — Вычислительные эксперименты EXP-0027..EXP-0031.
- `experiment_results.json` — Итоги экспериментов EXP-A..EXP-E.
- `test_local_bridge.py` — Модульные тесты физических и математических инвариантов.
- `manifest.json` — Контрольные суммы SHA256 всех артефактов цикла.

---

## 2. Воспроизведение вычислений и тестов

Все команды запускаются в корневой директории репозитория:

```powershell
# 1. Оцифровка и проверка согласованности данных
python research/local_muscle_bridge_2026_11_07/digitize_moll_data.py

# 2. Анализ идентифицируемости (SVD, FIM, Profile Likelihood)
python research/local_muscle_bridge_2026_11_07/identifiability.py

# 3. Запуск экспериментального комплекса (EXP-0027..EXP-0031)
python research/local_muscle_bridge_2026_11_07/experiments.py

# 4. Запуск модульного тестирования измерительного моста
python -m unittest discover -s research/local_muscle_bridge_2026_11_07 -p "test_*.py"
```
