from .models import PredictionRequest
from .procedures import get_procedure_params


def calculate_quantiles(req: PredictionRequest):
    proc_params = get_procedure_params(req.surgery_procedure)
    base = proc_params["base_minutes"]
    proc_mult = proc_params["multiplier"]

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

    else:  # red
        summary = "High Risk: Session overrun is statistically likely."
        bullets = [
            f"Median required time ({p50}m) exceeds booked slot ({booked}m).",
            "High probability of incomplete training objectives.",
            f"Critical factors: {top_factors_str}."
        ]
        action = "EXTEND BOOKING or SPLIT SESSION."

    return summary, bullets, action
