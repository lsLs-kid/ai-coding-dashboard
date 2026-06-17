export type TrendDirection = "up" | "down" | "flat";
export type Status = "active" | "low" | "inactive";
export type InsightType = "risk" | "warning" | "info" | "success";

export interface DashboardFilters {
  date_range: string;
  granularity: "day" | "week" | "month";
  pdu: string;
  lm_team: string;
  user: string;
  terminal_type: string;
  client_version: string;
  ide_type: string;
  model: string;
}

export interface FilterOption {
  label: string;
  value: string;
}

export interface FilterOptions {
  date_ranges: FilterOption[];
  granularities: FilterOption[];
  pdus: FilterOption[];
  lm_teams: FilterOption[];
  users: FilterOption[];
  terminal_types: FilterOption[];
  client_versions: FilterOption[];
  ide_types: FilterOption[];
  models: FilterOption[];
}

export interface KpiMetric {
  key: string;
  label: string;
  value: string;
  unit?: string;
  previous_label: string;
  change: string;
  direction: TrendDirection;
  accent: "blue" | "red" | "green" | "cyan";
}

export interface TrendPoint {
  date: string;
  active_users: number;
  token_cost: number;
  ai_mr_ratio: number;
}

export interface RankingRow {
  rank: number;
  pdu: string;
  lm_team: string;
  active_users: number;
  rollout_ratio: number;
  token_cost: number;
  ai_lines: number;
  ai_mr_ratio: number;
}

export interface QuadrantPoint {
  name: string;
  token_cost: number;
  ai_mr_ratio: number;
  ai_lines: number;
  category: string;
}

export interface Insight {
  type: InsightType;
  title: string;
  description: string;
}

export interface UserDetail {
  id: string;
  name: string;
  pdu: string;
  lm_team: string;
  terminal_type: string;
  client_version: string;
  ide_type: string;
  last_active_at: string | null;
  prompt_count: number;
  token_cost: number;
  mr_count: number;
  ai_lines: number;
  status: Status;
}

export interface MrDetail {
  mr_id: string;
  repository: string;
  author: string;
  pdu: string;
  lm_team: string;
  merged_at: string;
  total_lines: number;
  ai_lines: number;
  ai_mr_ratio: number;
  status: "merged" | "pending";
}

export interface TokenDetail {
  id: string;
  date: string;
  user: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  trace_id: string;
  status_code: number;
}

export interface DashboardOverview {
  filters: DashboardFilters;
  updated_at: string;
  kpis: KpiMetric[];
  trends: TrendPoint[];
  rankings: RankingRow[];
  quadrant: QuadrantPoint[];
  insights: Insight[];
  users: UserDetail[];
  mrs: MrDetail[];
  tokens: TokenDetail[];
}
