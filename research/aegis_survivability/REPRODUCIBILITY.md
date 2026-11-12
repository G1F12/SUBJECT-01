# AEGIS-01 — REPRODUCIBILITY & VERIFICATION PROTOCOL

## 1. СРЕДА ИСПОЛНЕНИЯ И ТРЕБОВАНИЯ

- **Операционная система:** Windows 10/11 x64 (полная кросс-платформенная совместимость с Linux/macOS).
- **Интерпретатор Python:** Python 3.12.x (минимально допустимая версия: Python 3.10+).
- **Зависимости:**
  - `numpy >= 1.24.0` (протестировано на 2.5.4)
  - `scipy >= 1.10.0` (протестировано на 1.18.1)
  - `pytest >= 7.0.0` (протестировано на 9.2.0)
- **Отсутствие внешних сетевых зависимостей:** Все модели работают автономно, детерминированно и офлайн.

---

## 2. ПОШАГОВЫЙ ПРОТОКОЛ ВОСПРОИЗВЕДЕНИЯ

### Шаг 1: Клонирование / Переход в рабочую директорию
```powershell
Set-Location "D:\AEGIS-01"
```

### Шаг 2: Запуск полного исследовательского конвейера
```powershell
python aegis\run_all.py
```
*Ожидаемый вывод:*
```text
======================================================================
AEGIS-01 COMPUTATIONAL PIPELINE EXECUTION
======================================================================
[1/7] Running MODEL-01: Tissue Mechanics & Puncture/Cut...
[2/7] Running MODEL-02: Multilayer Protection & Wave Attenuation...
[3/7] Running MODEL-03: Neural Latency & Dodge Horizon...
[4/7] Running MODEL-04: Ballistic Energy Transfer & BABT...
[5/7] Running MODEL-05: Hemodynamic Stability & Hemorrhage...
[6/7] Running MODEL-06: Regeneration Dynamics & Oncogenic Limits...
[7/7] Running MODEL-07: Integrated Architecture Trade-offs...

[SUCCESS] All 7 models executed. Results stored in D:\AEGIS-01\data\results
Summary CSV generated: D:\AEGIS-01\data\results\summary_metrics.csv
```

### Шаг 3: Запуск набора автоматических тестов
```powershell
pytest tests -v
```
*Ожидаемый результат:* **42 passed in < 0.5s**.

---

## 3. СТРУКТУРА ТЕСТОВОГО ПОКРЫТИЯ

| Тестовый модуль | Число тестов | Проверяемые физические аспекты |
| :--- | :--- | :--- |
| `test_model_01_tissue_mechanics.py` | 7 | Масштабирование радиуса индентора, превосходство кератина панголина, Atkins-модель резания, чувствительность OAT. |
| `test_model_02_multilayer_protection.py` | 6 | Сохранение энергии акустической волны ($T_E + R_E = 1.0$), затухание в трехслойном композите, демпфирование. |
| `test_model_03_reaction_movement.py` | 7 | Закон Хёрша ($v = 6 d$), положительность латентности, нулевое смещение до истечения латентности, теорема горизонта уклонения. |
| `test_model_04_energy_transfer.py` | 4 | Сохранение импульса при баллистическом контакте, критерий VC, снижение BFD остеодермами. |
| `test_model_05_hemodynamic_stability.py` | 5 | Формула Торричелли, сохранение объема крови ($V_{\text{loss}} \le V_0$), смыв тромба при сдвиге $>40$ Па, фатальность разрыва аорты. |
| `test_model_06_regeneration_dynamics.py` | 4 | Разрыв шкал «закрытие раны vs нейротизация», безрубцовое заживление *Acomys*, подавление онкогенеза копиями $TP53$. |
| `test_model_07_integrated_architecture.py` | 5 | Баланс массы, закон Клайбера, тепловой коллапс сплошного панциря, Парето-доминирование архитектуры ARCH-4. |
| `test_registry_integrity.py` | 4 | Валидность всех 8 файлов JSON, формат 8-символьных ID, **100% отсутствие коллизий с SUBJECT-01**, целостность перекрестных ссылок. |
| **ИТОГО** | **42** | **100% PASS** |

---

## 4. СТАТУС ВЕРИФИКАЦИИ И ХЕШИ ДАННЫХ

Все генерируемые артефакты в `data/results/` являются детерминированными.  
Любое изменение констант или уравнений приводит к воспроизводимому изменению метрик в `summary_metrics.csv`.
