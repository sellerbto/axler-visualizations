---
name: axler-visualizations
description: Use when the user asks to create, edit, review, organize, or deploy interactive visualizations for Sheldon Axler's Linear Algebra Done Right, or refers to the sellerbto/axler-visualizations GitHub project. Before acting, bootstrap the project by reading the repository's current AGENTS.md and math visualization skill from GitHub, then follow those files as the source of truth.
---

# Axler Visualizations Project Router

This is a bootstrap skill for the `sellerbto/axler-visualizations` project.

Do not duplicate the full project rules here. The repository files are the source of truth and may evolve over time.

## Repository

GitHub repository:

`sellerbto/axler-visualizations`

Default branch:

`main`

## Required bootstrap

For any task that changes, reviews, extends, or reasons about this visualization project:

1. Use the GitHub connector/app, not web search, to access the user's repository.
2. Read the current `/AGENTS.md` from `main`.
3. Read the current `/skills/math-visualization/SKILL.md` from `main`.
4. Treat those two files as the current source of truth, even if they differ from assumptions in the conversation or from this bootstrap skill.
5. Inspect the relevant current project files before editing them.

Do not skip the bootstrap just because the project was discussed earlier in the conversation. The repository may have changed.

## Execution rules

After bootstrapping:

- Follow `AGENTS.md` for repository structure, bilingual behavior, navigation, GitHub Pages constraints, and repository workflow.
- Follow `skills/math-visualization/SKILL.md` for interaction design, mathematical fidelity, visual style, renderer choices, and quality checks.
- Make requested site changes directly in `sellerbto/axler-visualizations` on `main` unless the user explicitly asks for a branch or pull request.
- Re-read every affected file after writing it.
- Do not report completion until the written files have been verified in GitHub.
- If repository structure changes, update `AGENTS.md` and its visualization registry when appropriate.

## New visualization workflow

When the user asks for a new visualization:

1. Bootstrap from the two repository files above.
2. Understand the mathematical statement and identify the one relationship the interaction should make visible.
3. Create the visualization in its own folder according to `AGENTS.md`.
4. Support both English and Russian according to the repository convention.
5. Add the visualization to the root menu.
6. Preserve language across menu/detail navigation.
7. Verify the new page, menu entry, links, and both language paths from the resulting source.

## Existing visualization workflow

When the user asks to modify an existing visualization:

1. Bootstrap from the two repository files above.
2. Read the existing visualization file and the root menu if navigation or metadata may be affected.
3. Preserve the existing mathematical behavior unless the requested change intentionally alters it.
4. Make the smallest coherent change that satisfies the request.
5. Re-read and verify all affected files.

## Failure handling

If the GitHub repository is not accessible through the GitHub connector:

- do not guess from stale copies;
- tell the user repository access is unavailable;
- ask them to grant or restore GitHub access.

If one of the required bootstrap files is missing, inspect the repository structure and tell the user before proceeding with structural changes.
