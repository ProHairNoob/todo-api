/*
 * Shared helpers for the Todo frontend.
 *
 * Auth model (verified against the live backend, see README-frontend.md):
 *   - POST /register and POST /login return {token, user_id}.
 *   - Every /todos* request must send:  Authorization: <token>
 *     (the RAW token — no "Bearer " prefix; todo.py compares the whole
 *     header value against the stored token, confirmed against the running API).
 *   - The token is owned by the browser: localStorage, attached manually
 *     to every request. There is no cookie/session on the server side.
 *
 * Route map (once wired — see the WIRING REQUIRED section of the README):
 *   GET  /            -> login page   (index.html)
 *   GET  /register    -> register page (register.html)
 *   GET  /dashboard   -> todo dashboard (todos.html)
 *   (GET /todos is already the JSON API — the HTML dashboard intentionally
 *   lives at a different path, /dashboard, so it never collides with it.)
 */

const TODO = (() => {
  const TOKEN_KEY = "todo_token";
  const ROUTES = { login: "/", register: "/register", dashboard: "/dashboard" };

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  /**
   * Minimal fetch wrapper for this API.
   * - JSON in, JSON out (except DELETE, which returns 204 with no body).
   * - Adds the raw-token Authorization header automatically when auth=true.
   * - On a 401 for an authenticated call, clears the token and bounces to
   *   login rather than surfacing a generic error (per the spec's 401 handling).
   *
   * Returns { ok, status, data } — never throws for a normal HTTP error
   * response, only for a genuine network failure (caller shows a message).
   */
  async function api(path, { method = "GET", body, auth = true } = {}) {
    const headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth) {
      const token = getToken();
      if (!token) {
        clearToken();
        window.location.href = ROUTES.login;
        return { ok: false, status: 401, data: { detail: "Unauthorized" } };
      }
      headers["Authorization"] = token; // raw token, no "Bearer " prefix
    }

    let res;
    try {
      res = await fetch(path, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch (networkErr) {
      return { ok: false, status: 0, data: { detail: "Network error — is the API running?" } };
    }

    if (auth && res.status === 401) {
      clearToken();
      window.location.href = ROUTES.login;
      return { ok: false, status: 401, data: { detail: "Unauthorized" } };
    }

    let data = null;
    if (res.status !== 204) {
      try {
        data = await res.json();
      } catch (_) {
        data = null;
      }
    }
    return { ok: res.ok, status: res.status, data };
  }

  /** Turns FastAPI's error shapes into one readable line. */
  function errorMessage(data, fallback) {
    if (!data) return fallback;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail.length) {
      // Pydantic validation errors, e.g. password too short.
      return data.detail.map((d) => d.msg).join(" ");
    }
    return fallback;
  }

  function showMessage(el, text, kind = "error") {
    if (!el) return;
    el.textContent = text;
    el.classList.remove("hidden");
    el.classList.toggle("text-rose-400", kind === "error");
    el.classList.toggle("text-emerald-400", kind === "success");
  }

  function hideMessage(el) {
    if (!el) return;
    el.classList.add("hidden");
    el.textContent = "";
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }

  /** Redirects away from login/register if a token already looks valid. */
  async function redirectIfAuthenticated() {
    const token = getToken();
    if (!token) return;
    const { ok } = await api("/todos?page=1&limit=1");
    if (ok) window.location.href = ROUTES.dashboard;
    // On failure, api() already clears the bad token and would have redirected
    // itself only from an authenticated *dashboard* call — here we just stay put.
  }

  /** Guards the dashboard: bounce to login immediately if there's no token. */
  function requireAuth() {
    if (!getToken()) {
      window.location.href = ROUTES.login;
      return false;
    }
    return true;
  }

  return {
    ROUTES,
    getToken,
    setToken,
    clearToken,
    api,
    errorMessage,
    showMessage,
    hideMessage,
    escapeHtml,
    redirectIfAuthenticated,
    requireAuth,
  };
})();
