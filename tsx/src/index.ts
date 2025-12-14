import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { MCP_INSTRUCTIONS, MCP_NAME, MCP_VERSION } from "./constants.js";
import { registerResources } from "./resources/registry.js";
import { registerTools } from "./tools/registry.js";

const server = new McpServer({
  name: MCP_NAME,
  version: MCP_VERSION,
});

registerTools(server);
registerResources(server);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`${MCP_NAME} MCP Server running on stdio`);
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
