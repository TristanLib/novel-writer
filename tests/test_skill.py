from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
