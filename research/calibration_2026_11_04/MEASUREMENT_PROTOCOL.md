# Реальная измерительная модель и pre-test уточнение схемы

Prereg0446eaad опубликован до extraction. Новая когорта — Lendt et al.,
DOI10.1186/s12966-024-01646-y, sourceZenodo10.5281/zenodo.13477128v1.0.0,
CCBY4.0. MechanicalW является prescribed ergometer workload, не независимым
output способности. Не тестируемCPE45power на этой величине.

CPET: Metalyzer3B,Cortex; gas calibration перед каждымsession поmethods;
ergoselect100 stationary cycle,30/60/90/120/150W для sourceID≤50,
50/75/100W дляsourceID>50,6min each,5min recovery. Два исходных протокола
сохраняются как task/covariate различие, не объединяются в одинаковые trials.
Наша новая test-группа n%5==0 не равна publisherMLsplit и отделена по людям.

Имена колонок Sauerstoffaufnahme/Kohlendioxidabgabe — L/min, подтверждены
paper/sourcecodeWeir recipe иdevelopment numeric consistency; Leistung —W,
Trittfrequenz —rpm,t —elapsedh:m:s. Sourcecode stageend390+660k seconds;
preregisteredfinal60s window=[end−60,end], не авторские3min summary.
Используется time-weighted trapezoid на наблюдаемых соседних точках сgap≤15s,
coverage≥80%,observed≥30s. Совпадающие округлённые timestamps усредняются из
реально зарегистрированных breath samples, без interpolation/imputation.
Missingcadence/power остаётсяNone; walking не получает выдуманные0W.
Gas requirements и outputpower requirements разделены, чтобы не терять
реальные passive/standinggas из-за отсутствия cadence наtreadmill.

ZeroW recovery не приравнивается passiveRMR. В большинстве nativeCPET files
пятиминутные паузы представлены gap, поэтому recoveryVO2/paidrecharge **NOT
OBSERVED**, а не интерполированы. Предварительное developmentчтение обнаружило
только один полностью покрытый candidateinterboutwindow; его task/cadence/power
будут проверены отдельно, не универсализированы.

Отдельный файлwalk, исходнаяwindow330..390s: sitting дляID>50, standing дляID≤50.
Это measured pulmonary gas baseline в указанной posture, на тех же людях,
но другой task/file. Ни fastingRMR, ни cyclingunloadedcost из него автоматически
не следуют. Предложенныйbaseline_slope оценивает cost=Bperson+bW и проверяется
как ограниченная переносимая эмпирическая гипотеза, не как измеренныйηD2.

PrimarycostE=(3.9VO2+1.1VCO2)4184/60 W, source's published recipe.
AlternativeWeir coefficients3.941/1.106 будут sensitivitycheck, не новый исход.
E is gas-derived fuel-cost estimate, **не независимое измерение heat/ATP**.
DeviceEnergieumsatz и авторскиеEEresults — derived, не второе энергетическое
наблюдение. PCr, activevolume, localO2 transport и MVC/twitch отсутствуют.

Модель наблюдения:
```
yO2(t)=gO[alpha(t) v_local(t-delay)+v_other(t)] * Ktransport(t)+bO+epsO
yCO2(t)=gC vCO2,pulmonary(t)+bC+epsC
Esystemic=cO yO2+cC yCO2
PCr_signal=gP cPCr Vsample; Efast=Gamma cPCr Vactive
```
Ktransport — measurement/transport nuisance, не новое заявленное physiology
state. alpha,other,delay,gains,offsets неизвестны; systemicabsolute anchor
не определяет отдельноlocalQ,M,η,Ci. PCr reference/activevolume не наблюдаются
в этой когорте; данные других людей не подставляются как еёindividualstates.

Дляflat baseline/slowkinetic profiles нет IDENTIFIEDstatus. Statisticalprecision
при фиксированных gain/offset не включает systematiccalibration uncertainty.
Новыйmodel_lock фиксирует всеparams/code/developmentdata до открытияtest.
Проверкаcost и еёуспех не снимают NOTEXTERNALLYVALIDATED дляTARGET-CPE45.
