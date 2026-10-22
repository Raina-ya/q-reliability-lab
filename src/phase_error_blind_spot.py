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

import numpy as np


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
    """Render figures with Matplotlib, with a Pillow fallback for offline QA.

    Matplotlib is the declared project dependency and normal rendering path.
    The fallback keeps the experiment reproducible in restricted build
    environments where optional packages cannot be downloaded.
    """
    directory.mkdir(parents=True, exist_ok=True)
    p = np.array([row["p"] for row in rows])

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        _write_figures_with_pillow(rows, directory)
        return

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


def _write_figures_with_pillow(rows: list[dict[str, float]], directory: Path) -> None:
    """Restricted-environment fallback; normal users render with Matplotlib."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1296, 792
    margin = {"left": 110, "right": 45, "top": 55, "bottom": 95}
    colors = [(31, 119, 180), (214, 39, 40)]
    font = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=18)

    def render(filename: str, title: str, ylabel: str, series, y_min: float, y_max: float) -> None:
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        x0, y0 = margin["left"], height - margin["bottom"]
        x1, y1 = width - margin["right"], margin["top"]
        draw.line((x0, y0, x1, y0), fill="black", width=3)
        draw.line((x0, y0, x0, y1), fill="black", width=3)

        for tick in range(6):
            x = x0 + (x1 - x0) * tick / 5
            value = tick / 5
            draw.line((x, y0, x, y0 + 8), fill="black", width=2)
            draw.text((x - 18, y0 + 15), f"{value:.1f}", fill="black", font=small)
        for tick in range(5):
            value = y_min + (y_max - y_min) * tick / 4
            y = y0 - (y0 - y1) * tick / 4
            draw.line((x0 - 8, y, x0, y), fill="black", width=2)
            draw.line((x0, y, x1, y), fill=(225, 225, 225), width=1)
            draw.text((15, y - 10), f"{value:.2f}", fill="black", font=small)

        for index, (label, values) in enumerate(series):
            points = []
            for row, value in zip(rows, values):
                x = x0 + (x1 - x0) * row["p"]
                y = y0 - (y0 - y1) * (value - y_min) / (y_max - y_min)
                points.append((int(round(x)), int(round(y))))
            draw.line(points, fill=colors[index], width=5)
            legend_y = y1 + 15 + index * 30
            draw.line((x1 - 390, legend_y + 10, x1 - 340, legend_y + 10), fill=colors[index], width=5)
            draw.text((x1 - 325, legend_y), label, fill="black", font=small)

        draw.text((width // 2 - 235, 12), title, fill="black", font=font)
        draw.text((width // 2 - 110, height - 42), "Phase-flip probability p", fill="black", font=small)
        draw.text((12, 18), ylabel, fill="black", font=small)
        image.save(directory / filename)

    render(
        "success_vs_fidelity.png",
        "Task success is blind to the phase error",
        "Metric value",
        [
            ("P(00) + P(11)", [row["success_probability"] for row in rows]),
            ("Fidelity to Phi+", [row["fidelity"] for row in rows]),
        ],
        0.0,
        1.0,
    )
    render(
        "coherence_real_vs_magnitude.png",
        "Signed coherence reveals the phase reversal",
        "Coherence",
        [
            ("Re(rho[00,11])", [row["coherence_real"] for row in rows]),
            ("|rho[00,11]|", [row["coherence_magnitude"] for row in rows]),
        ],
        -0.5,
        0.5,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/phase_error_sweep.csv"))
    parser.add_argument("--figures", type=Path, default=Path("paper/figures"))
    args = parser.parse_args()

    rows = sweep()
    write_csv(rows, args.output)
    write_figures(rows, args.figures)
    print(f"Wrote {len(rows)} rows to {args.output} and two figures to {args.figures}")


if __name__ == "__main__":
    main()
