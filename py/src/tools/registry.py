import re

from src.constants import MCP_VERSION, MCP_WEBSITE_URL, RESOURCES_CATEGORIES, RESUME_DATE_VERSION
from src.types.models import (
    ExperienceTimeline,
    HealthCheckResponse,
    ProjectDetails,
    ProjectNotFound,
    ResourceStatus,
    TimelineEntry,
)
from src.types.tool import Metadata
from src.util.resources import list_resources, load_resource, search_resources
from src.util.search import is_semantic_search_available
from src.util.search import semantic_search as _semantic_search


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

    @mcp.tool()
    def get_section(resource: str, section: str) -> str:
        """Extract a specific section from a resource by heading name.

        Args:
            resource: Resource name (resume, bio, projects, skills, work, contact)
            section: Section heading to extract (case-insensitive)

        Returns:
            Content under the specified heading, or error message if not found.
        """
        content = load_resource(resource)
        if content.startswith("Resource '"):
            return content

        # Find section by heading (supports # or ## headings)
        pattern = rf"^(#{1, 2})\s+{re.escape(section)}\s*$"
        lines = content.split("\n")

        section_start = None
        section_level = None

        for i, line in enumerate(lines):
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                section_start = i
                section_level = len(match.group(1))
                break

        if section_start is None:
            # List available sections
            headings = [line for line in lines if re.match(r"^#{1,2}\s+", line)]
            available = ", ".join(h.lstrip("#").strip() for h in headings[:10])
            return f"Section '{section}' not found in {resource}. Available sections: {available}"

        # Extract content until next heading of same or higher level
        section_lines = [lines[section_start]]
        for line in lines[section_start + 1 :]:
            heading_match = re.match(r"^(#{1,2})\s+", line)
            if heading_match and len(heading_match.group(1)) <= section_level:
                break
            section_lines.append(line)

        return "\n".join(section_lines).strip()

    @mcp.tool()
    def filter_projects_by_tech(tech: str) -> str:
        """Filter projects by technology/stack.

        Args:
            tech: Technology to filter by (e.g., "Python", "TypeScript", "Rust")

        Returns:
            Formatted list of projects using the specified technology.
        """
        content = load_resource("projects")
        if content.startswith("Resource '"):
            return content

        # Parse projects - each project starts with ### heading
        projects = re.split(r"(?=^###\s+)", content, flags=re.MULTILINE)
        matching_projects = []

        for project in projects:
            if not project.strip() or not project.startswith("###"):
                continue

            # Check if tech appears in Stack line (case-insensitive)
            if re.search(rf"Stack:.*{re.escape(tech)}", project, re.IGNORECASE):
                matching_projects.append(project.strip())

        if not matching_projects:
            return f"No projects found using '{tech}'. Try searching for: Python, TypeScript, Rust, React, etc."

        return f"# Projects using {tech}\n\n" + "\n\n".join(matching_projects)

    @mcp.tool()
    def get_project_details(project_name: str) -> ProjectDetails | ProjectNotFound:
        """Get structured details about a specific project.

        Args:
            project_name: Name of the project to look up
        """
        content = load_resource("projects")
        if content.startswith("Resource '"):
            return ProjectNotFound(error=content)

        # Parse projects - each project starts with ### heading
        projects = re.split(r"(?=^###\s+)", content, flags=re.MULTILINE)

        for project in projects:
            if not project.strip() or not project.startswith("###"):
                continue

            # Extract project name from heading
            name_match = re.match(r"###\s+(.+)", project)
            if not name_match:
                continue

            name = name_match.group(1).strip()
            if project_name.lower() not in name.lower():
                continue

            # Extract URL
            url = None
            url_match = re.search(r"URL:\s*(.+)", project)
            if url_match:
                url = url_match.group(1).strip()

            # Extract Stack
            tech_stack = []
            stack_match = re.search(r"Stack:\s*(.+)", project)
            if stack_match:
                tech_stack = [t.strip() for t in stack_match.group(1).split(",")]

            # Extract Summary (everything after the metadata lines)
            lines = project.split("\n")
            summary_lines = []
            in_summary = False
            for line in lines:
                if line.startswith("Summary:"):
                    in_summary = True
                    summary_lines.append(line.replace("Summary:", "").strip())
                elif in_summary and line.strip() and not line.startswith(("URL:", "Stack:")):
                    summary_lines.append(line.strip())

            summary = " ".join(summary_lines) if summary_lines else None

            return ProjectDetails(name=name, url=url, tech_stack=tech_stack, summary=summary)

        # Project not found - list available projects
        available = []
        for project in projects:
            name_match = re.match(r"###\s+(.+)", project)
            if name_match:
                available.append(name_match.group(1).strip())

        return ProjectNotFound(error=f"Project '{project_name}' not found", available_projects=available)

    @mcp.tool()
    def get_experience_timeline() -> ExperienceTimeline:
        """Return work experience as structured timeline entries."""
        resume = load_resource("resume")
        if resume.startswith("Resource '"):
            return ExperienceTimeline(entries=[])

        # Extract work experience section only (not Personal Projects, Volunteer, etc.)
        lines = resume.split("\n")
        in_work = False
        work_lines = []

        for line in lines:
            if re.match(r"^##\s+Work\s+Experience\s*$", line, re.IGNORECASE):
                in_work = True
                continue
            elif in_work and re.match(r"^##\s+", line):
                # Stop at next ## section
                break
            elif in_work:
                work_lines.append(line)

        if not work_lines:
            return ExperienceTimeline(entries=[])

        # Parse entries - only ### headings are job entries
        # Format: ### Company — Role
        #         (blank line)
        #         _Month Year – Month Year | Location_
        entries: list[TimelineEntry] = []
        i = 0
        while i < len(work_lines):
            line = work_lines[i]

            # Match job heading: ### Company — Role
            job_match = re.match(r"^###\s+(.+?)\s*[—–-]\s*(.+)$", line)
            if job_match:
                company = job_match.group(1).strip()
                role = job_match.group(2).strip()

                # Look for date in the next few lines (may have blank line)
                start_date = None
                end_date = None
                for j in range(1, 4):  # Check next 3 lines
                    if i + j >= len(work_lines):
                        break
                    next_line = work_lines[i + j]
                    date_match = re.search(r"_(\w+\s+\d{4})\s*[–-]\s*(\w+\s+\d{4}|Present)", next_line)
                    if date_match:
                        start_date = date_match.group(1)
                        end_date = date_match.group(2)
                        break

                entries.append(
                    TimelineEntry(
                        role=role,
                        company=company,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

            i += 1

        return ExperienceTimeline(entries=entries)

    @mcp.tool()
    def semantic_search(query: str, top_k: int = 5) -> str:
        """Search resources using semantic similarity (embedding-based).

        This tool uses AI embeddings to find semantically similar content,
        even if the exact words don't match.

        Args:
            query: Natural language search query.
            top_k: Maximum number of results to return (default 5).

        Returns:
            Formatted search results with similarity scores, or error message
            if semantic search is not available.
        """
        if not is_semantic_search_available():
            return (
                "Semantic search is not available. "
                "Install with: pip install larkin-mcp[semantic]\n\n"
                "Falling back to keyword search..."
            )

        try:
            results = _semantic_search(query, top_k=top_k)

            if not results:
                return f"No semantically similar content found for: '{query}'"

            output = [f"# Semantic Search Results for '{query}'", ""]
            for result in results:
                score_pct = int(result["score"] * 100)
                output.append(f"## {result['resource'].title()} ({score_pct}% match)")
                # Truncate long chunks for readability
                chunk = result["chunk"]
                if len(chunk) > 300:
                    chunk = chunk[:300] + "..."
                output.append(f"> {chunk}")
                output.append("")

            return "\n".join(output)
        except Exception as e:
            return f"Semantic search error: {e}"
