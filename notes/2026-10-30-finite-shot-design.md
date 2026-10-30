# Finite-shot phase-error experiment design

## Question and fixed analysis plan

The deterministic density-matrix sweep gives exact probabilities. This follow-up
experiment asks what finite samples reveal when the same Bell state is measured
in either the computational (`Z`) or X basis.

For `N` shots, define a correlated-success count `K` and estimator
`K / N`. In the Z basis, `00` and `11` are both accepted and occur with
probability `1/2` each for every phase-flip probability `p`; the other two
outcomes have probability zero. Therefore `K_Z=N` and the estimator is one for
all `p`. Z-basis samples have the same distribution for every `p`, so they
cannot identify the phase-flip probability.

In the X basis, `++` and `--` are accepted. A `|Phi+>` component produces
these two outcomes with total probability one, while a `|Phi->` component
produces `+-` and `-+` with total probability one. Hence

```math
K_X sim \mathrm{Binomial}(N, 1-p),
\qquad
\widehat{S}_X=K_X/N,
\qquad
\mathbb{E}[\widehat{S}_X]=1-p.
```

The null interpretation is that the Z-basis success samples are compatible
with every `p` in this model. The alternative is that the X-basis estimator
changes with `p` and therefore carries phase-error information. This
interpretation is fixed before sampling.

## Pre-registered sweep

- `p`: `0.00, 0.25, 0.50, 0.75, 1.00`, spanning both endpoints and three
  intermediate error levels.
- `shots`: `100, 1_000, 10_000`, making the expected sampling standard error
  visibly scale with `1/sqrt(N)` while keeping the committed CSV compact.
- `repetitions`: `100` independent repetitions for every `(p, shots, basis)`
  condition; no repetitions are discarded.
- `basis`: `Z` and `X`.
- root seed: `20261030`; each row receives a deterministic child seed so the
  exact sweep can be reconstructed and audited.

The planned output has 3,000 rows:
`5 probabilities * 3 shot budgets * 100 repetitions * 2 bases`.

## CSV schema draft

The initial sampling CSV columns are, in order:

`p`, `basis`, `shots`, `repetition`, `seed`, `success_count`, `failure_count`,
`observed_success_probability`, `analytic_success_probability`.

`observed_success_probability` is always the finite-shot `success_count / shots`.
`analytic_success_probability` is stored separately and is never presented as
an observation. Task 6 will append Wilson interval endpoint columns.

## Test specification written before implementation

1. Counts must be nonnegative and sum exactly to `shots`.
2. Repeating the same `(p, basis, shots, seed)` must return the same result.
3. At `p=0` and `p=1`, Z-basis success remains exactly one; X-basis success
   is exactly one and zero, respectively.
4. For X basis at `p=0.30` with 100,000 shots, the observed estimate must lie
   within five binomial standard errors of `0.70`. The tolerance is
   `5 * sqrt(0.70 * 0.30 / 100000)`, about `0.00725`, which is a stated
   sampling bound rather than an arbitrary loose tolerance.
