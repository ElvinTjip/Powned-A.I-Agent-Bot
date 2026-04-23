# scorer

**Doel:** Scoort elk nieuwsitem op PowNed-relevantie (0–100) via Claude Haiku en geeft een Nederlandse uitleg per item.

**Input:** `list[dict]` met velden `title` en `summary`

**Output:** dezelfde lijst, aangevuld met `score` (int) en `score_reason` (str)

## Bestanden

- `scorer.py` — Anthropic API-aanroepen en batch-logica
- `powned_lens.md` — de system prompt die de PowNed-bril definieert (**hier tune je**)

## De PowNed-bril aanpassen

Open `powned_lens.md` en pas de voorbeelden of scoringsregels aan. De prompt wordt bij elke scoring-run opnieuw ingelezen — geen herstart nodig.

## Losse test

```bash
ANTHROPIC_API_KEY=sk-ant-... python - <<'EOF'
from scorer.scorer import score_item
result = score_item(
    title="Burgemeester betrapt op doublepark voor gemeentehuis",
    summary="De burgemeester van Almelo parkeerde herhaaldelijk zijn dienstauto op een invalidentijdsplaats."
)
print(result)
EOF
```

## Kostenraming

Claude Haiku (claude-haiku-4-5-20251001): ~$0.25 / 1M input tokens, ~$1.25 / 1M output.
Bij 200 items/dag × 600 tokens/item ≈ **< €1/maand**. Ruim binnen budget.
