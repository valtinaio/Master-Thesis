---
name: update-plan
description: Updates the current PLAN.md with the detailed plan for the "in_planing" step index.
---

Path for `PLAN.md`: `plan/PLAN.md`

# Example of the PLAN.md Table
A final plan for a specific step is already defined within the chat. For example for step 1. The Plan has the current state (= table):

| Step Index | Goal | Short description of the task | Status |
| 1 | Updating fmp_api.py & sec_api.py | Defining which API is used when and how | in_planning |
| --- | --- | --- | --- |
|  |  |  |  |

# Your Taks

## First
Under the table you find `# Detailed description of "in_planning"`.
And there you find:
`Step Index: `
Fill `Step Index: ` with the Step Index with `in_planing`. Means here this would become `Step Index: 1`.

## Second
If under the `## Description` block, there is a current old plan, delete that plan. Never delete the title `## Description`.
Then, under `## Description` you provide the new complete discussed FINAL plan how the goal must be implemented.
GOAL: The goal is, that based on that plan under `## Description` a new LLM call (whith new context) knwos exactly how it must implement the code.

## Third
Finally, once `## Description` is written, go to `plan/PLAN.md` and update the status of the row with the step index we were working on, to `completed`.