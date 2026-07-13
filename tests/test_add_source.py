"""Tests for scripts/add_source.py — type resolution, feed discovery, signals."""

from __future__ import annotations

import argparse

import add_source as a
import sources_registry as sr


def ns(**kw):
    return argparse.Namespace(**kw)


def test_looks_feed_url():
    assert a.looks_feed_url("https://x.com/feed")
    assert a.looks_feed_url("https://x.com/atom.xml")
    assert not a.looks_feed_url("https://x.com/blog/post")


def test_resolve_x_account():
    stored, handle, url = a.resolve(ns(type="x_account", handle="@simonw"))
    assert (stored, handle, url) == ("x_account", "simonw", "https://x.com/simonw")


def test_resolve_github_user_and_query():
    assert a.resolve(ns(type="github_user", handle="trailofbits")) == (
        "github_user",
        "trailofbits",
        "https://github.com/trailofbits",
    )
    assert a.resolve(ns(type="github_query", handle="threat modeling")) == (
        "github_query",
        "threat modeling",
        None,
    )


def test_resolve_youtube():
    stored, handle, url = a.resolve(ns(type="youtube", handle="https://youtube.com/@LiveOverflow"))
    assert stored == "youtube" and url == "https://youtube.com/@LiveOverflow"
    assert a.resolve(ns(type="youtube", handle="@x"))[2] is None  # bare handle -> no url


def test_resolve_rss_feed_url_skips_discovery():
    # an explicit feed URL is used as-is (no network discovery)
    assert a.resolve(ns(type="rss", handle="https://blog.example.com/feed")) == (
        "rss",
        "https://blog.example.com/feed",
        "https://blog.example.com/feed",
    )


def test_resolve_blog_discovers_feed(monkeypatch):
    monkeypatch.setattr(a, "discover_feed", lambda url: "https://blog.example.com/rss.xml")
    stored, handle, url = a.resolve(ns(type="blog", handle="https://blog.example.com"))
    assert stored == "rss"
    assert handle == "https://blog.example.com/rss.xml"
    assert url == "https://blog.example.com"


def test_collect_signals_manual_and_github(monkeypatch):
    manual = a.collect_signals(
        ns(followers=1000, stars=None, subscribers=None), "x_account", "simonw"
    )
    assert manual == {"followers": 1000}
    monkeypatch.setattr(a, "github_user_followers", lambda u: 3012)
    auto = a.collect_signals(
        ns(followers=None, stars=None, subscribers=None), "github_user", "trailofbits"
    )
    assert auto == {"followers": 3012}


def test_main_registers_source(sandbox, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["add_source", "github_query", "mcp security", "--topics", "ai-security", "--tier", "high"],
    )
    assert a.main() == 0
    sources = sr.load_sources()
    assert len(sources) == 1
    assert sources[0]["type"] == "github_query" and sources[0]["tier"] == "high"


def test_main_rejects_bad_topic(sandbox, monkeypatch):
    import pytest

    monkeypatch.setattr("sys.argv", ["add_source", "x_account", "@x", "--topics", "bogus"])
    with pytest.raises(SystemExit):
        a.main()
