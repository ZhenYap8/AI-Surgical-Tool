from app.services.procedures import get_procedure_params


def test_exact_procedure_match():
    params = get_procedure_params("Suturing")
    assert params["base_minutes"] == 15
    assert params["multiplier"] == 1.0


def test_keyword_match_in_longer_name():
    params = get_procedure_params("Laparoscopic Cholecystectomy")
    assert params["base_minutes"] == 45
    assert params["multiplier"] == 1.2


def test_unknown_procedure_uses_default():
    params = get_procedure_params("Unknown Procedure XYZ")
    assert params["base_minutes"] == 40
    assert params["multiplier"] == 1.0
