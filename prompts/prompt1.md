# AI Surgical Training Tool — System Design Document

**Project:** Surgical Training Risk Assessment Tool  
**Author:** Zhen Wei Yap  
**Status:** Trial / Pilot Phase  
**Last Updated:** 2025  

---

## System Inputs

### 1. Case Parameters
Standard inputs provided per training session:

- **Surgery Procedure** — Free-text field. The surgeon/doctor inputs the name of the surgical procedure being performed (e.g., "Laparoscopic Cholecystectomy", "Open Appendectomy", "Robotic Prostatectomy"). This replaces the previous fixed Task Type dropdown. The FastAPI backend parses this input and maps it to a procedure category and duration multiplier (see *Procedure Multiplier Logic* below).
- **Surgery Type** — Open / Laparoscopic / Robotic. Affects baseline duration assumptions and complexity weighting.
- **Complexity Level** — Ordinal scale (1–5)
- **Workspace Constraint** — Open / Moderate / Tight
- **Fine Motor Demands** — Low / Medium / High
- **Target Count** — Number of repetitions required
- **Tool Changes** — Number of instrument exchanges
- **Session Index** — Cumulative session number; proxy for fatigue
- **Time of Day** — Morning / Afternoon / Evening (circadian adjustment)
- **Booked Duration** — Allocated theatre time in minutes

### 2. Trainee / Surgeon Parameters
Role-based contextual inputs:

- **Experience Level** — Novice / Intermediate / Advanced (auto-derived from Surgeon Profile grade)

### 3. Historical Performance Baseline *(future integration)*
- Average procedural duration per procedure type
- Overrun frequency (% of cases exceeding booked time)
- Predicted vs. actual duration comparison metric

---

## Procedure Multiplier Logic

### Can FastAPI decide the multiplier based on the surgical procedure name?

**Yes — and this is the recommended approach.**

Rather than a fixed dropdown of 4 task types, the FastAPI backend can accept the free-text procedure name and apply a dynamic multiplier using a keyword-matching or classification lookup. This approach is both practical and extensible.

### Implementation Options

#### Option A — Keyword Lookup Table (Recommended for MVP)
Maintain a dictionary in the backend that maps procedure keywords to a `base_minutes` and `complexity_multiplier`:

```python
PROCEDURE_LOOKUP = {
    "cholecystectomy":        {"base_minutes": 45, "multiplier": 1.2},
    "appendectomy":           {"base_minutes": 35, "multiplier": 1.0},
    "hernia repair":          {"base_minutes": 50, "multiplier": 1.1},
    "prostatectomy":          {"base_minutes": 120, "multiplier": 1.4},
    "colectomy":              {"base_minutes": 90, "multiplier": 1.35},
    "bowel resection":        {"base_minutes": 95, "multiplier": 1.35},
    "nephrectomy":            {"base_minutes": 80, "multiplier": 1.3},
    "thyroidectomy":          {"base_minutes": 60, "multiplier": 1.15},
    "suturing":               {"base_minutes": 15, "multiplier": 1.0},
    "knot tying":             {"base_minutes": 12, "multiplier": 0.9},
    "peg transfer":           {"base_minutes": 10, "multiplier": 0.85},
    # fallback
    "default":                {"base_minutes": 40, "multiplier": 1.0},
}

def get_procedure_params(procedure_name: str) -> dict:
    name = procedure_name.lower()
    for keyword, params in PROCEDURE_LOOKUP.items():
        if keyword in name:
            return params
    return PROCEDURE_LOOKUP["default"]
```

The matched multiplier is then applied inside `calculate_quantiles()` alongside the surgery type, experience level, and other coefficients.

#### Option B — ML Classification *(future)*
A trained text classifier (e.g., fine-tuned on surgical procedure ontologies such as SNOMED-CT) could categorise free-text input into procedure families with associated risk and duration profiles. This is the target architecture for the full system.

### API Field Change

The `PredictionRequest` schema is updated as follows:

```python
# Before
task_type: str   # "suturing" | "peg_transfer" | "knot_tying" | "cutting"

# After
surgery_procedure: str   # Free-text, e.g. "Laparoscopic Cholecystectomy"
surgery_type: str        # "open" | "laparoscopic" | "robotic"
```

The backend resolves `surgery_procedure` → `base_minutes` + `procedure_multiplier` before calculating P50/P80/P90.

---

## Surgeon Profile Module

### Purpose

To refine prediction accuracy by incorporating individual surgeon characteristics, moving beyond generic role-based assumptions. Each surgeon's profile acts as a personalised calibration layer on top of the base model output.

---

### Key Inputs

#### a) Surgeon Level (Grade)
Categorical input reflecting training stage. Used as a **baseline efficiency multiplier** within the prediction engine.

| Category | Options |
|----------|---------|
| Core Trainee | CT1, CT2 |
| Specialty Trainee | ST1, ST2, ST3, ST4, ST5, ST6, ST7 |
| Consultant | Consultant (<5 years), Consultant (5+ years) |

#### b) Procedures Performed
Integer count — both overall and procedure-specific. Models the **learning curve effect**: rapid efficiency gain in early cases, plateauing towards expert level.

#### c) Risk / Consistency Index
A continuous **0–10 scale**:

| Score | Profile |
|-------|---------|
| 0 | Fast / Risky — minimal redundancy, high speed |
| 5 | Balanced — moderate pacing, typical variance |
| 10 | Slow / Cautious — methodical, low variance |

This index directly modulates the P50–P90 spread in the duration distribution. A high index increases P50 (slower base) but compresses uncertainty (more consistent).

#### d) Historical Performance Data
- **Average Duration** — Personal baseline for calibration against cohort norms
- **Duration Variance** — Consistency metric; high variance increases P90 estimates
- **Overrun Frequency** — Percentage of previous cases that exceeded booked time

#### e) Surgical Approach *(contextual)*
Method type used: Open / Laparoscopic / Robotic. Affects baseline duration assumptions and complexity weighting.

#### f) Skillsets *(free-form tags)*
User-defined tags representing specific competencies (e.g., `laparoscopy`, `robotics`, `cataract`). Used for contextual filtering and cohort matching in future iterations.

---

### Integration with System Layers

#### Layer 1 — Prediction Engine
Surgeon Profile inputs act as **weighted coefficients** applied to the base duration model:

- A **high Risk Index** (e.g., 9/10) increases the P50 estimate but narrows the P50–P90 gap (consistent, cautious surgeon).
- A **Novice grade** (CT1/CT2) increases both the base duration and variance — reflecting higher unpredictability.
- **Procedure count** applies a learning-curve adjustment; surgeons early in their case volume receive a positive duration multiplier that reduces as count increases.

#### Layer 2 — Risk Classification
The enriched duration distribution from Layer 1 is compared against the booked slot. The profile-calibrated P80/P90 values inform whether the traffic-light score is Green, Amber, or Red.

#### Layer 3 — Feedback Loop
Post-case, the system compares:

```
Predicted Time (profile-adjusted) ↔ Actual Duration
```

If a surgeon consistently **beats** their prediction, their personal **Efficiency Factor** is decremented for future bookings. If they consistently **overrun**, it is incremented. This enables continuous personalised recalibration without retraining the base model.

---

### Trainee Insight

The Surgeon Profile Module also serves an **educational function**:

- Provides objective data on a trainee's pace relative to their grade cohort.
- Highlights outlier sessions (unusually fast or slow) for reflective debrief.
- Tracks improvement over time via procedure count and variance trends.
- Supports supervisors in identifying trainees who may benefit from targeted intervention.

---

### Data Model

Each surgeon profile is stored with the following schema:

```json
{
  "id": "string (UUID)",
  "name": "string",
  "grade": "string (e.g. ST3)",
  "proceduresPerformed": "number",
  "primaryProcedure": "string (optional)",
  "riskIndex": "number (0–10)",
  "skills": ["string"],
  "createdAt": "number (Unix timestamp)",
  "updatedAt": "number (Unix timestamp)"
}
```

Profiles are persisted to `localStorage` on the client during the pilot phase. Server-side persistence is planned for production.

---

### Disclaimer

> The Surgeon Profile Module is designed for **logistical resource allocation and educational support only**. Profile data and predictions do not constitute a clinical assessment, competency judgement, or performance review. This tool must not replace the professional judgement of a supervising clinician or training programme director.

---

## Output Schema

The system returns the following per assessment:

| Field | Type | Description |
|-------|------|-------------|
| `p50_minutes` | number | Median duration estimate |
| `p80_minutes` | number | 80th percentile estimate |
| `p90_minutes` | number | 90th percentile estimate |
| `recommended_booking_minutes` | number | Suggested slot allocation |
| `overrun_probability_est` | number | Probability of exceeding booked time (0–1) |
| `risk_color` | string | `green` / `amber` / `red` |
| `explanation_text` | string | Plain-English summary |
| `explanation_bullets` | string[] | Key contributing factors |
| `recommended_action` | string | Scheduling recommendation |

---

## Constraints & Limitations

- **Pilot stage only** — outputs are experimental and should not be used for operational decisions.
- **No patient data** is used or stored at any point.
- Procedure name matching is keyword-based in the MVP; mismatched or unusual procedure names will fall back to default multipliers.
- Model predictions are based on synthetic/simulated training data pending real-world dataset integration.