import { describe, expect, test } from "bun:test";
import { loadResource, listResources, searchResources } from "../src/util/resources";

describe("loadResource", () => {
  test("load resume", async () => {
    const content = await loadResource("resume");
    expect(content).toContain("John Larkin");
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load bio", async () => {
    const content = await loadResource("bio");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load skills", async () => {
    const content = await loadResource("skills");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load projects", async () => {
    const content = await loadResource("projects");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load contact", async () => {
    const content = await loadResource("contact");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load work", async () => {
    const content = await loadResource("work");
    expect(content).toBeTruthy();
    expect(content).not.toMatch(/^Resource '/);
  });

  test("load nonexistent resource returns error message", async () => {
    const content = await loadResource("nonexistent_resource_xyz");
    expect(content).toMatch(/^Resource '/);
    expect(content.toLowerCase()).toContain("not found");
  });
});

describe("listResources", () => {
  test("returns array", () => {
    const resources = listResources();
    expect(Array.isArray(resources)).toBe(true);
  });

  test("contains expected resources", () => {
    const resources = listResources();
    const expected = ["resume", "bio", "skills", "projects", "contact", "work"];
    for (const resource of expected) {
      expect(resources).toContain(resource);
    }
  });

  test("no empty entries", () => {
    const resources = listResources();
    for (const resource of resources) {
      expect(resource).toBeTruthy();
    }
  });
});

describe("searchResources", () => {
  test("finds matches", async () => {
    const results = await searchResources("Python");
    expect(Object.keys(results).length).toBeGreaterThan(0);
  });

  test("case insensitive", async () => {
    const resultsLower = await searchResources("python");
    const resultsUpper = await searchResources("PYTHON");
    expect(Object.keys(resultsLower).length).toBeGreaterThan(0);
    expect(Object.keys(resultsUpper).length).toBeGreaterThan(0);
  });

  test("no matches returns empty object", async () => {
    const results = await searchResources("xyznonexistentterm123");
    expect(Object.keys(results).length).toBe(0);
  });

  test("returns dictionary with string arrays", async () => {
    const results = await searchResources("Python");
    expect(typeof results).toBe("object");
    for (const [resource, lines] of Object.entries(results)) {
      expect(typeof resource).toBe("string");
      expect(Array.isArray(lines)).toBe(true);
      for (const line of lines) {
        expect(typeof line).toBe("string");
      }
    }
  });
});
