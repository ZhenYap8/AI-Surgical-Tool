from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CORS Middleware to allow requests from React frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Procedure Lookup Table ---

PROCEDURE_LOOKUP = {
    "cholecystectomy":   {"base_minutes": 45, "multiplier": 1.2},
    "appendectomy":      {"base_minutes": 35, "multiplier": 1.0},
    "hernia repair":     {"base_minutes": 50, "multiplier": 1.1},
    "prostatectomy":     {"base_minutes": 120, "multiplier": 1.4},
    "colectomy":         {"base_minutes": 90, "multiplier": 1.35},
    "bowel resection":   {"base_minutes": 95, "multiplier": 1.35},
    "nephrectomy":       {"base_minutes": 80, "multiplier": 1.3},
    "thyroidectomy":     {"base_minutes": 60, "multiplier": 1.15},
    "suturing":          {"base_minutes": 15, "multiplier": 1.0},
    "knot tying":        {"base_minutes": 12, "multiplier": 0.9},
    "peg transfer":      {"base_minutes": 10, "multiplier": 0.85},
    "cutting":           {"base_minutes": 8,  "multiplier": 0.9},
    "default":           {"base_minutes": 40, "multiplier": 1.0},
}

def get_procedure_params(procedure_name: str) -> dict:
    name = procedure_name.lower()
    for keyword, params in PROCEDURE_LOOKUP.items():
        if keyword in name:
            return params
    return PROCEDURE_LOOKUP["default"]

# --- Pydantic Models ---

class PredictionRequest(BaseModel):
    surgery_procedure: str  # Free-text, e.g. "Laparoscopic Cholecystectomy"
    booked_minutes: int
    complexity_level: int  # 1-5
    session_index: int  # fatigue proxy
    experience_level: str  # novice, intermediate, advanced
    target_count: int  # number of reps/targets
    tool_changes: int
    fine_motor_ratio: str  # low, medium, high
    workspace_constraint: str  # open, moderate, tight
    time_of_day: str
    surgery_type: str  # open, laparoscopic, robotic

class PredictionResponse(BaseModel):
    p50_minutes: float
    p80_minutes: float
    p90_minutes: float
    risk_color: str
    recommended_booking_minutes: float
    overrun_probability_est: float
    top_factors: List[str]

class ExplanationRequest(BaseModel):
    booked_minutes: int
    p50: float
    p80: float
    p90: float
    risk_color: str
    top_factors: List[str]

class ExplanationResponse(BaseModel):
    explanation_text: str
    explanation_bullets: List[str]
    recommended_action: str

# Combined response model for the single-call endpoint
class FullResponse(PredictionResponse, ExplanationResponse):
    pass


# --- Business Logic ---

def calculate_quantiles(req: PredictionRequest):
    # Resolve procedure → base_minutes + procedure_multiplier
    proc_params = get_procedure_params(req.surgery_procedure)
    base = proc_params["base_minutes"]
    proc_mult = proc_params["multiplier"]

    # Surgery type multiplier
    surgery_type_mult = 1.0
    if req.surgery_type.lower() == "laparoscopic":
        surgery_type_mult = 1.15
    elif req.surgery_type.lower() == "robotic":
        surgery_type_mult = 1.25

    factors = []
    factors.append(f"Procedure: {req.surgery_procedure}")

    if req.surgery_type.lower() in ("laparoscopic", "robotic"):
        factors.append(f"{req.surgery_type.capitalize()} approach")

    # 1. Experience Level (Major Factor)
    exp_mult = 1.0
    if req.experience_level.lower() == "novice":
        exp_mult = 1.6
        factors.append("Novice trainee (learning curve)")
    elif req.experience_level.lower() == "advanced":
        exp_mult = 0.7
        factors.append("Advanced trainee pace")

    # 2. Complexity & targets
    target_scale = 1.0 + (req.target_count - 5) * 0.05
    if req.target_count > 8:
        factors.append(f"High repetition count ({req.target_count})")

    complexity_mult = 1.0 + (req.complexity_level - 1) * 0.1
    if req.complexity_level >= 4:
        factors.append(f"High procedure complexity (Lv {req.complexity_level})")

    # 3. Environmental/Physical constraints
    constraint_mult = 1.0
    if req.workspace_constraint.lower() == "tight":
        constraint_mult = 1.25
        factors.append("Restricted workspace geometry")

    # 4. Fatigue (Session Index)
    fatigue_mult = 1.0
    if req.session_index > 3:
        fatigue_mult += (req.session_index * 0.05)
        factors.append(f"Fatigue risk (Session #{req.session_index})")

    # 5. Time of Day Adjustments
    if req.time_of_day.lower() == "evening":
        fatigue_mult += 0.1
        factors.append("Evening session (circadian fatigue)")

    # 6. Tool overhead
    tool_time = req.tool_changes * 1.5
    if req.tool_changes > 2:
        factors.append(f"Frequent tool changes ({req.tool_changes})")

    # Calculate P50
    p50 = (
        base
        * proc_mult
        * surgery_type_mult
        * exp_mult
        * complexity_mult
        * target_scale
        * constraint_mult
        * fatigue_mult
    ) + tool_time

    # Derive P80/P90
    uncertainty_base = 1.2
    if req.experience_level.lower() == "novice":
        uncertainty_base = 1.4
    elif req.experience_level.lower() == "advanced":
        uncertainty_base = 1.1

    if req.fine_motor_ratio.lower() == "high":
        uncertainty_base += 0.1
        factors.append("High fine-motor demand increases variance")

    p80 = p50 * uncertainty_base
    p90 = p50 * (uncertainty_base + 0.2)

    return round(p50, 1), round(p80, 1), round(p90, 1), factors

def determine_risk(booked, p50, p80):
    # 🟢 Green if p80_minutes <= booked_minutes
    if p80 <= booked:
        return "green"
    # 🟠 Amber if p50_minutes <= booked_minutes < p80_minutes
    elif p50 <= booked < p80:
        return "amber"
    # 🔴 Red if booked_minutes < p50_minutes
    else: 
        return "red"

def estimate_overrun_prob(booked, p50, p80, p90):
    # Piecewise interpolation logic
    if booked >= p90:
        return 0.05
    elif booked >= p80:
        # Interpolate between p80 (20% risk) and p90 (10% risk) -> roughly 15%
        return 0.15
    elif booked >= p50:
        # Interpolate between p50 (50% risk) and p80 (20% risk) -> roughly 35%
        return 0.35
    else:
        # Very high risk
        return 0.85

def generate_explanation_data(booked, p50, p80, p90, risk, factors):
    top_factors_str = ", ".join(factors) if factors else "Standard training parameters"
    
    if risk == "green":
        summary = "Schedule is optimal: Booked duration accommodates P80 estimate."
        bullets = [
            f"Estimated median time is {p50} min; booked time is {booked} min.",
            "Sufficient buffer for trainee learning curve and resets.",
            f"Key inputs: {top_factors_str}."
        ]
        action = "Confirm training slot."
        
    elif risk == "amber":
        summary = "Moderate pressure: Trainee may feel rushed if errors occur."
        bullets = [
            f"Booked time ({booked}m) is below P80 ({p80}m) confidence level.",
            "Buffer is minimal for handling tool difficulties or fatigue.",
            f"Driven by: {top_factors_str}."
        ]
        action = "Add 10 mins buffer or reduce target count."
        
    else: # red
        summary = "High Risk: Session overrun is statistically likely."
        bullets = [
            f"Median required time ({p50}m) exceeds booked slot ({booked}m).",
            "High probability of incomplete training objectives.",
            f"Critical factors: {top_factors_str}."
        ]
        action = "EXTEND BOOKING or SPLIT SESSION."

    return summary, bullets, action

# --- Endpoints ---

@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(req: PredictionRequest):
    p50, p80, p90, factors = calculate_quantiles(req)
    risk = determine_risk(req.booked_minutes, p50, p80)
    overrun = estimate_overrun_prob(req.booked_minutes, p50, p80, p90)
    
    return {
        "p50_minutes": p50,
        "p80_minutes": p80,
        "p90_minutes": p90,
        "risk_color": risk,
        "recommended_booking_minutes": p80,
        "overrun_probability_est": overrun,
        "top_factors": factors
    }

@app.post("/explain", response_model=ExplanationResponse)
def explain_endpoint(req: ExplanationRequest):
    summary, bullets, action = generate_explanation_data(
        req.booked_minutes, req.p50, req.p80, req.p90, req.risk_color, req.top_factors
    )
    return {
        "explanation_text": summary,
        "explanation_bullets": bullets,
        "recommended_action": action
    }

@app.post("/predict_and_explain", response_model=FullResponse)
def predict_and_explain_endpoint(req: PredictionRequest):
    # 1. Predict
    p50, p80, p90, factors = calculate_quantiles(req)
    risk = determine_risk(req.booked_minutes, p50, p80)
    overrun = estimate_overrun_prob(req.booked_minutes, p50, p80, p90)
    
    # 2. Explain
    summary, bullets, action = generate_explanation_data(
        req.booked_minutes, p50, p80, p90, risk, factors
    )
    
    return {
        "p50_minutes": p50,
        "p80_minutes": p80,
        "p90_minutes": p90,
        "risk_color": risk,
        "recommended_booking_minutes": p80,
        "overrun_probability_est": overrun,
        "top_factors": factors,
        "explanation_text": summary,
        "explanation_bullets": bullets,
        "recommended_action": action
    }
