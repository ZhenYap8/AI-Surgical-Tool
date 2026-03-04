# Surgical Training Risk Assessment (MVP)

A production-style MVP to assess overrun risk in surgical simulation training sessions.

## Overview
This tool predicts the duration of surgical training tasks and assesses the risk of "booking overrun" using a probabilistic heuristic model (Layer 1) and generates explainable feedback (Layer 2).

**Note:** This is an analytics tool for training logistics. It is **not** a clinical medical device.

## Stack
- **Backend**: Python FastAPI
- **Frontend**: React + Vite

## Prerequisites
- Node.js (v18+)
- Python (v3.9+)

## Run Instructions

### 1. Backend
```bash
# In root directory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```
Server will run at: `http://localhost:8000`
Swagger docs available at: `http://localhost:8000/docs`

### 2. Frontend
```bash
# In /web directory
npm install
npm run dev
```
Open browser at: `http://localhost:5173`

## Example Payload (POST /predict_and_explain)
```json
{
  "task_type": "suturing",
  "booked_minutes": 30,
  "complexity_level": 4,
  "session_index": 5,
  "experience_level": "novice",
  "target_count": 6,
  "tool_changes": 3,
  "fine_motor_ratio": "high",
  "workspace_constraint": "tight",
  "time_of_day": "afternoon",
  "surgeon_level": "ST1-7",
  "procedure_count": 25,
  "overrun_freq": 0.1,
  "risk_index": 5
}
```

## Logic Overview
1. **P50/P80/P90**: Calculated via heuristics based on base task duration + multipliers.
   - **Surgeon Profile**: Adjusts efficiency based on grade (Consultant/Registrar/CT) and procedure volume.
   - **Risk Index**: Adjusts for speed vs. caution trade-offs (High index = slower but consistent).
   - **Environmental**: Complexity, distance, traffic, speed.
2. **Risk Color**: 
   - 🟢 Green: Booked >= P80
   - 🟠 Amber: P50 <= Booked < P80
   - 🔴 Red: Booked < P50
3. **Explanation**: Template-based generation mocking an LLM response.
