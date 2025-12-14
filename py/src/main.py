import logging

from mcp.server.fastmcp import FastMCP

from src.constants import (
    MCP_INSTRUCTIONS,
    MCP_NAME,
    MCP_WEBSITE_URL,
)
from src.prompts.registry import register_prompts
from src.resources.registry import register_resources
from src.tools.registry import register_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(MCP_NAME)


mcp = FastMCP(
    name=MCP_NAME,
    instructions=MCP_INSTRUCTIONS,
    website_url=MCP_WEBSITE_URL,
)

register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
