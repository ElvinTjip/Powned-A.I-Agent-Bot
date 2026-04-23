from sources.v1_sources import SourceDefinition

# TODO (fase 4): implement HTML scraping with httpx + BeautifulSoup
# Legal note: respect robots.txt and rate-limit to >= 1 req / 2s


def scrape_html(source: SourceDefinition) -> list[dict]:
    raise NotImplementedError(f"HTML scraper not yet implemented for: {source.name}")
