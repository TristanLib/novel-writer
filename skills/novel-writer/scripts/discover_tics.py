#!/usr/bin/env python3
"""Rank Chinese n-grams that a target manuscript over- or under-uses against a baseline.

Slop forensics without word segmentation: count 2-4 character Han n-grams in
narration only (quoted speech removed), compare target against baseline with a
smoothed log-odds z-score, and print a ranked TSV. The script reports
candidates for a human to read in context; it does not prove that a phrase is
an AI tic. Use a human-written baseline when one is available. A baseline of
the author's other books only finds book-specific habits.

Sections:
  over   n-grams the target uses more often than the baseline, highest z first
  under  n-grams the baseline uses more often, lowest z first; checks whether
         revision has stripped ordinary figures or questions from the target
  probe  fixed comparison markers (simile words, questions, ellipses), always printed
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_prose_shape import QUOTED_RE, discover_files, extract_paragraphs, han_count, load_terms  # noqa: E402

HAN_RUN_RE = re.compile(r"[㐀-䶿一-鿿]+")
SEPARATOR = "\n"
ALPHA = 0.5
SUPERSTRING_SHARE = 0.8
PROBES = ("像", "仿佛", "似乎", "好像", "如同", "宛如", "犹如", "似的", "一般", "？", "！", "吗", "呢", "……", "——")
PROBE_ALIASES = {"？": ("？", "?"), "！": ("！", "!")}
COLUMNS = (
    "section",
    "ngram",
    "n",
    "z",
    "target_count",
    "target_per_10k",
    "baseline_count",
    "baseline_per_10k",
    "target_chapters",
    "baseline_chapters",
    "example",
)


@dataclass
class Corpus:
    narration: list[str] = field(default_factory=list)
    counts: Counter[str] = field(default_factory=Counter)
    chapters: Counter[str] = field(default_factory=Counter)
    totals: Counter[int] = field(default_factory=Counter)
    han_characters: int = 0


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("gb18030")


def narration_paragraphs(text: str) -> list[str]:
    # A separator rather than a question mark keeps removed speech out of the
    # punctuation probes and stops the text on either side from fusing.
    return [QUOTED_RE.sub(SEPARATOR, paragraph.text) for paragraph in extract_paragraphs(text)]


def chunk_paragraphs(paragraphs: list[str], chunk_chars: int) -> list[str]:
    if chunk_chars <= 0:
        return [SEPARATOR.join(paragraphs)]
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for paragraph in paragraphs:
        current.append(paragraph)
        size += han_count(paragraph)
        if size >= chunk_chars:
            chunks.append(SEPARATOR.join(current))
            current, size = [], 0
    if current:
        if chunks:
            chunks[-1] += SEPARATOR + SEPARATOR.join(current)
        else:
            chunks.append(SEPARATOR.join(current))
    return chunks


def mask_terms(text: str, pattern: re.Pattern[str] | None) -> str:
    return pattern.sub(SEPARATOR, text) if pattern else text


def build_corpus(paths: list[Path], lengths: range, chunk_chars: int, exclude: re.Pattern[str] | None) -> Corpus:
    corpus = Corpus()
    for path in paths:
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError) as error:
            print(f"NOTE: skipped unreadable file {path}: {error}", file=sys.stderr)
            continue
        for chunk in chunk_paragraphs(narration_paragraphs(text), chunk_chars):
            corpus.narration.append(chunk)
            corpus.han_characters += han_count(chunk)
            seen: set[str] = set()
            for run in HAN_RUN_RE.findall(mask_terms(chunk, exclude)):
                for n in lengths:
                    for start in range(len(run) - n + 1):
                        gram = run[start : start + n]
                        corpus.counts[gram] += 1
                        seen.add(gram)
                    corpus.totals[n] += max(0, len(run) - n + 1)
            corpus.chapters.update(seen)
    return corpus


def log_odds_z(target_hits: int, target_total: int, baseline_hits: int, baseline_total: int) -> float:
    target_odds = (target_hits + ALPHA) / (max(target_total - target_hits, 0) + ALPHA)
    baseline_odds = (baseline_hits + ALPHA) / (max(baseline_total - baseline_hits, 0) + ALPHA)
    delta = math.log(target_odds) - math.log(baseline_odds)
    return delta / math.sqrt(1 / (target_hits + ALPHA) + 1 / (baseline_hits + ALPHA))


def per_10k(hits: int, characters: int) -> str:
    return f"{hits / characters * 10000:.2f}" if characters else "0.00"


def suppress_substrings(candidates: dict[str, int]) -> set[str]:
    """Drop a shorter n-gram when a longer candidate containing it carries most of its count."""
    dropped: set[str] = set()
    for longer, count in candidates.items():
        for n in range(2, len(longer)):
            for start in range(len(longer) - n + 1):
                shorter = longer[start : start + n]
                if shorter in candidates and count >= SUPERSTRING_SHARE * candidates[shorter]:
                    dropped.add(shorter)
    return dropped


def example(corpus: Corpus, needle: str, radius: int = 14) -> str:
    for text in corpus.narration:
        index = text.find(needle)
        if index >= 0:
            snippet = text[max(0, index - radius) : index + len(needle) + radius]
            return " ".join(snippet.split())
    return ""


def ranked_rows(section: str, target: Corpus, baseline: Corpus, args: argparse.Namespace) -> list[list[str]]:
    source = target if section == "over" else baseline
    scored: dict[str, float] = {}
    for gram in source.counts:
        if source.counts[gram] < args.min_count or source.chapters[gram] < args.min_chapters:
            continue
        n = len(gram)
        z = log_odds_z(target.counts[gram], target.totals[n], baseline.counts[gram], baseline.totals[n])
        if (z > 0) == (section == "over") and z != 0:
            scored[gram] = z
    dropped = suppress_substrings({gram: source.counts[gram] for gram in scored})
    ordered = sorted((gram for gram in scored if gram not in dropped), key=lambda gram: (-abs(scored[gram]), gram))
    return [row(section, gram, scored[gram], target, baseline, source) for gram in ordered[: args.top]]


def row(section: str, gram: str, z: float, target: Corpus, baseline: Corpus, source: Corpus) -> list[str]:
    return [
        section,
        gram,
        str(len(gram)),
        f"{z:.2f}",
        str(target.counts[gram]),
        per_10k(target.counts[gram], target.han_characters),
        str(baseline.counts[gram]),
        per_10k(baseline.counts[gram], baseline.han_characters),
        str(target.chapters[gram]),
        str(baseline.chapters[gram]),
        example(source, gram),
    ]


def probe_rows(target: Corpus, baseline: Corpus) -> list[list[str]]:
    rows: list[list[str]] = []
    for marker in PROBES:
        forms = PROBE_ALIASES.get(marker, (marker,))
        counts = []
        chapters = []
        for corpus in (target, baseline):
            per_chapter = [sum(text.count(form) for form in forms) for text in corpus.narration]
            counts.append(sum(per_chapter))
            chapters.append(sum(count > 0 for count in per_chapter))
        z = log_odds_z(counts[0], target.han_characters, counts[1], baseline.han_characters)
        source = target if counts[0] >= counts[1] else baseline
        rows.append([
            "probe",
            marker,
            str(len(marker)),
            f"{z:.2f}",
            str(counts[0]),
            per_10k(counts[0], target.han_characters),
            str(counts[1]),
            per_10k(counts[1], baseline.han_characters),
            str(chapters[0]),
            str(chapters[1]),
            example(source, forms[0]),
        ])
    return rows


def parse_lengths(value: str) -> range:
    match = re.fullmatch(r"(\d+)(?:-(\d+))?", value.strip())
    if not match:
        raise argparse.ArgumentTypeError("use N or N-M, for example 2-4")
    low = int(match.group(1))
    high = int(match.group(2) or low)
    if not 1 <= low <= high <= 8:
        raise argparse.ArgumentTypeError("lengths must satisfy 1 <= N <= M <= 8")
    return range(low, high + 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--target", nargs="+", type=Path, required=True, help="chapters or directories to inspect")
    parser.add_argument("--baseline", nargs="+", type=Path, required=True, help="comparison chapters or directories, ideally human-written")
    parser.add_argument("--n", type=parse_lengths, default=range(2, 5), help="n-gram lengths, default 2-4")
    parser.add_argument("--min-chapters", type=int, default=3, help="drop n-grams found in fewer chapters on the ranked side")
    parser.add_argument("--min-count", type=int, default=5, help="drop n-grams with fewer hits on the ranked side")
    parser.add_argument("--exclude", type=Path, help="glossary of names and coined terms to mask, one per line")
    parser.add_argument("--chunk-chars", type=int, default=0, help="split each file into chunks of at least this many Han characters")
    parser.add_argument("--top", type=int, default=50, help="rows per ranked section")
    parser.add_argument("--extensions", default=".md,.txt", help="comma-separated extensions to scan inside directories")
    args = parser.parse_args()

    extensions = {item if item.startswith(".") else f".{item}" for item in args.extensions.split(",") if item}
    try:
        target_files = discover_files(args.target, extensions)
        baseline_files = discover_files(args.baseline, extensions)
    except FileNotFoundError as error:
        parser.error(f"path not found: {error}")
    if not target_files or not baseline_files:
        parser.error("both --target and --baseline need at least one readable file")
    exclude = None
    if args.exclude:
        try:
            terms = load_terms(args.exclude)
        except (OSError, UnicodeDecodeError) as error:
            parser.error(f"unreadable glossary: {error}")
        if terms:
            exclude = re.compile("|".join(re.escape(term) for term in terms))

    target = build_corpus(target_files, args.n, args.chunk_chars, exclude)
    baseline = build_corpus(baseline_files, args.n, args.chunk_chars, exclude)
    print(
        f"NOTE: target {len(target.narration)} chapter(s), {target.han_characters} narration Han characters; "
        f"baseline {len(baseline.narration)} chapter(s), {baseline.han_characters}",
        file=sys.stderr,
    )

    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(COLUMNS)
    writer.writerows(ranked_rows("over", target, baseline, args))
    writer.writerows(ranked_rows("under", target, baseline, args))
    writer.writerows(probe_rows(target, baseline))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
