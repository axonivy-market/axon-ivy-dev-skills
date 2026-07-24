# Axon Ivy Dev Skills

Agent Skills for building, reviewing, and maintaining [Axon Ivy](https://developer.axonivy.com/) projects with AI coding agents.

This repository packages reusable [Agent Skills](https://agentskills.io) covering development using Axon Ivy framework (for example process design, data modeling, and CMS) and the project delivery lifecycle (from requirements engineering and implementation to verification and code review).

If you want to know more about Agent Skills, see [agentskills.io](https://agentskills.io).

## Skills Overview

33 skills grouped into 9 purpose-based categories — install the ones that match what you're building:

| Category | Skills | Purpose |
| --- | --- | --- |
| `general` | `axon-ivy`, `axon-ivy-init`, `ivy-market-import` | Project setup and cross-cutting orchestration for Axon Ivy development |
| `process-workflow` | `axon-ivy-workflow-guide`, `axon-ivy-process`, `axon-ivy-process-verify`, `axon-ivy-error-handling`, `axon-ivy-data`, `axon-ivy-java-data` | Designing, building, and verifying Axon Ivy workflow processes and their data |
| `smart-workflow` | `axon-ivy-smart-workflow` | AI-powered and agentic capabilities within Axon Ivy workflows |
| `persistence` | `axon-ivy-repository`, `axon-ivy-jpa`, `axon-ivy-persistence-utils`, `axon-ivy-liquibase`, `axon-ivy-liquibase-verify` | Data storage and persistence for Axon Ivy projects |
| `ui` | `axon-ivy-html`, `axon-ivy-primefaces-verify`, `axon-ivy-cms`, `axon-ivy-cms-verify` | User interface and content for Axon Ivy projects |
| `configuration` | `axon-ivy-variable-config`, `axon-ivy-user-role-config`, `axon-ivy-custom-fields`, `custom-fields-l10n` | Project-level configuration for Axon Ivy |
| `integrations` | `axon-ivy-rest`, `axon-ivy-mail`, `axon-ivy-business-calendar` | Connecting Axon Ivy to external systems and services |
| `delivery-workflow` | `axon-ivy-requirements-creation`, `axon-ivy-implement-story`, `axon-ivy-verify-story`, `axon-ivy-release` | The end-to-end software delivery lifecycle for Axon Ivy features |
| `quality-testing` | `axon-ivy-test`, `review-java`, `review-javascript` | Quality assurance for Axon Ivy projects |

## Quick Install

### GitHub CLI

```bash
gh skill install axonivy-market/axon-ivy-dev-skills

# Install skills for a specific agent (e.g. Claude Code)
gh skill install axonivy-market/axon-ivy-dev-skills --agent claude-code

gh skill install axonivy-market/axon-ivy-dev-skills persistence/skills/axon-ivy-jpa

gh skill list
gh skill update
```

See the GitHub announcement for details: [Manage agent skills with GitHub CLI](https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/)

### Manual Installation

```bash
git clone https://github.com/axonivy-market/axon-ivy-dev-skills.git
# Copy any skill folder (e.g. process-workflow/skills/axon-ivy-process) to ~/.claude/skills/ (Claude Code) or ~/.agents/skills/ (other agents)
```

## Contribution

This skill set is actively evolving, and your contributions are always warmly welcome to enrich our skills set.

1. Create a new skill folder and add `SKILL.md` using the structure below.
2. Follow the repository folder naming convention and anatomy.
3. Place the new skill under the matching category's `skills/` folder from the table above (e.g. `ui/skills/my-skill-name/`). If it doesn't fit an existing category, propose a new one.
4. Add eval cases and run the evaluation CI to verify correctness and efficiency. See guide [evals/EVALUATION.md](evals/EVALUATION.md)
5. Open a PR for review.

For more information about the Agent Skills standard, [agentskills.io](https://agentskills.io/specification).

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add instructions this skill should follow]
```

The frontmatter requires these fields:
- `name`: unique identifier in lowercase, using hyphens for spaces
- `description`: what the skill does and when it should be used

## Disclaimer

These skills encode Axon Ivy development patterns to assist AI coding agents. Always review generated code and test thoroughly in your own environment before relying on them for production work, especially skills that modify project files, data, or configuration.
