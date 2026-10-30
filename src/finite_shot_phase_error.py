"""Finite-shot correlated-success sampling for the phase-flip experiment."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from numbers import Integral
from pathlib import Path
from statistics import NormalDist

import numpy as np


VALID_BASES = ("Z", "X")
FINITE_SHOT_PROBABILITIES = (0.0, 0.25, 0.5, 0.75, 1.0)
FINITE_SHOT_BUDGETS = (100, 1_000, 10_000)
FINITE_SHOT_REPETITIONS = 100
FINITE_SHOT_ROOT_SEED = 20261030
FINITE_SHOT_FIELDNAMES = (
    "p",
    "basis",
    "shots",
    "repetition",
    "seed",
    "success_count",
    "failure_count",
    "observed_success_probability",
    "analytic_success_probability",
    "wilson_lower",
    "wilson_upper",
)


@dataclass(frozen=True)
class FiniteShotResult:
    """One finite-shot correlated-success observation and its analytic expectation."""

    probability: float
    basis: str
    shots: int
    seed: int
    success_count: int
    failure_count: int
    observed_success_probability: float
    analytic_success_probability: float
    wilson_lower: float
    wilson_upper: float


@dataclass(frozen=True)
class WilsonInterval:
    """A bounded two-sided confidence interval for a binomial proportion."""

    lower: float
    upper: float
    confidence_level: float


def analytic_success_probability(probability: float, basis: str) -> float:
    """Return the correlated-success probability for the requested measurement basis."""
    _validate_probability(probability)
    _validate_basis(basis)
    return 1.0 if basis == "Z" else 1.0 - probability


def sample_success_counts(
    *, probability: float, basis: str, shots: int, seed: int
) -> FiniteShotResult:
    """Sample correlated-success counts with an explicitly supplied seed.

    The Z-basis accepted outcomes have total probability one for every phase
    flip rate. The X-basis accepted outcomes have total probability ``1 - p``.
    """
    _validate_probability(probability)
    _validate_basis(basis)
    _validate_shots(shots)
    _validate_seed(seed)

    analytic_probability = analytic_success_probability(probability, basis)
    rng = np.random.default_rng(seed)
    success_count = int(rng.binomial(shots, analytic_probability))
    failure_count = shots - success_count
    interval = wilson_interval(success_count=success_count, shots=shots)
    return FiniteShotResult(
        probability=probability,
        basis=basis,
        shots=shots,
        seed=seed,
        success_count=success_count,
        failure_count=failure_count,
        observed_success_probability=success_count / shots,
        analytic_success_probability=analytic_probability,
        wilson_lower=interval.lower,
        wilson_upper=interval.upper,
    )


def wilson_interval(
    *, success_count: int, shots: int, confidence_level: float = 0.95
) -> WilsonInterval:
    """Return a two-sided Wilson score interval for a binomial proportion."""
    _validate_shots(shots)
    if isinstance(success_count, bool) or not isinstance(success_count, Integral) or not 0 <= success_count <= shots:
        raise ValueError("success_count must be an integer in [0, shots]")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must lie in (0, 1)")

    estimate = success_count / shots
    z_score = NormalDist().inv_cdf((1.0 + confidence_level) / 2.0)
    z_squared = z_score**2
    denominator = 1.0 + z_squared / shots
    center = (estimate + z_squared / (2.0 * shots)) / denominator
    half_width = z_score * np.sqrt(
        estimate * (1.0 - estimate) / shots + z_squared / (4.0 * shots**2)
    ) / denominator
    lower = 0.0 if success_count == 0 else float(max(0.0, center - half_width))
    upper = 1.0 if success_count == shots else float(min(1.0, center + half_width))
    return WilsonInterval(lower=lower, upper=upper, confidence_level=confidence_level)


def finite_shot_sweep(root_seed: int = FINITE_SHOT_ROOT_SEED) -> list[dict[str, float | int | str]]:
    """Run the pre-registered finite-shot grid with deterministic child seeds."""
    _validate_seed(root_seed)
    rows: list[dict[str, float | int | str]] = []
    child_index = 0
    for probability in FINITE_SHOT_PROBABILITIES:
        for shots in FINITE_SHOT_BUDGETS:
            for basis in VALID_BASES:
                for repetition in range(FINITE_SHOT_REPETITIONS):
                    seed = root_seed + child_index
                    result = sample_success_counts(
                        probability=probability,
                        basis=basis,
                        shots=shots,
                        seed=seed,
                    )
                    rows.append(
                        {
                            "p": probability,
                            "basis": basis,
                            "shots": shots,
                            "repetition": repetition,
                            "seed": seed,
                            "success_count": result.success_count,
                            "failure_count": result.failure_count,
                            "observed_success_probability": result.observed_success_probability,
                            "analytic_success_probability": result.analytic_success_probability,
                            "wilson_lower": result.wilson_lower,
                            "wilson_upper": result.wilson_upper,
                        }
                    )
                    child_index += 1
    return rows


def write_finite_shot_csv(rows: list[dict[str, float | int | str]], output: Path) -> None:
    """Write the finite-shot sweep with a stable schema and numeric precision."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FINITE_SHOT_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.10f}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/finite_shot_sweep.csv"))
    parser.add_argument("--root-seed", type=int, default=FINITE_SHOT_ROOT_SEED)
    args = parser.parse_args()

    rows = finite_shot_sweep(root_seed=args.root_seed)
    write_finite_shot_csv(rows, args.output)
    print(f"Wrote {len(rows)} finite-shot rows to {args.output} using root seed {args.root_seed}")


def _validate_probability(probability: float) -> None:
    if not np.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")


def _validate_basis(basis: str) -> None:
    if basis not in VALID_BASES:
        raise ValueError(f"basis must be one of {VALID_BASES}")


def _validate_shots(shots: int) -> None:
    if isinstance(shots, bool) or not isinstance(shots, Integral) or shots <= 0:
        raise ValueError("shots must be a positive integer")


def _validate_seed(seed: int) -> None:
    if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
        raise ValueError("seed must be a non-negative integer")


if __name__ == "__main__":
    main()
