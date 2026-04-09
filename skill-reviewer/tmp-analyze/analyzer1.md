give me comment about this skill.

---
name: skill-reviewer
description: >
  Reviews existing skills for signal-to-noise quality and refines them without losing
  content power. Use when auditing skill health, before splitting a growing skill, or when
  an agent reports a skill is hard to follow. Trigger when the user says "review this
  skill", "audit skills", "refine this skill", or "improve this skill". Do NOT use line
  count alone as a quality signal — a long skill covering genuinely distinct concerns is
  fine.
---

# skill-reviewer

Audits and refines skill files to maximize signal-to-noise for agent consumption.

---

## When to Trigger

- An agent reports a skill is "hard to follow"
- After adding a new section to any skill
- When a skill has grown significantly and needs hygiene

> **Do NOT trigger just because a skill is long.** Line count is not a quality signal.
> A 1000-line skill covering 5 distinct concerns is better than 5 separate skills
> an agent must context-switch between. Only act when signal-to-noise is genuinely low.

---

## What Actually Hurts Agents

| Problem | Why it hurts | Detection |
|---------|-------------|-----------|
| **Vague section headers** | Agents can't quickly locate the right section | Header is a phrase, not a noun |
| **Prose > bullets** | Rules buried in paragraphs agents skim past | > 3 sentences explaining a single rule |
| **Anti-patterns as paragraph** | Hardest section to skim — agents ignore it | Listed as numbered items or paragraphs |
| **Duplicated rules** | Same rule stated 3x → agent confused which is authoritative | Same idea in 2+ sections |
| **Template inline in prose** | Agent can't copy-paste cleanly | Code mixed inside sentences |
| **Missing frontmatter** | Agent doesn't know when to trigger | No YAML frontmatter block |
| **Project-specific references** | Skill can't be ported to another codebase | Hardcoded paths, names, or conventions |
| **Mixed concerns in one section** | Forces agents to read everything to find the rule | Section covers both "what" and "how to apply it" |

---

## What Does NOT Hurt Agents

- Long skills with distinct sections covering distinct concerns
- Many lines of tables or code (high density, easy to skim)
- Sections > 100 lines if they cover one concern thoroughly
- Repetition across skills (different triggers, different contexts)

---

## Audit Steps

### Step 1 — Read with an Agent's Eyes

Skim the skill top-to-bottom. Note:
- Which sections would an agent actually read?
- Which sections would an agent skip or skim past?
- Where does the agent's eye stop vs. glaze over?

### Step 2 — Flag Signal-to-Noise Violations

| # | Check | Problem | Fix |
|---|-------|---------|-----|
| 1 | Vague header? | "Notes", "Other", "Further info" | Rename to descriptive noun |
| 2 | Rule as paragraph? | > 3 sentences for one rule | Convert to bullet or table |
| 3 | Anti-patterns as paragraph? | Numbered list or wall of text | Pure bullet list |
| 4 | Duplicate rule? | Same idea in 2+ sections | De-duplicate, keep one, link elsewhere |
| 5 | Template inline? | Code inside sentences | Extract to code block |
| 6 | Project-specific reference? | Hardcoded paths, names, conventions | Replace with generic placeholder or environment variable |
| 7 | Mixed concerns? | Section covers unrelated things | Split into sub-sections |
| 8 | Missing frontmatter? | No YAML block | Add before refining |

### Step 3 — Assess Section Quality

For each section, ask: **"Would an agent find the right rule here in 3 seconds?"**

- **Yes** → section is fine, leave it
- **No** → apply the most targeted fix (don't rewrite the whole section)

### Step 4 — Decide Refinement Scope

Apply fixes only to sections that failed Step 2. Do not rewrite a well-structured section just because it's long.

---

## Refinement Tactics

### Tactic 1 — Prose → Table or Bullet

| Before | After |
|--------|-------|
| "The following naming patterns are correct for domain services: `<domain>-service` is the standard. Examples include..." | `| Category | Pattern | Examples |\n|---|---|---|\n| Domain services | \`<domain>-service\` | auth-service, payment-service |`

### Tactic 2 — Anti-Patterns as Pure Bullet List

| Before | After |
|--------|-------|
| "## Anti-Patterns\nThe first anti-pattern to avoid is..." | `## Anti-Patterns\n\n- **Teaching preamble** — "First let me explain..." → Cut. How-tos jump to steps.\n- **Verbose rule** — > 3 sentences → Bullet or table.\n- **Duplicate rules** — Same idea in 2+ sections → Keep one, link.` |

### Tactic 3 — Navigation Headers

| ❌ Vague | ✅ Descriptive noun/number |
|----------|---------------------------|
| "Additional Notes" | "## 7. Templates" |
| "Other Considerations" | "## 10. Decision Records (ADRs)" |
| "Notes" | "## 5. Duplicate Scan Rules" |

### Tactic 4 — Extract Inline Templates

Extract example code embedded in prose into a labeled code block:

```
## Frontmatter Template

Correct format:

```yaml
---
title: [Short title]
type: tutorial | how-to | reference | explanation
---
```
```

### Tactic 5 — Replace Project-Specific References

Replace hardcoded values with generic placeholders:

```
Before: "Check .claude/rules/critical_dev.md for known issues."
After:  "Check the project's critical rules file (or equivalent) for known issues."
```

```
Before: "Review TILs in docs/architecture/til/"
After:  "Review TILs in [project-til-root]/"
```

### Tactic 6 — Split Only When Genuinely Mixed

Split a section only when it covers two or more distinct concerns that:
- Have different trigger conditions
- Need to be applied independently

Do NOT split a long section that covers one concern thoroughly.

---

## Output Format

After auditing, produce this report:

```markdown
## Skill Quality Report — `<skill-name>`

**Path:** `<path>`
**Signal-to-Noise:** ✅ Good | ⚠️ Needs cleanup | 🔴 Hard to follow

### Violations Found

1. **[Section 3]** "Notes" header — vague → rename to "Duplicate Scan Rules"
2. **[Section 7]** Rule stated as paragraph → convert to bullet list
3. **[Anti-patterns]** Numbered list → convert to pure bullet list
4. **[Section 2]** Project-specific path → replace with generic placeholder

### Refinements Applied

| # | Section | Fix |
|---|---------|-----|
| 1 | Section 3 | Renamed header |
| 2 | Section 7 | Prose → 3-bullet list |
| 3 | Anti-patterns | Numbered → bullet list |
| 4 | Section 2 | Replaced hardcoded path with generic placeholder |

### Remains Unchanged

- Sections 1, 2, 4, 5 — well-structured, no changes needed
- All templates — correctly in code blocks
```

---

## Refine Checklist

Before marking a refinement done, confirm:

- [ ] No vague section headers (agent can quickly locate sections)
- [ ] Rules use bullets or tables, not prose paragraphs
- [ ] Anti-patterns → pure bullet list
- [ ] No duplicate rules across sections
- [ ] Templates in code blocks, not inline in prose
- [ ] Frontmatter present (`name`, `description`)
- [ ] No hardcoded project names, paths, or conventions
- [ ] Did NOT rewrite well-structured sections just for being long

---

## Self-Refinement Loop

When using this skill to refine itself:

1. Audit this skill using the same audit steps above
2. Flag any violations in this skill
3. Save the current version as `SKILL.md.bak` before applying changes
4. Apply only targeted fixes — do not rewrite well-structured sections
5. Verify the refined version still triggers correctly via frontmatter