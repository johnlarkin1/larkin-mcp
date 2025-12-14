"""Resource loading utilities for the larkin-mcp server."""

import logging
from pathlib import Path

from src.constants import RESOURCES_CATEGORIES, RESOURCES_DIR, RESUME_MD_PATH

logger = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        super().__init__(f"Resource '{name}' not found at {path}")


class ResourceReadError(Exception):
    def __init__(self, name: str, path: Path, cause: Exception):
        self.name = name
        self.path = path
        self.cause = cause
        super().__init__(f"Error reading resource '{name}' from {path}: {cause}")


def load_resource(name: str, *, raise_on_error: bool = False) -> str:
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
    resources = []

    # resume has special path
    if RESUME_MD_PATH.exists():
        resources.append("resume")

    for expected in RESOURCES_CATEGORIES:
        if expected == "resume":
            continue  # already handled above
        resource_path = RESOURCES_DIR / f"{expected}.md"
        if resource_path.exists():
            resources.append(expected)

    logger.debug(f"Found {len(resources)} available resources: {resources}")
    return resources


def search_resources(query: str) -> dict[str, list[str]]:
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
