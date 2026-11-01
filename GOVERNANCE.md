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
