# Math Visualization Skill

Use this skill when turning a mathematical statement, theorem, example, or exercise into an interactive visualization.

## Goal

The visualization should make the mathematical mechanism visible. It should feel like an explorable mathematical note, not a dashboard or generic app UI.

Before building anything, answer:

1. What single mathematical relationship should the learner notice?
2. What should they be able to manipulate?
3. What visual change should make the relationship obvious?

## Core principles

- Prefer direct manipulation over explanatory prose.
- Make the interaction itself carry the explanation.
- Show where quantities come from and where they go.
- Use spatial structure that mirrors the algebraic structure.
- Prefer direct labels over legends.
- Highlight only the currently relevant mathematical objects.
- Avoid decorative cards, KPI-style panels, excessive badges, gradients, shadows, and generic SaaS layout patterns.
- Keep the page visually quiet so attention stays on the mathematics.
- Use typography and whitespace like a textbook or mathematical essay.
- Introduce color only when it encodes a mathematical role.
- If a relation can be shown with arrows, alignment, movement, grouping, or selection, prefer that over another paragraph of explanation.

## Interaction design

A strong interaction usually follows this pattern:

**select an object → reveal the relevant coefficients/structure → show the operation → show the resulting object**

Examples:

- select a column of a product matrix → reveal coefficients from the corresponding column of the right factor → combine columns of the left factor → show the resulting product column;
- select a vector → show its coordinates in a basis → reconstruct the vector;
- select a point/vector → apply a linear map → animate or draw the image;
- select an element of a kernel/range → show the defining relation directly.

The user should be able to edit simple numerical values whenever that helps test invariance or see that the pattern is general.

## Visual style

Aim for:

- warm/off-white or otherwise quiet background;
- dark mathematical text;
- serif typography for equations/headings where appropriate;
- thin rules instead of card borders;
- minimal controls;
- one accent color per mathematical role;
- responsive layout;
- direct manipulation of mathematical objects.

Do not make the visualization look like a generated analytics dashboard.

## Technical choices

Choose the smallest renderer that solves the problem.

- Plain HTML/CSS/JS for simple interactive algebra.
- SVG when geometry, arrows, movement, diagrams, or custom mathematical layouts matter.
- Canvas only when many animated graphical objects make SVG impractical.
- D3 only when its scales, transitions, selections, or data joins materially help.
- Avoid React/build tooling for a small standalone explainer unless complexity actually requires it.

Prefer a single static HTML file when possible so it can be hosted directly on GitHub Pages.

## Mathematical fidelity

- Match the notation used in the source material when possible.
- Do not replace the underlying theorem with a merely suggestive visual metaphor.
- Make dimensions/domains/codomains explicit when they matter.
- Make clear which entries are coefficients and which vectors/rows/columns they combine.
- Do not imply that finite numerical experimentation is a proof.
- Use examples to expose the invariant structure, then state that structure succinctly.

## Explanation hierarchy

Prefer this order:

1. visual mathematical object;
2. interaction;
3. symbolic identity generated from the interaction;
4. one short interpretation;
5. optional deeper note.

If the page needs a long paragraph before the user knows what to look at, redesign the visualization.

## Site architecture

Treat the repository as a growing library, not a single-page demo.

- Keep the root `index.html` as the visualization menu.
- Put each visualization in its own folder, e.g. `/3-51/index.html`, `/change-of-basis/index.html`.
- Every visualization page should have a clear link back to the menu.
- Add new entries to the menu as the library grows.
- Keep the same visual language across pages, but let the mathematical structure determine the interaction.

## Bilingual support

Every public page should support both English and Russian.

- Prefer one page with an `en` / `ru` string dictionary over duplicated HTML files.
- Use `?lang=en` and `?lang=ru` in links so language survives navigation.
- If no language is specified, use the browser language as a default.
- Keep mathematical notation identical across translations unless terminology requires a change.
- Translate the interface and explanation, not the symbols.

## Repository workflow

When working on this project, make requested site changes directly in the GitHub repository rather than leaving the result only as a local artifact.

After writes, re-read the affected files to verify that the expected version is present on `main`.

## Quality check

Before shipping, ask:

- Can someone understand the key idea by interacting for 20 seconds?
- Is every major UI element mathematically necessary?
- Does selection reveal causal structure rather than just highlight cells?
- Are colors doing semantic work?
- Could any paragraph be replaced by a visual relation?
- Does the page look more like an explorable textbook figure than a SaaS dashboard?
- Does it still work on mobile?
- Is the page reachable from the main menu?
- Do both RU and EN versions work and preserve language when navigating?

## Reference influences

This skill is a distilled house style inspired by principles from OpenAI data-visualization guidance, explorable-explanation patterns, math-focused SVG interaction patterns, and Tufte-style reduction of nonessential visual chrome. It is intentionally written as an original reusable checklist rather than a copy of any external skill.
