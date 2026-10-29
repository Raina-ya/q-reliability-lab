import numpy as np
import pytest

from src.phase_error_blind_spot import (
    RHO_PHI_PLUS,
    apply_phase_flip,
    basis_success_probability,
    fidelity_to_phi_plus,
    metrics,
)


@pytest.mark.parametrize("probability", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_phase_flip_output_matches_hand_derived_density_matrix(probability):
    expected = np.zeros((4, 4), dtype=np.complex128)
    expected[0, 0] = expected[3, 3] = 0.5
    expected[0, 3] = expected[3, 0] = (1.0 - 2.0 * probability) / 2.0

    assert np.allclose(apply_phase_flip(RHO_PHI_PLUS, probability), expected, atol=1e-12)


@pytest.mark.parametrize("probability", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_metrics_match_hand_derived_phase_flip_relations(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, probability)
    result = metrics(probability)
    expected_coherence = (1.0 - 2.0 * probability) / 2.0

    assert np.isclose(basis_success_probability(rho), 1.0, atol=1e-12)
    assert np.isclose(fidelity_to_phi_plus(rho), 1.0 - probability, atol=1e-12)
    assert np.isclose(np.real(rho[0, 3]), expected_coherence, atol=1e-12)
    assert np.isclose(np.abs(rho[0, 3]), abs(expected_coherence), atol=1e-12)
    assert result == pytest.approx(
        {
            "p": probability,
            "success_probability": 1.0,
            "x_basis_success_probability": 1.0 - probability,
            "fidelity": 1.0 - probability,
            "coherence_real": expected_coherence,
            "coherence_magnitude": abs(expected_coherence),
        },
        abs=1e-12,
    )
