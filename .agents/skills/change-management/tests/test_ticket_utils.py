"""Unit tests for ticket_utils (run: python -m unittest discover -s tests -v)."""
import datetime
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import ticket_utils  # noqa: E402


class NextIdTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.tickets = self.tmp / "tickets"
        self.tickets.mkdir()

    def test_empty_dir_starts_at_001(self):
        self.assertEqual(ticket_utils.compute_next_id(self.tickets),
                         ("CHANGE-001", 1, []))

    def test_increments_past_max(self):
        for name in ("CHANGE-001.md", "CHANGE-007.md", "CHANGE-003.md"):
            (self.tickets / name).write_text("x", encoding="utf-8")
        ticket_id, number, ids = ticket_utils.compute_next_id(self.tickets)
        self.assertEqual((ticket_id, number), ("CHANGE-008", 8))
        self.assertEqual(ids, [1, 3, 7])

    def test_rollover_past_999(self):
        (self.tickets / "CHANGE-999.md").write_text("x", encoding="utf-8")
        self.assertEqual(ticket_utils.compute_next_id(self.tickets)[0], "CHANGE-1000")

    def test_ignores_non_ticket_files(self):
        (self.tickets / "README.md").write_text("x", encoding="utf-8")
        self.assertEqual(ticket_utils.compute_next_id(self.tickets)[0], "CHANGE-001")


class NextVersionTests(unittest.TestCase):
    def setUp(self):
        self._original = ticket_utils.latest_tag_version
        self.addCleanup(setattr, ticket_utils, "latest_tag_version", self._original)

    def patch_tags(self, version):
        ticket_utils.latest_tag_version = lambda root: version

    def test_first_tag_is_v0_1_0(self):
        self.patch_tags(None)
        self.assertEqual(ticket_utils.compute_next_version("idea", None), "v0.1.0")

    def test_idea_bumps_minor(self):
        self.patch_tags((1, 2, 3))
        self.assertEqual(ticket_utils.compute_next_version("idea", None), "v1.3.0")

    def test_problem_bumps_patch(self):
        self.patch_tags((1, 2, 3))
        self.assertEqual(ticket_utils.compute_next_version("problem", None), "v1.2.4")

    def test_invalid_type_raises(self):
        with self.assertRaises(RuntimeError):
            ticket_utils.compute_next_version("feature", None)


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_creates_filled_ticket(self):
        target = ticket_utils.scaffold_ticket(
            self.tmp, "CHANGE-001", "add dark mode", "idea")
        content = target.read_text(encoding="utf-8")
        self.assertIn("id: CHANGE-001", content)
        self.assertIn("type: idea", content)
        self.assertIn("title: add dark mode", content)
        self.assertIn(datetime.date.today().isoformat(), content)
        self.assertIn("status: open", content)
        self.assertNotIn("YYYY-MM-DD", content)

    def test_rejects_colon_in_title(self):
        with self.assertRaises(RuntimeError):
            ticket_utils.scaffold_ticket(self.tmp, "CHANGE-001", "a: b", "idea")

    def test_refuses_overwrite(self):
        ticket_utils.scaffold_ticket(self.tmp, "CHANGE-001", "one", "idea")
        with self.assertRaises(RuntimeError):
            ticket_utils.scaffold_ticket(self.tmp, "CHANGE-001", "two", "idea")


if __name__ == "__main__":
    unittest.main()
