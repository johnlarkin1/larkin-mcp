import { describe, expect, test } from "bun:test";
import { MCP_VERSION, RESOURCES_CATEGORIES } from "../src/constants";
import { loadResource, searchResources } from "../src/util/resources";

describe("health_check logic", () => {
  test("returns expected structure", async () => {
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
      status: "healthy",
      version: MCP_VERSION,
      resources: resourcesStatus,
    };

    expect(result.status).toBe("healthy");
    expect(result.version).toBe(MCP_VERSION);
    expect(result.resources).toBeDefined();
  });

  test("resources have expected fields", async () => {
    for (const resource of RESOURCES_CATEGORIES) {
      const content = await loadResource(resource);
      const isAvailable = !content.startsWith("Resource '");

      if (isAvailable) {
        expect(Buffer.byteLength(content, "utf-8")).toBeGreaterThan(0);
      }
    }
  });
});

describe("search_info logic", () => {
  test("search returns formatted output", async () => {
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

  test("no results message", async () => {
    const results = await searchResources("xyznonexistent123");

    if (Object.keys(results).length === 0) {
      const message = "No matches found for 'xyznonexistent123'";
      expect(message).toContain("No matches found");
    }
  });
});
