// frontend/src/pages/Search.jsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import ResultCard from "../components/ResultCard.jsx";

export default function Search() {
  const [q, setQ] = useState("rag basics");
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [data, setData] = useState({
    query: "",
    corpus: [],
    rag: [], // some backends use "rag" instead of "corpus"
    social: { youtube: [], reddit: [], twitter: [] },
    notes: null,
  });

  // fetch session (optional)
  useEffect(() => {
    api.auth
      .me()
      .then(setMe)
      .catch(() => setMe(null));
  }, []);

  const onSearch = async (e) => {
    e?.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setErr("");
    try {
      const res = await api.search(q.trim());
      // normalize the shape so UI is resilient
      const social = res.social || {
        youtube: res.youtube || [],
        reddit: res.reddit || [],
        twitter: res.twitter || [],
      };
      setData({
        query: res.query ?? q.trim(),
        corpus: res.corpus ?? res.rag ?? [],
        rag: res.rag ?? res.corpus ?? [],
        social,
        notes: res.notes ?? null,
      });
    } catch (e) {
      setErr(String(e?.message || e));
      setData((d) => ({ ...d, corpus: [], rag: [], social: { youtube: [], reddit: [], twitter: [] } }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // auto-run first search on load
    onSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const Section = ({ title, children }) => (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ margin: "12px 0" }}>{title}</h3>
      {children}
    </div>
  );

  const renderList = (items) => {
    if (!items?.length) return <div style={{ opacity: 0.7 }}>No results.</div>;
    return (
      <div style={{ display: "grid", gap: 12 }}>
        {items.map((it, idx) => (
          <ResultCard key={idx} item={it} />
        ))}
      </div>
    );
  };

  return (
    <div style={{ padding: 24, maxWidth: 950, margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>SocialMediaRAG</h1>
        <div style={{ marginLeft: "auto", opacity: 0.85 }}>
          {me ? (
            <span>Signed in as <strong>{me.username || "user"}</strong></span>
          ) : (
            <span>Not signed in</span>
          )}
        </div>
      </header>

      <form onSubmit={onSearch} style={{ display: "flex", gap: 8 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search social + local corpus…"
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid var(--border, #333)",
            background: "var(--bgElev, #0f172a)",
            color: "inherit",
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 16px",
            borderRadius: 8,
            border: "1px solid transparent",
            background: loading ? "#3b3b3b" : "#2563eb",
            color: "white",
            cursor: loading ? "default" : "pointer",
          }}
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {err && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            borderRadius: 8,
            background: "rgba(239,68,68,.12)",
            border: "1px solid rgba(239,68,68,.35)",
          }}
        >
          <strong>Search failed:</strong> {err}
        </div>
      )}

      <div style={{ marginTop: 20, opacity: 0.8 }}>
        Query: <code>{data.query || q}</code>
      </div>

      {!!data.notes && (
        <div
          style={{
            marginTop: 12,
            padding: 10,
            borderRadius: 8,
            border: "1px dashed var(--border, #333)",
            background: "var(--bgNote, #0b1223)",
            opacity: 0.9,
          }}
        >
          {String(data.notes)}
        </div>
      )}

      <Section title="RAG (local corpus)">
        {renderList((data.corpus?.length ? data.corpus : data.rag) || [])}
      </Section>

      <Section title="Social Sources">
        <div style={{ display: "grid", gap: 20 }}>
          <div>
            <h4 style={{ margin: "0 0 8px" }}>YouTube</h4>
            {renderList(data.social?.youtube || [])}
          </div>
          <div>
            <h4 style={{ margin: "0 0 8px" }}>Reddit</h4>
            {renderList(data.social?.reddit || [])}
          </div>
          <div>
            <h4 style={{ margin: "0 0 8px" }}>Twitter/X</h4>
            {renderList(data.social?.twitter || [])}
          </div>
        </div>
      </Section>
    </div>
  );
}

