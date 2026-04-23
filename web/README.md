# web

**Doel:** HTMX-frontend voor de redactiefeed. Server-side rendered via Jinja2-templates in FastAPI.

**Input:** template-context vanuit `api/routes/`

**Output:** HTML-pagina's en partials (voor HTMX-swaps)

## Structuur

```
web/
  static/
    style.css
  templates/
    base.html              layout shell
    login.html             inlogpagina
    feed.html              hoofd-feed
    partials/
      card.html            één nieuwskaart (ook gebruikt voor HTMX-swaps)
      filters.html         sidebar met regio/score-filters
```

## HTMX-swaps

- **Favoriet-knop**: stuurt POST naar `/items/{id}/feedback`, ontvangt bijgewerkte `card.html` terug
- **Verberg-knop**: stuurt POST, ontvangt lege string → kaart verdwijnt uit DOM
- **Nu vernieuwen**: stuurt POST naar `/admin/run-pipeline`, geen swap (knop toont loading-state via `htmx-indicator`)

## Styling

Geen framework — puur CSS in `style.css`. PowNed-rood: `#e30613`.
