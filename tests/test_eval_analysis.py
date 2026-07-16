"""Tests for scripts/eval_analysis.py — the golden-set classifier + grounding gate."""

from __future__ import annotations

import common as c
import eval_analysis as ev


def test_golden_set_meets_accuracy_bar():
    report = ev.run()
    assert report["classification"]["total"] >= 10  # a real golden set, not a stub
    assert report["classification"]["accuracy"] >= ev.MIN_ACCURACY
    assert report["passed"] is True


def test_grounding_sanity_discriminates():
    grd = ev.grounding_sanity()
    assert grd["accepts_real"] is True and grd["rejects_fake"] is True


def test_evaluate_flags_a_mislabeled_item():
    rules = c.load_yaml(c.SOURCES_FILE)["classification"]
    # a web-smuggling story deliberately mislabeled as ai-security must count as a miss
    bad = [
        {
            "id": "x",
            "title": "HTTP request smuggling desync",
            "summary": "waf bypass",
            "expected_topic": "ai-security",
        }
    ]
    result = ev.evaluate_classification(bad, rules)
    assert result["correct"] == 0 and len(result["misses"]) == 1
    assert result["misses"][0]["predicted"] == "product-security"
