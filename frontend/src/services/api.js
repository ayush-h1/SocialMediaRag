// frontend/src/services/api.js
const API_BASE =
  (import.meta.env.VITE_API_BASE || "").replace(/\/$/, ""); // empty => same-origin

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    credentials: "include",
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { message: text };
  }

  if (!res.ok) {
    const msg =
      data?.detail || data?.message || `${res.status} ${res.statusText}`;
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export const api = {
  // auth
  login: (email, password) =>
    request("/api/auth/login", { method: "POST", body: { email, password } }),
  signup: (name, email, password) =>
    request("/api/auth/signup", {
      method: "POST",
      body: { name, email, password },
    }),
  me: (token) => request("/api/auth/me", { token }),

  // app features
  search: (q, token) =>
    request(`/api/search?q=${encodeURIComponent(q)}`, { token }),
  ingestRss: (url, token) =>
    request("/api/ingest/rss", { method: "POST", body: { url }, token }),
  trends: () => request("/api/trends"),
};

export const auth = {
  getToken() {
    return localStorage.getItem("token") || "";
  },
  setToken(t) {
    localStorage.setItem("token", t);
  },
  logout() {
    localStorage.removeItem("token");
  },
  isLoggedIn() {
    return !!localStorage.getItem("token");
  },
};
