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

// ── Code Merge Analysis ─────────────────────────────────────────────────────

export interface CodeMergeFilters {
  date_range: string;
  granularity: "day" | "week" | "month";
  pdu: string;
  lm_team: string;
  ai_ratio_threshold: 30 | 50 | 70;
}

export interface CodeMergeKpi {
  total_ai_lines: number;
  total_lines: number;
  overall_ai_ratio: number;
  total_mrs: number;
  ai_assisted_mrs: number;
  ai_assisted_ratio: number;
  total_repos: number;
  ai_lines_change: string;
  ai_ratio_change: string;
  mr_count_change: string;
  ai_assisted_ratio_change: string;
}

export interface PduMergeStats {
  pdu: string;
  total_lines: number;
  ai_lines: number;
  ai_ratio: number;
  mr_count: number;
  active_contributors: number;
}

export interface MergeTrendPoint {
  date: string;
  total_lines: number;
  ai_lines: number;
  ai_ratio: number;
  mr_count: number;
}

export interface RepoMergeStats {
  repository: string;
  mr_count: number;
  total_lines: number;
  ai_lines: number;
  ai_ratio: number;
}

export interface ContributorMergeStats {
  name: string;
  pdu: string;
  mr_count: number;
  total_lines: number;
  ai_lines: number;
  ai_ratio: number;
}

export interface CodeMergeOverview {
  kpis: CodeMergeKpi;
  pdu_breakdown: PduMergeStats[];
  trend: MergeTrendPoint[];
  top_repos: RepoMergeStats[];
  contributors: ContributorMergeStats[];
}

export interface MrPageRequest {
  date_range: string;
  granularity: "day" | "week" | "month";
  pdu: string;
  lm_team: string;
  ai_ratio_threshold: 30 | 50 | 70;
  page: number;
  page_size: number;
  sort_by: string;
  sort_order: "asc" | "desc";
}

export interface MrPageResponse {
  total: number;
  page: number;
  page_size: number;
  items: MrDetail[];
}
