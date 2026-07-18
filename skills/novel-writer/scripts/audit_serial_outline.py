#!/usr/bin/env python3
"""Audit deterministic structure in a Markdown serial-fiction outline.

The script checks chapter coverage, chapter-table shape, stage-range coverage,
required execution fields, promise references, and long setup-only runs. It
never edits files and does not judge literary quality.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


CHAPTER_RE = re.compile(
    r"^\s*(?:ch(?:apter)?\s*)?(\d{1,4})(?:\s|《|[：:._-]|$)", re.IGNORECASE
)
STAGE_RE = re.compile(
    r"^#{2,4}\s+.*?(\d{1,4})\s*[-—–~至]\s*(\d{1,4})", re.IGNORECASE
)
PROMISE_RE = re.compile(r"^V\d{2}-P\d{2,3}$", re.IGNORECASE)
PROMISE_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_-])V\d{2}-P\d{2,3}(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)
REQUIRED_HEADER_RE = re.compile(
    r"承接|目标|阻力|高地|动作|选择|回报|结果|代价|边界|交接|"
    r"bridge|goal|objective|resistance|action|choice|return|result|"
    r"cost|boundary|handoff",
    re.IGNORECASE,
)
SETUP_ONLY_RE = re.compile(
    r"^\s*(?:纯?铺垫|准备|等待|setup(?:-only)?|tbd|待定)\s*$",
    re.IGNORECASE,
)
RETURN_HEADER_RE = re.compile(r"回报|结果|return|result", re.IGNORECASE)


@dataclass
class Table:
    header: list[str]
    rows: list[tuple[int, list[str]]]
    start_line: int


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells
    )


def parse_tables(lines: list[str]) -> list[Table]:
    tables: list[Table] = []
    index = 0
    while index + 1 < len(lines):
        if "|" not in lines[index] or not is_separator(lines[index + 1]):
            index += 1
            continue
        header = split_row(lines[index])
        rows: list[tuple[int, list[str]]] = []
        cursor = index + 2
        while (
            cursor < len(lines)
            and "|" in lines[cursor]
            and lines[cursor].lstrip().startswith("|")
        ):
            rows.append((cursor + 1, split_row(lines[cursor])))
            cursor += 1
        tables.append(Table(header=header, rows=rows, start_line=index + 1))
        index = cursor
    return tables


def header_index(header: list[str], pattern: re.Pattern[str]) -> int | None:
    return next(
        (index for index, value in enumerate(header) if pattern.search(value)),
        None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outline", type=Path)
    parser.add_argument(
        "--contract",
        type=Path,
        help="optional Markdown volume contract containing a promise/payoff table",
    )
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--max-setup-run", type=int, default=3)
    args = parser.parse_args()

    if args.start > args.end:
        parser.error("--start must not be greater than --end")
    if args.max_setup_run < 0:
        parser.error("--max-setup-run must be zero or greater")
    if not args.outline.is_file():
        parser.error(f"file not found: {args.outline}")
    if args.contract is not None and not args.contract.is_file():
        parser.error(f"file not found: {args.contract}")

    outline_lines = args.outline.read_text(encoding="utf-8").splitlines()
    outline_tables = parse_tables(outline_lines)
    contract_lines = (
        args.contract.read_text(encoding="utf-8").splitlines()
        if args.contract
        else []
    )
    contract_tables = parse_tables(contract_lines)

    errors: list[str] = []
    warnings: list[str] = []
    chapter_rows: list[tuple[int, int, list[str], list[str]]] = []

    for table in outline_tables:
        if not table.header or not re.search(
            r"章|chapter", table.header[0], re.IGNORECASE
        ):
            continue
        for line_number, row in table.rows:
            if not row:
                continue
            match = CHAPTER_RE.match(row[0])
            if not match:
                continue
            chapter = int(match.group(1))
            if len(row) != len(table.header):
                errors.append(
                    f"chapter row at line {line_number} has {len(row)} columns; "
                    f"expected {len(table.header)}"
                )
            padded = row + [""] * max(0, len(table.header) - len(row))
            chapter_rows.append((chapter, line_number, table.header, padded))

    if not chapter_rows:
        errors.append("no chapter rows found in a table whose first header is Chapter/章")

    expected = list(range(args.start, args.end + 1))
    seen: dict[int, int] = {}
    ordered: list[int] = []
    setup_run: list[int] = []

    for chapter, line_number, header, row in chapter_rows:
        if not args.start <= chapter <= args.end:
            continue
        if chapter in seen:
            errors.append(
                f"chapter {chapter} is duplicated at lines "
                f"{seen[chapter]} and {line_number}"
            )
        else:
            seen[chapter] = line_number
            ordered.append(chapter)

        for index, name in enumerate(header):
            if index == 0 or not REQUIRED_HEADER_RE.search(name):
                continue
            if index >= len(row) or not row[index].strip():
                errors.append(
                    f"chapter {chapter} has an empty required field "
                    f"'{name}' at line {line_number}"
                )

        return_index = header_index(header, RETURN_HEADER_RE)
        return_value = (
            row[return_index].strip()
            if return_index is not None and return_index < len(row)
            else ""
        )
        if SETUP_ONLY_RE.fullmatch(return_value):
            setup_run.append(chapter)
        else:
            if len(setup_run) > args.max_setup_run:
                warnings.append(
                    f"setup-only run is long: chapters "
                    f"{setup_run[0]}-{setup_run[-1]}"
                )
            setup_run = []

    if len(setup_run) > args.max_setup_run:
        warnings.append(
            f"setup-only run is long: chapters {setup_run[0]}-{setup_run[-1]}"
        )

    missing = [chapter for chapter in expected if chapter not in seen]
    if missing:
        errors.append("missing chapters: " + ", ".join(map(str, missing)))
    if ordered and ordered != sorted(ordered):
        errors.append("chapter rows are not in ascending order")

    stage_ranges: list[tuple[int, int, int]] = []
    for line_number, line in enumerate(outline_lines, start=1):
        match = STAGE_RE.match(line)
        if not match:
            continue
        start, end = map(int, match.groups())
        if end < args.start or start > args.end:
            continue
        stage_ranges.append((start, end, line_number))

    if not stage_ranges:
        warnings.append("no stage headings with chapter ranges were found")
    else:
        coverage: dict[int, list[int]] = {chapter: [] for chapter in expected}
        for start, end, line_number in stage_ranges:
            if start > end:
                errors.append(
                    f"reversed stage range {start}-{end} at line {line_number}"
                )
                continue
            for chapter in range(
                max(start, args.start), min(end, args.end) + 1
            ):
                coverage[chapter].append(line_number)
        uncovered = [
            chapter for chapter, lines in coverage.items() if not lines
        ]
        overlap = [
            chapter for chapter, lines in coverage.items() if len(lines) > 1
        ]
        if uncovered:
            errors.append(
                "stage ranges do not cover: " + ", ".join(map(str, uncovered))
            )
        if overlap:
            errors.append(
                "stage ranges overlap at: " + ", ".join(map(str, overlap))
            )

    promise_definitions: dict[str, str] = {}
    sources = [(args.outline, outline_tables)]
    if args.contract is not None:
        sources.append((args.contract, contract_tables))

    for source_path, tables in sources:
        for table in tables:
            if not table.header or not re.search(
                r"承诺|promise", table.header[0], re.IGNORECASE
            ):
                continue
            for line_number, row in table.rows:
                if not row:
                    continue
                promise_id = row[0].strip().upper()
                if not PROMISE_RE.fullmatch(promise_id):
                    continue
                location = f"{source_path}:{line_number}"
                if promise_id in promise_definitions:
                    errors.append(
                        f"promise {promise_id} is defined twice at "
                        f"{promise_definitions[promise_id]} and {location}"
                    )
                else:
                    promise_definitions[promise_id] = location

    if args.contract is not None and not promise_definitions:
        errors.append(
            f"contract contains no recognized promise definitions: {args.contract}"
        )

    promise_uses: dict[str, list[int]] = {}
    for chapter, line_number, _, row in chapter_rows:
        if not args.start <= chapter <= args.end:
            continue
        refs = {
            match.group().upper()
            for match in PROMISE_REF_RE.finditer(" ".join(row))
        }
        if promise_definitions and not refs:
            warnings.append(
                f"chapter {chapter} has no promise reference at line {line_number}"
            )
        for promise_id in refs:
            promise_uses.setdefault(promise_id, []).append(chapter)
            if promise_definitions and promise_id not in promise_definitions:
                errors.append(
                    f"chapter {chapter} references undefined promise "
                    f"{promise_id} at line {line_number}"
                )

    for promise_id, location in promise_definitions.items():
        if promise_id not in promise_uses:
            warnings.append(
                f"promise {promise_id} defined at {location} is not referenced "
                "by any audited chapter"
            )

    print(f"Audited {args.outline}: chapters {args.start}-{args.end}")
    if args.contract is not None:
        print(f"Promise contract: {args.contract}")
    print(
        f"Chapter cards: {len(seen)}; promises: "
        f"{len(promise_definitions)}; stages: {len(stage_ranges)}"
    )
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")

    if errors:
        print(
            f"FAILED with {len(errors)} error(s) and "
            f"{len(warnings)} warning(s)."
        )
        return 1
    print(f"PASS with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
