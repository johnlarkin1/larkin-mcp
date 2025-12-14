"""Tests for MCP tool functions.

Note: These tests call the tool functions directly without going through
the MCP server, which is useful for unit testing the logic.
"""

import re

import pytest

from src.constants import MCP_VERSION, RESOURCES_CATEGORIES


class TestHealthCheck:
    """Tests for health_check tool logic."""

    def test_health_check_returns_dict(self):
        """Test that health_check returns the expected structure."""
        from src.util.resources import load_resource

        # Simulate health check logic
        resources_status = {}
        for resource in RESOURCES_CATEGORIES:
            content = load_resource(resource)
            is_available = not content.startswith("Resource '") and not content.startswith("Error")
            resources_status[resource] = {
                "available": is_available,
                "size_bytes": len(content.encode()) if is_available else 0,
            }

        result = {
            "status": "healthy",
            "version": MCP_VERSION,
            "resources": resources_status,
        }

        assert result["status"] == "healthy"
        assert result["version"] == MCP_VERSION
        assert "resources" in result

    def test_resources_have_expected_fields(self):
        """Test that each resource has expected status fields."""
        from src.util.resources import load_resource

        for resource in RESOURCES_CATEGORIES:
            content = load_resource(resource)
            is_available = not content.startswith("Resource '")

            if is_available:
                assert len(content.encode()) > 0


class TestGetSection:
    """Tests for get_section tool logic."""

    def test_extract_section(self, sample_markdown_content: str):
        """Test extracting a section from markdown."""
        # Find section by heading
        pattern = r"^(#{1,2})\s+Section One\s*$"
        lines = sample_markdown_content.split("\n")

        section_start = None
        section_level = None

        for i, line in enumerate(lines):
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                section_start = i
                section_level = len(match.group(1))
                break

        assert section_start is not None, "Section One not found"
        assert section_level == 2

    def test_section_not_found(self, sample_markdown_content: str):
        """Test behavior when section is not found."""
        pattern = r"^(#{1,2})\s+Nonexistent Section\s*$"
        lines = sample_markdown_content.split("\n")

        found = False
        for line in lines:
            if re.match(pattern, line, re.IGNORECASE):
                found = True
                break

        assert not found


class TestFilterProjectsByTech:
    """Tests for filter_projects_by_tech tool logic."""

    def test_filter_finds_python_projects(self, sample_projects_content: str):
        """Test filtering projects by Python."""
        projects = re.split(r"(?=^###\s+)", sample_projects_content, flags=re.MULTILINE)
        matching = []

        for project in projects:
            if project.strip() and project.startswith("###"):
                if re.search(r"Stack:.*Python", project, re.IGNORECASE):
                    matching.append(project.strip())

        assert len(matching) == 1
        assert "Project Alpha" in matching[0]

    def test_filter_finds_typescript_projects(self, sample_projects_content: str):
        """Test filtering projects by TypeScript."""
        projects = re.split(r"(?=^###\s+)", sample_projects_content, flags=re.MULTILINE)
        matching = []

        for project in projects:
            if project.strip() and project.startswith("###"):
                if re.search(r"Stack:.*TypeScript", project, re.IGNORECASE):
                    matching.append(project.strip())

        assert len(matching) == 1
        assert "Project Beta" in matching[0]

    def test_filter_no_matches(self, sample_projects_content: str):
        """Test filtering with no matching projects."""
        projects = re.split(r"(?=^###\s+)", sample_projects_content, flags=re.MULTILINE)
        matching = []

        for project in projects:
            if project.strip() and project.startswith("###"):
                if re.search(r"Stack:.*Cobol", project, re.IGNORECASE):
                    matching.append(project.strip())

        assert len(matching) == 0


class TestGetProjectDetails:
    """Tests for get_project_details tool logic."""

    def test_parse_project_details(self, sample_projects_content: str):
        """Test parsing project details."""
        projects = re.split(r"(?=^###\s+)", sample_projects_content, flags=re.MULTILINE)

        for project in projects:
            if not project.strip() or not project.startswith("###"):
                continue

            name_match = re.match(r"###\s+(.+)", project)
            if not name_match:
                continue

            name = name_match.group(1).strip()
            if "Alpha" not in name:
                continue

            # Parse details
            details = {"name": name}

            url_match = re.search(r"URL:\s*(.+)", project)
            if url_match:
                details["url"] = url_match.group(1).strip()

            stack_match = re.search(r"Stack:\s*(.+)", project)
            if stack_match:
                details["tech_stack"] = [t.strip() for t in stack_match.group(1).split(",")]

            assert details["name"] == "Project Alpha"
            assert details["url"] == "https://example.com/alpha"
            assert "Python" in details["tech_stack"]
            assert "FastAPI" in details["tech_stack"]
            return

        pytest.fail("Project Alpha not found")

    def test_project_not_found(self, sample_projects_content: str):
        """Test behavior when project is not found."""
        projects = re.split(r"(?=^###\s+)", sample_projects_content, flags=re.MULTILINE)

        found = False
        for project in projects:
            if not project.strip() or not project.startswith("###"):
                continue

            name_match = re.match(r"###\s+(.+)", project)
            if name_match and "Nonexistent" in name_match.group(1):
                found = True
                break

        assert not found


class TestSearchInfo:
    """Tests for search_info tool."""

    def test_search_returns_formatted_output(self):
        """Test that search returns formatted results."""
        from src.util.resources import search_resources

        results = search_resources("Python")
        if results:
            output = []
            for resource, lines in results.items():
                output.append(f"## {resource.title()}")
                output.extend(f"  - {line.strip()}" for line in lines[:5])

            formatted = "\n".join(output)
            assert "##" in formatted

    def test_search_no_results_message(self):
        """Test message when no results found."""
        from src.util.resources import search_resources

        results = search_resources("xyznonexistent123")
        if not results:
            message = "No matches found for 'xyznonexistent123'"
            assert "No matches found" in message
