# scraper

**Doel:** Haalt ruwe nieuwsitems op uit externe bronnen. Elke scraper-variant spreekt één brontype aan en geeft een uniforme `list[dict]` terug.

**Input:** `SourceDefinition` (uit `sources/`)

**Output:** `list[dict]` met velden: `url`, `url_hash`, `title`, `summary`, `region`, `published_at`, `is_paywall`, `source_name`, `source_type`, `source_url`

## Scraper-varianten

| Bestand | Type | Status |
|---------|------|--------|
| `rss.py` | RSS via feedparser | actief |
| `html.py` | HTML via httpx + BeautifulSoup | stub (fase 4) |
| `playwright_scraper.py` | JS-heavy sites | stub (fase 4) |
| `imap.py` | Gmail IMAP voor e-mailtips | stub (fase 4) |

## Losse test

```bash
python - <<'EOF'
from sources.v1_sources import RSS_SOURCES
from scraper.rss import scrape_rss
items = scrape_rss(RSS_SOURCES[0])
for i in items[:3]:
    print(i["title"], "|", i["region"])
EOF
```

## Juridische noten

- **RSS**: altijd legaal, altijd de voorkeur
- **HTML-scraping**: respecteer `robots.txt`, rate-limit op ≥1 req/2s, geen loginomzeiling
- **Playwright**: zware afhankelijkheid — gebruik alleen waar RSS ontbreekt
- **X/Twitter via Nitter**: werkt, maar schendt de X ToS — gebruik op eigen verantwoordelijkheid en documenteer het risico in je README
