# PowNed Redactie Agent

Automated news feed for the PowNed editorial team. Monitors regional and national Dutch news sources, scores items on PowNed relevance using Claude Haiku, and presents the best items in a login-protected web feed.

## Quick start (local)

```bash
cp .env.example .env      # fill in ANTHROPIC_API_KEY and POSTGRES_PASSWORD
docker compose up         # starts PostgreSQL + app
```

Open http://localhost:8000 — in DEV_MODE you can bypass Google SSO via `/dev-login`.

## Modules

| Module | Responsibility |
|--------|----------------|
| `sources/` | Source definitions (RSS feeds, scrape targets, social accounts) |
| `scraper/` | Ingestion: RSS, HTML, Playwright, IMAP |
| `scorer/` | AI relevance scoring via Claude Haiku |
| `deduper/` | Deduplication (URL hash + title similarity) |
| `api/` | FastAPI backend + routes |
| `web/` | HTMX frontend templates + static assets |
| `scheduler/` | APScheduler + pipeline orchestration |

## Score thresholds

| Score | Behaviour |
|-------|-----------| 
| 60–100 | Prominent in feed |
| 40–59 | Visible but lower ranked |
| 0–39 | Filtered out (default threshold) |

Threshold is configurable per user via the slider in the feed sidebar.

## Ethics note

Paywalled articles are shown with a **paywall** badge and a direct link. The agent never attempts to bypass logins or paywalls automatically.
