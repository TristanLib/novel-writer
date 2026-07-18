# Novel Writer

`novel-writer` is a single Codex skill for planning, drafting, reviewing,
polishing, and maintaining long-form serialized fiction.

It packages a practical production loop:

- volume, stage, promise/payoff, and multi-chapter planning;
- chapter cards and prose drafting;
- an evidence-backed ordinary-reader retention gate;
- reader-forward cross-chapter continuity review;
- canon, character, capability, evidence, mystery, and hook auditing;
- human-texture prose polish;
- progress, snapshot, and ledger synchronization.

The skill is genre-agnostic by default and includes an optional reference for
historical, institutional, examination, and transmigration fiction.

## Design principles

- Completed prose outranks summaries and plans.
- Every chapter is a reading transaction and must visibly change the reading
  state.
- Reader retention and consistency are separate acceptance gates.
- Project notes may locate evidence but may not repair an on-page gap.
- Any prose edit creates a new text version and invalidates stale review
  results.
- Internal scores are editorial proxies, not promises of market performance.

## Install

Ask Codex to install the skill from:

```text
https://github.com/TristanLib/novel-writer/tree/main/skills/novel-writer
```

Or install it manually:

```bash
git clone https://github.com/TristanLib/novel-writer.git
mkdir -p ~/.codex/skills
cp -R novel-writer/skills/novel-writer ~/.codex/skills/
```

Start a new Codex turn or reload the app after a manual installation so the
skill is rediscovered.

## Use

Invoke it explicitly with `$novel-writer`, for example:

```text
Use $novel-writer to design a 60-chapter volume with a promise/payoff map.
```

```text
Use $novel-writer to continue this novel by one chapter, then run the full
retention and continuity acceptance loop.
```

```text
Use $novel-writer to diagnose why these five chapters feel like setup without
rewriting canon yet.
```

```text
Use $novel-writer to polish this chapter without changing plot facts, evidence
order, capability limits, or the final hook.
```

## Repository layout

```text
skills/novel-writer/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
```

The repository contains one installable skill. Detailed procedures live in
task-specific references so Codex loads only the material needed for the
current writing task.

## License

MIT
