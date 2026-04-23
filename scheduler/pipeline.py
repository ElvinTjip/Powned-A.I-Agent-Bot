from datetime import datetime, timedelta, timezone

from api.database import SessionLocal
from api.models import Item, Source
from deduper.deduper import filter_new_items
from scorer.scorer import score_batch
from scraper.rss import scrape_rss
from sources.v1_sources import ALL_SOURCES, SourceDefinition

_RETENTION_DAYS = 30


def _get_or_create_source(db, source_def: SourceDefinition) -> Source:
    source = db.query(Source).filter(Source.url == source_def.url).first()
    if not source:
        source = Source(
            name=source_def.name,
            type=source_def.type,
            url=source_def.url,
            region=source_def.region,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run_pipeline() -> None:
    db = SessionLocal()
    try:
        raw_items: list[dict] = []

        for source_def in ALL_SOURCES:
            if source_def.type != "rss":
                # TODO (fase 4): dispatch to html/playwright/imap scrapers
                continue

            source = _get_or_create_source(db, source_def)
            items = scrape_rss(source_def)
            for item in items:
                item["source_id"] = source.id
            raw_items.extend(items)

        new_items = filter_new_items(raw_items, db)
        if not new_items:
            return

        scored_items = score_batch(new_items)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=_RETENTION_DAYS)

        for data in scored_items:
            item = Item(
                url=data["url"],
                url_hash=data["url_hash"],
                title=data["title"],
                summary=data.get("summary"),
                source_id=data["source_id"],
                region=data.get("region"),
                published_at=data.get("published_at"),
                score=data.get("score"),
                score_reason=data.get("score_reason"),
                is_paywall=data.get("is_paywall", False),
                scraped_at=now,
                expires_at=expires_at,
            )
            db.add(item)

        db.commit()
    finally:
        db.close()
