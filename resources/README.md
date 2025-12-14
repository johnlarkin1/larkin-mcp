# Shared Resources

This directory contains shared resources for all larkin-mcp implementations (Python, TypeScript, Rust).

## Directory Structure

```
resources/
├── content/                 # Source of truth for all content files
│   ├── resume/
│   │   ├── larkin_resume.md
│   │   └── larkin_resume.pdf
│   ├── bio.md
│   ├── contact.md
│   ├── projects.md
│   ├── skills.md
│   └── work.md
├── schemas/                 # JSON schemas for cross-language consistency
│   └── resource.schema.json
├── test-fixtures/           # Shared test data and contracts
│   └── tool-contracts.json
└── README.md
```

## Content Files

The `content/` directory is the **single source of truth** for all portfolio content. Each language implementation copies these files to its own location at build time.

### Resource Categories

| Resource | File | Description |
|----------|------|-------------|
| resume | resume/larkin_resume.md | Full professional resume in Markdown |
| resume.pdf | resume/larkin_resume.pdf | Resume in PDF format |
| bio | bio.md | Extended biography |
| contact | contact.md | Contact information |
| projects | projects.md | Curated list of projects |
| skills | skills.md | Skills and technologies |
| work | work.md | Detailed work experience |

## Build-Time Copy

Run the copy script to sync resources to all implementations:

```bash
python scripts/copy-resources.py
```

This copies `resources/content/` to:
- `py/src/resources/content/`
- `tsx/src/resources/content/`
- `rs/src/resources/content/`

**Note:** The implementation-specific `content/` directories are gitignored since they're generated.

## Schemas

The `schemas/` directory contains JSON schemas that define the expected structure of tool inputs and outputs. All implementations should validate against these schemas.

### resource.schema.json

Defines schemas for:
- `metadata` - Server metadata structure
- `healthCheck` - Health check response
- `projectDetails` - Structured project information
- `searchResult` - Semantic search result structure

## Test Fixtures

The `test-fixtures/` directory contains test data and contracts that all implementations must satisfy.

### tool-contracts.json

Defines expected behavior for each MCP tool:
- Input parameters
- Output structure
- Assertions that must pass

Use these contracts to:
1. Guide implementation in new languages
2. Verify consistency across implementations
3. Write integration tests

## Development Workflow

1. **Edit content** in `resources/content/` (not in implementation directories)
2. **Run copy script** to sync to implementations
3. **Test changes** in your preferred implementation
4. **Verify contracts** pass for all implementations

## Adding New Resources

1. Add the content file to `resources/content/`
2. Update `RESOURCES_CATEGORIES` in each implementation's constants
3. Add tool and resource registrations
4. Update `resource.schema.json` if needed
5. Add test cases to `tool-contracts.json`
