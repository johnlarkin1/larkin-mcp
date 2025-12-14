from pydantic import BaseModel, Field


class Metadata(BaseModel):
    mcp_version: str = Field(description="MCP server version")
    mcp_website: str = Field(description="MCP server website")
    resume_last_updated: str = Field(description="Date the resume was last updated")


class ResourceStatus(BaseModel):
    available: bool = Field(description="Whether the resource exists and is readable")
    size_bytes: int = Field(default=0, description="Size of the resource in bytes")


class HealthCheckResponse(BaseModel):
    status: str = Field(description="Server health status (e.g., 'healthy')")
    version: str = Field(description="MCP server version")
    resources: dict[str, ResourceStatus] = Field(description="Status of each resource")
