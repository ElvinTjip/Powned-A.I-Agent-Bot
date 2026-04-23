# deduper

**Doel:** Filtert items die al in de database staan of sterk lijken op recent opgeslagen items.

**Input:** `list[dict]` (ruwe items) + een actieve database-sessie

**Output:** `list[dict]` — alleen de items die nieuw en uniek zijn

## Strategie

1. **Exacte URL-check** via `url_hash` (SHA-256) — O(1) via index
2. **Titel-similariteit** via `difflib.SequenceMatcher` — vergelijkt tegen items van de afgelopen 7 dagen

Drempel: ≥ 0.85 similariteit → als duplicaat beschouwd.

## Losse test

```bash
python - <<'EOF'
from deduper.deduper import is_near_duplicate
print(is_near_duplicate("Burgemeester betrapt op fout parkeren", "Burgemeester betrapt op verkeerd parkeren"))
# verwacht: True
print(is_near_duplicate("Vuurwerk verbod Rotterdam", "Trein ontspoord bij Zwolle"))
# verwacht: False
EOF
```

## Schaalbaarheid

Voor v1 (< 10.000 titels) is SequenceMatcher snel genoeg. Bij grotere schaal: vervang door MinHash/LSH.
