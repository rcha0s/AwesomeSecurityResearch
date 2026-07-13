"""Tests for scripts/sources_registry.py — schema, ranking, hit-rate."""

from __future__ import annotations

import sources_registry as sr


def test_new_source_defaults_and_rank():
    s = sr.new_source("x_account", "@simonw", tier="high", topics=["ai-research"])
    assert s["id"] == "x_account:simonw"
    assert s["type"] == "x_account" and s["tier"] == "high"
    assert s["stats"] == {"ingested": 0, "curated": 0}
    assert 0 <= s["rank"] <= 100


def test_new_source_rejects_bad_type():
    import pytest

    with pytest.raises(ValueError):
        sr.new_source("bogus", "x")


def test_tier_anchors_rank():
    high = sr.new_source("rss", "https://a/feed", tier="high")
    low = sr.new_source("rss", "https://b/feed", tier="low")
    assert high["rank"] > low["rank"]


def test_signal_bumps_rank():
    plain = sr.new_source("github_user", "a", tier="medium")
    big = sr.new_source("github_user", "b", tier="medium", signals={"followers": 50000})
    assert big["rank"] > plain["rank"]


def test_hit_rate_moves_rank(sandbox):
    src = sr.new_source("rss", "https://a/feed", tier="medium")
    sr.add_source(src)
    base = sr.get_by_id(src["id"])["rank"]
    # 5 curated of 5 analyzed → hit-rate up
    sr.update_stats({src["id"]: (5, 5)})
    up = sr.get_by_id(src["id"])["rank"]
    assert up > base
    # then a run of pure noise → hit-rate down
    sr.update_stats({src["id"]: (10, 0)})
    down = sr.get_by_id(src["id"])["rank"]
    assert down < up


def test_add_source_is_idempotent(sandbox):
    src = sr.new_source("x_account", "@dup", tier="high")
    _, new1 = sr.add_source(src)
    _, new2 = sr.add_source(src)
    assert new1 is True and new2 is False
    assert len(sr.load_sources()) == 1


def test_sources_of_type_filters_active(sandbox):
    sr.add_source(sr.new_source("rss", "https://a/feed"))
    inactive = sr.new_source("rss", "https://b/feed")
    inactive["active"] = False
    sr.add_source(inactive)
    active = sr.sources_of_type("rss")
    assert len(active) == 1 and active[0]["handle"] == "https://a/feed"
    assert len(sr.sources_of_type("rss", active_only=False)) == 2
