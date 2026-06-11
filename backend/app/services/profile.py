from app.models.schemas import PredictionRequest
from app.services.procedure_classifier import ProcedureMatch


def has_profile(req: PredictionRequest) -> bool:
    return bool(req.surgeon_name or req.surgeon_grade or req.procedure_count is not None)


def apply_profile_to_duration(
    req: PredictionRequest,
    match: ProcedureMatch,
    p50: float,
    uncertainty_base: float,
    factors: list[str],
) -> tuple[float, float]:
    """Adjust duration estimates using surgeon profile when provided."""
    if req.procedure_count is not None:
        count = req.procedure_count
        if count < 20:
            p50 *= 1.12
            factors.append(f"Low procedure volume ({count} cases)")
        elif count >= 100:
            p50 *= 0.88
            factors.append(f"High procedure volume ({count} cases)")
        elif count >= 50:
            p50 *= 0.94
            factors.append(f"Established case volume ({count} procedures)")

    if req.risk_index is not None:
        ri = req.risk_index
        if ri <= 3:
            p50 *= 0.96
            uncertainty_base += 0.06
            factors.append(f"Low risk index ({ri}/10) — faster but less consistent")
        elif ri >= 8:
            p50 *= 1.1
            uncertainty_base = max(uncertainty_base - 0.04, 1.05)
            factors.append(f"High risk index ({ri}/10) — cautious, steadier pace")
        elif ri >= 6:
            p50 *= 1.04
            factors.append(f"Moderate-high risk index ({ri}/10)")

    if req.primary_procedure and req.primary_procedure.strip():
        primary = req.primary_procedure.lower()
        if match.procedure_id in primary or primary in match.matched_procedure.lower():
            p50 *= 0.93
            factors.append("Primary procedure familiarity")

    if req.profile_skills:
        procedure_tokens = set(match.matched_procedure.lower().split())
        matched_skills = [
            skill
            for skill in req.profile_skills
            if any(token in skill.lower() or skill.lower() in token for token in procedure_tokens)
            or skill.lower() in req.surgery_procedure.lower()
        ]
        if matched_skills:
            p50 *= max(0.9, 1 - 0.02 * len(matched_skills[:2]))
            factors.append(f"Relevant skills: {', '.join(matched_skills[:2])}")

    if req.surgeon_grade:
        factors.append(f"Surgeon grade: {req.surgeon_grade}")

    if req.surgeon_name:
        factors.append(f"Profile: {req.surgeon_name}")

    return p50, uncertainty_base
