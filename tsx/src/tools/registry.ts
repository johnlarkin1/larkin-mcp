import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { MCP_VERSION, MCP_WEBSITE_URL, RESUME_DATE_VERSION, RESOURCES_CATEGORIES } from "../constants.js";
import type { Metadata, HealthCheckResponse, ResourceStatus } from "../types/tool.js";
import { listResources, loadResource, searchResources } from "../util/resources.js";

export function registerTools(server: McpServer): void {
  server.tool("get_metadata", "Return metadata describing the MCP server and resume freshness.", {}, async () => {
    const metadata: Metadata = {
      mcp_version: MCP_VERSION,
      mcp_website: MCP_WEBSITE_URL,
      resume_last_updated: RESUME_DATE_VERSION,
    };
    return {
      content: [{ type: "text", text: JSON.stringify(metadata, null, 2) }],
    };
  });

  server.tool("get_resume", "Return the full resume content as Markdown.", {}, async () => {
    const content = await loadResource("resume");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_bio", "Return the extended biography content.", {}, async () => {
    const content = await loadResource("bio");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_contact", "Return contact instructions for reaching John.", {}, async () => {
    const content = await loadResource("contact");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_projects", "Return the curated list of noteworthy projects.", {}, async () => {
    const content = await loadResource("projects");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_skills", "Return the current skills overview.", {}, async () => {
    const content = await loadResource("skills");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_available_resources", "Return identifiers for all available content resources.", {}, async () => {
    const resources = listResources();
    return {
      content: [{ type: "text", text: JSON.stringify(resources) }],
    };
  });

  server.tool(
    "search_info",
    "Return a formatted summary of resources matching the query string.",
    {
      query: z.string().describe("The search query to find in resources"),
    },
    async ({ query }) => {
      const results = await searchResources(query);

      if (Object.keys(results).length === 0) {
        return {
          content: [{ type: "text", text: `No matches found for '${query}'` }],
        };
      }

      const output: string[] = [];
      for (const [resource, lines] of Object.entries(results)) {
        output.push(`## ${resource.charAt(0).toUpperCase() + resource.slice(1)}`);
        for (const line of lines.slice(0, 5)) {
          output.push(`  - ${line.trim()}`);
        }
      }

      return {
        content: [{ type: "text", text: output.join("\n") }],
      };
    }
  );

  server.tool("get_work", "Return detailed work experience and employment history.", {}, async () => {
    const content = await loadResource("work");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("get_tennis_info", "Return collegiate tennis career information including awards and match records.", {}, async () => {
    const content = await loadResource("tennis");
    return {
      content: [{ type: "text", text: content }],
    };
  });

  server.tool("health_check", "Return server health status and resource availability.", {}, async () => {
    const resourcesStatus: Record<string, ResourceStatus> = {};

    for (const resource of RESOURCES_CATEGORIES) {
      const content = await loadResource(resource);
      const isAvailable = !content.startsWith("Resource '") && !content.startsWith("Error");
      resourcesStatus[resource] = {
        available: isAvailable,
        size_bytes: isAvailable ? Buffer.byteLength(content, "utf-8") : 0,
      };
    }

    const response: HealthCheckResponse = {
      status: "healthy",
      version: MCP_VERSION,
      resources: resourcesStatus,
    };

    return {
      content: [{ type: "text", text: JSON.stringify(response, null, 2) }],
    };
  });
}
