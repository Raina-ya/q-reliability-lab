import numpy as np
import pytest

from src.phase_error_blind_spot import (
    MINUS_MINUS,
    PLUS_PLUS,
    RHO_PHI_PLUS,
    X_BASIS_CORRELATED_PROJECTOR,
    apply_phase_flip,
    basis_success_probability,
    x_basis_correlated_success_probability,
)


@pytest.mark.parametrize("probability", [0.0, 0.5, 1.0])
def test_x_basis_success_matches_analytic_endpoints(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, probability)

    assert np.isclose(x_basis_correlated_success_probability(rho), 1.0 - probability, atol=1e-12)


@pytest.mark.parametrize("probability", np.linspace(0.0, 1.0, 101))
def test_x_basis_projector_calculation_matches_analytic_sweep(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, float(probability))
    direct_projector_value = np.trace(X_BASIS_CORRELATED_PROJECTOR @ rho)

    assert np.isclose(x_basis_correlated_success_probability(rho), direct_projector_value.real, atol=1e-12)
    assert np.isclose(x_basis_correlated_success_probability(rho), 1.0 - probability, atol=1e-12)
    assert np.isclose(basis_success_probability(rho), 1.0, atol=1e-12)


def test_x_basis_correlated_projector_is_constructed_from_correlated_outcomes():
    expected = np.outer(PLUS_PLUS, PLUS_PLUS.conj()) + np.outer(MINUS_MINUS, MINUS_MINUS.conj())

    assert np.allclose(X_BASIS_CORRELATED_PROJECTOR, expected, atol=1e-12)
    assert np.allclose(
        X_BASIS_CORRELATED_PROJECTOR @ X_BASIS_CORRELATED_PROJECTOR,
        X_BASIS_CORRELATED_PROJECTOR,
        atol=1e-12,
    )
