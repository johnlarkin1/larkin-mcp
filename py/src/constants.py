from pathlib import Path

# MCP General
MCP_NAME = "larkin-mcp"
MCP_INSTRUCTIONS = (
    "This server provides information about John Larkin "
    "(github profile: johnlarkin1, site: johnlarkin1.github.io) and "
    "allows helpful tooling for more info"
)
MCP_WEBSITE_URL = "https://johnlarkin1.github.io/2025/larkin-mcp"
MCP_VERSION = "0.1.0"

# Resources
RESOURCES_DIR = Path(__file__).parent / "resources" / "content"
RESOURCES_CATEGORIES = ["resume", "bio", "projects", "contact", "skills", "work", "tennis"]

# Resume
RESUME_DATE_VERSION = "2025-12-14"
RESUME_PDF_PATH = RESOURCES_DIR / "resume" / "larkin_resume.pdf"
RESUME_MD_PATH = RESOURCES_DIR / "resume" / "larkin_resume.md"
