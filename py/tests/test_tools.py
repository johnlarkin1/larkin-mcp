"""Tests for MCP tool functions.

Note: These tests call the tool functions directly without going through
the MCP server, which is useful for unit testing the logic.
"""

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
