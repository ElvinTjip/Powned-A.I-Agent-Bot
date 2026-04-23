# sources

**Doel:** Definitie van alle nieuwsbronnen die de agent monitort. Geen scraping-logica hier — alleen configuratie.

**Input:** Geen (statische config)

**Output:** `list[SourceDefinition]` — importeerbaar door `scraper/` en `scheduler/pipeline.py`

## Structuur

- `v1_sources.py` — eerste bronnenlijst (RSS + HTML)

## RSS-feed URLs verificatie

De URLs in `v1_sources.py` zijn samengesteld op basis van bekende patronen. Verifieer elke URL handmatig voordat je de pipeline live zet:

```bash
python - <<'EOF'
import feedparser
from sources.v1_sources import RSS_SOURCES
for s in RSS_SOURCES:
    f = feedparser.parse(s.url)
    status = "OK" if f.entries else "LEEG/FOUT"
    print(f"{status:10} {s.name:30} {s.url}")
EOF
```

## Bronnen toevoegen

Voeg een `SourceDefinition` toe aan de relevante lijst in `v1_sources.py`. Type opties: `rss`, `html`, `playwright`, `imap`.
