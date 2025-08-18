import React, { useState } from "react";
import api from "../services/api"; // <-- NOTE: ../services/api (not ./services)

export default function Login() {
  const [mode, setMode] = useState("login"); // 'login' | 'signup'
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");

  const submit = async (e) => {
    e?.preventDefault();
    setErr("");
    setOk("");
    if (!username || !password) {
      setErr("Please enter username and password.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "signup") {
        await api.auth.signup(username, password);
        setOk("Account created. You can use the app now.");
      } else {
        await api.auth.login(username, password);
        setOk("Logged in. You can use the app now.");
      }
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", padding: 24 }}>
      <h1 style={{ marginBottom: 8 }}>SocialMediaRAG</h1>
      <div style={{ marginBottom: 16, opacity: 0.85 }}>
        {mode === "login" ? "Sign in" : "Create an account"}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button
          type="button"
          onClick={() => setMode("login")}
          disabled={busy}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #333",
            background: mode === "login" ? "#2563eb" : "transparent",
            color: mode === "login" ? "#fff" : "inherit",
            cursor: busy ? "default" : "pointer",
          }}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => setMode("signup")}
          disabled={busy}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #333",
            background: mode === "signup" ? "#2563eb" : "transparent",
            color: mode === "signup" ? "#fff" : "inherit",
            cursor: busy ? "default" : "pointer",
          }}
        >
          Sign Up
        </button>
      </div>

      <form onSubmit={submit} style={{ display: "grid", gap: 10 }}>
        <input
          autoComplete="username"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={busy}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #333",
            background: "var(--bgElev, #0f172a)",
            color: "inherit",
          }}
        />
        <input
          type="password"
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={busy}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #333",
            background: "var(--bgElev, #0f172a)",
            color: "inherit",
          }}
        />

        <button
          type="submit"
          disabled={busy}
          style={{
            marginTop: 6,
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid transparent",
            background: busy ? "#3b3b3b" : "#2563eb",
            color: "white",
            cursor: busy ? "default" : "pointer",
          }}
        >
          {busy ? "Please wait…" : mode === "login" ? "Login" : "Create account"}
        </button>
      </form>

      {err && (
        <div
          style={{
            marginTop: 14,
            padding: 10,
            borderRadius: 8,
            background: "rgba(239,68,68,.12)",
            border: "1px solid rgba(239,68,68,.35)",
          }}
        >
          {err}
        </div>
      )}
      {ok && (
        <div
          style={{
            marginTop: 14,
            padding: 10,
            borderRadius: 8,
            background: "rgba(34,197,94,.12)",
            border: "1px solid rgba(34,197,94,.35)",
          }}
        >
          {ok}
        </div>
      )}
    </div>
  );
}
