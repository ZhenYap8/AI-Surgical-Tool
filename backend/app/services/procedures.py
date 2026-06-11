from app.services.procedure_classifier import classify_procedure


def get_procedure_params(procedure_name: str) -> dict:
    match = classify_procedure(procedure_name)
    return {
        "base_minutes": match.base_minutes,
        "multiplier": match.multiplier,
        "matched_procedure": match.matched_procedure,
        "procedure_category": match.procedure_category,
        "match_confidence": match.match_confidence,
    }
