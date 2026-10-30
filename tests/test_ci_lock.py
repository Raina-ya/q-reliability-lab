from pathlib import Path


def test_ci_lock_pins_the_runtime_and_quality_tool_versions():
    locked = {
        line.split("==", maxsplit=1)[0]: line.split("==", maxsplit=1)[1]
        for line in Path("requirements-ci.txt").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }

    assert locked["numpy"] == "2.5.4"
    assert locked["matplotlib"] == "3.11.2"
    assert locked["pytest"] == "8.4.2"
    assert locked["ruff"] == "0.9.10"
