
// refreshes teh access token, checks post response at url, multi-try logic approached below
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refreshToken");
  if (!refreshToken) {
    throw new Error("No refresh token");
  }

  const res = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!res.ok) {
    throw new Error("Refresh failed");
  }

  const data = await res.json();
  // SimpleJWT returns: { access: "new_access_token" }
  localStorage.setItem("accessToken", data.access);
  return data.access;
}


// wrapper for the above function, neve rto call above function directly, always use this one
export async function authFetch(url, options = {}) {
  let accessToken = localStorage.getItem("accessToken");

  const makeRequest = (token) => {
    const headers = {
      ...(options.headers || {}),
    };

    // Always add Authorization if we have a token
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Only set Content-Type: application/json if body is NOT FormData
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    return fetch(url, {
      ...options,
      headers,
    });
  };

  // First attempt with current access token
  let res = await makeRequest(accessToken);

  if (res.status === 401) {
    try {
      // Try to refresh and retry once
      const newToken = await refreshAccessToken();
      res = await makeRequest(newToken);
    } catch (err) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      return res;
    }
  }

  return res;
}