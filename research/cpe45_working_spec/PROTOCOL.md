# Протокол EXP-0149 · Рабочая спецификация и чувствительность порогов TARGET-CPE45

## Цель и граница утверждения

1. Сформировать воспроизводимую **рабочую спецификацию** `CPE45` — расписание переменной нагрузки на 2700 с, окна `early/late`, точки наблюдения `post45` и три уровня рабочих порогов (`strict`, `working_default`, `permissive`) — на основе проверенных человеческих данных `EXP-0139` и тепловых ограничений `EXP-0063 / EXP-0131`.
2. **Жёсткий инвариант канона:** файл `research/targets/CPE45.json` (`success_thresholds = null`, `physiological_validation = "not_done"`, `historical_experiments_cpe45_status = "not_assessed"`) **не изменяется** до внешней эмпирической калибровки на совместном 2700-с человеческом наборе (`DEC-0007`, `tools/validate_repository.py`). Все числовые значения этого эксперимента имеют статус `PROVISIONAL_WORKING_ASSUMPTIONS_PENDING_CALIBRATION`.

## Входы и воспроизводимость

- Пять проверенных исходных файлов `EXP-0139` (`mclaughlin_29120024.xlsx`, `recovery_raw/Power_rawdata.xlsx`, `norbury_24156741.xlsx`, `cpe45_human/task2.tab`, `cpe45_human/leg.csv`) со сверкой SHA-256 до чтения.
- Результаты `research/cpe45_human_evidence/RESULTS.json` (включая опубликованные сводки `Goodall` и `Marshall`) и тепловые огибающие `research/exp0063_pennes_bioheat_cpe45/RESULTS.json`.
- Измерительный контракт `tools/cpe45.py` и `research/targets/CPE45.json`.

## Проверки

1. Квантили распределений и доля реальных участников `EXP-0139`, проходящих каждый из трёх уровней рабочих порогов (`strict`, `working_default`, `permissive`) — по отдельным каналам, с сохранением явного статуса `UNASSESSED_NO_HUMAN_ANCHOR` для координации и манёвренности в метрах.
2. Чувствительность оценки падения мощности к ширине окон `early/late` (`1×1`, `2×2`, `3×3` спринта у Jutlah; `5`, `9`, `11` мин у McLaughlin).
3. Проверка исполнимости расписания `5×540 с` (`duty_cycle = 0,6444`), окон `540 / 2160 с` и точек `post45` через `tools/cpe45.py` на детерминированной синтетической фикстуре (`SYNTHETIC_PROTOCOL_CONFORMANCE_FIXTURE`, без утверждения физиологической валидации).
