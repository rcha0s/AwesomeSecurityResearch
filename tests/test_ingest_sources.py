"""Tests for the HN + GHSA ingestor pure mapping functions (offline, no network)."""

from __future__ import annotations

import common as c
import ingest_ghsa as gh
import ingest_hn as hn

RULES = c.load_yaml(c.SOURCES_FILE)["classification"]


def test_hn_hit_classifies_on_topic():
    hit = {
        "objectID": "42",
        "title": "New prompt injection technique bypasses LLM guardrails",
        "url": "https://blog.example.com/pi",
        "author": "researcher",
        "points": 120,
        "num_comments": 30,
        "created_at": "2026-07-14T10:00:00.000Z",
    }
    cand = hn.hit_to_candidate(hit, RULES)
    assert cand["guess_topic"] == "ai-security"
    assert cand["article_url"] == "https://blog.example.com/pi"
    assert cand["source_rank"] == hn.HN_SOURCE_RANK
    assert cand["published"] == "2026-07-14" and cand["date"] == "2026-07"


def test_hn_off_topic_dropped():
    hit = {
        "objectID": "7",
        "title": "My weekend woodworking project",
        "url": "https://blog.example.com/wood",
        "points": 200,
    }
    assert hn.hit_to_candidate(hit, RULES) is None


def test_hn_self_post_falls_back_to_discussion_url():
    hit = {
        "objectID": "99",
        "title": "Ask HN: securing an MCP server against tool poisoning",
        "url": None,  # self/Ask-HN post: no external link
        "points": 80,
        "story_text": "how do you sandbox mcp tools",
    }
    cand = hn.hit_to_candidate(hit, RULES)
    assert cand is not None
    assert cand["article_url"] == "https://news.ycombinator.com/item?id=99"


def test_ghsa_supply_chain_default_routing():
    adv = {
        "ghsa_id": "GHSA-xxxx-yyyy-zzzz",
        "summary": "Arbitrary code execution in leftpad",
        "description": "A malicious version was published.",
        "severity": "high",
        "html_url": "https://github.com/advisories/GHSA-xxxx-yyyy-zzzz",
        "published_at": "2026-07-13T00:00:00Z",
        "vulnerabilities": [{"package": {"ecosystem": "npm", "name": "leftpad"}}],
    }
    cand = gh.advisory_to_candidate(adv, RULES)
    assert cand["guess_topic"] == "product-security"
    assert "GHSA-xxxx-yyyy-zzzz" in cand["title"]
    assert cand["severity"] == "HIGH"
    assert "npm/leftpad" in cand["excerpt"]


def test_ghsa_ai_package_routes_to_ai_security():
    adv = {
        "ghsa_id": "GHSA-aaaa-bbbb-cccc",
        "summary": "Prompt injection in an LLM agent framework",
        "description": "Untrusted tool output reaches the model.",
        "severity": "critical",
        "html_url": "https://github.com/advisories/GHSA-aaaa-bbbb-cccc",
        "published_at": "2026-07-12T00:00:00Z",
        "vulnerabilities": [{"package": {"ecosystem": "pip", "name": "some-agent-lib"}}],
    }
    cand = gh.advisory_to_candidate(adv, RULES)
    assert cand["guess_domain"] == "AI Security"
    assert cand["guess_topic"] == "ai-security"


def test_ghsa_affected_packages_dedup():
    adv = {
        "vulnerabilities": [
            {"package": {"ecosystem": "npm", "name": "a"}},
            {"package": {"ecosystem": "npm", "name": "a"}},  # dup
            {"package": {"ecosystem": "pip", "name": "b"}},
        ]
    }
    assert gh._affected_packages(adv) == "npm/a, pip/b"


def test_ghsa_missing_id_or_url_returns_none():
    assert gh.advisory_to_candidate({"ghsa_id": "", "html_url": "https://x/y"}, RULES) is None
    assert gh.advisory_to_candidate({"ghsa_id": "GHSA-1", "html_url": ""}, RULES) is None
