"""Tests for scripts/merge_analysis.py — validation, routing, dedup, confidence."""

from __future__ import annotations

import common as c
import merge_analysis as m
from conftest import make_entry


def test_entry_confidence_takes_minimum():
    e = make_entry(
        lessons=[
            {"point": "a", "confidence": 0.9},
            {"point": "b", "confidence": 0.3},
        ]
    )
    assert m.entry_confidence(e) == 0.3
    assert m.entry_confidence(make_entry(lessons=[])) == 1.0


def test_match_index_by_url_and_title():
    existing = [make_entry(title="Existing", source_url="https://a/x", article_url="https://a/x")]
    assert (
        m.match_index(existing, make_entry(source_url="https://a/x/", article_url="https://a/x/"))
        == 0
    )
    assert (
        m.match_index(
            existing,
            make_entry(
                title="Existing", source_url="https://other/z", article_url="https://other/z"
            ),
        )
        == 0
    )
    assert (
        m.match_index(
            existing,
            make_entry(
                title="Totally different thing", source_url="https://n/q", article_url="https://n/q"
            ),
        )
        is None
    )


def test_merge_routes_and_flags_low_confidence(sandbox):
    conf = c.load_config()
    analyzed = [
        make_entry(topic="ai-research", domain="Agents & Harnesses", source_url="https://a/ai"),
        make_entry(
            topic="ai-security",
            domain="Prompt Injection",
            subtype="Prompt Injection",
            title="Calendar prompt injection",
            source_url="https://a/sec",
            lessons=[{"point": "risky", "confidence": 0.2}],
        ),
        make_entry(topic="nope", domain="x", source_url="https://a/bad"),  # invalid domain/track
    ]
    merged, errors, _, _ = m.merge(analyzed, conf)
    assert len(merged) == 2 and len(errors) == 1
    assert len(c.load_pool("ai-research")["entries"]) == 1
    sec = c.load_pool("ai-security")["entries"]
    assert sec[0]["needs_review"] is True  # low confidence flagged


def test_low_credibility_unverified_flagged(sandbox):
    conf = c.load_config()
    # low-authority source (rank 20) whose excerpt can't be confirmed -> review
    low = make_entry(
        topic="ai-security",
        domain="MCP",
        source_url="https://a/low",
        source_rank=20,
        scores={"novelty": 90, "relevance": 90},
    )
    merged, _, _, _ = m.merge([low], conf)  # sandbox stubs grounding -> unverifiable
    assert merged[0]["needs_review"] is True


def test_high_credibility_not_flagged(sandbox):
    conf = c.load_config()
    high = make_entry(
        topic="ai-security",
        domain="MCP",
        source_url="https://a/high",
        source_rank=90,
        scores={"novelty": 90, "relevance": 90},
    )
    merged, _, _, _ = m.merge([high], conf)
    assert merged[0]["needs_review"] is False


def test_curation_gate_flags_low_novelty(sandbox):
    conf = c.load_config()
    # high confidence but derivative (low novelty) → held as needs_review
    derivative = make_entry(
        track="ai",
        domain="Agents & Harnesses",
        source_url="https://a/deriv",
        scores={"novelty": 20, "relevance": 90},
        lessons=[{"point": "known", "confidence": 0.95}],
    )
    novel = make_entry(
        track="ai",
        domain="Agents & Harnesses",
        source_url="https://a/novel",
        scores={"novelty": 85, "relevance": 90},
        lessons=[{"point": "fresh", "confidence": 0.95}],
    )
    merged, _, _, _ = m.merge([derivative, novel], conf)
    by_url = {e["source_url"]: e for e in merged}
    assert by_url["https://a/deriv"]["needs_review"] is True
    assert by_url["https://a/novel"]["needs_review"] is False


def test_merge_is_idempotent(sandbox):
    conf = c.load_config()
    analyzed = [
        make_entry(topic="ai-security", domain="Prompt Injection", source_url="https://a/dup")
    ]
    m.merge(analyzed, conf)
    m.merge(analyzed, conf)
    assert len(c.load_pool("ai-security")["entries"]) == 1


def test_main_merges_and_reranks(sandbox):
    c.save_json(
        c.ANALYSIS_OUT,
        [make_entry(topic="ai-research", domain="Agents & Harnesses", source_url="https://a/main")],
    )
    assert m.main() == 0
    entries = c.load_pool("ai-research")["entries"]
    assert len(entries) == 1 and "composite" in entries[0]["scores"]


def test_merge_returns_only_new_on_remerge(sandbox):
    conf = c.load_config()
    analyzed = [make_entry(topic="ai-security", domain="MCP", source_url="https://a/x")]
    _, _, _, new1 = m.merge(analyzed, conf)
    _, _, _, new2 = m.merge(analyzed, conf)  # same input again (idempotent)
    assert len(new1) == 1  # first merge: appended
    assert new2 == []  # re-merge: in-place update, NOT re-counted


def test_hit_rate_credited_once(sandbox):
    import sources_registry as sr

    src = sr.new_source("rss", "https://feed", tier="medium")
    sr.add_source(src)
    entry = make_entry(
        topic="ai-security", domain="MCP", source_url="https://a/hit", source_id=src["id"]
    )
    c.save_json(c.ANALYSIS_OUT, [entry])
    m.main()
    m.main()  # second run must NOT double-count
    stats = sr.get_by_id(src["id"])["stats"]
    assert stats["ingested"] == 1 and stats["curated"] == 1


def test_clear_candidates_removes_merged(sandbox):
    c.add_candidates([{"id": "keep", "title": "Keep me", "source_url": "https://a/keep"}])
    c.add_candidates([{"id": "gone", "title": "Merge me", "source_url": "https://a/gone"}])
    removed = m.clear_candidates([{"id": "gone"}], {c.normalize_url("https://a/gone")})
    assert removed == 1
    assert [x["id"] for x in c.load_candidates()] == ["keep"]
