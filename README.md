# SUBJECT-01 — The Strongest Project

**Единый исходный репозиторий исследования.** Старт проекта: 2026-11-01. Архивы старых исследований здесь только импортированные первичные артефакты, а не конкурирующие источники истины.

1. Начать с [`PROJECT_STATE.md`](PROJECT_STATE.md), затем [`GOVERNANCE.md`](GOVERNANCE.md) и [`handoffs/CURRENT.md`](handoffs/CURRENT.md).
2. Читать `registry/*.json` для идентификаторов и статусов; отчёты — для деталей.
3. Перед исследованием проверять дубликаты по ID, гипотезе, источникам и тестируемому утверждению.
4. Изменения добавлять в тот же репозиторий; записывать доказательства, негативные результаты и `CHANGELOG.md`.
5. Завершать обновление `python tools/validate_repository.py && python tools/reproduce_foundation.py` и Git commit.

**Только фактически записанный commit считается сохранённым изменением.** Для долговременного хранения нужен удалённый приватный Git-репозиторий, резервное копирование и проверка синхронизации. Сейчас remote отсутствует; Git bundle — единовременный перенос первого коммита, не серия ZIP-версий.

## Восстановление из единовременного начального Git bundle

```
git clone SUBJECT01_GENESIS.bundle SUBJECT01
cd SUBJECT01
git log -1 --oneline
python tools/validate_repository.py
python tools/reproduce_foundation.py
```

Для будущих сессий используйте **GitHub/Git remote**, а не повторное создание новых ZIP после каждого исследования. Статусы `arithmetic_reproduced`, `externally_verified`, `unverified`, `open` нельзя смешивать.
