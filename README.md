# Surgical Training Risk Assessment (MVP)

A production-style MVP to assess overrun risk in surgical simulation training sessions.

## Overview

This tool predicts the duration of surgical training tasks and assesses the risk of "booking overrun" using a probabilistic heuristic model (Layer 1) and generates explainable feedback (Layer 2).

**Note:** This is an analytics tool for training logistics. It is **not** a clinical medical device.

## Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: React 18, Vite 7

## Project Structure

```
AI-Surgical-Tool/
├── backend/
│   ├── app/                  # FastAPI application package
│   │   ├── main.py           # App entry point
│   │   ├── routers/          # API routes
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Prediction logic
│   │   └── db/               # SQLModel (future use)
│   └── tests/                # pytest unit tests
├── frontend/
│   └── src/
│       ├── api/              # API configuration
│       └── App.jsx           # Main UI
├── docs/                     # Design specs and prompts
└── Makefile                  # Dev shortcuts
```

## Prerequisites

- **Node.js** 20.x
- **Python** 3.9+ (3.11 recommended)

## Quick Start

### Install dependencies

```bash
make install
```

Or manually:

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run locally

Start both services:

```bash
make dev
```

Or run separately in two terminals:

```bash
# Terminal 1 — API at http://localhost:8000
make backend

# Terminal 2 — UI at http://localhost:5173
make frontend
```

Swagger docs: `http://localhost:8000/docs`

### Environment variables

Copy the frontend example env file (optional — defaults work for local dev):

```bash
cp frontend/.env.example frontend/.env.local
```

## Tests

```bash
make test
```

Or run individually:

```bash
make test-backend    # pytest
make test-frontend   # vitest
```

## Example Payload (POST /predict_and_explain)

```json
{
  "surgery_procedure": "Suturing",
  "booked_minutes": 30,
  "complexity_level": 3,
  "session_index": 1,
  "experience_level": "intermediate",
  "target_count": 5,
  "tool_changes": 1,
  "fine_motor_ratio": "medium",
  "workspace_constraint": "moderate",
  "time_of_day": "morning",
  "surgery_type": "laparoscopic"
}
```

## Logic Overview

1. **P50/P80/P90**: Calculated via heuristics based on base procedure duration + multipliers (experience, complexity, fatigue, workspace constraints).
2. **Risk Color**:
   - Green: Booked >= P80
   - Amber: P50 <= Booked < P80
   - Red: Booked < P50
3. **Explanation**: Template-based generation providing actionable feedback.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/predict` | Quantiles + risk only |
| POST | `/explain` | Explanation from prior prediction |
| POST | `/predict_and_explain` | Combined (used by frontend) |
| GET | `/docs` | Swagger UI |

## Deploy to Vercel (frontend + backend)

This repo is configured for Vercel **Services** — one project deploys both the Vite frontend and FastAPI backend.

### Prerequisites

- [Vercel account](https://vercel.com) connected to GitHub
- Vercel CLI ≥ 48.1.8 (optional): `npm i -g vercel`

### Dashboard setup

1. **Import** `ZhenYap8/AI-Surgical-Tool` on Vercel.
2. Set **Framework Preset** to **Services** (Vercel reads root `vercel.json`).
3. Confirm both services are detected:
   - `frontend` → `/` (Vite)
   - `backend` → `/api` (FastAPI)
4. Add environment variable (Production + Preview):

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | `/api` |

5. Click **Deploy**.

### What’s configured in the repo

| File | Purpose |
|------|---------|
| `vercel.json` | `experimentalServices` routing for frontend + backend |
| `backend/vercel_app.py` | Vercel serverless entrypoint |
| `backend/pyproject.toml` | `[tool.vercel] entrypoint = "vercel_app:app"` |
| `frontend/.env.production` | `VITE_API_URL=/api` for same-origin API calls |

### Verify after deploy

```bash
curl https://<your-app>.vercel.app/api/
curl https://<your-app>.vercel.app/api/docs
```

Open the site, run an assessment, and confirm network requests hit `/api/predict_and_explain`.

### Local development (unchanged)

Backend and frontend still run separately locally — `VITE_API_URL` defaults to `http://localhost:8000` via `frontend/.env.local` or `.env.example`.

### Alternative: frontend-only on Vercel

To keep the API on Render instead, deploy only `frontend` (root directory `frontend`) and set:

```
VITE_API_URL=https://ai-surgical-tool.onrender.com
```
