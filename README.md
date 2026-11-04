# SUBJECT-01 — The Strongest Project

**Единый исходный репозиторий исследования.** Старт проекта: 2026-11-01. Архивы старых исследований здесь только импортированные первичные артефакты, а не конкурирующие источники истины.

1. Начать с [`PROJECT_STATE.md`](PROJECT_STATE.md), затем [`GOVERNANCE.md`](GOVERNANCE.md) и [`handoffs/CURRENT.md`](handoffs/CURRENT.md).
2. Читать `registry/*.json` для идентификаторов и статусов; отчёты — для деталей.
3. Перед исследованием проверять дубликаты по ID, гипотезе, источникам и тестируемому утверждению.
4. Изменения добавлять в тот же репозиторий; записывать доказательства, негативные результаты и `CHANGELOG.md`.
5. Завершать обновление `python tools/validate_repository.py && python tools/reproduce_foundation.py && python tools/audit_foundation.py`, затем Git commit и проверка опубликованного HEAD.

**Только реально опубликованный и проверенный GitHub-коммит является подтверждением постоянной синхронизации.** Канонический репозиторий: публичный `G1F12/SUBJECT-01` (DEC-0005). Запрещено коммитить секреты и персональные медицинские данные. Исходный Git bundle — исторический первоначальный перенос, не серия ZIP-версий.

## Восстановление из единовременного начального Git bundle

```
git clone SUBJECT01_GENESIS.bundle SUBJECT01
cd SUBJECT01
git log -1 --oneline
python tools/validate_repository.py
python tools/reproduce_foundation.py
```

Для будущих сессий используйте **GitHub/Git remote**, а не повторное создание новых ZIP после каждого исследования. Статусы `arithmetic_reproduced`, `externally_verified`, `unverified`, `open` нельзя смешивать.

## Независимый аудит Foundation

- [Аудит 21 источника](audits/2026-11-01_sources.md) — метаданные и доступные аннотации, не full-text/retraction clearance.
- [Проверки Foundation](tools/audit_foundation.py) — 45 строк вычислительных сценариев, условные ограничения кислородного извлечения.
- Все исходные импортированные результаты сохранены, включая отрицательные и непроверенные утверждения.

## Интегрированная частично калиброванная модель

[Отчёт цикла](research/integrated_2026_11_01/REPORT.md) и
[аудит данных](research/integrated_2026_11_01/DATA_AUDIT.md).
Python >=3.12; `pip install -r requirements.txt`.
После трёх прежних проверок выполнить:

```text
python research/integrated_2026_11_01/test_model.py
python research/integrated_2026_11_01/experiments.py --check
```

Полная калибровка/валидация организма не завершена; сценарный uplift не эффект
вмешательства. Индивидуальные биологические эксперименты не выполнялись.

## TARGET-CPE45 — обязательная дополнительная цель

[Научно-инженерная спецификация](research/targets/COMBAT_LIKE_ENDURANCE_45MIN.md),
[машинная цель](research/targets/CPE45.json): сохранять комплексную физическую
работоспособность 2700 s при чередовании интенсивных действий и восстановления.
Принятие требования не подтверждает его достижимость. Пороги пока не калиброваны;
исторические EXP/Pareto по новой цели не оценены; биологические вмешательства NO_GO.

Измерение сохранённых временных рядов: `python tools/cpe45.py --input observations.json --output metrics.json`.
Контракт данных/единиц/окна и допустимые разрывы описаны в спецификации. Новая проверка:

```text
python -m unittest discover -s tests -p test_cpe45.py
```

Динамический цикл реализован отдельно: [CPE45 REPORT](research/cpe45_2026_11_04/REPORT.md).
15 сценариев, раздельные состояния энергии/утомления/тепла; проверка переноса
отрицательная: coupled RMSE378.54W против constant115.34W. ISS-0011 открыт,
модель not_empirically_validated; NO_GO сохранён.

```text
python research/cpe45_2026_11_04/test_model.py
python research/cpe45_2026_11_04/experiments.py --check
```

## Recovery identification и независимая фальсификация

[Новый отчёт EXP-0015..0018](research/recovery_2026_11_04/REPORT.md):
пререгистрация,14development/7новыхtestучастников,идентифицируемость и causal audit.
Исправленная физическая модель не превзошлаbaseline:RMSE361.71vs126.54W.
PCr recoverytau не установлена; энергетические параметры имеют scaleconfounding.
Исторический провал сохранён, CPE45 NOT EXTERNALLY VALIDATED,NO_GO.

```text
python research/recovery_2026_11_04/test_recovery.py
python research/recovery_2026_11_04/reproduce.py --check
```

При отсутствии cache исходные общедоступные OSFfiles скачиваются с проверкой
SHA256; из-за неустановленной rawлицензии сами XLSX не перепубликуются.

### Research Cycle 6

[Physiological calibration report](research/calibration_2026_11_04/REPORT.md):
real VO2/VCO2–workload data and limited independent systemic-cost validation.
This does not validate local reserve physiology or TARGET-CPE45. Offline replay
and public native retrieval are separate; see [reproduction](research/calibration_2026_11_04/README.md).
