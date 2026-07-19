import axios from "axios";
import type {
  BenchmarkResult,
  Conflict,
  DocumentRecord,
  ExpertContribution,
  ExpertContributionInput,
  GraphExport,
  NodeDetail,
  UploadResponse,
} from "./types";

export const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<UploadResponse>(
    "/api/v1/documents/upload",
    form,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function getDocuments(): Promise<DocumentRecord[]> {
  const { data } = await api.get<DocumentRecord[]>("/api/v1/documents");
  return data;
}

export async function getConflicts(status?: string): Promise<Conflict[]> {
  const { data } = await api.get<Conflict[]>("/api/v1/conflicts", {
    params: status ? { status } : undefined,
  });
  return data;
}

export async function resolveConflict(id: string): Promise<Conflict> {
  const { data } = await api.patch<Conflict>(
    `/api/v1/conflicts/${id}/resolve`
  );
  return data;
}

export async function generateWorkOrderPDF(id: string): Promise<Blob> {
  const { data } = await api.post(
    `/api/v1/conflicts/${id}/generate`,
    undefined,
    { responseType: "blob" }
  );
  return data as Blob;
}

export async function getGraphExport(): Promise<GraphExport> {
  const { data } = await api.get<GraphExport>("/api/v1/graph/export");
  return data;
}

export async function getGraphNodes(): Promise<GraphExport["nodes"]> {
  const { data } = await api.get<GraphExport["nodes"]>("/api/v1/graph/nodes");
  return data;
}

export async function getNodeDetail(tag: string): Promise<NodeDetail> {
  const { data } = await api.get<NodeDetail>(
    `/api/v1/graph/nodes/${encodeURIComponent(tag)}`
  );
  return data;
}

export async function submitExpertContribution(
  payload: ExpertContributionInput
): Promise<ExpertContribution> {
  const { data } = await api.post<ExpertContribution>(
    "/api/v1/expert/contribute",
    payload
  );
  return data;
}

export async function getExpertContributions(): Promise<ExpertContribution[]> {
  const { data } = await api.get<ExpertContribution[]>(
    "/api/v1/expert/contributions"
  );
  return data;
}

export async function getBenchmarks(): Promise<BenchmarkResult[]> {
  const { data } = await api.get<BenchmarkResult[]>("/api/v1/benchmarks");
  return data;
}
