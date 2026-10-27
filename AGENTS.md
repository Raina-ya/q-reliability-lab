# Q-Reliability Lab Instructions

## Scope

- Research question: Can computational-basis success probability alone incorrectly classify a phase-corrupted Bell-state circuit as successful?
- Scope the study to an ideal Bell state followed by a phase-flip channel on the first qubit. Do not imply results for a particular device or physical CNOT implementation.

## Repository Contract

- Keep implementation in `src/`, tests in `tests/`, generated CSV data in `experiments/`, generated figures in `paper/figures/`, research logs in `notes/`, and report sources and PDF in `paper/`.
- Treat `experiments/phase_error_sweep.csv` and figures under `paper/figures/` as generated artifacts of `src.phase_error_blind_spot`.
- Keep CSV values, numerical claims, LaTeX tables, plotted curves, and figure captions mutually consistent. Regenerate artifacts after changing equations or metrics.

## Metrics

- Computational-basis success: `S(p) = P(00) + P(11)`.
- Target-state fidelity: `F(p) = <Phi+|rho(p)|Phi+>`.
- Signed coherence: `Re(rho[00,11])`.
- Coherence magnitude: `|rho[00,11]|`.
- Preserve the distinction between signed coherence and coherence magnitude; it is part of the research result.

## Verification and Reproduction

- Tests must encode the research insight and analytic invariants, including the metric blind spot and endpoint behavior, rather than merely checking imports or syntax.
- From the repository root, regenerate and test with:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest
  .\.venv\Scripts\python.exe -m src.phase_error_blind_spot `
    --output experiments/phase_error_sweep.csv `
    --figures paper/figures
  ```

- From `paper/`, reproduce the PDF with:

  ```powershell
  pdflatex main.tex
  bibtex main
  pdflatex main.tex
  pdflatex main.tex
  ```

## Project-Specific Limitations

- This is deterministic classical simulation, not hardware data.
- The phase-flip channel is a simplified analytic model applied after ideal Bell-state preparation.
- SPAM error, crosstalk, coherent calibration error, finite-shot uncertainty, and drift are outside scope.
- Noise is not assigned to a specific time or gate location inside a physical CNOT implementation.
- Do not claim a CNOT error rate or device performance for IBM hardware or any other real device.
- Fidelity to one target and coherence magnitude are incomplete metrics; state what each metric can and cannot detect.
