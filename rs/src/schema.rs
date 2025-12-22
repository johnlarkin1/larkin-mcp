use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize)]
pub struct Metadata {
    pub mcp_version: &'static str,
    pub mcp_website: &'static str,
    pub resume_last_updated: &'static str,
}

#[derive(Debug, Serialize)]
pub struct ResourceStatus {
    pub available: bool,
    pub size_bytes: usize,
}

#[derive(Debug, Serialize)]
pub struct HealthCheckResponse {
    pub status: &'static str,
    pub version: &'static str,
    pub resources: std::collections::HashMap<&'static str, ResourceStatus>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct SearchQuery {
    #[schemars(description = "The search query to find in resources")]
    pub query: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
#[schemars(description = "Arguments for summarize_for_role prompt")]
pub struct SummarizeForRoleArgs {
    #[schemars(
        description = "The job title or role to summarize for (e.g., 'Staff Engineer', 'Engineering Manager')"
    )]
    pub role: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
#[schemars(description = "Arguments for compare_to_job prompt")]
pub struct CompareToJobArgs {
    #[schemars(description = "The full job description text to compare against")]
    pub job_description: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
#[schemars(description = "Arguments for interview_prep prompt")]
pub struct InterviewPrepArgs {
    #[schemars(description = "The job title/role being interviewed for")]
    pub role: String,
    #[schemars(description = "Optional company name for more targeted prep")]
    pub company: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
#[schemars(description = "Arguments for project_deep_dive prompt")]
pub struct ProjectDeepDiveArgs {
    #[schemars(description = "The name of the project to explore")]
    pub project_name: String,
}
