import { afterEach, describe, expect, it, vi } from "vitest";

describe("API config", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
    vi.unstubAllGlobals();
  });

  it("defaults to localhost backend when VITE_API_URL is unset and page is localhost", async () => {
    vi.stubEnv("VITE_API_URL", "");
    vi.stubGlobal("window", { location: { hostname: "localhost" } });
    const { API_BASE_URL, PREDICT_AND_EXPLAIN_URL } = await import("./config");

    expect(API_BASE_URL).toBe("http://localhost:8000");
    expect(PREDICT_AND_EXPLAIN_URL).toBe("http://localhost:8000/predict_and_explain");
  });

  it("defaults to page hostname when VITE_API_URL is unset on LAN", async () => {
    vi.stubEnv("VITE_API_URL", "");
    vi.stubGlobal("window", { location: { hostname: "192.168.1.42" } });
    const { resolveApiBaseUrl } = await import("./config");

    expect(resolveApiBaseUrl("", "192.168.1.42")).toBe("http://192.168.1.42:8000");
  });

  it("uses VITE_API_URL when set to a non-localhost host", async () => {
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

  it("rewrites localhost API URL to the page LAN hostname", async () => {
    const { resolveApiBaseUrl } = await import("./config");

    expect(resolveApiBaseUrl("http://localhost:8000", "192.168.1.42")).toBe(
      "http://192.168.1.42:8000"
    );
    expect(resolveApiBaseUrl("http://127.0.0.1:8000", "10.0.0.5")).toBe(
      "http://10.0.0.5:8000"
    );
  });

  it("does not rewrite when page is also localhost", async () => {
    const { resolveApiBaseUrl } = await import("./config");

    expect(resolveApiBaseUrl("http://localhost:8000", "localhost")).toBe(
      "http://localhost:8000"
    );
  });

  it("does not rewrite relative /api even on LAN", async () => {
    const { resolveApiBaseUrl } = await import("./config");

    expect(resolveApiBaseUrl("/api", "192.168.1.42")).toBe("/api");
  });
});
