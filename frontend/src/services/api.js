// Minimal API client for the app

const API_BASE =
  import.meta.env?.VITE_API_BASE ||
  (typeof window !== "undefined" ? `${window.location.origin}/api` : "/api");

function getToken() {
  return localStorage.getItem("token") || "";
}

async function request(path, { method = "GET", headers = {}, body } = {}) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    // try to surface server message
    let msg = `${res.status} ${res.statusText}`;
    try {
      const j = await res.json();
      if (j?.detail) msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
      if (j?.message) msg = j.message;
    } catch (_) {}
    throw new Error(msg);
  }

  // some endpoints (like /health) may return empty body
  const text = await res.text();
  return text ? JSON.parse(text) : {};
}

const api = {
  auth: {
    async login(username, password) {
      const data = await request("/auth/login", {
        method: "POST",
        body: { username, password },
      });
      if (data?.access_token) localStorage.setItem("token", data.access_token);
      return data;
    },
    async signup(username, password) {
      const data = await request("/auth/signup", {
        method: "POST",
        body: { username, password },
      });
      // optionally auto-login if backend returns a token
      if (data?.access_token) localStorage.setItem("token", data.access_token);
      return data;
    },
    async me() {
      return request("/auth/me", { method: "GET" });
    },
    logout() {
      localStorage.removeItem("token");
    },
  },

  async search(q) {
    const params = new URLSearchParams({ q });
    return request(`/search?${params.toString()}`, { method: "GET" });
  },

  async health() {
    return request("/health", { method: "GET" });
  },
};

export default api;

