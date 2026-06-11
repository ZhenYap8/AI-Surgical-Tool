from app.models.schemas import PredictionRequest
from app.services.analysis import generate_rich_analysis
from app.services.procedure_classifier import classify_procedure
from app.services.profile import apply_profile_to_duration
from app.services.procedures import get_procedure_params


def calculate_quantiles(req: PredictionRequest):
    match = classify_procedure(req.surgery_procedure)
    proc_params = get_procedure_params(req.surgery_procedure)
    base = proc_params["base_minutes"]
    proc_mult = proc_params["multiplier"]

    surgery_type_mult = 1.0
    if req.surgery_type.lower() == "laparoscopic":
        surgery_type_mult = 1.15
    elif req.surgery_type.lower() == "robotic":
        surgery_type_mult = 1.25

    factors = []
    factors.append(
        f"Procedure: {match.matched_procedure} ({int(match.match_confidence * 100)}% match)"
    )
    factors.append(f"Category: {match.procedure_category}")

    if req.surgery_type.lower() in ("laparoscopic", "robotic"):
        factors.append(f"{req.surgery_type.capitalize()} approach")

    exp_mult = 1.0
    if req.experience_level.lower() == "novice":
        exp_mult = 1.6
        factors.append("Novice trainee (learning curve)")
    elif req.experience_level.lower() == "advanced":
        exp_mult = 0.7
        factors.append("Advanced trainee pace")

    target_scale = 1.0 + (req.target_count - 5) * 0.05
    if req.target_count > 8:
        factors.append(f"High repetition count ({req.target_count})")

    complexity_mult = 1.0 + (req.complexity_level - 1) * 0.1
    if req.complexity_level >= 4:
        factors.append(f"High procedure complexity (Lv {req.complexity_level})")

    constraint_mult = 1.0
    if req.workspace_constraint.lower() == "tight":
        constraint_mult = 1.25
        factors.append("Restricted workspace geometry")

    fatigue_mult = 1.0
    if req.session_index > 3:
        fatigue_mult += req.session_index * 0.05
        factors.append(f"Fatigue risk (Session #{req.session_index})")

    if req.time_of_day.lower() == "evening":
        fatigue_mult += 0.1
        factors.append("Evening session (circadian fatigue)")

    tool_time = req.tool_changes * 1.5
    if req.tool_changes > 2:
        factors.append(f"Frequent tool changes ({req.tool_changes})")

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

    uncertainty_base = 1.2
    if req.experience_level.lower() == "novice":
        uncertainty_base = 1.4
    elif req.experience_level.lower() == "advanced":
        uncertainty_base = 1.1

    if req.fine_motor_ratio.lower() == "high":
        uncertainty_base += 0.1
        factors.append("High fine-motor demand increases variance")

    p50, uncertainty_base = apply_profile_to_duration(req, match, p50, uncertainty_base, factors)

    p80 = p50 * uncertainty_base
    p90 = p50 * (uncertainty_base + 0.2)

    return round(p50, 1), round(p80, 1), round(p90, 1), factors


def determine_risk(booked, p50, p80):
    if p80 <= booked:
        return "green"
    elif p50 <= booked < p80:
        return "amber"
    else:
        return "red"


def estimate_overrun_prob(booked, p50, p80, p90):
    if booked >= p90:
        return 0.05
    elif booked >= p80:
        return 0.15
    elif booked >= p50:
        return 0.35
    else:
        return 0.85


def generate_explanation_data(req: PredictionRequest, p50, p80, p90, risk, factors):
    match = classify_procedure(req.surgery_procedure)
    return generate_rich_analysis(req, match, p50, p80, p90, risk, factors)
