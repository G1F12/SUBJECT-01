# SUBJECT-01 — Canonical current state

- **As of:** 2026-11-01. Foundation / computational-first.
- **Canonical source:** https://github.com/G1F12/SUBJECT-01 (public by explicit user decision DEC-0005).
- **Verified baseline:** EXP-0001..0006: standalone execution and all 7 imported CSVs reproduce byte-for-byte as CSV records; 13 imported file SHA256 checks PASS.
- **Independent arithmetic/feasibility audit:** 45 CSV rows checked with `python tools/audit_foundation.py`: PASS arithmetic; conditional Fick oxygen-content violation for +50%/+100% extraction-only scenarios at assumed CaO2 0.200 L/L. See FND-0007 / NEG-0003 / ISS-0007. No physiological calibration.
- **Source audit:** 21/21 citations checked for publication identity and accessible abstracts/publisher/regulator summaries, documented in `audits/2026-11-01_sources.md` and `registry/sources.json`. No full-text systematic audit or correction/retraction audit. Scope mismatches recorded in ISS-0006; no source upgraded to empirically validated efficacy.
- **Evidence status:** no proof of radical healthy-human augmentation. **NO_GO** for intervention or efficacy claims.
- **Registries:** `registry/*.json` are cumulative and retain original claims, negative results and permanent IDs. No historical A/B/C artifacts imported (ISS-0004).
- **Open issues:** ISS-0002..0007 except ISS-0001 resolved. Sol/Argon 4 independent reviews not performed (ISS-0005).
- **Next action:** source full-text quality/retraction check, calibrated physiological bounds, and independent validation data, preserving prior imported outputs.
- **Verification:** `python tools/validate_repository.py`; `python tools/reproduce_foundation.py`; `python tools/audit_foundation.py`; `git status --short`; `git rev-parse HEAD`.

Do not confuse metadata audit, arithmetic checks and independent empirical validation. Require GitHub commit and remote-head verification for any claim of permanent publication.

Integration verification, reviewer provenance, dimensional derivations and date/correction clarifications: `audits/2026-11-01_integration.md`. No comprehensive correction/retraction audit completed; one SRC-0003 correction notice observed.
