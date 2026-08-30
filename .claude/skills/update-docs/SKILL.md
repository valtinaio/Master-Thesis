---
name: update-docs
description: Reads the codes/ folder and updates ARCHITECTURE.md, and CLAUDE.md
  if needed, so the documents describe the code as it actually is. Only use when
  the user explicitly asks for this skill by name — never on your own initiative
  and never as a follow-up to an unrelated edit.
---

# Update the documents from the code

Bring `ARCHITECTURE.md` — and `CLAUDE.md` where a rule changed — in line with
what `codes/` actually contains.

## Step 1 — Read

Read in this order:

1. `ARCHITECTURE.md` in full
2. `CLAUDE.md` in full
3. every `.py` file under `codes/`, including `codes/graphs/`

Do not rely on memory of any of them.

## Step 2 — Compare

List every point where the documents and the code disagree. Check:

- **File layout** — do the files that exist match the layout section? Is
  every graph one file in `codes/graphs/`, and does that folder hold graph
  files only?
- **Schemas** — do the models in `codes/schema.py` match the State section:
  field names, which sub-graph writes them, what they contain?
- **Sub-graphs** — for each graph file: do its nodes, its data sources and
  its output match what its numbered section describes?
- **Contracts** — for the black-box graphs (ML, Results), is the stated
  input/output contract still what the code implements?
- **Failure behaviour** — does the code fail hard or degrade gracefully where
  the spec says it should?
- **Conventions** — Pydantic over TypedDict, `with_structured_output()`,
  `pathlib` paths, LangGraph primitives.

For each disagreement decide which side is right:

- **The code is ahead** — the code implements a deliberate decision the
  document has not recorded yet. Update the document.
- **The code drifted** — the code contradicts a decision the document states
  on purpose. Do not touch the document; report it as a code problem.

If you cannot tell which, ask the user before editing.

## Step 3 — Report before editing

Show the user, as a short list: each disagreement, which side you judged
right, and the exact edit you propose. Then ask whether to apply it.
Wait for confirmation.

## Step 4 — Edit

Apply only the confirmed edits.

- Change only the sections that are actually wrong.
- Keep the existing structure, tone and heading order of both documents.
- Do not add sections for parts of the code that are still undefined.
- Touch `CLAUDE.md` only when a coding rule or the architecture summary
  changed. Structural detail belongs in `ARCHITECTURE.md`.

## Rules

- Never write or change code with this skill. It edits documents only.
- Never invent architecture. If the code raises a question the documents do
  not answer, offer options, simplest first, and always include the option
  "tell me your own solution".
- If documents and code already agree, say so and change nothing.
