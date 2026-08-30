---
name: create-plan
description: Builds an implementation plan for a goal. The complete plan must be defined by the user. Your goal is only to help the user create such a plan.
---

# Create a plan

Produce a plan the user can approve and then have implemented. Do not write
any code and do not modify any file while this skill is active.

# Your Goal
The USER must create the plan, not you! If the user doesn't give you enough information to complete the user-defined goal, then keep asking until every little technical detail is defined by the user. You NEVER define anything by yourself — not even small details. So the process is the following:
1. The user defines a goal with a rough plan of how to achieve that goal.
2. Your task is to identify gaps within that plan and ask the user for every little detail needed to fill those gaps.
3. You never suggest anything yourself; you only ask the user until the plan is complete. Only if the user's suggestions are technically wrong do you explain why they are wrong and make a suggestion yourself for how to solve them.

# The level of technical detail the user must provide
The user must provide very specific information. For example: if the user plans a new method for a class, the different arguments and the logic implementation (if, else, ...) must be completely defined by the user, so that you only implement exactly what the user told you, and not what you decided yourself.
