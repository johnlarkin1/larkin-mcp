import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerPrompts(server: McpServer): void {
  server.prompt(
    "summarize_for_role",
    "Generate a tailored summary of John's background for a specific job role.",
    {
      role: z.string().describe("The job title or role to summarize for (e.g., 'Staff Engineer', 'Engineering Manager')"),
    },
    async ({ role }) => {
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Based on John Larkin's background, create a concise 2-3 paragraph summary
highlighting why he would be a strong fit for a ${role} position.

To gather the necessary information, use these tools:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Notable projects demonstrating expertise
- get_skills() - Technical capabilities

Focus on:
1. Relevant experience from work history that aligns with the role
2. Technical skills that match typical ${role} requirements
3. Leadership experience or impact (if applicable)
4. Notable projects that demonstrate relevant capabilities

Keep the summary professional and tailored specifically for a ${role} position.`,
            },
          },
        ],
      };
    }
  );

  server.prompt(
    "compare_to_job",
    "Analyze how John's background aligns with a specific job description.",
    {
      job_description: z.string().describe("The full job description text to compare against"),
    },
    async ({ job_description }) => {
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Analyze John Larkin's fit for the following job description:

---
${job_description}
---

Use these tools to gather information:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_skills() - Technical capabilities
- get_projects() - Project portfolio

Please provide:
1. **Matching Qualifications**: Skills and experience that directly match job requirements
2. **Relevant Projects**: Projects that demonstrate applicable expertise
3. **Potential Gaps**: Areas where additional context or experience might be needed
4. **Unique Strengths**: Standout qualities that differentiate John from other candidates
5. **Suggested Talking Points**: Key accomplishments to highlight in an interview

Format the analysis in clear sections with bullet points for easy scanning.`,
            },
          },
        ],
      };
    }
  );

  server.prompt(
    "interview_prep",
    "Generate likely interview questions and talking points for a role.",
    {
      role: z.string().describe("The job title/role being interviewed for"),
      company: z.string().optional().describe("Optional company name for more targeted prep"),
    },
    async ({ role, company }) => {
      const companyContext = company ? ` at ${company}` : "";
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Help prepare John Larkin for an interview for a ${role} position${companyContext}.

Use these tools to understand John's background:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Project portfolio
- get_skills() - Technical capabilities

Generate:

## Likely Interview Questions
Based on John's experience and typical ${role} interviews, list 8-10 questions he's likely to face, categorized by:
- Technical questions
- Behavioral/situational questions
- Experience-based questions
- Questions about specific projects

## Recommended Answers/Talking Points
For each question, suggest specific examples from John's background that would make strong answers.

## Questions John Should Ask
Suggest thoughtful questions John could ask the interviewer about the ${role} role${companyContext}.

## Potential Weak Points to Prepare For
Identify any gaps or areas where John might need to prepare additional context.`,
            },
          },
        ],
      };
    }
  );

  server.prompt(
    "project_deep_dive",
    "Get detailed information about a specific project.",
    {
      project_name: z.string().describe("The name of the project to explore"),
    },
    async ({ project_name }) => {
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Provide a comprehensive overview of John Larkin's "${project_name}" project.

Use get_projects() and get_resume() to gather information.

Please include:
1. **Project Overview**: What the project does and its purpose
2. **Tech Stack**: Technologies and tools used
3. **Key Features**: Main capabilities and functionality
4. **Challenges & Solutions**: Technical challenges overcome
5. **Impact & Results**: Outcomes and metrics (if available)
6. **Relevance**: How this project demonstrates transferable skills

If the project isn't found, list available projects from get_projects() and suggest alternatives.`,
            },
          },
        ],
      };
    }
  );
}
