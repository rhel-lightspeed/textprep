"""Split Markdown files into their parts based on their headers."""

import tomllib

from langchain_text_splitters import MarkdownHeaderTextSplitter


def parse_markdown(content: str) -> dict:
    """Get the markdown content into a state that can be be traversed easily."""
    frontmatter, content = content.split("\n+++\n", 1)

    # Remove the leading '+++' from the frontmatter.
    # The split above took care of the trailing '+++'.
    frontmatter = frontmatter.strip("+").strip()

    # Remove any leading dashes from the content.
    content = content.strip().strip("-").strip()

    return {"frontmatter": parse_frontmatter(frontmatter), "content": split_markdown_by_headers(content)}


def parse_frontmatter(frontmatter: str) -> dict:
    """Parse the frontmatter in each document."""
    return tomllib.loads(frontmatter)


def split_markdown_by_headers(content: str) -> list:
    headers_to_split_on = [
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
        ("####", "H4"),
        ("#####", "H5"),
        ("######", "H6"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    doc_splits = markdown_splitter.split_text(content)
    return list(doc_splits) if doc_splits else []
