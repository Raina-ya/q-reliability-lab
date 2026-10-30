# Academic project presentation

`main.tex` is the Beamer source for the Q-Reliability Lab academic project presentation.

## Build

From this directory, run:

```sh
make pdf
```

The equivalent direct command is:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The build produces `main.pdf` in this directory. GitHub Actions compiles this deck with the same LaTeX action used for the paper.

## Figure provenance

The deck embeds committed experiment figures from `../paper/figures/`; it does not create decorative assets or manually redraw data.

| Figure | Generator | Data source |
| --- | --- | --- |
| `success_vs_fidelity.png` and `coherence_real_vs_magnitude.png` | `python -m src.phase_error_blind_spot` | `experiments/phase_error_sweep.csv` |
| `finite_shot_detectability.png` | `python -m src.finite_shot_figures` | `experiments/finite_shot_sweep.csv` |
| `channel_metric_sensitivity_matrix.png` | `python -m src.channel_metric_matrix` | `experiments/channel_metric_matrix.csv` |

The display tables reproduce values from the listed committed CSV files. The title uses the author name in `CITATION.cff`: Zhen-Jun Liu.
