---
name: create-plan
description: Builds an implementation plan for a goal or reviews a plan the user
  already has, resolving every open decision with the user first. Use when the
  user asks for a plan, wants an approach before coding, or presents a plan to
  be checked.
---

# Create a plan

Produce a plan the user can approve and then have implemented. Do not write
any code and do not modify any file while this skill is active.

## Step 1 — Understand the project

Read enough of the codebase to ground the plan in what actually exists:
structure, existing patterns, and the files the goal touches. Never plan
against assumed code.

## Step 2 — Choose the mode

**The user provided a plan** → Review it. Check whether it actually reaches
the stated goal, whether any step is missing, and whether it conflicts with
the existing code. Point out gaps concretely; do not rewrite the plan silently.

**The user provided only a goal** → Derive the plan yourself. List every
variable, definition and strategy decision the goal depends on.

Both modes then continue with Step 3.

## Step 3 — Resolve every open decision

Every technical and non-technical decision of implementation belongs to the user, not to you. Never assume a default.

Ask in rounds:

- One round at a time, grouping decisions that are independent of each other.
- Each question offers two or three concrete options, your recommendation with
  a one-line reason, and the explicit option: "or define it yourself".
- Adapt every following question to the answers already given. If an answer
  makes a later question obsolete, drop it. If it opens a new decision, ask it.

Repeat until every detail is defined by the user. Do not draft the plan while questions are still open.

## Step 4 — Present the plan

Output the plan directly in the chat. No file, no artifact.

Structure:

**Goal** — one sentence.

**Decisions** — the choices made, one line each, so the user can see what was
locked in.

**Steps** — numbered, in implementation order. Each step names what happens
and why.

**Files affected** — a table listing every file with its change type
(`new` / `modified` / `deleted`) and one line on what changes in it. This
section is mandatory; a plan without it is incomplete.

**Open risks** — anything that could still go wrong, or nothing.

## Step 5 — Hand over

End by asking whether to implement the plan as written. Ask as plain text in
the chat — do not use a clickable question or option widget. Wait for
confirmation. Do not start implementing on your own initiative.

## Rules

- Keep the plan as simple as the goal allows. Fewer steps beat more steps.
- Plan only what the user asked for. Do not add improvements to the scope (if not necessary).
- If the goal cannot be reached as stated, say so before planning around it.
