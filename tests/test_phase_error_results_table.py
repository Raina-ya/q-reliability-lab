from pathlib import Path
from tempfile import TemporaryDirectory

from src.phase_error_blind_spot import sweep, write_csv, write_results_table_from_csv


TEST_TEMPORARY_DIRECTORY = Path(__file__).parents[1] / ".pytest-tmp"


def test_paper_results_table_is_generated_from_representative_csv_rows():
    TEST_TEMPORARY_DIRECTORY.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=TEST_TEMPORARY_DIRECTORY) as directory:
        output_directory = Path(directory)
        csv_path = output_directory / "phase_error_sweep.csv"
        table_path = output_directory / "phase_error_results_table.tex"

        write_csv(sweep(), csv_path)
        write_results_table_from_csv(csv_path, table_path)

        assert table_path.read_text(encoding="utf-8") == """\\begin{tabular}{@{}cccccc@{}}
\\toprule
$p$ & $S_Z(p)$ & $S_X(p)$ & $F(p)$ & $\\mathrm{Re}(\\rho_{00,11})$ & $|\\rho_{00,11}|$\\\\
\\midrule
0.00 & 1.00 & 1.00 & 1.00 & 0.50 & 0.50\\\\
0.25 & 1.00 & 0.75 & 0.75 & 0.25 & 0.25\\\\
0.50 & 1.00 & 0.50 & 0.50 & 0.00 & 0.00\\\\
0.75 & 1.00 & 0.25 & 0.25 & -0.25 & 0.25\\\\
1.00 & 1.00 & 0.00 & 0.00 & -0.50 & 0.50\\\\
\\bottomrule
\\end{tabular}
"""
