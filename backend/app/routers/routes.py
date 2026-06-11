from fastapi import APIRouter

from app.models.schemas import (
    ExplanationRequest,
    ExplanationResponse,
    FullResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.services.logic import (
    calculate_quantiles,
    determine_risk,
    estimate_overrun_prob,
    generate_explanation_data,
)
from app.services.procedure_classifier import classify_procedure

router = APIRouter()


def _build_prediction_payload(req: PredictionRequest, p50, p80, p90, factors, risk, overrun):
    match = classify_procedure(req.surgery_procedure)
    return {
        "p50_minutes": p50,
        "p80_minutes": p80,
        "p90_minutes": p90,
        "risk_color": risk,
        "recommended_booking_minutes": p80,
        "overrun_probability_est": overrun,
        "top_factors": factors,
        "matched_procedure": match.matched_procedure,
        "procedure_category": match.procedure_category,
        "match_confidence": match.match_confidence,
    }


@router.post("/predict", response_model=PredictionResponse)
def predict_endpoint(req: PredictionRequest):
    p50, p80, p90, factors = calculate_quantiles(req)
    risk = determine_risk(req.booked_minutes, p50, p80)
    overrun = estimate_overrun_prob(req.booked_minutes, p50, p80, p90)
    return _build_prediction_payload(req, p50, p80, p90, factors, risk, overrun)


@router.post("/explain", response_model=ExplanationResponse)
def explain_endpoint(req: ExplanationRequest):
    prediction_req = PredictionRequest(
        surgery_procedure=req.surgery_procedure,
        booked_minutes=req.booked_minutes,
        complexity_level=req.complexity_level,
        session_index=req.session_index,
        experience_level=req.experience_level,
        target_count=req.target_count,
        tool_changes=req.tool_changes,
        fine_motor_ratio=req.fine_motor_ratio,
        workspace_constraint=req.workspace_constraint,
        time_of_day=req.time_of_day,
        surgery_type=req.surgery_type,
        surgeon_name=req.surgeon_name,
        surgeon_grade=req.surgeon_grade,
        procedure_count=req.procedure_count,
        risk_index=req.risk_index,
        primary_procedure=req.primary_procedure,
        profile_skills=req.profile_skills,
    )
    analysis = generate_explanation_data(
        prediction_req,
        req.p50,
        req.p80,
        req.p90,
        req.risk_color,
        req.top_factors,
    )
    return analysis


@router.post("/predict_and_explain", response_model=FullResponse)
def predict_and_explain_endpoint(req: PredictionRequest):
    p50, p80, p90, factors = calculate_quantiles(req)
    risk = determine_risk(req.booked_minutes, p50, p80)
    overrun = estimate_overrun_prob(req.booked_minutes, p50, p80, p90)
    analysis = generate_explanation_data(req, p50, p80, p90, risk, factors)

    return {
        **_build_prediction_payload(req, p50, p80, p90, factors, risk, overrun),
        **analysis,
    }
