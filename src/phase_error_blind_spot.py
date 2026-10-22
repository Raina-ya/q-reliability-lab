"""Demonstrate a computational-basis metric's blindness to phase errors.

The script applies a phase-flip channel to the first qubit of |Phi+>, sweeps
the flip probability p from 0 to 1, and records task success, state fidelity,
and the |00><11| coherence element. It intentionally implements only the
objects needed for this experiment, rather than a general quantum simulator.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


COMPLEX = np.complex128
IDENTITY_2 = np.eye(2, dtype=COMPLEX)
Z = np.array([[1, 0], [0, -1]], dtype=COMPLEX)
IDENTITY_4 = np.eye(4, dtype=COMPLEX)
Z_ON_FIRST = np.kron(Z, IDENTITY_2)

PHI_PLUS = np.array([1, 0, 0, 1], dtype=COMPLEX) / np.sqrt(2)
PHI_MINUS = np.array([1, 0, 0, -1], dtype=COMPLEX) / np.sqrt(2)
RHO_PHI_PLUS = np.outer(PHI_PLUS, PHI_PLUS.conj())


def phase_flip_kraus(probability: float) -> tuple[np.ndarray, np.ndarray]:
    """Return the two-qubit Kraus operators for a Z flip on qubit one."""
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    return (
        np.sqrt(1.0 - probability) * IDENTITY_4,
        np.sqrt(probability) * Z_ON_FIRST,
    )


def apply_phase_flip(rho: np.ndarray, probability: float) -> np.ndarray:
    """Apply E_p(rho) = sum_k E_k rho E_k^dagger."""
    return sum(operator @ rho @ operator.conj().T for operator in phase_flip_kraus(probability))


def basis_success_probability(rho: np.ndarray) -> float:
    """Return P(00) + P(11) in the computational basis."""
    return float(np.real(rho[0, 0] + rho[3, 3]))


def fidelity_to_phi_plus(rho: np.ndarray) -> float:
    """Return <Phi+|rho|Phi+>, valid because the reference state is pure."""
    return float(np.real(PHI_PLUS.conj() @ rho @ PHI_PLUS))


def metrics(probability: float) -> dict[str, float]:
    """Evaluate all metrics for one phase-flip probability."""
    rho = apply_phase_flip(RHO_PHI_PLUS, probability)
    coherence = rho[0, 3]  # rho[00,11] in the ordered basis 00, 01, 10, 11
    return {
        "p": probability,
        "success_probability": basis_success_probability(rho),
        "fidelity": fidelity_to_phi_plus(rho),
        "coherence_real": float(np.real(coherence)),
        "coherence_magnitude": float(np.abs(coherence)),
    }


def sweep() -> list[dict[str, float]]:
    """Evaluate p = 0.00, 0.01, ..., 1.00 exactly once each."""
    return [metrics(step / 100) for step in range(101)]


def write_csv(rows: list[dict[str, float]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: f"{value:.10f}" for key, value in row.items()})


def write_figures(rows: list[dict[str, float]], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    p = np.array([row["p"] for row in rows])

    plt.figure(figsize=(7.2, 4.4))
    plt.plot(p, [row["success_probability"] for row in rows], label=r"$P(00)+P(11)$", linewidth=2.4)
    plt.plot(p, [row["fidelity"] for row in rows], label=r"$F(\rho,|\Phi^+\rangle)$", linewidth=2.4)
    plt.xlabel("Phase-flip probability p")
    plt.ylabel("Metric value")
    plt.ylim(-0.04, 1.04)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(directory / "success_vs_fidelity.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.4))
    plt.plot(p, [row["coherence_real"] for row in rows], label=r"$\mathrm{Re}(\rho_{00,11})$", linewidth=2.4)
    plt.plot(p, [row["coherence_magnitude"] for row in rows], label=r"$|\rho_{00,11}|$", linewidth=2.4)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xlabel("Phase-flip probability p")
    plt.ylabel("Coherence element")
    plt.ylim(-0.54, 0.54)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(directory / "coherence_real_vs_magnitude.png", dpi=180)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/phase_error_sweep.csv"))
    parser.add_argument("--figures", type=Path, default=Path("figures"))
    args = parser.parse_args()

    rows = sweep()
    write_csv(rows, args.output)
    write_figures(rows, args.figures)
    print(f"Wrote {len(rows)} rows to {args.output} and two figures to {args.figures}")


if __name__ == "__main__":
    main()

