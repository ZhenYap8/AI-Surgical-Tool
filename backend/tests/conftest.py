import pytest

from app.models.schemas import PredictionRequest


@pytest.fixture
def sample_request() -> PredictionRequest:
    return PredictionRequest(
        surgery_procedure="Suturing",
        booked_minutes=30,
        complexity_level=3,
        session_index=1,
        experience_level="intermediate",
        target_count=5,
        tool_changes=1,
        fine_motor_ratio="medium",
        workspace_constraint="moderate",
        time_of_day="morning",
        surgery_type="laparoscopic",
    )
