from pydantic import BaseModel
from typing import List


class PredictionRequest(BaseModel):
    surgery_procedure: str
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


class FullResponse(PredictionResponse, ExplanationResponse):
    pass
