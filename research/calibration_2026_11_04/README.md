# Reproduction — Cycle 6

Python3.12, корневой requirements.txt. Быстрая offline проверка (реальные
измерительные snapshots, не синтетические human data):

```powershell
python -m unittest discover -s research/calibration_2026_11_04 -p test_calibration.py
python research/calibration_2026_11_04/reproduce.py
python research/calibration_2026_11_04/verify.py
```

verify запускает все Foundation/Integrated/CPE45/Recovery/Observability проверки
и новые тесты. Логи/exitcodes в verification.json; исторические отчёты не меняются.
manifest.json фиксирует source snapshots, locks, результаты, код и документы.
Replay optimizer tolerance .001 для pulmonary fits ниже1s native clock;
остальные метрики rtol2e−6/atol2e−5, hashes/code locks точные.

Native retrieval отдельно, требует публичной сети и не входит в offline replay:

```powershell
python research/calibration_2026_11_04/acquire.py --verify-cache
python research/calibration_2026_11_04/native_replay.py
```

URL/SHA/CRC/версии/лицензии в retrieval JSON. native_replay получает отсутствующие
public members, сверяет native hashes и заново вычисляет измерительные summaries
без перезаписи snapshots/locks. Raw cache tmp/calibration_raw ignored.
Не запускать models.py --test повторно и не менять model_lock/models.py/dataset.py:
13test людей просмотрены, independent result immutable. Для численного replay
используется временный output; повторное independent claim запрещено.
Synthetic parameter recovery только unit software control; не metabolic anchor.
