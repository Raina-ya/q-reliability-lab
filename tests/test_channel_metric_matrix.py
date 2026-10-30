import csv
from pathlib import Path

import numpy as np
import pytest

from src.channel_metric_matrix import (
    CHANNELS,
    MATRIX_FIELDNAMES,
    analytic_metrics,
    apply_channel,
    channel_metric_matrix,
    kraus_operators,
    metrics,
    write_channel_metric_matrix,
)
from src.phase_error_blind_spot import IDENTITY_4, RHO_PHI_PLUS


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("probability", np.linspace(0.0, 1.0, 21))
def test_kraus_channels_are_complete_and_output_physical_states(channel, probability):
    operators = kraus_operators(channel, float(probability))
    completeness = sum(operator.conj().T @ operator for operator in operators)
    rho = apply_channel(RHO_PHI_PLUS, channel, float(probability))

    np.testing.assert_allclose(completeness, IDENTITY_4, atol=1e-12)
    np.testing.assert_allclose(rho, rho.conj().T, atol=1e-12)
    np.testing.assert_allclose(np.trace(rho), 1.0, atol=1e-12)
    assert np.linalg.eigvalsh(rho).min() >= -1e-12


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("probability", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_computed_metrics_match_independent_analytic_limits(channel, probability):
    observed = metrics(channel, probability)
    expected = analytic_metrics(channel, probability)
    for metric, value in expected.items():
        np.testing.assert_allclose(observed[metric], value, atol=1e-12)


def test_blindness_claims_are_structural_over_the_full_parameter_range():
    probabilities = np.linspace(0.0, 1.0, 101)
    phase_z = [metrics("phase_flip", float(p))["z_basis_success_probability"] for p in probabilities]
    bit_x = [metrics("bit_flip", float(p))["x_basis_success_probability"] for p in probabilities]
    np.testing.assert_allclose(phase_z, 1.0, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(bit_x, 1.0, atol=1e-12, rtol=0.0)


def test_depolarizing_fidelity_reaches_the_one_quarter_floor():
    assert metrics("depolarizing", 1.0)["fidelity"] == pytest.approx(0.25)


def test_channel_metric_matrix_is_deterministic_and_has_expected_blind_entries(tmp_path):
    rows = channel_metric_matrix()
    output = tmp_path / "channel_metric_matrix.csv"
    write_channel_metric_matrix(rows, output)
    with output.open(newline="", encoding="utf-8") as stream:
        stored = list(csv.DictReader(stream))

    assert len(stored) == 15
    assert tuple(stored[0]) == MATRIX_FIELDNAMES
    assert next(row for row in stored if row["channel"] == "phase_flip" and row["metric"] == "z_basis_success_probability")["structurally_blind"] == "true"
    assert next(row for row in stored if row["channel"] == "bit_flip" and row["metric"] == "x_basis_success_probability")["structurally_blind"] == "true"
    assert Path("experiments/channel_metric_matrix.csv").read_bytes() == output.read_bytes()
