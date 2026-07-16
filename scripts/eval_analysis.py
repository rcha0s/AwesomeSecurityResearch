#!/usr/bin/env python3
"""
eval_analysis.py — Deterministic regression check on the analysis pipeline.

The LLM's judgement (novelty/relevance) can't be unit-tested, but the pieces
around it can, and they silently drift as the classifier keywords, the taxonomy,
or the grounding logic evolve. This runs two offline checks over a hand-labeled
golden set and fails (exit 1) if quality regresses — gate rubric/keyword changes
on it.

  1. Classification accuracy — the keyword classifier's topic (and domain) vs the
     golden labels. Catches a keyword edit that silently misroutes a topic.
  2. Grounding sanity — c.is_grounded must accept a real excerpt and reject a
     fabricated one. Catches a normalize_text/threshold change that would let
     hallucinated quotes through (or reject honest ones).

Usage:
    python scripts/eval_analysis.py            # report + gate
    python scripts/eval_analysis.py --json      # machine-readable report
"""

from __future__ import annotations

import argparse
import json

import aggregate as agg
import common as c

GOLDEN_DIR = c.ROOT / "evals" / "golden"
# Below this classification accuracy the run fails — the classifier has regressed.
MIN_ACCURACY = 0.85


def load_golden() -> list[dict]:
    return c.load_json(GOLDEN_DIR / "classification.json", default=[]) or []


def predict(item: dict, rules: dict) -> tuple[str | None, str | None]:
    """Predict (topic, domain) for a labeled item using the keyword classifier."""
    blob = f"{item.get('title', '')} {item.get('summary', '')}"
    domain = agg.classify_domain(blob, rules, [])  # strict: no single-domain fallback
    topic = c.topic_for_domain(domain) if domain else None
    return topic, domain


def evaluate_classification(golden: list[dict], rules: dict) -> dict:
    """Compare predicted vs expected topic for every golden item."""
    misses: list[dict] = []
    correct = 0
    for item in golden:
        topic, domain = predict(item, rules)
        if topic == item.get("expected_topic"):
            correct += 1
        else:
            misses.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "expected": item.get("expected_topic"),
                    "predicted": topic,
                    "predicted_domain": domain,
                }
            )
    total = len(golden)
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 3) if total else 0.0,
        "misses": misses,
    }


def grounding_sanity() -> dict:
    """is_grounded must accept a real excerpt and reject a fabricated one."""
    source = (
        "The agent re-injected the full tool output every turn, so context grew "
        "unbounded. Summarizing each result first cut token use by roughly 40%."
    )
    real = c.is_grounded("cut token use by roughly 40%", source)
    fake = c.is_grounded("the model achieved 99% accuracy on MMLU", source)
    return {
        "accepts_real": bool(real),
        "rejects_fake": not bool(fake),
        "ok": bool(real and not fake),
    }


def run() -> dict:
    rules = c.load_yaml(c.SOURCES_FILE)["classification"]
    golden = load_golden()
    cls = evaluate_classification(golden, rules)
    grd = grounding_sanity()
    passed = cls["accuracy"] >= MIN_ACCURACY and grd["ok"]
    return {"classification": cls, "grounding": grd, "min_accuracy": MIN_ACCURACY, "passed": passed}


def print_report(report: dict) -> None:
    cls = report["classification"]
    print(
        f"Classification: {cls['correct']}/{cls['total']} correct " f"(accuracy {cls['accuracy']})"
    )
    for miss in cls["misses"]:
        print(f"  MISS {miss['id']}: expected {miss['expected']!r}, got {miss['predicted']!r}")
        print(f"       {miss['title']}")
    grd = report["grounding"]
    status = "ok" if grd["ok"] else "FAIL"
    print(
        f"Grounding sanity: {status} (accepts_real={grd['accepts_real']}, rejects_fake={grd['rejects_fake']})"
    )
    print(
        f"\n{'PASS' if report['passed'] else 'FAIL'} (gate: accuracy >= {report['min_accuracy']})"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
