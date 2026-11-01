# Foundation audit integration verification — 2026-11-01

Base: `5f51a531f7e69d6c3200fbf2ee04f2777053dc56` (fetched origin/main).
Working tree was clean; git apply --check passed before applying the supplied patch.
Reviewer: OpenAI Codex, model GPT-6 (session-provided identity); prepared audit
reviewer/model provenance was not supplied and is not invented. No Sol/Argon
review or independent empirical validation is claimed.

Reproducible task: apply the provided audit, inspect all registries/model/report,
independently derive dimensional balances, compare 45 CSV scenario rows, verify
13 original hashes, cross-check all 21 citations, run all three Python tools and
publish via checked PR. This is integration review, not a new experiment.

Patch SHA-256: `5ac6c78d6be524ced8cfb85a5dd50198acd20e2ac5ac945b8c76d15cd979a90b`.

## Adjudication

FND-0007/NEG-0003 are conditional mass-balance results. With Q in L blood/min
and deltaC in L oxygen/L blood, VO2 is L oxygen/min. Cv=Ca-deltaC must be >=0.
At assumed Ca=0.200, +30% requires deltaC=0.195, Cv=0.005 (97.5% extraction),
+50% requires 0.225 (Cv=-0.025), +100% requires 0.300 (Cv=-0.100).
Only the last two violate this assumed bound. Changing Q or Ca changes the
conclusion; feasible arithmetic does not establish cardiovascular feasibility.

Other dimensional checks: sigma [N/cm2] times PCSA [cm2] gives N; tendon cap
is dimensionless; mv2/2 [J] divided by time gives W; rho*CdA*v3/2 gives W
and its time average at constant acceleration is peak/4. Heat storage
m*c*deltaT/t is W (218.75 W here); efficiency is dimensionless. Milliseconds
are converted to seconds before multiplying speed. Square-grid spacing is
sqrt(2)*radius; (10 mm/spacing)^2 gives tracks/cm2, not perfusion capacity.

ISS-0006/ISS-0007 remain open; DEC-0005 reflects explicit public visibility,
verified via GitHub API. ISS-0001 is resolved by the existing durable remote.
Historical DEC-0004 is retained and superseded by DEC-0005 for visibility and
publication; it no longer describes the current workflow.

Corrections to supplied audit: clarify online versus issue dates, record the
observed SRC-0003 figure correction, narrow efficiency mismatch wording to
what abstract-level review supports, and distinguish historical report claims.
Strengthened verifier coverage for tendon flags, baseline VO2 and heat storage;
validator now enforces 21 IDs, one report row per source and 13 unique artifacts.
No imported scientific artifact was changed. Original observations and negative
results remain. See source audit for depth and retrieval limitations.

## Verification

All three Python commands PASS in existing .venv; git diff --check PASS.
7 CSV datasets exactly reproduced as parsed records; 45 rows independently
recomputed; 13 SHA-256 hashes match. GitHub workflow runs all three commands.
Environment: 3.12.10; numpy/matplotlib versions below.

contourpy==1.4.0
cycler==0.12.1
fonttools==4.68.0
kiwisolver==1.5.1
matplotlib==3.11.2
numpy==2.5.4
packaging==26.3
pillow==13.0.0
pyparsing==3.3.3
python-dateutil==4.0.0
tzdata==2026.6
