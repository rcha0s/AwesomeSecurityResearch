#!/usr/bin/env python3
"""
common.py — Shared foundation for the research analyzer pipeline.

Everything that more than one script needs lives here: path constants, config
loading, the entry schema + validation, small text/url helpers (reused by the
aggregators), deterministic scoring math (reused by rerank + tests), and the
Jina Reader article fetch used by every ingestion path.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# Windows consoles default to cp1252, which can't encode much of the research
# text we print (curly quotes, non-breaking hyphens, emoji). Force UTF-8 so the
# pipeline never crashes on a stray glyph.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # pragma: no cover - already-detached streams
            pass

try:
    import yaml
    from dateutil import parser as dateparser
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("Missing dependencies. Run: pip install -r requirements.txt") from exc

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CONFIG_FILE = ROOT / "config.yaml"
SOURCES_FILE = ROOT / "scripts" / "sources.yaml"

CANDIDATES_FILE = DATA_DIR / "candidates.json"
ANALYSIS_OUT = DATA_DIR / "analysis_out.json"
ARCHIVE_FILE = DATA_DIR / "archive.json"
RAW_DIR = DATA_DIR / "_raw"

SCHEMA_VERSION = "3.0"
JINA_READER = "https://r.jina.ai/"

# --- Topics: the three tracked databases -----------------------------------
# Each topic is its own rolling pool + rendered directory. `domains` are
# suggested sub-groupings (not enforced — the analyzer picks a sensible one).
TOPICS: dict[str, dict] = {
    "ai-security": {
        "name": "AI Security",
        "blurb": "Securing AI systems: harness & agent security, MCP, skill scanning, "
        "prompt injection, memory poisoning, model supply chain, LLM red-teaming.",
        "domains": [
            "Harness & Agent Security",
            "MCP & Tools",
            "Prompt Injection",
            "Memory & Context Poisoning",
            "Model Supply Chain",
            "LLM Red-Teaming",
            "RAG / Data Poisoning",
            "Information Disclosure",
        ],
    },
    "product-security": {
        "name": "Product Security",
        "blurb": "Securing products: application security, supply chain, cloud & infra, "
        "identity, mobile, plus red teaming and threat modeling (AI-assisted or not).",
        "domains": [
            "Application Security",
            "Supply Chain & Dependencies",
            "Cloud & Infrastructure",
            "Identity & Access",
            "Mobile Security",
            "Threat Modeling & Red Teaming",
            "Detection & Response",
            "AI-Generated Code Risk",
        ],
    },
    "ai-research": {
        "name": "AI Research",
        "blurb": "Practitioner AI: improving your harness, understanding, and architecture "
        "for using LLMs/agents on real tasks. Not model internals or ML-research.",
        "domains": [
            "Agents & Harnesses",
            "Prompting & Context",
            "Tooling & Infrastructure",
            "Evaluation",
            "Architecture & Optimization",
            "Models & Capabilities",
        ],
    },
}

# Convenience: {topic: [domains]} (mirrors the old TRACK_DOMAINS shape).
TOPIC_DOMAINS: dict[str, list[str]] = {k: v["domains"] for k, v in TOPICS.items()}

POOL_FILES: dict[str, Path] = {t: DATA_DIR / f"{t}.json" for t in TOPICS}

# Maps the legacy 2-track domains onto the three topics (used to migrate old
# data and to coarse-guess a topic at ingest from the keyword classifier).
LEGACY_DOMAIN_TO_TOPIC: dict[str, str] = {
    "AI Security": "ai-security",
    "Web Application Security": "product-security",
    "Mobile Security": "product-security",
    "Agents & Harnesses": "ai-research",
    "Prompting & Context": "ai-research",
    "Models & Capabilities": "ai-research",
    "Tooling & Infrastructure": "ai-research",
    "Evaluation & Safety": "ai-research",
}

ACTIONABLE_TYPES = ("takeaway", "skill", "harness", "tool", "other")
DISCOVERED_VIA = ("twitter", "linkedin", "rss", "github", "youtube", "manual")


def domain_slug(domain: str) -> str:
    """Directory-safe slug for a domain, e.g. 'AI Security' -> 'ai-security'."""
    return slugify(domain)


def topic_for_domain(domain: str) -> str | None:
    """Best topic for a (possibly legacy) domain string."""
    if domain in LEGACY_DOMAIN_TO_TOPIC:
        return LEGACY_DOMAIN_TO_TOPIC[domain]
    for topic, domains in TOPIC_DOMAINS.items():
        if domain in domains:
            return topic
    return None


# --- Config ----------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    weights: dict[str, float]
    half_life_days: float
    skill_composite_threshold: float
    confidence_min: float
    limits: dict[str, int]
    curation: dict[str, float]
    max_age_days: int


def load_config(path: Path = CONFIG_FILE) -> Config:
    raw = load_yaml(path)
    weights = raw["weights"]
    total = sum(weights.get(k, 0) for k in ("newness", "novelty", "relevance"))
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"config weights must sum to 1.0 (got {total})")
    return Config(
        weights=weights,
        half_life_days=float(raw["half_life_days"]),
        skill_composite_threshold=float(raw["skill_composite_threshold"]),
        confidence_min=float(raw["confidence_min"]),
        limits=raw.get("limits", {}),
        curation=raw.get("curation", {}),
        max_age_days=int(raw.get("max_age_days", 31)),
    )


# --- IO --------------------------------------------------------------------
def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def empty_pool(topic: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "topic": topic,
        "name": TOPICS[topic]["name"],
        "domains": TOPICS[topic]["domains"],
        "entries": [],
    }


def load_pool(topic: str) -> dict:
    pool = load_json(POOL_FILES[topic], default=None)
    return pool if pool else empty_pool(topic)


def save_pool(topic: str, pool: dict) -> None:
    save_json(POOL_FILES[topic], pool)


# --- Text / URL helpers (reused by both aggregators) -----------------------
def normalize_url(url: str) -> str:
    url = (url or "").strip().lower()
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"\?.*$", "", url)
    return url.rstrip("/")


_TRACKING_PARAM = re.compile(r"^(utm_|fbclid|gclid|mc_|ref$|ref_|igshid|si$)", re.I)


def clean_source_url(url: str) -> str:
    """Strip tracking query params (utm_*, fbclid, …) for clean public citations.

    Keeps meaningful query params; only removes known tracking keys. Preserves
    case and path (unlike normalize_url, which is for de-duplication only).
    """
    url = (url or "").strip()
    if "?" not in url:
        return url
    base, _, query = url.partition("?")
    kept = [
        pair
        for pair in query.split("&")
        if pair and not _TRACKING_PARAM.match(pair.split("=", 1)[0])
    ]
    return f"{base}?{'&'.join(kept)}" if kept else base


def slugify(text: str, limit: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:limit].strip("-") or "item"


def make_id(title: str, url: str) -> str:
    digest = hashlib.sha1((title + url).encode("utf-8")).hexdigest()[:10]
    return f"{slugify(title, 48)}-{digest}"


def clean_summary(raw: str, limit: int = 320) -> str:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def title_similar(a: str, b: str, threshold: float = 0.87) -> bool:
    """Fuzzy title match for cross-source de-duplication."""
    na = re.sub(r"\s+", " ", (a or "").lower()).strip()
    nb = re.sub(r"\s+", " ", (b or "").lower()).strip()
    if not na or not nb:
        return False
    return SequenceMatcher(None, na, nb).ratio() >= threshold


def entry_datetime(entry: dict) -> datetime | None:
    for key in ("published", "updated", "created"):
        val = entry.get(key)
        if val:
            try:
                dt = dateparser.parse(val)
                return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
            except (ValueError, OverflowError, TypeError):
                continue
    for key in ("published_parsed", "updated_parsed"):
        val = entry.get(key)
        if val:
            return datetime(*val[:6], tzinfo=UTC)
    return None


def extract_urls(text: str) -> list[str]:
    """Pull http(s) URLs out of free text (tweet bodies), de-duplicated."""
    found = re.findall(r"https?://[^\s<>\"')]+", text or "")
    seen: dict[str, None] = {}
    for url in found:
        seen.setdefault(url.rstrip(".,);"), None)
    return list(seen)


def date_from_url(url: str) -> str | None:
    """Extract a publish date embedded in a URL path, e.g. /2026/05/13/ or
    /2026/05/. Returns YYYY-MM-DD or YYYY-MM, or None. Many blogs (OWASP, Unit42,
    Google, Microsoft, Project Zero) date their permalinks this way."""
    m = re.search(r"/(20\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])(?:/|-)", url or "")
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"/(20\d{2})/(0[1-9]|1[0-2])/", url or "")
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def to_month(date: str | None) -> str | None:
    """Coerce a full or partial date string to YYYY-MM (for newness scoring)."""
    return date[:7] if date and len(date) >= 7 and date[4] == "-" else None


def best_date(entry: dict) -> str | None:
    """The most precise source date available for an entry."""
    return entry.get("published") or entry.get("date")


def parse_date_end(date: str | None) -> datetime | None:
    """Parse YYYY-MM-DD, or YYYY-MM as the LAST day of that month (lenient — a
    month-only date shouldn't age out early). Returns None if unparseable."""
    if not date:
        return None
    try:
        return datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        pass
    try:
        start = datetime.strptime(date[:7], "%Y-%m").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return None
    nxt = start.replace(year=start.year + (start.month == 12), month=start.month % 12 + 1)
    return nxt - timedelta(days=1)


def is_fresh(entry: dict, max_age_days: int, now: datetime | None = None) -> bool:
    """True if the entry's source date is within the freshness window. Undated
    entries are treated as fresh (we don't drop what we can't date)."""
    dt = parse_date_end(best_date(entry))
    if dt is None:
        return True
    now = now or datetime.now(UTC)
    return (now - dt).days <= max_age_days


# --- Scoring math (deterministic; shared by rerank + tests) ----------------
def parse_month(date: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(date, fmt).replace(tzinfo=UTC)
        except (ValueError, TypeError):
            continue
    return None


def newness_score(date: str, half_life_days: float, now: datetime | None = None) -> int:
    """Time-decayed newness in [0, 100]; halves every half_life_days."""
    published = parse_month(date)
    if published is None:
        return 0
    now = now or datetime.now(UTC)
    age_days = max(0.0, (now - published).total_seconds() / 86400.0)
    return round(100 * math.exp(-age_days / max(1.0, half_life_days)))


def composite_score(scores: dict, weights: dict[str, float]) -> float:
    total = sum(
        weights.get(axis, 0.0) * float(scores.get(axis, 0) or 0)
        for axis in ("newness", "novelty", "relevance")
    )
    return round(total, 2)


def entry_composite(entry: dict, conf: Config) -> float:
    """An entry's composite, recomputing decayed newness if it's missing."""
    scores = dict(entry.get("scores") or {})
    if "composite" in scores:
        return float(scores["composite"])
    scores["newness"] = newness_score(best_date(entry) or "", conf.half_life_days)
    return composite_score(scores, conf.weights)


def is_curated(entry: dict, conf: Config) -> bool:
    """True if the finding belongs in the public curated view (topic pages +
    newsletter). Everything else — flagged needs_review OR below the composite
    floor — is held in the REVIEW.md queue (still in the pool, just not shown)."""
    if entry.get("needs_review"):
        return False
    return entry_composite(entry, conf) >= conf.curation.get("min_composite", 0)


def review_reason(entry: dict, conf: Config) -> str:
    """Why an entry is in the review queue (for REVIEW.md)."""
    if entry.get("needs_review"):
        return "flagged needs_review (low confidence / novelty / relevance)"
    return (
        f"composite {entry_composite(entry, conf)} < floor {conf.curation.get('min_composite', 0)}"
    )


# --- Schema validation -----------------------------------------------------
# `topic` is the hard constraint; `domain` is a free-text sub-grouping label
# (the analyzer picks a sensible one, so we don't enforce membership).
REQUIRED_FIELDS = ("topic", "domain", "title", "source_url")


def validate_entry(entry: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not entry.get(field):
            errors.append(f"missing required field: {field}")
    topic = entry.get("topic")
    if topic and topic not in TOPICS:
        errors.append(f"unknown topic: {topic} (want one of {tuple(TOPICS)})")
    actionable = entry.get("actionable")
    if actionable is not None:
        if not isinstance(actionable, dict):
            errors.append("actionable must be an object")
        elif actionable.get("type") not in ACTIONABLE_TYPES:
            errors.append(f"actionable.type must be one of {ACTIONABLE_TYPES}")
    lessons = entry.get("lessons")
    if lessons is not None and not isinstance(lessons, list):
        errors.append("lessons must be a list")
    return errors


# --- Pool / candidate helpers (shared by ingestors + merge) ----------------
def all_pool_entries() -> list[dict]:
    entries: list[dict] = []
    for topic in TOPICS:
        entries += load_pool(topic)["entries"]
    return entries


def known_urls() -> set[str]:
    """Normalized source/article URLs already present in either pool."""
    urls: set[str] = set()
    for entry in all_pool_entries():
        for key in ("source_url", "article_url", "tweet_url"):
            if entry.get(key):
                urls.add(normalize_url(entry[key]))
    return urls


def archive_entries(entries: list[dict]) -> int:
    """Append aged-out entries to data/archive.json, de-duped by id. Preserves
    history so the growing pool isn't lost even though the live tracker prunes."""
    if not entries:
        return 0
    existing = load_json(ARCHIVE_FILE, default=[]) or []
    seen = {e.get("id") for e in existing}
    added = [e for e in entries if e.get("id") not in seen]
    if added:
        save_json(ARCHIVE_FILE, existing + added)
    return len(added)


def load_candidates() -> list[dict]:
    return load_json(CANDIDATES_FILE, default=[]) or []


def save_candidates(candidates: list[dict]) -> None:
    save_json(CANDIDATES_FILE, candidates)


def add_candidates(new: list[dict]) -> list[dict]:
    """Merge new candidates into the staging file, de-duped by URL + title.

    De-dupes against both the existing staging queue and the published pools,
    so nothing already analyzed gets re-queued. Returns the actually-added list.
    """
    existing = load_candidates()
    max_age = load_config().max_age_days
    seen_urls = known_urls() | {normalize_url(c.get("source_url", "")) for c in existing}
    seen_titles = [c.get("title", "") for c in existing] + [
        e.get("title", "") for e in all_pool_entries()
    ]
    added: list[dict] = []
    for cand in new:
        nurl = normalize_url(cand.get("source_url", ""))
        if not nurl or nurl in seen_urls:
            continue
        # HARD freshness gate: never stage anything older than the window.
        if not is_fresh(cand, max_age):
            continue
        if any(title_similar(cand.get("title", ""), t) for t in seen_titles):
            continue
        existing.append(cand)
        added.append(cand)
        seen_urls.add(nurl)
        seen_titles.append(cand.get("title", ""))
    if added:
        save_candidates(existing)
    return added


def utcnow_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def write_raw(cand_id: str, text: str) -> str:
    """Persist fetched article text to data/_raw/<id>.txt; return its path str."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{cand_id}.txt"
    path.write_text(text, encoding="utf-8")
    return str(path.relative_to(ROOT))


def fetch_readable(url: str, timeout: int = 30, max_chars: int = 20000) -> str:
    """Fetch clean reader text for a URL via Jina Reader. Raises on failure."""
    import requests  # local import keeps offline unit tests import-clean

    resp = requests.get(
        JINA_READER + url,
        timeout=timeout,
        headers={"Accept": "text/plain", "User-Agent": "AwesomeSecurityResearch/1.0"},
    )
    resp.raise_for_status()
    text = resp.text.strip()
    if not text:
        raise RuntimeError(f"empty reader response for {url}")
    return text[:max_chars]
