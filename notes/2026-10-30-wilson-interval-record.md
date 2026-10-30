# Wilson interval record

For `K` correlated successes in `N` shots, let `p_hat = K/N` and use the
two-sided 95% normal quantile `z = 1.959963984540054`. The Wilson score
interval is

```math
\frac{\widehat p + z^2/(2N)}{1+z^2/N}
\mathbin{\pm}
\frac{z}{1+z^2/N}
\sqrt{\frac{\widehat p(1-\widehat p)}{N}+\frac{z^2}{4N^2}}.
```

Wilson intervals are used instead of the naive normal interval
`p_hat +/- z sqrt(p_hat(1-p_hat)/N)`. At zero or all successes the latter has
zero width before clipping, while the Wilson interval provides a finite,
bounded range that reflects finite sample size. This is a frequentist
confidence interval, not a posterior probability.

## Hand check

For `K=5`, `N=10`, `p_hat=0.5`, and `z^2=3.841458820694124`, the centre is

```math
\frac{0.5 + 3.841458820694124/20}{1 + 3.841458820694124/10}=0.5,
```

and the half-width is `0.263406909487436`, giving
`[0.236593090512564, 0.763406909487436]`. The unit test locks this numerical
case. The edge cases `K=0` and `K=N` are tested separately; all reported
endpoints are required to be in `[0,1]` with lower less than or equal to upper.
The implementation clamps only floating-point roundoff at these mathematical
boundaries to `[0,1]`; it does not widen the interval or relax any test.
