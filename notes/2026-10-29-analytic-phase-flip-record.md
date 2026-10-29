# Analytic phase-flip record

## Task 1: Bell state, channel, and metric cross-checks

The computational basis is ordered as `(00, 01, 10, 11)`.  Ideal Bell-state
preparation gives

\[
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}},
\qquad
\rho_+ = |\Phi^+\rangle\langle\Phi^+|
= \frac12
\begin{pmatrix}
1&0&0&1\\
0&0&0&0\\
0&0&0&0\\
1&0&0&1
\end{pmatrix}.
\]

For a phase flip on the first qubit, let `Z_1 = Z \otimes I` and use
`E_0 = sqrt(1-p) I_4`, `E_1 = sqrt(p) Z_1`.  The Kraus completeness relation
is

\[
E_0^\dagger E_0 + E_1^\dagger E_1
= (1-p)I_4 + p Z_1^\dagger Z_1 = I_4,
\]

because `Z_1^2 = I_4`.  Since `Z_1|\Phi^+\rangle=|\Phi^-\rangle`, the output
is

\[
\rho(p) = (1-p)|\Phi^+\rangle\langle\Phi^+|
+ p|\Phi^-\rangle\langle\Phi^-|
= \frac12
\begin{pmatrix}
1&0&0&1-2p\\
0&0&0&0\\
0&0&0&0\\
1-2p&0&0&1
\end{pmatrix}.
\]

Therefore the computational-basis success, target fidelity, and coherence
relations are

\[
S_Z(p)=\rho_{00,00}+\rho_{11,11}=1,
\quad F_{\Phi^+}(p)=1-p,
\quad \operatorname{Re}(\rho_{00,11})=\frac{1-2p}{2},
\quad |\rho_{00,11}|=\frac{|1-2p|}{2}.
\]

Parameterized regression tests evaluate these four relations at
`p = 0, 0.25, 0.5, 0.75, 1` directly from the density matrix returned by the
program.  The expected matrix is also checked at each point, so a broken
channel action or metric formula cannot be hidden by agreement between two
incorrect derived metrics.

At `p = 1`, the output is `|Phi-><Phi-|`.  Its populations remain `1/2` on
`00` and `11`, so `S_Z(1) = 1`.  Its relative phase is opposite to the target,
making it orthogonal to `|Phi+>` and hence `F_{Phi+}(1) = 0`.  Thus the
computational-basis metric accepts the same outcomes but does not test the
relative phase.

## Task 2: Physical-invariant sweep

The channel is tested over the dense grid `p = 0.00, 0.01, ..., 1.00`.
For every output, the test verifies a `(4, 4)` `complex128` matrix, unit
trace, Hermiticity, and positive semidefiniteness.  The expected nonzero
eigenvalues are `1-p` and `p`, so the smallest exact eigenvalue is zero at
the endpoints.  The positivity assertion permits only `-1e-12`, which is a
rounding allowance near this mathematical boundary, not a tolerance large
enough to conceal a physical violation.  The same `1e-12` absolute tolerance
is used for matrix equalities; the inputs use decimal fractions represented
in binary floating point and the operations contain square roots and matrix
products.

The sweep also verifies Kraus completeness at every grid point, bounds all
reported probabilities in `[0, 1]`, bounds coherence magnitude in `[0, 1/2]`,
and verifies the symmetry

\[
|\rho_{00,11}(p)|=|\rho_{00,11}(1-p)|.
\]

Inputs below zero and above one are rejected with `ValueError`; `NaN` is also
rejected because it does not define a physical channel probability.

## Task 3: X-basis correlated-success diagnostic

Define the one-qubit X-basis states as
`|+> = (|0> + |1>)/sqrt(2)` and `|-> = (|0> - |1>)/sqrt(2)`.  The
correlated-success projector is

\[
\Pi_X = |++\rangle\langle++| + |--\rangle\langle--|
= \frac12\begin{pmatrix}
1&0&0&1\\
0&1&1&0\\
0&1&1&0\\
1&0&0&1
\end{pmatrix}.
\]

The diagnostic is calculated from the projector, not from its analytic
formula:

\[
S_X(p) = \operatorname{Tr}(\Pi_X\rho(p))
= \frac12\left(\rho_{00,00}+\rho_{11,11}
+\rho_{00,11}+\rho_{11,00}\right) = 1-p.
\]

The code constructs `Pi_X` by outer products of the `|++>` and `|-->`
vectors, then evaluates `Tr(Pi_X rho)`.  Endpoint and dense-grid tests compare
that matrix computation to `1-p`; they also establish the contrast
`S_Z(p)=1` and `S_X(p)=1-p`.
