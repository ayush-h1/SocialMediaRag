// frontend/src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE || "";

// tiny fetch wrapper
async function http(method, path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "content-type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${text}`);
  }
  // try json, fall back to text
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

const api = {
  get: (path) => http("GET", path),
  post: (path, body) => http("POST", path, body),
};

export default api;

