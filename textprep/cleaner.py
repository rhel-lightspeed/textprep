"""Clean up various parts of documents."""

import re


def clean_links(content: str) -> str:
    """Clean up links in the markdown content."""
    # Inline link pattern: [link text](URL)
    content = re.sub(r"\[([^\]]+)\]\((http[s]?:\/\/[^\)]+)\)", r"\1 (\2)", content)

    # Reference link pattern: [link text][ref]
    content = re.sub(r"\[([^\]]+)\]\[[^\]]+\]", r"\1", content)

    # Remove reference-style definitions: [ref]: URL
    content = re.sub(r"\n\s*\[[^\]]+\]:\s*(http[s]?:\/\/[^\s]+)", r" (\1)", content)

    return content.strip()


def remove_sections(sections: list, excluded_sections: list) -> list:
    """Remove sections from markdown documents."""
    return [x for x in sections if next(iter(x.metadata.values())) not in excluded_sections]
