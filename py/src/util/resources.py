from src.constants import RESOURCES_CATEGORIES, RESOURCES_DIR, RESUME_MD_PATH


def load_resource(name: str) -> str:
    if name == "resume":
        path = RESUME_MD_PATH
    else:
        path = RESOURCES_DIR / f"{name}.md"

    if not path.exists():
        return f"Resource '{name}' not found. Please create {path}"

    return path.read_text()


def list_resources() -> list[str]:
    resources = []
    if RESUME_MD_PATH.exists():
        resources.append("resume")
    for expected in RESOURCES_CATEGORIES:
        if (RESOURCES_DIR / f"{expected}.md").exists():
            resources.append(expected)

    return resources


def search_resources(query: str) -> dict[str, list[str]]:
    results = {}
    query_lower = query.lower()
    for resource_name in list_resources():
        content = load_resource(resource_name)
        matching_lines = [line for line in content.splitlines() if query_lower in line.lower()]

        if matching_lines:
            results[resource_name] = matching_lines

    return results
