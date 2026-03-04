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
