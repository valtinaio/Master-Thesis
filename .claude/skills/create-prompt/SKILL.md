---
name: create-prompt
description: Writes a reusable prompt for a given task, including three few-shot
  examples. Use when the user asks to create, write, or improve a prompt, needs
  a system prompt for an LLM call, or wants a task turned into a prompt template.
---

# Write a prompt

Turn the user's task description into a prompt that another LLM can execute
reliably. Do not execute the task yourself.

## Step 1 — Resolve ambiguity first

Do not write the prompt while any required behaviour is still undefined.
For each unclear point, ask the user and provide:

1. Two or three concrete options
2. Your recommendation and why
3. The explicit option: "or define it yourself"

Check at minimum:

- **Output format** — plain text, JSON, Markdown, fixed fields, ...?
- **Length and level of detail**
- **Tone and audience**
- **Edge cases** — what should happen on missing, invalid, or out-of-scope input?
- **Boundaries** — what must the LLM never do?

Ask everything in one message. Wait for answers. Do not guess and do not write
a draft "in the meantime".

If the user's description already answers a point, do not ask about it.

## Step 2 — Write the prompt

Structure:

```
<Role and objective — one or two sentences>

<Instructions as imperative bullets>

<Output format — stated explicitly>

<Examples>

<Edge case handling>
```

Rules:

- Imperative voice. "Extract the date", not "You should try to extract".
- State what to do, not only what to avoid.
- Put the output format in words AND show it in the examples.

## Step 3 — Add exactly three few-shot examples

The examples carry most of the generalisation. Make them **maximally
different** from each other. Vary along these axes:

- Input length — short vs. long
- Input quality — clean vs. messy, incomplete, or noisy
- Difficulty — obvious case vs. ambiguous or edge case

At least one example must cover a hard or degenerate case, so the LLM learns
the boundary and not just the happy path.

Format each example identically:

```
Input: <...>
Output: <...>
```

The output in every example must match the specified format exactly — any
deviation teaches the wrong pattern.

## Step 4 — Deliver

Save the prompt in a user-defined path as a markdown file. If the user doesn't
provide a saving-path, ask for it. Never invent a saving path yourself.

## Rules

- Never invent requirements the user did not state.
- Prefer the shortest prompt that fully specifies the behaviour.
- Exactly three examples — not two, not five.
