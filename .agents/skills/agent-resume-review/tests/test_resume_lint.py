#!/usr/bin/env python3
"""Tests for resume_lint.py — run with: python -m unittest discover tests"""

import importlib.util
import os
import unittest

_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "scripts", "resume_lint.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("resume_lint", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rl = _load_module()
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(_ROOT, "assets", name), encoding="utf-8") as fh:
        return fh.read()


class TestSampleResumes(unittest.TestCase):
    def test_weak_sample_below_60(self):
        report = rl.lint_resume(_read("sample-resume-weak.md"))
        self.assertLess(report["score"], 60)
        self.assertGreater(len(report["findings"]), 2)

    def test_strong_sample_above_85(self):
        report = rl.lint_resume(_read("sample-resume-strong.md"))
        self.assertGreaterEqual(report["score"], 85)
        self.assertEqual(report["findings"], [])

    def test_weak_en_sample_below_60(self):
        report = rl.lint_resume(_read("sample-resume-weak-en.md"))
        self.assertLess(report["score"], 60)
        self.assertGreater(len(report["findings"]), 2)

    def test_strong_en_sample_above_85(self):
        report = rl.lint_resume(_read("sample-resume-strong-en.md"))
        self.assertGreaterEqual(report["score"], 85)
        self.assertEqual(report["findings"], [])


class TestLanguageDetection(unittest.TestCase):
    def test_zh_samples_classified_zh(self):
        for name in ("sample-resume-weak.md", "sample-resume-strong.md"):
            self.assertEqual(rl.detect_language(_read(name)), "zh", name)

    def test_en_samples_classified_en(self):
        for name in ("sample-resume-weak-en.md", "sample-resume-strong-en.md"):
            self.assertEqual(rl.detect_language(_read(name)), "en", name)

    def test_zh_resume_with_english_tech_terms(self):
        text = "## 技术技能\n- Python、FastAPI、Docker、MCP\n## 项目经历\n- 主导开发\n"
        self.assertEqual(rl.detect_language(text), "zh")


class TestKeywordGroups(unittest.TestCase):
    def test_synonym_counts_as_hit(self):
        found, missing = rl.keyword_coverage("熟悉 RAG 系统设计", rl.TIER1_KEYWORDS)
        self.assertIn("rag", found)
        found, _ = rl.keyword_coverage("基于大语言模型开发", rl.TIER1_KEYWORDS)
        self.assertIn("llm", found)

    def test_github_does_not_satisfy_git(self):
        found, _ = rl.keyword_coverage("github.com/zhangsan", rl.TIER2_KEYWORDS)
        self.assertNotIn("git", found)

    def test_tier_weights_sum(self):
        self.assertEqual(sum(rl.SCORE_WEIGHTS.values()), 100)


class TestScoping(unittest.TestCase):
    def test_quantification_uses_projects_slice_only(self):
        text = (
            "## 技术技能\n"
            "- Python、Docker、Git\n"
            "## 项目经历\n"
            "- 主导设计 Agent 系统,日均 500+ 次调用\n"
            "## 自我评价\n"
            "- 学习能力强\n"
        )
        report = rl.lint_resume(text)
        self.assertEqual(report["stats"]["bullets"], 1)
        self.assertEqual(report["stats"]["quantified_ratio"], 1.0)

    def test_weak_verbs_detected_in_projects(self):
        text = "## 项目经历\n- 参与了项目的开发工作\n- 协助团队完成部署\n"
        report = rl.lint_resume(text)
        self.assertIn("参与", report["stats"]["weak_verb_hits"])
        self.assertIn("协助", report["stats"]["weak_verb_hits"])

    def test_english_weak_verbs_detected(self):
        text = ("## Experience\n"
                "- Participated in requirement analysis\n"
                "- Assisted the team with deployment\n")
        report = rl.lint_resume(text)
        self.assertIn("participated", report["stats"]["weak_verb_hits"])
        self.assertIn("assisted", report["stats"]["weak_verb_hits"])
        self.assertEqual(report["language"], "en")

    def test_mastery_claims_capped(self):
        text = "精通Python 精通Docker 精通K8s 精通Java"
        score, claims = rl.check_mastery_claims(text)
        self.assertEqual(claims, 4)
        self.assertEqual(score, 0)

    def test_english_mastery_claims_counted(self):
        text = "Expert in Python, Docker expert, Kubernetes expert, Go expert"
        score, claims = rl.check_mastery_claims(text)
        self.assertEqual(claims, 4)
        self.assertEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
