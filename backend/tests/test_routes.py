from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint(sample_request):
    response = client.post("/predict", json=sample_request.model_dump())
    assert response.status_code == 200

    data = response.json()
    assert data["p50_minutes"] < data["p80_minutes"] < data["p90_minutes"]
    assert data["risk_color"] in ("green", "amber", "red")
    assert 0 <= data["overrun_probability_est"] <= 1
    assert isinstance(data["top_factors"], list)


def test_predict_and_explain_endpoint(sample_request):
    response = client.post("/predict_and_explain", json=sample_request.model_dump())
    assert response.status_code == 200

    data = response.json()
    assert data["explanation_text"]
    assert len(data["explanation_bullets"]) >= 3
    assert data["recommended_action"]
    assert data["matched_procedure"]
    assert data["procedure_category"]
    assert 0 <= data["match_confidence"] <= 1
    assert len(data["risk_hazards"]) >= 2
    assert len(data["training_insights"]) >= 3


def test_explain_endpoint():
    payload = {
        "booked_minutes": 30,
        "p50": 25.0,
        "p80": 30.0,
        "p90": 35.0,
        "risk_color": "amber",
        "top_factors": ["Procedure: Suturing"],
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["explanation_text"]
    assert data["recommended_action"]
