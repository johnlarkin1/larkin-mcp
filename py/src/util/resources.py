"""Resource loading utilities for the larkin-mcp server."""

import logging
from pathlib import Path

from src.constants import RESOURCES_CATEGORIES, RESOURCES_DIR, RESUME_MD_PATH
from src.types.models import ResourceInfo

logger = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        super().__init__(f"Resource '{name}' not found at {path}")


class ResourceReadError(Exception):
    """Raised when a resource exists but cannot be read."""

    def __init__(self, name: str, path: Path, cause: Exception):
        self.name = name
        self.path = path
        self.cause = cause
        super().__init__(f"Error reading resource '{name}' from {path}: {cause}")


def load_resource(name: str, *, raise_on_error: bool = False) -> str:
    """Load a resource file by name.

    Args:
        name: Resource identifier (e.g., "resume", "bio", "projects")
        raise_on_error: If True, raise exceptions instead of returning error strings.
                       Defaults to False for backward compatibility.

    Returns:
        Resource content as string, or error message if raise_on_error=False.

    Raises:
        ResourceNotFoundError: If raise_on_error=True and resource not found.
        ResourceReadError: If raise_on_error=True and resource cannot be read.
    """
    if name == "resume":
        path = RESUME_MD_PATH
    else:
        path = RESOURCES_DIR / f"{name}.md"

    if not path.exists():
        msg = f"Resource '{name}' not found at {path}"
        logger.warning(msg)
        if raise_on_error:
            raise ResourceNotFoundError(name, path)
        return f"Resource '{name}' not found. Please create {path}"

    try:
        content = path.read_text()
        logger.debug(f"Loaded resource '{name}' ({len(content)} bytes)")
        return content
    except Exception as e:
        msg = f"Error reading resource '{name}' from {path}: {e}"
        logger.error(msg)
        if raise_on_error:
            raise ResourceReadError(name, path, e) from e
        return f"Error reading resource '{name}': {e}"


def list_resources() -> list[str]:
    """List all available resource identifiers.

    Returns:
        List of resource names that exist and can be loaded.
    """
    resources = []

    # Check resume separately since it has a special path
    if RESUME_MD_PATH.exists():
        resources.append("resume")

    # Check other resources from categories
    for expected in RESOURCES_CATEGORIES:
        if expected == "resume":
            continue  # Already handled above
        resource_path = RESOURCES_DIR / f"{expected}.md"
        if resource_path.exists():
            resources.append(expected)

    logger.debug(f"Found {len(resources)} available resources: {resources}")
    return resources


def search_resources(query: str) -> dict[str, list[str]]:
    """Search all resources for lines matching a query string.

    Args:
        query: Search string (case-insensitive).

    Returns:
        Dictionary mapping resource names to lists of matching lines.
    """
    if not query or not query.strip():
        logger.warning("Empty search query provided")
        return {}

    results: dict[str, list[str]] = {}
    query_lower = query.lower()

    for resource_name in list_resources():
        try:
            content = load_resource(resource_name, raise_on_error=True)
            matching_lines = [line for line in content.splitlines() if query_lower in line.lower()]

            if matching_lines:
                results[resource_name] = matching_lines
                logger.debug(f"Found {len(matching_lines)} matches in '{resource_name}'")
        except (ResourceNotFoundError, ResourceReadError) as e:
            logger.warning(f"Skipping resource '{resource_name}' in search: {e}")
            continue

    logger.info(f"Search for '{query}' found matches in {len(results)} resources")
    return results


def get_resource_info(name: str) -> ResourceInfo:
    """Get metadata about a resource."""
    if name == "resume":
        path = RESUME_MD_PATH
    else:
        path = RESOURCES_DIR / f"{name}.md"

    size_bytes = 0
    if path.exists():
        try:
            size_bytes = path.stat().st_size
        except OSError as e:
            logger.warning(f"Could not get size for '{name}': {e}")

    return ResourceInfo(name=name, path=str(path), exists=path.exists(), size_bytes=size_bytes)
