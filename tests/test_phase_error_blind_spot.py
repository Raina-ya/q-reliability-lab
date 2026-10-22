import numpy as np
import pytest

from src.phase_error_blind_spot import (
    IDENTITY_4,
    PHI_MINUS,
    PHI_PLUS,
    RHO_PHI_PLUS,
    apply_phase_flip,
    basis_success_probability,
    fidelity_to_phi_plus,
    phase_flip_kraus,
)


@pytest.mark.parametrize("probability", [0.0, 0.2, 0.5, 1.0])
def test_kraus_completeness(probability):
    operators = phase_flip_kraus(probability)
    completeness = sum(operator.conj().T @ operator for operator in operators)
    assert np.allclose(completeness, IDENTITY_4)


@pytest.mark.parametrize("probability", [0.0, 0.13, 0.5, 0.87, 1.0])
def test_output_trace_is_one(probability):
    assert np.trace(apply_phase_flip(RHO_PHI_PLUS, probability)) == pytest.approx(1.0)


@pytest.mark.parametrize("probability", [0.0, 0.13, 0.5, 0.87, 1.0])
def test_output_is_hermitian(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, probability)
    assert np.allclose(rho, rho.conj().T)


@pytest.mark.parametrize("probability", [0.0, 0.13, 0.5, 0.87, 1.0])
def test_output_is_positive_semidefinite(probability):
    eigenvalues = np.linalg.eigvalsh(apply_phase_flip(RHO_PHI_PLUS, probability))
    assert np.min(eigenvalues) >= -1e-12


def test_zero_noise_matches_target_state():
    assert np.allclose(apply_phase_flip(RHO_PHI_PLUS, 0.0), RHO_PHI_PLUS)


def test_half_phase_flip_removes_off_diagonal_coherence():
    rho = apply_phase_flip(RHO_PHI_PLUS, 0.5)
    assert rho[0, 3] == pytest.approx(0.0)
    assert rho[3, 0] == pytest.approx(0.0)


@pytest.mark.parametrize("probability", np.linspace(0.0, 1.0, 11))
def test_basis_success_is_blind_to_phase_flip(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, float(probability))
    assert basis_success_probability(rho) == pytest.approx(1.0)


@pytest.mark.parametrize("probability", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_fidelity_changes_with_phase_flip(probability):
    rho = apply_phase_flip(RHO_PHI_PLUS, probability)
    assert fidelity_to_phi_plus(rho) == pytest.approx(1.0 - probability)


def test_full_phase_flip_produces_phi_minus():
    expected = np.outer(PHI_MINUS, PHI_MINUS.conj())
    assert np.allclose(apply_phase_flip(RHO_PHI_PLUS, 1.0), expected)
    assert np.vdot(PHI_PLUS, PHI_MINUS) == pytest.approx(0.0)

