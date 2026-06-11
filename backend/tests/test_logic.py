from app.models.schemas import PredictionRequest
from app.services.logic import (
    calculate_quantiles,
    determine_risk,
    estimate_overrun_prob,
    generate_explanation_data,
)


def test_calculate_quantiles_returns_ordered_percentiles(sample_request):
    p50, p80, p90, factors = calculate_quantiles(sample_request)

    assert p50 < p80 < p90
    assert isinstance(factors, list)
    assert len(factors) >= 1
    assert any("Suturing" in factor for factor in factors)


def test_novice_increases_duration():
    novice = PredictionRequest(
        surgery_procedure="Suturing",
        booked_minutes=30,
        complexity_level=3,
        session_index=1,
        experience_level="novice",
        target_count=5,
        tool_changes=1,
        fine_motor_ratio="medium",
        workspace_constraint="moderate",
        time_of_day="morning",
        surgery_type="open",
    )
    advanced = novice.model_copy(update={"experience_level": "advanced"})

    novice_p50, _, _, _ = calculate_quantiles(novice)
    advanced_p50, _, _, _ = calculate_quantiles(advanced)

    assert novice_p50 > advanced_p50


def test_determine_risk_colors():
    assert determine_risk(100, 50, 80) == "green"
    assert determine_risk(60, 50, 80) == "amber"
    assert determine_risk(40, 50, 80) == "red"


def test_estimate_overrun_prob_buckets():
    assert estimate_overrun_prob(100, 50, 80, 90) == 0.05
    assert estimate_overrun_prob(85, 50, 80, 90) == 0.15
    assert estimate_overrun_prob(60, 50, 80, 90) == 0.35
    assert estimate_overrun_prob(40, 50, 80, 90) == 0.85


def test_generate_explanation_data_for_each_risk(sample_request):
    for risk in ("green", "amber", "red"):
        analysis = generate_explanation_data(
            sample_request, 25.0, 30.0, 35.0, risk, ["Procedure: Suturing"]
        )
        assert analysis["explanation_text"]
        assert len(analysis["explanation_bullets"]) >= 3
        assert analysis["recommended_action"]
        assert analysis["matched_procedure"]
        assert len(analysis["risk_hazards"]) >= 2
        assert len(analysis["training_insights"]) >= 3
