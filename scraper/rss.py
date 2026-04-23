import hashlib
from datetime import datetime, timezone

import feedparser

from sources.v1_sources import SourceDefinition

_PAYWALL_KEYWORDS = ("abonnement", "inloggen", "subscriber", "premium", "paywall", "alleen voor abonnees")


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _detect_paywall(entry: dict) -> bool:
    text = (entry.get("summary", "") + " " + entry.get("title", "")).lower()
    return any(kw in text for kw in _PAYWALL_KEYWORDS)


def _parse_date(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return None


def scrape_rss(source: SourceDefinition) -> list[dict]:
    feed = feedparser.parse(source.url)
    items = []

    for entry in feed.entries:
        url = entry.get("link", "").strip()
        if not url:
            continue

        items.append({
            "url": url,
            "url_hash": _hash_url(url),
            "title": entry.get("title", "").strip(),
            "summary": entry.get("summary", "").strip() or None,
            "region": source.region,
            "published_at": _parse_date(entry),
            "is_paywall": _detect_paywall(entry),
            "source_name": source.name,
            "source_type": source.type,
            "source_url": source.url,
        })

    return items
