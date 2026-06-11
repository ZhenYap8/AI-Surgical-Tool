function normalizeApiBaseUrl(value) {
  if (!value) return "http://localhost:8000";
  return value.replace(/\/$/, "");
}

export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_URL);

export const PREDICT_AND_EXPLAIN_URL = `${API_BASE_URL}/predict_and_explain`;
