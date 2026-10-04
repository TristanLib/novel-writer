from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "novel-writer"
SCRIPTS = SKILL / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"


class SkillStructureTests(unittest.TestCase):
    def test_skill_frontmatter_and_references(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: novel-writer\n"))
        self.assertNotIn("TODO", text)

        frontmatter = text.split("---", 2)[1]
        keys = [
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if ":" in line
        ]
        self.assertEqual(keys, ["name", "description"])

        references = re.findall(r"\(references/([^)]+)\)", text)
        self.assertGreaterEqual(len(references), 6)
        for reference in references:
            self.assertTrue(
                (SKILL / "references" / reference).is_file(),
                reference,
            )

    def test_interface_mentions_skill(self) -> None:
        text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Novel Writer"', text)
        self.assertIn("$novel-writer", text)


class ScriptTests(unittest.TestCase):
    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_outline_auditor_accepts_complete_fixture(self) -> None:
        result = self.run_script(
            "audit_serial_outline.py",
            str(FIXTURES / "outline.md"),
            "--contract",
            str(FIXTURES / "contract.md"),
            "--start",
            "1",
            "--end",
            "5",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_outline_auditor_rejects_duplicate_and_missing_chapter(self) -> None:
        text = (FIXTURES / "outline.md").read_text(encoding="utf-8")
        broken = text.replace("| 005 |", "| 004 |")
        with tempfile.TemporaryDirectory() as directory:
            outline = Path(directory) / "broken-outline.md"
            outline.write_text(broken, encoding="utf-8")
            result = self.run_script(
                "audit_serial_outline.py",
                str(outline),
                "--start",
                "1",
                "--end",
                "5",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicated", result.stdout)
        self.assertIn("missing chapters: 5", result.stdout)

    def test_meta_scanner_accepts_clean_prose(self) -> None:
        result = self.run_script(
            "scan_prose_meta.py",
            str(FIXTURES / "clean-prose.md"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("found 0 candidate(s)", result.stdout)

    def test_meta_scanner_flags_project_language(self) -> None:
        result = self.run_script(
            "scan_prose_meta.py",
            str(FIXTURES / "meta-prose.md"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow language", result.stdout)
        self.assertIn("project file or path", result.stdout)


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_chapters(directory: Path, chapters: list[str]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for index, text in enumerate(chapters, start=1):
        (directory / f"chapter-{index:03d}.md").write_text(text, encoding="utf-8")
    return directory


FILLER = "海面很平，船慢慢向南边走去，岸上的人还在等消息。"


class ProseShapeAuditTests(unittest.TestCase):
    def audit(self, *chapters: str, extra: tuple[str, ...] = ()) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for index, text in enumerate(chapters, start=1):
                path = Path(directory) / f"chapter-{index}.md"
                path.write_text(text, encoding="utf-8")
                paths.append(str(path))
            result = run_script("audit_prose_shape.py", *paths, "--json", *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def codes(self, report: dict) -> list[str]:
        return [finding["code"] for finding in report["findings"]]

    def test_flags_negation_pairs_in_narration_with_rate(self) -> None:
        text = "\n\n".join(
            [
                "林川没有回头，也没有停下。",
                "陈默没碰缆绳，也没去开舱门。",
                "沈禾不看岸上，也不出声。",
                "白露没有点灯，也没有记账。",
            ]
        )
        report = self.audit(text)
        self.assertIn("negation-pair", self.codes(report))
        summary = report["files"][0]
        self.assertGreater(summary["narration_han_characters"], 0)
        self.assertGreater(summary["family_per_10k"]["negation-pair"], 0)

    def test_ignores_negation_pairs_inside_dialogue(self) -> None:
        text = "\n\n".join(
            [
                "林川说：“没有回头，也没有停下。”",
                "陈默答：“没碰缆绳，也没去开舱门。”",
                "沈禾喊：“不看岸上，也不出声。”",
                "白露道：“没有点灯，也没有记账。”",
            ]
        )
        report = self.audit(text)
        self.assertNotIn("negation-pair", self.codes(report))
        self.assertEqual(report["files"][0]["family_hits"]["negation-pair"], 0)

    def test_flags_reverse_not_is_in_both_directions(self) -> None:
        text = "那是旧伤，不是新伤。\n\n不是退潮，是暗流在拉船。"
        report = self.audit(text)
        self.assertIn("reverse-not-is", self.codes(report))
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 2)

    def test_reverse_not_is_skips_compound_shi(self) -> None:
        report = self.audit("他只是累了，不是病了。")
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 0)

    def test_reverse_not_is_skips_shi_bu_shi_question(self) -> None:
        report = self.audit("是不是旧伤，不是他能判断的。")
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 0)

    def test_reverse_not_is_skips_affirmation_tag(self) -> None:
        report = self.audit("是的，不是第一次了。")
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 0)

    def test_reverse_not_is_skips_tag_question(self) -> None:
        report = self.audit("那是他的船，不是吗。\n\n不是退潮，是吗。")
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 0)

    def test_reverse_not_is_handles_match_at_paragraph_start(self) -> None:
        report = self.audit("是旧伤，不是新伤，疼的地方也还")
        self.assertEqual(report["files"][0]["family_hits"]["reverse-not-is"], 1)

    def test_flags_negation_parade(self) -> None:
        report = self.audit("没有灯，没有人声，没有退路。")
        self.assertIn("negation-parade", self.codes(report))

    def test_negation_parade_skips_bound_morpheme(self) -> None:
        report = self.audit("船沉没在雾里，没人回头，只有灯还亮着。")
        self.assertEqual(report["files"][0]["family_hits"]["negation-parade"], 0)

    def test_flags_contract_negation(self) -> None:
        text = "\n\n".join(
            [
                "账本不能替他们记住欠款。",
                "她不拿听来的消息当作证据。",
                "林川不凭一句传话替东家做主。",
            ]
        )
        report = self.audit(text)
        self.assertIn("contract-negation", self.codes(report))

    def test_contrast_frame_reports_shell_breakdown(self) -> None:
        text = "\n\n".join(
            [
                "这并非退潮，而是暗流。",
                "与其说他在等风，不如说他在等人。",
                "他守的是表，而非港口。",
            ]
        )
        report = self.audit(text)
        messages = [f["message"] for f in report["findings"] if f["code"] == "repeated-frame"]
        contrast = [m for m in messages if m.startswith("contrast frame")]
        self.assertEqual(len(contrast), 1, messages)
        self.assertIn("并非", contrast[0])
        self.assertIn("而非", contrast[0])

    def test_contrast_frame_skips_yu_qi_ta(self) -> None:
        text = "\n\n".join(
            [
                "他与其他人不同。",
                "林川与其余三人分开站。",
                "那条船与其他渔船并排停着。",
            ]
        )
        report = self.audit(text)
        messages = [f["message"] for f in report["findings"] if f["code"] == "repeated-frame"]
        self.assertFalse([m for m in messages if m.startswith("contrast frame")], messages)

    def test_flags_overcompressed_prose(self) -> None:
        short = ["他推门出去看海。"] * 50
        long = ["船头压浪向南偏，桅杆吃风发出长响，舱底积水随船身来回晃荡，四人各守一处位置不动声色。"] * 30
        report = self.audit("\n\n".join(short + long))
        self.assertIn("overcompressed-prose", self.codes(report))

    def test_flags_low_connective_density(self) -> None:
        paragraph = "林川收绳。陈默看水。沈禾报时。白露记账。船头偏南。"
        report = self.audit("\n\n".join([paragraph] * 45))
        self.assertIn("low-connective-density", self.codes(report))

    def test_reverse_checks_quiet_on_connected_prose(self) -> None:
        paragraph = (
            "林川把地图摊在桌上的时候，已经看出这一趟的风向比昨天变得早，"
            "所以他没有急着出发，而是等陈默把第一根浮绳放下去，看它漂了多远。"
        )
        report = self.audit("\n\n".join([paragraph] * 30))
        self.assertNotIn("overcompressed-prose", self.codes(report))
        self.assertNotIn("low-connective-density", self.codes(report))

    def test_names_file_marks_attributed_dialogue(self) -> None:
        text = "\n\n".join(
            [
                "林川道：“先往南走，每过一段看一次水。”",
                "林川沿着河道走了很久，直到天黑才回到船上。",
            ]
        )
        without = self.audit(text)
        with tempfile.TemporaryDirectory() as directory:
            names = Path(directory) / "names.txt"
            names.write_text("# 主角组\n林川、沈禾\n陈默\n", encoding="utf-8")
            with_names = self.audit(text, extra=("--names", str(names)))
        self.assertEqual(without["files"][0]["narrative_paragraphs"], 2)
        self.assertEqual(with_names["files"][0]["narrative_paragraphs"], 1)

    def test_book_mode_aggregates_family_rates(self) -> None:
        dense = "林川没有回头，也没有停下。\n\n陈默没碰缆绳，也没去开舱门。"
        clean = FILLER
        report = self.audit(dense, clean)
        family = report["book"]["families"]["negation-pair"]
        self.assertEqual(report["book"]["chapters"], 2)
        self.assertEqual(family["hits"], 2)
        self.assertEqual(family["chapters_hit"], 1)
        self.assertGreater(family["per_10k"], 0)


class DiscoverTicsTests(unittest.TestCase):
    def discover(self, target: Path, baseline: Path, *extra: str) -> list[dict[str, str]]:
        result = run_script(
            "discover_tics.py",
            "--target",
            str(target),
            "--baseline",
            str(baseline),
            *extra,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))

    def section(self, rows: list[dict[str, str]], name: str) -> list[str]:
        return [row["ngram"] for row in rows if row["section"] == name]

    def target_chapter(self, extra: str = "") -> str:
        lines = [FILLER, "船上的人绕路走。", "风大了也绕路走。", "方位不明时绕路走。", extra]
        return "\n\n".join(line for line in lines if line)

    def baseline_chapter(self) -> str:
        return "\n\n".join([FILLER, "他仿佛听见了潮声。", "灯影仿佛还在晃。", "她问：“你听见了吗？”", "谁在岸上？"])

    def test_planted_trigram_ranks_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [self.target_chapter()] * 3)
            baseline = write_chapters(root / "baseline", [self.baseline_chapter()] * 3)
            rows = self.discover(target, baseline, "--min-count", "3")
        self.assertEqual(self.section(rows, "over")[0], "绕路走")

    def test_exclude_glossary_removes_names(self) -> None:
        chapter = self.target_chapter("沈禾报时。沈禾看旗。")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [chapter] * 3)
            baseline = write_chapters(root / "baseline", [self.baseline_chapter()] * 3)
            glossary = root / "glossary.txt"
            glossary.write_text("沈禾\n", encoding="utf-8")
            plain = self.discover(target, baseline, "--min-count", "3")
            excluded = self.discover(target, baseline, "--min-count", "3", "--exclude", str(glossary))
        self.assertTrue(any("沈禾" in ngram for ngram in self.section(plain, "over")))
        self.assertFalse(any("沈禾" in row["ngram"] for row in excluded))

    def test_min_chapters_drops_single_chapter_bursts(self) -> None:
        burst = self.target_chapter("孤岛灯塔亮了。" * 10)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [burst, self.target_chapter(), self.target_chapter()])
            baseline = write_chapters(root / "baseline", [self.baseline_chapter()] * 3)
            strict = self.discover(target, baseline, "--min-count", "3")
            loose = self.discover(target, baseline, "--min-count", "3", "--min-chapters", "1")
        self.assertNotIn("孤岛灯塔", self.section(strict, "over"))
        self.assertIn("孤岛灯塔", self.section(loose, "over"))

    def test_under_tail_lists_baseline_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [self.target_chapter()] * 3)
            baseline = write_chapters(root / "baseline", [self.baseline_chapter()] * 3)
            rows = self.discover(target, baseline, "--min-count", "3")
        self.assertIn("仿佛", self.section(rows, "under"))

    def test_probe_rows_count_narration_questions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [self.target_chapter()] * 3)
            baseline = write_chapters(root / "baseline", [self.baseline_chapter()] * 3)
            rows = self.discover(target, baseline, "--min-count", "3")
        probe = {row["ngram"]: row for row in rows if row["section"] == "probe"}
        self.assertEqual(probe["？"]["target_count"], "0")
        self.assertEqual(probe["？"]["baseline_count"], "3")
        self.assertEqual(probe["仿佛"]["baseline_count"], "6")

    def test_chunking_splits_single_file_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = write_chapters(root / "target", [self.target_chapter()] * 3)
            baseline = write_chapters(root / "baseline", ["\n\n".join([self.baseline_chapter()] * 3)])
            single = self.discover(target, baseline, "--min-count", "3")
            chunked = self.discover(target, baseline, "--min-count", "3", "--chunk-chars", "40")
        self.assertNotIn("仿佛", self.section(single, "under"))
        self.assertIn("仿佛", self.section(chunked, "under"))


if __name__ == "__main__":
    unittest.main()
