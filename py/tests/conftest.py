"""Shared pytest fixtures for larkin-mcp tests."""

import pytest


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing section extraction."""
    return """# Main Title

## Section One
Content for section one.
More content here.

## Section Two
Content for section two.

### Subsection
Nested content.

## Section Three
Final section content.
"""


@pytest.fixture
def sample_projects_content() -> str:
    """Sample projects markdown for testing project parsing."""
    return """# Projects

## Active Projects

### Project Alpha
URL: https://example.com/alpha
Stack: Python, FastAPI, PostgreSQL
Summary: A sample project using Python and FastAPI for API development.

### Project Beta
URL: https://example.com/beta
Stack: TypeScript, React, Node.js
Summary: A frontend application built with React and TypeScript.

## Past Projects

### Project Gamma
URL: https://example.com/gamma
Stack: Rust, WebAssembly
Summary: A high-performance tool built with Rust.
"""
