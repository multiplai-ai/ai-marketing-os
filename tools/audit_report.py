#!/usr/bin/env python3
"""
Audit Report Generator
----------------------
Deterministic scorer/report generator for the assessment-led audit funnel
(the "Agency AI Operating System Audit"). Takes one survey submission plus
the four instrument files (survey questions, scoring model, fix library,
report template), computes dimension scores, the overall score, a maturity
band, and a peer benchmark line, selects the top-3 fixes from the weakest
dimensions, and merges everything into the prospect-facing report template.

Python 3 stdlib only. Dry-run by default: prints the report to stdout.
Pass --write to save to --out.

Usage:
    python3 tools/audit_report.py --selftest
    python3 tools/audit_report.py --responses .tmp/response.json
    python3 tools/audit_report.py --responses .tmp/response.json \\
        --booking-url https://example.com/book \\
        --out .tmp/report-acme.md --write
    python3 tools/audit_report.py --responses .tmp/response.json \\
        --questions brains/multiplai/marketing/audit-funnel/survey-questions.md \\
        --scoring brains/multiplai/marketing/audit-funnel/scoring-model.md \\
        --fixes brains/multiplai/marketing/audit-funnel/fix-library.md \\
        --template brains/multiplai/marketing/audit-funnel/report-template.md

Responses JSON format (transient file, e.g. under .tmp/ — contact data
belongs in the Notion lead pipeline, never in the repo):
    {
      "first_name": "Dana",            (optional; defaults to "there")
      "company": "Northbeam Digital",  (optional; defaults to "Your agency")
      "answers": {"Q1": 2, "Q2": 1, ..., "Q10": 0}   (required; 0-3 each)
    }

Markdown parsing contracts are documented at the top of each instrument
file. In short: survey questions live in fenced blocks tagged `question`,
the scoring model in one block tagged `scoring`, fixes in blocks tagged
`fix`, and the template body sits between `<!-- template-start -->` and
`<!-- template-end -->` markers.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Default instrument paths (MultiplAI funnel assets). Override per entity
# with the CLI flags; the audit-funnel skill passes {brain} paths.
DEFAULT_QUESTIONS = "brains/multiplai/marketing/audit-funnel/survey-questions.md"
DEFAULT_SCORING = "brains/multiplai/marketing/audit-funnel/scoring-model.md"
DEFAULT_FIXES = "brains/multiplai/marketing/audit-funnel/fix-library.md"
DEFAULT_TEMPLATE = "brains/multiplai/marketing/audit-funnel/report-template.md"

MAX_OPTION_SCORE = 3

TEMPLATE_START = "<!-- template-start -->"
TEMPLATE_END = "<!-- template-end -->"


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def _fenced_blocks(text: str, tag: str) -> list[str]:
    """Return the inner text of every fenced code block tagged `tag`."""
    pattern = re.compile(r"```" + re.escape(tag) + r"[ \t]*\n(.*?)```", re.DOTALL)
    return pattern.findall(text)


def parse_questions(path: Path) -> dict:
    """Parse scored question blocks from survey-questions.md.

    Returns {question_id: {"dimension": str, "text": str,
                           "options": {0: str, 1: str, 2: str, 3: str}}}
    """
    text = path.read_text(encoding="utf-8")
    questions: dict = {}
    for block in _fenced_blocks(text, "question"):
        q: dict = {"options": {}}
        qid = None
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            m = re.fullmatch(r"option\s+(\d+)", key)
            if m:
                q["options"][int(m.group(1))] = value
            elif key == "id":
                qid = value
            elif key in ("dimension", "text"):
                q[key] = value
        if qid is None:
            raise ValueError(f"question block without id in {path}")
        for req in ("dimension", "text"):
            if req not in q:
                raise ValueError(f"question {qid}: missing '{req}' in {path}")
        expected = set(range(MAX_OPTION_SCORE + 1))
        if set(q["options"]) != expected:
            raise ValueError(
                f"question {qid}: expected options {sorted(expected)}, "
                f"got {sorted(q['options'])}"
            )
        if qid in questions:
            raise ValueError(f"duplicate question id {qid} in {path}")
        questions[qid] = q
    if not questions:
        raise ValueError(f"no question blocks found in {path}")
    return questions


def parse_scoring(path: Path) -> dict:
    """Parse the scoring model block from scoring-model.md.

    Returns {"dimensions": {key: display_name} (ordered),
             "bands": [{"name", "lo", "hi", "description"}],
             "benchmarks": {band_name: int},
             "segments": {band_name: str},
             "fix_selection": (2, 1)}
    """
    text = path.read_text(encoding="utf-8")
    blocks = _fenced_blocks(text, "scoring")
    if len(blocks) != 1:
        raise ValueError(f"expected exactly one scoring block in {path}, got {len(blocks)}")
    model: dict = {"dimensions": {}, "bands": [], "benchmarks": {}, "segments": {},
                   "fix_selection": (2, 1)}
    for line in blocks[0].splitlines():
        line = line.strip()
        if not line:
            continue
        head, _, value = line.partition(":")
        head, value = head.strip(), value.strip()
        if head.startswith("dimension "):
            model["dimensions"][head.split(None, 1)[1]] = value
        elif head.startswith("band "):
            name = head.split(None, 1)[1]
            range_part, _, desc = value.partition("|")
            m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", range_part.strip())
            if not m:
                raise ValueError(f"band {name}: bad range {range_part!r} in {path}")
            model["bands"].append({
                "name": name,
                "lo": int(m.group(1)),
                "hi": int(m.group(2)),
                "description": desc.strip(),
            })
        elif head.startswith("benchmark "):
            model["benchmarks"][head.split(None, 1)[1]] = int(value)
        elif head.startswith("segment "):
            model["segments"][head.split(None, 1)[1]] = value
        elif head == "fix_selection":
            m = re.fullmatch(r"(\d+)\s*\+\s*(\d+)", value)
            if not m:
                raise ValueError(f"bad fix_selection {value!r} in {path}")
            model["fix_selection"] = (int(m.group(1)), int(m.group(2)))
    # Validate band coverage of 0-100 with no gaps/overlaps
    bands = sorted(model["bands"], key=lambda b: b["lo"])
    if not bands or bands[0]["lo"] != 0 or bands[-1]["hi"] != 100:
        raise ValueError(f"bands must cover 0-100 in {path}")
    for prev, cur in zip(bands, bands[1:]):
        if cur["lo"] != prev["hi"] + 1:
            raise ValueError(
                f"band gap/overlap between {prev['name']} and {cur['name']} in {path}"
            )
    for band in model["bands"]:
        if band["name"] not in model["benchmarks"]:
            raise ValueError(f"band {band['name']} has no benchmark in {path}")
        if band["name"] not in model["segments"]:
            raise ValueError(f"band {band['name']} has no segment in {path}")
    if not model["dimensions"]:
        raise ValueError(f"no dimensions defined in {path}")
    return model


def parse_fixes(path: Path) -> list[dict]:
    """Parse fix blocks from fix-library.md, preserving file order.

    Returns [{"id", "dimension", "title", "effort", "offer", "body"}].
    Lines after `body:` (to the end of the block) join into one paragraph.
    """
    text = path.read_text(encoding="utf-8")
    fixes: list[dict] = []
    seen_ids: set = set()
    for block in _fenced_blocks(text, "fix"):
        fix: dict = {}
        body_lines: list[str] = []
        in_body = False
        for line in block.splitlines():
            if in_body:
                body_lines.append(line.strip())
                continue
            stripped = line.strip()
            if not stripped:
                continue
            key, _, value = stripped.partition(":")
            key, value = key.strip(), value.strip()
            if key == "body":
                in_body = True
                if value:
                    body_lines.append(value)
            elif key in ("id", "dimension", "title", "effort", "offer"):
                fix[key] = value
        fix["body"] = " ".join(part for part in body_lines if part)
        for req in ("id", "dimension", "title", "effort", "offer", "body"):
            if not fix.get(req):
                raise ValueError(f"fix block missing '{req}' in {path}: {fix}")
        if fix["id"] in seen_ids:
            raise ValueError(f"duplicate fix id {fix['id']} in {path}")
        seen_ids.add(fix["id"])
        fixes.append(fix)
    if not fixes:
        raise ValueError(f"no fix blocks found in {path}")
    return fixes


def parse_template(path: Path) -> str:
    """Extract the prospect-facing template body between the start/end markers.

    Markers count only when they are alone on a line, so the contract prose
    at the top of the template file can mention them in backticks safely.
    """
    text = path.read_text(encoding="utf-8")
    start = re.search(rf"^{re.escape(TEMPLATE_START)}\s*$", text, re.MULTILINE)
    if not start:
        raise ValueError(f"missing {TEMPLATE_START!r} marker line in {path}")
    body = text[start.end():]
    end = re.search(rf"^{re.escape(TEMPLATE_END)}\s*$", body, re.MULTILINE)
    if end:
        body = body[:end.start()]
    return body.strip() + "\n"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_response(answers: dict, questions: dict, model: dict) -> dict:
    """Compute dimension scores, overall score, band, benchmark, and segment."""
    missing = sorted(set(questions) - set(answers))
    if missing:
        raise ValueError(f"response missing answers for: {', '.join(missing)}")
    unknown = sorted(set(answers) - set(questions))
    if unknown:
        raise ValueError(f"response has unknown question ids: {', '.join(unknown)}")

    per_dim: dict = {key: [] for key in model["dimensions"]}
    for qid, q in questions.items():
        value = answers[qid]
        if not isinstance(value, int) or not 0 <= value <= MAX_OPTION_SCORE:
            raise ValueError(f"answer for {qid} must be an integer 0-{MAX_OPTION_SCORE}, got {value!r}")
        if q["dimension"] not in per_dim:
            raise ValueError(f"question {qid} uses unknown dimension {q['dimension']!r}")
        per_dim[q["dimension"]].append(value)

    dim_scores: dict = {}
    for key, values in per_dim.items():
        if not values:
            raise ValueError(f"dimension {key!r} has no questions")
        dim_scores[key] = round(100 * sum(values) / (MAX_OPTION_SCORE * len(values)))

    overall = round(sum(dim_scores.values()) / len(dim_scores))

    band = next((b for b in model["bands"] if b["lo"] <= overall <= b["hi"]), None)
    if band is None:
        raise ValueError(f"no band covers overall score {overall}")

    # Weakest dimensions: lowest score first; ties break by scoring-model order.
    dim_order = list(model["dimensions"])
    ranked = sorted(dim_order, key=lambda k: (dim_scores[k], dim_order.index(k)))

    return {
        "dimension_scores": dim_scores,
        "overall": overall,
        "band": band,
        "benchmark": model["benchmarks"][band["name"]],
        "segment": model["segments"][band["name"]],
        "ranked_dimensions": ranked,  # weakest -> strongest
    }


def select_fixes(scored: dict, fixes: list[dict], model: dict) -> list[dict]:
    """Select top-3 fixes: `fix_selection` (default 2+1) from the weakest and
    second-weakest dimensions, in fix-library order, spilling down the
    weakness ranking if a dimension runs short."""
    primary_n, secondary_n = model["fix_selection"]
    want_total = primary_n + secondary_n
    by_dim: dict = {}
    for fix in fixes:
        by_dim.setdefault(fix["dimension"], []).append(fix)

    selected: list[dict] = []
    quotas = [primary_n, secondary_n]
    for i, dim in enumerate(scored["ranked_dimensions"]):
        quota = quotas[i] if i < len(quotas) else 1  # spill: 1 per further dim
        for fix in by_dim.get(dim, [])[:quota]:
            if len(selected) < want_total:
                selected.append(fix)
        if len(selected) >= want_total:
            break
    if len(selected) < want_total:
        raise ValueError(
            f"fix library too small: needed {want_total}, found {len(selected)}"
        )
    return selected


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def _benchmark_phrase(overall: int, benchmark: int) -> str:
    delta = overall - benchmark
    if delta > 0:
        return f"{delta} points ahead of it"
    if delta < 0:
        return f"{abs(delta)} points behind it"
    return "right on it"


def _dimension_table(scored: dict, model: dict) -> str:
    rows = ["| Dimension | Your score |", "|---|---|"]
    for key, display in model["dimensions"].items():
        rows.append(f"| {display} | {scored['dimension_scores'][key]}/100 |")
    return "\n".join(rows)


def build_fields(response: dict, scored: dict, selected: list[dict],
                 model: dict, booking_url: str) -> dict:
    """Assemble the merge-field dictionary for the report template."""
    ranked = scored["ranked_dimensions"]
    fields = {
        "first_name": response.get("first_name") or "there",
        "company": response.get("company") or "Your agency",
        "date": date.today().isoformat(),
        "overall_score": str(scored["overall"]),
        "band_name": scored["band"]["name"],
        "band_description": scored["band"]["description"],
        "peer_benchmark": str(scored["benchmark"]),
        "benchmark_phrase": _benchmark_phrase(scored["overall"], scored["benchmark"]),
        "dimension_table": _dimension_table(scored, model),
        "weakest_dimension": model["dimensions"][ranked[0]],
        "strongest_dimension": model["dimensions"][ranked[-1]],
        "booking_url": booking_url,
    }
    for i, fix in enumerate(selected, start=1):
        fields[f"fix_{i}_title"] = fix["title"]
        fields[f"fix_{i}_body"] = fix["body"]
        fields[f"fix_{i}_effort"] = fix["effort"]
    return fields


def merge_template(template: str, fields: dict) -> tuple[str, list[str]]:
    """Substitute {field} tokens. Returns (report, unresolved_tokens)."""
    def sub(match):
        return fields.get(match.group(1), match.group(0))

    report = re.sub(r"\{([a-z0-9_]+)\}", sub, template)
    unresolved = sorted(set(re.findall(r"\{([a-z0-9_]+)\}", report)))
    return report, unresolved


def generate(response: dict, questions_path: Path, scoring_path: Path,
             fixes_path: Path, template_path: Path, booking_url: str) -> dict:
    """Full pipeline: parse instrument, score, select fixes, merge report."""
    questions = parse_questions(questions_path)
    model = parse_scoring(scoring_path)
    fixes = parse_fixes(fixes_path)
    template = parse_template(template_path)

    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ValueError('responses JSON must contain an "answers" object')

    scored = score_response(answers, questions, model)
    selected = select_fixes(scored, fixes, model)
    fields = build_fields(response, scored, selected, model, booking_url)
    report, unresolved = merge_template(template, fields)

    return {
        "questions": questions,
        "model": model,
        "fixes": fixes,
        "scored": scored,
        "selected": selected,
        "report": report,
        "unresolved": unresolved,
    }


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def summary_lines(result: dict) -> list[str]:
    scored = result["scored"]
    model = result["model"]
    dims = ", ".join(
        f"{model['dimensions'][k]} {scored['dimension_scores'][k]}"
        for k in model["dimensions"]
    )
    return [
        f"Overall: {scored['overall']}/100  Band: {scored['band']['name']}"
        f"  Benchmark: {scored['benchmark']}  Segment: {scored['segment']}",
        f"Dimensions: {dims}",
        f"Fixes: {', '.join(f['id'] for f in result['selected'])}",
    ]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

SELFTEST_LOW = {
    "first_name": "Dana",
    "company": "Northbeam Digital",
    "answers": {"Q1": 1, "Q2": 0, "Q3": 1, "Q4": 0, "Q5": 1,
                "Q6": 1, "Q7": 0, "Q8": 1, "Q9": 0, "Q10": 1},
}

SELFTEST_HIGH = {
    "first_name": "Priya",
    "company": "Signalcraft",
    "answers": {f"Q{i}": 3 for i in range(1, 11)},
}


def run_selftest(questions_path: Path, scoring_path: Path,
                 fixes_path: Path, template_path: Path) -> int:
    """Exercise the full parse -> score -> select -> merge path and assert
    sane output against the real instrument files."""
    booking_url = "https://example.com/selftest-booking"
    failures: list[str] = []

    def check(label: str, condition: bool, detail: str = ""):
        status = "ok" if condition else "FAIL"
        print(f"  [{status}] {label}" + (f" ({detail})" if detail and not condition else ""))
        if not condition:
            failures.append(label)

    print("SELFTEST: audit_report.py")
    print(f"  instrument: {questions_path}")

    # --- Instrument contract ---
    questions = parse_questions(questions_path)
    model = parse_scoring(scoring_path)
    fixes = parse_fixes(fixes_path)
    template = parse_template(template_path)

    check("10 scored questions parsed", len(questions) == 10, f"got {len(questions)}")
    check("5 dimensions defined", len(model["dimensions"]) == 5,
          f"got {len(model['dimensions'])}")
    per_dim_counts = {k: 0 for k in model["dimensions"]}
    for q in questions.values():
        per_dim_counts[q["dimension"]] += 1
    check("2 questions per dimension", all(n == 2 for n in per_dim_counts.values()),
          str(per_dim_counts))
    check("4 maturity bands covering 0-100", len(model["bands"]) == 4,
          f"got {len(model['bands'])}")
    check("at least 3 fixes per dimension", all(
        sum(1 for f in fixes if f["dimension"] == k) >= 3 for k in model["dimensions"]
    ), str({k: sum(1 for f in fixes if f['dimension'] == k) for k in model['dimensions']}))
    check("template body non-trivial", len(template) > 500, f"{len(template)} chars")

    # --- Low-band sample (weakest: tooling, then delivery via tiebreak) ---
    low = generate(SELFTEST_LOW, questions_path, scoring_path, fixes_path,
                   template_path, booking_url)
    s = low["scored"]
    check("low sample overall score == 20", s["overall"] == 20, f"got {s['overall']}")
    check("low sample band == Manual", s["band"]["name"] == "Manual", s["band"]["name"])
    check("low sample segment == fixit", s["segment"] == "fixit", s["segment"])
    fix_ids = [f["id"] for f in low["selected"]]
    check("low sample selects 3 fixes", len(fix_ids) == 3, str(fix_ids))
    check("low sample fixes follow 2+1 weakest-dimension rule",
          fix_ids == ["FIX-TOOL-01", "FIX-TOOL-02", "FIX-FLOW-01"], str(fix_ids))
    check("low sample report has no unresolved merge fields",
          not low["unresolved"], str(low["unresolved"]))
    check("low sample report carries score and band",
          "20/100" in low["report"] and "Manual" in low["report"])
    check("low sample report carries booking url", booking_url in low["report"])
    check("low sample report names the prospect",
          "Dana" in low["report"] and "Northbeam Digital" in low["report"])

    # --- High-band sample ---
    high = generate(SELFTEST_HIGH, questions_path, scoring_path, fixes_path,
                    template_path, booking_url)
    s = high["scored"]
    check("high sample overall score == 100", s["overall"] == 100, f"got {s['overall']}")
    check("high sample band == Agentic", s["band"]["name"] == "Agentic", s["band"]["name"])
    check("high sample segment == partner", s["segment"] == "partner", s["segment"])
    check("high sample benchmark phrase reads 'ahead'",
          "ahead" in high["report"], "")
    check("high sample report has no unresolved merge fields",
          not high["unresolved"], str(high["unresolved"]))

    # --- Validation guardrails ---
    try:
        score_response({"Q1": 2}, questions, model)
        check("incomplete response rejected", False)
    except ValueError:
        check("incomplete response rejected", True)
    try:
        bad = dict(SELFTEST_LOW["answers"], Q1=7)
        score_response(bad, questions, model)
        check("out-of-range answer rejected", False)
    except ValueError:
        check("out-of-range answer rejected", True)

    print()
    if failures:
        print(f"SELFTEST FAILED: {len(failures)} check(s): {'; '.join(failures)}")
        return 1
    print("SELFTEST PASSED: all checks green.")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Audit report generator — deterministic scoring + report merge "
                    "for the assessment-led audit funnel"
    )
    parser.add_argument("--responses", metavar="FILE",
                        help="Path to one submission's responses JSON")
    parser.add_argument("--questions", metavar="FILE", default=DEFAULT_QUESTIONS,
                        help=f"Survey questions markdown (default: {DEFAULT_QUESTIONS})")
    parser.add_argument("--scoring", metavar="FILE", default=DEFAULT_SCORING,
                        help=f"Scoring model markdown (default: {DEFAULT_SCORING})")
    parser.add_argument("--fixes", metavar="FILE", default=DEFAULT_FIXES,
                        help=f"Fix library markdown (default: {DEFAULT_FIXES})")
    parser.add_argument("--template", metavar="FILE", default=DEFAULT_TEMPLATE,
                        help=f"Report template markdown (default: {DEFAULT_TEMPLATE})")
    parser.add_argument("--out", metavar="FILE",
                        help="Output path for the merged report markdown")
    parser.add_argument("--booking-url", metavar="URL", default="{booking_url}",
                        help="Instant-booking calendar URL to merge into the report "
                             "(left as a placeholder token if omitted)")
    parser.add_argument("--dry-run", "-n", action="store_true", default=True,
                        help="Print the report to stdout without writing (default)")
    parser.add_argument("--write", action="store_true",
                        help="Actually write the report to --out")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the embedded end-to-end selftest and exit")

    args = parser.parse_args()

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else PROJECT_ROOT / path

    questions_path = resolve(args.questions)
    scoring_path = resolve(args.scoring)
    fixes_path = resolve(args.fixes)
    template_path = resolve(args.template)

    for path in (questions_path, scoring_path, fixes_path, template_path):
        if not path.exists():
            print(f"Error: instrument file not found: {path}", file=sys.stderr)
            return 1

    if args.selftest:
        return run_selftest(questions_path, scoring_path, fixes_path, template_path)

    if not args.responses:
        parser.print_help()
        return 1

    responses_path = resolve(args.responses)
    if not responses_path.exists():
        print(f"Error: responses file not found: {responses_path}", file=sys.stderr)
        return 1
    try:
        response = json.loads(responses_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {responses_path}: {e}", file=sys.stderr)
        return 1

    try:
        result = generate(response, questions_path, scoring_path, fixes_path,
                          template_path, args.booking_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if result["unresolved"] and result["unresolved"] != ["booking_url"]:
        print(f"Warning: unresolved merge fields: {result['unresolved']}",
              file=sys.stderr)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("AUDIT REPORT" + ("" if args.write else " (DRY RUN)"))
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for line in summary_lines(result):
        print(line)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if args.write:
        if not args.out:
            print("Error: --write requires --out", file=sys.stderr)
            return 1
        out_path = resolve(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result["report"], encoding="utf-8")
        print(f"Report written: {out_path}")
        print("Reminder: reports are human-approved before sending (audit-funnel skill gate).")
    else:
        print()
        print(result["report"])
        print("(Dry run — pass --write --out <path> to save.)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
