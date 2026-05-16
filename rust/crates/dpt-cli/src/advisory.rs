//! Aggressive prompt-keyword -> sub-droid advisory.
//!
//! Activated by `UserPromptSubmit`. Returns a short `additionalContext`
//! block listing 1-3 relevant sub-droids when the prompt matches known
//! keyword patterns. The advisory is purely informational - the orchestrator
//! decides whether to act on the hint via `Task()`.
//!
//! "Aggressive" means we surface a hint on most non-trivial prompts. The
//! signal-to-noise tradeoff was chosen explicitly during scope-C design;
//! the orchestrator can ignore the block when it is irrelevant.

const MAX_SUGGESTIONS: usize = 3;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Suggestion {
    pub trigger: &'static str,
    pub droids: &'static [&'static str],
    pub skill: Option<&'static str>,
    pub reason: &'static str,
}

const RULES: &[Rule] = &[
    Rule {
        keywords: &["audit", "review", "code review", "readiness"],
        suggestion: Suggestion {
            trigger: "audit/review",
            droids: &["dpt-sec", "dpt-perf", "dpt-review", "dpt-lead", "dpt-qa"],
            skill: Some("dpt-audit"),
            reason: "parallel audit lanes - read-only, safe to batch [P]",
        },
    },
    Rule {
        keywords: &[
            "bug",
            "fix",
            "regression",
            "broken",
            "failing test",
            "stack trace",
        ],
        suggestion: Suggestion {
            trigger: "bug/fix",
            droids: &["dpt-dev", "dpt-qa"],
            skill: Some("dpt-bugfix"),
            reason: "scoped fix workflow - skip heavyweight PRD/architecture",
        },
    },
    Rule {
        keywords: &[
            "feature",
            "build a",
            "build me",
            "implement",
            "add support",
            "add a",
            "new module",
            "fullstack",
        ],
        suggestion: Suggestion {
            trigger: "feature/build",
            droids: &["dpt-product", "dpt-arch", "dpt-scrum", "dpt-dev"],
            skill: Some("dpt-fullstack"),
            reason: "non-trivial multi-component feature - run wave plan",
        },
    },
    Rule {
        keywords: &[
            "research",
            "best practice",
            "best practices",
            "find docs",
            "compare libraries",
            "official docs",
        ],
        suggestion: Suggestion {
            trigger: "research",
            droids: &["dpt-research"],
            skill: None,
            reason: "multi-hop research from official sources",
        },
    },
    Rule {
        keywords: &[
            "security",
            "vulnerab",
            "owasp",
            "cve",
            "auth bypass",
            "xss",
            "sqli",
        ],
        suggestion: Suggestion {
            trigger: "security",
            droids: &["dpt-sec"],
            skill: None,
            reason: "OWASP Top 10 / CWE focused review",
        },
    },
    Rule {
        keywords: &[
            "performance",
            "slow",
            "optimi",
            "latency",
            "throughput",
            "memory leak",
        ],
        suggestion: Suggestion {
            trigger: "performance",
            droids: &["dpt-perf"],
            skill: None,
            reason: "measure-before-optimize workflow",
        },
    },
    Rule {
        keywords: &[
            "architect",
            "design",
            "structure",
            "system design",
            "diagram",
        ],
        suggestion: Suggestion {
            trigger: "architecture/design",
            droids: &["dpt-arch"],
            skill: None,
            reason: "writes ARCHITECTURE.md from PRD requirements",
        },
    },
    Rule {
        keywords: &["requirement", "user story", "prd", "scope", "spec out"],
        suggestion: Suggestion {
            trigger: "requirements",
            droids: &["dpt-product"],
            skill: None,
            reason: "writes PRD.md with user stories",
        },
    },
    Rule {
        keywords: &[
            "api", "endpoint", "route", "rest", "graphql", "openapi", "swagger",
        ],
        suggestion: Suggestion {
            trigger: "api",
            droids: &["dpt-api"],
            skill: None,
            reason: "consistent API surface design",
        },
    },
    Rule {
        keywords: &["database", "schema", "migration", "sql", "table", "index"],
        suggestion: Suggestion {
            trigger: "data/schema",
            droids: &["dpt-data"],
            skill: None,
            reason: "schemas, queries, migrations",
        },
    },
    Rule {
        keywords: &["ui", "ux", "accessibility", "a11y", "wcag", "design system"],
        suggestion: Suggestion {
            trigger: "ui/ux",
            droids: &["dpt-ux"],
            skill: None,
            reason: "simple, accessible interfaces",
        },
    },
    Rule {
        keywords: &[
            "deploy",
            "ci/cd",
            "ci pipeline",
            "github action",
            "docker",
            "kubernetes",
            "k8s",
            "terraform",
            "infra",
            "devops",
        ],
        suggestion: Suggestion {
            trigger: "ops/devops",
            droids: &["dpt-ops"],
            skill: None,
            reason: "DevOps, CI/CD, deployment",
        },
    },
    Rule {
        keywords: &["test", "testing", "qa", "verify", "test coverage"],
        suggestion: Suggestion {
            trigger: "qa/test",
            droids: &["dpt-qa"],
            skill: None,
            reason: "tests code and verifies quality",
        },
    },
    Rule {
        keywords: &["solid", "clean code", "principle", "lead review"],
        suggestion: Suggestion {
            trigger: "principles",
            droids: &["dpt-lead"],
            skill: None,
            reason: "SOLID + clean-code review (no security or perf)",
        },
    },
    Rule {
        keywords: &[
            "simpli",
            "refactor",
            "complex",
            "over-engineer",
            "yagni",
            "kiss",
        ],
        suggestion: Suggestion {
            trigger: "simplicity",
            droids: &["dpt-review"],
            skill: None,
            reason: "simplicity advocate, flags over-engineering",
        },
    },
    Rule {
        keywords: &["document", "docstring", "readme", "user guide"],
        suggestion: Suggestion {
            trigger: "docs",
            droids: &["dpt-docs"],
            skill: None,
            reason: "writes clear documentation",
        },
    },
    Rule {
        keywords: &["spelling", "grammar", "proofread", "typos"],
        suggestion: Suggestion {
            trigger: "grammar",
            droids: &["dpt-grammar"],
            skill: None,
            reason: "grammar and clarity check",
        },
    },
    Rule {
        keywords: &[
            "plan",
            "breakdown",
            "stories",
            "wave",
            "task list",
            "scope this",
            "split",
        ],
        suggestion: Suggestion {
            trigger: "planning",
            droids: &["dpt-scrum"],
            skill: None,
            reason: "writes STORIES.md with [P]/[S] waves",
        },
    },
];

struct Rule {
    keywords: &'static [&'static str],
    suggestion: Suggestion,
}

/// Match the prompt against the keyword rules. Returns up to
/// `MAX_SUGGESTIONS` formatted suggestion lines, or `None` when no rule
/// triggered.
pub fn suggest(prompt: &str) -> Option<String> {
    if prompt.trim().is_empty() {
        return None;
    }
    let lower = prompt.to_ascii_lowercase();
    let mut hits: Vec<&Suggestion> = Vec::new();
    for rule in RULES {
        if hits.len() >= MAX_SUGGESTIONS {
            break;
        }
        if rule.keywords.iter().any(|kw| lower.contains(kw)) {
            // Avoid surfacing the same trigger twice if multiple rules share
            // a label (currently none do, but keep the guard cheap).
            if !hits.iter().any(|s| s.trigger == rule.suggestion.trigger) {
                hits.push(&rule.suggestion);
            }
        }
    }
    if hits.is_empty() {
        return None;
    }
    Some(format_advisory(&hits))
}

fn format_advisory(hits: &[&Suggestion]) -> String {
    let mut out =
        String::from("Droidpartment advisory (prompt -> sub-droid hints, advisory only):\n");
    for s in hits {
        let droid_list = s.droids.join(", ");
        if let Some(skill) = s.skill {
            out.push_str(&format!(
                "  - {} -> Skill('{}') or Task in [{}] ({})\n",
                s.trigger, skill, droid_list, s.reason
            ));
        } else {
            out.push_str(&format!(
                "  - {} -> Task('{}') ({})\n",
                s.trigger, droid_list, s.reason
            ));
        }
    }
    out.push_str(
        "These are hints, not orders. Skip the advisory when it doesn't fit; \
         the orchestrator decides whether to delegate via Task().",
    );
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_prompt_returns_none() {
        assert!(suggest("").is_none());
        assert!(suggest("   ").is_none());
    }

    #[test]
    fn matches_audit_keyword() {
        let s = suggest("can you audit the auth module?").unwrap();
        assert!(s.contains("audit/review"));
        assert!(s.contains("dpt-sec"));
        assert!(s.contains("dpt-audit"));
    }

    #[test]
    fn matches_bugfix_keyword() {
        let s = suggest("there's a regression in the login flow, please fix").unwrap();
        assert!(s.contains("bug/fix"));
        assert!(s.contains("dpt-bugfix"));
    }

    #[test]
    fn matches_feature_implementation() {
        let s = suggest("implement a feature for password reset").unwrap();
        assert!(s.contains("feature/build") || s.contains("feature"));
        assert!(s.contains("dpt-fullstack") || s.contains("dpt-dev"));
    }

    #[test]
    fn matches_security_keyword_specifically() {
        let s = suggest("check this code for OWASP Top 10 issues").unwrap();
        assert!(s.contains("security"));
        assert!(s.contains("dpt-sec"));
    }

    #[test]
    fn caps_at_three_suggestions() {
        let s = suggest("audit the security and performance of this api endpoint").unwrap();
        let count = s.matches("\n  - ").count();
        assert!(count <= MAX_SUGGESTIONS, "got {count}");
    }

    #[test]
    fn unrelated_prompt_returns_none() {
        assert!(suggest("hello there").is_none());
        assert!(suggest("what time is it").is_none());
    }

    #[test]
    fn case_insensitive() {
        let s = suggest("AUDIT my code").unwrap();
        assert!(s.contains("audit/review"));
    }

    #[test]
    fn output_explicitly_marks_hints_as_advisory() {
        let s = suggest("audit").unwrap();
        assert!(s.contains("advisory only"));
        assert!(s.contains("hints, not orders"));
    }
}
