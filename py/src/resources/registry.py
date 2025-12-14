from src.constants import MCP_VERSION, RESOURCES_DIR, RESUME_DATE_VERSION
from src.util.resources import load_resource


def register_resources(mcp):
    @mcp.resource("config://version")
    def get_version() -> str:
        return MCP_VERSION

    @mcp.resource("config://resume-version")
    def get_resume_version() -> str:
        return RESUME_DATE_VERSION

    @mcp.resource("larkin://resume")
    def get_resume() -> str:
        return load_resource("resume")

    @mcp.resource("larkin://resume.pdf", mime_type="application/pdf")
    def get_resume_pdf() -> bytes:
        pdf_path = RESOURCES_DIR / "resume" / "larkin_resume.pdf"
        return pdf_path.read_bytes()

    @mcp.resource("larkin://bio")
    def get_bio() -> str:
        return load_resource("bio")

    @mcp.resource("larkin://projects")
    def get_projects() -> str:
        return load_resource("projects")

    @mcp.resource("larkin://contact")
    def get_contact() -> str:
        return load_resource("contact")

    @mcp.resource("larkin://skills")
    def get_skills() -> str:
        return load_resource("skills")
