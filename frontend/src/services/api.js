// frontend/src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE || ""; // same-origin in Render

async function handle(res) {
  if (!res.ok) {
    let detail = "";
    try { detail = await res.text(); } catch {}
    throw new Error(`${res.status} ${res.statusText} ${detail}`.trim());
  }
  return res.json();
}

export async function apiGet(path, opts = {}) {
  const res = await fetch(API_BASE + path, {
    method: "GET",
    headers: { Accept: "application/json" },
    // no cookies by default — avoids CORS complications
    credentials: opts.credentials ?? "same-origin",
    ...opts,
  });
  return handle(res);
}

export async function apiPost(path, body, opts = {}) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: opts.credentials ?? "include", // we do want cookies for auth flows
    body: JSON.stringify(body ?? {}),
    ...opts,
  });
  return handle(res);
}
