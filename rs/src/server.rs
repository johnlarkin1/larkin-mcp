use rmcp::{
    ErrorData as McpError,
    handler::server::{tool::ToolRouter, wrapper::Parameters},
    model::{CallToolResult, Content, ServerCapabilities, ServerInfo},
    tool, tool_handler, tool_router,
};

use crate::constants::{MCP_INSTRUCTIONS, MCP_VERSION, MCP_WEBSITE_URL, RESUME_DATE_VERSION};
use crate::resources::{self, RESOURCE_CATEGORIES};
use crate::schema::{HealthCheckResponse, Metadata, SearchQuery};

/// So this is really for my own learning, but the approach with rmcp 
/// is that these macros are pseuoequivalent to the Python decorators
/// tool_router. Per the docs:
/// "The #[tool_router] macro automatically generates the routing logic, 
/// and the #[tool] attribute marks methods as MCP tools."
#[derive(Clone)]
pub struct LarkinServer {
    tool_router: ToolRouter<Self>,
}

impl Default for LarkinServer {
    fn default() -> Self {
        Self::new()
    }
}

#[tool_router]
impl LarkinServer {
    pub fn new() -> Self {
        Self {
            tool_router: Self::tool_router(),
        }
    }

    #[tool(description = "Return metadata describing the MCP server and resume freshness.")]
    async fn get_metadata(&self) -> Result<CallToolResult, McpError> {
        let metadata = Metadata {
            mcp_version: MCP_VERSION,
            mcp_website: MCP_WEBSITE_URL,
            resume_last_updated: RESUME_DATE_VERSION,
        };
        let json = serde_json::to_string_pretty(&metadata).unwrap_or_default();
        Ok(CallToolResult::success(vec![Content::text(json)]))
    }

    #[tool(description = "Return the full resume content as Markdown.")]
    async fn get_resume(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::RESUME,
        )]))
    }

    #[tool(description = "Return the extended biography content.")]
    async fn get_bio(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(resources::BIO)]))
    }

    #[tool(description = "Return contact instructions for reaching John.")]
    async fn get_contact(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::CONTACT,
        )]))
    }

    #[tool(description = "Return the curated list of noteworthy projects.")]
    async fn get_projects(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::PROJECTS,
        )]))
    }

    #[tool(description = "Return the current skills overview.")]
    async fn get_skills(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::SKILLS,
        )]))
    }

    #[tool(description = "Return detailed work experience and employment history.")]
    async fn get_work(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::WORK,
        )]))
    }

    #[tool(description = "Return collegiate tennis career information including awards and match records.")]
    async fn get_tennis_info(&self) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![Content::text(
            resources::TENNIS,
        )]))
    }

    #[tool(description = "Return identifiers for all available content resources.")]
    async fn get_available_resources(&self) -> Result<CallToolResult, McpError> {
        let resources: Vec<String> = RESOURCE_CATEGORIES.iter().map(|s| s.to_string()).collect();
        let json = serde_json::to_string_pretty(&resources).unwrap_or_default();
        Ok(CallToolResult::success(vec![Content::text(json)]))
    }

    #[tool(description = "Return a formatted summary of resources matching the query string.")]
    async fn search_info(
        &self,
        Parameters(params): Parameters<SearchQuery>,
    ) -> Result<CallToolResult, McpError> {
        let results = resources::search_resources(&params.query);

        if results.is_empty() {
            return Ok(CallToolResult::success(vec![Content::text(format!(
                "No matches found for '{}'",
                params.query
            ))]));
        }

        let mut output = Vec::new();
        for (resource, lines) in results {
            output.push(format!("## {}", capitalize(resource)));
            for line in lines {
                output.push(format!("  - {}", line.trim()));
            }
        }

        Ok(CallToolResult::success(vec![Content::text(
            output.join("\n"),
        )]))
    }

    #[tool(description = "Return server health status and resource availability.")]
    async fn health_check(&self) -> Result<CallToolResult, McpError> {
        let response = HealthCheckResponse {
            status: "healthy",
            version: MCP_VERSION,
            available_resources: RESOURCE_CATEGORIES.to_vec(),
        };
        let json = serde_json::to_string_pretty(&response).unwrap_or_default();
        Ok(CallToolResult::success(vec![Content::text(json)]))
    }
}

#[tool_handler]
impl rmcp::ServerHandler for LarkinServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            instructions: Some(MCP_INSTRUCTIONS.into()),
            capabilities: ServerCapabilities::builder().enable_tools().build(),
            ..Default::default()
        }
    }
}

fn capitalize(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
    }
}
