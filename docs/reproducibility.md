# Reproducibility contract

GitHub Actions installs exact Python package versions from
`requirements-ci.txt`. The human-facing dependency ranges remain in
`pyproject.toml`; the lock prevents NumPy and Matplotlib minor releases from
silently changing CI results.

The deterministic phase-error CSV, finite-shot CSV, and generated LaTeX table
are byte-compared in CI. CSV writers explicitly use LF line endings so that the
comparison is cross-platform. Figures are rendered from those committed CSV
values by the committed plotting scripts. They are tested for successful
regeneration from the data, but are not byte-compared because raster metadata,
font rendering, and image encoders can vary across operating systems. The
numeric tolerance for all analytic and CSV comparisons is the test-specific
`numpy.testing` tolerance; the generated CSV itself must be byte-identical.
