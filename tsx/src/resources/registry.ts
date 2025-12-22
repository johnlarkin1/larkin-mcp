import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  MCP_VERSION,
  RESOURCES_DIR,
  RESUME_DATE_VERSION,
} from "../constants.js";
import { loadResource } from "../util/resources.js";
import { resolve } from "path";

export function registerResources(server: McpServer): void {
  server.resource("config://version", "MCP server version", async () => ({
    contents: [
      { uri: "config://version", text: MCP_VERSION, mimeType: "text/plain" },
    ],
  }));

  server.resource(
    "config://resume-version",
    "Resume last updated date",
    async () => ({
      contents: [
        {
          uri: "config://resume-version",
          text: RESUME_DATE_VERSION,
          mimeType: "text/plain",
        },
      ],
    }),
  );

  server.resource(
    "larkin://resume",
    "John Larkin's resume in Markdown format",
    async () => {
      const content = await loadResource("resume");
      return {
        contents: [
          { uri: "larkin://resume", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.resource(
    "larkin://resume.pdf",
    "John Larkin's resume in PDF format",
    async () => {
      const pdfPath = resolve(RESOURCES_DIR, "resume/larkin_resume.pdf");
      const file = Bun.file(pdfPath);
      const buffer = await file.arrayBuffer();
      const base64 = Buffer.from(buffer).toString("base64");
      return {
        contents: [
          {
            uri: "larkin://resume.pdf",
            blob: base64,
            mimeType: "application/pdf",
          },
        ],
      };
    },
  );

  server.resource(
    "larkin://bio",
    "John Larkin's extended biography",
    async () => {
      const content = await loadResource("bio");
      return {
        contents: [
          { uri: "larkin://bio", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.resource(
    "larkin://projects",
    "Curated list of John's noteworthy projects",
    async () => {
      const content = await loadResource("projects");
      return {
        contents: [
          {
            uri: "larkin://projects",
            text: content,
            mimeType: "text/markdown",
          },
        ],
      };
    },
  );

  server.resource(
    "larkin://contact",
    "Contact information for John Larkin",
    async () => {
      const content = await loadResource("contact");
      return {
        contents: [
          { uri: "larkin://contact", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.resource(
    "larkin://skills",
    "John Larkin's skills overview",
    async () => {
      const content = await loadResource("skills");
      return {
        contents: [
          { uri: "larkin://skills", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.resource(
    "larkin://work",
    "John Larkin's work experience and employment history",
    async () => {
      const content = await loadResource("work");
      return {
        contents: [
          { uri: "larkin://work", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );

  server.resource(
    "larkin://tennis",
    "John Larkin's collegiate tennis career information",
    async () => {
      const content = await loadResource("tennis");
      return {
        contents: [
          { uri: "larkin://tennis", text: content, mimeType: "text/markdown" },
        ],
      };
    },
  );
}
