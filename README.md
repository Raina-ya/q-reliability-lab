# Q-Reliability Lab

Q-Reliability Lab is a reproducible study of a narrow benchmarking question: **can computational-basis success probability mistakenly judge a Bell-state circuit as successful after a phase error has changed or removed its quantum coherence?**

This first version was developed as an AI-assisted study artifact. Its scope, derivations, code, tests, and limitations are intentionally exposed for review rather than presented as independent hardware research.

## Why this matters

For the Bell target

\[
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt{2}},
\]

the task metric `P(00) + P(11)` observes only computational-basis populations. A phase error can preserve those populations while changing the relative phase that distinguishes `|Phi+>` from `|Phi->` or from an incoherent mixture. A benchmark based on the task metric alone can therefore report perfect success for the wrong quantum state.

## Noise model and metrics

The simulation applies a phase-flip channel to the first qubit after Bell-state preparation:

\[
\mathcal{E}_p(\rho)=(1-p)\rho+p(Z\otimes I)\rho(Z\otimes I).
\]

For `p = 0, 0.01, ..., 1`, it records:

- computational-basis success `P(00) + P(11)`;
- pure-target fidelity `<Phi+|rho|Phi+>`;
- `Re(rho[00,11])`;
- `|rho[00,11]|`.

![Success probability remains one while fidelity falls linearly.](figures/success_vs_fidelity.png)

The complete derivation and result table are in [the report](paper/main.pdf). The pre-execution hypothesis is preserved in [the research log](notes/2026-10-22-metric-blind-spot.md).

## Reproduce

Python 3.10 or newer is required.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m src.phase_error_blind_spot --output experiments/phase_error_sweep.csv --figures figures
```

The final command deterministically regenerates the 101-row CSV and both PNG figures. There is no Monte Carlo sampling in this version.

## Current limitations

- This is an analytic density-matrix calculation and deterministic simulation, not hardware data.
- The phase-flip channel is a simplified model.
- SPAM error, crosstalk, coherent calibration error, finite-shot uncertainty, and device drift are not included.
- The error is applied after ideal Bell-state preparation, not at a specified pulse or time location inside a physical CNOT implementation.
- No claim is made about the actual CNOT error rate of an IBM or any other quantum device.
- The study identifies one metric blind spot; it is not randomized benchmarking or complete CNOT characterization.

## License

MIT

