# Retention and payoff audit

Use this as a hard editorial gate for completed prose and an explicitly
provisional gate for chapter cards.

## Contents

- Reader return and four-sentence blind recall
- Eight-dimension score and default hard pass
- Setup warnings and rolling gates
- Hook diversity and promise debt
- Cold-reader and live-data validation
- Migration from older rubrics

## Reader return

Require at least one visible reading-state change per chapter:

- concrete success or failure;
- useful answer that changes the next action;
- relationship decision or shifted obligation;
- emotional truth with behavioral consequence;
- resource gained, spent, blocked, or made dangerous;
- public status or interpretation changing;
- irreversible choice or visible price.

Mentioning a future problem is not enough. Learning a clue is weak unless it
changes leverage, choice, risk, relationship, resource, or status.

## Four-sentence blind recall

For completed prose, read without the outline, chapter card, progress file,
ledger, or author explanation. Answer each question in one compact, specific
sentence:

1. What is being sought, contested, protected, decided, or survived now?
2. What definite result has this chapter already delivered?
3. What meaningful choice did a central character make, and what changed?
4. Why would an ordinary serial reader click the next chapter now?

Fail before scoring if an answer can only be `the plot continues`, `more clues
appear`, `things become complicated`, or an explanation from project notes.

## Evidence-backed eight-dimension score

Score every dimension from 0 to 2 and cite the on-page evidence for each
nonzero score. For completed prose, measure opening percentages from body text
only.

An explanation-only paragraph mainly recaps or explains rules, procedure,
evidence limits, setting, or backstory without adding action, resistance,
choice, emotional reaction, or result change.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Reader entry | The immediate goal or pressure remains unclear after the first 20% | Goal is clear by 20%, but obstacle, deadline, desire, or cost is weak | The first 10% establishes a concrete immediate goal/question plus pressure, obstacle, deadline, or cost |
| Promise and same-chapter payoff | Opening promise is postponed, replaced, or answered only with another setup clue | Partial information arrives, but the promised situation barely changes | A bounded answer, result, decision, local win/loss, or explicit state change is delivered while the larger problem may continue |
| Character agency | The central character only arrives, observes, follows, or explains | The character reacts or proposes, but the choice barely affects action or outcome | A meaningful choice changes action, result, risk, relationship, resource, or status |
| Genre or premise payoff | The book's core pleasure exists only in notes, summary, or terminology | A relevant beat appears, but explanation is needed to feel its value | A scene-visible professional, puzzle, action, horror, romance, wonder, comedy, status, or emotional payoff expresses the premise |
| Chapter return | Removing the chapter leaves knowledge, leverage, resource, relationship, status, commitment, interpretation, and cost effectively unchanged | One modest change occurs but is easy to defer or forget | A concrete answer, gain, loss, shift, commitment, interpretation, or cost alters the reading state |
| Human or emotional consequence | Only information, systems, roles, or plot tokens move | A feeling, body, livelihood, shame, duty, desire, or social friction appears but does not affect action | A specific human consequence changes what someone risks, chooses, owes, can do, or must face |
| Pacing and exposition load | Explanation-only material exceeds 40% of paragraphs or runs for 6+ consecutive paragraphs | It occupies 26%-40%, or one block runs for 3-5 paragraphs | It is at most 25% and never runs beyond 2 consecutive paragraphs; explanation is carried by action, conflict, and reaction |
| Next-chapter drive and hook freshness | The reader would stop, or the ending repeats generic danger, a new name, letter, clue, or prior hook shape | The reader might continue later from general curiosity | The reader would click now because a specific action, decision, deadline, confrontation, relationship risk, answer upgrade, or cost has begun, and the hook advances beyond the previous three |

At scoring boundaries, take the lower score. Do not award points because a
later chapter will explain the current one or because the outline labels a beat
important.

## Default hard pass

Require all of:

- four specific blind-recall sentences;
- at least `13/16`;
- no zero dimension;
- `Promise and same-chapter payoff` at `2`;
- `Next-chapter drive and hook freshness` at least `1`;
- score, lowest-scoring evidence, revision action, and exact text or plan
  version recorded;
- deletion test passed.

Missing fields mean failure. A project may set a stricter threshold but should
not silently lower the default.

After scoring, record:

```markdown
Ordinary-reader continuation verdict: continue / hesitate / stop
Most direct click reason or abandonment reason:
Evidence type: editorial proxy / cold-reader sample / live platform data
```

Without actual readers or comparable platform data, label the result
`editorial proxy passed; market not validated`.

For outline cards, cite the planned on-page scene, choice, result, and handoff.
Replace plan scores with prose-based scores after drafting.

## Setup-only warning signs

- characters arrive, recap, and postpone action;
- new names or institutions appear without changing an immediate choice;
- a chapter explains rules that no one tests;
- information moves between people but leverage does not;
- the hook is only another unknown person, letter, footprint, or fragment;
- adjacent chapters keep promising the same future event.

Setup is valid when it carries friction, commitment, cost, or a local result.

## Rolling hard gates

Use windows as diagnostics, not victory quotas.

### Three chapters

- every chapter passes individually;
- no two setup-only chapters occur in a row;
- at least two distinct return types appear;
- no same-shaped hook is used more than twice;
- every chapter states what changes now.

### Five chapters

- all five pass individually;
- total at least `68/80`;
- at least one chapter reaches `15/16`;
- dimension-eight click scores total at least `8/10`, contain no `0`, and do
  not contain consecutive `1`s;
- at least three hook types appear;
- at least one relationship, resource, status, institution, evidence custody,
  or moral position changes in a way the next block must respect;
- at least one tracked promise pays an intermediate dividend;
- pacing/exposition may score `1` in at most two nonconsecutive chapters.

Projects may adopt a stricter five-chapter total, such as `70/80`.

### Ten chapters or one stage

- both five-chapter windows pass;
- dimension-eight click scores total at least `17/20`;
- the final chapter's click score is `2`;
- stage objective is achieved, transformed, or definitively failed;
- the cost survives;
- a relationship, identity, judgment, resource, or power position changes;
- the next stage becomes necessary;
- carried promises receive a new valid payoff window.

If a window fails, revise chapter function, action chain, payoff, or handoff.
Do not add arbitrary cliffhangers, villains, anonymous letters, or unrelated
spectacle.

## Hook diversity

Rotate among:

- concrete deadline;
- material object or text changing hands;
- public ruling or price change;
- relationship decision;
- action already underway;
- revealed cost of a win;
- specific question with a reachable next step;
- moral choice that cannot be postponed.

Repeated mysterious letters, eavesdroppers, anonymous threats, and `a stronger
person noticed` lose force quickly.

## Promise debt

For each promise, ask:

1. Has the reader received an intermediate dividend?
2. Has its meaning or pressure evolved?
3. Is final payoff still aimed at the opening question?
4. If carried forward, is there a fair reason and a new valid window?

Do not repay one promise with unrelated spectacle.

## Cold-reader and live-data validation

When three suitable cold readers are available, show prose only. Ask whether
they would read the next chapter immediately, what they received, what they
expect next, and where they skimmed. Treat `2 of 3 willing to continue`, with
at least two independently naming a concrete return and next question, as a
practical sample pass.

After publication, prefer the platform's comparable retention metric. If only
chapter readership snapshots exist, compare `N+1 / N` and `N+3 / N` under the
same exposure window and similar traffic conditions. After at least ten
comparable observations, use the rolling median as the local baseline. Treat
recommendation traffic, update time, chapter length, outages, and promotions as
confounders. Verify mutable platform thresholds at the time of use.

## Migration from older rubrics

- Apply the current eight-dimension gate to every new, rewritten, or
  structurally expanded chapter.
- Never convert older totals arithmetically or invent retroactive evidence.
- Label existing exact text without a current record as
  `unscored under the current retention gate`.
- Keep earlier continuity acceptance as a separate historical fact.
- Any prose change invalidates the old score, rolling curve, reader-forward
  pass, and formal audit for that version.
