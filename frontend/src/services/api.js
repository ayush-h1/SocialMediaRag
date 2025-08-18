// frontend/src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE_URL || ""; // same-origin by default

async function http(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} – ${text}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const auth = {
  login: (username, password) =>
    http("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  me: () => http("/api/auth/me"),
  logout: () => http("/api/auth/logout", { method: "POST" }),
};

export const search = (q) => http(`/api/search?q=${encodeURIComponent(q)}`);

const api = { http, auth, search };
export default api;
