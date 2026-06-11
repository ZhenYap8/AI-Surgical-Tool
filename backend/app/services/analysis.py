import hashlib
from typing import List

from app.models.schemas import PredictionRequest
from app.services.procedure_classifier import ProcedureMatch
from app.services.procedure_knowledge import PROCEDURE_KNOWLEDGE
from app.services.profile import has_profile


def _seed(*parts) -> int:
    digest = hashlib.md5("|".join(str(part) for part in parts).encode(), usedforsecurity=False)
    return int(digest.hexdigest(), 16)


def _pick(options: List[str], seed: int) -> str:
    return options[seed % len(options)]


def _pick_many(options: List[str], seed: int, count: int) -> List[str]:
    if not options:
        return []
    chosen = []
    for offset in range(count):
        candidate = options[(seed + offset * 7) % len(options)]
        if candidate not in chosen:
            chosen.append(candidate)
    idx = 0
    while len(chosen) < count and idx < len(options):
        candidate = options[(seed + idx) % len(options)]
        if candidate not in chosen:
            chosen.append(candidate)
        idx += 1
    return chosen[:count]


def _timing_context(req: PredictionRequest, p50: float, p80: float, p90: float) -> dict:
    booked = req.booked_minutes
    buffer_after_p80 = round(booked - p80, 1)
    buffer_after_p50 = round(booked - p50, 1)
    shortfall = round(p50 - booked, 1)
    ratio = round(booked / p50, 1) if p50 else 0

    if booked >= p90:
        slack = "generous"
    elif booked >= p80:
        slack = "comfortable"
    elif booked >= p50:
        slack = "tight"
    else:
        slack = "insufficient"

    return {
        "booked": booked,
        "p50": p50,
        "p80": p80,
        "p90": p90,
        "buffer_after_p80": buffer_after_p80,
        "buffer_after_p50": buffer_after_p50,
        "shortfall": shortfall,
        "ratio": ratio,
        "slack": slack,
    }


def _contextual_risks(req: PredictionRequest) -> List[str]:
    risks = []

    if req.procedure_count is not None and req.procedure_count < 20:
        risks.append(f"Limited case exposure ({req.procedure_count} procedures) may slow decisive step transitions")
    if req.risk_index is not None and req.risk_index >= 8:
        risks.append(f"High risk index ({req.risk_index}/10) suggests deliberate pace — schedule should allow methodical checks")
    elif req.risk_index is not None and req.risk_index <= 3:
        risks.append(f"Low risk index ({req.risk_index}/10) may trade consistency for speed under pressure")

    if req.experience_level.lower() == "novice":
        risks.append("Learning-curve stalls often appear mid-case when steps are unfamiliar")
    if req.complexity_level >= 4:
        risks.append(f"Complexity level {req.complexity_level}/5 increases recovery time after technical errors")
    if req.session_index > 3:
        risks.append(f"Later session order (#{req.session_index}) can slow instrument handling and decision pace")
    if req.time_of_day.lower() == "evening":
        risks.append("Evening sessions tend to show slower fine-motor consistency in simulation data")
    if req.workspace_constraint.lower() == "tight":
        risks.append("Cramped workspace can trigger repeated repositioning and port clashes")
    if req.tool_changes > 2:
        risks.append(f"{req.tool_changes} tool changes introduce handoff friction across the case")
    if req.fine_motor_ratio.lower() == "high":
        risks.append("High fine-motor demand makes small errors more costly in total duration")
    if req.target_count > 8:
        risks.append(f"Target of {req.target_count} reps magnifies minor per-rep delays")

    return risks


def _contextual_hazards(req: PredictionRequest) -> List[str]:
    hazards = []

    if req.surgery_type.lower() == "laparoscopic":
        hazards.append("Long laparoscopic instruments amplify tremor and reduce tactile feedback")
    elif req.surgery_type.lower() == "robotic":
        hazards.append("Bed-to-console coordination gaps can pause critical dissection phases")

    if req.workspace_constraint.lower() == "tight":
        hazards.append("Limited port spacing increases instrument collision during suturing or clipping")

    if req.experience_level.lower() == "novice":
        hazards.append("Supervisor intervention points should be agreed before the clock starts")

    return hazards


def _profile_label(req: PredictionRequest) -> str:
    if req.surgeon_name and req.surgeon_grade:
        return f"{req.surgeon_name} ({req.surgeon_grade})"
    if req.surgeon_name:
        return req.surgeon_name
    if req.surgeon_grade:
        return req.surgeon_grade
    return ""


def _build_summary(req: PredictionRequest, match: ProcedureMatch, ctx: dict, risk: str, seed: int) -> str:
    proc = match.matched_procedure
    approach = req.surgery_type
    exp = req.experience_level
    profile = _profile_label(req)
    who = f"For {profile}, " if profile else "For this trainee, "

    if risk == "green":
        options = [
            (
                f"For {proc} ({approach}), the slot looks {ctx['slack']}: "
                f"median pace is ~{ctx['p50']} min while {ctx['booked']} min is booked."
            ),
            (
                f"This {exp} trainee session on {proc} has meaningful headroom — "
                f"roughly {ctx['buffer_after_p80']} min remains even at P80 pace."
            ),
            (
                f"{who}scheduling looks appropriate for {proc}; unlikely overrun unless "
                f"unplanned teaching stops or equipment faults occur."
            ),
        ]
        if has_profile(req) and req.procedure_count is not None:
            options.append(
                f"{who}{proc} timing reflects {req.procedure_count} prior procedures and "
                f"risk index {req.risk_index or 'n/a'}/10."
            )
    elif risk == "amber":
        options = [
            (
                f"{who}{proc} under {approach} access is borderline: booked {ctx['booked']} min "
                f"covers median ({ctx['p50']} min) but not the P80 case ({ctx['p80']} min)."
            ),
            (
                f"Trainee may complete core objectives, but {proc} timing leaves little room "
                f"for coaching pauses or repeated critical steps."
            ),
            (
                f"Session is serviceable yet fragile — one prolonged {proc} step could consume "
                f"the remaining {ctx['buffer_after_p50']} min buffer."
            ),
        ]
    else:
        options = [
            (
                f"{proc} is under-booked by about {ctx['shortfall']} min versus median need; "
                f"objectives may be truncated before safe closure."
            ),
            (
                f"At current pace assumptions, this {exp} {proc} case likely outruns the slot "
                f"before P80 confidence is reached."
            ),
            (
                f"High schedule stress: even efficient execution of {proc} struggles to fit "
                f"{ctx['booked']} min when P80 is {ctx['p80']} min."
            ),
        ]

    return _pick(options, seed)


def _build_timing_narrative(
    req: PredictionRequest,
    match: ProcedureMatch,
    ctx: dict,
    risk: str,
    seed: int,
) -> List[str]:
    proc = match.matched_procedure
    c = ctx

    if risk == "green":
        if c["ratio"] >= 2.5:
            lead = (
                f"Booked time is ~{c['ratio']}× the median — suitable for multiple {proc} reps, "
                "structured debrief, or complication drills."
            )
            pool = [
                f"At ~{c['p50']} min median, this {c['booked']} min slot could support several full runs before time pressure appears.",
                f"P90 ({c['p90']} min) still sits well inside the booking; outlier delays are unlikely to breach the slot.",
                f"Roughly {c['buffer_after_p80']} min remains even if the trainee runs at P80 pace throughout.",
                _pick(PROCEDURE_KNOWLEDGE[match.procedure_id]["insights"], seed),
            ]
            return [lead, *_pick_many(pool, seed, 2)]
        pool = [
            f"Median completion around {c['p50']} min leaves ~{c['buffer_after_p80']} min after a realistic P80 run.",
            f"Current booking should absorb routine resets during {proc} without compressing teaching time.",
            f"Tail-risk estimate (P90 {c['p90']} min) remains inside the {c['booked']} min allocation.",
            f"For an {req.experience_level} trainee, this margin supports one unplanned redo of a difficult step.",
        ]
    elif risk == "amber":
        pool = [
            f"Median {c['p50']} min is covered, but a typical slower run ({c['p80']} min) would leave only {c['buffer_after_p80']} min spare.",
            f"If {proc} dissection slows (common with {req.tool_changes} tool changes), overrun risk rises quickly.",
            f"P90 at {c['p90']} min exceeds comfortable slack — facilitator should pre-agree stop/go checkpoints.",
            f"Consider whether {req.target_count} targets are necessary in a slot this tight for {proc}.",
        ]
    else:
        pool = [
            f"Median requirement (~{c['p50']} min) already exceeds booking by ~{c['shortfall']} min before any teaching overhead.",
            f"Even an efficient P80 path ({c['p80']} min) cannot fit without extending the {proc} session.",
            f"With {req.experience_level} experience and complexity {req.complexity_level}/5, time pressure may force skipped steps.",
            f"Worst-case tail (P90 {c['p90']} min) suggests incomplete closure or rushed safety checks.",
        ]

    return _pick_many(pool, seed, 3)


def _build_training_insights(req: PredictionRequest, match: ProcedureMatch, factors: List[str], seed: int) -> List[str]:
    insights = [
        f"You entered '{req.surgery_procedure}' — interpreted as {match.matched_procedure} ({match.procedure_category}).",
        f"Approach: {req.surgery_type} | Trainee band: {req.experience_level} | Session #{req.session_index}.",
        f"Operational load: {req.target_count} targets, {req.tool_changes} tool changes, complexity {req.complexity_level}/5.",
    ]

    if has_profile(req):
        profile_bits = []
        if req.surgeon_name:
            profile_bits.append(req.surgeon_name)
        if req.surgeon_grade:
            profile_bits.append(f"grade {req.surgeon_grade}")
        if req.procedure_count is not None:
            profile_bits.append(f"{req.procedure_count} procedures logged")
        if req.risk_index is not None:
            profile_bits.append(f"risk index {req.risk_index}/10")
        if req.primary_procedure:
            profile_bits.append(f"primary: {req.primary_procedure}")
        if req.profile_skills:
            profile_bits.append(f"skills: {', '.join(req.profile_skills[:4])}")
        insights.append(f"Surgeon profile applied — {'; '.join(profile_bits)}.")
    else:
        insights.append("No surgeon profile selected — analysis uses session inputs and experience band only.")

    contextual = []
    if req.workspace_constraint.lower() == "tight":
        contextual.append("Workspace marked tight — expect ergonomics to influence pace.")
    if req.time_of_day.lower() == "evening":
        contextual.append("Evening slot selected — fatigue effects are more likely late in the case.")
    if req.fine_motor_ratio.lower() == "high":
        contextual.append("High fine-motor demand flagged — precision steps will dominate variance.")

    driver = [f for f in factors if not f.startswith("Procedure:") and not f.startswith("Category:")]
    if driver:
        contextual.append(f"Strongest model drivers this run: {', '.join(driver[:3])}.")

    return insights + _pick_many(contextual, seed + 3, min(3, len(contextual) or 1))


def generate_rich_analysis(
    req: PredictionRequest,
    match: ProcedureMatch,
    p50: float,
    p80: float,
    p90: float,
    risk: str,
    factors: List[str],
):
    knowledge = PROCEDURE_KNOWLEDGE[match.procedure_id]
    seed = _seed(req.surgery_procedure, req.booked_minutes, req.session_index, req.experience_level, risk)
    ctx = _timing_context(req, p50, p80, p90)

    summary = _build_summary(req, match, ctx, risk, seed)
    bullets = _build_timing_narrative(req, match, ctx, risk, seed + 1)

    procedure_risks = knowledge["risks"][:2]
    procedure_hazards = knowledge["hazards"][:2]
    contextual_risks = _contextual_risks(req)[:3]
    contextual_hazards = _contextual_hazards(req)[:2]

    risk_hazards = []
    for item in procedure_risks + contextual_risks:
        line = f"Risk — {item}"
        if line not in risk_hazards:
            risk_hazards.append(line)
    for item in procedure_hazards + contextual_hazards:
        line = f"Hazard — {item}"
        if line not in risk_hazards:
            risk_hazards.append(line)

    training_insights = _build_training_insights(req, match, factors, seed)

    actions = {
        "green": [
            f"Keep the {match.matched_procedure} slot; use spare time for structured feedback rather than extra unplanned reps.",
            f"Run the case with a explicit step checklist for {match.matched_procedure}, then log actual vs predicted timings.",
            "No schedule change needed — monitor only for equipment delays or faculty interruptions.",
        ],
        "amber": [
            f"Add 10–15 min for {match.matched_procedure}, or drop target count from {req.target_count} to reduce overrun exposure.",
            "Pre-stage instruments to avoid losing the thin buffer during tool swaps.",
            f"Assign a facilitator timekeeper for the highest-variance {match.matched_procedure} steps.",
        ],
        "red": [
            f"Extend booking for {match.matched_procedure} or split into two sessions before retrying.",
            f"Reduce complexity to ≤3 and lower targets below {req.target_count} for the next attempt.",
            "Escalate to supervisor planning review — current slot is unlikely to meet training objectives safely.",
        ],
    }
    action = _pick(actions[risk], seed + 5)

    return {
        "explanation_text": summary,
        "explanation_bullets": bullets,
        "recommended_action": action,
        "matched_procedure": match.matched_procedure,
        "procedure_category": match.procedure_category,
        "match_confidence": match.match_confidence,
        "risk_hazards": risk_hazards[:6],
        "training_insights": training_insights[:6],
    }
