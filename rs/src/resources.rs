//! Embedded content resources compiled into the binary.
//!
//! Uses `include_str!` to embed markdown files at compile time,
//! producing a single self-contained binary.

/// Resume content in markdown format
pub const RESUME: &str = include_str!("resources/content/resume/larkin_resume.md");

/// Extended biography
pub const BIO: &str = include_str!("resources/content/bio.md");

/// Contact information
pub const CONTACT: &str = include_str!("resources/content/contact.md");

/// Notable projects
pub const PROJECTS: &str = include_str!("resources/content/projects.md");

/// Skills overview
pub const SKILLS: &str = include_str!("resources/content/skills.md");

/// Work experience and employment history
pub const WORK: &str = include_str!("resources/content/work.md");

pub const TENNIS: &str = include_str!("resources/content/tennis.md");

/// All available resource categories
pub const RESOURCE_CATEGORIES: &[&str] =
    &["resume", "bio", "projects", "contact", "skills", "work"];

/// Get content by resource name
pub fn get_resource(name: &str) -> Option<&'static str> {
    match name {
        "resume" => Some(RESUME),
        "bio" => Some(BIO),
        "contact" => Some(CONTACT),
        "projects" => Some(PROJECTS),
        "skills" => Some(SKILLS),
        "work" => Some(WORK),
        // "tennis" => Some(TENNIS),
        _ => None,
    }
}

/// Search all resources for lines containing the query string (case-insensitive)
pub fn search_resources(query: &str) -> Vec<(&'static str, Vec<&'static str>)> {
    let query_lower = query.to_lowercase();
    let mut results = Vec::new();

    for &category in RESOURCE_CATEGORIES {
        if let Some(content) = get_resource(category) {
            let matching_lines: Vec<&str> = content
                .lines()
                .filter(|line| line.to_lowercase().contains(&query_lower))
                .take(5)
                .collect();

            if !matching_lines.is_empty() {
                results.push((category, matching_lines));
            }
        }
    }

    results
}
