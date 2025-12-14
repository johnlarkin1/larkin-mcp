import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// MCP General
export const MCP_NAME = "larkin-mcp";
export const MCP_VERSION = "0.1.0";
export const MCP_INSTRUCTIONS =
  "This server provides information about John Larkin " +
  "(github profile: johnlarkin1, site: johnlarkin1.github.io) and " +
  "allows helpful tooling for more info";
export const MCP_WEBSITE_URL = "https://johnlarkin1.github.io/2025/larkin-mcp";

// Resources
const __dirname = dirname(fileURLToPath(import.meta.url));
export const RESOURCES_DIR = resolve(__dirname, "./resources/content");
export const RESOURCES_CATEGORIES = ["resume", "bio", "projects", "contact", "skills", "work"];

// Resume
export const RESUME_DATE_VERSION = "2025-12-14";
export const RESUME_PDF_PATH = resolve(RESOURCES_DIR, "resume/larkin_resume.pdf");
export const RESUME_MD_PATH = resolve(RESOURCES_DIR, "resume/larkin_resume.md");
