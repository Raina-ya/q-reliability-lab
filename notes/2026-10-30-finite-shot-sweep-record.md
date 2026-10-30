# Finite-shot sweep record

The committed `experiments/finite_shot_sweep.csv` contains the pre-registered
3,000 rows generated with root seed `20261030`. No repetitions are filtered or
removed. The schema includes the per-row seed, observed count-derived estimate,
analytic expectation, and 95% Wilson confidence interval.

## Ten-row spot check

The following X-basis rows use repetition zero and are copied from the
generated CSV. They cover every error probability at both the smallest and
largest shot budgets.

| p | shots | seed | successes | failures | observed | analytic | 95% Wilson interval |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.00 | 100 | 20261130 | 100 | 0 | 1.0000 | 1.0000 | [0.9630, 1.0000] |
| 0.00 | 10,000 | 20261530 | 10,000 | 0 | 1.0000 | 1.0000 | [0.9996, 1.0000] |
| 0.25 | 100 | 20261730 | 72 | 28 | 0.7200 | 0.7500 | [0.6251, 0.7986] |
| 0.25 | 10,000 | 20262130 | 7,398 | 2,602 | 0.7398 | 0.7500 | [0.7311, 0.7483] |
| 0.50 | 100 | 20262330 | 49 | 51 | 0.4900 | 0.5000 | [0.3942, 0.5865] |
| 0.50 | 10,000 | 20262730 | 5,053 | 4,947 | 0.5053 | 0.5000 | [0.4955, 0.5151] |
| 0.75 | 100 | 20262930 | 19 | 81 | 0.1900 | 0.2500 | [0.1251, 0.2778] |
| 0.75 | 10,000 | 20263330 | 2,511 | 7,489 | 0.2511 | 0.2500 | [0.2427, 0.2597] |
| 1.00 | 100 | 20263530 | 0 | 100 | 0.0000 | 0.0000 | [0.0000, 0.0370] |
| 1.00 | 10,000 | 20263930 | 0 | 10,000 | 0.0000 | 0.0000 | [0.0000, 0.0004] |

The endpoint counts are exact as designed. At intermediate probabilities, the
10,000-shot observations are closer to the analytic value and their Wilson
intervals are narrower than their 100-shot counterparts, without removing the
less visually tidy 100-shot repetitions.
