"""Register MCP prompts for guiding LLM interactions.

Note... I had CC fire up these prompts because it's a lot of writing. But you get the gist.
"""


def register_prompts(mcp):
    """Register MCP prompts that guide LLM interactions with John Larkin's portfolio.

    Prompts are pre-defined templates that help LLMs understand how to use
    the available tools effectively for common use cases.
    """

    @mcp.prompt()
    def summarize_for_role(role: str) -> str:
        """Generate a tailored summary of John's background for a specific job role.

        Args:
            role: The job title or role to summarize for (e.g., "Staff Engineer", "Engineering Manager")
        """
        return f"""Based on John Larkin's background, create a concise 2-3 paragraph summary
highlighting why he would be a strong fit for a {role} position.

To gather the necessary information, use these tools:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Notable projects demonstrating expertise
- get_skills() - Technical capabilities

Focus on:
1. Relevant experience from work history that aligns with the role
2. Technical skills that match typical {role} requirements
3. Leadership experience or impact (if applicable)
4. Notable projects that demonstrate relevant capabilities

Keep the summary professional and tailored specifically for a {role} position."""

    @mcp.prompt()
    def compare_to_job(job_description: str) -> str:
        """Analyze how John's background aligns with a specific job description.

        Args:
            job_description: The full job description text to compare against
        """
        return f"""Analyze John Larkin's fit for the following job description:

---
{job_description}
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

Format the analysis in clear sections with bullet points for easy scanning."""

    @mcp.prompt()
    def interview_prep(role: str, company: str = "") -> str:
        """Generate likely interview questions and talking points for a role.

        Args:
            role: The job title/role being interviewed for
            company: Optional company name for more targeted prep
        """
        company_context = f" at {company}" if company else ""
        return f"""Help prepare John Larkin for an interview for a {role} position{company_context}.

Use these tools to understand John's background:
- get_resume() - Full professional background
- get_work() - Detailed employment history
- get_projects() - Project portfolio
- get_skills() - Technical capabilities

Generate:

## Likely Interview Questions
Based on John's experience and typical {role} interviews, list 8-10 questions he's likely to face, categorized by:
- Technical questions
- Behavioral/situational questions
- Experience-based questions
- Questions about specific projects

## Recommended Answers/Talking Points
For each question, suggest specific examples from John's background that would make strong answers.

## Questions John Should Ask
Suggest thoughtful questions John could ask the interviewer about the {role} role{company_context}.

## Potential Weak Points to Prepare For
Identify any gaps or areas where John might need to prepare additional context."""

    @mcp.prompt()
    def project_deep_dive(project_name: str) -> str:
        """Get detailed information about a specific project.

        Args:
            project_name: The name of the project to explore
        """
        return f"""Provide a comprehensive overview of John Larkin's "{project_name}" project.

Use get_projects() and get_resume() to gather information.

Please include:
1. **Project Overview**: What the project does and its purpose
2. **Tech Stack**: Technologies and tools used
3. **Key Features**: Main capabilities and functionality
4. **Challenges & Solutions**: Technical challenges overcome
5. **Impact & Results**: Outcomes and metrics (if available)
6. **Relevance**: How this project demonstrates transferable skills

If the project isn't found, list available projects from get_projects() and suggest alternatives."""
