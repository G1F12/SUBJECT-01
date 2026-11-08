# SUBJECT-01 — handoff Research Cycle 7 (Identifiability Repair & Final Consistency Audit)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
Cycle 7 исходная база: c1e75ca293ad385efa25a74843431870dda162ad.
Исследовательская ветка ремонта: correction/cycle7-identifiability-repair-20261108.
Итоговый main SHA проверяется через GitHub после PR и merge.

Ключевые документы Cycle 7 (Identifiability Repaired):
- research/local_muscle_bridge_2026_11_07/REPORT.md (полный научный отчёт с выверенной таблицей Claim Audit)
- research/local_muscle_bridge_2026_11_07/MATHEMATICS.md (доказательства симметрий, разграничение D2 vs 7-параметрической модели, ранги M1-M7)
- research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md (разделение 4 задержек, термодинамические эквиваленты, буфер PCr vs оборот ATP)
- research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md (категоризация данных, открытость Cannon 2014 PMC4262339)
- research/local_muscle_bridge_2026_11_07/LIMITATIONS.md (протокол отзывов, точные сценарные границы 42.8-77.1%, ранги 0/7..6/7)
- research/local_muscle_bridge_2026_11_07/README.md (инструкция по воспроизведению)
- research/local_muscle_bridge_2026_11_07/identifiability.py (пайплайн расчёта Якобиана, SVD, FIM и профилей правдоподобия)
- research/local_muscle_bridge_2026_11_07/identifiability_results.json (воспроизводимые численные ранги и нуль-пространства)

Результаты ремонта модели идентифицируемости:
1. Устранено критическое несоответствие между текстом отчёта (ранг 9/9 на 9 параметрах) и кодом `identifiability.py`:
   - Модель `LocalBridgeModel` параметризована 7 физиологическими параметрами: eta_loc, PCr_rest_mM, V_active_L, dG_ATP_kJ_mol, tau_PCr_rec_s, Q_loc_max_mM_s, M_loc_mM_s.
   - Механическая мощность P_ext(t) верифицирована как заданный эргометрический вход (rank M1 = 0/7).
   - Устранён баг пропуска V_active в M6 (_vol_ vs volume) через словарь TOPOLOGY_CHANNELS.
   - Введена поблочная масштабная нормировка матрицы Якоби (dimensionless RMS sensitivity).
   - Точные воспроизводимые ранги: M1=0/7, M2=3/7, M3=4/7, M4=3/7, M5=4/7, M6=5/7, M7=6/7.
   - Доказано, что максимальный ранг M7 равен строго 6/7 из-за неустранимой скалярной коллинеарности (eta_loc * dG_ATP).
2. Энергетическая метрология и термодинамика:
   - Разграничены dG_ATP (-50..-64 кДж/моль), dG_PCr (-34..-45 кДж/моль) и dG_CK (-10..-15 кДж/моль).
   - Буферная ёмкость PCr: 204.8..1021.4 Дж (размах 4.99).
   - Отношение W_5s / dE_PCr (0.44..1.50) классифицировано как диагностический артефакт неполного баланса и занижения активного объёма, а не истинный КПД > 100%.
   - Зафиксирована мультимодальность калибровки (T2*-MRI, DCE-MRI, US+HD-sEMG для объёма; A-V difference, ASL, NIRS для baseline).
   - Доказана структурная идентифицируемость задержки транспорта и постоянной времени ткани (kappa_FIM = 6.89, det > 0).

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=13, ISS=18, SRC=62.

Следующий приоритет (Cycle 8):
Получение данных многосрезовой МРТ-волюметрии (V_active) и изолированного локального базального расхода (M_loc) до перехода к предсказанию мощности всего тела.
