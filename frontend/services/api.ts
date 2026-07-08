// MeriAwaaz AI — frontend API client.
// All calls target the FastAPI backend. Base URL is configurable via
// NEXT_PUBLIC_API_BASE (defaults to the local dev backend on :8000).

import type {
  DashboardData,
  HeatmapData,
  RecommendationsResponse,
  SubmissionListResponse,
  SubmissionResponse,
  SubmitIssueInput,
} from "@/types/api";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000";

// The backend serves the interactive Leaflet heatmap page at /heatmap.
export const HEATMAP_URL = `${API_BASE}/heatmap`;

async function getJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

// ── Reads ──────────────────────────────────────────────────────────────────

export function getDashboard(): Promise<DashboardData> {
  return getJSON<DashboardData>("/api/dashboard");
}

export function getRecommendations(): Promise<RecommendationsResponse> {
  return getJSON<RecommendationsResponse>("/api/recommendations");
}

export function getHeatmap(): Promise<HeatmapData> {
  return getJSON<HeatmapData>("/api/heatmap");
}

export function listSubmissions(limit = 100, offset = 0): Promise<SubmissionListResponse> {
  return getJSON<SubmissionListResponse>(
    `/api/submissions?limit=${limit}&offset=${offset}`
  );
}

/** Mark submissions resolved. Fully-resolved clusters leave the dashboard/map. */
export async function resolveSubmissions(ids: string[]): Promise<{ resolved: number }> {
  const res = await fetch(`${API_BASE}/api/submissions/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Resolve failed: ${res.status} ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<{ resolved: number }>;
}

export function explainProject(projectId: string) {
  return getJSON(`/api/explain/${encodeURIComponent(projectId)}`);
}

// ── Writes ─────────────────────────────────────────────────────────────────

/**
 * Submit a citizen issue. The backend infers the channel from what is attached
 * (audio → voice, photo → image, else text) and re-derives category/location
 * from the text, so we send the description + location as the message text.
 */
export async function submitIssue(input: SubmitIssueInput): Promise<SubmissionResponse> {
  const { text, category, location, lat, lng, photo, audio } = input;

  const channel = audio ? "voice" : photo ? "image" : "text";

  // Fold the location (and a light category hint) into the message so the
  // pipeline's Citizen Intelligence agent can extract them.
  const parts = [text?.trim()].filter(Boolean) as string[];
  if (location && location.trim()) parts.push(`Location: ${location.trim()}`);
  if (category && category.trim()) parts.push(`Category hint: ${category.trim()}`);
  const message = parts.join("\n");

  const form = new FormData();
  form.append("channel", channel);
  form.append("text", message);
  if (lat != null && lng != null) {
    form.append("lat", String(lat));
    form.append("lng", String(lng));
  }
  if (photo) form.append("photo", photo);
  if (audio) form.append("audio", audio);

  const res = await fetch(`${API_BASE}/api/submissions`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Submission failed: ${res.status} ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<SubmissionResponse>;
}

/** Submit a citizen video (separate backend endpoint). */
export async function submitVideo(video: File, text = ""): Promise<SubmissionResponse> {
  const form = new FormData();
  form.append("channel", "video");
  form.append("video", video);
  if (text) form.append("text", text);
  const res = await fetch(`${API_BASE}/api/submissions/video`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Video submission failed: ${res.status} ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<SubmissionResponse>;
}
