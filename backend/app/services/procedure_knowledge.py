PROCEDURE_KNOWLEDGE = {
    "cholecystectomy": {
        "display_name": "Cholecystectomy",
        "category": "Hepatobiliary",
        "base_minutes": 45,
        "multiplier": 1.2,
        "aliases": ["lap chole", "laparoscopic cholecystectomy", "open cholecystectomy"],
        "keywords": ["gallbladder", "cystic", "calot", "bile"],
        "risks": [
            "Critical view of safety may be rushed under time pressure",
            "Cystic duct misidentification risk during early training reps",
        ],
        "hazards": [
            "Electrocautery near hepatobiliary structures",
            "Retractor crowding in limited port spacing",
        ],
        "insights": [
            "Verbalise critical view of safety before clipping",
            "Slow down when Calot's triangle anatomy is uncertain",
        ],
    },
    "appendectomy": {
        "display_name": "Appendectomy",
        "category": "General Surgery",
        "base_minutes": 35,
        "multiplier": 1.0,
        "aliases": ["lap appendectomy", "open appendectomy", "appendicectomy"],
        "keywords": ["appendix", "mesoappendix", "base"],
        "risks": [
            "Base control errors if stump management is hurried",
            "Perforated-case simulation adds non-linear time spikes",
        ],
        "hazards": [
            "Blind stapling/firing without adequate exposure",
            "Trocar placement conflicts in tight abdominal models",
        ],
        "insights": [
            "Confirm base orientation before division",
            "Allow extra time for mesoappendix control in novice reps",
        ],
    },
    "hernia repair": {
        "display_name": "Hernia Repair",
        "category": "Abdominal Wall",
        "base_minutes": 50,
        "multiplier": 1.1,
        "aliases": ["laparoscopic hernia", "inguinal hernia", "mesh repair"],
        "keywords": ["hernia", "mesh", "inguinal", "femoral", "defect"],
        "risks": [
            "Mesh handling and fixation add setup variability",
            "Reduced tactile feedback increases positioning errors",
        ],
        "hazards": [
            "Cord/vessel proximity during dissection",
            "Ergonomic strain from sustained mesh positioning",
        ],
        "insights": [
            "Pre-position mesh and fixation tools before docking",
            "Use deliberate slow mesh deployment in training reps",
        ],
    },
    "prostatectomy": {
        "display_name": "Prostatectomy",
        "category": "Urology",
        "base_minutes": 120,
        "multiplier": 1.4,
        "aliases": ["robotic prostatectomy", "laparoscopic prostatectomy", "ralp"],
        "keywords": ["prostate", "vesicle", "urethra", "neurovascular"],
        "risks": [
            "Long case duration amplifies fatigue-related variance",
            "Anastomosis quality degrades when session is rushed",
        ],
        "hazards": [
            "Bleeding obscuring planes during trainee-led steps",
            "Console-robot coordination delays on handoffs",
        ],
        "insights": [
            "Plan a mid-case pause checkpoint for long simulations",
            "Reserve buffer for urethrovesical anastomosis rehearsal",
        ],
    },
    "colectomy": {
        "display_name": "Colectomy",
        "category": "Colorectal",
        "base_minutes": 90,
        "multiplier": 1.35,
        "aliases": ["laparoscopic colectomy", "right hemicolectomy", "sigmoid colectomy"],
        "keywords": ["colon", "mesentery", "vascular", "anastomosis"],
        "risks": [
            "Vascular control steps dominate overrun in novice runs",
            "Anastomosis troubleshooting is a common tail-risk event",
        ],
        "hazards": [
            "Ureter/retroperitoneal structure proximity in deep dissection",
            "Instrument clash during multi-quadrant mobilisation",
        ],
        "insights": [
            "Stage the case: mobilisation, control, then anastomosis",
            "Build explicit time for leak-test rehearsal if simulated",
        ],
    },
    "bowel resection": {
        "display_name": "Bowel Resection",
        "category": "Colorectal",
        "base_minutes": 95,
        "multiplier": 1.35,
        "aliases": ["small bowel resection", "intestinal resection"],
        "keywords": ["bowel", "resection", "anastomosis", "mesentery"],
        "risks": [
            "Perfusion assessment and resection margins add variability",
            "Stapler misfire or reload cycles extend session time",
        ],
        "hazards": [
            "Tension on mesentery during trainee traction",
            "Contamination risk if enterotomy not managed promptly",
        ],
        "insights": [
            "Confirm vascular arcade before stapler deployment",
            "Keep reload kits accessible to avoid long interruptions",
        ],
    },
    "nephrectomy": {
        "display_name": "Nephrectomy",
        "category": "Urology",
        "base_minutes": 80,
        "multiplier": 1.3,
        "aliases": ["laparoscopic nephrectomy", "robotic nephrectomy"],
        "keywords": ["kidney", "renal", "hilum", "ureter"],
        "risks": [
            "Hilar control is a high-variance training milestone",
            "Adherent perinephric fat slows early trainee progress",
        ],
        "hazards": [
            "Vascular injury risk during inexperienced hilar dissection",
            "Port triangulation limits in robotic docking setups",
        ],
        "insights": [
            "Use a structured hilar approach checklist per rep",
            "Allow warm-up on mobilisation before hilar time trial",
        ],
    },
    "thyroidectomy": {
        "display_name": "Thyroidectomy",
        "category": "Head & Neck",
        "base_minutes": 60,
        "multiplier": 1.15,
        "aliases": ["robotic thyroidectomy", "hemithyroidectomy"],
        "keywords": ["thyroid", "parathyroid", "recurrent laryngeal", "isthmus"],
        "risks": [
            "Nerve monitoring setup and interpretation add overhead",
            "Fine dissection steps are sensitive to micro-fatigue",
        ],
        "hazards": [
            "Recurrent laryngeal nerve proximity in narrow field",
            "Cautery thermal spread near parathyroid tissue",
        ],
        "insights": [
            "Prioritise nerve plane identification over speed",
            "Schedule head-and-neck cases earlier in the session",
        ],
    },
    "suturing": {
        "display_name": "Suturing",
        "category": "Fundamentals Lab",
        "base_minutes": 15,
        "multiplier": 1.0,
        "aliases": ["suture practice", "skin closure", "interrupted sutures"],
        "keywords": ["suture", "needle", "knot", "closure"],
        "risks": [
            "Knot security checks extend time when targets are high",
            "Needle re-grasps spike duration for novice trainees",
        ],
        "hazards": [
            "Needlestick risk with rushed needle handling",
            "Poor ergonomics from non-dominant hand positioning",
        ],
        "insights": [
            "Batch needle loads to reduce pick-up delays",
            "Focus on consistent knot sequence before speed drills",
        ],
    },
    "knot tying": {
        "display_name": "Knot Tying",
        "category": "Fundamentals Lab",
        "base_minutes": 12,
        "multiplier": 0.9,
        "aliases": ["knot practice", "instrument tie", "hand tie"],
        "keywords": ["knot", "tie", "throw", "ligature"],
        "risks": [
            "Slipped knots trigger full rep restarts",
            "Two-handed coordination errors add nonlinear delay",
        ],
        "hazards": [
            "Suture tangling under time pressure",
            "Wrist fatigue from repeated instrument ties",
        ],
        "insights": [
            "Use a standardised square-knot sequence for benchmarking",
            "Reduce target count when introducing a new knot technique",
        ],
    },
    "peg transfer": {
        "display_name": "Peg Transfer",
        "category": "Laparoscopic Skills",
        "base_minutes": 10,
        "multiplier": 0.85,
        "aliases": ["peg drill", "laparoscopic peg transfer"],
        "keywords": ["peg", "transfer", "lap", "coordination"],
        "risks": [
            "Dropped object recovery dominates overrun time",
            "Non-dominant hand weakness widens variance",
        ],
        "hazards": [
            "Camera-assist conflicts during solo drills",
            "Port collision in tight trainer boxes",
        ],
        "insights": [
            "Stabilise the object before committing to transfer",
            "Practise camera navigation separately if drops are frequent",
        ],
    },
    "cutting": {
        "display_name": "Cutting",
        "category": "Fundamentals Lab",
        "base_minutes": 8,
        "multiplier": 0.9,
        "aliases": ["precision cutting", "scissor drill"],
        "keywords": ["cut", "scissor", "incision", "precision"],
        "risks": [
            "Edge-quality failures force repeat attempts",
            "Fine motor tremor increases with session fatigue",
        ],
        "hazards": [
            "Uncontrolled scissor closure near tethered tissue",
            "Visual misjudgement without adequate magnification",
        ],
        "insights": [
            "Use smooth scissor arcs rather than stabbing cuts",
            "Lower target count when fine-motor demand is high",
        ],
    },
    "default": {
        "display_name": "General Surgical Procedure",
        "category": "Unclassified",
        "base_minutes": 40,
        "multiplier": 1.0,
        "aliases": [],
        "keywords": ["surgery", "operative", "procedure"],
        "risks": [
            "Unfamiliar workflow increases setup and reset time",
            "Procedure ambiguity widens duration confidence intervals",
        ],
        "hazards": [
            "Unclear step sequence may cause tool idle time",
            "Generic briefing may miss procedure-specific safety checks",
        ],
        "insights": [
            "Confirm procedure checklist before starting the session",
            "Log actual timings to improve future matching accuracy",
        ],
    },
}
