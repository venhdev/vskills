---
name: harness-audit
description: >
  Audit a project against Harness Engineering standards — comprehensive evaluation
  of a codebase's coding agent harness quality. Use this skill when the user wants
  to: check if a project meets harness engineering standards, audit AGENTS.md /
  CLAUDE.md, review tool/MCP setup, evaluate context management, check verification
  loops, architectural constraints, observability, or any request phrased as
  "how good is this project's harness", "check harness setup", "harness audit",
  "evaluate agent setup". Always trigger when the user mentions harness engineering
  alongside a specific project or codebase.
---

# Harness Engineering Audit

This skill audits a project (local path or repo) against 8 Harness Engineering standards
synthesized from: OpenAI, Anthropic, LangChain, Thoughtworks, HumanLayer, and community.

**Definition**: Agent = Model + Harness. The harness is everything surrounding the model —
system prompt, tools, context management, constraints, verification loops, observability.

---

## Workflow

### Step 1: Gather project information

Ask the user (if not already provided):
1. **Path or repo** — local path, GitHub URL, or current working directory?
2. **Project type** — greenfield (new) or legacy (existing codebase)?
3. **Agent in use** — Claude Code, Codex, custom agent, or none yet?
4. **Scope** — full audit (8 categories) or specific categories only?

If the user already provided a path in their message, skip and proceed to Step 2.

### Step 2: Scan project structure

Run scans to collect evidence:

```bash
# Check agent instruction files
find . -maxdepth 3 -name "CLAUDE.md" -o -name "AGENTS.md" -o -name "AGENT.md" \
       -o -name ".claude" -o -name "agent.md" 2>/dev/null

# Check docs structure
ls -la docs/ 2>/dev/null || echo "No docs/ directory"

# Check CI/CD & linters
ls .github/workflows/ 2>/dev/null
find . -name ".eslintrc*" -o -name "pyproject.toml" -o -name ".flake8" \
       -o -name "biome.json" -o -name "ruff.toml" 2>/dev/null | head -10

# Check test infrastructure
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" 2>/dev/null | wc -l

# Check MCP config
find . -name "mcp*.json" -o -name ".mcp*" -o -name "mcp_config*" 2>/dev/null

# Check skills
find . -name "SKILL.md" -o -name "*.skill" 2>/dev/null

# Read agent instruction file if present
cat AGENTS.md 2>/dev/null || cat CLAUDE.md 2>/dev/null | head -100

# Check architectural structure
find . -maxdepth 2 -type d | head -30
```

> Read **references/checklist.md** for detailed evidence commands per category.

### Step 3: Score 8 Categories

For each category, evaluate based on evidence found. Scoring scale:
- **✅ Pass (2pts)** — Clearly meets the standard
- **⚠️ Partial (1pt)** — Present but with significant gaps
- **❌ Fail (0pts)** — Missing or implemented incorrectly

**8 Categories (16pts total):**

| # | Category | Focus |
|---|----------|-------|
| 1 | Agent Instruction File | AGENTS.md / CLAUDE.md quality |
| 2 | Context Management | Sub-agents, context firewall, handoff |
| 3 | Verification Loop | Build-verify, test-before-done |
| 4 | Architectural Constraints | Linters, structural tests, boundaries |
| 5 | Tool & MCP Hygiene | Context-efficient tooling |
| 6 | Documentation as System of Record | Knowledge in repo, not Slack |
| 7 | Observability & Loop Detection | Traces, doom loop prevention |
| 8 | Planning & Workflow Design | Plan-before-execute, sprint contracts |

Total scoring:
- **14-16pts** — 🟢 Excellent harness
- **10-13pts** — 🟡 Good, a few areas to improve
- **6-9pts** — 🟠 Partial harness, notable gaps
- **0-5pts** — 🔴 Weak harness, significant refactoring needed

### Step 4: Output Report

Format output using this template:

```
# 🔍 Harness Engineering Audit Report
**Project:** [name / path]
**Date:** [date]
**Agent:** [tool in use]
**Type:** [Greenfield / Legacy]

---

## 📊 Total Score: X/16 — [Excellent/Good/Partial/Weak]

| Category | Score | Status |
|----------|-------|--------|
| 1. Agent Instruction File | X/2 | ✅/⚠️/❌ |
| 2. Context Management | X/2 | ... |
| ...

---

## 📋 Category Details

### 1. Agent Instruction File [X/2]
**Evidence found:** ...
**Assessment:** ...
**Improvement suggestions:** ...

[repeat for all 8 categories]

---

## 🚀 Top 3 Quick Wins
1. [Easiest action with highest impact]
2. ...
3. ...

## 🗺️ Improvement Roadmap
[Ordered by priority, grouped by effort]
```

### Step 5: Follow-up

Offer the user:
- "Want me to dive deeper into any specific category?"
- "Want me to generate a tailored AGENTS.md template for this project?"
- "Want me to create a detailed harness improvement plan?"

---

## Edge Cases

- **Repo with no code yet** — Audit based on structure + config files
- **No agent in use** — Audit "harness readiness" (how prepared the codebase is for agents)
- **Monorepo** — Audit each package/app separately or evaluate shared harness config
- **Private/closed repo** — Ask user to paste AGENTS.md content and config files directly
