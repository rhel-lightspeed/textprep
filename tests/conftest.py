"""Pytest's configuration file."""

import pytest

EXAMPLE_DOCS_DIR = "tests/example_docs"
EXAMPLE_DOCS = {
    "errata": "RHSA-2022_0886.md",
}


def load_example_doc(doctype: str):
    """Load an example document."""
    with open(f"{EXAMPLE_DOCS_DIR}/{EXAMPLE_DOCS[doctype]}") as f:
        return f.read()


@pytest.fixture
def errata_doc():
    """Load an example errata document."""
    return load_example_doc("errata")


@pytest.fixture
def errata_doc_path():
    """Load an example errata document path."""
    return f"{EXAMPLE_DOCS_DIR}/{EXAMPLE_DOCS["errata"]}"
