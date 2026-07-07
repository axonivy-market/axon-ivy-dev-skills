# Axon Ivy Dev Skills

Agent Skills for building, reviewing, and maintaining [Axon Ivy](https://developer.axonivy.com/) projects with AI coding agents.

This repository packages reusable [Agent Skills](https://agentskills.io) covering development using Axon Ivy framework (for example process design, data modeling, and CMS) and the project delivery lifecycle (from requirements engineering and implementation to verification and code review).

If you want to know more about Agent Skills, see [agentskills.io](https://agentskills.io).

## Skills Overview 🧭

35 listed skills across 3 categories:

| Category | Skills | Highlights | Details |
| --- | ---: | --- | --- |
| Core Platform 🔧 | 21 | Core Axon Ivy development capabilities for process design, data handling, UI, CMS, configuration, integrations, and testing. | `axon-ivy`, `axon-ivy-init`, `axon-ivy-workflow-guide`, `axon-ivy-process`, `axon-ivy-process-verify`, `axon-ivy-data`, `axon-ivy-java-data`, `axon-ivy-html`, `axon-ivy-primefaces-verify`, `axon-ivy-cms`, `axon-ivy-cms-verify`, `axon-ivy-variable-config`, `axon-ivy-user-role-config`, `axon-ivy-custom-fields`, `axon-ivy-error-handling`, `axon-ivy-rest`, `axon-ivy-repository`, `axon-ivy-test`, `ivy-market-import`, `axon-ivy-smart-workflow`, `axon-ivy-business-calendar` |
| Professional Services 🧩 | 8 | Delivery-oriented capabilities for persistence architecture, migrations, utilities, communication, and structured implementation workflows. | `axon-ivy-liquibase`, `axon-ivy-liquibase-verify`, `axon-ivy-jpa`, `axon-ivy-persistence-utils`, `axon-ivy-mail`, `axon-ivy-requirements-creation`, `axon-ivy-implement-story`, `axon-ivy-verify-story` |
| Other 🛠️ | 6 | Supporting capabilities for release activities and code quality verification across Java and JavaScript. | `axon-ivy-requirements-creation`, `axon-ivy-implement-story`, `axon-ivy-verify-story`, `axon-ivy-release`, `review-java`, `review-javascript` |

## Quick Install ⚡

Choose skills based on the categories above so the selected skills match your purpose. You can follow one of the installation methods below:

### GitHub CLI

If you have GitHub CLI v2.90.0 or newer with `gh skill`, you can install and manage skills directly from this repository.
The install command can run interactively to let you choose the target agent host, or you can define it in advance with `--agent` (for example `--agent claude-code`).

```bash
# Install all skills from this repository
gh skill install axonivy-market/axon-ivy-dev-skills

# Install one specific skill
gh skill install axonivy-market/axon-ivy-dev-skills axon-ivy-jpa

# Install one specific skill for a predefined agent host
gh skill install axonivy-market/axon-ivy-dev-skills axon-ivy-jpa --agent claude-code

# List installed skills
gh skill list

# Check for updates
gh skill update

# Update one specific skill
gh skill update axon-ivy-jpa
```
See the GitHub announcement for details: [Manage agent skills with GitHub CLI](https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/)

### Manual Installation

```bash
git clone https://github.com/axonivy-market/axon-ivy-dev-skills.git
# Copy any skill folder to ~/.claude/skills/ (Claude Code) or ~/.agents/skills/ (other agents)
```

## Contribution 🤝

This skill set is actively evolving, and your contributions are always warmly welcome to enrich our skills set.

Create a basic skill as a folder with a `SKILL.md` file that contains YAML frontmatter and instructions.

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

1. Create a new skill folder and add `SKILL.md` using the structure above.
2. Follow the repository folder naming convention and anatomy.
3. Place the new skill in the appropriate category in the list above.
4. Open a PR for review.

For more information about the Agent Skills standard, [agentskills.io](https://agentskills.io/specification).

## Disclaimer ⚠️

These skills encode Axon Ivy development patterns to assist AI coding agents. Always review generated code and test thoroughly in your own environment before relying on them for production work, especially skills that modify project files, data, or configuration.