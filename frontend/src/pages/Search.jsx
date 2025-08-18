// frontend/src/Search.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, auth } from "./services/api";
import ResultCard from "./components/ResultCard.jsx";

export default function Search() {
  const [q, setQ] = useState("rag basics");
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [context, setContext] = useState([]);
  const [social, setSocial] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    const token = auth.getToken();
    if (!token) return;
    api.me(token)
      .then(setMe)
      .catch(() => {
        // invalid token -> clear
        auth.logout();
        setMe(null);
      });
  }, []);

  async function doSearch(e) {
    e?.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const token = auth.getToken() || undefined;
      const r = await api.search(q, token);
      setAnswer(r.answer || "");
      setContext(r.context || []);
      setSocial(r.social || []);
    } catch (e) {
      setErr(e.message || "Search failed");
      setAnswer("");
      setContext([]);
      setSocial([]);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    auth.logout();
    setMe(null);
  }

  return (
    <div className="container" style={{ marginTop: 40 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Search</h2>
        <div>
          {me ? (
            <>
              <span style={{ marginRight: 8 }}>Hi, {me.name || me.email}</span>
              <button className="btn" onClick={logout}>Logout</button>
            </>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </div>
      </div>

      <form onSubmit={doSearch} style={{ display: "flex", gap: 10 }}>
        <input
          className="form-control"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask about your social corpus…"
        />
        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {err && <div style={{ color: "salmon", marginTop: 12 }}>{err}</div>}

      <div style={{ marginTop: 24 }}>
        <h4>RAG (local corpus)</h4>
        {answer ? <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p> : <p>No answer yet.</p>}
        {context?.length ? (
          <>
            <h5>Context</h5>
            {context.map((c, i) => (
              <ResultCard key={i} item={c} />
            ))}
          </>
        ) : null}
      </div>

      <div style={{ marginTop: 24 }}>
        <h4>Social Sources</h4>
        {social?.length ? (
          social.map((s, i) => <ResultCard key={i} item={s} />)
        ) : (
          <p>Nothing yet.</p>
        )}
      </div>
    </div>
  );
}
