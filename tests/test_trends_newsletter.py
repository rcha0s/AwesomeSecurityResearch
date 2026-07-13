"""Tests for scripts/trends.py and scripts/generate_newsletter.py."""

from __future__ import annotations

from datetime import UTC, datetime

import common as c
import generate_newsletter as nl
import trends
from conftest import make_entry


def _seed_cluster(topic="ai-security"):
    pool = c.load_pool(topic)
    pool["entries"] = [
        make_entry(
            topic=topic,
            domain="MCP & Tools",
            title="Tool A",
            source_url="https://a/1",
            source_id="src-1",
            tags=["agent-security", "mcp"],
            published="2026-07-01",
        ),
        make_entry(
            topic=topic,
            domain="MCP & Tools",
            title="Tool B",
            source_url="https://a/2",
            source_id="src-2",
            tags=["agent-security"],
            published="2026-07-02",
        ),
    ]
    c.save_pool(topic, pool)


def test_build_trends_clusters_by_tag(sandbox):
    _seed_cluster()
    conf = c.load_config()
    result = trends.build_trends("ai-security", conf, datetime(2026, 7, 13, tzinfo=UTC))
    tags = {t["tag"] for t in result}
    assert "agent-security" in tags  # 2 findings, 2 sources -> qualifies
    assert "mcp" not in tags  # only 1 finding -> below threshold


def test_trends_main_writes_files(sandbox):
    _seed_cluster()
    assert trends.main() == 0
    assert (sandbox / "TRENDS.md").exists()
    assert (c.DATA_DIR / "trends.json").exists()
    body = (sandbox / "TRENDS.md").read_text(encoding="utf-8")
    assert "agent-security" in body


def test_newsletter_has_all_topics(sandbox):
    _seed_cluster()
    trends.main()
    assert nl.main() == 0
    text = (sandbox / "NEWSLETTER.md").read_text(encoding="utf-8")
    for meta in c.TOPICS.values():
        assert meta["name"] in text
    assert "Emerging trends" in text
    assert "Tool A" in text  # latest research surfaced
