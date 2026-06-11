from app.models.schemas import PredictionRequest
from app.services.analysis import generate_rich_analysis
from app.services.procedure_classifier import classify_procedure


def test_analysis_mentions_surgeon_profile():
    req = PredictionRequest(
        surgery_procedure="Laparoscopic Cholecystectomy",
        booked_minutes=90,
        complexity_level=3,
        session_index=1,
        experience_level="intermediate",
        target_count=5,
        tool_changes=1,
        fine_motor_ratio="medium",
        workspace_constraint="moderate",
        time_of_day="morning",
        surgery_type="laparoscopic",
        surgeon_name="Dr. Patel",
        surgeon_grade="ST5",
        procedure_count=45,
        risk_index=6,
        primary_procedure="Cholecystectomy",
        profile_skills=["laparoscopy"],
    )
    match = classify_procedure(req.surgery_procedure)
    analysis = generate_rich_analysis(req, match, 50.0, 60.0, 70.0, "amber", [])

    joined = " ".join([analysis["explanation_text"], *analysis["training_insights"]]).lower()
    assert "dr. patel" in joined
    assert "st5" in joined or "grade st5" in joined
    assert "45" in joined
    assert "risk index" in joined
