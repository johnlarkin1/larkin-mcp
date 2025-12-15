import { describe, expect, test } from "bun:test";
import { readFileSync } from "fs";
import { resolve } from "path";
import { MCP_VERSION, RESOURCES_CATEGORIES, RESUME_DATE_VERSION, RESOURCES_DIR } from "../src/constants";
import { loadResource, listResources, searchResources } from "../src/util/resources";

// Load test fixtures
const contractsPath = resolve(__dirname, "../../resources/test-fixtures/tool-contracts.json");
const schemaPath = resolve(__dirname, "../../resources/schemas/resource.schema.json");
const toolContracts = JSON.parse(readFileSync(contractsPath, "utf-8"));
const resourceSchema = JSON.parse(readFileSync(schemaPath, "utf-8"));

// TypeScript tools list (should match Python)
const TYPESCRIPT_TOOLS = new Set([
  "get_metadata",
  "get_resume",
  "get_bio",
  "get_contact",
  "get_projects",
  "get_skills",
  "get_work",
  "get_available_resources",
  "search_info",
  "health_check",
]);

// TypeScript resources list
const TYPESCRIPT_RESOURCES = new Set([
  "config://version",
  "config://resume-version",
  "larkin://resume",
  "larkin://resume.pdf",
  "larkin://bio",
  "larkin://projects",
  "larkin://contact",
  "larkin://skills",
  "larkin://work",
]);

describe("Tool Contract Sync", () => {
  test("all contract tools implemented", () => {
    const contractTools = new Set(Object.keys(toolContracts.tools));
    const missing = [...contractTools].filter((t) => !TYPESCRIPT_TOOLS.has(t));
    expect(missing).toEqual([]);
  });

  test("no extra tools in TypeScript", () => {
    const contractTools = new Set(Object.keys(toolContracts.tools));
    const extra = [...TYPESCRIPT_TOOLS].filter((t) => !contractTools.has(t));
    expect(extra).toEqual([]);
  });

  test("tools match exactly", () => {
    const contractTools = new Set(Object.keys(toolContracts.tools));
    expect(TYPESCRIPT_TOOLS).toEqual(contractTools);
  });
});

describe("Resource Contract Sync", () => {
  test("all contract resources implemented", () => {
    const contractResources = new Set(Object.keys(toolContracts.resources));
    const missing = [...contractResources].filter((r) => !TYPESCRIPT_RESOURCES.has(r));
    expect(missing).toEqual([]);
  });

  test("no extra resources in TypeScript", () => {
    const contractResources = new Set(Object.keys(toolContracts.resources));
    const extra = [...TYPESCRIPT_RESOURCES].filter((r) => !contractResources.has(r));
    expect(extra).toEqual([]);
  });

  test("resources match exactly", () => {
    const contractResources = new Set(Object.keys(toolContracts.resources));
    expect(TYPESCRIPT_RESOURCES).toEqual(contractResources);
  });
});

describe("Resource Categories Sync", () => {
  test("categories match schema", () => {
    const schemaCategories = new Set(resourceSchema.properties.resourceCategories.items.enum);
    const tsCategories = new Set(RESOURCES_CATEGORIES);
    expect(tsCategories).toEqual(schemaCategories);
  });
});

describe("Tool Output Contracts", () => {
  test("get_metadata output", () => {
    const result = {
      mcp_version: MCP_VERSION,
      mcp_website: "https://johnlarkin1.github.io/2025/larkin-mcp",
      resume_last_updated: RESUME_DATE_VERSION,
    };

    const contract = toolContracts.tools.get_metadata.expectedOutput;

    for (const field of contract.requiredFields) {
      expect(result).toHaveProperty(field);
    }

    expect(result.mcp_version).toMatch(/^\d+\.\d+\.\d+$/);
    expect(result.resume_last_updated).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  test("get_resume output", async () => {
    const content = await loadResource("resume");
    expect(content).toContain("John Larkin");
    expect(content).not.toMatch(/^Resource '/);
  });

  test("get_available_resources output", () => {
    const resources = listResources();
    const contract = toolContracts.tools.get_available_resources.expectedOutput;

    for (const assertion of contract.assertions) {
      if (assertion.startsWith("Contains '")) {
        const expected = assertion.split("'")[1];
        expect(resources).toContain(expected);
      }
    }

    for (const item of resources) {
      expect(typeof item).toBe("string");
    }
  });

  test("search_info with matches", async () => {
    const results = await searchResources("Python");

    if (Object.keys(results).length > 0) {
      const output: string[] = [];
      for (const [resource, lines] of Object.entries(results)) {
        output.push(`## ${resource.charAt(0).toUpperCase() + resource.slice(1)}`);
        for (const line of (lines as string[]).slice(0, 5)) {
          output.push(`  - ${line.trim()}`);
        }
      }
      const formatted = output.join("\n");
      expect(formatted).toContain("##");
    }
  });

  test("search_info no matches", async () => {
    const results = await searchResources("xyznonexistent123");
    expect(Object.keys(results).length).toBe(0);
  });

  test("health_check output", async () => {
    const resourcesStatus: Record<string, { available: boolean; size_bytes: number }> = {};

    for (const resource of RESOURCES_CATEGORIES) {
      const content = await loadResource(resource);
      const isAvailable = !content.startsWith("Resource '") && !content.startsWith("Error");
      resourcesStatus[resource] = {
        available: isAvailable,
        size_bytes: isAvailable ? Buffer.byteLength(content, "utf-8") : 0,
      };
    }

    const result = {
      status: "healthy" as const,
      version: MCP_VERSION,
      resources: resourcesStatus,
    };

    // Check required fields
    const contract = toolContracts.tools.health_check.expectedOutput;
    for (const field of contract.requiredFields) {
      expect(result).toHaveProperty(field);
    }

    // Check status enum
    const schemaStatuses = resourceSchema.definitions.healthCheck.properties.status.enum;
    expect(schemaStatuses).toContain(result.status);

    // Check version semver
    expect(result.version).toMatch(/^\d+\.\d+\.\d+$/);

    // Check each resource has required fields
    for (const [name, status] of Object.entries(result.resources)) {
      expect(typeof status.available).toBe("boolean");
      expect(typeof status.size_bytes).toBe("number");
      expect(status.size_bytes).toBeGreaterThanOrEqual(0);
    }
  });
});

describe("Resource Output Contracts", () => {
  test("config://version matches semver", () => {
    expect(MCP_VERSION).toMatch(/^\d+\.\d+\.\d+$/);
  });

  test("config://resume-version matches date pattern", () => {
    expect(RESUME_DATE_VERSION).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  test("larkin://resume returns expected content", async () => {
    const content = await loadResource("resume");
    expect(content).toBeTruthy();
    expect(content).toContain("John Larkin");
  });

  test("larkin://resume.pdf exists and is valid", () => {
    const pdfPath = resolve(RESOURCES_DIR, "resume/larkin_resume.pdf");
    const file = Bun.file(pdfPath);
    expect(file.size).toBeGreaterThan(0);
  });

  test("larkin://bio returns non-empty content", async () => {
    const content = await loadResource("bio");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("larkin://projects returns non-empty content", async () => {
    const content = await loadResource("projects");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("larkin://contact returns non-empty content", async () => {
    const content = await loadResource("contact");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("larkin://skills returns non-empty content", async () => {
    const content = await loadResource("skills");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("larkin://work returns non-empty content", async () => {
    const content = await loadResource("work");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });
});
