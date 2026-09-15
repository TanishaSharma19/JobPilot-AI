import { useEffect, useState } from "react";
import "./App.css";
import "./Workspace.css";

const loadingStages = [
  "Reading job description",
  "Extracting requirements",
  "Comparing your skills",
  "Identifying skill gaps",
  "Building your action plan",
];
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";;

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [resetToken, setResetToken] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      const endpoint = mode === "forgot" ? "/auth/forgot-password" : mode === "reset" ? "/auth/reset-password" : `/auth/${mode}`;
      const body = mode === "forgot" ? { email: form.email } : mode === "reset" ? { token: resetToken, password: form.password } : form;
      const response = await fetch(`${API_BASE}${endpoint}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to continue");
      if (mode === "forgot") {
        setMessage(data.message);
        if (data.reset_token) {
          setResetToken(data.reset_token);
          setMode("reset");
        }
      } else if (mode === "reset") {
        setMessage(data.message);
        setMode("login");
        setForm({ name: "", email: form.email, password: "" });
      } else {
        localStorage.setItem("jobpilot_token", data.token);
        onAuthenticated(data.user, data.token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const title = mode === "login" ? "Welcome back." : mode === "register" ? "Start your career journey." : mode === "forgot" ? "Reset your password." : "Choose a new password.";
  return (
    <main className="auth-page">
      <section className="auth-card panel">
        <a className="brand auth-brand" href="#top"><span className="brand-mark">✦</span><span><strong>JobAI Pilot</strong><small>AI Career Assistant</small></span></a>
        <div className="auth-intro"><span className="eyebrow">Your career command center</span><h1>{title}</h1><p>{mode === "forgot" ? "Enter your email and we will prepare a password reset." : "Keep your analyses and career plans in one workspace."}</p></div>
        <form onSubmit={submit}>
          {mode === "register" && <label className="auth-field"><span>Full name</span><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>}
          {mode !== "reset" && <label className="auth-field"><span>Email address</span><input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>}
          {mode === "reset" && <label className="auth-field"><span>Reset token</span><input required value={resetToken} onChange={(e) => setResetToken(e.target.value)} /></label>}
          {(mode === "login" || mode === "register" || mode === "reset") && <label className="auth-field"><span> {mode === "reset" ? "New password" : "Password"}</span><input required minLength={8} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>}
          {message && <p className="auth-message">{message}</p>}
          {error && <p className="auth-error">{error}</p>}
          <button className="primary-button auth-submit" disabled={submitting}>{submitting ? "Please wait..." : mode === "login" ? "Sign in  ↗" : mode === "register" ? "Create account  ↗" : mode === "forgot" ? "Send reset instructions" : "Update password"}</button>
        </form>
        <div className="auth-links">
          {mode === "login" && <button onClick={() => { setMode("forgot"); setError(""); setMessage(""); }}>Forgot password?</button>}
          {mode !== "register" && <button onClick={() => { setMode("register"); setError(""); setMessage(""); }}>Create an account</button>}
          {mode !== "login" && <button onClick={() => { setMode("login"); setError(""); setMessage(""); }}>Back to sign in</button>}
        </div>
      </section>
    </main>
  );
}

function SectionHeading({ eyebrow, title, icon }) {
  return (
    <div className="section-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{icon} {title}</h2>
    </div>
  );
}

function MetricCard({ label, value, icon, tone }) {
  return (
    <article className={`metric-card ${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </article>
  );
}

function ScoreRing({ score }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let frame;
    const start = performance.now();
    const animate = (now) => {
      const progress = Math.min((now - start) / 1200, 1);
      setDisplayScore(Math.round(score * (1 - Math.pow(1 - progress, 3))));
      if (progress < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  return (
    <div className="score-ring" style={{ "--score": `${displayScore * 3.6}deg` }}>
      <div className="score-ring-inner">
        <strong>{displayScore}%</strong>
        <span>Good Match</span>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <section className="loading-state panel" aria-live="polite">
      <div className="loading-orbit"><span>✦</span></div>
      <span className="eyebrow">Agent in progress</span>
      <h2>Analyzing your opportunity...</h2>
      <p>JobAI Pilot is connecting the dots across this role and your experience.</p>
      <div className="stage-list">
        {loadingStages.map((stage, index) => (
          <div className={`stage stage-${index}`} key={stage}>
            <span className="stage-mark">{index < 2 ? "✓" : index === 2 ? "◌" : "○"}</span>
            {stage}
          </div>
        ))}
      </div>
    </section>
  );
}

function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [candidateProfile, setCandidateProfile] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("jobpilot_token"));
  const [authChecking, setAuthChecking] = useState(() => Boolean(localStorage.getItem("jobpilot_token")));

  useEffect(() => {
    if (!token) {
      return;
    }
    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("Session expired")))
      .then((data) => setUser(data.user))
      .catch(() => { localStorage.removeItem("jobpilot_token"); setToken(null); setUser(null); })
      .finally(() => setAuthChecking(false));
  }, [token]);

  const analyzeJob = async () => {
    if (!jobDescription.trim() || !candidateProfile.trim()) {
      setError("Please enter both job description and candidate profile.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const response = await fetch(`${API_BASE}/analyze-job`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          job_description: jobDescription,
          candidate_profile: candidateProfile,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze job.");
      }

      const data = await response.json();

      setAnalysis(data.analysis);
    } catch (err) {
      console.error(err);
      setError(
        "Something went wrong. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearJob = () => {
    setJobDescription("");
    setError("");
  };

  const renderResults = () => {
    const score = analysis.match_score ?? 70;
    const requirements = analysis.job_requirements ?? [];
    const matches = analysis.strong_matches ?? [];
    const gaps = analysis.skill_gaps ?? [];
    const plan = analysis.action_plan ?? [];
    return (
      <div className="results-shell">
        <div className="results-intro">
          <div>
            <span className="eyebrow">Analysis complete</span>
            <h2>Your career strategy, clarified.</h2>
          </div>
          <span className="success-pill">● Ready to act</span>
        </div>

        <div className="metrics-grid">
          <MetricCard label="Match Score" value={`${score}%`} icon="◔" tone="blue" />
          <MetricCard label="Skills Matched" value={matches.length || 8} icon="✓" tone="green" />
          <MetricCard label="Skill Gaps" value={gaps.length || 2} icon="!" tone="amber" />
          <MetricCard label="Experience" value="Verify" icon="◌" tone="violet" />
        </div>

        <section className="score-panel panel">
          <div className="score-copy">
            <SectionHeading eyebrow="Your advantage" title="Match score" icon="◔" />
            <p className="score-lede">You meet most of the technical requirements, but your professional experience needs stronger evidence.</p>
            <div className="score-legend"><span className="legend-dot" /> Strong technical alignment <b>{score}%</b></div>
          </div>
          <ScoreRing score={score} />
        </section>

        <div className="dashboard-grid">
          <section className="panel requirements-panel">
            <SectionHeading eyebrow="Role fit" title="Job Requirements" icon="▣" />
            <div className="requirement-list">
              {requirements.map((item, index) => {
                const preferred = /typescript|next|preferred/i.test(item);
                return <div className={`requirement-row ${preferred ? "preferred" : index === requirements.length - 1 ? "partial" : "matched"}`} key={`${item}-${index}`}><span>{preferred ? "★" : "✓"}</span><p>{item}</p><small>{preferred ? "Preferred" : "Strong match"}</small></div>;
              })}
            </div>
          </section>

          <section className="panel matches-panel">
            <SectionHeading eyebrow="Your edge" title="Your Strong Matches" icon="✦" />
            <div className="skill-cloud">
              {matches.map((item, index) => <span className="skill-chip" key={`${item}-${index}`}><i>✓</i>{item}</span>)}
            </div>
            <div className="match-note"><span>✦</span><p>Your profile has a strong keyword foundation for this role.</p></div>
          </section>
        </div>

        <section className="panel gaps-panel">
          <SectionHeading eyebrow="Where to focus" title="Skill Gaps" icon="⚠" />
          <div className="gaps-list">
            {gaps.map((gap, index) => <div className="gap-item" key={`${gap}-${index}`}><div className="gap-icon">!</div><div><h3>{gap.split(":")[0]}</h3><p>{gap}</p><span>Suggested improvement · Add clear evidence and measurable outcomes.</span></div><b>High impact</b></div>)}
          </div>
        </section>

        <section className="panel action-panel">
          <SectionHeading eyebrow="Your next moves" title="Your AI Action Plan" icon="◎" />
          <div className="timeline">
            {plan.map((step, index) => <div className="timeline-item" key={`${step}-${index}`}><span className="timeline-number">{String(index + 1).padStart(2, "0")}</span><div><h3>{step.split(":")[0]}</h3><p>{step.includes(":") ? step.split(":").slice(1).join(":").trim() : "Align your evidence and language with the role to make your application more compelling."}</p></div></div>)}
          </div>
        </section>

        <section className="advice-panel panel"><div className="advice-icon">✦</div><div><span className="eyebrow">Agent insight</span><h2>AI Application Advice</h2><p>{analysis.application_advice}</p></div></section>
      </div>
    );
  };

  if (authChecking) return <div className="auth-loading">Loading your workspace...</div>;
  if (!user) return <AuthScreen onAuthenticated={(authenticatedUser, authenticatedToken) => { setUser(authenticatedUser); setToken(authenticatedToken); }} />;

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand-mark">✦</span><span><strong>JobAI Pilot</strong><small>AI Career Assistant</small></span></a>
        <div className="top-actions"><button className="icon-button" aria-label="Notifications">♢<span /></button><button className="avatar" title="Sign out" onClick={() => { localStorage.removeItem("jobpilot_token"); setToken(null); setUser(null); }}> {user.name?.slice(0, 2).toUpperCase() || "JD"} </button></div>
      </header>

      <main id="top" className="container">
        <>
          <section className="hero-copy" id="analyze"><div className="hero-glow" /><span className="eyebrow">AI career intelligence <span className="live-dot" /> Live analysis</span><h1>Turn Any Job Description<br /><em>Into Your Career Strategy</em></h1><p>AI-powered job analysis that instantly identifies your strengths, skill gaps, and the actions you should take to improve your application.</p></section>
          <section className="input-grid panel">
          <div className="input-card"><div className="input-header"><div><span className="eyebrow">Step 01</span><h2>Job Description</h2></div><span className="input-icon">▤</span></div><textarea aria-label="Job Description" placeholder="Paste the job description here..." value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} /><div className="input-footer"><span>{jobDescription.length} characters</span><div><button className="text-button" onClick={() => navigator.clipboard?.readText().then(setJobDescription)}>↙ Paste</button><button className="text-button" onClick={clearJob}>Clear</button></div></div></div>
          <div className="input-card"><div className="input-header"><div><span className="eyebrow">Step 02</span><h2>Candidate Profile</h2></div><span className="input-icon">◎</span></div><textarea aria-label="Candidate Profile" placeholder="Tell us about your skills, experience, and projects..." value={candidateProfile} onChange={(e) => setCandidateProfile(e.target.value)} /></div>
          </section>
          <div className="analyze-row"><button className="primary-button analyze-button" onClick={analyzeJob} disabled={loading}>{loading ? "Analyzing opportunity..." : "Analyze Job  ↗"}</button>{error && <p className="error" role="alert">{error}</p>}</div>
          {loading && <LoadingState />}
          {!loading && !analysis && <section className="empty-state panel"><div className="empty-art"><span>✦</span><i /><i /><i /></div><span className="eyebrow">Your next opportunity awaits</span><h2>Ready to analyze your next opportunity?</h2><p>Paste a job description and your candidate profile to get an AI-powered career analysis.</p></section>}
          {!loading && analysis && renderResults()}
        </>
      </main>
    </div>
  );
}

export default App;