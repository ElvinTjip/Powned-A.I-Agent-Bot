from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from api.models import Item

_TITLE_THRESHOLD = 0.85
_LOOKBACK_DAYS = 7


def is_near_duplicate(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= _TITLE_THRESHOLD


def filter_new_items(items: list[dict], db: Session) -> list[dict]:
    """Remove items already present in the DB or near-duplicate of a recent title."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=_LOOKBACK_DAYS)
    recent_titles: list[str] = [
        t for (t,) in db.query(Item.title).filter(Item.scraped_at >= cutoff).all()
    ]

    new_items: list[dict] = []
    seen_hashes: set[str] = set()

    for item in items:
        # Exact duplicate within this batch
        if item["url_hash"] in seen_hashes:
            continue

        # Exact duplicate in DB
        if db.query(Item.id).filter(Item.url_hash == item["url_hash"]).first():
            continue

        # Near-duplicate title
        # TODO: replace with MinHash/LSH when recent_titles exceeds ~10k entries
        if any(is_near_duplicate(item["title"], t) for t in recent_titles):
            continue

        seen_hashes.add(item["url_hash"])
        new_items.append(item)

    return new_items
