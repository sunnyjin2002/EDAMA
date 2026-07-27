# Elite Dangerous Translator

EN-CN article translation workflow module for the EDAMA project.
Provides glossary management, translation memory, and manual
article submission. Translation, review, tagging, and publishing
workflows are planned in upcoming phases.

This module is imported by the main EDAMA backend and served
through the shared FastAPI application. All routes are accessible
at `http://localhost:3312/<route>` and rendered by the Next.js
frontend at `http://localhost:3302`.

## Glossary

Glossary CSV files live under `data/glossary/`. Supported columns:

- `source_term_en`
- `approved_term_zh`
- `aliases_en`
- `entity_type`
- `notes`
- `status`

Import one file from the command line:

```
python scripts/import_glossary.py data/glossary/example.csv
```

Import every CSV file under `data/glossary/`:

```
python scripts/import_glossary.py
```

The glossary page at `/glossary` (frontend: `http://localhost:3302/glossary`)
supports search, CSV import, and entry management.

API endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/glossary` | List entries (optional `?q=` search) |
| GET | `/glossary/{id}` | Get single entry |
| POST | `/glossary` | Create entry (JSON body) |
| PUT | `/glossary/{id}` | Update entry (JSON body) |
| POST | `/glossary/import` | Import CSV (multipart upload or file name) |

## Translation Memory

Translation memory CSV files live under
`data/references/translation_memory/`. Supported columns:

- `source_text`
- `translated_text`
- `source_reference`
- `tags`

Import one file:

```
python scripts/import_translation_memory.py data/references/translation_memory/example.csv
```

Import all files in the directory:

```
python scripts/import_translation_memory.py
```

The translation memory page at `/translation-memory` supports
search, CSV import, and side-by-side review.

API endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/translation-memory` | List entries (optional `?q=` search) |
| POST | `/translation-memory/import` | Import CSV |

## Manual Submission Flow

Submit lore drafts through the frontend form at
`http://localhost:3302/articles/manual/new` or via the API:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/articles/manual/new` | Returns form field schema |
| POST | `/articles/manual` | Submit article (JSON body) |
| GET | `/articles/{id}` | Article detail with linked jobs |
| GET | `/jobs` | List all jobs |
| GET | `/jobs/{id}` | Job detail with status and logs |

POST body for `/articles/manual`:

```json
{
  "title": "Optional title",
  "source_url": "https://...",
  "source_text": "Full article text (required)",
  "target_language": "zh-CN"
}
```

Returns the created article and job:

```json
{
  "article": { "id": 1, "source_title": "...", ... },
  "job": { "id": 1, "status": "queued", ... },
  "message": "Article created. Job #1 queued for translation."
}
```

Manual jobs are draft-oriented. They are queued for a later
translation phase; no translation or publishing is run automatically.

## Database

The default database URL is `sqlite:///./data/app.db`.

Run from the project root:

```
# Apply the initial schema migration
alembic upgrade head

# Create a future migration after changing ORM models
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

The schema includes tables for: articles, jobs, translations,
glossary entries, translation memory, tags, article/tag links,
publish records, and job logs.

## Quality Checks

Run from the project root:

```
pytest
ruff check .
black --check .
```

## Current Scope

Included:

- FastAPI REST API serving all endpoints as JSON
- ORM models for the MVP persistence layer
- Manual submission workflow (article + queued job)
- Glossary import, search, create, and update
- Translation memory import and search
- Job listing and detail (status, logs, linked article)
- Alembic configuration and initial migration
- Settings loaded from `.env`

Not included yet (upcoming phases 6–16):

- LLM provider integration (OpenAI, Gemini, DeepSeek)
- Translation, review, tagging, and publishing workflows
- Automated source polling and article ingestion
- Notification service (email)
- Wiki publishing integration
- Authentication or authorization
