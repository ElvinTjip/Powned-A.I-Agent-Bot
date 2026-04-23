from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceDefinition:
    name: str
    type: str  # rss | html | playwright | imap
    url: str
    region: Optional[str] = None


# CHECK: verify each URL is still valid before going live
RSS_SOURCES: list[SourceDefinition] = [
    SourceDefinition("NOS Algemeen",        "rss", "https://feeds.nos.nl/nosnieuwsalgemeen",       "nationaal"),
    SourceDefinition("NOS Regio",           "rss", "https://feeds.nos.nl/nosnieuwsregio",          "nationaal"),
    SourceDefinition("GeenStijl",           "rss", "https://www.geenstijl.nl/rss.xml",             "nationaal"),
    SourceDefinition("RTV Oost",            "rss", "https://www.rtvoost.nl/rss",                   "Overijssel"),
    SourceDefinition("RTV Rijnmond",        "rss", "https://www.rtvrijmond.nl/rss",                "Zuid-Holland"),
    SourceDefinition("RTV Noord",           "rss", "https://www.rtvnoord.nl/rss",                  "Groningen"),
    SourceDefinition("NH Nieuws",           "rss", "https://www.nhnieuws.nl/rss",                  "Noord-Holland"),
    SourceDefinition("Omroep Brabant",      "rss", "https://www.omroepbrabant.nl/rss",             "Brabant"),
    SourceDefinition("L1",                  "rss", "https://www.l1.nl/rss.xml",                    "Limburg"),
    SourceDefinition("Omroep Gelderland",   "rss", "https://www.omroepgelderland.nl/rss",          "Gelderland"),
    SourceDefinition("Reddit r/nl",         "rss", "https://www.reddit.com/r/thenetherlands/.rss", "nationaal"),
]

# TODO (fase 4): add Playwright-based sources (Dumpert, paywall sites)
HTML_SOURCES: list[SourceDefinition] = []

ALL_SOURCES: list[SourceDefinition] = RSS_SOURCES + HTML_SOURCES
