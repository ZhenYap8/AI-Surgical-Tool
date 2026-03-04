import { useState, useEffect, useRef } from 'react'

const API_URL = "http://localhost:8000/predict_and_explain";

const GRADE_OPTIONS = [
  "CT1", "CT2",
  "ST1", "ST2", "ST3", "ST4", "ST5", "ST6", "ST7",
  "Consultant (<5 yrs)", "Consultant (5+ yrs)"
];

const GRADE_TO_EXPERIENCE = {
  "CT1": "novice", "CT2": "novice",
  "ST1": "novice", "ST2": "novice", "ST3": "intermediate",
  "ST4": "intermediate", "ST5": "intermediate",
  "ST6": "advanced", "ST7": "advanced",
  "Consultant (<5 yrs)": "advanced", "Consultant (5+ yrs)": "advanced"
};

const RISK_ICONS = { green: "🟢", amber: "🟠", red: "🔴" };
const RISK_LABELS = { green: "LOW RISK", amber: "MODERATE RISK", red: "HIGH RISK" };

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

// ─── Procedure Search Combobox ────────────────────────────────────────────────
function ProcedureSearchInput({ value, onChange }) {
  const [query, setQuery] = useState(value || "");
  const [open, setOpen] = useState(false);
  const [highlighted, setHighlighted] = useState(-1);
  const wrapperRef = useRef(null);

  const filtered = query.trim().length === 0
    ? []
    : PROCEDURE_SUGGESTIONS.filter(p =>
        p.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 6);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
        setHighlighted(-1);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleInput = (e) => {
    setQuery(e.target.value);
    onChange(e.target.value);
    setOpen(true);
    setHighlighted(-1);
  };

  const handleSelect = (suggestion) => {
    setQuery(suggestion);
    onChange(suggestion);
    setOpen(false);
    setHighlighted(-1);
  };

  const handleKeyDown = (e) => {
    if (!open || filtered.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlighted(h => Math.min(h + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlighted(h => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (highlighted >= 0) handleSelect(filtered[highlighted]);
    } else if (e.key === "Escape") {
      setOpen(false);
      setHighlighted(-1);
    }
  };

  // Highlight matching substring
  const highlight = (text, query) => {
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1 || !query) return text;
    return (
      <>
        {text.slice(0, idx)}
        <mark className="suggestion-match">{text.slice(idx, idx + query.length)}</mark>
        {text.slice(idx + query.length)}
      </>
    );
  };

  return (
    <div className="procedure-combobox" ref={wrapperRef}>
      <div className="procedure-input-wrapper">
        <span className="procedure-search-icon">🔍</span>
        <input
          className="form-control procedure-search-input"
          type="text"
          placeholder="e.g. Robotic, Cholecystectomy…"
          value={query}
          onChange={handleInput}
          onFocus={() => query.trim().length > 0 && setOpen(true)}
          onKeyDown={handleKeyDown}
          autoComplete="off"
          aria-autocomplete="list"
          aria-expanded={open && filtered.length > 0}
        />
        {query && (
          <button
            className="procedure-clear-btn"
            type="button"
            aria-label="Clear"
            onClick={() => { setQuery(""); onChange(""); setOpen(false); }}
          >✕</button>
        )}
      </div>
      {open && filtered.length > 0 && (
        <ul className="procedure-suggestions-list" role="listbox">
          {filtered.map((s, i) => (
            <li
              key={s}
              className={`procedure-suggestion-item ${i === highlighted ? "active" : ""}`}
              role="option"
              aria-selected={i === highlighted}
              onMouseDown={() => handleSelect(s)}
              onMouseEnter={() => setHighlighted(i)}
            >
              {highlight(s, query)}
            </li>
          ))}
        </ul>
      )}
      {open && query.trim().length > 0 && filtered.length === 0 && (
        <div className="procedure-no-match">No matching procedures — will use default estimate</div>
      )}
    </div>
  );
}

// ─── Profile Modal ────────────────────────────────────────────────────────────
function ProfileModal({ profile, onSave, onDelete, onClose }) {
  const [form, setForm] = useState(profile || {
    id: null, name: "", grade: "", proceduresPerformed: 0,
    primaryProcedure: "", riskIndex: 5, skills: [],
    createdAt: null, updatedAt: null
  });
  const [skillInput, setSkillInput] = useState("");
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = "Name is required.";
    if (!form.grade) e.grade = "Please select a grade.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;
    onSave({ ...form, proceduresPerformed: Number(form.proceduresPerformed) || 0 });
  };

  const handleSkillKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = skillInput.trim().toLowerCase();
      if (!val || form.skills.length >= 12 || val.length > 20) return;
      if (!form.skills.map(s => s.toLowerCase()).includes(val)) {
        setForm(p => ({ ...p, skills: [...p.skills, val] }));
      }
      setSkillInput("");
    }
  };

  const removeSkill = (s) => setForm(p => ({ ...p, skills: p.skills.filter(x => x !== s) }));

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="modal-title">{form.id ? "Edit Profile" : "New Surgeon Profile"}</h3>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <div className="modal-body">
          {/* Row: Name + Procedures */}
          <div className="form-row-2">
            <div className="input-group">
              <label className="input-label">Full Name <span className="required">*</span></label>
              <input
                className={`form-control ${errors.name ? "input-error" : ""}`}
                type="text"
                placeholder="e.g. Dr. Sarah Smith"
                value={form.name}
                onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
              />
              {errors.name && <span className="error-msg">{errors.name}</span>}
            </div>
            <div className="input-group">
              <label className="input-label">Total Procedures</label>
              <input
                className="form-control"
                type="number"
                min="0"
                value={form.proceduresPerformed}
                onChange={e => setForm(p => ({ ...p, proceduresPerformed: e.target.value }))}
              />
            </div>
          </div>

          {/* Primary Procedure */}
          <div className="input-group">
            <label className="input-label">Primary Procedure <span className="optional">(optional)</span></label>
            <input
              className="form-control"
              type="text"
              placeholder="e.g. Laparoscopic Cholecystectomy"
              value={form.primaryProcedure || ""}
              onChange={e => setForm(p => ({ ...p, primaryProcedure: e.target.value }))}
            />
          </div>

          {/* Grade Pills */}
          <div className="input-group">
            <label className="input-label">Doctor Experience <span className="required">*</span></label>
            <div className="grade-pills">
              {GRADE_OPTIONS.map(g => (
                <button
                  key={g}
                  type="button"
                  className={`grade-pill ${form.grade === g ? "selected" : ""}`}
                  onClick={() => setForm(p => ({ ...p, grade: g }))}
                >{g}</button>
              ))}
            </div>
            {errors.grade && <span className="error-msg">{errors.grade}</span>}
          </div>

          {/* Skill Chips */}
          <div className="input-group">
            <label className="input-label">
              Skillsets
              <span className="tag-count">{form.skills.length}/12</span>
            </label>
            <div className="tag-input-container">
              {form.skills.map(s => (
                <span key={s} className="edit-chip">
                  #{s}
                  <button type="button" className="chip-remove" onClick={() => removeSkill(s)} aria-label={`Remove ${s}`}>✕</button>
                </span>
              ))}
              <input
                className="tag-input"
                type="text"
                placeholder={form.skills.length === 0 ? "Type a skill, press Enter (e.g., laparoscopy, robotics)" : ""}
                value={skillInput}
                onChange={e => setSkillInput(e.target.value)}
                onKeyDown={handleSkillKeyDown}
                maxLength={20}
                disabled={form.skills.length >= 12}
              />
            </div>
            <span className="input-helper">Max 12 tags · 20 chars each · Case-insensitive</span>
          </div>

          {/* Risk Index Slider */}
          <div className="input-group">
            <div className="slider-header">
              <label className="input-label">Risk / Consistency Index</label>
              <span className="range-value-badge">{form.riskIndex}</span>
            </div>
            <input
              type="range" min="0" max="10"
              className="range-slider"
              value={form.riskIndex}
              onChange={e => setForm(p => ({ ...p, riskIndex: parseInt(e.target.value) }))}
            />
            <div className="range-labels">
              <span>0 — Fast / Risky</span>
              <span>10 — Slow / Cautious</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          {form.id && (
            <button className="btn-danger" onClick={() => onDelete(form.id)}>Delete Profile</button>
          )}
          <div className="modal-footer-right">
            <button className="btn-ghost" onClick={onClose}>Cancel</button>
            <button className="btn-primary modal-save-btn" onClick={handleSave}>
              {form.id ? "Save Changes" : "Create Profile"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Profile Card (read-only summary) ────────────────────────────────────────
function ProfileSummaryCard({ profile, onEdit }) {
  return (
    <div className="profile-summary-card">
      <div className="profile-summary-top">
        <div>
          <div className="profile-name">{profile.name}</div>
          <div className="profile-meta">
            <span className="grade-pill selected mini">{profile.grade}</span>
            {profile.primaryProcedure && <span className="meta-item">{profile.primaryProcedure}</span>}
            <span className="meta-item">{profile.proceduresPerformed} procedures</span>
            <span className="meta-item ri-badge">RI {profile.riskIndex}/10</span>
          </div>
        </div>
        <button className="btn-edit-profile" onClick={onEdit}>Edit</button>
      </div>
      {profile.skills.length > 0 && (
        <div className="skill-tags">
          {profile.skills.map((s, i) => (
            <span key={i} className="skill-chip">#{s}</span>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Results Visualization ────────────────────────────────────────────────────
function ResultsPanel({ result, bookedMinutes }) {
  const max = Math.max(result.p90_minutes, bookedMinutes) * 1.25;
  const pct = (v) => `${Math.min((v / max) * 100, 100).toFixed(1)}%`;

  return (
    <div className="results-content">
      {/* Risk Header */}
      <div className={`risk-header ${result.risk_color}`}>
        <div className="risk-icon">{RISK_ICONS[result.risk_color]}</div>
        <div className="risk-label">{RISK_LABELS[result.risk_color]}</div>
        <div className="risk-sub">Based on current training parameters</div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-value">{result.p50_minutes}m</span>
          <span className="stat-label">P50 Median</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{result.p80_minutes}m</span>
          <span className="stat-label">P80 Estimate</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{result.recommended_booking_minutes}m</span>
          <span className="stat-label">Rec. Booking</span>
        </div>
        <div className={`stat-box overrun-stat ${result.risk_color}`}>
          <span className="stat-value">{(result.overrun_probability_est * 100).toFixed(0)}%</span>
          <span className="stat-label">Overrun Risk</span>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="card chart-card">
        <div className="card-header">
          <h4 className="card-title">Duration Estimate vs. Booked Time</h4>
        </div>
        <div className="chart-wrapper">
          {/* Booked bar */}
          <div className="bar-row">
            <div className="bar-meta">Booked</div>
            <div className="bar-track">
              <div className="bar-fill booked-fill" style={{ width: pct(bookedMinutes) }} />
              <span className="bar-value-label">{bookedMinutes}m</span>
            </div>
          </div>
          {/* Prediction range */}
          <div className="bar-row">
            <div className="bar-meta">P50</div>
            <div className="bar-track">
              <div className="bar-fill p50-fill" style={{ width: pct(result.p50_minutes) }} />
              <span className="bar-value-label">{result.p50_minutes}m</span>
            </div>
          </div>
          <div className="bar-row">
            <div className="bar-meta">P80</div>
            <div className="bar-track">
              <div className="bar-fill p80-fill" style={{ width: pct(result.p80_minutes) }} />
              <span className="bar-value-label">{result.p80_minutes}m</span>
            </div>
          </div>
          <div className="bar-row">
            <div className="bar-meta">P90</div>
            <div className="bar-track">
              <div className="bar-fill p90-fill" style={{ width: pct(result.p90_minutes) }} />
              <span className="bar-value-label">{result.p90_minutes}m</span>
            </div>
          </div>
          {/* Scale tick */}
          <div className="chart-scale">
            <span>0m</span>
            <span>{Math.round(max / 2)}m</span>
            <span>{Math.round(max)}m</span>
          </div>
        </div>
      </div>

      {/* Analysis */}
      <div className="card analysis-card">
        <div className="card-header">
          <h4 className="card-title">Analysis</h4>
        </div>
        <p className="analysis-summary">{result.explanation_text}</p>
        {result.top_factors && result.top_factors.length > 0 && (
          <div className="factors-list">
            <span className="factors-label">Key Factors:</span>
            <div className="factors-chips">
              {result.top_factors.map((f, i) => <span key={i} className="factor-chip">{f}</span>)}
            </div>
          </div>
        )}
        <ul className="analysis-bullets">
          {result.explanation_bullets.map((b, i) => <li key={i}>{b}</li>)}
        </ul>
        <div className={`recommendation-banner ${result.risk_color}`}>
          <strong>Recommendation: </strong>{result.recommended_action}
        </div>
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  // Profile state
  const [profiles, setProfiles] = useState(() => {
    try { return JSON.parse(localStorage.getItem("surgeon_profiles")) || []; }
    catch { return []; }
  });
  const [selectedProfileId, setSelectedProfileId] = useState("");
  const [modalState, setModalState] = useState(null); // null | { profile | null }

  useEffect(() => {
    localStorage.setItem("surgeon_profiles", JSON.stringify(profiles));
  }, [profiles]);

  const selectedProfile = profiles.find(p => p.id === selectedProfileId) || null;

  // Form state
  const [formData, setFormData] = useState({
    surgery_procedure: "Suturing",
    booked_minutes: 30,
    complexity_level: 3,
    session_index: 1,
    experience_level: "intermediate",
    target_count: 5,
    tool_changes: 1,
    fine_motor_ratio: "medium",
    workspace_constraint: "moderate",
    time_of_day: "morning",
    surgery_type: "laparoscopic"
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // When profile changes, sync experience_level
  useEffect(() => {
    if (selectedProfile?.grade) {
      const level = GRADE_TO_EXPERIENCE[selectedProfile.grade] || "intermediate";
      setFormData(p => ({ ...p, experience_level: level }));
    }
  }, [selectedProfileId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numFields = ["complexity_level", "booked_minutes", "session_index", "target_count", "tool_changes"];
    setFormData(p => ({ ...p, [name]: numFields.includes(name) ? parseInt(value) || 0 : value }));
  };

  const assessRisk = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Profile CRUD
  const handleSaveProfile = (profile) => {
    const now = Date.now();
    if (profile.id) {
      setProfiles(p => p.map(x => x.id === profile.id ? { ...profile, updatedAt: now } : x));
    } else {
      const newProfile = { ...profile, id: String(now), createdAt: now, updatedAt: now };
      setProfiles(p => [...p, newProfile]);
      setSelectedProfileId(newProfile.id);
    }
    setModalState(null);
  };

  const handleDeleteProfile = (id) => {
    if (!window.confirm("Are you sure you want to delete this profile?")) return;
    setProfiles(p => p.filter(x => x.id !== id));
    if (selectedProfileId === id) setSelectedProfileId("");
    setModalState(null);
  };

  return (
    <div className="app-wrapper">
      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <img
              src="/nhs-logo.png"
              alt="NHS"
              className="nhs-logo-img"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            <div className="nhs-badge" style={{ display: 'none' }}>NHS</div>
            <div>
              <h1 className="header-title">Surgical Training Risk Assessment</h1>
              <p className="header-subtitle">Operative scheduling & overrun prediction tool</p>
            </div>
          </div>
          <div className="header-tag">⚠️ Trial — Not for clinical use</div>
        </div>
      </header>

      <div className="main-grid">
        {/* ── LEFT: Input Panel ── */}
        <aside className="input-panel">

          {/* Surgeon Profile Module */}
          <div className="card profile-card">
            <div className="card-header">
              <h3 className="card-title">Surgeon Profile</h3>
              <button className="btn-add-profile" onClick={() => setModalState({ profile: null })}>
                + Add Profile
              </button>
            </div>

            <div className="profile-selector-row">
              <select
                className="form-control profile-select"
                value={selectedProfileId}
                onChange={e => setSelectedProfileId(e.target.value)}
              >
                <option value="">— Select a profile —</option>
                {profiles.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>

            {selectedProfile ? (
              <ProfileSummaryCard
                profile={selectedProfile}
                onEdit={() => setModalState({ profile: selectedProfile })}
              />
            ) : (
              <div className="profile-empty">
                <span className="profile-empty-icon">👤</span>
                <p>Select or create a surgeon profile to calibrate predictions.</p>
              </div>
            )}
          </div>

          {/* Training Parameters */}
          <div className="card params-card">
            <div className="card-header">
              <h3 className="card-title">Training Parameters</h3>
            </div>

            <div className="params-grid">
              <div className="input-group">
                <label className="input-label">Surgery Procedure</label>
                <ProcedureSearchInput
                  value={formData.surgery_procedure}
                  onChange={(val) => setFormData(p => ({ ...p, surgery_procedure: val }))}
                />
              </div>

              <div className="input-group">
                <label className="input-label">Surgery Type</label>
                <select className="form-control" name="surgery_type" value={formData.surgery_type} onChange={handleChange}>
                  <option value="open">Open Surgery</option>
                  <option value="laparoscopic">Laparoscopic</option>
                  <option value="robotic">Robotic Surgery</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">
                  Experience Level
                  {selectedProfile && <span className="auto-badge">auto</span>}
                </label>
                <select className="form-control" name="experience_level" value={formData.experience_level} onChange={handleChange}>
                  <option value="novice">Novice</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">Workspace Constraint</label>
                <select className="form-control" name="workspace_constraint" value={formData.workspace_constraint} onChange={handleChange}>
                  <option value="open">Open</option>
                  <option value="moderate">Moderate</option>
                  <option value="tight">Tight</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">Fine Motor Demands</label>
                <select className="form-control" name="fine_motor_ratio" value={formData.fine_motor_ratio} onChange={handleChange}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">Time of Day</label>
                <select className="form-control" name="time_of_day" value={formData.time_of_day} onChange={handleChange}>
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                  <option value="evening">Evening</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">Target Count (Reps)</label>
                <input className="form-control" type="number" min="1" name="target_count" value={formData.target_count} onChange={handleChange} />
              </div>

              <div className="input-group">
                <label className="input-label">Session Index (Fatigue)</label>
                <input className="form-control" type="number" min="1" name="session_index" value={formData.session_index} onChange={handleChange} />
              </div>

              <div className="input-group">
                <label className="input-label">Tool Changes</label>
                <input className="form-control" type="number" min="0" name="tool_changes" value={formData.tool_changes} onChange={handleChange} />
              </div>
            </div>

            {/* Complexity Slider */}
            <div className="input-group slider-group">
              <div className="slider-header">
                <label className="input-label">Complexity Level</label>
                <span className="range-value-badge">{formData.complexity_level} / 5</span>
              </div>
              <input type="range" min="1" max="5" className="range-slider" name="complexity_level" value={formData.complexity_level} onChange={handleChange} />
              <div className="range-labels">
                <span>Low</span><span>High</span>
              </div>
            </div>

            {/* Booked Minutes — highlighted */}
            <div className="input-group booked-group">
              <label className="input-label booked-label">⏱ Booked Duration (minutes)</label>
              <input className="form-control booked-input" type="number" min="5" name="booked_minutes" value={formData.booked_minutes} onChange={handleChange} />
            </div>

            <div className="btn-assess-wrapper">
              <button className="btn-assess" onClick={assessRisk} disabled={loading}>
                {loading ? (
                  <><span className="spinner" /> Analysing…</>
                ) : "Assess Training Risk"}
              </button>

              {error && (
                <div className="error-banner">
                  <strong>Error:</strong> {error}. Is the backend running on port 8000?
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* ── RIGHT: Output Panel ── */}
        <main className="output-panel">
          {result ? (
            <ResultsPanel result={result} bookedMinutes={formData.booked_minutes} />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <h3>No Assessment Yet</h3>
              <p>Configure training parameters on the left and click <strong>Assess Training Risk</strong> to generate a prediction.</p>
            </div>
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p><strong>⚠️ Trial Stage Disclaimer:</strong> This tool is in a pilot/testing phase. Predictions are for experimental logistics planning only and must not replace clinical judgement.</p>
        <p className="attribution">Designed by Zhen Wei Yap</p>
      </footer>

      {/* Profile Modal */}
      {modalState && (
        <ProfileModal
          profile={modalState.profile}
          onSave={handleSaveProfile}
          onDelete={handleDeleteProfile}
          onClose={() => setModalState(null)}
        />
      )}
    </div>
  );
}
