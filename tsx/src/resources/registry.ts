import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  MCP_VERSION,
  RESOURCES_DIR,
  RESUME_DATE_VERSION,
} from "../constants.js";
import { loadResource } from "../util/resources.js";
import { resolve } from "path";

export function registerResources(server: McpServer): void {
  server.registerResource(
    "version",
    "config://version",
    {
      title: "Get version",
      description: "MCP server version",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [{ uri: uri.href, text: MCP_VERSION, mimeType: "text/plain" }],
    }),
  );

  server.registerResource(
    "resume-version",
    "config://resume-version",
    {
      title: "Get resume version",
      description: "Resume last updated date",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [
        {
          uri: uri.href,
          text: RESUME_DATE_VERSION,
          mimeType: "text/plain",
        },
      ],
    }),
  );

  server.registerResource(
    "resume",
    "larkin://resume",
    {
      title: "Get resume",
      description: "John Larkin's resume in Markdown format",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("resume");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.registerResource(
    "resume-pdf",
    "larkin://resume.pdf",
    {
      title: "Get resume pdf",
      description: "John Larkin's resume in PDF format",
      mimeType: "application/pdf",
    },
    async (uri) => {
      const pdfPath = resolve(RESOURCES_DIR, "resume/larkin_resume.pdf");
      const file = Bun.file(pdfPath);
      const buffer = await file.arrayBuffer();
      const base64 = Buffer.from(buffer).toString("base64");
      return {
        contents: [
          {
            uri: uri.href,
            blob: base64,
            mimeType: "application/pdf",
          },
        ],
      };
    },
  );

  server.registerResource(
    "bio",
    "larkin://bio",
    {
      title: "Get bio",
      description: "John Larkin's extended biography",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("bio");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.registerResource(
    "projects",
    "larkin://projects",
    {
      title: "Get projects",
      description: "Curated list of John's noteworthy projects",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("projects");
      return {
        contents: [
          {
            uri: uri.href,
            text: content,
            mimeType: "text/markdown",
          },
        ],
      };
    },
  );

  server.registerResource(
    "contact",
    "larkin://contact",
    {
      title: "Get contact",
      description: "Contact information for John Larkin",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("contact");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.registerResource(
    "skills",
    "larkin://skills",
    {
      title: "Get skills",
      description: "John Larkin's skills overview",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("skills");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.registerResource(
    "work",
    "larkin://work",
    {
      title: "Get work",
      description: "John Larkin's work experience and employment history",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("work");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.registerResource(
    "tennis",
    "larkin://tennis",
    {
      title: "Get tennis info",
      description: "John Larkin's collegiate tennis career information",
      mimeType: "text/markdown",
    },
    async (uri) => {
      const content = await loadResource("tennis");
      return {
        contents: [
          { uri: uri.href, text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );
}
