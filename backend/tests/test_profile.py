from app.models.schemas import PredictionRequest
from app.services.logic import calculate_quantiles


def _base_request(**overrides):
    data = {
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
        "surgery_type": "open",
    }
    data.update(overrides)
    return PredictionRequest(**data)


def test_experienced_profile_reduces_duration():
    base_p50, _, _, _ = calculate_quantiles(_base_request())
    exp_p50, _, _, exp_factors = calculate_quantiles(
        _base_request(
            surgeon_name="Dr. Smith",
            surgeon_grade="ST7",
            procedure_count=150,
            risk_index=8,
            primary_procedure="Suturing",
            profile_skills=["suturing"],
        )
    )

    assert exp_p50 < base_p50
    assert any("Profile: Dr. Smith" in factor for factor in exp_factors)
    assert any("procedure volume" in factor.lower() for factor in exp_factors)


def test_low_volume_profile_increases_duration():
    base_p50, _, _, _ = calculate_quantiles(_base_request())
    nov_p50, _, _, nov_factors = calculate_quantiles(
        _base_request(
            surgeon_name="Dr. Jones",
            surgeon_grade="CT1",
            procedure_count=8,
            risk_index=2,
        )
    )

    assert nov_p50 > base_p50
    assert any("risk index" in factor.lower() for factor in nov_factors)
