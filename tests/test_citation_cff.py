from pathlib import Path


def test_citation_cff_has_the_required_cff_scalar_and_author_structure():
    """Validate the simple CFF/YAML subset used by this metadata file offline."""
    lines = Path("CITATION.cff").read_text(encoding="utf-8").splitlines()
    scalars = {}
    author = {}
    in_authors = False
    for line in lines:
        if not line or line.startswith("#"):
            continue
        if line == "authors:":
            in_authors = True
            continue
        if in_authors and not line.startswith(" "):
            in_authors = False
        if in_authors and line.startswith("  - "):
            key, value = line[4:].split(": ", maxsplit=1)
            author[key] = value
            continue
        if in_authors and line.startswith("    "):
            key, value = line.strip().split(": ", maxsplit=1)
            author[key] = value
            continue
        if not line.startswith(" ") and ": " in line:
            key, value = line.split(": ", maxsplit=1)
            scalars[key] = value.strip('"')

    assert scalars["cff-version"] == "1.2.0"
    assert scalars["title"] == "Q-Reliability Lab"
    assert scalars["version"] == "0.1.0"
    assert scalars["license"] == "MIT"
    assert scalars["repository-code"] == "https://github.com/Raina-ya/q-reliability-lab"
    assert author == {"family-names": "Liu", "given-names": "Zhen-Jun"}
