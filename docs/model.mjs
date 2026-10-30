/** Exact phase-flip Bell-state model mirrored by src/phase_error_blind_spot.py. */
export function phaseFlipMetrics(probability) {
  if (!Number.isFinite(probability) || probability < 0 || probability > 1) {
    throw new RangeError("probability must lie in [0, 1]");
  }
  const coherence = (1 - 2 * probability) / 2;
  return {
    probability,
    zBasisSuccess: 1,
    xBasisSuccess: 1 - probability,
    fidelity: 1 - probability,
    coherence,
    coherenceMagnitude: Math.abs(coherence),
    densityMatrix: [
      [0.5, 0, 0, coherence],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [coherence, 0, 0, 0.5],
    ],
  };
}
