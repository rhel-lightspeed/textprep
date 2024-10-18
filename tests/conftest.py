"""Pytest's configuration file."""

import pytest


def load_example_doc(doctype: str):
    """Load an example document."""
    example_docs = {
        "errata": "RHSA-2022_0886.md",
    }
    with open(f"tests/example_docs/{example_docs[doctype]}") as f:
        return f.read()


@pytest.fixture
def errata_doc():
    """Load an example errata document."""
    return load_example_doc("errata")
