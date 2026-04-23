# scheduler

**Doel:** Tijdsgebaseerde triggers voor de pipeline + de pipeline-orchestratie zelf.

**Input:** geen externe input — draait op cron of via de `/admin/run-pipeline` endpoint

**Output:** nieuw gescoorde items in de database

## Bestanden

- `scheduler.py` — APScheduler-setup (dagelijks 08:30)
- `pipeline.py` — voert de volledige run uit: scrape → dedup → score → opslaan

## Pipeline-stappen

```
voor elke actieve bron
  → scraper haalt ruwe items op
  → deduper filtert duplicaten
→ scorer scoort alle nieuwe items in batch
→ items worden opgeslagen in de DB
```

## Losse test (zonder scheduler)

```bash
ANTHROPIC_API_KEY=sk-ant-... DATABASE_URL=postgresql://... python - <<'EOF'
from scheduler.pipeline import run_pipeline
run_pipeline()
EOF
```

## Schema

Dagelijks om 08:30. Aanpassen in `scheduler.py` via de `CronTrigger`-parameters.
