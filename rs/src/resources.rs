pub const RESUME: &str = include_str!("resources/content/resume/larkin_resume.md");
pub const BIO: &str = include_str!("resources/content/bio.md");
pub const CONTACT: &str = include_str!("resources/content/contact.md");
pub const PROJECTS: &str = include_str!("resources/content/projects.md");
pub const SKILLS: &str = include_str!("resources/content/skills.md");
pub const WORK: &str = include_str!("resources/content/work.md");
pub const TENNIS: &str = include_str!("resources/content/tennis.md");

pub const RESOURCE_CATEGORIES: &[&str] = &[
    "resume", "bio", "projects", "contact", "skills", "work", "tennis",
];

pub fn get_resource(name: &str) -> Option<&'static str> {
    match name {
        "resume" => Some(RESUME),
        "bio" => Some(BIO),
        "contact" => Some(CONTACT),
        "projects" => Some(PROJECTS),
        "skills" => Some(SKILLS),
        "work" => Some(WORK),
        "tennis" => Some(TENNIS),
        _ => None,
    }
}

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
