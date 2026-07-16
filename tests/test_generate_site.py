"""Tests for scripts/generate_site.py — trees, per-entry pages, tolerant ranking."""

from __future__ import annotations

import common as c
import generate_site as g
from conftest import make_entry


def _seed(sandbox):
    ai = c.load_pool("ai-research")
    ai["entries"] = [make_entry(source_url="https://a/ai1")]
    c.save_pool("ai-research", ai)
    sec = c.load_pool("ai-security")
    sec["entries"] = [
        # security entry: scored (so it's curated), no summary, has threat block
        {
            "topic": "ai-security",
            "domain": "Injection",
            "title": "Legacy XSS finding",
            "source_url": "https://a/sec1",
            "date": "2026-01",
            "scores": {"novelty": 70, "relevance": 70},
            "threat": "Reflected XSS in search.",
            "conditions": "Unescaped param.",
            "mitigations": "Encode output.",
        }
    ]
    c.save_pool("ai-security", sec)


def test_generate_site_builds_trees_and_pages(sandbox):
    _seed(sandbox)
    g.main()
    assert (sandbox / "README.md").exists()
    assert (sandbox / "ai-security" / "README.md").exists()
    assert (sandbox / "ai-research" / "README.md").exists()
    ai_pages = list((sandbox / "ai-research" / c.domain_slug("Agents & Harnesses")).glob("*.md"))
    sec_pages = list((sandbox / "ai-security" / c.domain_slug("Injection")).glob("*.md"))
    assert ai_pages and sec_pages
    readme = (sandbox / "README.md").read_text(encoding="utf-8")
    assert "This week's snapshot" in readme
    assert "How to use this repo" in readme  # robust docs README


def test_legacy_entry_renders_without_scores(sandbox):
    _seed(sandbox)
    conf = c.load_config()
    legacy = c.load_pool("ai-security")["entries"][0]
    page = g.render_entry_page(legacy, conf)
    assert "Legacy XSS finding" in page
    assert "Threat" in page  # threat/conditions/mitigations block still appears


def test_ai_entry_with_summary_no_threat(sandbox):
    conf = c.load_config()
    page = g.render_entry_page(make_entry(), conf)
    assert "## TL;DR" in page  # entries are condensed TL;DR gists
    assert "Threat · Conditions" not in page  # no threat on AI-research entry


def test_entry_scores_tolerant_of_missing():
    conf = c.load_config()
    s = g.entry_scores({"date": "2026-07"}, conf)
    assert {"newness", "novelty", "relevance", "composite"} <= s.keys()


def test_week_snapshot_only_recent(sandbox):
    conf = c.load_config()
    in_week = make_entry(title="recent-item", source_url="https://a/r", published="2099-01-05")
    ancient = make_entry(title="ancient-item", source_url="https://a/o", published="2000-01-01")
    lines = "\n".join(g._week_snapshot([in_week, ancient], conf))
    assert "This week's snapshot" in lines
    assert "recent-item" in lines and "source ↗" in lines  # links to the source article
    assert "ancient-item" not in lines  # outside the snapshot window
