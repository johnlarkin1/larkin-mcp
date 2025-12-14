from src.constants import MCP_VERSION, MCP_WEBSITE_URL, RESOURCES_CATEGORIES, RESUME_DATE_VERSION
from src.types.models import HealthCheckResponse, ResourceStatus
from src.types.tool import Metadata
from src.util.resources import list_resources, load_resource, search_resources


def register_tools(mcp):
    """Register MCP tools that expose John Larkin's portfolio content."""

    @mcp.tool()
    def get_metadata() -> Metadata:
        """Return metadata describing the MCP server and resume freshness."""
        return Metadata(
            mcp_version=MCP_VERSION,
            mcp_website=MCP_WEBSITE_URL,
            resume_last_updated=RESUME_DATE_VERSION,
        )

    @mcp.tool()
    def get_resume() -> str:
        """Return the full resume content as Markdown."""
        return load_resource("resume")

    @mcp.tool()
    def get_bio() -> str:
        """Return the extended biography content."""
        return load_resource("bio")

    @mcp.tool()
    def get_contact() -> str:
        """Return contact instructions for reaching John."""
        return load_resource("contact")

    @mcp.tool()
    def get_projects() -> str:
        """Return the curated list of noteworthy projects."""
        return load_resource("projects")

    @mcp.tool()
    def get_skills() -> str:
        """Return the current skills overview."""
        return load_resource("skills")

    @mcp.tool()
    def get_work() -> str:
        """Return detailed work experience and employment history."""
        return load_resource("work")

    @mcp.tool()
    def get_available_resources() -> list[str]:
        """Return identifiers for all available content resources."""
        return list_resources()

    @mcp.tool()
    def search_info(query: str) -> str:
        """Return a formatted summary of resources matching the query string."""
        results = search_resources(query)

        if not results:
            return f"No matches found for '{query}'"

        output = []
        for resource, lines in results.items():
            output.append(f"## {resource.title()}")
            output.extend(f"  - {line.strip()}" for line in lines[:5])

        return "\n".join(output)

    @mcp.tool()
    def health_check() -> HealthCheckResponse:
        """Return server health status and resource availability."""
        resources_status = {}
        for resource in RESOURCES_CATEGORIES:
            content = load_resource(resource)
            is_available = not content.startswith("Resource '") and not content.startswith("Error")
            resources_status[resource] = ResourceStatus(
                available=is_available,
                size_bytes=len(content.encode()) if is_available else 0,
            )

        return HealthCheckResponse(
            status="healthy",
            version=MCP_VERSION,
            resources=resources_status,
        )
