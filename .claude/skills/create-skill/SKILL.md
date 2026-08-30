---
name: create-skill
description: Creates a new Claude Code skill as a SKILL.md file in .claude/skills/.
  Use when the user asks to create, add, or write a new skill, or wants a repeated
  workflow turned into a reusable skill.
---

# Create a new skill

The user defines what the new skill must do. Your job is to turn that into a
correctly structured SKILL.md file.

## Step 1 — Clarify (only if needed)

Ask only what you cannot clearly infer:

- What task should the skill handle?
- When should it trigger — which requests should load it?

If the user already described both, skip this step and write the file.

## Step 2 — Pick the name

Lowercase, hyphenated, verb-first where possible: `api-route`, `write-migration`,
`review-diff`. This name becomes both the directory name and the slash command.

## Step 3 — Write the file

Path: `.claude/skills/<skill-name>/SKILL.md`

The filename must be exactly `SKILL.md` (uppercase). The directory name must
match the `name` field in the frontmatter.

Template:

```markdown
---
name: <skill-name>
description: <What it does.> Use when <concrete trigger situations, in the
  words the user would actually type>.
---

# <Title>

## Steps
1. ...
2. ...

## Rules
- ...
```

## Rules for the generated skill

- The `description` decides whether the skill ever loads. State what it does
  AND when it applies. Vague descriptions never trigger.
- Keep the body short — well under 5k tokens. Move long references, templates,
  or examples into separate files in the same directory and link to them from
  the body.
- Write imperative instructions, not prose explanation.
- Include only what the user asked for. Do not invent extra steps or rules.

## Step 4 — Verify

After writing, tell the user:

- The exact path of the created file
- To test it in a fresh session by phrasing a request naturally, without
  naming the skill — if it does not load, the description is too vague

## Scope

Personal skills that should work across all projects go to
`~/.claude/skills/<skill-name>/SKILL.md` instead. Use the project path by
default; only use the personal path if the user asks for it.
