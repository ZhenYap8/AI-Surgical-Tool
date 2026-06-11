from app.models.schemas import PredictionRequest
from app.services.analysis import generate_rich_analysis
from app.services.procedure_classifier import classify_procedure


def _request(**overrides):
    base = {
        "surgery_procedure": "Laparoscopic Cholecystectomy",
        "booked_minutes": 300,
        "complexity_level": 3,
        "session_index": 1,
        "experience_level": "advanced",
        "target_count": 5,
        "tool_changes": 1,
        "fine_motor_ratio": "medium",
        "workspace_constraint": "moderate",
        "time_of_day": "morning",
        "surgery_type": "laparoscopic",
    }
    base.update(overrides)
    return PredictionRequest(**base)


def test_generous_booking_produces_contextual_narrative():
    req = _request(booked_minutes=300)
    match = classify_procedure(req.surgery_procedure)
    analysis = generate_rich_analysis(req, match, 53.7, 59.1, 64.5, "green", [])

    joined = " ".join([analysis["explanation_text"], *analysis["explanation_bullets"]]).lower()
    assert "cholecystectomy" in joined
    assert "template" not in joined
    assert "key inputs" not in joined
    assert any(token in joined for token in ("×", "multiple", "reps", "headroom", "margin", "spare"))


def test_tight_booking_produces_pressure_language():
    req = _request(booked_minutes=40)
    match = classify_procedure(req.surgery_procedure)
    analysis = generate_rich_analysis(req, match, 53.7, 59.1, 64.5, "red", [])

    joined = " ".join([analysis["explanation_text"], *analysis["explanation_bullets"]]).lower()
    assert any(word in joined for word in ("under-booked", "exceeds", "extend", "truncated", "pressure"))
