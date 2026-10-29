import numpy as np
import pytest

from src.phase_error_blind_spot import (
    COMPLEX,
    IDENTITY_4,
    RHO_PHI_PLUS,
    apply_phase_flip,
    metrics,
    phase_flip_kraus,
)


PROBABILITIES = np.linspace(0.0, 1.0, 101)
ATOL = 1e-12


@pytest.mark.parametrize("probability", PROBABILITIES)
def test_channel_is_trace_preserving_and_outputs_a_physical_density_matrix(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, float(probability))

    assert rho.shape == (4, 4)
    assert rho.dtype == COMPLEX
    assert np.isclose(np.trace(rho), 1.0, atol=ATOL)
    assert np.allclose(rho, rho.conj().T, atol=ATOL)
    assert np.min(np.linalg.eigvalsh(rho)) >= -ATOL


@pytest.mark.parametrize("probability", PROBABILITIES)
def test_kraus_operators_are_complete_across_the_sweep(probability):
    operators = phase_flip_kraus(float(probability))
    completeness = sum(operator.conj().T @ operator for operator in operators)

    assert completeness.shape == (4, 4)
    assert completeness.dtype == COMPLEX
    assert np.allclose(completeness, IDENTITY_4, atol=ATOL)


@pytest.mark.parametrize("probability", PROBABILITIES)
def test_metric_bounds_hold_across_the_sweep(probability):
    result = metrics(float(probability))

    assert 0.0 <= result["success_probability"] <= 1.0
    assert 0.0 <= result["fidelity"] <= 1.0
    assert -0.5 <= result["coherence_real"] <= 0.5
    assert 0.0 <= result["coherence_magnitude"] <= 0.5


@pytest.mark.parametrize("probability", PROBABILITIES)
def test_coherence_magnitude_is_symmetric_about_half_phase_flip(probability):
    left = metrics(float(probability))["coherence_magnitude"]
    right = metrics(float(1.0 - probability))["coherence_magnitude"]

    assert np.isclose(left, right, atol=ATOL)


@pytest.mark.parametrize("probability", [-0.01, 1.01, float("nan")])
def test_channel_rejects_nonphysical_probabilities(probability):
    with pytest.raises(ValueError, match=r"probability must lie in \[0, 1\]"):
        phase_flip_kraus(probability)
