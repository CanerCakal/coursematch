# CourseMatch

A cross-university course equivalency and curriculum comparison system. It answers the question every transfer and exchange student asks — *"will this course count?"* — by comparing course content across universities and producing a similarity score.

## How It Works

The comparison engine is currently **rule-based**: course titles and descriptions are normalized (Turkish/English stop-word removal), domain terms are mapped to shared keys across both languages (`programlama` ↔ `programming`, `algoritma` ↔ `algorithm`, and so on), and a similarity score is computed from the overlapping keywords. This is a deliberate first step — deterministic, explainable and cheap to run. Semantic, embedding-based comparison is on the roadmap (below).

## Features

- Cascading selection flow: university → department → course
- Similarity score and recommendation presentation between two courses
- **Comparison history** — past comparisons are persisted with their university context and can be revisited
- Filtering + pagination on course and department listings
- Auto-generated API documentation (FastAPI / OpenAPI)

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React + Vite + TypeScript |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + Alembic migrations |
| Environment | Docker Compose |

## Architecture

```
backend/app/
├── api/routes/     # universities, departments, courses endpoints
├── models/         # SQLAlchemy models (incl. comparison history)
├── schemas/        # Pydantic schemas
├── services/       # course_similarity — the comparison engine
└── db/             # connection + table init on startup

frontend/src/       # single-page flow: select → compare → history
```

Development follows a `develop`-branch PR workflow — the commit history reads as feature-based merges.

## Running Locally

```bash
git clone https://github.com/CanerCakal/coursematch.git
cd coursematch
docker compose up
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Roadmap

- [ ] Add semantic similarity (sentence embeddings) alongside the rule-based engine and compare the two approaches
- [ ] Bulk course import (CSV / curriculum page parsing)
- [ ] Classify results by score thresholds: equivalent / partially equivalent / not equivalent

## Status

In active development. The core flow — adding courses, listing, comparing, history — is working.
