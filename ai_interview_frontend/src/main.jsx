import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_API_BASE_URL);
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const [createdUser, setCreatedUser] = useState(null);
  const [createdInterview, setCreatedInterview] = useState(null);
  const [userInterviews, setUserInterviews] = useState(null);
  const [interviewDetails, setInterviewDetails] = useState(null);

  async function loadInterviewDetails(interviewId) {
    const data = await apiGet(
      apiBaseUrl,
      `/interviews/${encodeURIComponent(interviewId)}/details`
    );
    setInterviewDetails(data);
    return data;
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Interview System</h1>
          <p>Frontend for testing the FastAPI backend workflow.</p>
        </div>
      </header>

      <section className="panel">
        <h2>Backend</h2>
        <label className="label">
          API Base URL
          <input
            value={apiBaseUrl}
            onChange={(event) => setApiBaseUrl(event.target.value)}
          />
        </label>
        <button
          onClick={async () => {
            setError("");
            try {
              const data = await apiGet(apiBaseUrl, "/health");
              setHealth(data);
            } catch (err) {
              setError(err.message);
            }
          }}
        >
          Test /health
        </button>
        {health && <JsonBlock title="Health" data={health} />}
      </section>

      {error && <div className="error">{error}</div>}

      <div className="grid">
        <CreateUser
          apiBaseUrl={apiBaseUrl}
          onCreated={setCreatedUser}
          onError={setError}
        />
        <CreateInterview
          apiBaseUrl={apiBaseUrl}
          defaultUserId={createdUser?.user_id || ""}
          onCreated={(interview) => {
            setCreatedInterview(interview);
            setInterviewDetails(null);
          }}
          onError={setError}
        />
      </div>

      <div className="grid">
        <LoadUserInterviews
          apiBaseUrl={apiBaseUrl}
          defaultUserId={createdUser?.user_id || createdInterview?.user_id || ""}
          onLoaded={setUserInterviews}
          onError={setError}
        />
        <LoadInterviewDetails
          apiBaseUrl={apiBaseUrl}
          defaultInterviewId={createdInterview?.interview_id || ""}
          onLoaded={setInterviewDetails}
          onError={setError}
        />
      </div>

      {createdUser && <JsonBlock title="Created User" data={createdUser} />}
      {createdInterview && (
        <JsonBlock title="Created Interview" data={createdInterview} />
      )}
      {userInterviews && (
        <JsonBlock title="User Interviews" data={userInterviews} />
      )}

      {interviewDetails && (
        <InterviewDetails
          apiBaseUrl={apiBaseUrl}
          details={interviewDetails}
          onError={setError}
          onRefresh={() => loadInterviewDetails(interviewDetails.interview.interview_id)}
        />
      )}
    </div>
  );
}

function CreateUser({ apiBaseUrl, onCreated, onError }) {
  const [email, setEmail] = useState("tony@example.com");
  const [name, setName] = useState("Yicheng Teng");
  const [loading, setLoading] = useState(false);

  async function submit() {
    onError("");
    setLoading(true);
    try {
      const data = await apiPost(apiBaseUrl, "/users", { email, name });
      onCreated(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>1. Create User</h2>
      <label className="label">Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
      <label className="label">Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
      <button onClick={submit} disabled={loading}>{loading ? "Creating..." : "Create User"}</button>
    </section>
  );
}

function CreateInterview({ apiBaseUrl, defaultUserId, onCreated, onError }) {
  const [userId, setUserId] = useState(defaultUserId);
  const [targetRole, setTargetRole] = useState("backend engineer");
  const [difficulty, setDifficulty] = useState("medium");
  const [types, setTypes] = useState(["coding", "behavioral"]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultUserId && !userId) setUserId(defaultUserId);
  }, [defaultUserId, userId]);

  function toggleType(type) {
    setTypes((current) =>
      current.includes(type)
        ? current.filter((item) => item !== type)
        : [...current, type]
    );
  }

  async function submit() {
    onError("");
    setLoading(true);
    try {
      const data = await apiPost(apiBaseUrl, "/interviews", {
        user_id: userId,
        interview_types: types,
        target_role: targetRole,
        difficulty,
      });
      onCreated(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>2. Create Interview</h2>
      <label className="label">User ID<input value={userId} onChange={(e) => setUserId(e.target.value)} /></label>
      <label className="label">Target Role<input value={targetRole} onChange={(e) => setTargetRole(e.target.value)} /></label>
      <label className="label">Difficulty
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option value="easy">easy</option>
          <option value="medium">medium</option>
          <option value="hard">hard</option>
        </select>
      </label>
      <div className="checkboxGroup">
        {['coding', 'behavioral', 'system_design'].map((type) => (
          <label key={type}>
            <input type="checkbox" checked={types.includes(type)} onChange={() => toggleType(type)} />
            {type}
          </label>
        ))}
      </div>
      <button onClick={submit} disabled={loading}>{loading ? "Creating..." : "Create Interview"}</button>
      <p className="hint">After creating interview, run the question generation worker, then load details.</p>
    </section>
  );
}

function LoadUserInterviews({ apiBaseUrl, defaultUserId, onLoaded, onError }) {
  const [userId, setUserId] = useState(defaultUserId);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultUserId && !userId) setUserId(defaultUserId);
  }, [defaultUserId, userId]);

  async function load() {
    onError("");
    setLoading(true);
    try {
      const data = await apiGet(apiBaseUrl, `/interviews/${encodeURIComponent(userId)}/interviews`);
      onLoaded(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>3. Get Interviews by User</h2>
      <label className="label">User ID<input value={userId} onChange={(e) => setUserId(e.target.value)} /></label>
      <button onClick={load} disabled={loading}>{loading ? "Loading..." : "Load Interviews"}</button>
    </section>
  );
}

function LoadInterviewDetails({ apiBaseUrl, defaultInterviewId, onLoaded, onError }) {
  const [interviewId, setInterviewId] = useState(defaultInterviewId);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultInterviewId && !interviewId) setInterviewId(defaultInterviewId);
  }, [defaultInterviewId, interviewId]);

  async function load() {
    onError("");
    setLoading(true);
    try {
      const data = await apiGet(apiBaseUrl, `/interviews/${encodeURIComponent(interviewId)}/details`);
      onLoaded(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>4. Get Interview Details</h2>
      <label className="label">Interview ID<input value={interviewId} onChange={(e) => setInterviewId(e.target.value)} /></label>
      <button onClick={load} disabled={loading}>{loading ? "Loading..." : "Load Details"}</button>
    </section>
  );
}

function InterviewDetails({ apiBaseUrl, details, onRefresh, onError }) {
  const interview = details.interview;
  const questions = details.questions || [];

  return (
    <section className="panel fullWidth">
      <div className="sectionHeader">
        <div>
          <h2>Interview Details</h2>
          <p><strong>ID:</strong> {interview?.interview_id}</p>
          <p><strong>Status:</strong> {interview?.status}</p>
        </div>
        <button onClick={async () => { try { await onRefresh(); } catch (err) { onError(err.message); } }}>Refresh</button>
      </div>

      {questions.length === 0 && <p className="hint">No questions yet. Run question_generation_listener first.</p>}

      {questions.map((item, index) => (
        <QuestionCard
          key={item.question?.question_id || index}
          apiBaseUrl={apiBaseUrl}
          interviewId={interview?.interview_id}
          item={item}
          onRefresh={onRefresh}
          onError={onError}
        />
      ))}
    </section>
  );
}

function QuestionCard({ apiBaseUrl, interviewId, item, onRefresh, onError }) {
  const question = item.question;
  const answer = item.answer;
  const evaluation = item.evaluation;
  const [answerText, setAnswerText] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitAnswer() {
    onError("");
    setLoading(true);
    try {
      await apiPost(
        apiBaseUrl,
        `/interviews/${encodeURIComponent(interviewId)}/questions/${encodeURIComponent(question.question_id)}/answer`,
        { answer: answerText }
      );
      setAnswerText("");
      await onRefresh();
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="questionCard">
      <div className="badges">
        <span className="badge">{question?.type}</span>
        <span className="badge">order {question?.question_order}</span>
        <span className="badge">{question?.status}</span>
      </div>
      <h3>{question?.question}</h3>

      {question?.expected_signals?.length > 0 && (
        <div>
          <strong>Expected Signals</strong>
          <ul>{question.expected_signals.map((x, i) => <li key={i}>{x}</li>)}</ul>
        </div>
      )}

      {!answer && (
        <div className="answerBox">
          <label className="label">Submit Answer
            <textarea rows="5" value={answerText} onChange={(e) => setAnswerText(e.target.value)} placeholder="Type answer here..." />
          </label>
          <button onClick={submitAnswer} disabled={loading || !answerText.trim()}>{loading ? "Submitting..." : "Submit Answer"}</button>
          <p className="hint">After submitting, run answer_evaluation_listener, then refresh.</p>
        </div>
      )}

      {answer && (
        <div className="resultBox">
          <h4>Answer</h4>
          <p>{answer.answer_text}</p>
          <p><strong>Status:</strong> {answer.status}</p>
        </div>
      )}

      {evaluation ? (
        <div className="evaluationBox">
          <h4>Evaluation</h4>
          <p><strong>Score:</strong> {evaluation.score}</p>
          <p>{evaluation.feedback}</p>
          {evaluation.strengths?.length > 0 && <List title="Strengths" items={evaluation.strengths} />}
          {evaluation.improvements?.length > 0 && <List title="Improvements" items={evaluation.improvements} />}
          {evaluation.follow_up_questions?.length > 0 && <List title="Follow-up Questions" items={evaluation.follow_up_questions} />}
        </div>
      ) : answer ? (
        <p className="hint">Evaluation not ready yet.</p>
      ) : null}
    </div>
  );
}

function List({ title, items }) {
  return <div><strong>{title}</strong><ul>{items.map((x, i) => <li key={i}>{x}</li>)}</ul></div>;
}

function JsonBlock({ title, data }) {
  return <section className="panel fullWidth"><h2>{title}</h2><pre>{JSON.stringify(data, null, 2)}</pre></section>;
}

async function apiGet(apiBaseUrl, path) {
  const response = await fetch(`${trimSlash(apiBaseUrl)}${path}`);
  return parseResponse(response);
}

async function apiPost(apiBaseUrl, path, body) {
  const response = await fetch(`${trimSlash(apiBaseUrl)}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

async function parseResponse(response) {
  const text = await response.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }

  if (!response.ok) {
    const detail = typeof data === "object" && data !== null ? data.detail || JSON.stringify(data) : data || response.statusText;
    throw new Error(`${response.status}: ${detail}`);
  }
  return data;
}

function trimSlash(value) {
  return value.replace(/\/$/, "");
}

createRoot(document.getElementById("root")).render(<App />);
