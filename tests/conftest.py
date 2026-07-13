"""Shared pytest fixtures — isolate every test from the real data pools."""

from __future__ import annotations

import common
import pytest
import sources_registry


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Redirect all pool/candidate/output paths into a temp dir with empty pools."""
    data = tmp_path / "data"
    data.mkdir()
    pools = {t: data / f"{t}.json" for t in common.TOPICS}
    monkeypatch.setattr(common, "ROOT", tmp_path)
    monkeypatch.setattr(common, "DATA_DIR", data)
    monkeypatch.setattr(common, "POOL_FILES", pools)
    monkeypatch.setattr(common, "CANDIDATES_FILE", data / "candidates.json")
    monkeypatch.setattr(common, "ANALYSIS_OUT", data / "analysis_out.json")
    monkeypatch.setattr(common, "ARCHIVE_FILE", data / "archive.json")
    monkeypatch.setattr(common, "RAW_DIR", data / "_raw")
    monkeypatch.setattr(sources_registry, "REGISTRY_FILE", data / "sources.json")
    for topic in common.TOPICS:
        common.save_pool(topic, common.empty_pool(topic))
    return tmp_path


def make_entry(**over) -> dict:
    """A valid analyzed entry; override any field via kwargs."""
    entry = {
        "topic": "ai-research",
        "domain": "Agents & Harnesses",
        "subtype": "Orchestration",
        "title": "Compacting tool outputs cuts agent tokens",
        "source_url": "https://example.com/compact",
        "article_url": "https://example.com/compact",
        "date": "2026-07",
        "summary": "Summarize tool outputs before re-injecting.",
        "takeaway": "Compact tool outputs to shrink context cost.",
        "lessons": [
            {"point": "Summarize before re-injecting", "excerpt": "40% less", "confidence": 0.9}
        ],
        "scores": {"novelty": 80, "relevance": 85},
        "actionable": {
            "type": "harness",
            "title": "Add compaction",
            "detail": "Summarize big results.",
        },
        "tags": ["agents", "context"],
    }
    entry.update(over)
    return entry
