# Red-team self-audit of the research claims

## A1. Is this trivial?

**Finding.** The central claim is that, for the specified Bell state and
first-qubit phase-flip channel, `P(00) + P(11)` remains one while
phase-sensitive quantities change. This is a known consequence of measuring
only computational-basis populations, not a new physical discovery.

**Evidence.** The state and metrics are derived in `paper/main.tex:48-185`.
The implementation directly evaluates a Kraus map and a projector
(`src/phase_error_blind_spot.py:35-76`). The distinction between populations
and coherences is standard quantum-information material, for which the report
cites Nielsen and Chuang (`paper/main.tex:59-67`). A phase flip maps `|Phi+>`
to `|Phi->`, leaving the computational-basis probabilities unchanged.

**Severity.** Major for wording; none for the mathematics.

**Remediation.** Abstract, Introduction, and Conclusion now call this a
reproducible quantitative demonstration/benchmark of a known limitation, not
a new noise model or hardware result. P2 adds a controlled channel comparison.

## A2. Physics correctness

**Finding.** The phase-flip definition, Kraus map, matrix elements, and
X-basis diagnostic are correct for a first-qubit Pauli-Z error.

**Evidence.** With `Z_1 = Z tensor I`, the Kraus operators are
`E_0 = sqrt(1-p) I_4` and `E_1 = sqrt(p) Z_1`; hence
`E_0^dagger E_0 + E_1^dagger E_1 = (1-p) I_4 + p Z_1^2 = I_4`.
For `|Phi+> = (|00> + |11>)/sqrt(2)`, `Z_1|Phi+> = |Phi->`, giving

```
rho(p) = 1/2 [[1, 0, 0, 1-2p],
              [0, 0, 0, 0],
              [0, 0, 0, 0],
              [1-2p, 0, 0, 1]].
```

Therefore `S_Z = rho_00,00 + rho_11,11 = 1`. The correlated X projector
`Pi_X = |++><++| + |--><--|` gives `S_X = 1-p`. Equations are in
`paper/main.tex:93-185`; code is at `src/phase_error_blind_spot.py:18-76`;
endpoints and dense grids are tested in `tests/test_phase_flip_analytics.py`
and `tests/test_x_basis_diagnostic.py`.

At `p=0`, the state is `|Phi+>`; at `p=1`, it is the orthogonal but equally
Z-correlated `|Phi->`; at `p=0.5`, it is the incoherent equal-population
mixture. `S_Z` is structurally independent of `p`, not numerically flat by
accident, because Z leaves both accepted diagonal populations unchanged.

**Severity.** None.

**Remediation.** P2 adds independent channel implementations and completeness
tests to compare this conclusion across a constrained channel set.

## A3. Metric definitions and limits

| Metric | Definition | Detects here | Blind or invariant here |
| --- | --- | --- | --- |
| Z correlated success | `S_Z = rho_00,00 + rho_11,11` | population outside `{00,11}` | relative phase between `|00>` and `|11>` |
| X correlated success | `S_X = Tr(Pi_X rho)` | specified phase flips | errors not represented by this binary projector |
| Target fidelity | `F = <Phi+|rho|Phi+>` | departure from this target | general process properties |
| Signed coherence | `Re(rho_00,11)` | sign reversal and coherence loss | populations and imaginary coherence |
| Coherence magnitude | `|rho_00,11|` | coherence loss at `p=0.5` | relative-phase sign |

**Evidence.** Definitions are in `paper/main.tex:158-187`, and metric code is
`src/phase_error_blind_spot.py:50-75`. Labels are accurate as long as
“success” means the explicitly defined correlated-success event rather than a
complete circuit-quality claim.

**Severity.** Minor.

**Remediation.** P2 preserves basis-qualified labels. P3 explicitly shows the
selected basis in the interactive lab.

## A4. Statistics and uncertainty

**Finding.** Wilson intervals are appropriate for these binomial proportions
because the design includes zero/all-success endpoints, where a normal interval
is poorly behaved. They are frequentist confidence intervals, not posteriors.

**Evidence.** The formula and endpoint behavior are in
`src/finite_shot_phase_error.py:99-119`; hand-checked and endpoint cases are
tested in `tests/test_wilson_intervals.py`. Every observation initializes a
fresh seeded RNG (`src/finite_shot_phase_error.py:80-84`), and the sweep gives
each row one deterministic child seed (`src/finite_shot_phase_error.py:122-154`).
The aggregate convergence check uses 100 repetitions at 1,000 shots and an
absolute tolerance of `0.02` (`tests/test_finite_shot_sweep_data.py:55-67`).
The worst-case standard error of that mean is about `sqrt(0.25/(100*1000)) =
0.00158`; `0.02` is a conservative regression tolerance, not an assertion of
experimental precision.

The figure illustrates structural Z-basis blindness and X-basis sampling; it
does not specify a hypothesis test, confidence-interval separation rule, or
minimum detectable effect.

**Severity.** Major for any stronger detectability claim; none for the interval
calculation.

**Remediation.** The paper avoids claiming statistical proof. P2 uses exact
deterministic channel-matrix differences rather than visual inference.

## A5. Scope and threats to validity

**Finding.** Strong objections are one input state, one post-circuit Pauli
channel, classical simulation, no SPAM/readout/crosstalk/drift, no specified
circuit location, and no prior-benchmark comparison. They are fatal to hardware
or general-certification claims, but clear limitations for this narrow model.

**Evidence.** Current paper limitations are explicit at `paper/main.tex:310-335`.
The README contradicts shipped code by saying finite-shot uncertainty is absent
(`README.md:120-126`) despite sampling and Wilson intervals in
`src/finite_shot_phase_error.py:67-119`.

**Severity.** Major documentation contradiction.

**Remediation.** P0 corrects README wording: finite-shot statistical uncertainty
is included, while hardware measurement mechanisms and SPAM are not. P2 expands
only the simulated channel set.

## A6. Reproducibility and traceability spot check

**Finding.** Pass for three checked claims.

| Paper number | Trace | Result |
| --- | --- | --- |
| `S_Z(0.50)=1` | `paper/main.tex:262`; `experiments/phase_error_sweep.csv` at `p=0.5000000000`; `python -m src.phase_error_blind_spot` | Pass |
| `S_X(0.50)=0.50` | `paper/main.tex:262`; same CSV row and generator | Pass |
| 3,000 finite-shot rows | `paper/main.tex:218-223`; `experiments/finite_shot_sweep.csv`; `python -m src.finite_shot_phase_error --root-seed 20261030` | Pass |

Byte-stable finite-shot regeneration and the deterministic 101-point sweep are
tested in `tests/test_finite_shot_sweep_data.py:42-53` and
`tests/test_phase_error_sweep_data.py:51-58`.

**Severity.** None for this spot check.

**Remediation.** P1c locks CI dependencies; P2 adds a matching matrix-data
regeneration check.

## Verdict

The honest claim is defensible when framed as a reproducible quantitative
benchmark of a known basis-dependent metric blind spot, including finite-shot
precision but not hardware behavior. The phase-flip derivation, implementation,
and stated finite-shot model are sound. Novelty wording and the README's
finite-shot limitation must change; the exact conclusion remains valid within
the declared Bell-state, Pauli-channel, and measurement definitions.
