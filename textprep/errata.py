"""Parse errata documents."""

from textprep.splitter import parse_markdown

EXCLUDED_SECTIONS = ["Updated Packages"]

if __name__ == "__main__":
    with open("tests/example_docs/RHSA-2022_0886.md") as f:
        errata_doc = parse_markdown(f.read())

    for section in errata_doc["content"]:
        print(section.metadata)
        print(section.page_content)
        print()
