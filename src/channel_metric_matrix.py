"""Compare metric sensitivity for first-qubit Pauli noise channels."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from src.phase_error_blind_spot import (
    IDENTITY_2,
    IDENTITY_4,
    PHI_PLUS,
    RHO_PHI_PLUS,
    X_BASIS_CORRELATED_PROJECTOR,
    Z,
    basis_success_probability,
    fidelity_to_phi_plus,
    x_basis_correlated_success_probability,
)


X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
CHANNELS = ("bit_flip", "phase_flip", "depolarizing")
METRICS = (
    "z_basis_success_probability",
    "x_basis_success_probability",
    "fidelity",
    "coherence_real",
    "coherence_magnitude",
)
MATRIX_FIELDNAMES = (
    "channel",
    "metric",
    "value_at_p0",
    "value_at_p1",
    "maximum_absolute_change",
    "structurally_blind",
)


def kraus_operators(channel: str, probability: float) -> tuple[np.ndarray, ...]:
    """Return a conventional first-qubit bit, phase, or depolarizing channel."""
    _validate_channel(channel)
    _validate_probability(probability)
    if channel == "bit_flip":
        return (np.sqrt(1.0 - probability) * IDENTITY_4, np.sqrt(probability) * np.kron(X, IDENTITY_2))
    if channel == "phase_flip":
        return (np.sqrt(1.0 - probability) * IDENTITY_4, np.sqrt(probability) * np.kron(Z, IDENTITY_2))
    return (
        np.sqrt(1.0 - 3.0 * probability / 4.0) * IDENTITY_4,
        np.sqrt(probability / 4.0) * np.kron(X, IDENTITY_2),
        np.sqrt(probability / 4.0) * np.kron(Y, IDENTITY_2),
        np.sqrt(probability / 4.0) * np.kron(Z, IDENTITY_2),
    )


def apply_channel(rho: np.ndarray, channel: str, probability: float) -> np.ndarray:
    """Apply the selected Kraus channel to a density matrix."""
    return sum(operator @ rho @ operator.conj().T for operator in kraus_operators(channel, probability))


def metrics(channel: str, probability: float) -> dict[str, float]:
    """Evaluate the common metric set after the selected channel."""
    rho = apply_channel(RHO_PHI_PLUS, channel, probability)
    coherence = rho[0, 3]
    return {
        "z_basis_success_probability": basis_success_probability(rho),
        "x_basis_success_probability": x_basis_correlated_success_probability(rho),
        "fidelity": fidelity_to_phi_plus(rho),
        "coherence_real": float(np.real(coherence)),
        "coherence_magnitude": float(np.abs(coherence)),
    }


def analytic_metrics(channel: str, probability: float) -> dict[str, float]:
    """Independent closed forms used to test the channel implementation."""
    _validate_channel(channel)
    _validate_probability(probability)
    if channel == "bit_flip":
        return {
            "z_basis_success_probability": 1.0 - probability,
            "x_basis_success_probability": 1.0,
            "fidelity": 1.0 - probability,
            "coherence_real": (1.0 - probability) / 2.0,
            "coherence_magnitude": (1.0 - probability) / 2.0,
        }
    if channel == "phase_flip":
        return {
            "z_basis_success_probability": 1.0,
            "x_basis_success_probability": 1.0 - probability,
            "fidelity": 1.0 - probability,
            "coherence_real": (1.0 - 2.0 * probability) / 2.0,
            "coherence_magnitude": abs(1.0 - 2.0 * probability) / 2.0,
        }
    return {
        "z_basis_success_probability": 1.0 - probability / 2.0,
        "x_basis_success_probability": 1.0 - probability / 2.0,
        "fidelity": 1.0 - 3.0 * probability / 4.0,
        "coherence_real": (1.0 - probability) / 2.0,
        "coherence_magnitude": (1.0 - probability) / 2.0,
    }


def channel_metric_matrix() -> list[dict[str, float | str]]:
    """Summarize each metric's full [0, 1] response for every channel."""
    probabilities = np.linspace(0.0, 1.0, 101)
    rows: list[dict[str, float | str]] = []
    for channel in CHANNELS:
        values = [metrics(channel, float(probability)) for probability in probabilities]
        for metric in METRICS:
            series = np.array([row[metric] for row in values])
            rows.append(
                {
                    "channel": channel,
                    "metric": metric,
                    "value_at_p0": float(series[0]),
                    "value_at_p1": float(series[-1]),
                    "maximum_absolute_change": float(np.max(np.abs(series - series[0]))),
                    "structurally_blind": str(bool(np.allclose(series, series[0], atol=1e-12, rtol=0.0))).lower(),
                }
            )
    return rows


def write_channel_metric_matrix(rows: list[dict[str, float | str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MATRIX_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.10f}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def write_heatmap(rows: list[dict[str, float | str]], output: Path) -> None:
    """Render the matrix of maximum metric changes from the committed CSV data."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = np.array(
        [
            [float(next(row["maximum_absolute_change"] for row in rows if row["channel"] == channel and row["metric"] == metric)) for metric in METRICS]
            for channel in CHANNELS
        ]
    )
    figure, axis = plt.subplots(figsize=(7.0, 2.8), constrained_layout=True)
    image = axis.imshow(data, vmin=0.0, vmax=1.0, cmap="viridis")
    axis.set_xticks(range(len(METRICS)), ["Z success", "X success", "Fidelity", "Re(coherence)", "|coherence|"])
    axis.set_yticks(range(len(CHANNELS)), ["Bit flip", "Phase flip", "Depolarizing"])
    for row_index, channel in enumerate(CHANNELS):
        for column_index, metric in enumerate(METRICS):
            value = data[row_index, column_index]
            axis.text(column_index, row_index, f"{value:.2f}", ha="center", va="center", color="white" if value > 0.5 else "black")
    figure.colorbar(image, ax=axis, label="Maximum absolute change over p in [0, 1]")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)


def _validate_channel(channel: str) -> None:
    if channel not in CHANNELS:
        raise ValueError(f"channel must be one of {CHANNELS}")


def _validate_probability(probability: float) -> None:
    if not np.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/channel_metric_matrix.csv"))
    parser.add_argument("--figure", type=Path, default=Path("paper/figures/channel_metric_sensitivity_matrix.png"))
    args = parser.parse_args()
    rows = channel_metric_matrix()
    write_channel_metric_matrix(rows, args.output)
    write_heatmap(rows, args.figure)
    print(f"Wrote {len(rows)} channel-metric rows to {args.output} and heatmap to {args.figure}")


if __name__ == "__main__":
    main()
