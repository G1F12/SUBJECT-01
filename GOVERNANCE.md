# Research governance v1 (policy, not a software release)

## Hard rules

1. Git repository is canonical; do not treat chat memory, handoff text or detached ZIPs as a second source of truth.
2. Permanent prefixes: `HYP` hypothesis, `EXP` experiment, `FND` finding, `NEG` negative/counterexample, `DEC` decision, `ISS` issue, `SRC` source; four-digit sequential IDs. **Never recycle or renumber existing IDs.**
3. Registry content is cumulative: amend status, link a superseding ID or mark `retired`; do not erase failed work or sources.
4. Evidence taxonomy: `unverified` (hypothesis), `arithmetic_reproduced` (computational calculation only), `externally_verified` (independent evidence check plus provenance), `empirically_validated` (measured relevant function with protocol and controls). Never promote statuses without evidence.
5. Model inputs, assumptions, environment, data license/access, full code and output hashes must be stored. If a dataset cannot be redistributed, store immutable URL, version, checksums and a retrieval recipe, never secrets/private health data.
6. Before running an experiment, search registry by mechanism, endpoints, dataset and previously rejected hypotheses.
7. Record results **including negative outcomes**, failed runs, uncertainties and restrictions on extrapolation. Any change to a past result must preserve original provenance.
8. For every completed research change: update relevant registries, PROJECT_STATE.md, CHANGELOG.md and handoffs/CURRENT.md, run validators, then commit once. Avoid per-experiment ZIP/release creation.
9. Multi-AI: store agent/model metadata, task, prompt or reproducible instructions, referenced data/commit and disagreements; independent reviewer does not inherit trusted status. Only adjudicated/verified claims merge.
10. At beginning of a new chat: read Git HEAD, PROJECT_STATE.md, open issues, current handoff and current registries before planning new research; at end prepare a short handoff with commit ID and known unresolved issues.
11. Visibility/privacy: **this repository is intentionally PUBLIC by explicit user decision (DEC-0005)**. Publish only appropriate scientific code, claims and shareable data. Never commit secrets, identifying health data, restricted material or unpublished personal datasets. Changing repository visibility requires a separate decision.
12. Safety/regulation: computational analysis first; any wet-lab or biological interventions require independent scientific and ethical review and relevant permissions. Model calculations are not efficacy evidence.

## Change and commit protocol

- Branch for nontrivial proposals, verify scope and assumptions.
- Add or update stable registry IDs; link each finding to experiment/source and write limitations.
- Check hashes; reproduce; ensure no duplicate or contradictory unresolved entries.
- Update state, changelog and handoff. Commit and record the resulting SHA in user-visible completion report.
- When remote configured, push and **verify remote HEAD equals local SHA**. Without that verification say "local commit only".
- Periodic encrypted backups are independent of versioning and should be tested for recovery.

## Source audit policy

Legacy source imports are references with provenance, **not externally verified** evidence; a DOI URL alone is not a verification. Reviews should check publication title, year, design, numeric claim, applicability, conflicts, full text and retraction/correction status.

## Дополнительная обязательная цель TARGET-CPE45

DEC-0007 (02.11.2026): оценка 2700-секундной комплексной работоспособности при
перемежающейся интенсивной нагрузке и восстановлении дополняет главную цель.
Спецификация: research/targets/COMBAT_LIKE_ENDURANCE_45MIN.md; CPE45.json.
Будущие сравнения архитектур обязаны включать самостоятельный CPE45 endpoint
и post-функцию; отсутствие данных означает not_assessed, а не достижение цели.
EXP-0001..0010 и их Pareto сохраняются без ретроактивного повышения статуса.
Интенсивность/пороги требуют научного обоснования; synthetic PASS не empirical
validation. Разработка динамики — следующая задача ISS-0011, не результат этой
регистрации. Политика NO_GO и основная цель проекта остаются в силе.

### Пререгистрация кандидатной спецификации `CPE45` до сбора человеческих данных (DEC-0056)

Во избежание ретроспективной подгонки порогов после сбора человеческих данных `MEASUREMENT-3` допускается пререгистрация кандидатного протокола и критериев успеха в отдельном файле `research/targets/CPE45_CANDIDATE_FINAL_SPEC.json` при соблюдении четырёх обязательных инвариантов:
1. Канонический файл `research/targets/CPE45.json` остаётся неизменным (`success_thresholds: null`, `historical_experiments_cpe45_status: "not_assessed"`), а исторические `EXP-0001..0010` не переоцениваются до эмпирической валидации и отдельного утверждающего `DEC`.
2. Кандидатная спецификация обязана содержать явные поля `"empirical_validation": false` и `"status": "PREREGISTERED_CANDIDATE_NOT_EMPIRICALLY_VALIDATED"`.
3. Исследовательский тепловой порог прохождения (`< 38,5 °C` в умеренном климате / `< 39,0 °C` для мониторируемых акклиматизированных взрослых) строго отделён от медицинского предела немедленной остановки теста (`≥ 39,5 °C`).
4. Прохождение синтетических тестов `tools/cpe45.py`, `evaluate_session()` и `evaluate_cohort()` проверяет исключительно программно-измерительный контракт и **никогда** не считается эмпирическим подтверждением `CPE45` или закрытием Этапа 2.
