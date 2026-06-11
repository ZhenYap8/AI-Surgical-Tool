from typing import List, Optional

from pydantic import BaseModel, Field


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
    # Optional surgeon profile context (from frontend localStorage profile)
    surgeon_name: Optional[str] = None
    surgeon_grade: Optional[str] = None
    procedure_count: Optional[int] = None
    risk_index: Optional[int] = Field(default=None, ge=1, le=10)
    primary_procedure: Optional[str] = None
    profile_skills: List[str] = Field(default_factory=list)


class PredictionResponse(BaseModel):
    p50_minutes: float
    p80_minutes: float
    p90_minutes: float
    risk_color: str
    recommended_booking_minutes: float
    overrun_probability_est: float
    top_factors: List[str]
    matched_procedure: str
    procedure_category: str
    match_confidence: float


class ExplanationRequest(BaseModel):
    booked_minutes: int
    p50: float
    p80: float
    p90: float
    risk_color: str
    top_factors: List[str]
    surgery_procedure: str = "General procedure"
    complexity_level: int = 3
    session_index: int = 1
    experience_level: str = "intermediate"
    target_count: int = 5
    tool_changes: int = 1
    fine_motor_ratio: str = "medium"
    workspace_constraint: str = "moderate"
    time_of_day: str = "morning"
    surgery_type: str = "open"
    surgeon_name: Optional[str] = None
    surgeon_grade: Optional[str] = None
    procedure_count: Optional[int] = None
    risk_index: Optional[int] = Field(default=None, ge=1, le=10)
    primary_procedure: Optional[str] = None
    profile_skills: List[str] = Field(default_factory=list)


class ExplanationResponse(BaseModel):
    explanation_text: str
    explanation_bullets: List[str]
    recommended_action: str
    matched_procedure: str
    procedure_category: str
    match_confidence: float
    risk_hazards: List[str]
    training_insights: List[str]


class FullResponse(PredictionResponse, ExplanationResponse):
    pass
