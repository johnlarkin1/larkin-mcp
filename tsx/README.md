# larkin-mcp (TypeScript/Bun)

An MCP server for understanding and inquiring about John Larkin.

## Setup

```bash
bun install
```

## Running

```bash
# Production (stdio transport)
bun run src/index.ts

# With MCP Inspector
bunx @modelcontextprotocol/inspector bun run src/index.ts
```

## Testing

```bash
bun test
```

## Tools

- `get_metadata` - Returns MCP server metadata
- `get_resume` - Returns resume content as Markdown
- `get_bio` - Returns extended biography
- `get_contact` - Returns contact information
- `get_projects` - Returns list of projects
- `get_skills` - Returns skills overview
- `get_work` - Returns work experience and employment history
- `get_available_resources` - Lists available resource identifiers
- `search_info` - Searches across all resources
- `health_check` - Returns server health status and resource availability

## Resources

- `config://version` - MCP version
- `config://resume-version` - Resume last updated date
- `larkin://resume` - Resume (Markdown)
- `larkin://resume.pdf` - Resume (PDF)
- `larkin://bio` - Biography
- `larkin://projects` - Projects
- `larkin://contact` - Contact info
- `larkin://skills` - Skills
- `larkin://work` - Work experience

## Prompts

- `summarize_for_role(role)` - Generate tailored summary for a job role
- `compare_to_job(job_description)` - Analyze fit for a job description
- `interview_prep(role, company?)` - Interview prep with questions
- `project_deep_dive(project_name)` - Deep dive into a specific project
