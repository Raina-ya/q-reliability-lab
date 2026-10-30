import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from src.phase_error_blind_spot import sweep, write_csv, write_figures


REQUIRED_COLUMNS = {
    "p",
    "success_probability",
    "x_basis_success_probability",
}
TEST_TEMPORARY_DIRECTORY = Path(__file__).parents[1] / ".pytest-tmp"


def test_basis_success_comparison_figure_is_generated_from_the_sweep_pipeline():
    TEST_TEMPORARY_DIRECTORY.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=TEST_TEMPORARY_DIRECTORY) as directory:
        output_directory = Path(directory)
        csv_path = output_directory / "phase_error_sweep.csv"

        rows = sweep()
        write_csv(rows, csv_path)
        write_figures(rows, output_directory)

        with csv_path.open(newline="", encoding="utf-8") as stream:
            columns = set(csv.DictReader(stream).fieldnames or [])

        figure_path = output_directory / "basis_success_comparison.png"
        assert REQUIRED_COLUMNS <= columns
        assert figure_path.is_file()
        assert figure_path.stat().st_size > 0
