use rmcp::{
    ErrorData as McpError, RoleServer,
    handler::server::{router::prompt::PromptRouter, tool::ToolRouter, wrapper::Parameters},
    model::*,
    prompt, prompt_handler, prompt_router,
    service::RequestContext,
    tool, tool_handler, tool_router,
};
use serde_json::json;

use crate::constants::{MCP_INSTRUCTIONS, MCP_VERSION, MCP_WEBSITE_URL, RESUME_DATE_VERSION};
use crate::resources::{self, RESOURCE_CATEGORIES};
use crate::schema::{
    CompareToJobArgs, HealthCheckResponse, InterviewPrepArgs, Metadata, ProjectDeepDiveArgs,
    ResourceStatus, SearchQuery, SummarizeForRoleArgs,
};

const RESUME_PDF: &[u8] = include_bytes!("resources/content/resume/larkin_resume.pdf");

/// So this is really for my own learning, but the approach with rmcp
/// is that these macros are pseuoequivalent to the Python decorators
/// tool_router. Per the docs:
/// "The #[tool_router] macro automatically generates the routing logic,
/// and the #[tool] attribute marks methods as MCP tools."
#[derive(Clone)]
pub struct LarkinServer {
    tool_router: ToolRouter<Self>,
    prompt_router: PromptRouter<Self>,
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
            prompt_router: Self::prompt_router(),
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

    #[tool(
        description = "Return collegiate tennis career information including awards and match records."
    )]
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
        let mut resources_status = std::collections::HashMap::new();

        for &category in RESOURCE_CATEGORIES {
            if let Some(content) = resources::get_resource(category) {
                let is_available =
                    !content.starts_with("Resource '") && !content.starts_with("Error");
                resources_status.insert(
                    category,
                    ResourceStatus {
                        available: is_available,
                        size_bytes: if is_available { content.len() } else { 0 },
                    },
                );
            }
        }

        let response = HealthCheckResponse {
            status: "healthy",
            version: MCP_VERSION,
            resources: resources_status,
        };
        let json = serde_json::to_string_pretty(&response).unwrap_or_default();
        Ok(CallToolResult::success(vec![Content::text(json)]))
    }
}

#[prompt_router]
impl LarkinServer {
    #[prompt(
        name = "summarize_for_role",
        description = "Generate a tailored summary of John's background for a specific job role."
    )]
    async fn summarize_for_role(
        &self,
        Parameters(args): Parameters<SummarizeForRoleArgs>,
    ) -> Result<GetPromptResult, McpError> {
        let content = format!(
            r#"Based on John Larkin's background, create a concise 2-3 paragraph summary
highlighting why he would be a strong fit for a {} position.

To gather the necessary information, use these tools:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Notable projects demonstrating expertise
- get_skills() - Technical capabilities

Focus on:
1. Relevant experience from work history that aligns with the role
2. Technical skills that match typical {} requirements
3. Leadership experience or impact (if applicable)
4. Notable projects that demonstrate relevant capabilities

Keep the summary professional and tailored specifically for a {} position."#,
            args.role, args.role, args.role
        );

        Ok(GetPromptResult {
            description: Some(format!(
                "Generate a tailored summary for a {} position",
                args.role
            )),
            messages: vec![PromptMessage::new_text(PromptMessageRole::User, content)],
        })
    }

    #[prompt(
        name = "compare_to_job",
        description = "Analyze how John's background aligns with a specific job description."
    )]
    async fn compare_to_job(
        &self,
        Parameters(args): Parameters<CompareToJobArgs>,
    ) -> Result<GetPromptResult, McpError> {
        let content = format!(
            r#"Analyze John Larkin's fit for the following job description:

---
{}
---

Use these tools to gather information:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_skills() - Technical capabilities
- get_projects() - Project portfolio

Please provide:
1. **Matching Qualifications**: Skills and experience that directly match job requirements
2. **Relevant Projects**: Projects that demonstrate applicable expertise
3. **Potential Gaps**: Areas where additional context or experience might be needed
4. **Unique Strengths**: Standout qualities that differentiate John from other candidates
5. **Suggested Talking Points**: Key accomplishments to highlight in an interview

Format the analysis in clear sections with bullet points for easy scanning."#,
            args.job_description
        );

        Ok(GetPromptResult {
            description: Some("Analyze fit against job description".to_string()),
            messages: vec![PromptMessage::new_text(PromptMessageRole::User, content)],
        })
    }

    #[prompt(
        name = "interview_prep",
        description = "Generate likely interview questions and talking points for a role."
    )]
    async fn interview_prep(
        &self,
        Parameters(args): Parameters<InterviewPrepArgs>,
    ) -> Result<GetPromptResult, McpError> {
        let company_context = args
            .company
            .as_ref()
            .map(|c| format!(" at {}", c))
            .unwrap_or_default();

        let content = format!(
            r#"Help prepare John Larkin for an interview for a {} position{}.

Use these tools to understand John's background:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Project portfolio
- get_skills() - Technical capabilities

Generate:

## Likely Interview Questions
Based on John's experience and typical {} interviews, list 8-10 questions he's likely to face, categorized by:
- Technical questions
- Behavioral/situational questions
- Experience-based questions
- Questions about specific projects

## Recommended Answers/Talking Points
For each question, suggest specific examples from John's background that would make strong answers.

## Questions John Should Ask
Suggest thoughtful questions John could ask the interviewer about the {} role{}.

## Potential Weak Points to Prepare For
Identify any gaps or areas where John might need to prepare additional context."#,
            args.role, company_context, args.role, args.role, company_context
        );

        Ok(GetPromptResult {
            description: Some(format!(
                "Interview prep for {} role{}",
                args.role, company_context
            )),
            messages: vec![PromptMessage::new_text(PromptMessageRole::User, content)],
        })
    }

    #[prompt(
        name = "project_deep_dive",
        description = "Get detailed information about a specific project."
    )]
    async fn project_deep_dive(
        &self,
        Parameters(args): Parameters<ProjectDeepDiveArgs>,
    ) -> Result<GetPromptResult, McpError> {
        let content = format!(
            r#"Provide a comprehensive overview of John Larkin's "{}" project.

Use get_projects() and get_resume() to gather information.

Please include:
1. **Project Overview**: What the project does and its purpose
2. **Tech Stack**: Technologies and tools used
3. **Key Features**: Main capabilities and functionality
4. **Challenges & Solutions**: Technical challenges overcome
5. **Impact & Results**: Outcomes and metrics (if available)
6. **Relevance**: How this project demonstrates transferable skills

If the project isn't found, list available projects from get_projects() and suggest alternatives."#,
            args.project_name
        );

        Ok(GetPromptResult {
            description: Some(format!("Deep dive into {} project", args.project_name)),
            messages: vec![PromptMessage::new_text(PromptMessageRole::User, content)],
        })
    }
}

#[tool_handler]
#[prompt_handler]
impl rmcp::ServerHandler for LarkinServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            instructions: Some(MCP_INSTRUCTIONS.into()),
            capabilities: ServerCapabilities::builder()
                .enable_tools()
                .enable_resources()
                .enable_prompts()
                .build(),
            ..Default::default()
        }
    }

    async fn list_resources(
        &self,
        _request: Option<PaginatedRequestParam>,
        _ctx: RequestContext<RoleServer>,
    ) -> Result<ListResourcesResult, McpError> {
        Ok(ListResourcesResult {
            resources: vec![
                RawResource::new("config://version", "Get version".to_string()).no_annotation(),
                RawResource::new("config://resume-version", "Get resume version".to_string())
                    .no_annotation(),
                RawResource::new("larkin://resume", "Get resume".to_string()).no_annotation(),
                RawResource::new("larkin://resume.pdf", "Get resume pdf".to_string())
                    .no_annotation(),
                RawResource::new("larkin://bio", "Get bio".to_string()).no_annotation(),
                RawResource::new("larkin://projects", "Get projects".to_string()).no_annotation(),
                RawResource::new("larkin://contact", "Get contact".to_string()).no_annotation(),
                RawResource::new("larkin://skills", "Get skills".to_string()).no_annotation(),
                RawResource::new("larkin://work", "Get work".to_string()).no_annotation(),
                RawResource::new("larkin://tennis", "Get tennis info".to_string()).no_annotation(),
            ],
            next_cursor: None,
            meta: None,
        })
    }

    async fn read_resource(
        &self,
        ReadResourceRequestParam { uri }: ReadResourceRequestParam,
        _ctx: RequestContext<RoleServer>,
    ) -> Result<ReadResourceResult, McpError> {
        match uri.as_str() {
            "config://version" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(MCP_VERSION, uri)],
            }),
            "config://resume-version" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(RESUME_DATE_VERSION, uri)],
            }),
            "larkin://resume" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::RESUME, uri)],
            }),
            "larkin://resume.pdf" => {
                use base64::{Engine as _, engine::general_purpose::STANDARD};
                let base64_data = STANDARD.encode(RESUME_PDF);
                Ok(ReadResourceResult {
                    contents: vec![ResourceContents::BlobResourceContents {
                        blob: base64_data,
                        uri: uri.clone(),
                        mime_type: Some("application/pdf".into()),
                        meta: None,
                    }],
                })
            }
            "larkin://bio" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::BIO, uri)],
            }),
            "larkin://projects" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::PROJECTS, uri)],
            }),
            "larkin://contact" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::CONTACT, uri)],
            }),
            "larkin://skills" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::SKILLS, uri)],
            }),
            "larkin://work" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::WORK, uri)],
            }),
            "larkin://tennis" => Ok(ReadResourceResult {
                contents: vec![ResourceContents::text(resources::TENNIS, uri)],
            }),
            _ => Err(McpError::resource_not_found(
                "resource_not_found",
                Some(json!({ "uri": uri })),
            )),
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
