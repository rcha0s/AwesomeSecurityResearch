"""Tests for grounding/citation verification."""

from __future__ import annotations

import common as c
import verify_citations as vc

SOURCE = (
    "Attackers inflate the skill file size to exceed scanner thresholds, bypassing "
    "both ClawScan and VirusTotal detection. This is a novel supply-chain evasion."
)


def test_is_grounded_verbatim_and_fuzzy():
    assert c.is_grounded("inflate the skill file size to exceed scanner thresholds", SOURCE)
    assert c.is_grounded("Inflate the skill file size to exceed scanner thresholds.", SOURCE)
    assert not c.is_grounded("attackers use a rootkit to disable antivirus", SOURCE)
    assert not c.is_grounded("", SOURCE)


def test_is_grounded_folds_typography():
    # verbatim quote must ground even if the source uses en-dashes / curly quotes
    src = "predicted 18–51 days ahead, and the model doesn’t “save” the key."
    assert c.is_grounded("18-51 days ahead", src)  # hyphen vs en-dash
    assert c.is_grounded('doesn\'t "save" the key', src)  # straight vs curly quotes


def test_ground_entry_scores_lessons():
    entry = {
        "lessons": [
            {"point": "evasion", "excerpt": "inflate the skill file size to exceed scanner"},
            {"point": "made up", "excerpt": "this quote does not appear anywhere at all"},
            {"point": "no excerpt"},  # ignored
        ]
    }
    vc.ground_entry(entry, source_text=SOURCE)
    assert entry["lessons"][0]["grounded"] is True
    assert entry["lessons"][1]["grounded"] is False
    assert entry["grounding_score"] == 0.5  # 1 of 2 excerpt-bearing lessons grounded


def test_ground_entry_unverifiable_when_no_source():
    entry = {"lessons": [{"point": "x", "excerpt": "y"}], "source_url": "manual:abc"}
    vc.ground_entry(entry, source_text=None)
    assert entry["grounding_score"] is None  # can't fetch a manual source


def test_fully_grounded():
    assert vc.fully_grounded({"grounding_score": None})  # unverifiable != ungrounded
    assert vc.fully_grounded({"grounding_score": 1.0})
    assert not vc.fully_grounded({"grounding_score": 0.5})


def test_source_text_from_raw_path(sandbox):
    raw = c.RAW_DIR / "x.txt"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(SOURCE, encoding="utf-8")
    text = vc.source_text_for({"raw_path": str(raw.relative_to(c.ROOT))})
    assert "ClawScan" in text


def test_merge_flags_ungrounded(sandbox, monkeypatch):
    import merge_analysis as m
    from conftest import make_entry

    # force a source with text that does NOT contain the excerpt
    monkeypatch.setattr(vc, "source_text_for", lambda e: "totally unrelated source text")
    conf = c.load_config()
    entry = make_entry(
        topic="ai-security",
        domain="MCP",
        source_url="https://a/x",
        lessons=[{"point": "p", "excerpt": "an invented quote", "confidence": 0.9}],
    )
    merged, _, _, _ = m.merge([entry], conf)
    assert merged[0]["needs_review"] is True  # ungrounded excerpt held for review
