const API_BASE = "http://127.0.0.1:8000/api";

export async function apiFetch(path, options = {}) {
  const accessToken = localStorage.getItem("accessToken");

  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || JSON.stringify(data) || "Request failed");
  }

  return data;
}