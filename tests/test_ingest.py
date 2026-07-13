"""Tests for the ingestion pure functions (aggregate, ingest_twitter, add) + fetch."""

from __future__ import annotations

import argparse

import add
import aggregate
import common as c
import ingest_twitter as it
import pytest


def test_aggregate_classifies_tracks():
    rules = c.load_yaml(c.SOURCES_FILE)["classification"]
    ai = aggregate.build_candidate(
        {
            "link": "https://x/a",
            "title": "multi-agent orchestration harness",
            "summary": "tool use",
        },
        {"name": "F", "type": "blog", "domains": ["Agents & Harnesses"]},
        rules,
    )
    assert ai["guess_topic"] == "ai-research" and ai["guess_domain"] == "Agents & Harnesses"
    sec = aggregate.build_candidate(
        {"link": "https://x/b", "title": "request smuggling desync", "summary": "waf bypass"},
        {"name": "G", "type": "v", "domains": ["Web Application Security"]},
        rules,
    )
    assert sec["guess_topic"] == "product-security"


def test_parse_tweets_shape_tolerant():
    assert it.parse_tweets('{"tweets":[{"text":"hi"}]}') == [{"text": "hi"}]
    assert it.parse_tweets('[{"text":"hi"}]') == [{"text": "hi"}]
    assert it.parse_tweets("not json") == []


def test_normalize_tweet_extracts_external_link():
    t = {
        "full_text": "great post https://blog.example.com/x",
        "screen_name": "@researcher",
        "url": "https://x.com/researcher/status/1",
        "entities": {"urls": [{"expanded_url": "https://blog.example.com/x"}]},
    }
    n = it.normalize_tweet(t)
    assert n["author"] == "researcher"
    assert n["links"] == ["https://blog.example.com/x"]


def test_normalize_tweet_real_twitter_cli_schema():
    # the actual shape twitter-cli emits under data[]
    t = {
        "id": "2075744411502133559",
        "text": "New writeup on agent harness security https://blog.example.com/harness",
        "author": {"screenName": "researcher", "name": "A Researcher", "verified": True},
        "urls": [{"expandedUrl": "https://blog.example.com/harness"}],
        "createdAtISO": "2026-07-11T00:50:07+00:00",
    }
    n = it.normalize_tweet(t)
    assert n["author"] == "researcher"
    assert n["links"] == ["https://blog.example.com/harness"]
    assert n["url"] == "https://x.com/researcher/status/2075744411502133559"
    assert n["created"].startswith("2026-07")
    cand = it.tweet_to_candidate(t, fetch=False)
    assert cand["date"] == "2026-07"
    assert cand["tweet_url"].endswith("2075744411502133559")


def test_tweet_to_candidate():
    cand = it.tweet_to_candidate(
        {
            "text": "MCP tool poisoning writeup https://b.io/mcp",
            "screen_name": "sec",
            "entities": {"urls": [{"expanded_url": "https://b.io/mcp"}]},
        },
        fetch=False,
    )
    assert cand["discovered_via"] == "twitter"
    assert cand["article_url"] == "https://b.io/mcp"
    assert it.tweet_to_candidate({"text": "", "links": []}, fetch=False) is None


def test_add_source_via():
    assert add.source_via("https://www.linkedin.com/posts/x") == "linkedin"
    assert add.source_via("https://x.com/a/status/1") == "twitter"
    assert add.source_via("https://blog.example.com") == "manual"


def test_add_build_candidate(sandbox):
    args = argparse.Namespace(
        url="https://linkedin.com/posts/x",
        text=None,
        file=None,
        title="My title",
        author="Jane",
        date="2026-07",
        topic="ai-research",
    )
    cand = add.build_candidate(args, "Body text about agents.")
    assert cand["discovered_via"] == "linkedin"
    assert cand["guess_topic"] == "ai-research"
    assert cand["title"] == "My title"
    assert cand["raw_path"] is not None


def test_aggregate_build_candidate_none_cases():
    rules = c.load_yaml(c.SOURCES_FILE)["classification"]
    assert aggregate.build_candidate({"link": "", "title": "x"}, {"domains": []}, rules) is None
    # unclassifiable + multi-domain feed → no confident domain
    none = aggregate.build_candidate(
        {"link": "https://x/z", "title": "zzz qqq", "summary": ""},
        {"name": "F", "domains": ["AI Security", "Mobile Security"]},
        rules,
    )
    assert none is None


def test_add_resolve_text_variants(tmp_path):
    args = argparse.Namespace(text="pasted", file=None, url=None)
    assert add.resolve_text(args) == ("pasted", False)
    f = tmp_path / "body.txt"
    f.write_text("from file", encoding="utf-8")
    args = argparse.Namespace(text=None, file=str(f), url=None)
    assert add.resolve_text(args) == ("from file", False)
    with pytest.raises(SystemExit):
        add.resolve_text(argparse.Namespace(text=None, file=None, url=None))


def test_add_main_stages(sandbox, monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["add", "--text", "agents body", "--title", "T", "--topic", "ai-research"]
    )
    assert add.main() == 0
    assert len(c.load_candidates()) == 1


def test_ingest_run_cli_missing_returns_none():
    assert it.run_cli(["definitely-not-a-real-cmd-xyz", "--help"]) is None


def test_ingest_doctor_ok_false(monkeypatch):
    monkeypatch.setattr(it, "run_cli", lambda *a, **k: None)
    assert it.doctor_ok() is False


def test_collect_tweets_empty_when_no_sources():
    assert it.collect_tweets({"twitter": {"home_feed": False, "accounts": []}}, {}) == []


def test_tweet_to_candidate_fetch_writes_raw(sandbox, monkeypatch):
    monkeypatch.setattr(c, "fetch_readable", lambda url, **k: "clean text")
    cand = it.tweet_to_candidate(
        {
            "text": "post https://b.io/x",
            "screen_name": "a",
            "entities": {"urls": [{"expanded_url": "https://b.io/x"}]},
        },
        fetch=True,
    )
    assert cand["raw_path"] is not None


def test_fetch_readable_mocked(monkeypatch):
    class Resp:
        text = "clean article text"

        def raise_for_status(self):
            return None

    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: Resp())
    assert c.fetch_readable("https://x/y") == "clean article text"
