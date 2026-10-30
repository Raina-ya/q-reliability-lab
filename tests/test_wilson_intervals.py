import pytest

from src.finite_shot_phase_error import sample_success_counts, wilson_interval


def test_wilson_interval_matches_the_hand_checked_symmetric_case():
    interval = wilson_interval(success_count=5, shots=10)

    assert interval.lower == pytest.approx(0.236593090512564, abs=1e-12)
    assert interval.upper == pytest.approx(0.763406909487436, abs=1e-12)


@pytest.mark.parametrize(
    ("success_count", "shots", "expected"),
    [
        (0, 10, (0.0, 0.277532799862889)),
        (10, 10, (0.722467200137111, 1.0)),
    ],
)
def test_wilson_interval_handles_binomial_endpoints(success_count, shots, expected):
    interval = wilson_interval(success_count=success_count, shots=shots)

    assert interval.lower == pytest.approx(expected[0], abs=1e-12)
    assert interval.upper == pytest.approx(expected[1], abs=1e-12)


@pytest.mark.parametrize("success_count", [0, 3, 10])
def test_wilson_interval_is_ordered_and_bounded(success_count):
    interval = wilson_interval(success_count=success_count, shots=10)

    assert 0.0 <= interval.lower <= interval.upper <= 1.0


def test_finite_shot_result_includes_its_wilson_interval():
    result = sample_success_counts(probability=0.3, basis="X", shots=100, seed=17)

    assert result.wilson_lower <= result.observed_success_probability <= result.wilson_upper
