import { afterEach, describe, expect, it, vi } from "vitest";

describe("API config", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("defaults to localhost backend when VITE_API_URL is unset", async () => {
    vi.stubEnv("VITE_API_URL", "");
    const { API_BASE_URL, PREDICT_AND_EXPLAIN_URL } = await import("./config");

    expect(API_BASE_URL).toBe("http://localhost:8000");
    expect(PREDICT_AND_EXPLAIN_URL).toBe("http://localhost:8000/predict_and_explain");
  });

  it("uses VITE_API_URL when set", async () => {
    vi.stubEnv("VITE_API_URL", "http://example.com:9000");
    const { API_BASE_URL, PREDICT_AND_EXPLAIN_URL } = await import("./config");

    expect(API_BASE_URL).toBe("http://example.com:9000");
    expect(PREDICT_AND_EXPLAIN_URL).toBe("http://example.com:9000/predict_and_explain");
  });

  it("supports relative Vercel API path", async () => {
    vi.stubEnv("VITE_API_URL", "/api");
    const { API_BASE_URL, PREDICT_AND_EXPLAIN_URL } = await import("./config");

    expect(API_BASE_URL).toBe("/api");
    expect(PREDICT_AND_EXPLAIN_URL).toBe("/api/predict_and_explain");
  });
});
