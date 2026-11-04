# Cycle 5: вычислительный протокол

База 4e900fbb337cf59efff8b75f473528485c7cc045. EXP-0019..0022 свободны
после проверки всех реестров. Один агент OpenAI Codex; независимость аудита
означает повторный вывод из уравнений, не независимого внешнего рецензента.

До новых вычислений: исторический recovery replay проходит. Старые 10 и 7 test
просмотрены; их результаты только воспроизводятся, никакой новой настройки.
Новая человеческая validation запускается только при получении подходящей
независимой когорты и отдельной опубликованной preregistration до extraction.
В этом цикле синтетические результаты не заменяют эту проверку.

EXP-0019: аналитическая эквивариантность D2, independently assembled log-Jacobian,
SVD/FIM, channel ablations M1..M7. EXP-0020: public-source retrieval/access audit.
EXP-0021: конечная сетка virtual designs, D/E-optimality на общей определённой
проекции, uncertainty corners, профиль tau. EXP-0022: quotient reduction,
synthetic recovery, noise/missing/sampling/sync/discrepancy/convergence.

Неизменённый recovery engine — источник dynamics. Шум — условный независимый
Gaussian: power 20 W, oxidative 40 W, relative PCr .02, absolute reserve 160 J,
independent eta .01. Это design assumptions, не паспортные ошибки приборов.
PCr=fast reserve — проверяемая гипотеза observation map, не установленный факт.
VO2=oxidative_W / known caloric equivalent и известная local allocation —
идеализированная калибровка. Реальное pulmonary VO2 не равно local ATP flux.

Все ранги локальны, порог SVD 1e-6; публикуются спектры и пороговая чувствительность.
Нулевые направления не получают finite marginal confidence intervals через pinv.
D/E сравниваются только на одной проекции/единицах/шуме, с отдельным временем
наблюдения; anchors учитываются один раз, не на каждом отсчёте.
Подмена неизвестного calibration gain фиксированным запрещена в интерпретации.

Остановочный критерий: конечная сетка протоколов и трёх parameter corners;
малые synthetic replicates предназначены для stress tests, не coverage estimation.
Полноранговая локальная FIM не считается доказательством global identifiability.
NO_GO, NOT EXTERNALLY VALIDATED и прежние отрицательные выводы сохраняются.
