---
name: create-agent-skill
description: 'Create, update, or review a VS Code agent skill. Use when turning a repeatable workflow into a SKILL.md, deciding workspace versus personal scope, drafting skill instructions, or validating skill structure and discoverability.'
argument-hint: 'Describe the workflow the skill should capture and where it should be available.'
user-invocable: true
disable-model-invocation: false
---

# Create an Agent Skill

Create a focused, reusable `SKILL.md` for a repeatable agent workflow.

## When to Use

- Turn a conversation, checklist, or implementation method into a reusable skill.
- Create, update, or review a workspace or personal `SKILL.md`.
- Decide whether a workflow belongs in a skill, instructions file, prompt, custom agent, or hook.
- Improve a skill's discovery description, procedure, or validation guidance.

## Procedure

1. Review the conversation and available repository context. Extract the workflow's ordered steps, decision points, branching logic, quality criteria, and completion checks.
2. If the workflow is unclear, ask what outcome the skill should produce, whether it is workspace-scoped or personal, and whether the user wants a quick checklist or a full workflow.
3. Choose the smallest suitable primitive:
   - Use a skill for an on-demand, multi-step workflow with optional bundled resources.
   - Use agent instructions for guidance that should apply broadly and automatically.
   - Use a prompt for one focused task with parameters.
   - Use a custom agent when the workflow needs context isolation or distinct tool restrictions.
   - Use a hook when a deterministic lifecycle command must enforce behavior.
4. Choose a scope and path:
   - Workspace: `.github/skills/<skill-name>/SKILL.md`, `.agents/skills/<skill-name>/SKILL.md`, or `.claude/skills/<skill-name>/SKILL.md`.
   - Personal: `~/.copilot/skills/<skill-name>/SKILL.md`, `~/.agents/skills/<skill-name>/SKILL.md`, or `~/.claude/skills/<skill-name>/SKILL.md`.
5. Draft the skill with YAML frontmatter. Set `name` to 1-64 lowercase alphanumeric characters and hyphens, matching the containing folder. Add a specific, keyword-rich `description`; quote descriptions containing colons. Add `argument-hint` only when it helps invocation.
6. Write a concise body containing:
   - What the skill accomplishes.
   - Concrete trigger cases under `When to Use`.
   - A numbered procedure with decisions and expected outputs.
   - References to bundled resources using relative `./` paths when resources exist.
7. Inspect the draft for ambiguity. Identify the weakest instruction or unresolved decision, ask a focused question when needed, then revise the skill rather than leaving assumptions implicit.
8. Validate the result:
   - Confirm the file is under a supported skills directory.
   - Confirm the folder name equals the frontmatter `name`.
   - Confirm YAML is between the opening and closing `---` markers, uses spaces rather than tabs, and includes a meaningful `description`.
   - Confirm procedure steps are self-contained, actionable, and complete without relying on hidden conversation context.
   - Confirm referenced scripts, templates, and documents exist at their relative paths.
   - Keep `SKILL.md` below 500 lines; move lengthy domain material into referenced resources.
9. Report what the skill produces, where it was saved, example prompts that should trigger it, and useful related customizations to consider next.

## Quality Criteria

A finished skill has a narrow purpose, a discoverable description with concrete trigger terms, explicit decision points, progressive loading, and a verifiable completion state. It should preserve existing project conventions and avoid duplicating always-on instructions.
