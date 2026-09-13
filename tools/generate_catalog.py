#!/usr/bin/env python3
"""Generate a plain-language workflow library from canonical skill metadata."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


STARTERS = {
    "strategy-suite", "content-strategy", "content-brief", "writing",
    "human-writing-standard", "linkedin-post", "ads-audit", "ads-landing",
    "seo-qc", "geo-audit", "prompt-optimizer",
}
EVALUATED = {
    "discovery-intake", "positioning-strategy", "icp-personas",
    "brand-strategy", "content-strategy", "strategy-suite",
}

# These summaries are written for the person choosing a workflow. The longer
# technical descriptions in each SKILL.md remain available to the assistant.
PUBLIC_GUIDE = {
    "ads": ("Paid Advertising Guide", "Choose the right advertising review or planning workflow for the channels you use."),
    "ads-audit": ("Paid Advertising Audit", "Review several advertising channels together and leave with a prioritized fix list."),
    "ads-budget": ("Advertising Budget Review", "Decide where to increase, reduce, or stop advertising spend based on performance and readiness."),
    "ads-competitor": ("Competitor Advertising Review", "Study competitors' visible advertising to find useful messaging, creative, and channel patterns."),
    "ads-creative": ("Advertising Creative Review", "Find weak, repetitive, or poorly matched advertising creative and plan the next tests."),
    "ads-google": ("Google Ads Review", "Review Google Ads structure, tracking, search terms, creative, and wasted spend."),
    "ads-landing": ("Landing Page Review", "Check whether a landing page fulfills the promise that brought visitors there and makes the next step clear."),
    "ads-linkedin": ("LinkedIn Ads Review", "Review LinkedIn Ads targeting, tracking, forms, creative, and bidding."),
    "ads-meta": ("Meta Ads Review", "Review Facebook and Instagram campaign tracking, audiences, creative, structure, and performance."),
    "ads-microsoft": ("Microsoft Ads Review", "Review Microsoft and Bing campaigns, including imported settings, tracking, targeting, and search traffic."),
    "ads-plan": ("Paid Advertising Plan", "Choose channels, campaign structure, budget, creative needs, measurement, and a phased launch plan."),
    "ads-tiktok": ("TikTok Ads Review", "Review TikTok campaign tracking, creative, bidding, structure, and shopping setup."),
    "ads-youtube": ("YouTube Ads Review", "Review YouTube campaign formats, video creative, audiences, and measurement."),
    "ai-tool-review": ("AI Tool Review", "Turn firsthand product testing into a fair, useful review with a clear recommendation."),
    "brand-guide": ("Visual Brand Guide", "Turn approved visual decisions into a usable guide for color, type, imagery, layout, and reusable design rules."),
    "brand-strategy": ("Brand Strategy and Key Messages", "Turn positioning and customer research into a clear message hierarchy, proof points, and voice guidance."),
    "build-workflow": ("Build an AI Workflow", "Design and validate a reusable Claude workflow for a repeated task."),
    "components": ("Reusable Brand Graphics", "Create editable graphic building blocks from an approved visual brand system."),
    "content-brief": ("Article Content Brief", "Prepare a sourced article brief with audience, angle, structure, search questions, and missing research."),
    "content-calendar": ("Monthly Content Calendar", "Turn an approved content strategy into a realistic four-week publishing plan."),
    "content-campaign": ("Content Campaign Plan", "Plan the coordinated articles, social posts, emails, and other assets for a launch or campaign."),
    "content-produce": ("Content Production", "Move one content idea from an approved brief through drafting, review, and publish-ready files."),
    "content-strategy": ("Content Strategy", "Decide what to publish, for whom, on which channels, and how the work supports business goals."),
    "creative-produce": ("Create Campaign Assets", "Produce campaign assets from an approved brief and visual brand system."),
    "creative-status": ("Creative Readiness Check", "See which brand and creative foundations exist, what is missing, and what to create next."),
    "creative-suite": ("Creative System Guide", "Set up and operate a repeatable system for visual research, brand decisions, templates, and campaign assets."),
    "cro": ("Website Conversion Review", "Find the page changes most likely to make the offer clearer and the next action easier."),
    "design-extract": ("Website Style Extraction", "Turn the visual patterns on an existing website into reusable colors, type, spacing, and component rules."),
    "design-systems": ("Design System", "Build an approved visual system that can guide websites, presentations, social assets, and other creative work."),
    "dev-process": ("Software Work Guide", "Guide a software change from understanding and planning through implementation, review, and release."),
    "discovery-intake": ("Business Discovery", "Organize business, customer, marketing, evidence, and constraint information before strategy work begins."),
    "growth-operator-hiring": ("Growth Operator Hiring", "Define the role, score candidates, and run a practical hiring process for a full-loop growth operator."),
    "geo-audit": ("GEO Audit", "Review how easily AI answer engines can discover, understand, and cite a website, then prioritize improvements."),
    "human-writing-standard": ("Human Writing Review", "Keep writing grounded in a real author's words, evidence, judgment, and natural rhythm."),
    "icp-personas": ("Ideal Customers and Buyer Personas", "Define the companies, people, buying roles, and real work patterns most likely to fit the offer."),
    "linkedin-post": ("LinkedIn Post", "Turn a real idea or source into one voice-matched LinkedIn post, or a deliberately varied batch."),
    "mood": ("Visual Direction", "Compare a few visual directions and choose the feeling, texture, energy, and composition the brand should use."),
    "positioning-strategy": ("Positioning Strategy", "Choose the market alternative to compete against and explain why the offer is meaningfully different."),
    "prompt-optimizer": ("Prompt Improver", "Turn a rough request into a clear prompt with the context, constraints, output, and success criteria the model needs."),
    "research": ("Visual and Competitor Research", "Collect visual references, compare patterns, and turn them into clear direction for creative work."),
    "seo": ("SEO Audit", "Use search and site data to find and prioritize technical, content, and authority improvements."),
    "seo-qc": ("Article Search Quality Check", "Review a finished article for search usefulness, answer quality, evidence, and specific improvements."),
    "strategy-suite": ("Strategy Guide", "Review what strategy already exists and guide the next decision across discovery, positioning, customers, brand, and content."),
    "templates": ("Brand Templates", "Create reusable, editable templates for common social, presentation, and campaign formats."),
    "video-production": ("Video Production", "Plan or produce titles, overlays, motion graphics, and edits from an approved brief and visual identity."),
    "visual-content": ("Shareable Visuals", "Turn content into editable diagrams, frameworks, infographics, and reference cards."),
    "writing": ("Article and Newsletter Writing", "Draft source-faithful long-form writing from a brief, transcript, interview, research set, or notes."),
    "writing-setup": ("Writing Setup", "Set up voice examples, source rules, and output formats for repeatable writing work."),
}


def category(sid: str) -> str:
    if sid == "geo-audit":
        return "AI search visibility"
    if sid.startswith("ads"):
        return "Advertising and conversion"
    if sid in {"discovery-intake", "positioning-strategy", "icp-personas", "brand-strategy",
               "content-strategy", "strategy-suite", "audit-funnel", "ecosystem-partnerships",
               "growth-operator-hiring", "growth-operator-onboarding"}:
        return "Strategy and customers"
    if sid in {"content-brief", "content-calendar", "content-campaign", "content-produce",
               "human-writing-standard", "linkedin-post", "monthly-content-planning-and-publishing",
               "quarterly-content-planning", "social-audience-growth-weekly", "social-growth-os",
               "weekly-social-audience-growth", "writing", "writing-setup", "youtube-transcript",
               "ai-tool-review", "mcp-skill-release-newsletter"}:
        return "Content and writing"
    if sid in {"seo", "seo-qc", "cro", "scrape-website"}:
        return "SEO and websites"
    if sid in {"brand-guide", "components", "creative-produce", "creative-status", "creative-suite",
               "design-extract", "design-systems", "mood", "research", "templates",
               "video-production", "visual-content", "artifact-to-presentation"}:
        return "Brand, creative, and presentations"
    if sid in {"engagement-report", "l2-microsite-report", "monthly-mbr", "monthly-scorecard",
               "weekly-audience-report", "weekly-executive-update", "weekly-kpi-report",
               "whitelist-email-refresh", "to-gamma", "to-notion", "to-sheets"}:
        return "Reporting and publishing"
    return "Operations and automation"


def skill_header(text: str) -> dict:
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        return {}
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else {}


def short_description(text: str) -> str:
    clean = " ".join(text.strip().split())
    clean = re.split(r"(?<=[.!?])\s", clean, maxsplit=1)[0]
    return clean if len(clean) <= 220 else clean[:217].rstrip() + "…"


def load_workflows(root: Path) -> list[dict]:
    workflows = []
    for path in sorted((root / "sops").glob("*/sop.yaml")):
        meta = yaml.safe_load(path.read_text(encoding="utf-8"))
        header = skill_header((path.parent / "SKILL.md").read_text(encoding="utf-8"))
        sid = meta["id"]
        guide_title, guide_description = PUBLIC_GUIDE.get(
            sid,
            (str(meta["title"]), short_description(str(header.get("description", meta["title"])))),
        )
        workflows.append({
            "id": sid,
            "title": guide_title,
            "description": guide_description,
            "maturity": meta["maturity"],
            "category": category(sid),
        })
    return workflows


def render(root: Path) -> str:
    workflows = load_workflows(root)
    categories = (
        "Strategy and customers", "Content and writing", "Advertising and conversion",
        "SEO and websites", "AI search visibility", "Brand, creative, and presentations",
        "Reporting and publishing", "Operations and automation",
    )
    text = """# Workflow library

This is the human-readable map of AI Marketing OS. Each workflow is a reusable
set of instructions for Claude or Codex. Click a workflow name to read the full
instructions the assistant follows.

You do not need to configure all of them. Choose one outcome, give the assistant
the relevant source material, and describe the task in normal language. In
Claude, you can also select an installed workflow from the `/` or `+` menu.

## Good places to start

| What you want to accomplish | Workflow | Example request |
| --- | --- | --- |
| Work out which strategy step comes next | [Strategy Guide](../sops/strategy-suite/SKILL.md) | “Review our existing strategy files and guide me through the next missing decision.” |
| Decide what content to create and why | [Content Strategy](../sops/content-strategy/SKILL.md) | “Build a content strategy from these business goals, customer notes, and positioning.” |
| Prepare a well-sourced article | [Article Content Brief](../sops/content-brief/SKILL.md) | “Create a content brief from these sources and clearly label missing research.” |
| Draft an article or newsletter | [Article and Newsletter Writing](../sops/writing/SKILL.md) | “Turn this transcript and brief into an article without inventing claims.” |
| Make writing sound less generic | [Human Writing Review](../sops/human-writing-standard/SKILL.md) | “Review this draft for generic language and unsupported claims.” |
| Draft a social post | [LinkedIn Post](../sops/linkedin-post/SKILL.md) | “Turn this idea into one LinkedIn post for review. Do not publish it.” |
| Find the biggest advertising problems | [Paid Advertising Audit](../sops/ads-audit/SKILL.md) | “Review these exports and explain the three highest-priority problems.” |
| Improve a landing page | [Landing Page Review](../sops/ads-landing/SKILL.md) | “Compare this page with the promise that sends visitors there.” |
| Improve visibility in AI answers | [GEO Audit](../sops/geo-audit/SKILL.md) | “Audit these priority pages for AI search visibility and give me an evidence-backed 30-day plan.” |

## How to read the labels

- **Good place to start:** broadly useful and a sensible first experience.
- **Evidence reviewed:** recorded offline examples exist, with limits documented.
- **Test with your setup:** included for use, but live accounts and integrations
  have not been verified across every environment.

"""
    for group in categories:
        public = [w for w in workflows if w["category"] == group and w["maturity"] == "released"]
        if not public:
            continue
        text += f"## {group}\n\n| Workflow | What it helps you do | Readiness |\n| --- | --- | --- |\n"
        for item in public:
            readiness = ("Good place to start" if item["id"] in STARTERS else
                         "Evidence reviewed" if item["id"] in EVALUATED else
                         "Test with your setup")
            title = item["title"].replace("|", "\\|")
            description = item["description"].replace("|", "\\|")
            text += f'| [{title}](../sops/{item["id"]}/SKILL.md) | {description} | {readiness} |\n'
        text += "\n"

    internal = [w for w in workflows if w["maturity"] != "released"]
    text += """<details>
<summary><strong>Advanced and system workflows</strong></summary>

These workflows support specialized reporting, publishing, account operations,
or older systems. Read the requirements before using them. Some need configured
accounts, exports, approval rules, or tools that are not included automatically.

| Workflow | What it helps you do |
| --- | --- |
"""
    for item in internal:
        title = item["title"].replace("|", "\\|")
        description = item["description"].replace("|", "\\|")
        text += f'| [{title}](../sops/{item["id"]}/SKILL.md) | {description} |\n'
    text += """
</details>

## What a workflow can and cannot do

A workflow improves how the assistant approaches a task. It does not provide
facts about your business or automatic access to your accounts. Workflows that
need analytics, ads, publishing systems, or other services require you to supply
the right exports or configure the relevant connection.

Creating a draft or recommendation does not authorize publishing, sending,
scheduling, spending money, or changing an external account. Review those
actions separately.

For installation and a first task, use [Start here](../START-HERE.md).
"""
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = args.root / "docs/capabilities.md"
    expected = render(args.root)
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != expected:
            parser.exit(1, "workflow library stale: run python tools/generate_catalog.py\n")
    else:
        target.write_text(expected, encoding="utf-8")
    print("workflow library current")


if __name__ == "__main__":
    main()
