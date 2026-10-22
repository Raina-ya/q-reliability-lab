# Can task success hide loss of quantum-state fidelity?

## Research question

Can computational-basis success probability alone mistakenly judge a Bell-state circuit as successful after a phase-flip channel has changed or removed the state's quantum coherence?

## Hypothesis

Yes. A phase flip changes the relative phase between the `|00>` and `|11>` amplitudes but does not change their computational-basis populations. Therefore, `P(00) + P(11)` should remain one while fidelity to `|Phi+>` and the signed coherence element `Re(rho[00,11])` change with the phase-flip probability.

The coherence magnitude requires separate interpretation: it should decrease to zero at `p = 0.5` and return to `0.5` at `p = 1`, because the final state at `p = 1` is the coherent but orthogonal state `|Phi->`, not an incoherent mixture.

## Metrics

- Computational-basis success probability: `P(00) + P(11)`.
- Fidelity to the pure target: `<Phi+|rho|Phi+>`.
- Signed coherence: `Re(rho[00,11])`.
- Coherence magnitude: `|rho[00,11]|`.

## Falsification condition

The hypothesis would be false if the selected computational-basis success metric changed consistently with the phase-flip probability and therefore tracked the loss of fidelity or the sign change of the off-diagonal coherence.

This prediction is written before running the parameter sweep so that the numerical output tests a stated claim rather than supplying a post-hoc narrative.

