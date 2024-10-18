"""Tests for cleaner functions."""

from textprep import cleaner


def test_clean_links():
    """Test cleaning up links."""
    content = """
Here is a [link](https://example.com) and here is another [reference link][1].

[1]: https://example.com/reference
"""
    result = cleaner.clean_links(content)
    assert result == (
        "Here is a link (https://example.com) and here is another reference link. (https://example.com/reference)"
    )
