"""Tests for scripts/generate_skills.py — skill stubs + LEARNINGS digest."""

from __future__ import annotations

import common as c
import generate_skills as gs
from conftest import make_entry


def _skill_entry(**over):
    base = dict(
        track="security",
        domain="AI Security",
        subtype="Prompt Injection",
        title="Calendar input guard",
        source_url="https://a/cal",
        # novelty+relevance alone clear the threshold regardless of newness/wall-clock
        scores={"novelty": 100, "relevance": 100},
        actionable={
            "type": "skill",
            "title": "Calendar guard",
            "detail": "Strip instructions.",
            "skill_slug": "calendar-input-guard",
        },
    )
    base.update(over)
    return base


def test_skill_stub_created_for_high_composite(sandbox):
    conf = c.load_config()
    written = gs.write_skills([_skill_entry()], conf)
    assert "calendar-input-guard" in written
    path = sandbox / "skills" / "calendar-input-guard" / "SKILL.md"
    assert path.exists()
    body = path.read_text(encoding="utf-8")
    assert gs.AUTO_MARKER in body and "name: calendar-input-guard" in body


def test_low_composite_skill_skipped(sandbox):
    conf = c.load_config()
    low = _skill_entry(scores={"novelty": 1, "relevance": 1}, date="2020-01")
    assert gs.write_skills([low], conf) == []


def test_human_edited_skill_preserved(sandbox):
    conf = c.load_config()
    path = sandbox / "skills" / "calendar-input-guard" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("hand-written, no marker", encoding="utf-8")
    gs.write_skills([_skill_entry()], conf)
    assert path.read_text(encoding="utf-8") == "hand-written, no marker"


def test_main_writes_skill_and_learnings(sandbox):
    pool = c.load_pool("security")
    pool["entries"] = [_skill_entry()]
    c.save_pool("security", pool)
    assert gs.main() == 0
    assert (sandbox / "skills" / "calendar-input-guard" / "SKILL.md").exists()
    assert (sandbox / "LEARNINGS.md").exists()


def test_learnings_written_and_ranked(sandbox):
    conf = c.load_config()
    entries = [
        make_entry(title="low", source_url="https://a/1", scores={"novelty": 5, "relevance": 5}),
        make_entry(title="high", source_url="https://a/2", scores={"novelty": 95, "relevance": 95}),
    ]
    text = gs.render_learnings(entries, conf, ["some-skill"], "2026-07-09")
    assert text.index("high") < text.index("low")
    assert "Generated skills" in text
