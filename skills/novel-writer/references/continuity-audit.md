# Reader-forward continuity and formal audit

Use this reference after drafting and before accepting new or substantially
revised prose. Retention and consistency are independent gates.

## Contents

- Linked reading window and reader-forward pass
- Formal checklist
- Severity rules
- Evidence tables
- Output format

## Build the linked reading window

Include:

- target chapter;
- immediate bridge chapter or preceding scene;
- earlier chapters where each central relationship was introduced or last
  materially changed;
- earlier chapters where each central object or piece of evidence was
  introduced, transferred, reinterpreted, or last used;
- earlier chapters where an important poem, message, document, or text was
  introduced or changed.

Add more chapters only when a transition cannot otherwise be verified. Avoid
unbounded full-book rereads.

## Read forward as an ordinary reader

Read the selected chapters from earliest to latest and finish with the target.
Judge what the prose communicates before consulting summaries.

Trace:

- **Characters:** relationship state, knowledge, motive, obligation, injury,
  resources, title or form of address, and last meaningful interaction.
- **Objects and evidence:** source, physical condition, custody, access,
  observers, transfer, interpretation, and allowed next use.
- **Poems and texts:** exact wording, attribution, written or oral carrier,
  copies, variants or errors, audience, spread, effect, and backlash.
- **Causality:** time, location, scene access, promise, choice, cost, unresolved
  action, and whether the next action follows naturally.

Flag:

- relationship change without an on-page bridge;
- object teleportation or unexplained physical-state change;
- knowledge without a source;
- text wording, attribution, carrier, or audience changing without explanation;
- time, place, access, or consequence being forgotten;
- project notes being required to understand what happened.

Correct before grading. Then reread the linked window in order. Do not proceed
to formal acceptance while the reader pass depends on an external explanation.

When three or more similar-looking, similarly named, or same-type objects occur
in one window, create an internal object table:

| Stable label | Contents/state | Source | Carrier | Custodian | Transfer scene | Knowers | Current disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |

The prose need not show the table, but readers must be able to distinguish each
object through stable wording or physical detail.

## Formal checklist

1. **Chapter function:** advance new information, conflict, choice, or cost.
2. **Continuity:** verify identities, duties, secrets, evidence, injuries,
   resources, relationships, locations, and time pressure.
3. **Character fit:** require scene-level pressure, motive, ignorance, fear,
   debt, loyalty, injury, or desire for unusual behavior.
4. **POV and identity boundaries:** verify names, pronouns, memories,
   assumptions, disguise, possession, rebirth, amnesia, and secret knowledge.
5. **Capability and resources:** reject unearned tools, authority, access,
   allies, money, status, technology, knowledge, powers, or perfect deductions.
6. **Domain causality:** follow established professional, legal, medical,
   financial, technical, combat, and institutional rules.
7. **Sensitive zones:** require conditions and cost before core secrets,
   forbidden records, major antagonists, command centers, key ledgers, or
   truth-core material.
8. **Evidence provenance:** verify source, custody, access, observers,
   interpretation, and future reveal boundary.
9. **Reverse search:** check variants, first appearance, prior wording,
   repeated reveals, and custody gaps.
10. **Mystery pacing:** add evidence, contradiction, pressure, or cost without
    solving the long mystery prematurely.
11. **Hook novelty:** compare with the previous three endings; require new
    information, danger, choice, witness, transfer, deadline, or cost.
12. **Narrative immersion:** remove chapter-navigation references, file paths,
    outline terms, workflow notes, and author- or reader-facing language from
    body prose.
13. **Project promise:** serve premise, protagonist arc, volume goal, theme, or
    genre promise rather than only move plot tokens.

Run `scripts/scan_prose_meta.py` on revised manuscript files and inspect each
candidate.

## Severity

- **P0:** breaks canon, creates impossible causality, violates hard capability
  or domain rules, reveals forbidden truth too early, or requires major rewrite
  before continuation.
- **P1:** materially weakens continuity, evidence, motivation, access,
  capability, mystery pacing, or reader comprehension and should be fixed now.
- **P2:** polish, clarity, emphasis, hook strength, or ledger hygiene issue that
  does not block the chapter.

Fix P0 immediately. Fix P1 before acceptance unless the user explicitly defers
it with a recorded reason. Handle P2 during polish or record accepted residual
risk.

Any prose or factual correction invalidates the current retention score,
rolling window, reader-forward pass, and formal audit. Restart on the revised
version.

## Evidence tables

Use when durable details appear:

```markdown
Key object/evidence/text trace:
| Item | First appearance | Latest change | Current use | Knowers/custody | Reverse-search result | Handling |
| --- | --- | --- | --- | --- | --- | --- |

Ending-hook comparison:
- Previous three hooks:
- Current hook's new information:
- Result: distinct / revised into new pressure, evidence, choice, or cost
```

## Output format

Lead with the gate state, then findings ordered by severity:

```markdown
Retention gate:
- Status: pass / fail / not evaluated
- Four-sentence recall: complete / incomplete
- Eight scores and total:
- Exact text version:
- Continuation verdict: continue / hesitate / stop
- Lowest-scoring evidence:

Reader-forward pass:
- Linked chapters:
- Selection reasons:
- Result: coherent / corrected / still needs revision

P0/P1/P2 - Finding title
Location:
Problem:
Recommended correction:

Final acceptance:
- Review round and exact version:
- Retention gate:
- Reader-forward continuity:
- Formal audit:
- Applicable rolling window:
- Result: accepted / revise and rerun / diagnosis only
```

Do not declare full chapter acceptance when retention was not evaluated,
failed, or became stale after an edit.
