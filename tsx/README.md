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
bunx @anthropic/mcp-inspector bun run src/index.ts
```

## Tools

- `get_metadata` - Returns MCP server metadata
- `get_resume` - Returns resume content as Markdown
- `get_bio` - Returns extended biography
- `get_contact` - Returns contact information
- `get_projects` - Returns list of projects
- `get_skills` - Returns skills overview
- `get_available_resources` - Lists available resource identifiers
- `search_info` - Searches across all resources

## Resources

- `config://version` - MCP version
- `config://resume-version` - Resume last updated date
- `larkin://resume` - Resume (Markdown)
- `larkin://resume.pdf` - Resume (PDF)
- `larkin://bio` - Biography
- `larkin://projects` - Projects
- `larkin://contact` - Contact info
- `larkin://skills` - Skills
