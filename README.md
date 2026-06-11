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
