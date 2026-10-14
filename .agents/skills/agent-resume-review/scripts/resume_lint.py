#!/usr/bin/env python3
"""resume_lint.py — deterministic lint for AI Agent engineer resumes (zh/en).

Checks the mechanical half of the agent-resume-review rubric: required
sections, contact info, quantified-bullet ratio, weak-verb usage, keyword-tier
coverage, proficiency claims, and length. Chinese and English resumes are
both first-class: section/verb/proficiency rules carry zh and en aliases,
keywords match synonym groups across languages, and the report states which
language it detected. Judgment calls (depth, credibility, project fit) stay
with the reviewer — see references/scoring-rubric.md in this skill.

Usage:
    python resume_lint.py                          # lint the bundled weak sample
    python resume_lint.py path/to/resume.md        # lint one resume
    python resume_lint.py path/to/resume.md --json # machine-readable report
    python resume_lint.py resume.md --min-score 70 # exit 1 below threshold

Exit codes: 0 = lint completed (see score in the report), 1 = IO/usage error
or score below --min-score. The lint reports; it never blocks on its own.
All thresholds live in SCORE_WEIGHTS / THRESHOLDS.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

# Make Windows console/pipes safe for the Chinese terms this lint prints.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass

# --- Rule data -----------------------------------------------------------

REQUIRED_SECTIONS: List[Tuple[str, str]] = [
    ("education", r"教育背景|教育经历|education|academic\s+background"),
    ("skills", r"技术技能|专业技能|技能|technical\s+skills|skills"),
    ("projects", r"项目经历|项目经验|(?:work\s+)?experience|projects?"),
]

CONTACT_PATTERNS: Dict[str, str] = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    # CN mobile / CN landline / US / international (+CC …) formats
    "phone": (r"1[3-9]\d{9}|\+?\d{1,3}[\s.-]\(?\d{1,4}\)?[\s.-]\d{3,4}"
              r"[\s.-]?\d{4,6}|\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"),
    "github": r"github\.com/[A-Za-z0-9_-]+",
}

# Tier-1: must-have keyword groups for an AI Agent role — any synonym counts.
# Each entry: (canonical label, [synonyms, ...]).
TIER1_KEYWORDS = [
    ("python", []),
    ("agent", []),
    ("llm", ["大语言模型", "大模型"]),
    ("prompt", []),
    ("rag", ["检索增强"]),
    ("function calling", ["tool calling", "函数调用"]),
    ("asyncio", ["异步", "async"]),
]

# Tier-2: strongly recommended keyword groups.
TIER2_KEYWORDS = [
    ("mcp", ["model context protocol"]),
    ("langchain", ["langgraph"]),
    ("nanobot", []),
    ("向量数据库", ["milvus", "faiss", "weaviate", "qdrant", "vector database"]),
    ("transformer", []),
    ("fastapi", []),
    ("docker", []),
    ("git", []),
]

# Weak verbs that signal "no ownership" (resume-standards.md verb tiers).
# ASCII terms match on word boundaries; zh terms match as substrings.
WEAK_VERBS = ["参与", "协助", "帮助", "参加",
              "participated", "assisted", "helped"]

# Proficiency claims that must survive an interview probe (精通 / expert).
MASTERY_CLAIMS = ["精通", "expert"]

BULLET_RE = re.compile(r"^\s*(?:[•·▪‣\-*>]|\d+[.、)])\s*(.+)$")
DIGIT_RE = re.compile(r"\d")

SCORE_WEIGHTS = {
    "sections": 20,     # 3 required sections + contact info, 5 each
    "quantification": 25,
    "weak_verbs": 15,
    "keywords": 25,     # tier-1 (15) + tier-2 (10)
    "mastery_claims": 5,
    "length": 10,
}

THRESHOLDS = {
    "quantified_ratio_good": 0.6,   # >= 60% of bullets carry a number
    "one_page_nonempty_lines": 60,  # ~one A4 page of markdown resume
    "mastery_claims_ok": 3,         # more than 3 精通 = credibility risk
}


class Finding:
    """One lint finding: severity, where, and how to fix it."""

    def __init__(self, check: str, severity: str, detail: str, suggestion: str):
        self.check = check
        self.severity = severity
        self.detail = detail
        self.suggestion = suggestion

    def as_dict(self) -> Dict[str, str]:
        return {
            "check": self.check,
            "severity": self.severity,
            "detail": self.detail,
            "suggestion": self.suggestion,
        }


# --- Loading -------------------------------------------------------------


def load_resume(path: str) -> str:
    """Read a resume file, trying UTF-8 then GBK (common for zh resumes)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"resume file not found: {path}")
    for encoding in ("utf-8", "gbk"):
        try:
            with open(path, "r", encoding=encoding) as handle:
                text = handle.read()
            if text.strip():
                return text
            raise ValueError(f"resume file is empty: {path}")
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode resume file as UTF-8 or GBK: {path}")


# --- Individual checks ----------------------------------------------------


def check_sections(text: str) -> Tuple[float, List[str]]:
    """Required sections + contact info; returns (score, missing labels)."""
    missing: List[str] = []
    found = 0
    for label, pattern in REQUIRED_SECTIONS:
        if re.search(pattern, text, re.IGNORECASE):
            found += 1
        else:
            missing.append(label)
    contact_found = [name for name, pat in CONTACT_PATTERNS.items()
                     if re.search(pat, text)]
    score = found * 5 + (5 if contact_found else 0)
    if not contact_found:
        missing.append("contact (email/phone/github)")
    return score, missing


def bullet_lines(text: str) -> List[str]:
    """Return the content of all bullet lines (•, -, *, 1.) in the resume."""
    bullets: List[str] = []
    for line in text.splitlines():
        match = BULLET_RE.match(line)
        if match:
            bullets.append(match.group(1).strip())
    return bullets


def check_quantification(bullets: List[str]) -> Tuple[float, float, int]:
    """Fraction of bullets that contain a digit; returns (score, ratio, n)."""
    if not bullets:
        return 0.0, 0.0, 0
    quantified = sum(1 for b in bullets if DIGIT_RE.search(b))
    ratio = quantified / len(bullets)
    score = SCORE_WEIGHTS["quantification"] * min(
        ratio / THRESHOLDS["quantified_ratio_good"], 1.0)
    return score, ratio, len(bullets)


def _term_in(term: str, haystack_lower: str) -> bool:
    """ASCII terms match on word boundaries (github ≠ git); zh as substring."""
    if term.isascii():
        return re.search(rf"\b{re.escape(term)}\b", haystack_lower) is not None
    return term in haystack_lower


def check_weak_verbs(bullets: List[str]) -> Tuple[float, List[str]]:
    """Weak verbs (参与/协助/帮助/participated/assisted) signal no ownership."""
    hits: List[str] = []
    for verb in WEAK_VERBS:
        if any(_term_in(verb, b.lower()) for b in bullets):
            hits.append(verb)
    score = max(SCORE_WEIGHTS["weak_verbs"] - 5 * len(hits), 0)
    return score, sorted(hits)


def keyword_coverage(text: str, groups: List[Tuple[str, List[str]]]) -> Tuple[List[str], List[str]]:
    """Group coverage (any synonym counts); ASCII terms match on word
    boundaries so e.g. 'github' does not satisfy the 'git' keyword."""
    lowered = text.lower()
    found: List[str] = []
    missing: List[str] = []
    for canonical, synonyms in groups:
        hit = False
        for term in [canonical] + synonyms:
            if term.isascii():
                if re.search(rf"\b{re.escape(term)}\b", lowered):
                    hit = True
                    break
            elif term in lowered:
                hit = True
                break
        (found if hit else missing).append(canonical)
    return found, missing


def check_keywords(text: str) -> Tuple[float, Dict[str, Any]]:
    """Tier-1 (15 pts) + tier-2 (10 pts) coverage for AI Agent roles."""
    t1_found, t1_missing = keyword_coverage(text, TIER1_KEYWORDS)
    t2_found, t2_missing = keyword_coverage(text, TIER2_KEYWORDS)
    score = (len(t1_found) / len(TIER1_KEYWORDS) * 15
             + len(t2_found) / len(TIER2_KEYWORDS) * 10)
    return score, {
        "tier1_found": t1_found, "tier1_missing": t1_missing,
        "tier2_found": t2_found, "tier2_missing": t2_missing,
    }


def check_mastery_claims(text: str) -> Tuple[float, int]:
    """Each 精通 / expert claim must survive an interview probe; cap at 3."""
    lowered = text.lower()
    claims = sum(1 for term in MASTERY_CLAIMS
                 for _ in range(text.count(term) if not term.isascii()
                                else len(re.findall(rf"\b{re.escape(term)}\b", lowered))))
    score = SCORE_WEIGHTS["mastery_claims"] if claims <= THRESHOLDS["mastery_claims_ok"] else 0
    return score, claims


def check_length(text: str) -> Tuple[float, int]:
    """One-page heuristic: non-empty line count against an A4 budget."""
    nonempty = sum(1 for line in text.splitlines() if line.strip())
    if nonempty <= THRESHOLDS["one_page_nonempty_lines"]:
        score = SCORE_WEIGHTS["length"]
    elif nonempty <= THRESHOLDS["one_page_nonempty_lines"] + 15:
        score = SCORE_WEIGHTS["length"] / 2
    else:
        score = 0.0
    return score, nonempty


def projects_slice(text: str) -> str:
    """Return the text between the projects/experience heading and the next
    major section, or EOF. Quantification and weak-verb rules apply here —
    skills-list bullets need no numbers. Works for zh and en layouts."""
    start = re.search(
        r"^#+\s*(?:.*)(项目经历|项目经验|(?:work\s+)?experience|projects?).*$",
        text, re.IGNORECASE | re.MULTILINE)
    if not start:
        return text
    rest = text[start.end():]
    stop = re.search(
        r"^#+\s*(?:.*(自我评价|个人亮点|其他|summary|highlights?|about\s+me|"
        r"education|certifications|additional)).*$",
        rest, re.IGNORECASE | re.MULTILINE)
    return rest[:stop.start()] if stop else rest


def detect_language(text: str) -> str:
    """Classify as zh / en / mixed by CJK share of lettered characters.
    zh-market resumes carry English tech vocabulary (Python, MCP, ...), so
    the zh boundary sits low: only near-balanced prose counts as mixed."""
    cjk = sum(1 for ch in text if "一" <= ch <= "鿿")
    letters = sum(1 for ch in text if ch.isalpha())
    if letters == 0:
        return "unknown"
    ratio = cjk / letters
    if ratio > 0.25:
        return "zh"
    if ratio < 0.1:
        return "en"
    return "mixed"


# --- Report ---------------------------------------------------------------


def lint_resume(text: str) -> Dict[str, Any]:
    """Run every mechanical check and assemble the score + findings."""
    findings: List[Finding] = []
    sections_score, missing_sections = check_sections(text)
    bullets = bullet_lines(projects_slice(text))
    quant_score, quant_ratio, n_bullets = check_quantification(bullets)
    weak_score, weak_hits = check_weak_verbs(bullets)
    keyword_score, keyword_detail = check_keywords(text)
    mastery_score, mastery_claims = check_mastery_claims(text)
    length_score, nonempty_lines = check_length(text)

    if missing_sections:
        findings.append(Finding(
            "sections", "high",
            f"missing: {', '.join(missing_sections)}",
            "Use standard headings an ATS can parse: 教育背景 / 技术技能 / "
            "项目经历 (zh) or Education / Skills / Experience (en)."))
    if n_bullets == 0:
        findings.append(Finding(
            "quantification", "high", "no bullet lines detected",
            "Express project work as bullets (•/-/1.) so impact is scannable."))
    elif quant_ratio < THRESHOLDS["quantified_ratio_good"]:
        findings.append(Finding(
            "quantification", "high",
            f"only {quant_ratio:.0%} of {n_bullets} bullets carry a number "
            f"(target ≥ {THRESHOLDS['quantified_ratio_good']:.0%})",
            "Rewrite results with STAR numbers: 提升 X% / improved by X%, "
            "日均 X 次 / X requests per day."))
    if weak_hits:
        findings.append(Finding(
            "weak_verbs", "high",
            f"weak verbs present: {', '.join(weak_hits)}",
            "Lead with ownership verbs: 主导 / 设计 / 实现 / 优化 (zh) or "
            "led / designed / built / optimized (en)."))
    if keyword_detail["tier1_missing"]:
        findings.append(Finding(
            "keywords", "high",
            f"tier-1 keywords missing: {', '.join(keyword_detail['tier1_missing'])}",
            "Fold must-have keywords into skills/projects naturally (2-3 times each)."))
    if keyword_detail["tier2_missing"]:
        findings.append(Finding(
            "keywords", "medium",
            f"tier-2 keywords missing: {', '.join(keyword_detail['tier2_missing'])}",
            "Add the ones you actually used; never pad keywords you cannot defend."))
    if mastery_claims > THRESHOLDS["mastery_claims_ok"]:
        findings.append(Finding(
            "mastery_claims", "medium",
            f"{mastery_claims} mastery claims (精通 / expert) — over the cap of "
            f"{THRESHOLDS['mastery_claims_ok']}",
            "Downgrade uncertain claims to 熟悉 / proficient; every mastery "
            "claim gets probed."))
    if length_score < SCORE_WEIGHTS["length"]:
        findings.append(Finding(
            "length", "medium",
            f"{nonempty_lines} non-empty lines exceeds the one-page budget "
            f"({THRESHOLDS['one_page_nonempty_lines']})",
            "Cut to one page: fewer, deeper projects beat a long list."))

    total = (sections_score + quant_score + weak_score + keyword_score
             + mastery_score + length_score)
    return {
        "score": round(total, 1),
        "language": detect_language(text),
        "components": {
            "sections": round(sections_score, 1),
            "quantification": round(quant_score, 1),
            "weak_verbs": round(weak_score, 1),
            "keywords": round(keyword_score, 1),
            "mastery_claims": round(mastery_score, 1),
            "length": round(length_score, 1),
        },
        "stats": {
            "bullets": n_bullets,
            "quantified_ratio": round(quant_ratio, 2),
            "weak_verb_hits": weak_hits,
            "mastery_claims": mastery_claims,
            "nonempty_lines": nonempty_lines,
            **keyword_detail,
        },
        "findings": [f.as_dict() for f in findings],
    }


def render_text(report: Dict[str, Any], path: str) -> str:
    """Human-readable report, mirrored by render via --json."""
    lines = [
        "=" * 64,
        "RESUME LINT REPORT",
        "=" * 64,
        f"File: {path}",
        f"Language: {report.get('language', 'unknown')}",
        f"Lint score: {report['score']}/100",
        "",
        "Components:",
    ]
    for name, value in report["components"].items():
        lines.append(f"  {name:<16} {value:>5} / {SCORE_WEIGHTS[name]}")
    lines.append("")
    if report["findings"]:
        lines.append("Findings:")
        for item in report["findings"]:
            lines.append(f"  [{item['severity'].upper():<6}] {item['check']}: "
                         f"{item['detail']}")
            lines.append(f"          fix: {item['suggestion']}")
    else:
        lines.append("Findings: none — mechanical checks all clean.")
    lines.append("")
    lines.append("Judgment checks (depth, credibility, JD fit) are manual: "
                 "see references/scoring-rubric.md.")
    return "\n".join(lines)


def default_sample_path() -> str:
    """Bundled weak sample, resolved relative to this script (skill boundary)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "assets", "sample-resume-weak.md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic lint for AI Agent engineer resumes (zh/en).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python resume_lint.py                            # bundled weak sample\n"
            "  python resume_lint.py my-resume.md --json        # machine-readable\n"
            "  python resume_lint.py my-resume.md --min-score 70\n"
            "\n"
            "checks: sections, contact, quantified-bullet ratio, weak verbs,\n"
            "keyword tiers, mastery claims, one-page length. Run --help."
        ))
    parser.add_argument("resume", nargs="?",
                        default=default_sample_path(),
                        help="Resume file (.md/.txt); defaults to the bundled sample")
    parser.add_argument("--json", action="store_true",
                        help="Emit the report as JSON")
    parser.add_argument("--min-score", type=float, default=None,
                        help="Exit 1 when the lint score is below this value")
    args = parser.parse_args()

    try:
        text = load_resume(args.resume)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = lint_resume(text)
    if args.json:
        report["file"] = args.resume
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text(report, args.resume))

    if args.min_score is not None and report["score"] < args.min_score:
        print(f"error: lint score {report['score']} below minimum "
              f"{args.min_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
