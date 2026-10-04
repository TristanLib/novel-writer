#!/usr/bin/env python3
"""Report warning-only shape candidates in Chinese novel prose.

The scanner never treats punctuation, rhetorical forms, or statistical outliers
as automatic defects. A completed scan exits 0 even when warnings are present.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
SENTENCE_END_RE = re.compile(r"(?<=[。！？!?；;])\s*")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
LEADING_MARK_RE = re.compile(r"^[\s“”‘’「」『』《》〈〉（()【】\[\]，、。！？!?；;：:—–-]+")
DIALOGUE_START_RE = re.compile(r"^[\s]*[“‘「『]")
VISIBLE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fffＡ-ｚA-Za-z0-9]")
TERM_SPLIT_RE = re.compile(r"[\s,，、;；]+")
QUOTE_PAIRS = (("「", "」"), ("『", "』"), ("【", "】"), ("“", "”"), ("‘", "’"), ('"', '"'))
QUOTED_RE = re.compile(
    "|".join(f"{re.escape(start)}[^{re.escape(end)}\n]*{re.escape(end)}" for start, end in QUOTE_PAIRS)
)

FRAME_PATTERNS = {
    "contrast frame": re.compile(
        r"不是.{0,24}而是|并非.{0,24}而是|不在于.{0,24}而在于|"
        r"与其(?![他她它中余])(?:说)?.{0,24}(?:倒)?不如(?:说)?|不只.{0,24}(?:还|也)|看似.{0,24}实则|"
        r"并非|而非|倒不如|与其(?![他她它中余])"
    ),
    "explanatory bridge": re.compile(
        r"这(?:就|也)?说明|这(?:就|也)?意味着|也就是说|换句话说|由此可见|显然"
    ),
    "proof-summary frame": re.compile(
        r"足以说明|足以证明|只能说明|不能证明|尚不能确定|仍待查证|有待核实"
    ),
}

# Shells of the contrast frame. Deleting 不是…而是 often brings the same move
# back as 并非/而非/与其, so the contrast finding lists which shells were used.
CONTRAST_SHELLS = (
    ("不是", "不是…而是"),
    ("并非", "并非"),
    ("不在于", "不在于…而在于"),
    ("与其", "与其…不如"),
    ("不只", "不只…还/也"),
    ("看似", "看似…实则"),
    ("而非", "而非"),
    ("倒不如", "倒不如"),
)

# Negation families, ported from zenstory-ai/oh-story-claudecode
# skills/story-deslop/scripts/check-ai-patterns.js (MIT). They scan narration
# only: quoted speech is masked first, so dialogue never counts.
NEGATION_PAIR_RE = re.compile(
    r"(?:没有|没|不)[^，。！？；,!?\n]{1,10}[，,；]\s*[^，。！？；,!?\n]{0,6}?也(?:没有|没|不)"
)
NEGATION_PARADE_RES = (
    re.compile(r"(?:没有[^。！？!?\n，,]{1,12}[，,]){2}"),
    re.compile(
        r"(?<![沉淹埋出隐湮吞覆漫泯])没(?!有?过?多久)(?:有)?[^。！？!?\n，,]{1,12}[，,]\s*"
        r"没(?!有?过?多久)(?:有)?[^。！？!?\n，,]{1,16}[，,。.][^。！？!?\n，,]{0,6}只(?:是|会|有)"
    ),
)
REVERSE_NOT_IS_RE = re.compile(r"是([^。！？!?\n，,]{1,12})[，,]\s*(?:而)?不是([^。！？!?\n]{1,20})")
NOT_IS_FLIP_RE = re.compile(r"(?<!是)不是[^。！？!?\n，,；;]{1,16}[，,]\s*是")
# 还是/只是/可是… are compounds, not a copula followed by a negated alternative.
REVERSE_NOT_IS_PREV_EXCLUDE = frozenset("不就也还只可但于倒像若要正便总老更最算怕凡或即自竟原本仍许净光单尽")
TAG_QUESTION_CHARS = frozenset("吗么吧嘛")
AFFIRMATION_PARTICLES = frozenset("的啊呀呢")
AFFIRMATION_BOUNDARY = frozenset("，,。.！!？?、；;：: \t\n")
# Constraint narration: a rule restated in place of the scene enacting it.
CONTRACT_NEGATION_RE = re.compile(r"(?:不能|不拿|不凭|不准)[^，。！？；\n]{0,14}(?:替|当作|当成|伸到|补成)")

NEGATION_FAMILIES = {
    "negation-pair": (3, "「没A，也没B」 negation pair"),
    "reverse-not-is": (2, "「是A，不是B」/「不是A，是B」 flip"),
    "negation-parade": (1, "「没有X，没有Y」 negation list"),
    "contract-negation": (3, "「不能/不拿/不凭/不准……替/当作」 constraint narration"),
}
NEGATION_ADVICE = {
    "negation-pair": "show what the character did instead of what they did not, and keep only the denials that carry weight",
    "reverse-not-is": "drop the trailing denial and render A concretely, or let a detail make the contrast",
    "negation-parade": "replace the list of absences with what the scene actually contains; keep at most one telling absence",
    "contract-negation": "check whether the scene enacts the limit instead of restating it as a rule",
}

# Counter-checks against over-correction into telegraphic prose, same source.
OVERCOMPRESSED_PARTICLE_RE = re.compile(r"[的了就着过呢吧啊呀嘛]")
LOW_CONNECTIVE_FUNCTION_TERMS = (
    "的", "了", "就", "在", "是", "也", "都", "还", "又", "把", "被", "给", "这个", "那个",
    "里面", "以后", "时候", "现在", "因为", "所以", "但是", "不过", "然后", "已经", "还是",
    "起来", "出来", "下去",
)
LOW_CONNECTIVE_PLAIN_TERMS = (
    "的", "了", "就", "也", "还", "又", "这个", "那个", "东西", "事情", "时候", "里面",
    "以后", "一下", "一点", "有点", "还是",
)


@dataclass(frozen=True)
class Paragraph:
    line: int
    text: str
    source_lines: int


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    code: str
    message: str
    excerpt: str


def discover_files(paths: list[Path], extensions: set[str]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_file():
            files.add(path.resolve())
            continue
        if not path.is_dir():
            raise FileNotFoundError(path)
        for candidate in path.rglob("*"):
            if (
                candidate.is_file()
                and candidate.suffix.lower() in extensions
                and not any(part.startswith(".") for part in candidate.parts)
            ):
                files.add(candidate.resolve())
    return sorted(files)


def clean_inline(text: str) -> str:
    text = URL_RE.sub("", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def extract_paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    buffer: list[str] = []
    start_line = 0
    in_fence = False
    in_frontmatter = False

    def flush() -> None:
        nonlocal buffer, start_line
        if buffer:
            joined = clean_inline(" ".join(buffer))
            if joined:
                paragraphs.append(Paragraph(start_line, joined, len(buffer)))
        buffer = []
        start_line = 0

    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if line_number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped:
            flush()
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            flush()
            continue
        if stripped.startswith("|") or re.match(r"^\|?\s*:?-{3,}", stripped):
            flush()
            continue
        if re.match(r"^[-*+]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            flush()
            continue
        if stripped.startswith(">"):
            stripped = stripped.lstrip("> ")
        if not buffer:
            start_line = line_number
        buffer.append(stripped)
    flush()
    return paragraphs


def han_count(text: str) -> int:
    return len(HAN_RE.findall(text))


def visible_count(text: str) -> int:
    return len(VISIBLE_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    return [piece.strip() for piece in SENTENCE_END_RE.split(text) if piece.strip()]


def mask_quoted(text: str, fill: str = "？") -> str:
    """Replace quoted spans with same-length filler so offsets and clause breaks survive."""
    return QUOTED_RE.sub(lambda match: fill * len(match.group(0)), text)


def strip_quoted(text: str) -> str:
    return QUOTED_RE.sub("", text)


def load_terms(path: Path) -> list[str]:
    """Read one term per line; '#' starts a comment, and 、/commas/spaces also separate terms."""
    terms: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        terms.update(term for term in TERM_SPLIT_RE.split(line.split("#", 1)[0]) if term)
    return sorted(terms, key=lambda term: (-len(term), term))


def dialogue_start_re(names: list[str]) -> re.Pattern[str]:
    if not names:
        return DIALOGUE_START_RE
    alternation = "|".join(re.escape(name) for name in names)
    return re.compile(
        rf"^[\s]*(?:[“‘「『]|(?:{alternation})[^，。！？；“”「」]{{0,5}}[道问答说喝斥喊叫](?:[：:，,]?\s*[“‘「『]|[：:]))"
    )


def is_dialogue_or_verse(paragraph: Paragraph, dialogue_re: re.Pattern[str] = DIALOGUE_START_RE) -> bool:
    count = han_count(paragraph.text)
    if dialogue_re.search(paragraph.text):
        return True
    if paragraph.source_lines > 1 and count / paragraph.source_lines <= 24:
        return True
    return count <= 24 and not re.search(r"[。！？!?；;]", paragraph.text)


def excerpt(text: str, limit: int = 150) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def sentence_opener(sentence: str) -> str:
    chars = HAN_RE.findall(LEADING_MARK_RE.sub("", sentence))
    return "".join(chars[:6]) if len(chars) >= 6 else ""


def merge_spans(spans: list[tuple[int, int, str]]) -> list[str]:
    merged: list[str] = []
    last_end = -1
    for start, end, text in sorted(spans):
        if start < last_end:
            last_end = max(last_end, end)
            continue
        last_end = end
        merged.append(text)
    return merged


def is_affirmation_tag(text: str, index: int) -> bool:
    return (
        text[index : index + 1] == "是"
        and text[index + 1 : index + 2] in AFFIRMATION_PARTICLES
        and (index + 2 >= len(text) or text[index + 2] in AFFIRMATION_BOUNDARY)
    )


def reverse_not_is_hits(text: str) -> list[str]:
    spans: list[tuple[int, int, str]] = []
    position = 0
    while match := REVERSE_NOT_IS_RE.search(text, position):
        start = match.start()
        position = start + 1
        if start > 0 and text[start - 1] in REVERSE_NOT_IS_PREV_EXCLUDE:
            continue
        if text[start + 1] == "不" or is_affirmation_tag(text, start) or match.group(2)[0] in TAG_QUESTION_CHARS:
            continue
        spans.append((start, match.end(), match.group(0)))
        position = match.end()
    position = 0
    while match := NOT_IS_FLIP_RE.search(text, position):
        shi = match.end() - 1
        position = match.start() + 1
        if text[shi + 1 : shi + 2] in TAG_QUESTION_CHARS or is_affirmation_tag(text, shi):
            continue
        spans.append((match.start(), match.end(), match.group(0)))
        position = match.end()
    return merge_spans(spans)


def negation_family_hits(text: str) -> dict[str, list[str]]:
    parade = [
        (match.start(), match.end(), match.group(0))
        for pattern in NEGATION_PARADE_RES
        for match in pattern.finditer(text)
    ]
    return {
        "negation-pair": [match.group(0) for match in NEGATION_PAIR_RE.finditer(text)],
        "reverse-not-is": reverse_not_is_hits(text),
        "negation-parade": merge_spans(parade),
        "contract-negation": [match.group(0) for match in CONTRACT_NEGATION_RE.finditer(text)],
    }


def per_10k(hits: int, characters: int) -> float:
    return round(hits / characters * 10000, 2) if characters else 0.0


def contrast_breakdown(matches: list[str]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for match in matches:
        label = next((label for prefix, label in CONTRAST_SHELLS if match.startswith(prefix)), match)
        counts[label] += 1
    return ", ".join(f"{label} {count}" for label, count in sorted(counts.items(), key=lambda item: -item[1]))


def overcompressed_finding(path: Path, paragraphs: list[Paragraph]) -> Finding | None:
    lengths: list[int] = []
    particles = 0
    first_line = 0
    samples: list[str] = []
    for paragraph in paragraphs:
        if re.fullmatch(r"【[^】]+】", paragraph.text):
            continue
        narration = strip_quoted(paragraph.text).strip()
        length = visible_count(narration)
        if not length:
            continue
        first_line = first_line or paragraph.line
        lengths.append(length)
        particles += len(OVERCOMPRESSED_PARTICLE_RE.findall(narration))
        if length <= 15 and len(samples) < 4:
            samples.append(narration)
    characters = sum(lengths)
    if characters < 1200 or len(lengths) < 45:
        return None
    short_ratio = sum(length <= 15 for length in lengths) / len(lengths)
    particle_rate = particles / characters * 1000
    if short_ratio < 0.58 or particle_rate >= 85:
        return None
    return Finding(str(path), first_line, "overcompressed-prose", f"{short_ratio:.0%} of {len(lengths)} narration paragraphs have 15 or fewer characters and natural particles run {particle_rate:.1f} per 1000; reread for outline-like breaks before adding connectives, and keep deliberate short shots", excerpt(" | ".join(samples)))


def low_connective_finding(path: Path, paragraphs: list[Paragraph]) -> Finding | None:
    characters = function_hits = plain_hits = 0
    first_line = 0
    sentence_lengths: list[int] = []
    samples: list[str] = []
    for paragraph in paragraphs:
        narration = strip_quoted(paragraph.text).strip()
        length = visible_count(narration)
        if not length:
            continue
        first_line = first_line or paragraph.line
        characters += length
        function_hits += sum(narration.count(term) for term in LOW_CONNECTIVE_FUNCTION_TERMS)
        plain_hits += sum(narration.count(term) for term in LOW_CONNECTIVE_PLAIN_TERMS)
        for sentence in re.split(r"[。！？!?]", narration):
            if sentence_length := visible_count(sentence):
                sentence_lengths.append(sentence_length)
                if sentence_length <= 12 and len(samples) < 4:
                    samples.append(sentence.strip())
    if characters < 800 or not sentence_lengths:
        return None
    function_rate = function_hits / characters * 1000
    plain_rate = plain_hits / characters * 1000
    long_ratio = sum(length >= 30 for length in sentence_lengths) / len(sentence_lengths)
    if function_rate >= 100 or plain_rate >= 65 or long_ratio >= 0.08:
        return None
    return Finding(str(path), first_line, "low-connective-density", f"narration function words run {function_rate:.1f} per 1000 and plain connectives {plain_rate:.1f} per 1000, with {long_ratio:.0%} of sentences at 30+ characters; reread for telegraphic flow before restoring needed links", excerpt(" | ".join(samples)))


def scan_file(path: Path, text: str, dialogue_re: re.Pattern[str] = DIALOGUE_START_RE) -> tuple[dict[str, object], list[Finding]]:
    paragraphs = extract_paragraphs(text)
    findings: list[Finding] = []
    narrative = [p for p in paragraphs if not is_dialogue_or_verse(p, dialogue_re) and han_count(p.text) >= 12]
    sentences = [
        (paragraph, sentence)
        for paragraph in paragraphs
        for sentence in split_sentences(paragraph.text)
    ]

    for paragraph, sentence in sentences:
        count = han_count(sentence)
        if count >= 90:
            findings.append(Finding(str(path), paragraph.line, "long-sentence", f"sentence carries {count} Han characters; confirm that its actor and action remain visible", excerpt(sentence)))
        de_count = sentence.count("的")
        if count >= 28 and de_count >= 4 and de_count / max(count, 1) >= 0.055:
            findings.append(Finding(str(path), paragraph.line, "dense-modifiers", f"sentence contains {de_count} uses of 的 across {count} Han characters; inspect the modifier chain", excerpt(sentence)))

    openers: dict[str, list[Paragraph]] = defaultdict(list)
    for paragraph, sentence in sentences:
        if han_count(sentence) >= 12 and (opener := sentence_opener(sentence)):
            openers[opener].append(paragraph)
    for opener, hits in sorted(openers.items()):
        if len(hits) >= 3:
            findings.append(Finding(str(path), hits[0].line, "repeated-opener", f"sentence opener {opener!r} appears {len(hits)} times; retain it only if repetition serves voice or focus", excerpt(hits[0].text)))

    for label, pattern in FRAME_PATTERNS.items():
        hits = [
            (paragraph, match.group(0))
            for paragraph, sentence in sentences
            for match in pattern.finditer(sentence)
        ]
        if len(hits) >= 3:
            first_paragraph, first_match = hits[0]
            shells = f" [{contrast_breakdown([match for _, match in hits])}]" if label == "contrast frame" else ""
            findings.append(Finding(str(path), first_paragraph.line, "repeated-frame", f"{label} appears {len(hits)} times{shells}; inspect cadence and paragraph function rather than banning the form", excerpt(first_match)))

    narration_characters = 0
    family_hits: dict[str, list[tuple[Paragraph, str]]] = {code: [] for code in NEGATION_FAMILIES}
    for paragraph in paragraphs:
        masked = mask_quoted(paragraph.text)
        narration_characters += han_count(masked)
        for code, matches in negation_family_hits(masked).items():
            family_hits[code].extend((paragraph, match) for match in matches)
    for code, (minimum, label) in NEGATION_FAMILIES.items():
        hits = family_hits[code]
        if len(hits) >= minimum:
            findings.append(Finding(str(path), hits[0][0].line, code, f"{label} appears {len(hits)} time(s) in narration ({per_10k(len(hits), narration_characters)} per 10k Han characters); {NEGATION_ADVICE[code]}", excerpt(" | ".join(match for _, match in hits[:3]))))

    for finding in (overcompressed_finding(path, paragraphs), low_connective_finding(path, paragraphs)):
        if finding:
            findings.append(finding)

    lengths = [han_count(p.text) for p in narrative]
    single_count = sum(len(split_sentences(p.text)) == 1 for p in narrative)
    single_ratio = single_count / len(narrative) if narrative else 0.0
    if len(narrative) >= 8 and single_ratio >= 0.75:
        findings.append(Finding(str(path), narrative[0].line, "short-paragraph-drumbeat", f"{single_ratio:.0%} of {len(narrative)} narrative paragraphs contain one sentence; verify that the drumbeat is earned", excerpt(narrative[0].text)))

    variation = None
    if len(lengths) >= 10:
        mean = sum(lengths) / len(lengths)
        variance = sum((value - mean) ** 2 for value in lengths) / len(lengths)
        variation = math.sqrt(variance) / mean if mean else None
        if variation is not None and mean >= 24 and variation <= 0.28:
            findings.append(Finding(str(path), narrative[0].line, "uniform-paragraph-shape", f"narrative paragraph length has low variation (CV={variation:.2f}); compare action, thought, and dialogue rhythms", excerpt(narrative[0].text)))

    summary: dict[str, object] = {
        "path": str(path),
        "han_characters": han_count("\n".join(p.text for p in paragraphs)),
        "paragraphs": len(paragraphs),
        "narrative_paragraphs": len(narrative),
        "narrative_single_sentence_ratio": round(single_ratio, 4),
        "narrative_length_cv": round(variation, 4) if variation is not None else None,
        "narration_han_characters": narration_characters,
        "family_hits": {code: len(hits) for code, hits in family_hits.items()},
        "family_per_10k": {code: per_10k(len(hits), narration_characters) for code, hits in family_hits.items()},
        "warnings": len(findings),
    }
    return summary, findings


def book_summary(summaries: list[dict[str, object]]) -> dict[str, object]:
    characters = sum(int(summary["narration_han_characters"]) for summary in summaries)
    families: dict[str, dict[str, float | int]] = {}
    for code in NEGATION_FAMILIES:
        counts = [summary["family_hits"][code] for summary in summaries]
        families[code] = {
            "hits": sum(counts),
            "per_10k": per_10k(sum(counts), characters),
            "chapters_hit": sum(count > 0 for count in counts),
        }
    return {"chapters": len(summaries), "narration_han_characters": characters, "families": families}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--extensions", default=".md,.txt")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--names", type=Path, help="character names, one per line; lets 林川道：“……” count as dialogue")
    args = parser.parse_args()

    extensions = {
        value if value.startswith(".") else f".{value}"
        for raw in args.extensions.split(",")
        if (value := raw.strip().lower())
    }
    try:
        files = discover_files(args.paths, extensions)
    except FileNotFoundError as error:
        parser.error(f"path not found: {error}")
    try:
        dialogue_re = dialogue_start_re(load_terms(args.names) if args.names else [])
    except (OSError, UnicodeDecodeError) as error:
        parser.error(f"unreadable names file: {error}")

    summaries: list[dict[str, object]] = []
    findings: list[Finding] = []
    unreadable: list[str] = []
    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            unreadable.append(f"{path}: {error}")
            continue
        summary, file_findings = scan_file(path, content, dialogue_re)
        summaries.append(summary)
        findings.extend(file_findings)

    book = book_summary(summaries)
    if args.json:
        print(json.dumps({"files": summaries, "book": book, "findings": [asdict(item) for item in findings], "unreadable": unreadable, "policy": "warnings_only"}, ensure_ascii=False, indent=2))
    else:
        for summary in summaries:
            print("INFO: {path}: {han_characters} Han chars, {paragraphs} prose paragraphs, {narrative_paragraphs} narrative paragraphs, {warnings} warning(s)".format(**summary))
        for item in findings:
            print(f"WARN: {item.path}:{item.line}: [{item.code}] {item.message}: {item.excerpt}")
        if len(summaries) > 1:
            print(f"BOOK: {book['chapters']} chapters, {book['narration_han_characters']} narration Han characters")
            for code, family in book["families"].items():
                print(f"BOOK: [{code}] {family['hits']} hit(s), {family['per_10k']} per 10k, in {family['chapters_hit']}/{book['chapters']} chapters")
        for message in unreadable:
            print(f"ERROR: unreadable: {message}", file=sys.stderr)
        print("NOTE: findings are contextual reread prompts. The scanner bans no punctuation or rhetorical form and never acts as an acceptance gate.")
    return 2 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main())
