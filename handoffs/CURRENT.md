# SUBJECT-01 — handoff Research Cycle 7 (Scientific Correction & Audit)

Канон: G1F12/SUBJECT-01. Начать с git status, git fetch origin и сверки HEAD с origin/main.
Cycle 7 исходная база: f8e6761d5f58e71ff8bdf304741414d974359d8a; merge commit: 90ec6c642acc661a3091a9aa8fafc91d59417458.
Исследовательская ветка аудита: correction/cycle7-scientific-audit-20261107.
Итоговый main SHA проверяется через GitHub после PR и CI.

Ключевые документы Cycle 7 (Corrected):
- research/local_muscle_bridge_2026_11_07/REPORT.md (полный научный отчёт с таблицей Claim Audit)
- research/local_muscle_bridge_2026_11_07/MATHEMATICS.md (доказательства симметрий, разграничение D2 vs 3-слойной модели)
- research/local_muscle_bridge_2026_11_07/MEASUREMENT_MODEL.md (разделение 4 задержек, буфер PCr vs оборот ATP)
- research/local_muscle_bridge_2026_11_07/DATA_AUDIT.md (категоризация данных, открытость Cannon 2014 PMC4262339)
- research/local_muscle_bridge_2026_11_07/LIMITATIONS.md (протокол отзывов, сценарные границы 45-78%)
- research/local_muscle_bridge_2026_11_07/README.md (инструкция по воспроизведению)

Результаты аудита и исправлений:
1. Заявления о новых эмпирических корреляциях R2=0.919 и R2=0.978 ОТОЗВАНЫ. Подтверждены первоисточники Moll et al. 2017: R2=0.73, p<0.005; R2=0.55, p=0.01; R2=0.65, p<0.01.
2. Доля 66.3% реклассифицирована как сценарный расчёт при КПД 0.28 (диапазон 45-78%).
3. Устранена ошибка размерности в EXP-0030: разграничены буфер PCr (205-1021 Дж) и оборот ATP (>11,500 Дж). По Cannon et al. 2014 Table 1 (PMC4262339), окисление даёт 88-95% оборота ATP, PCr — лишь 1.5-3.0%. КПД > 1.0 аннулирован.
4. Сравнение EXP-0031 ОТОЗВАНО: RMSE 0.65 Вт получен из захардкоженных прогнозов, in-sample константы и N=2 точек 1 человека.
5. Статус Cannon et al. (2014) исправлен на OPEN_ACCESS_PMC.

Научный статус:
- TARGET-CPE45: NOT EXTERNALLY VALIDATED.
- Биологические вмешательства: NO_GO.
- Архитектуры I/II/III на 2700 секундах: преимуществ не показано.
- Реестры: EXP=31, HYP=6, FND=32, NEG=24, DEC=13, ISS=18, SRC=62.

Следующий приоритет (Cycle 8):
Получение данных многосрезовой МРТ-волюметрии (V_active) и изолированного локального базального расхода (M_loc) до перехода к предсказанию мощности всего тела.
