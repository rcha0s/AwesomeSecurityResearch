"""Unit tests for scripts/common.py helpers, scoring, and validation."""

from __future__ import annotations

from datetime import UTC, datetime

import common as c
from conftest import make_entry


def test_normalize_url_strips_query_fragment_trailing():
    assert c.normalize_url("HTTPS://A.com/x/?q=1#frag") == "https://a.com/x"
    assert c.normalize_url("  https://a.com/x/  ") == "https://a.com/x"


def test_make_id_is_deterministic_and_slugged():
    a = c.make_id("MCP Tool Poisoning!", "http://x/a")
    b = c.make_id("MCP Tool Poisoning!", "http://x/a")
    assert a == b and a.startswith("mcp-tool-poisoning")


def test_slugify_and_clean_summary():
    assert c.slugify("Hello, World!!") == "hello-world"
    assert c.clean_summary("<p>a   b</p>") == "a b"
    assert c.clean_summary("x" * 400).endswith("…")


def test_title_similar():
    assert c.title_similar("MCP tool poisoning", "MCP Tool Poisoning")
    assert not c.title_similar("prompt injection", "supply chain attack")
    assert not c.title_similar("", "anything")


def test_extract_urls_dedup_and_trim():
    urls = c.extract_urls("see https://a.com/x, and https://a.com/x also http://b.io/y).")
    assert urls == ["https://a.com/x", "http://b.io/y"]


def test_clean_source_url_strips_tracking():
    assert c.clean_source_url("https://a.com/x?utm_source=rss&utm_medium=rss") == "https://a.com/x"
    assert c.clean_source_url("https://a.com/x?id=5&utm_source=x") == "https://a.com/x?id=5"
    assert c.clean_source_url("https://a.com/x") == "https://a.com/x"
    assert c.clean_source_url("https://a.com/x?fbclid=abc") == "https://a.com/x"


def test_date_from_url():
    assert c.date_from_url("https://x.com/2026/05/13/post") == "2026-05-13"
    assert c.date_from_url("https://x.com/2026/05/post") == "2026-05"
    assert c.date_from_url("https://x.com/no-date-here") is None


def test_is_fresh_window():
    now = datetime(2026, 7, 13, tzinfo=UTC)
    assert c.is_fresh({"published": "2026-07-01"}, 31, now=now) is True
    assert c.is_fresh({"published": "2026-06-30"}, 31, now=now) is True
    assert c.is_fresh({"published": "2026-05-01"}, 31, now=now) is False
    # month-only is treated as end-of-month (lenient)
    assert c.is_fresh({"date": "2026-06"}, 31, now=now) is True
    assert c.is_fresh({"date": "2026-05"}, 31, now=now) is False
    # undated entries are kept (never dropped for lack of a date)
    assert c.is_fresh({}, 31, now=now) is True


def test_add_candidates_rejects_stale(sandbox):
    stale = {
        "id": "old",
        "title": "Old thing",
        "source_url": "https://a/old",
        "published": "2020-01-01",
    }
    assert c.add_candidates([stale]) == []


def test_newness_score_decays():
    now = datetime(2026, 7, 1, tzinfo=UTC)
    fresh = c.newness_score("2026-07", 45, now=now)
    old = c.newness_score("2026-01", 45, now=now)
    assert fresh > old
    assert c.newness_score("", 45, now=now) == 0
    assert 90 <= fresh <= 100


def test_composite_score_weights():
    scores = {"newness": 100, "novelty": 0, "relevance": 0}
    assert c.composite_score(scores, {"newness": 0.3, "novelty": 0.35, "relevance": 0.35}) == 30.0


def test_composite_includes_credibility():
    w = {"newness": 0.25, "novelty": 0.3, "relevance": 0.3, "credibility": 0.15}
    assert c.composite_score({"credibility": 100}, w) == 15.0
    assert c.composite_score({"credibility": 0}, w) == 0.0


def test_credibility_of_from_source_rank():
    assert c.credibility_of({"source_rank": 80}) == 80.0
    assert c.credibility_of({}) == 50.0  # unknown source -> neutral default


def test_credibility_corroboration_bonus():
    two = [{"url": "https://a"}, {"url": "https://b"}]
    assert c.credibility_of({"source_rank": 60, "corroborating_sources": two}) == 70.0  # +2*5
    # capped at 100
    many = [{"url": f"https://{i}"} for i in range(10)]
    assert c.credibility_of({"source_rank": 95, "corroborating_sources": many}) == 100.0


def test_resolve_redirects_skips_non_shortener():
    # a non-shortener URL is returned unchanged with no network call
    assert c.resolve_redirects("https://blog.example.com/post") == "https://blog.example.com/post"


def test_validate_entry_ok_and_errors():
    assert c.validate_entry(make_entry()) == []
    assert any("missing" in e for e in c.validate_entry({"topic": "ai-research"}))
    # domain is free-text now — any string is valid
    assert c.validate_entry(make_entry(domain="Any Free Domain")) == []
    assert any("unknown topic" in e for e in c.validate_entry(make_entry(topic="nope")))
    bad = make_entry(actionable={"type": "nope"})
    assert any("actionable.type" in e for e in c.validate_entry(bad))


def test_parse_month():
    assert c.parse_month("2026-07").year == 2026
    assert c.parse_month("2026-07-15").day == 15
    assert c.parse_month("garbage") is None


def test_add_candidates_dedup(sandbox):
    cand = {"id": "x1", "title": "A finding", "source_url": "https://a.com/x"}
    dup = {"id": "x2", "title": "A finding!", "source_url": "https://a.com/x/"}
    added = c.add_candidates([cand, dup])
    assert len(added) == 1
    # re-adding the same url is a no-op
    assert c.add_candidates([cand]) == []
    assert len(c.load_candidates()) == 1


def test_add_candidates_skips_pooled(sandbox):
    pool = c.load_pool("ai-security")
    pool["entries"].append(
        make_entry(topic="ai-security", domain="Prompt Injection", source_url="https://a.com/known")
    )
    c.save_pool("ai-security", pool)
    assert (
        c.add_candidates([{"id": "n", "title": "New", "source_url": "https://a.com/known"}]) == []
    )
