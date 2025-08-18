// frontend/src/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, auth } from "./services/api";

export default function Login() {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      let resp;
      if (mode === "signup") {
        resp = await api.signup(name.trim(), email.trim(), password);
      } else {
        resp = await api.login(email.trim(), password);
      }
      // backend returns { token, user: {...} }
      auth.setToken(resp.token);
      nav("/search");
    } catch (e) {
      setErr(e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 480, marginTop: 80 }}>
      <h2>SocialMediaRAG</h2>

      <div style={{ display: "flex", gap: 12, margin: "18px 0" }}>
        <button
          className={mode === "login" ? "btn btn-primary" : "btn"}
          onClick={() => setMode("login")}
          type="button"
        >
          Login
        </button>
        <button
          className={mode === "signup" ? "btn btn-primary" : "btn"}
          onClick={() => setMode("signup")}
          type="button"
        >
          Sign up
        </button>
      </div>

      <form onSubmit={onSubmit}>
        {mode === "signup" && (
          <div className="form-group" style={{ marginBottom: 12 }}>
            <label>Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="form-control"
              placeholder="Your name"
            />
          </div>
        )}

        <div className="form-group" style={{ marginBottom: 12 }}>
          <label>Email</label>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="form-control"
            type="email"
            placeholder="you@example.com"
          />
        </div>

        <div className="form-group" style={{ marginBottom: 18 }}>
          <label>Password</label>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="form-control"
            type="password"
            placeholder="••••••••"
          />
        </div>

        {err && (
          <div style={{ color: "salmon", marginBottom: 12 }}>{err}</div>
        )}

        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Please wait…" : mode === "signup" ? "Create account" : "Login"}
        </button>
      </form>
    </div>
  );
}
