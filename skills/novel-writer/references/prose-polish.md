# Prose polish

Polish prose without silently changing the story contract. Preserve plot
facts, evidence order, character choices, capability limits, domain logic,
relationship state, and intended next hook unless the user requests a rewrite.

Read the target chapter, current state, and relevant voice, mystery, and domain
guidance before editing.

## Passes

### 1. Restore human texture

Cut:

- generic explanation;
- repetitive sentence frames;
- over-neat summaries;
- slogan-like theme statements;
- narration that tells readers what the scene already proves;
- dialogue where every speaker uses the same logic-first cadence;
- clues summarized more often than experienced.

Prefer:

- concrete gesture and object;
- fatigue, pain, impatience, embarrassment, hunger, and practical inconvenience;
- partial knowledge and interrupted thought;
- status pressure, awkward silence, local idiom, and social friction;
- small decisions that reveal motive.

Do not add new facts merely to create texture.

### 1a. Make paragraphs advance

Label each paragraph privately by its main job: action, perception, dialogue
move, new fact, distinction, decision, consequence, pressure, or transition.
Every new paragraph should add something or deliberately change rhythm.

- Compress the paragraph to one clause. If the clause duplicates its neighbour,
  merge, cut, or expose the new consequence.
- Remove it temporarily. If action, knowledge, relationship, pressure, and
  rhythm all remain unchanged, it may be ornamental.
- Check the handoff. The next paragraph should answer, complicate, redirect, or
  act on something left by the previous one.

A pause, silence, or sensory beat can still change pressure. Judge function, not
event count.

### 1b. Keep the Chinese sentence spine visible

When a sentence is hard to parse, bring the actor, object, or decisive action
forward. Split stacked conditions when they matter independently. Turn one
layer of a dense `的` chain into a verb, a concrete relation, or a separate
sentence. Keep long sentences when accumulation creates pressure and readers
can still find the grammatical spine.

For `他`, `她`, `他们`, `这`, `那`, `此事`, and omitted subjects, verify that a
reader can recover the referent without project notes. Repeat a name after a
scene turn, a long interruption, or when same-gender characters compete for the
same pronoun.

Use `scripts/audit_prose_shape.py` to locate statistical candidates, then judge
the quoted prose manually. Its negation families (`没A，也没B`, `是A，不是B`,
`没有X，没有Y`, and `不能/不拿/不凭……替/当作` constraint narration) scan narration only.
When the contrast-frame warning lists `并非`, `而非`, or `与其`, the frame has
changed shells rather than gone away. `overcompressed-prose` and
`low-connective-density` flag the opposite failure, prose cut down to outline
beats. Use `scripts/discover_tics.py` for repeated phrases that no fixed pattern
covers.

### 1c. Filter detail through viewpoint

A detail should reveal attention, alter action, establish material conditions,
distinguish an object, create pressure, expose status, or prepare a consequence.
Let the viewpoint character notice what their goal, trade, fear, injury, desire,
or misconception makes salient. If action, wording, bodily response, or silence
already carries the emotion, remove the immediate explanation and reread. Keep
the explanation when the interpretation itself is new, disputed, or revealing.

### 2. Remove meta-language

Remove project-facing or author-facing language from publishable body prose,
including chapter-navigation numbers, outline labels, file names, workflow
terms, `this chapter`, `previous chapter`, `next chapter`, `the reader`,
`foreshadowing`, `main plot`, `subplot`, and `ending hook`.

Use `scripts/scan_prose_meta.py` and inspect each candidate.

### 3. Strengthen world-specific detail

Replace generic mood words with concrete objects, work, institutions, sensory
pressure, social rules, and material consequences established by the project.

### 4. Sharpen pressure

Make time, money, rank, reputation, law, health, uncertainty, resources, and
relationship costs visible through action and response.

### 5. Differentiate dialogue

Give every speaker a goal, pressure, knowledge boundary, and withholding
pattern. Avoid dialogue that exists only to explain plot.

### 6. Tune rhythm

Vary paragraph length. Let procedural, sensory, and social detail build
pressure before a turn. Use short beats only where the scene earns them. Read
the scene aloud; mark repeated paragraph landings, unearned short-paragraph
drumbeats, and stretches where action, thought, and dialogue all use the same
weight.

### 7. Improve clue visibility

Present clues as objects, contradictions, omissions, phrasing, variants,
repeated details, or custody changes. Do not explain their final meaning too
early.

### 8. Strengthen premise payoff

Make the scene better express the book's core pleasure, protagonist arc,
volume goal, theme, or genre promise without turning theme into a slogan.

### 9. Strengthen the final hook

End on a concrete action, decision, deadline, confrontation, relationship risk,
answer upgrade, command, discovery, or cost. Compare with the previous three
ending shapes.

### 10. Give breathable confirmation

In clue-heavy prose, provide at least one clear local takeaway, partial answer,
emotional consequence, practical result, or changed choice. Do not end every
scene by adding another unexplained token.

## Constraints

- Follow the project's length target.
- Do not grant unearned capability, authority, resources, or access.
- Do not remove conditions that justify sensitive access.
- Do not add lore, solve a conflict early, move evidence order, or replace the
  hook unless a rewrite is requested.
- Do not de-mechanize with ornamental filler, random dialect, fake disorder, or
  unrelated banter.
- Do not ban ordinary colons, dashes, contrast frames, parallelism, dialogue
  tags, one-sentence paragraphs, or poem lines. Diagnose repeated function and
  cadence in context; never rewrite merely to clear a token count.
- Treat any prose edit as a new exact text version.

After polishing, rerun the full retention gate, reader-forward continuity, and
formal audit. Do not report the chapter accepted until the polished version
passes all applicable gates.

Several paragraph and rhythm diagnostics were adapted and generalized from the
MIT-licensed [human-writing project](https://github.com/KKKKhazix/human-writing/tree/22d20b672680e4c1a34e75aec550ff48d622ca59).
Its universal punctuation and phrase prohibitions are intentionally excluded.
