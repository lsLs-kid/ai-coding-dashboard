from typing import Literal

from pydantic import BaseModel, Field


Granularity = Literal["day", "week", "month"]
TrendDirection = Literal["up", "down", "flat"]
Status = Literal["active", "low", "inactive"]


class DashboardFilters(BaseModel):
    date_range: str = Field(default="last_30_days")
    granularity: Granularity = Field(default="day")
    pdu: str = Field(default="all")
    lm_team: str = Field(default="all")
    user: str = Field(default="all")
    terminal_type: str = Field(default="all")
    client_version: str = Field(default="all")
    ide_type: str = Field(default="all")
    model: str = Field(default="all")


class FilterOption(BaseModel):
    label: str
    value: str


class FilterOptions(BaseModel):
    date_ranges: list[FilterOption]
    granularities: list[FilterOption]
    pdus: list[FilterOption]
    lm_teams: list[FilterOption]
    users: list[FilterOption]
    terminal_types: list[FilterOption]
    client_versions: list[FilterOption]
    ide_types: list[FilterOption]
    models: list[FilterOption]


class KpiMetric(BaseModel):
    key: str
    label: str
    value: str
    unit: str | None = None
    previous_label: str = "较上期"
    change: str
    direction: TrendDirection
    accent: Literal["blue", "red", "green", "cyan"] = "blue"


class TrendPoint(BaseModel):
    date: str
    active_users: int
    token_cost: float
    ai_mr_ratio: float


class RankingRow(BaseModel):
    rank: int
    pdu: str
    lm_team: str
    active_users: int
    rollout_ratio: float
    token_cost: float
    ai_lines: int
    ai_mr_ratio: float


class QuadrantPoint(BaseModel):
    name: str
    token_cost: float
    ai_mr_ratio: float
    ai_lines: int
    category: str


class Insight(BaseModel):
    type: Literal["risk", "warning", "info", "success"]
    title: str
    description: str


class UserDetail(BaseModel):
    id: str
    name: str
    pdu: str
    lm_team: str
    terminal_type: str
    client_version: str
    ide_type: str
    last_active_at: str | None
    prompt_count: int
    token_cost: float
    mr_count: int
    ai_lines: int
    status: Status


class MrDetail(BaseModel):
    mr_id: str
    repository: str
    author: str
    pdu: str
    lm_team: str
    merged_at: str
    total_lines: int
    ai_lines: int
    ai_mr_ratio: float
    status: Literal["merged", "pending"]


class TokenDetail(BaseModel):
    id: str
    date: str
    user: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    trace_id: str
    status_code: int


class DashboardOverview(BaseModel):
    filters: DashboardFilters
    updated_at: str
    kpis: list[KpiMetric]
    trends: list[TrendPoint]
    rankings: list[RankingRow]
    quadrant: list[QuadrantPoint]
    insights: list[Insight]
    users: list[UserDetail]
    mrs: list[MrDetail]
    tokens: list[TokenDetail]


class ExportReportResponse(BaseModel):
    report_id: str
    status: Literal["mocked", "queued", "ready"]
    message: str
