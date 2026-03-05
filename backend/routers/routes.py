import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from models import PredictionRequest, PredictionResponse, ExplanationRequest, ExplanationResponse, FullResponse
from logic import calculate_quantiles, determine_risk, estimate_overrun_prob, generate_explanation_data

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
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


@router.post("/explain", response_model=ExplanationResponse)
def explain_endpoint(req: ExplanationRequest):
    summary, bullets, action = generate_explanation_data(
        req.booked_minutes, req.p50, req.p80, req.p90, req.risk_color, req.top_factors
    )
    return {
        "explanation_text": summary,
        "explanation_bullets": bullets,
        "recommended_action": action
    }


@router.post("/predict_and_explain", response_model=FullResponse)
def predict_and_explain_endpoint(req: PredictionRequest):
    p50, p80, p90, factors = calculate_quantiles(req)
    risk = determine_risk(req.booked_minutes, p50, p80)
    overrun = estimate_overrun_prob(req.booked_minutes, p50, p80, p90)
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