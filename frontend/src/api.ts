import type {
  CodeMergeFilters,
  CodeMergeOverview,
  DashboardFilters,
  DashboardOverview,
  FilterOptions,
  MrPageRequest,
  MrPageResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export const defaultFilters: DashboardFilters = {
  date_range: "last_30_days",
  granularity: "day",
  pdu: "all",
  lm_team: "all",
  user: "all",
  terminal_type: "all",
  client_version: "all",
  ide_type: "all",
  model: "all",
};

export const defaultCodeMergeFilters: CodeMergeFilters = {
  date_range: "last_30_days",
  granularity: "day",
  pdu: "all",
  lm_team: "all",
  ai_ratio_threshold: 50,
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function getFilterOptions(): Promise<FilterOptions> {
  return request<FilterOptions>("/dashboard/filters");
}

export function getOverview(filters: DashboardFilters): Promise<DashboardOverview> {
  return request<DashboardOverview>("/dashboard/overview", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}

export function exportReport(
  filters: DashboardFilters,
): Promise<{ report_id: string; status: string; message: string }> {
  return request("/dashboard/reports/export", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}

export function getCodeMergeOverview(filters: CodeMergeFilters): Promise<CodeMergeOverview> {
  return request<CodeMergeOverview>("/codemerge/overview", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}

export function getCodeMergeMrs(req: MrPageRequest): Promise<MrPageResponse> {
  const params = new URLSearchParams({
    date_range: req.date_range,
    granularity: req.granularity,
    pdu: req.pdu,
    lm_team: req.lm_team,
    ai_ratio_threshold: String(req.ai_ratio_threshold),
    page: String(req.page),
    page_size: String(req.page_size),
    sort_by: req.sort_by,
    sort_order: req.sort_order,
  });
  return request<MrPageResponse>(`/codemerge/mrs?${params.toString()}`);
}
