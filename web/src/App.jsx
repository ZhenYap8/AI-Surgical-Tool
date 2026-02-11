import { useState } from 'react'

const API_URL = "http://localhost:8000/predict_and_explain";

function App() {
  const [formData, setFormData] = useState({
    task_type: "suturing",
    booked_minutes: 30,
    complexity_level: 3,
    session_index: 1,
    experience_level: "intermediate",
    target_count: 5,
    tool_changes: 1,
    fine_motor_ratio: "medium",
    workspace_constraint: "moderate",
    time_of_day: "morning"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ["complexity_level", "booked_minutes", "session_index", "target_count", "tool_changes"].includes(name) ? 
              parseInt(value) : value
    }));
  };

  const assessRisk = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) throw new Error("API Request Failed");
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Visualization scale helper
  const getMaxScale = () => {
    if (!result) return 100;
    return Math.max(result.p90_minutes, formData.booked_minutes) * 1.2;
  };
  
  const getPct = (val) => {
    const max = getMaxScale();
    return Math.min((val / max) * 100, 100) + "%";
  };

  return (
    <div className="container">
      <nav className="navbar">
        <div className="navbar-content">
          <img 
            src="/nhslogo.svg.webp" 
            alt="NHS Logo" 
            className="nhs-logo"
            onError={(e) => {
              // Fallback if local file isn't found
              e.target.src = "https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" 
            }}
          />
          <h1>Surgical Training Risk Assessment</h1>
        </div>
      </nav>

      <main className="layout">
        <section className="input-panel">
          <h2>Training Parameters</h2>
          
          <div className="form-group">
            <label>Task Type</label>
            <select name="task_type" value={formData.task_type} onChange={handleChange}>
              <option value="suturing">Suturing</option>
              <option value="peg_transfer">Peg Transfer</option>
              <option value="knot_tying">Knot Tying</option>
              <option value="cutting">Cutting/Dissection</option>
            </select>
          </div>

          <div className="form-group">
             <label>Experience Level</label>
             <select name="experience_level" value={formData.experience_level} onChange={handleChange}>
               <option value="novice">Novice</option>
               <option value="intermediate">Intermediate</option>
               <option value="advanced">Advanced</option>
             </select>
          </div>

          <div className="form-group">
            <label>Complexity (1-5): {formData.complexity_level}</label>
            <input 
              type="range" min="1" max="5" 
              name="complexity_level" 
              value={formData.complexity_level} 
              onChange={handleChange} 
            />
          </div>

          <div className="form-group">
            <label>Target Count (Reps)</label>
            <input 
              type="number" 
              name="target_count" 
              value={formData.target_count} 
              onChange={handleChange} 
            />
          </div>

          <div className="form-group">
            <label>Workspace Constraint</label>
            <select name="workspace_constraint" value={formData.workspace_constraint} onChange={handleChange}>
              <option value="open">Open</option>
              <option value="moderate">Moderate</option>
              <option value="tight">Tight</option>
            </select>
          </div>
          
           <div className="form-group">
            <label>Session Index (Fatigue)</label>
            <input 
              type="number" min="1"
              name="session_index" 
              value={formData.session_index} 
              onChange={handleChange} 
            />
          </div>
          
          <div className="form-group">
            <label>Tool Changes</label>
            <input 
              type="number" min="0"
              name="tool_changes" 
              value={formData.tool_changes} 
              onChange={handleChange} 
            />
          </div>

           <div className="form-group">
            <label>Fine Motor Demands</label>
            <select name="fine_motor_ratio" value={formData.fine_motor_ratio} onChange={handleChange}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div className="form-group">
            <label>Time of Day</label>
            <select name="time_of_day" value={formData.time_of_day} onChange={handleChange}>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="evening">Evening</option>
            </select>
          </div>

          <div className="form-group highlight">
            <label>Booked Minutes</label>
            <input 
              type="number" 
              name="booked_minutes" 
              value={formData.booked_minutes} 
              onChange={handleChange} 
            />
          </div>

          <button onClick={assessRisk} disabled={loading}>
            {loading ? "Analyzing..." : "Assess Training Risk"}
          </button>
          
          {error && <div className="error">{error}</div>}
        </section>

        <section className="output-panel">
          {result ? (
            <>
              <div className={`traffic-light ${result.risk_color}`}>
                <div className="light-circle"></div>
                <h2>{result.risk_color.toUpperCase()} RISK</h2>
              </div>
              
              <div className="metrics">
                 <div className="metric-box">
                   <span>Rec. Booking</span>
                   <strong>{result.recommended_booking_minutes}m</strong>
                 </div>
                 <div className="metric-box">
                   <span>Overrun Prob.</span>
                   <strong>{(result.overrun_probability_est * 100).toFixed(0)}%</strong>
                 </div>
              </div>

              <h3>Duration Estimates (vs Booked)</h3>
              <div className="chart-container">
                {/* Booked Marker */}
                <div className="bar-row">
                   <div className="bar-label">Booked ({formData.booked_minutes}m)</div>
                   <div className="track">
                     <div className="bar booked-bar" style={{ width: getPct(formData.booked_minutes) }}></div>
                   </div>
                </div>

                {/* Stat Markers */}
                <div className="bar-row">
                   <div className="bar-label">Predicted</div>
                   <div className="track">
                      {/* P50 */}
                      <div className="marker p50" style={{ left: getPct(result.p50_minutes) }}>
                        <span className="tooltip">50%: {result.p50_minutes}m</span>
                      </div>
                      {/* P80 */}
                      <div className="marker p80" style={{ left: getPct(result.p80_minutes) }}>
                        <span className="tooltip">80%: {result.p80_minutes}m</span>
                      </div>
                      {/* P90 */}
                      <div className="marker p90" style={{ left: getPct(result.p90_minutes) }}>
                        <span className="tooltip">90%: {result.p90_minutes}m</span>
                      </div>
                      <div className="fill-range" style={{ 
                        left: getPct(result.p50_minutes), 
                        width: `calc(${getPct(result.p90_minutes)} - ${getPct(result.p50_minutes)})` 
                      }}></div>
                   </div>
                </div>
              </div>

              <div className="explanation">
                <h3>Analysis</h3>
                <p><strong>{result.explanation_text}</strong></p>
                <ul>
                  {result.explanation_bullets.map((b, i) => <li key={i}>{b}</li>)}
                </ul>
                <div className="action-box">
                  <strong>Recommendation:</strong> {result.recommended_action}
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">
              Enter details and click "Assess Risk" to see the prediction.
            </div>
          )}
        </section>
      </main>

      <footer className="footer-disclaimer">
        <p>
          <strong>⚠️ Trial Stage Disclaimer:</strong> This tool is currently in a pilot/testing phase. 
          The predictions and risk assessments provided are for experimental purposes only and should not be relied upon for critical operational or clinical decisions.
        </p>
        <p className="attribution">Designed by Zhen Wei Yap</p>
      </footer>
    </div>
  )
}

export default App
