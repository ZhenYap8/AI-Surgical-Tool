import re
from dataclasses import dataclass

from app.services.procedure_knowledge import PROCEDURE_KNOWLEDGE


@dataclass
class ProcedureMatch:
    procedure_id: str
    matched_procedure: str
    procedure_category: str
    match_confidence: float
    base_minutes: float
    multiplier: float


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def classify_procedure(raw_name: str) -> ProcedureMatch:
    """Score free-text procedure names using keyword overlap (lightweight ML-style matching)."""
    name = raw_name.strip().lower()
    tokens = _tokenize(name)

    best_id = "default"
    best_score = 0.0

    for procedure_id, knowledge in PROCEDURE_KNOWLEDGE.items():
        if procedure_id == "default":
            continue

        score = 0.0
        aliases = [procedure_id, *knowledge.get("aliases", [])]

        for alias in aliases:
            alias_lower = alias.lower()
            if name == alias_lower:
                score += 6.0
            elif alias_lower in name or name in alias_lower:
                score += 4.0

        keyword_tokens: set[str] = set()
        for keyword in knowledge.get("keywords", []):
            keyword_tokens.update(_tokenize(keyword))

        overlap = len(tokens & keyword_tokens)
        score += overlap * 1.75

        display_tokens = _tokenize(knowledge["display_name"])
        score += len(tokens & display_tokens) * 1.25

        if score > best_score:
            best_score = score
            best_id = procedure_id

    knowledge = PROCEDURE_KNOWLEDGE[best_id]
    confidence = 0.35 if best_id == "default" else min(best_score / 7.0, 0.99)

    return ProcedureMatch(
        procedure_id=best_id,
        matched_procedure=knowledge["display_name"],
        procedure_category=knowledge["category"],
        match_confidence=round(confidence, 2),
        base_minutes=knowledge["base_minutes"],
        multiplier=knowledge["multiplier"],
    )
