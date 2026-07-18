#!/usr/bin/env python3
"""Scan publishable prose for project-facing or author-facing language.

Findings are review candidates, not automatic proof of an error. The script
returns status 1 when candidates exist unless --no-fail is supplied.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CandidatePattern:
    label: str
    regex: re.Pattern[str]


PATTERNS = (
    CandidatePattern(
        "chapter navigation",
        re.compile(
            r"第[0-9０-９零〇一二三四五六七八九十百千]+章|"
            r"\bchapter\s+\d{1,4}\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "workflow language",
        re.compile(
            r"本章|上一章|下一章|前一章|后一章|前文|后文|"
            r"章末|伏笔|主线|支线|剧情|章卡|追读|复审|"
            r"\bthis chapter\b|\bprevious chapter\b|\bnext chapter\b|"
            r"\bchapter card\b|\bending hook\b|\bretention gate\b|"
            r"\breview gate\b|\bmain plot\b|\bsubplot\b|\bforeshadowing\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "reader or author address",
        re.compile(r"读者|作者|\bthe reader\b|\bthe author\b", re.IGNORECASE),
    ),
    CandidatePattern(
        "project file or path",
        re.compile(
            r"(?:^|[\s`'\"(])(?:drafts|docs|manuscripts|references)/|"
            r"\b(?:PROGRESS|AGENTS|README)\.md\b|"
            r"\bvolume-[0-9a-z._/-]+\b|\bchapter-[0-9a-z._/-]+\b",
            re.IGNORECASE,
        ),
    ),
    CandidatePattern(
        "review severity label",
        re.compile(r"(?<![A-Za-z0-9])P[012](?![A-Za-z0-9])"),
    ),
)


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--extensions",
        default=".md,.txt",
        help="comma-separated extensions when scanning directories",
    )
    parser.add_argument(
        "--allow-pattern",
        action="append",
        default=[],
        help="regex for lines to suppress; may be repeated",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="return status 0 even when candidates are found",
    )
    args = parser.parse_args()

    extensions = {
        value.strip().lower()
        for value in args.extensions.split(",")
        if value.strip()
    }
    extensions = {
        value if value.startswith(".") else f".{value}" for value in extensions
    }
    allow_patterns = [
        re.compile(value, re.IGNORECASE) for value in args.allow_pattern
    ]

    try:
        files = discover_files(args.paths, extensions)
    except FileNotFoundError as error:
        parser.error(f"path not found: {error}")

    if not files:
        print("No matching prose files found.")
        return 0

    findings = 0
    unreadable = 0
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            unreadable += 1
            print(f"WARN: skipped non-UTF-8 file: {path}", file=sys.stderr)
            continue

        for line_number, line in enumerate(lines, start=1):
            if (
                line_number == 1
                and re.match(r"^\s*#{1,6}\s+", line)
            ):
                continue
            if any(pattern.search(line) for pattern in allow_patterns):
                continue
            for candidate in PATTERNS:
                match = candidate.regex.search(line)
                if not match:
                    continue
                findings += 1
                excerpt = line.strip()
                if len(excerpt) > 220:
                    excerpt = excerpt[:217] + "..."
                print(
                    f"{path}:{line_number}: [{candidate.label}] "
                    f"{match.group(0)!r}: {excerpt}"
                )

    print(
        f"Scanned {len(files)} file(s); found {findings} candidate(s); "
        f"skipped {unreadable} unreadable file(s)."
    )
    if findings and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
