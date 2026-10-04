---
name: novel-writer
description: Plan, draft, rewrite, audit, polish, and maintain long-form serialized fiction in local manuscript repositories. Use when Codex needs to create or revise a volume, arc, stage plan, promise-payoff map, or multi-chapter outline; write, continue, expand, or structurally rewrite a chapter; diagnose reader retention or pacing; run cross-chapter continuity, character, evidence, capability, or mystery checks; polish prose without breaking canon; or synchronize durable project state after accepted manuscript changes.
---

# Novel Writer

Use this skill as the procedural layer for serial-fiction work. Treat project
files as authority for story facts, setting, voice, and local thresholds.

## Authority

Resolve story conflicts in this order unless the project explicitly defines a
stricter hierarchy:

1. completed prose;
2. current progress, continuity snapshots, and specialist ledgers;
3. detailed execution outlines and chapter cards;
4. volume outlines, stage plans, and external research.

Use summaries and outlines to locate evidence. Never use them to explain away a
discontinuity that readers encounter in the prose.

Preserve the user's existing file layout and naming conventions. Do not create
a duplicate project workflow when a compact adapter can point to this skill and
record only project-specific canon, thresholds, and paths.

## Route the task

Read every selected reference completely before acting.

- For a new volume, arc, stage plan, 20-100+ chapter outline, payoff map, or
  large structural reorder, read
  [serial-planning.md](references/serial-planning.md) and
  [outline-templates.md](references/outline-templates.md).
- For a new chapter, continuation, rewrite, or expansion, read
  [chapter-production.md](references/chapter-production.md),
  [retention-audit.md](references/retention-audit.md), and
  [continuity-audit.md](references/continuity-audit.md).
- For retention, pacing, setup debt, payoff, or hook complaints, read
  [retention-audit.md](references/retention-audit.md).
- For continuity, out-of-character behavior, capability limits, evidence,
  objects, chronology, identity secrets, or mystery reveals, read
  [continuity-audit.md](references/continuity-audit.md).
- For line editing, de-mechanizing, dialogue, rhythm, scene pressure, or hook
  refinement, read [prose-polish.md](references/prose-polish.md).
- For progress files, snapshots, ledgers, entry points, or final handoff, read
  [state-sync.md](references/state-sync.md).
- For transmigration, historical institutions, examinations, bureaucracy,
  guilds, or borrowed famous texts, also read
  [historical-transmigration.md](references/historical-transmigration.md).

## Core chapter acceptance loop

For new or substantially revised prose:

1. Discover project instructions, current state, relevant plans, and the
   smallest continuity-sensitive evidence set.
2. Build a chapter card with an immediate reader question, meaningful choice,
   same-chapter payoff, visible state change, cost, and specific next drive.
3. Draft or revise one chapter file while preserving local length and naming
   rules.
4. Run the prose-only retention gate. Record four-sentence blind recall, all
   eight evidence-backed scores, a direct `continue / hesitate / stop` verdict,
   the lowest-scoring evidence, revision action, and exact text version.
5. Run reader-forward continuity on a focused linked-chapter window in story
   order.
6. Run the formal severity audit for canon, causality, character, capability,
   evidence, domain, mystery, hook, and meta-language risks.
7. Apply a human-texture pass and prose polish without silently changing the
   story contract. For Chinese prose, inspect paragraph function, sentence
   focus, referent handoff, viewpoint-filtered detail, and read-aloud rhythm;
   do not impose universal punctuation or rhetorical-template bans.
8. If any prose changes, invalidate the prior score and reviews. Repeat the
   retention gate, reader-forward pass, and formal audit on the final version.
9. Update durable project state only after all required gates pass
   consecutively on the same exact text.
10. Report changed files, gate results, unresolved risk, and the next concrete
    bridge. Commit or publish only when authorized.

Retention and consistency are independent gates. A clean continuity report
cannot rescue a weak or unscored chapter. An editorial score is not market
proof; label it as a proxy when no cold-reader or live-platform evidence exists.

## Non-negotiable checks

- Advance at least one of: new information, new conflict, new choice, or new
  cost.
- Give the reader a bounded result in the current chapter; another clue or
  future promise alone is not enough.
- Keep protagonists within earned knowledge, authority, resources,
  relationships, access, and capability.
- Track important objects, evidence, documents, texts, injuries, debts, and
  promises through source, custody, knowers, state changes, and allowed next
  use.
- Compare the ending with recent hooks; require a new fact, action, decision,
  deadline, relationship risk, answer, or cost.
- Remove project-facing language from publishable prose, including chapter
  numbers used as navigation, file paths, outline labels, workflow notes, and
  references to the reader or author.
- Treat every substantive prose edit as a new version that invalidates earlier
  retention and acceptance records.

## Deterministic helpers

Run the outline auditor when a Markdown outline uses chapter tables, stage
ranges, and optional promise IDs:

```bash
python skills/novel-writer/scripts/audit_serial_outline.py \
  path/to/detailed-outline.md \
  --contract path/to/volume-outline.md \
  --start 101 --end 200
```

Run the meta-language scanner on publishable manuscript files:

```bash
python skills/novel-writer/scripts/scan_prose_meta.py drafts/
```

Run the warning-only Chinese prose-shape auditor when prose feels mechanically
regular, syntactically dense, or over-explained:

```bash
python skills/novel-writer/scripts/audit_prose_shape.py \
  --names names.txt path/to/chapter.md
```

`--names` takes a plain list of character names so that `林川道：“……”` counts
as dialogue. Pass a whole `drafts/` directory to get per-10k rates and the
number of chapters hit for each negation family. To find a book's own repeated
phrases, compare its narration against a baseline corpus:

```bash
python skills/novel-writer/scripts/discover_tics.py \
  --target drafts/ --baseline path/to/baseline/ --exclude names.txt > tics.tsv
```

Prefer a human-written baseline. Against the author's other books it only finds
book-specific habits. Read the `under` and `probe` rows before stripping
similes or questions any further.

These scripts report candidates only. Inspect every finding in context; a
diegetic use, deliberate rhythm, poem line, dialogue beat, or repeated character
focus may be valid. Never optimize prose for a scanner.
