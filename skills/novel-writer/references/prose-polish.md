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
pressure before a turn. Use short beats only where the scene earns them.

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
- Treat any prose edit as a new exact text version.

After polishing, rerun the full retention gate, reader-forward continuity, and
formal audit. Do not report the chapter accepted until the polished version
passes all applicable gates.
