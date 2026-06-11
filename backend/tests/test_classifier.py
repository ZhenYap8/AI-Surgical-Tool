from app.services.procedure_classifier import classify_procedure


def test_exact_alias_match_high_confidence():
    match = classify_procedure("Laparoscopic Cholecystectomy")
    assert match.matched_procedure == "Cholecystectomy"
    assert match.procedure_category == "Hepatobiliary"
    assert match.match_confidence >= 0.7


def test_keyword_match_for_partial_input():
    match = classify_procedure("practice suturing on pad")
    assert match.matched_procedure == "Suturing"
    assert match.match_confidence > 0.35


def test_unknown_procedure_falls_back_to_default():
    match = classify_procedure("Completely Unknown Procedure XYZ")
    assert match.matched_procedure == "General Surgical Procedure"
    assert match.procedure_category == "Unclassified"
