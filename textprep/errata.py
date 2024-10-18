"""Parse errata documents."""

import os
import re

from textprep.cleaner import clean_links
from textprep.splitter import parse_markdown


def load_errata(path: str) -> dict:
    """Load an errata document from a file."""
    if not os.path.isfile(path):
        raise FileNotFoundError()

    with open(path) as f:
        raw_text = f.read()

    try:
        parsed = parse_markdown(raw_text)
    except ValueError:
        print(f"Error parsing file at {path}")
        raise

    return parsed


def get_section_content(sections: list, section_name: str) -> str:
    """Get the content of a section by its name."""
    for section in sections:
        if next(iter(section.metadata.values())) == section_name:
            return str(section.page_content.strip())

    return ""


def clean_bugzillas(section: str) -> str:
    """Clean up bugzilla references in the errata."""
    pattern = r"\[([^\]]+)\]\((http[s]?:\/\/[^\)]+)\)"
    matches = re.findall(pattern, section)

    bugzillas = []
    for match in matches:
        bz_name = match[0].replace(" - ", " ")
        bz_url = match[1]
        bugzillas.append(f"- {bz_name} found at {bz_url}")

    return "This update fixes the these bugs:\n\n" + "\n".join(bugzillas)


def clean_description(section: str) -> str:
    """Clean up an errata description."""
    # Be specific about what we're fixing.
    section = section.replace("Security Fix(es):", "This update fixes the following security issues:")

    # Remove the boilerplate line about checking references.
    section = "\n".join([
        x for x in section.split("\n") if not x.startswith("For more details about the security issue")
    ])

    return section.strip()


def clean_solution(section: str) -> str:
    """Clean up an errata solution.

    Some errata have specific instructions included in the errata itself while others
    just link to a solution article.

    TODO: It would be nice to pull in the solution article here instead of a link.
    """
    if section.startswith("For details on how to apply this update"):
        section = section.replace("\n\n", " ")

    return clean_links(section).strip()


def get_affected_products(product_keys: list, product_detail: list) -> str:
    """Get the affected products from the frontmatter.

    This is tricky because the portal_product_filter contains a pipe delimited table,
    but the names of products are fully repeated for every version and architecture.
    That's a *lot* of redundant information to hand off to the embedding model and LLM.

    The portal_product_names list contains the keys that go along with the
    portal_product_filter table, so we can use to generate a more concise list.
    """
    product_detail = [x.split("|") for x in product_detail]

    product_pieces = []
    for product_key in product_keys:
        # Get all the affected versions from the affected products detail list that
        # match ths current product key.
        versions = sorted([x[2] for x in product_detail if x[1] == product_key])

        # Add the version(s) to the end the product key.
        if len(versions) > 1:
            product_pieces.append(f"- {product_key} versions {" and ".join(versions)}")
        else:
            product_pieces.append(f"- {product_key} version {versions[0]}")

    product_text = "\n".join(sorted(product_pieces))

    return "This errata affects the following products:\n\n" + product_text


def parse(path: str) -> str:
    """Parse an errata document into a clean format."""
    errata_doc = load_errata(path)

    metadata = errata_doc["frontmatter"]
    sections = errata_doc["content"]

    description = get_section_content(sections, "Description")
    solution = get_section_content(sections, "Solution")
    bugzillas = get_section_content(sections, "Fixes")
    products = get_affected_products(
        metadata["extra"]["portal_product_names"], metadata["extra"]["portal_product_filter"]
    )

    clean_doc_pieces = [
        metadata["extra"]["original_title"],
        f"Published: {metadata["extra"]["issued"]}",
        f"Access this document at this URL: https://access.redhat.com{metadata["path"]}",
        metadata["extra"]["portal_summary"],
        clean_description(description),
        clean_solution(solution),
        products,
        clean_bugzillas(bugzillas),
    ]

    clean_doc = "\n\n".join(clean_doc_pieces)

    return clean_doc
