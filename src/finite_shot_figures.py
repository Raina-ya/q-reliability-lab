"""Generate finite-shot phase-error figures from the committed sweep CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from src.finite_shot_phase_error import FINITE_SHOT_BUDGETS, VALID_BASES


REPRESENTATIVE_PROBABILITY = 0.5
REPRESENTATIVE_REPETITION = 0
MEAN_COMPARISON_SHOTS = 1_000


def read_finite_shot_rows(path: Path) -> list[dict[str, float | int | str]]:
    """Read the finite-shot CSV with numeric fields restored to numeric types."""
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "p": float(row["p"]),
                "basis": row["basis"],
                "shots": int(row["shots"]),
                "repetition": int(row["repetition"]),
                "seed": int(row["seed"]),
                "success_count": int(row["success_count"]),
                "failure_count": int(row["failure_count"]),
                "observed_success_probability": float(row["observed_success_probability"]),
                "analytic_success_probability": float(row["analytic_success_probability"]),
                "wilson_lower": float(row["wilson_lower"]),
                "wilson_upper": float(row["wilson_upper"]),
            }
            for row in csv.DictReader(stream)
        ]


def write_finite_shot_detectability_figure(rows: list[dict[str, float | int | str]], output: Path) -> None:
    """Plot finite-shot estimates, Wilson intervals, and analytic expectations."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"Z": "#1f77b4", "X": "#ff7f0e"}
    figure, (by_shots, by_probability) = plt.subplots(2, 1, figsize=(5.0, 6.4), constrained_layout=True)

    for basis in VALID_BASES:
        selected = [
            row
            for row in rows
            if row["p"] == REPRESENTATIVE_PROBABILITY
            and row["repetition"] == REPRESENTATIVE_REPETITION
            and row["basis"] == basis
        ]
        selected.sort(key=lambda row: int(row["shots"]))
        shots = np.array([int(row["shots"]) for row in selected])
        estimates = np.array([float(row["observed_success_probability"]) for row in selected])
        lower_errors = estimates - np.array([float(row["wilson_lower"]) for row in selected])
        upper_errors = np.array([float(row["wilson_upper"]) for row in selected]) - estimates
        analytic = float(selected[0]["analytic_success_probability"])
        by_shots.errorbar(
            shots,
            estimates,
            yerr=np.vstack((lower_errors, upper_errors)),
            color=colors[basis],
            marker="o",
            capsize=3,
            label=f"{basis}-basis observed",
        )
        by_shots.axhline(analytic, color=colors[basis], linestyle="--", linewidth=1.2)

    by_shots.set_xscale("log")
    by_shots.set_xticks(FINITE_SHOT_BUDGETS, [str(shots) for shots in FINITE_SHOT_BUDGETS])
    by_shots.set_ylim(-0.06, 1.06)
    by_shots.set_xlabel("Shots")
    by_shots.set_ylabel("Correlated-success estimate")
    by_shots.set_title("(a) p = 0.50; 95% Wilson intervals")
    by_shots.grid(alpha=0.25)
    by_shots.legend(loc="center right", fontsize=8)

    for basis in VALID_BASES:
        means = []
        standard_errors = []
        analytic = []
        for probability in sorted({float(row["p"]) for row in rows}):
            selected = [
                row
                for row in rows
                if row["p"] == probability and row["basis"] == basis and row["shots"] == MEAN_COMPARISON_SHOTS
            ]
            estimates = np.array([float(row["observed_success_probability"]) for row in selected])
            means.append(float(np.mean(estimates)))
            standard_errors.append(float(np.std(estimates, ddof=1) / np.sqrt(len(estimates))))
            analytic.append(float(selected[0]["analytic_success_probability"]))

        probabilities = sorted({float(row["p"]) for row in rows})
        by_probability.errorbar(
            probabilities,
            means,
            yerr=1.96 * np.array(standard_errors),
            color=colors[basis],
            marker="o",
            capsize=3,
            label=f"{basis}-basis empirical mean",
        )
        by_probability.plot(
            probabilities,
            analytic,
            color=colors[basis],
            linestyle="--",
            linewidth=1.2,
            label=f"{basis}-basis analytic",
        )

    by_probability.set_xlim(-0.04, 1.04)
    by_probability.set_ylim(-0.06, 1.06)
    by_probability.set_xlabel("Phase-flip probability p")
    by_probability.set_ylabel("Correlated-success probability")
    by_probability.set_title("(b) 1,000 shots; empirical means over 100 repetitions")
    by_probability.grid(alpha=0.25)
    by_probability.legend(loc="center right", fontsize=7)

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("experiments/finite_shot_sweep.csv"))
    parser.add_argument("--output", type=Path, default=Path("paper/figures/finite_shot_detectability.png"))
    args = parser.parse_args()

    rows = read_finite_shot_rows(args.input)
    write_finite_shot_detectability_figure(rows, args.output)
    print(f"Wrote finite-shot detectability figure to {args.output}")


if __name__ == "__main__":
    main()
