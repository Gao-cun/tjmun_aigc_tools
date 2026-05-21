import type { AnalyzeResponse, Delegate, DelegateProfile, EmbeddingStats } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, cache: "no-store" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof error.detail === "string" ? error.detail : "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  listDelegates: () => request<Delegate[]>("/delegates"),
  createDelegate: (payload: { name: string; country?: string; committee?: string; notes?: string }) =>
    request<Delegate>("/delegates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  seedDemo: () => request<{ createdDelegates: number; createdDocuments: number }>("/demo/seed", { method: "POST" }),
  getProfile: (delegateId: string) => request<DelegateProfile>(`/delegate/${delegateId}/profile`),
  getEmbeddingStats: (delegateId: string) => request<EmbeddingStats>(`/embedding_stats?delegate_id=${delegateId}`),
  uploadHistory: (form: FormData) => request<{ document_id: string; status: string; message: string }>("/upload_history", { method: "POST", body: form }),
  analyze: (form: FormData) => request<AnalyzeResponse>("/analyze", { method: "POST", body: form }),
  revisionAnalysis: (payload: unknown) =>
    request<{ revision_session_id: string; result: Record<string, unknown> }>("/revision_analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
};
