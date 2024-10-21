"""Tests for parsing errata files."""

import pytest
from langchain_core.documents import Document

from textprep.errata import (
    affects_rhel,
    clean_bugzillas,
    clean_description,
    clean_solution,
    get_affected_products,
    get_section_content,
    load_errata,
    parse,
)


def test_load_errata(tmp_path):
    content = """+++
title = '''Super important errata right here'''
+++

# Most important heading

First bit of content.
"""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "errata.md"
    p.write_text(content, encoding="utf-8")

    # Load valid markdown.
    result = load_errata(p)
    assert result["frontmatter"]["title"] == "Super important errata right here"
    assert result["content"][0].page_content.strip() == "First bit of content."

    # Load some JSON to throw an exception.
    p.write_text('{"key": "Wait a minute, this is JSON!}')
    with pytest.raises(ValueError):
        result = load_errata(p)

    # Delete the file and try to load it again.
    p.unlink()
    with pytest.raises(FileNotFoundError):
        result = load_errata(p)


def test_get_section_content(errata_doc):
    sections = [
        Document(metadata={"Header 1": "First"}, page_content="First section content"),
        Document(metadata={"Header 2": "Second"}, page_content="Second section content"),
    ]

    assert get_section_content(sections, "First") == "First section content"
    assert get_section_content(sections, "Second") == "Second section content"
    assert get_section_content(sections, "Third") == ""


def test_clean_bugzillas():
    content = """
- [BZ - 2044863](https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044863)
- [BZ - 2044864](https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044864)
- [BZ - 2044865](https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044865)
"""
    result = clean_bugzillas(content)
    expected = """This update fixes the these bugs:

- BZ 2044863 found at https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044863
- BZ 2044864 found at https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044864
- BZ 2044865 found at https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044865"""
    assert result == expected


def test_clean_description():
    content = """This is an important errata!

Security Fix(es):

- A very special CVE

For more details about the security issue(s), blah blah blah."""
    result = clean_description(content)
    print(result)
    expected = (
        "This is an important errata!\n\nThis update fixes the following security issues:\n\n- A very special CVE"
    )
    assert result == expected


def test_clean_solution():
    # The newlines should be removed and the link should be cleaned on this boilerplate
    # text.
    content = """For details on how to apply this update, which includes the changes described in this advisory, refer to:

<https://access.redhat.com/articles/11258>"""
    result = clean_solution(content)
    assert result.endswith("refer to: https://access.redhat.com/articles/11258")

    # This should be left untouched since it's unique content.
    content = "This is unique content about a solution you should know!"
    assert clean_solution(content) == content


def test_get_affected_products():
    product_keys = [
        "Red Hat CodeReady Linux Builder for ARM 64 - Extended Update Support",
        "Red Hat CodeReady Linux Builder for ARM 64",
    ]
    product_detail = [
        "Red Hat Enterprise Linux|Red Hat CodeReady Linux Builder for ARM 64|8|aarch64",
        "Red Hat Enterprise Linux|Red Hat CodeReady Linux Builder for ARM 64 - Extended Update Support|8.8|aarch64",
        "Red Hat Enterprise Linux|Red Hat CodeReady Linux Builder for ARM 64 - Extended Update Support|8.6|aarch64",
    ]

    result = get_affected_products(product_keys, product_detail)

    # These two matching ones should be joined.
    expected = "- Red Hat CodeReady Linux Builder for ARM 64 - Extended Update Support versions 8.6 and 8.8"
    assert expected in result

    # This one should be separate.
    expected = "- Red Hat CodeReady Linux Builder for ARM 64 version 8"
    assert expected in result


def test_parse_functional(errata_doc_path):
    result = parse(errata_doc_path)
    expected = """RHSA-2022:0886 - Moderate: virt:rhel and virt-devel:rhel security update

Published: 2022-03-15T09:10:17Z

Access this document at this URL: https://access.redhat.com/errata/RHSA-2022:0886

An update for the virt:rhel and virt-devel:rhel modules is now available for Red Hat Enterprise Linux 8.

Red Hat Product Security has rated this update as having a security impact of Moderate. A Common Vulnerability Scoring System (CVSS) base score, which gives a detailed severity rating, is available for each vulnerability from the CVE link(s) in the References section.

Kernel-based Virtual Machine (KVM) offers a full virtualization solution for Linux on numerous hardware platforms. The virt:rhel module contains packages which provide user-space components used to run virtual machines using KVM. The packages also provide APIs for managing and interacting with the virtualized
systems.

This update fixes the following security issues:

- QEMU: virtiofsd: potential privilege escalation via CVE-2018-13405 (CVE-2022-0358)

For details on how to apply this update, which includes the changes described in this advisory, refer to: https://access.redhat.com/articles/11258

This errata affects the following products:

- Red Hat CodeReady Linux Builder for ARM 64 - Extended Update Support versions 8.6 and 8.8
- Red Hat CodeReady Linux Builder for ARM 64 version 8
- Red Hat CodeReady Linux Builder for IBM z Systems - Extended Update Support versions 8.6 and 8.8
- Red Hat CodeReady Linux Builder for IBM z Systems version 8
- Red Hat CodeReady Linux Builder for Power, little endian - Extended Update Support versions 8.6 and 8.8
- Red Hat CodeReady Linux Builder for Power, little endian version 8
- Red Hat CodeReady Linux Builder for x86_64 - Extended Update Support versions 8.6 and 8.8
- Red Hat CodeReady Linux Builder for x86_64 version 8
- Red Hat Enterprise Linux Server - AUS version 8.6
- Red Hat Enterprise Linux Server - TUS versions 8.6 and 8.8
- Red Hat Enterprise Linux Server for Power LE - Update Services for SAP Solutions versions 8.6 and 8.8
- Red Hat Enterprise Linux for ARM 64 - Extended Update Support versions 8.6 and 8.8
- Red Hat Enterprise Linux for ARM 64 version 8
- Red Hat Enterprise Linux for IBM z Systems - Extended Update Support versions 8.6 and 8.8
- Red Hat Enterprise Linux for IBM z Systems version 8
- Red Hat Enterprise Linux for Power, little endian - Extended Update Support versions 8.6 and 8.8
- Red Hat Enterprise Linux for Power, little endian version 8
- Red Hat Enterprise Linux for x86_64 - Extended Update Support versions 8.6 and 8.8
- Red Hat Enterprise Linux for x86_64 - Update Services for SAP Solutions versions 8.6 and 8.8
- Red Hat Enterprise Linux for x86_64 version 8

This update fixes the these bugs:

- BZ 2044863 found at https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2044863"""
    assert result == expected


def test_affects_rhel(tmp_path):
    content = """+++
portal_product_names=["Red Hat Enterprise Linux Server - Extended Life Cycle Support","Red Hat Enterprise Linux for x86_64 - Update Services for SAP Solutions","Red Hat Enterprise Linux for x86_64 - Extended Update Support","Red Hat Enterprise Linux Desktop","Red Hat Enterprise Linux Server - AUS","Red Hat Enterprise Linux EUS Compute Node","Red Hat Enterprise Linux Server - TUS","Red Hat Enterprise Linux Server","Red Hat Enterprise Linux Workstation","Red Hat Enterprise Linux Server from RHUI","Red Hat Enterprise Linux for Scientific Computing"]
+++

# Heading

Content.
"""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "errata.md"
    p.write_text(content, encoding="utf-8")
    assert affects_rhel(p)

    content = """+++
portal_product_names=["Red Hat OpenShift Enterprise Infrastructure","Red Hat OpenShift Enterprise Application Node","Red Hat OpenShift Enterprise JBoss EAP add-on","Red Hat OpenShift Enterprise Client Tools"]
+++

# Heading

Content.
"""
    p.write_text(content, encoding="utf-8")
    assert not affects_rhel(p)
