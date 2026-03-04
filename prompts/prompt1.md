✅ Copilot Edit Prompt

Edit the current document to include a new subsection under System Inputs titled:

“Surgeon Profile Module”

The new section should:

Expand the System Inputs to explicitly include a structured Surgeon Profile.

Integrate naturally with the existing Layer One (Prediction Engine), Layer Two (Risk Classification), and Layer Three (Feedback Loop) structure.

Maintain the same professional tone and formatting style as the rest of the document.

The Surgeon Profile Module should include:

Surgeon level (CT1–CT2, ST1–7, Consultant <5 years, Consultant >5 years)

Number of procedures performed (overall and procedure-specific)

Historical average procedural duration

Variance/consistency in duration

Overrun frequency rate (percentage of cases exceeding booked time)

Surgeon’s predicted time vs actual time comparison metric

Surgical approach type (Open, Laparoscopic, Robotic)

Risk-style index (0–10 scale: Efficient vs Risk-Averse)

It should explain:

How these features feed into the Prediction Engine as weighted inputs.

How Surgeon Prediction, Model Prediction, and Actual Duration feed into the Feedback Loop for continuous recalibration.

How this module supports trainee calibration and performance insight.

That this remains decision-support software and does not replace clinical judgement.

Ensure the section:

Is integrated into the existing structure (not standalone).

Improves clarity and depth of the overall system design.

Does not repeat content unnecessarily.

### 4. Surgeon Profile Module (New Subsection)

**Purpose**: To refine prediction accuracy by incorporating individual surgeon characteristics, moving beyond generic role-based assumptions.

**Key Inputs**:
*   **Surgeon Level**: Categorical input (CT1–CT2, ST1–7, Consultant <5 years, Consultant >5 years) acting as a baseline efficiency multiplier.
*   **Procedures Performed**: Integer count (overall and procedure-specific) to model the learning curve effect (e.g., rapid gain in early cases vs. plateau in experts).
*   **Risk/Consistency Index**: A verified 0–10 scale where 0 represents a "Fast/Risky" style and 10 represents a "Slow/Cautious" style. This directly modulates the distribution variance (P90-P50 spread).
*   **Historical Performance**:
    *   *Average Duration*: Baseline for personal calibration.
    *   *Overrun Frequency*: Percentage of previous cases that exceeded booked time.
*   **Surgical Approach**: Method context (Open, Laparoscopic, Robotic).

**Integration Logic**:
1.  **Prediction Engine (Layer 1)**: These inputs act as weighted coefficients. For example, a high "Risk Index" increases the P50 estimation but narrows the P50-P90 uncertainty gap (consistent but slow). A "Novice" level increases both the base duration and the variance.
2.  **Feedback Loop (Layer 3)**: The system compares the *Predicted Time* vs *Actual Time*. If a specific surgeon consistently beats the prediction, their personal "Efficiency Factor" is updated for future bookings.
3.  **Trainee Insight**: Provides objectified data on a trainee's pace relative to their cohort, supporting targeted educational interventions.

**Disclaimer**: This profiling is for logistical resource allocation and educational support only. It does not replace clinical judgement or competency assessment.