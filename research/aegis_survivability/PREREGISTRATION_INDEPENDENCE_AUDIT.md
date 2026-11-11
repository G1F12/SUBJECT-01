# AEGIS-01 — PRE-REGISTRATION & INDEPENDENCE AUDIT
## Cryptographic Hash Verification, Chronological Provenance & Four-Tier Epistemic Taxonomy

**Document ID:** `AEGIS-DOC-C10B-PREREG-001`  
**Cycle:** 10B Forensic Audit  
**Status:** `PRE_REGISTRATION = UNVERIFIED`  
**Decision ID:** `DEC-0057` | **Issue ID:** `ISS-0046`  
**Audited Hash (SHA-256):** `225d6994d5b97539f52c1ef5968ee8ac5f96a8b4da37c1e057e983b5f2faea25`

---

## 1. Forensic Hash Audit: What Was Actually Hashed?

In Cycle 10, the following SHA-256 digest was claimed as a cryptographic pre-registration lock:
```
225d6994d5b97539f52c1ef5968ee8ac5f96a8b4da37c1e057e983b5f2faea25
```

### 1.1 Target of the Hash
- **Claimed in Documentation:** "Python code hash was generated and frozen."
- **Forensic Reality:** The hash did **not** correspond to any standalone file, script, or configuration on disk.
- Instead, it was computed directly from an in-memory multiline Python string literal assigned to the variable `FROZEN_MODEL_CODE` within `aegis/cycle10_models.py`:
  ```python
  FROZEN_MODEL_CODE = """
  def predict_keratin_modulus(w: float, p: float, theta_deg: float, mode: str) -> float:
      w_c = 0.18
      p_hill = 3.0
      e_solid_dry = 3.20  # GPa
      e_solid_wet = 0.18  # GPa
      e_solid = e_solid_wet + (e_solid_dry - e_solid_wet) / (1.0 + (w / w_c)**p_hill)
      p_factor = (1.0 - p)**2
      rad = math.radians(theta_deg)
      orient = math.cos(rad)**4 + 0.65 * math.sin(rad)**4
      mode_factor = 0.75 if mode == "tension" else (1.0 if mode == "compression" else 0.90)
      return e_solid * p_factor * orient * mode_factor
  """
  ```
- **File Match Status:** The file `aegis/cycle10_models.py` itself has a completely different SHA-256 hash. However, executing `hashlib.sha256(FROZEN_MODEL_CODE.strip().encode('utf-8')).hexdigest()` deterministically reproduces the exact claimed digest.

---

## 2. Chronological Provenance in Git

1. **First Appearance in Git:**
   - Commit `0f627c84899dc502ea6f123f68013e60f9002384` (AEGIS-01, Wed Nov 11 17:48:54 2026).
   - Commit `84d00dbdd73662447961014c8e2c555ed2754f67` (SUBJECT-01, Wed Nov 11 17:50:00 2026).
2. **Co-Commitment with Results:**
   - The declaration of the hash, the definition of the "frozen" code, the data tables for Li et al. (2010), and the data tables for Tombolato et al. (2010) were **committed simultaneously in the exact same git commit**.
   - There exists no prior commit, git tag, pull request, or external public ledger (e.g. OSF, Zenodo) where the model formulation was locked *before* the experimental results were evaluated.
3. **Data Availability Prior to Model Freezing:**
   - The papers Li et al. (2010) and Tombolato et al. (2010) were published in 2010.
   - An LLM agent operating in 2026 has full internal or retrieved access to published 2010 experimental values.
   - Therefore, chronological pre-registration cannot be established from a single atomic commit.

---

## 3. Post-Hoc Model Structural Changes

A prospective pre-registered model must not alter its functional structure in response to test dataset characteristics:
1. **Introduction of Bending Mode Factor:**
   In Cycle 9, `predict_keratin_modulus()` supported only two modes: tension ($0.75$) and compression ($1.00$). When Tombolato 2010 three-point bending coupons were evaluated in Cycle 10, the model formulation was modified to add:
   $$\text{mode\_factor} = 0.90\quad\text{if mode == 'bending'}$$
2. **Conclusion:** The model structure was directly tailored to accommodate the incoming bending test set, violating strict pre-registration independence.

---

## 4. The Four-Tier Epistemic Taxonomy

Scientific integrity demands that four distinct concepts—often conflated in machine learning literature—be strictly separated:

```
+===================================================================================================+
| Epistemic Tier                   | Definition                            | AEGIS Cycle 10 Status  |
+===================================================================================================+
| 1. REPRODUCIBLE_HASH             | A cryptographic hash of code or text  | VERIFIED               |
|                                  | that can be verified deterministically| (225d6994d5b9... is a  |
|                                  | by any independent third party.       | exact valid hash)      |
+----------------------------------+---------------------------------------+------------------------+
| 2. CHRONOLOGICALLY_PRE_REGISTERED| A model specification and hypothesis  | UNVERIFIED             |
|                                  | recorded in an immutable ledger       | (Co-committed in same  |
|                                  | BEFORE observing the test targets.    | commit with results)   |
+----------------------------------+---------------------------------------+------------------------+
| 3. INDEPENDENT_TEST_SET          | An experimental dataset collected by  | VERIFIED (Li 2010)     |
|                                  | independent investigators from a      | (Different laboratory, |
|                                  | different laboratory and species.     | different species)     |
+----------------------------------+---------------------------------------+------------------------+
| 4. TRUE_BLIND_HOLDOUT            | Target labels/measurements completely | UNVERIFIED / REFUTED   |
|                                  | withheld from modelers and context    | (Published 2010 data   |
|                                  | during inference execution.           | accessible in corpora) |
+===================================================================================================+
```

### Critical Rules:
- A `REPRODUCIBLE_HASH` is **NOT** proof of `CHRONOLOGICAL_PRE_REGISTRATION`.
- An `INDEPENDENT_TEST_SET` is **NOT** necessarily a `TRUE_BLIND_HOLDOUT` when working with historical scientific literature.
- Claiming `PRE_REGISTRATION = VERIFIED` requires proof of temporal priority prior to data exposure.

---

## 5. Formal Verdict

Because temporal priority cannot be mathematically proven for an atomic co-commitment, and because the model structure was modified to introduce a bending mode factor:

$$\mathbf{PRE\_REGISTRATION = UNVERIFIED}$$
