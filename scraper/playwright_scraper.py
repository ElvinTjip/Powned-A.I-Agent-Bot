from sources.v1_sources import SourceDefinition

# TODO (fase 4): implement JS-heavy scraping with Playwright
# Legal note: only use where RSS is unavailable; never bypass logins or paywalls.
# X/Twitter via Nitter: technically works but violates X ToS — document the risk explicitly.


def scrape_playwright(source: SourceDefinition) -> list[dict]:
    raise NotImplementedError(f"Playwright scraper not yet implemented for: {source.name}")
