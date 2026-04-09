---
name: unified-docs-creator
description: >
  Creates, audits, and refactors documentation using the Diátaxis framework.
  Use whenever you need to create a new document, update an existing one, audit
  a docs folder, clean up scattered or duplicated content, or restructure
  documentation. Activate it proactively when a task involves writing .md files,
  updating README-style docs, onboarding guides, architecture records, or any
  reference documentation. Trigger it when the user says "document this", "write
  a guide", "organize docs", "docs audit", "fix the docs structure", "apply
  Diátaxis", "cleanup docs", "clear deprecated docs", or similar. Works in any
  codebase without hardcoding project names, paths, or frameworks.
---

# unified-docs-creator

Guides agents to create, update, and maintain high-quality documentation using the Diátaxis framework. Fully generic — no project names, paths, or methodology references in the rules.

> **Quick start: Run Section 3 (Auto-Detection) first — always, before touching any doc.**

---

## 1. The Documentation Compass

Every document answers one of four questions. Classify by asking two questions:

**Question 1:** Is the reader **studying** or **working**?
**Question 2:** Does the reader need **practical steps** or **theoretical understanding**?

| | Practical | Theoretical |
|---|---|---|
| **Studying** | **Tutorial** | **Explanation** |
| **Working** | **How-to Guide** | **Reference** |

| Type | What it answers | Audience |
|------|-----------------|----------|
| **Tutorial** | "How do I learn this?" | Beginner, no prior knowledge |
| **How-to Guide** | "How do I accomplish X?" | Has basics, needs to get something done |
| **Reference** | "What does X do?" | Knows what they're looking for |
| **Explanation** | "Why is it designed this way?" | Wants conceptual clarity |

**Rules per type:**
- **Tutorial**: Step-by-step, builds something concrete. No teaching preamble.
- **How-to**: Jump straight to steps. "How to X" — never "how do I learn X".
- **Reference**: Tables, lists, signatures. Dense. No opinions.
- **Explanation**: Conceptual. Uses "why". May reference but is not a how-to.

### Editorial Expectations per Type

| Type | Prose density | Length | Structure |
|------|--------------|--------|-----------|
| **Tutorial** | Low — action sentences only | Medium — build something real | Numbered steps, concrete result at end |
| **How-to** | Low — direct, no preamble | Short — just the task | Task-oriented, "how to X" |
| **Reference** | High — dense tables/lists | Long — comprehensive | Tables, signatures, exhaustive |
| **Explanation** | Medium — conceptual prose | Variable | Narrative, "why", may reference other types |

> **Rule:** If you find yourself writing more than 2 sentences of context before the first step → you are writing a Tutorial, not a How-to. Cut the preamble.

---

## 2. Keyword Matrix

Use this matrix to detect and classify documents. Match by checking title, first paragraph, and section headings.

### Tutorial synonyms
"getting started", "introduction", "learn", "basics", "first steps", "beginner", "walkthrough", "hands-on", "step by step", "build", "create from scratch", "bootcamp", "crash course", "prerequisites", "setup from zero"

### How-to synonyms
"how to", "guide to", "how do I", "setting up", "configure", "install", "deploy", "enable", "disable", "manage", "add", "remove", "update", "upgrade", "integrate", "connect", "authenticate", "set up", "get started with", "implement", "build with", "work with", "use X with"

### Reference synonyms
"api", "reference", "specification", "configuration", "options", "parameters", "flags", "cli", "commands", "schema", "types", "interface", "endpoints", "response codes", "error codes", "signature", "return value", "request format", "data model", "struct", "enum", "class", "method", "changelog", "migration-guide"

### Explanation synonyms
"why", "concept", "architecture", "design", "decisions", "rationale", "theory", "overview", "background", "understanding", "tradeoffs", "alternatives", "compared to", "vs", "history", "motivation", "principles", "roadmap"

### Title-Pattern Priority (overrides keyword matrix)

If the document title contains any of the following patterns, classify by title **regardless** of body keywords. Apply this before running the keyword matrix scan.

| Title pattern | → Type |
|---------------|--------|
| "getting started", "introduction to", "learn", "basics", "first steps", "beginner", "walkthrough", "hands-on", "step by step", "build your first", "from scratch", "crash course", "bootcamp", "prerequisites", "setup from zero" | Tutorial |
| "how to", "how do I", "guide to" | How-to |
| "api", "reference", "specification", "changelog", "migration guide" | Reference |
| "why", "architecture", "design decisions", "rationale", "overview" | Explanation |

> **Why this matters:** A doc titled *"Getting Started: How to Deploy"* has both Tutorial and How-to keywords in its body. Title-pattern priority gives the title veto power so it is classified as a Tutorial — matching reader intent.

### Standard Audiences

Use one of these canonical values for the `audience` frontmatter field:

| Audience | Use when the reader is... |
|----------|---------------------------|
| `new contributors` | onboarding to the project or codebase |
| `developers` | building or integrating with the system |
| `api consumers` | calling the public or internal API |
| `operators` | deploying, configuring, or running the system |
| `maintainers` | contributing to core logic or architecture |

If no standard audience fits, write a concise one-liner (e.g., `"data scientists tuning ML pipelines"`) — but prefer an existing canonical value when possible.

---

## 3. Project Structure Auto-Detection

Detects the actual project structure before creating or updating any doc.

### Scan README files

Read these files (in order) to understand the project's existing structure:

```
/README.md
/docs/README.md
/docs/index.md
[docs-folder]/SUMMARY.md       ← MkDocs/Docusaurus
[docs-folder]/_Sidebar.md
```

From these, extract:
- Docs folder name (`docs/`, `doc/`, `documentation/`, `wiki/`, etc.)
- How the project categorizes its documentation
- Any existing conventions (e.g., `guides/`, `reference/`, `tutorials/`)
- Authoritative source for each topic

### List all docs

List all `*.md` files in the docs folder and root-level markdown (excluding `node_modules/`, `dist/`, build output). From the listing, detect:
- Topics already covered
- Scattered content (same topic in multiple files — DRY violation)
- File naming patterns suggesting type (`how-to-*.md`, `reference/*.md`)
- Orphaned docs with no clear audience (YAGNI candidate)

### Classify all docs

Use Section 2 (Keyword Matrix) to classify every `*.md` file by type. Flag mismatches.

### Monorepo / Cross-Cutting Docs

After listing all docs in a monorepo, detect cross-cutting content using these two rules:

1. **File-level heuristic**: If a doc's title or description contains "shared", "common", "global", "gateway", "contract", or "monorepo" → flag as a candidate cross-cutting doc.
2. **Reference heuristic**: If a doc is linked from 2 or more service subdirectory `docs/` folders → promote it to the workspace root `docs/cross-cutting/`.

> **Default rule:** Keep docs per service. Only elevate to `docs/` at the workspace root when both heuristics agree, or when a human explicitly marks the doc as cross-cutting.

---

## 4. Default Docs Tree Template

Use this as a starting point. Adapt it to match the project's actual structure (from Section 3).

```
docs/
├── README.md                        ← root index / overview
├── how-to/
│   ├── setup.md                    ← environment setup
│   ├── auth.md                     ← authentication
│   └── deploy.md                   ← deployment
├── reference/
│   ├── api.md                      ← API endpoints
│   └── config.md                   ← configuration reference
├── explanation/
│   └── architecture.md             ← architecture decisions
└── tutorials/
    └── first-service.md            ← build your first service
```

**Rules:**
- Each subfolder = one Diátaxis type
- One topic, one file — not multiple partial files
- If the project uses flat `*.md` files, match the project's convention

> **Every file requires frontmatter** — see Section 6 before creating.

---

## 5. Document Creation Workflow

### Before creating

1. Confirm the topic isn't already covered (run the duplicate scan below)
2. If scattered content exists across multiple files → run a cleanup audit (Section 7) before writing
3. New task or concept → proceed

### Scan Depth for Duplicates

Do NOT rely only on filename matching. Use this 3-tier scan before creating a new doc:

1. **Filename scan** (fast): Check for matching or near-matching file names
2. **Title/heading scan** (medium): Grep for matching title keywords in all doc titles and first headings
3. **Full-text scan** (deep, for ambiguous cases): Grep for the core concept (e.g., "authentication", "JWT", "auth") across all doc bodies

Only after all 3 tiers come back clean → proceed as a new doc.
If tier 2 or 3 finds a match → link to the existing doc instead of creating a new one.

### Creating

1. **Classify** — Use Section 1 + Section 2 to determine type
2. **Place** — Use the project's structure (Section 3) to find the right location
3. **Write** — Apply the correct type structure
4. **Add frontmatter** — Follow Section 6
5. **Verify** — Run the checklist in Section 8 before finishing

### Updating an existing doc

1. Re-classify — does it still match its type?
2. Does the update change the type? If yes, move or split it.
3. Check for knowledge duplicated elsewhere
4. Update `lastReviewed` in frontmatter

### Linking conventions

When cross-referencing other docs:
- **Within the same folder:** `[Title](./file.md)` or `[Title](./file.md#anchor)`
- **Across folders:** `[Title](../type/filename.md)` — use relative paths, never absolute
- **Between services (monorepo):** `[Title](../../other-service/docs/file.md)`
- **Never link bare URLs** for internal docs — use descriptive relative links
- Every cross-reference **must include a context line**: not just `"See X"` but `"See X for why this is configured this way"`

---

## 6. Document Frontmatter (Required)

Every new or updated document **must** start with this YAML frontmatter:

```yaml
---
title: [Short descriptive title]
description: [One-sentence summary. Write as a compressed infinitive: "Configure X for Y" or "Deploy to cloud platform." Avoid full sentences — aim for 10–15 words max.]
type: [tutorial | how-to | reference | explanation]
audience: [new contributors | developers | api consumers | operators | maintainers]
created: [ISO date — e.g., 2026-04-02]
lastReviewed: [ISO date — e.g., 2026-04-02]
---
```

---

## 7. Cleanup / Audit Mode

Activate when the user says: "cleanup", "clear", "audit", "fix scattered docs", "find duplicates", "remove deprecated docs", or similar.

### Workflow

1. **Scan** — Run Section 3 auto-detection on the full docs folder
2. **Classify** — Keyword-scan every `*.md` (Section 2)
3. **Find violations:**

   | Violation | Definition | Recommended Action |
   |-----------|------------|-------------------|
   | **Misplaced** | Doc type doesn't match its folder's implied category | Move to correct folder or rename |
   | **Duplicate** | Same knowledge in multiple files | Merge into one canonical file; add redirect links elsewhere |
   | **Orphan** | No keywords match, no clear audience — **or** not reachable from any index/SUMMARY and links to nothing | Delete or mark stale |
   | **Stale** | `lastReviewed` older than 6 months | Flag for review; update if content is still accurate |
   | **Hardcoded values** | Config/flag descriptions copied verbatim | Replace with "see [source]" |
   | **SSOT Violation** | Config values or contract specs copied verbatim instead of linking to the authoritative source | Replace with "see [source]"; link, don't inline |

4. **Report** — For each finding include:
   - File path
   - Violation type
   - Confidence level: `low | medium | high`
   - Recommended action
5. **Act only on explicit user approval** — never auto-delete, auto-move, or auto-merge

---

## 8. Quality Checklist

Before marking any doc creation or update done, verify:

| # | Check | How |
|---|-------|-----|
| 1 | **Correct type** | Matches its declared type's structure rules? |
| 2 | **Frontmatter complete** | Has `title`, `description`, `type`, `audience`, `created`, `lastReviewed`? |
| 3 | **No duplication** | Topic already covered elsewhere? Link instead. |
| 4 | **SSOT-aligned** | Config values → "see [source]". Contracts and specs → linked, not inlined. Never copy from an authoritative source. |
| 5 | **Right level** | Audience match correct? |
| 6 | **Actionable** | Can the reader do something after reading this? |
| 7 | **No bare URLs for internal links** | Search for `[](http` — every internal link must use relative `[Title](./path)` syntax, never a bare URL |
| 8 | **Cross-refs include context** | Every "See X" link includes a one-line context clause (e.g., "See X for why this is configured this way") |

---

## 9. Anti-Patterns

- **How-to with a teaching preamble** — "First let me explain X..." → Cut the preamble. How-tos jump straight to steps.
- **Reference with opinions** — "This API is great because..." → Remove.
- **Tutorial without a concrete result** — Must end with something working.
- **SSOT violation** — Copying descriptions verbatim → "see [source]" instead.
- **Speculative content (YAGNI)** — "This might be useful later..." → Delete, **unless it is the declared SSOT for a planned feature** (in that case, move it to the project's TIL or spec doc).
- **Orphan doc** — No keywords match, no clear audience → Delete or mark stale.
- **Cross-reference without context** — "See X" with no reason why → Add one-line note explaining why.

---

## 10. Decision Records (ADRs)

Architecture Decision Records document significant design choices. Unlike other doc types, ADRs have a **lifecycle** — they can be superseded, deprecated, or completed. Agents must check status before acting on an ADR.

### When to write an ADR

Create one when a decision has **lasting consequences** across multiple services, packages, or layers:
- Naming conventions that affect Docker, Traefik, env vars, and clients
- Authentication strategy (e.g., JWT vs session, PKCE requirements)
- Protocol choices (REST vs gRPC, GraphQL)
- Database-per-service vs shared database
- Event schema conventions

Do **not** create an ADR for:
- Routine refactors with no architectural impact
- Single-service implementation details
- Tooling changes (use a TIL entry instead)

### Lifecycle states

| Status | Meaning | Agent behavior |
|--------|---------|----------------|
| `draft` | Under active discussion | Read and contribute if asked |
| `accepted` | Final decision, in force | Read and follow |
| `completed` | Fully implemented | Read for historical context |
| `deprecated` | Outdated but kept for history | Read, do not follow |
| `superseded` | Replaced by another ADR | Skip entirely, follow `supersededBy` |

### Standard frontmatter

```yaml
---
title: [Short descriptive title — noun phrase, not verb phrase]
type: decision
status: draft | accepted | completed | deprecated | superseded
supersededBy: ADR-XXX  # fill only when status is superseded
created: YYYY-MM-DD
decided: YYYY-MM-DD    # date the decision was accepted
deciders: [name, name]  # people or team who made the decision
---
```

### Standard structure

```markdown
## Context
What problem prompted this decision? What constraints or forces are at play?

## Decision
What was decided? State the decision clearly and specifically.

## Alternatives considered
What other options were evaluated? Why were they rejected?

## Consequences
- **Positive**: What becomes easier or more maintainable?
- **Negative**: What trade-offs or complications were introduced?
- **Neutral**: What consequences are still uncertain?

## Status Log
- YYYY-MM-DD — Draft
- YYYY-MM-DD — Accepted (decision finalized)
- YYYY-MM-DD — Completed (fully implemented)
- YYYY-MM-DD — Superseded by ADR-XXX  ← added only when replaced
```

### Agent fast-skip rule

> **Before reading any ADR, check `status` in frontmatter first.**

- `draft` → read and contribute
- `accepted` → read and follow
- `completed` → read for history context only
- `deprecated` → read for history, do not follow
- `superseded` → **skip entirely**, follow the `supersededBy` link instead

### Updating a resolved ADR

When an ADR's status changes:

1. Update the `status` field in frontmatter
2. Add a new entry to the **Status Log**
3. If `superseded`, add the `supersededBy` field
4. For `completed` ADRs, add an **Implementation** section documenting what was built and when

### ADR placement

| Project style | Where ADRs live |
|---------------|----------------|
| Monorepo | `docs/architecture/decisions/ADR-001-title.md` |
| Flat | `docs/decisions/ADR-001-title.md` |
| Mixed (MemoZen) | `docs/architecture/adr/` for official ADRs; `reports/issues/` for working/resolved ADRs |

> **Canonical ADR location takes priority.** If a doc lives in `reports/issues/` but the project convention is `docs/architecture/adr/`, move it when it reaches `accepted` status. Working drafts may live in `reports/issues/` for faster iteration.
