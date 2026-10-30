import csv
import math
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from src.finite_shot_phase_error import (
    FINITE_SHOT_BUDGETS,
    FINITE_SHOT_FIELDNAMES,
    FINITE_SHOT_PROBABILITIES,
    FINITE_SHOT_REPETITIONS,
    VALID_BASES,
    finite_shot_sweep,
    write_finite_shot_csv,
)


CSV_PATH = Path(__file__).parents[1] / "experiments" / "finite_shot_sweep.csv"
TEST_TEMPORARY_DIRECTORY = Path(__file__).parents[1] / ".pytest-tmp"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def test_committed_finite_shot_csv_has_the_preregistered_schema_and_row_count():
    with CSV_PATH.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    expected_count = (
        len(FINITE_SHOT_PROBABILITIES)
        * len(FINITE_SHOT_BUDGETS)
        * FINITE_SHOT_REPETITIONS
        * len(VALID_BASES)
    )
    assert reader.fieldnames == list(FINITE_SHOT_FIELDNAMES)
    assert len(rows) == expected_count


def test_committed_finite_shot_csv_is_byte_reproducible_from_the_preregistered_seed():
    TEST_TEMPORARY_DIRECTORY.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=TEST_TEMPORARY_DIRECTORY) as directory:
        rebuilt_path = Path(directory) / "finite_shot_sweep.csv"
        write_finite_shot_csv(finite_shot_sweep(), rebuilt_path)

        assert rebuilt_path.read_bytes() == CSV_PATH.read_bytes()


def test_aggregate_finite_shot_estimates_converge_to_the_analytic_expectation():
    grouped_estimates: dict[tuple[float, int, str], list[float]] = defaultdict(list)
    for row in read_rows(CSV_PATH):
        grouped_estimates[(float(row["p"]), int(row["shots"]), row["basis"])].append(
            float(row["observed_success_probability"])
        )

    for (probability, shots, basis), estimates in grouped_estimates.items():
        expected = 1.0 if basis == "Z" else 1.0 - probability
        mean_estimate = sum(estimates) / len(estimates)
        if expected in (0.0, 1.0):
            assert mean_estimate == expected
        else:
            five_standard_errors = 5 * math.sqrt(
                expected * (1.0 - expected) / (shots * FINITE_SHOT_REPETITIONS)
            )
            assert abs(mean_estimate - expected) <= five_standard_errors
