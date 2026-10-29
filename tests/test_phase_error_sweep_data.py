import csv
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.phase_error_blind_spot import sweep, write_csv


FIELDNAMES = [
    "p",
    "success_probability",
    "x_basis_success_probability",
    "fidelity",
    "coherence_real",
    "coherence_magnitude",
]
CSV_PATH = Path(__file__).parents[1] / "experiments" / "phase_error_sweep.csv"
TEST_TEMPORARY_DIRECTORY = Path(__file__).parents[1] / ".pytest-tmp"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def test_committed_sweep_csv_has_expected_schema_and_row_count():
    with CSV_PATH.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    assert reader.fieldnames == FIELDNAMES
    assert len(rows) == 101


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (0, [0.0, 1.0, 1.0, 1.0, 0.5, 0.5]),
        (50, [0.5, 1.0, 0.5, 0.5, 0.0, 0.0]),
        (100, [1.0, 1.0, 0.0, 0.0, -0.5, 0.5]),
    ],
)
def test_committed_sweep_csv_matches_analytic_endpoint_and_midpoint_values(index, expected):
    row = read_rows(CSV_PATH)[index]
    values = [float(row[fieldname]) for fieldname in FIELDNAMES]

    assert values == pytest.approx(expected, abs=1e-10)


def test_csv_rebuild_is_deterministic():
    TEST_TEMPORARY_DIRECTORY.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=TEST_TEMPORARY_DIRECTORY) as directory:
        first = Path(directory) / "first.csv"
        second = Path(directory) / "second.csv"

        write_csv(sweep(), first)
        write_csv(sweep(), second)

        assert first.read_bytes() == second.read_bytes()
