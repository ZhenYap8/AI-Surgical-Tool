const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1"]);

function getPageHostname() {
  if (typeof window === "undefined") return null;
  return window.location?.hostname || null;
}

function isLocalHostname(hostname) {
  return LOCAL_HOSTS.has(hostname);
}

/**
 * Resolve the API base URL for the current environment.
 * - Relative paths (e.g. `/api`) are kept as-is for same-origin deploys.
 * - Absolute localhost URLs are rewritten to the page hostname when the UI
 *   is opened via a LAN IP (phone on the same Wi‑Fi).
 * - With no env set, defaults to `http://{pageHostname}:8000` in the browser.
 */
export function resolveApiBaseUrl(envValue, pageHostname = getPageHostname()) {
  const raw = (envValue ?? "").trim();

  if (!raw) {
    if (pageHostname) {
      return `http://${pageHostname}:8000`;
    }
    return "http://localhost:8000";
  }

  const normalized = raw.replace(/\/$/, "");

  // Same-origin relative path (Vercel production)
  if (normalized.startsWith("/")) {
    return normalized;
  }

  try {
    const url = new URL(normalized);
    if (
      pageHostname &&
      !isLocalHostname(pageHostname) &&
      isLocalHostname(url.hostname)
    ) {
      url.hostname = pageHostname;
      return url.origin + (url.pathname === "/" ? "" : url.pathname.replace(/\/$/, ""));
    }
    return url.origin + (url.pathname === "/" ? "" : url.pathname.replace(/\/$/, ""));
  } catch {
    return normalized;
  }
}

export const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_URL);

export const PREDICT_AND_EXPLAIN_URL = `${API_BASE_URL}/predict_and_explain`;
