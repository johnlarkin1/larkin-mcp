"""Pydantic models for MCP tool inputs and outputs."""

from pydantic import BaseModel, Field


class ResourceStatus(BaseModel):
    available: bool = Field(description="Whether the resource exists and is readable")
    size_bytes: int = Field(default=0, description="Size of the resource in bytes")


class ResourceInfo(BaseModel):
    name: str = Field(description="Resource identifier")
    path: str = Field(description="File path")
    exists: bool = Field(description="Whether the resource file exists")
    size_bytes: int = Field(default=0, description="File size in bytes")


class HealthCheckResponse(BaseModel):
    status: str = Field(description="Server health status (e.g., 'healthy')")
    version: str = Field(description="MCP server version")
    resources: dict[str, ResourceStatus] = Field(description="Status of each resource")
