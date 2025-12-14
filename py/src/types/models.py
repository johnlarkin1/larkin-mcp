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


class ProjectDetails(BaseModel):
    name: str = Field(description="Project name")
    url: str | None = Field(default=None, description="Project URL")
    tech_stack: list[str] = Field(default_factory=list, description="Technologies used")
    summary: str | None = Field(default=None, description="Project description")


class ProjectNotFound(BaseModel):
    error: str = Field(description="Error message")
    available_projects: list[str] = Field(default_factory=list, description="List of available project names")


class TimelineEntry(BaseModel):
    role: str = Field(description="Job title or company/role")
    company: str | None = Field(default=None, description="Company name if separate from role")
    start_date: str | None = Field(default=None, description="Start date (e.g., 'August 2025')")
    end_date: str | None = Field(default=None, description="End date (e.g., 'Present')")


class ExperienceTimeline(BaseModel):
    entries: list[TimelineEntry] = Field(default_factory=list, description="Work experience entries")
