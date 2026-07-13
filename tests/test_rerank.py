"""Tests for scripts/rerank.py — decay, composite, and sort."""

from __future__ import annotations

from datetime import UTC, datetime

import common as c
import rerank
from conftest import make_entry


def test_score_entry_fills_scores():
    conf = c.load_config()
    now = datetime(2026, 7, 1, tzinfo=UTC)
    scored = rerank.score_entry(make_entry(scores={"novelty": 50, "relevance": 60}), conf, now=now)
    s = scored["scores"]
    assert "newness" in s and "composite" in s and "scored_at" in s
    assert s["composite"] == c.composite_score(s, conf.weights)


def test_score_entry_defaults_missing_axes():
    conf = c.load_config()
    scored = rerank.score_entry(make_entry(scores=None, date="2026-07"), conf)
    assert scored["scores"]["novelty"] == 0
    assert scored["scores"]["relevance"] == 0


def test_rerank_pool_sorts_by_composite(sandbox):
    pool = c.load_pool("ai")
    pool["entries"] = [
        make_entry(title="low", source_url="https://a/1", scores={"novelty": 5, "relevance": 5}),
        make_entry(title="high", source_url="https://a/2", scores={"novelty": 95, "relevance": 95}),
    ]
    c.save_pool("ai", pool)
    out = rerank.rerank_pool("ai")
    assert out["entries"][0]["title"] == "high"
    # persisted
    assert c.load_pool("ai")["entries"][0]["title"] == "high"


def test_rerank_all_scores_both_pools(sandbox):
    for track, domain in (("ai", "Agents & Harnesses"), ("security", "AI Security")):
        pool = c.load_pool(track)
        pool["entries"] = [make_entry(track=track, domain=domain, source_url=f"https://a/{track}")]
        c.save_pool(track, pool)
    rerank.rerank_all()
    for track in ("ai", "security"):
        assert "composite" in c.load_pool(track)["entries"][0]["scores"]


def test_rerank_main_cli(sandbox, monkeypatch):
    pool = c.load_pool("ai")
    pool["entries"] = [make_entry(source_url="https://a/cli")]
    c.save_pool("ai", pool)
    monkeypatch.setattr("sys.argv", ["rerank", "--track", "ai"])
    assert rerank.main() == 0
    assert "composite" in c.load_pool("ai")["entries"][0]["scores"]
