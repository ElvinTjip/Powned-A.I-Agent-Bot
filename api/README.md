# api

**Doel:** FastAPI-applicatie. Serveert de feed-UI, verwerkt gebruikersacties en biedt een handmatige pipeline-trigger.

**Input:** HTTP-requests van browsers (HTMX + form posts)

**Output:** HTML-responses (Jinja2-templates) en JSON voor de trigger-endpoint

## Routes

| Method | Path | Beschrijving |
|--------|------|--------------|
| GET | `/` | Hoofd-feed (vereist login) |
| GET | `/login` | Start Google OAuth2-flow |
| GET | `/auth/callback` | OAuth2-callback van Google |
| GET | `/dev-login` | DEV_MODE bypass (nooit in productie) |
| GET | `/logout` | Sessie wissen |
| POST | `/items/{id}/feedback` | Favoriet / verberg / gebruikt |
| POST | `/admin/run-pipeline` | Handmatige pipeline-trigger |

## Sessies

Sessies worden opgeslagen in een signed cookie via `itsdangerous`. `SECRET_KEY` in `.env` moet een willekeurige 32-char string zijn.

## Losse test

```bash
uvicorn api.main:app --reload
# Ga naar http://localhost:8000/dev-login (DEV_MODE=true vereist)
```
