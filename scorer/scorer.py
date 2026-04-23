import json
import os
from pathlib import Path

import anthropic

_LENS_PATH = Path(__file__).parent / "powned_lens.md"
_MODEL = "claude-haiku-4-5-20251001"


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _load_lens() -> str:
    return _LENS_PATH.read_text(encoding="utf-8")


def score_item(title: str, summary: str | None) -> dict:
    """Return {"score": int 0-100, "reason": str}."""
    text = f"Titel: {title}\n\nSamenvatting: {summary or '(geen samenvatting beschikbaar)'}"

    message = _client().messages.create(
        model=_MODEL,
        max_tokens=256,
        system=_load_lens(),
        messages=[
            {
                "role": "user",
                "content": (
                    "Beoordeel dit nieuwsitem voor de PowNed-redactiefeed.\n\n"
                    f"{text}\n\n"
                    "Geef een JSON-object terug met twee velden:\n"
                    '- "score": geheel getal 0–100\n'
                    '- "reason": één Nederlandse zin waarom dit item wel of niet bij PowNed past\n\n'
                    "Geef alleen het JSON-object terug, geen andere tekst."
                ),
            }
        ],
    )

    raw = message.content[0].text.strip()
    try:
        result = json.loads(raw)
        return {
            "score": int(result.get("score", 0)),
            "reason": str(result.get("reason", "")),
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        # TODO: add structured logging
        return {"score": 0, "reason": "Scoring mislukt (parse error)"}


def score_batch(items: list[dict]) -> list[dict]:
    """Score items in-place. Adds 'score' and 'score_reason' to each dict."""
    for item in items:
        result = score_item(item["title"], item.get("summary"))
        item["score"] = result["score"]
        item["score_reason"] = result["reason"]
    return items
