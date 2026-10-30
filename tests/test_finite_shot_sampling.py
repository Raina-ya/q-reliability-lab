import math

import pytest

from src.finite_shot_phase_error import sample_success_counts


def test_finite_shot_counts_are_conserved():
    result = sample_success_counts(probability=0.3, basis="X", shots=100, seed=17)

    assert result.success_count >= 0
    assert result.failure_count >= 0
    assert result.success_count + result.failure_count == result.shots
    assert result.observed_success_probability == result.success_count / result.shots


def test_finite_shot_sampling_is_reproducible_from_an_explicit_seed():
    first = sample_success_counts(probability=0.3, basis="X", shots=100, seed=20261030)
    second = sample_success_counts(probability=0.3, basis="X", shots=100, seed=20261030)

    assert first == second


def test_different_explicit_seeds_produce_different_intermediate_x_basis_counts():
    first = sample_success_counts(probability=0.3, basis="X", shots=100_000, seed=1)
    second = sample_success_counts(probability=0.3, basis="X", shots=100_000, seed=2)

    assert first.success_count != second.success_count


@pytest.mark.parametrize(
    ("probability", "basis", "expected_success_count"),
    [
        (0.0, "Z", 64),
        (1.0, "Z", 64),
        (0.0, "X", 64),
        (1.0, "X", 0),
    ],
)
def test_finite_shot_endpoint_behavior(probability, basis, expected_success_count):
    result = sample_success_counts(probability=probability, basis=basis, shots=64, seed=11)

    assert result.success_count == expected_success_count


def test_large_shot_x_basis_estimate_converges_to_the_analytic_probability():
    probability = 0.3
    shots = 100_000
    result = sample_success_counts(probability=probability, basis="X", shots=shots, seed=20261030)
    five_standard_errors = 5 * math.sqrt((1 - probability) * probability / shots)

    assert result.analytic_success_probability == pytest.approx(1 - probability)
    assert abs(result.observed_success_probability - result.analytic_success_probability) <= five_standard_errors


@pytest.mark.parametrize("basis", ["Z", "X"])
def test_observed_estimators_are_bounded(basis):
    result = sample_success_counts(probability=0.3, basis=basis, shots=100, seed=7)

    assert 0.0 <= result.observed_success_probability <= 1.0


@pytest.mark.parametrize(
    ("probability", "basis", "shots", "seed"),
    [
        (-0.1, "X", 10, 1),
        (1.1, "X", 10, 1),
        (0.3, "Y", 10, 1),
        (0.3, "X", 0, 1),
        (0.3, "X", 10, -1),
    ],
)
def test_invalid_sampling_inputs_are_rejected(probability, basis, shots, seed):
    with pytest.raises(ValueError):
        sample_success_counts(probability=probability, basis=basis, shots=shots, seed=seed)
