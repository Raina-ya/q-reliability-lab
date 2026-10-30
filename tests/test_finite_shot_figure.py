import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from src.finite_shot_figures import read_finite_shot_rows, write_finite_shot_detectability_figure


CSV_PATH = Path(__file__).parents[1] / "experiments" / "finite_shot_sweep.csv"
REQUIRED_COLUMNS = {
    "p",
    "basis",
    "shots",
    "observed_success_probability",
    "analytic_success_probability",
    "wilson_lower",
    "wilson_upper",
}
TEST_TEMPORARY_DIRECTORY = Path(__file__).parents[1] / ".pytest-tmp"


def test_finite_shot_figure_is_generated_from_the_committed_csv():
    with CSV_PATH.open(newline="", encoding="utf-8") as stream:
        columns = set(csv.DictReader(stream).fieldnames or [])

    TEST_TEMPORARY_DIRECTORY.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=TEST_TEMPORARY_DIRECTORY) as directory:
        output_path = Path(directory) / "finite_shot_detectability.png"
        write_finite_shot_detectability_figure(read_finite_shot_rows(CSV_PATH), output_path)

        assert REQUIRED_COLUMNS <= columns
        assert output_path.is_file()
        assert output_path.stat().st_size > 0
