"""Tests for scripts/ingest_youtube.py — URL building + candidate mapping."""

from __future__ import annotations

import ingest_youtube as iy


def test_channel_videos_url_forms():
    assert iy.channel_videos_url("@LiveOverflow") == "https://www.youtube.com/@LiveOverflow/videos"
    assert iy.channel_videos_url("UCabc123") == "https://www.youtube.com/channel/UCabc123/videos"
    assert iy.channel_videos_url("plainname") == "https://www.youtube.com/@plainname/videos"
    # a full URL keeps its host, gains /videos once (not twice)
    assert iy.channel_videos_url("https://youtube.com/@x") == "https://youtube.com/@x/videos"
    assert iy.channel_videos_url("https://youtube.com/@x/videos") == "https://youtube.com/@x/videos"


def test_video_to_candidate_maps_fields():
    v = {
        "webpage_url": "https://youtu.be/abc",
        "title": "Exploiting a parser bug",
        "upload_date": "20260701",
        "description": "A deep dive into the bug.",
        "channel": "LiveOverflow",
    }
    source = {"id": "youtube:lo", "rank": 70.0, "topics": ["product-security"]}
    cand = iy.video_to_candidate(v, source)
    assert cand["discovered_via"] == "youtube"
    assert cand["published"] == "2026-07-01" and cand["date"] == "2026-07"
    assert cand["source_id"] == "youtube:lo" and cand["source_rank"] == 70.0
    assert cand["article_url"] == "https://youtu.be/abc"


def test_video_to_candidate_requires_url_and_title():
    src = {"id": "s", "rank": 1, "topics": []}
    assert iy.video_to_candidate({"title": "x"}, src) is None  # no url
    assert iy.video_to_candidate({"webpage_url": "https://y", "title": ""}, src) is None


def test_video_to_candidate_handles_missing_date():
    v = {"webpage_url": "https://y", "title": "t"}
    cand = iy.video_to_candidate(v, {"id": "s", "rank": 1, "topics": []})
    assert cand["published"] is None and cand["date"] is None


def test_collect_empty_without_sources(sandbox):
    assert iy.collect(3) == []  # no youtube sources registered
