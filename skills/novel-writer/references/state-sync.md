# Project state synchronization

Update durable state only after the final artifact passes every required gate
on its exact current version.

## Discover the project's state model

Use existing equivalents when present:

- progress/status file for completed boundary, live character state, and next
  bridge;
- continuity snapshot for compressed prior events and current resources;
- detailed outline for execution cards and chapter handoffs;
- mystery or evidence ledger for clue provenance and reveal windows;
- text, poem, message, or document ledger for exact wording, attribution,
  carriers, variants, circulation, and backlash;
- domain/rules file for reusable capability and institutional boundaries;
- README or project instructions for durable entry points and collaboration
  rules.

Do not force these filenames on an established project. For a new project, a
compact starting layout may be:

```text
README.md
AGENTS.md
PROGRESS.md
drafts/
docs/
├── series-bible.md
├── character-bible.md
├── style-guide.md
├── volume-outline.md
├── volume-detailed-outline.md
├── continuity-snapshot.md
├── mystery-threads.md
└── domain-bible.md
```

Keep project-specific workflow notes as a thin adapter: record local paths,
canon priority, thresholds, naming rules, and special constraints without
copying this whole skill.

## Update rules

1. **Artifact status:** record the new or revised chapter, story, plan, or asset.
2. **Exact version:** record a content fingerprint or other stable identifier
   for the reviewed text.
3. **Retention:** record four-sentence completion, eight-dimension total,
   lowest-scoring evidence, direct continuation verdict, pass/fail state, and
   required rolling window.
4. **Plot movement:** record only changed evidence, conflict, choice, cost,
   relationship, resource, status, and hook.
5. **Character state:** update only changed knowledge, motive, injury,
   obligation, relationship, resource, or formal position.
6. **Domain state:** record reusable rules and limits, not one-off scene detail.
7. **Mystery state:** preserve first appearance, source, custody, knowers,
   current interpretation, next allowed movement, and forbidden early reveal.
8. **Text state:** preserve exact wording, attribution, carrier, copies,
   variants, audience, propagation, benefit, and source risk.
9. **Hook difference:** when a clue or threat repeats, state what new fact,
   pressure, choice, transfer, or cost the later use adds.
10. **Project promise:** record how the accepted work changes the protagonist
    arc, volume goal, theme, or genre promise when relevant.
11. **Next bridge:** rewrite the next-step section from the final scene's real
    pressure, not the old outline.
12. **Planning state:** update an outline only when accepted prose changes
    sequence, promise, provenance, boundary, or stage assessment.
13. **Entry points:** update README or project instructions only for durable new
    documents, assets, workflows, or collaboration rules.
14. **Version control handoff:** inspect status and report only relevant files;
    commit or publish only when authorized.

## Evidence trace template

```markdown
- ID: Canonical term (variants: A, B)
  First appearance:
  Source/custody:
  Current knowers:
  Latest confirmed use:
  Current interpretation:
  Next verification/payoff window:
  Forbidden early reveal:
  New information beyond the previous hook:
```

## Keep out

- Do not duplicate progress logs across project instructions, README, workflow,
  and progress files.
- Do not summarize every scene; preserve high-signal state.
- Do not leave durable clues only in prose or a temporary review note.
- Do not mark planned events as completed canon.
- Do not update unrelated files because they are nearby.
- Do not stage unrelated user changes.
- Do not convert historical retention scores into the current rubric.
- Do not describe a consistency-only pass as full chapter acceptance.
