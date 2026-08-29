# AGENTS.md

Instructions for agents working in this repository.

## Project purpose

This repository is a growing library of interactive visualizations for Sheldon Axler's *Linear Algebra Done Right*.

The goal is not to build a general-purpose app. Each visualization should isolate one mathematical idea and make its mechanism directly explorable.

## Agent / ChatGPT entrypoints

For agents that support reusable skills, the project bootstrap skill is:

`skills/axler-visualizations/SKILL.md`

That skill should route the agent back to the current repository instructions instead of relying on stale embedded project context.

For visualization design principles, read:

`skills/math-visualization/SKILL.md`

The current `AGENTS.md` and `skills/math-visualization/SKILL.md` are the source of truth for project work.

## Repository structure

Keep the repository organized as a small static site for GitHub Pages.

```text
/
├── index.html                      # main visualization menu
├── AGENTS.md                       # repository/workflow instructions
├── skills/
│   ├── axler-visualizations/
│   │   └── SKILL.md                # ChatGPT/agent project bootstrap skill
│   └── math-visualization/
│       └── SKILL.md                # visualization design guidance
├── 3-51/
│   └── index.html                  # one visualization
├── 3-81/
│   └── index.html                  # one visualization
├── 3-82/
│   └── index.html                  # one visualization
├── 3-84/
│   └── index.html                  # one visualization
└── <new-topic>/
    └── index.html                  # future visualization
```

Rules:

- The root `index.html` is always the public menu.
- Every visualization lives in its own folder.
- Prefer stable, short folder names such as `3-51`, `change-of-basis`, or `null-space-range`.
- Do not put a visualization back into the root page.
- Avoid build tooling unless a future visualization genuinely requires it. Plain HTML/CSS/JS is preferred.

## Adding a new visualization

When adding a visualization:

1. Create a new folder with its own `index.html`.
2. Follow `skills/math-visualization/SKILL.md` when designing the interaction.
3. Add the visualization to the root menu.
4. Add both English and Russian interface copy.
5. Add a back link to the root menu.
6. Preserve the selected language when navigating between the menu and the visualization.
7. Re-read all changed files after writing them and verify the expected version is on `main`.

A new visualization is not complete until it is reachable from the root menu.

## Bilingual support

All public pages must support English and Russian.

Use one HTML file with an `en` / `ru` string dictionary instead of duplicating the page.

Navigation convention:

```text
?lang=en
?lang=ru
```

Rules:

- If `?lang=` is present, use it.
- Otherwise, use browser language as the default.
- Menu links must carry the selected language into visualization pages.
- Back links must carry the selected language back to the menu.
- Mathematical notation should remain the same across languages unless terminology genuinely requires a change.
- Translate UI and explanation text, not symbols.

## Main menu

The root menu is user-facing, not a developer status page.

It should contain only useful public copy:

- project title;
- short description;
- language switch;
- available visualizations;
- concise descriptions of those visualizations.

Do not show internal implementation notes such as:

- how folders are structured;
- how agents should add pages;
- that the menu is "ready for expansion";
- instructions about `/topic/index.html`;
- repository maintenance guidance.

Those instructions belong in this file, not on the website.

When the library grows, prefer a simple data-driven list of visualization metadata in the root page so adding a new entry requires minimal markup changes.

## Visual style

The site should feel like an explorable mathematical text, not a SaaS dashboard.

Keep visual language consistent across pages:

- quiet warm background;
- dark text;
- serif typography for mathematical headings/equations where appropriate;
- restrained borders and shadows;
- minimal controls;
- color only when it carries a mathematical role;
- responsive layout.

The interaction itself should explain the mathematics. Avoid large explanatory panels when the same idea can be shown through selection, alignment, arrows, movement, or highlighting.

## User-facing copy

Keep public copy concise and natural.

Avoid meta-language about design or implementation. In particular, do not put phrases like these on the public site:

- "dashboard slop";
- "the menu is ready for expansion";
- "new pages can be added as...";
- agent/developer instructions;
- comments about the repository architecture.

Copy should explain the mathematics or help navigation.

## GitHub workflow

When the user asks for a site change, make the change directly in this repository rather than only producing a local artifact.

For each write:

1. Read the current file before replacing it.
2. Update or create the required file on `main`.
3. Re-read the affected file after the write.
4. Verify important links and language paths conceptually from the resulting source.

Do not claim a change is complete until the repository has been re-read successfully.

## GitHub Pages assumptions

The site is intended to work as a static GitHub Pages project.

Therefore:

- use relative links;
- do not assume a custom domain;
- do not depend on a server-side router;
- keep pages functional when opened under the repository path;
- avoid APIs that require secrets or a backend.

## Current visualization registry

At the moment:

- `3-51/` — matrix multiplication as linear combinations of columns/rows.
- `3-81/` — matrix of a product of linear maps via basis-vector columns.
- `3-82/` — identity operator between two bases and inverse coordinate-change matrices.
- `3-84/` — change-of-basis formula `A = C^{-1}BC` as two coordinate routes for the same operator.

Keep this list updated when new visualization folders are added.
