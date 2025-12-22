import { existsSync } from "fs";
import { resolve } from "path";
import {
  RESOURCES_CATEGORIES,
  RESOURCES_DIR,
  RESUME_MD_PATH,
} from "../constants.js";

export async function loadResource(name: string): Promise<string> {
  const path =
    name === "resume" ? RESUME_MD_PATH : resolve(RESOURCES_DIR, `${name}.md`);

  const file = Bun.file(path);
  if (!(await file.exists())) {
    return `Resource '${name}' not found. Please create ${path}`;
  }

  return await file.text();
}

export function listResources(): string[] {
  const resources: string[] = [];

  if (existsSync(RESUME_MD_PATH)) {
    resources.push("resume");
  }

  for (const category of RESOURCES_CATEGORIES) {
    const path = resolve(RESOURCES_DIR, `${category}.md`);
    if (existsSync(path)) {
      resources.push(category);
    }
  }

  return resources;
}

export async function searchResources(
  query: string,
): Promise<Record<string, string[]>> {
  const results: Record<string, string[]> = {};
  const queryLower = query.toLowerCase();

  for (const resourceName of listResources()) {
    const content = await loadResource(resourceName);
    const matchingLines = content
      .split("\n")
      .filter((line) => line.toLowerCase().includes(queryLower));

    if (matchingLines.length > 0) {
      results[resourceName] = matchingLines;
    }
  }

  return results;
}
