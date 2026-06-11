# AI Surgical Training Tool — System Design Document

**Project:** Surgical Training Risk Assessment Tool  
**Author:** Zhen Wei Yap  
**Status:** Trial / Pilot Phase  
**Last Updated:** 2025  
**Change from prompt1.md:** Surgery Procedure field changed from free-text input to a searchable autocomplete combobox.

---

## System Inputs

### 1. Case Parameters
Standard inputs provided per training session:

- **Surgery Procedure** — Searchable autocomplete field. The surgeon/doctor begins typing a procedure name (e.g., "Robotic", "Chole") and is presented with up to 6 matching suggestions drawn from a curated `PROCEDURE_SUGGESTIONS` list. The user may select a suggestion or continue typing a custom value. Custom/unmatched entries fall back to the default multiplier in the backend. Replaces the previous free-text input. See *Procedure Search UX* below.
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

## Procedure Search UX

### Why Autocomplete Instead of Free-Text?

The previous free-text input for Surgery Procedure was replaced with a **searchable combobox** to:

1. **Reduce typos** that cause keyword matching to fail and fall back to default parameters.
2. **Guide users** toward known procedure names that have calibrated `base_minutes` and `multiplier` values.
3. **Preserve flexibility** — users can still type a custom/unlisted procedure; the backend gracefully falls back to the default estimate.

### Frontend Implementation (`ProcedureSearchInput` component)

```jsx
const PROCEDURE_SUGGESTIONS = [
  "Cholecystectomy",
  "Laparoscopic Cholecystectomy",
  "Robotic Cholecystectomy",
  "Appendectomy",
  "Laparoscopic Appendectomy",
  "Hernia Repair",
  "Laparoscopic Hernia Repair",
  "Robotic Hernia Repair",
  "Prostatectomy",
  "Robotic Prostatectomy",
  "Laparoscopic Prostatectomy",
  "Colectomy",
  "Laparoscopic Colectomy",
  "Robotic Colectomy",
  "Bowel Resection",
  "Laparoscopic Bowel Resection",
  "Nephrectomy",
  "Laparoscopic Nephrectomy",
  "Robotic Nephrectomy",
  "Thyroidectomy",
  "Robotic Thyroidectomy",
  "Suturing",
  "Knot Tying",
  "Peg Transfer",
  "Cutting",
  "Open Appendectomy",
  "Open Colectomy",
  "Open Nephrectomy",
];
```

### Combobox Behaviour

| Interaction | Behaviour |
|-------------|-----------|
| Type any substring | Filters list; up to 6 matches shown |
| `ArrowDown` / `ArrowUp` | Moves highlight through suggestions |
| `Enter` | Selects highlighted suggestion |
| `Escape` | Closes dropdown, retains typed value |
| Click suggestion | Selects and closes dropdown |
| Click `✕` button | Clears the field |
| Click outside | Closes dropdown |
| No matches found | Shows "No matching procedures — will use default estimate" |

### Matching Highlight

The matched substring within each suggestion is rendered in **bold + underline** so users can see exactly which part of their query matched.

### Custom / Unlisted Procedures

If a user types a procedure not in `PROCEDURE_SUGGESTIONS`, the value is still sent to the backend as-is. The backend `get_procedure_params()` function performs its own keyword-matching against `PROCEDURE_LOOKUP`. If no keyword match is found, the default parameters apply:

```python
"default": {"base_minutes": 40, "multiplier": 1.0}
```

---

## Procedure Multiplier Logic

### Backend Implementation (unchanged from prompt1.md)

```python
PROCEDURE_LOOKUP = {
    "cholecystectomy":   {"base_minutes": 45, "multiplier": 1.2},
    "appendectomy":      {"base_minutes": 35, "multiplier": 1.0},
    "hernia repair":     {"base_minutes": 50, "multiplier": 1.1},
    "prostatectomy":     {"base_minutes": 120, "multiplier": 1.4},
    "colectomy":         {"base_minutes": 90, "multiplier": 1.35},
    "bowel resection":   {"base_minutes": 95, "multiplier": 1.35},
    "nephrectomy":       {"base_minutes": 80, "multiplier": 1.3},
    "thyroidectomy":     {"base_minutes": 60, "multiplier": 1.15},
    "suturing":          {"base_minutes": 15, "multiplier": 1.0},
    "knot tying":        {"base_minutes": 12, "multiplier": 0.9},
    "peg transfer":      {"base_minutes": 10, "multiplier": 0.85},
    "cutting":           {"base_minutes": 8,  "multiplier": 0.9},
    "default":           {"base_minutes": 40, "multiplier": 1.0},
}

def get_procedure_params(procedure_name: str) -> dict:
    name = procedure_name.lower()
    for keyword, params in PROCEDURE_LOOKUP.items():
        if keyword in name:
            return params
    return PROCEDURE_LOOKUP["default"]
```

### API Field (unchanged from prompt1.md)

```python
surgery_procedure: str   # Autocomplete-assisted, e.g. "Robotic Cholecystectomy"
surgery_type: str        # "open" | "laparoscopic" | "robotic"
```

---

## Surgeon Profile Module

*(Unchanged from prompt1.md — see original document)*

---

## Output Schema

*(Unchanged from prompt1.md — see original document)*

---

## Constraints & Limitations

- **Pilot stage only** — outputs are experimental and should not be used for operational decisions.
- **No patient data** is used or stored at any point.
- The autocomplete suggestion list is static and curated; it should be extended as the procedure library grows.
- Procedure name matching on the backend remains keyword-based in the MVP; custom entries not matching any keyword fall back to default multipliers.
- Model predictions are based on synthetic/simulated training data pending real-world dataset integration.
