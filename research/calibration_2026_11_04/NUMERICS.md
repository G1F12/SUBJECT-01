# Cross-platform negative numerical result

Linux CI runs41881845684 and41882497475 failed the original .001 comparison of
pulmonary optimizer diagnostics, while all physical parameters, endpoint metrics,
locks, classifications and profile support intervals met their existing tolerance.
Source and archived output hashes remained exact. The failures are retained in
GitHub Actions; original parameter_identification.json is not rewritten.

Diagnosis: the curve contains max(0,t−onset−delay), a sampled activation knee.
For participant17, delay16.99999983s places a sample within1.7e−7s of the knee;
for participant56, delay3.00000004s is within4.3e−8s. Finite differences at this
nondifferentiable point produce different delay derivatives on different platforms.
Example FIM(delay,delay): .15128→.09618 and .19734→1.52840. Both τ profiles
already include the lower bound1s and remain UNIDENTIFIABLE. These FIMs cannot
be interpreted as regular Gaussian precision matrices. Other near-knee fits also
retain this caveat even if their numerical derivative happens to reproduce.

Replay policy detects the mathematical knee from the actual time observations
and both fitted delays (distance<1e−4s), excludes only FIM/SVD derivative entries
there, and keeps parameters, local-rank labels, profile support and status checks.
Those local ranks remain archived numerical diagnostics, not proof of regularity.
Non-knee FIM/SVD retain .001 comparison. Dimensionless profile objective tolerance
is .01 (observed largest difference .005815), small relative to threshold3.84;
profile support/classification must still reproduce. Parameter tolerance remains
rtol/atol .001, below the native1s clock; all test metrics use tighter2e−6/2e−5.
The new regression test rejects a2s parameter alteration. This change neither
retunes a physiological model nor changes the published pre-test lock or test.
