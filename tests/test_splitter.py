"""Test the splitter functions."""

from unittest import mock

from langchain_core.documents import Document

from textprep import splitter


def test_parse_frontmatter():
    """Test parsing frontmatter."""
    frontmatter = """
key1 = "quoted value"
key2 = 'single quoted value'
key3 = '''triple quoted value'''
key4 = ["listitem1", "listitem2"]
"""
    result = splitter.parse_frontmatter(frontmatter)
    assert isinstance(result, dict)
    assert len(result) == 4
    assert result == {
        "key1": "quoted value",
        "key2": "single quoted value",
        "key3": "triple quoted value",
        "key4": ["listitem1", "listitem2"],
    }


@mock.patch("textprep.splitter.parse_frontmatter", return_value={"key": "value"})
def test_parse_markdown(mock_parse_frontmatter):
    """Test parsing markdown content."""
    content = """+++
key = value
+++

## Markdown header
First.

Second.
"""
    result = splitter.parse_markdown(content)
    assert isinstance(result, dict)
    assert len(result) == 2
    assert result["frontmatter"] == {"key": "value"}
    assert result["content"][0].metadata["Header 2"] == "Markdown header"
    assert result["content"][0].page_content == "First.\n\nSecond."


def test_split_markdown_by_headers_failure():
    """Test a document without content."""
    result = splitter.split_markdown_by_headers("")
    assert result == []


def test_parse_markdown_functional(errata_doc):
    """Test parsing full markdown document."""
    result = splitter.parse_markdown(errata_doc)
    assert isinstance(result, dict)
    assert len(result) == 2
    assert "security update" in result["frontmatter"]["title"]
    assert "Synopsis" in result["content"][0].metadata["Header 2"]
    assert "Moderate" in result["content"][0].page_content


def test_remove_empty_sections():
    """Test removing empty sections."""
    sections = [
        Document(metadata={"Header 1": "header"}, page_content="Valid data"),
        Document(metadata={"Header 2": "header"}, page_content="(none)"),
    ]
    result = splitter.remove_empty_sections(sections)
    assert len(result) == 1
