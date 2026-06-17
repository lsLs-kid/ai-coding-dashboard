import type { DashboardFilters, DashboardOverview, FilterOptions } from "./types";

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
  model: "all"
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
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
    body: JSON.stringify(filters)
  });
}

export function exportReport(filters: DashboardFilters): Promise<{ report_id: string; status: string; message: string }> {
  return request("/dashboard/reports/export", {
    method: "POST",
    body: JSON.stringify(filters)
  });
}
