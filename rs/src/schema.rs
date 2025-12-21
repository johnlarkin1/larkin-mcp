use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize)]
pub struct Metadata {
    pub mcp_version: &'static str,
    pub mcp_website: &'static str,
    pub resume_last_updated: &'static str,
}

#[derive(Debug, Serialize)]
pub struct HealthCheckResponse {
    pub status: &'static str,
    pub version: &'static str,
    pub available_resources: Vec<&'static str>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct SearchQuery {
    pub query: String,
}
