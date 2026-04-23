# TODO (fase 4): read editorial tips from a dedicated Gmail address via IMAP
# Credentials go in .env: IMAP_HOST, IMAP_USER, IMAP_PASSWORD
# Each unread email becomes one item with source_type="imap" and region=None.
# Mark emails as read after ingestion — do not delete them.


def scrape_imap() -> list[dict]:
    raise NotImplementedError("IMAP scraper not yet implemented")
