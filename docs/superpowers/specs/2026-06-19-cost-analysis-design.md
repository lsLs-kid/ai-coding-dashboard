# 成本分析页面 Design Spec

## Goal

新增"成本分析"页面，面向平台运营者展示 AI Coding 平台的 Token 消耗情况。支持按 input/output/total 维度切换，提供趋势、模型分布、PDU 排行和明细表格。

## Confirmed Decisions

| 问题 | 决策 |
|---|---|
| 目标用户 | 平台运营者 |
| 成本数据口径 | 只用 Token 量，不计算金额 |
| 模型区分 | 趋势图整体单线，模型分布图按模型拆分 |
| 筛选维度 | 复用 DashboardFilters，新增 `cost_type`（input/output/total） |
| cost_type 影响范围 | 全页所有图表和表格 |
| 页面布局 | 4 KPI 卡 + 3 横向图表 + 分页表格 |
| 后端路由架构 | 新建独立 `/api/cost` 路由组，复用 `TokenDetail` |

## Page Layout

### Filters

复用现有 `DashboardFilters` 字段（日期范围、粒度、PDU、LM 团队、用户、端类型、客户端版本、IDE 类型、模型），新增：

- `cost_type: Literal["input", "output", "total"]`，默认 `"total"`

筛选栏任意字段变化时，同时重新请求 overview 和 tokens（重置到第 1 页）。

### KPI Cards（4 张）

| # | 指标 | 字段 | 备注 |
|---|---|---|---|
| 1 | 总 Token 消耗 | `total_tokens` | 带环比 `total_tokens_change` |
| 2 | Input Token | `input_tokens` | 带环比 `input_tokens_change` |
| 3 | Output Token | `output_tokens` | 带环比 `output_tokens_change` |
| 4 | 人均 Token 消耗 | `per_user_tokens` | 总 Token / 活跃用户数，带环比 |

### Charts（3 张横向排列）

| # | 图表 | 数据来源 | 说明 |
|---|---|---|---|
| 1 | Token 消耗趋势 | `trend` | X 轴时间，Y 轴按 `cost_type` 展示 input/output/total；单线 |
| 2 | 模型 Token 分布 | `model_distribution` | 横向柱状图，按 total_tokens 排序 |
| 3 | PDU Token Top 10 | `top_pdus` | 横向柱状图，按 `total_tokens` 排序 |

### Token Detail Table

- 独立请求 `GET /api/cost/tokens`
- 列：日期、PDU、LM 团队、用户、模型、Input Token、Output Token、Total Token
- 支持列排序（`sort_by` + `sort_order`）
- 分页：每页 20 条

## Backend API

### New Route Group

文件：`backend/app/api/cost_routes.py`，挂载前缀 `/api/cost`，在 `main.py` 中注册。

| 方法 | 路径 | 请求体 | 响应体 |
|---|---|---|---|
| POST | `/api/cost/overview` | `CostFilters` | `CostOverview` |
| GET | `/api/cost/tokens` | query params from `TokenPageRequest` | `TokenPageResponse` |

> `/tokens` 使用 GET + query params 以便支持浏览器直链和前端 URL 状态同步。

### New Schemas（追加到 `backend/app/schemas.py`）

```python
class CostFilters(DashboardFilters):
    cost_type: Literal["input", "output", "total"] = "total"


class CostKpi(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int
    per_user_tokens: float
    total_tokens_change: str
    input_tokens_change: str
    output_tokens_change: str
    per_user_tokens_change: str


class CostTrendPoint(BaseModel):
    date: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ModelCostStats(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class PduCostStats(BaseModel):
    pdu: str
    total_tokens: int


class CostOverview(BaseModel):
    kpis: CostKpi
    trend: list[CostTrendPoint]
    model_distribution: list[ModelCostStats]
    top_pdus: list[PduCostStats]


class TokenPageRequest(BaseModel):
    date_range: str = "last_30_days"
    granularity: Literal["day", "week", "month"] = "day"
    pdu: str = "all"
    lm_team: str = "all"
    user: str = "all"
    terminal_type: str = "all"
    client_version: str = "all"
    ide_type: str = "all"
    model: str = "all"
    cost_type: Literal["input", "output", "total"] = "total"  # int for GET query coercion
    page: int = 1
    page_size: int = 20
    sort_by: str = "date"
    sort_order: Literal["asc", "desc"] = "desc"


class TokenPageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TokenDetail]
```

### Provider Interface（新增到 `backend/app/services/provider.py`）

```python
@abstractmethod
def get_cost_overview(self, filters: CostFilters) -> CostOverview: ...

@abstractmethod
def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse: ...
```

## Frontend Structure

### File Changes

```
frontend/src/
├── App.tsx                    # 已有，/cost 路由已指向 PlaceholderPage
├── pages/
│   ├── CostPage.tsx           # 新页面（替换 PlaceholderPage）
│   ├── OverviewPage.tsx       # 不变
│   └── CodeMergePage.tsx      # 不变
├── api.ts                     # 新增 getCostOverview / getCostTokens / defaultCostFilters
└── types.ts                   # 新增 Cost* 类型
```

### CostPage 内部组件树

```
CostPage
├── CostFilterBar（筛选栏，含成本类型下拉）
├── CostKpiSection（4 张 KPI 卡片，复用现有卡片样式）
├── CostChartsSection（3 张横向图表）
│   ├── TokenTrendChart
│   ├── ModelDistributionChart
│   └── PduTopChart
└── TokenTable（独立 state：page / sort_by / sort_order）
```

### Data Loading

1. 页面挂载时并行请求 overview + tokens（第 1 页）
2. 筛选变化 → 重新请求 overview + tokens（重置 page = 1）
3. 翻页 / 排序变化 → 仅重新请求 tokens，不触发 overview

## Notes

- `TokenPageRequest.cost_type` 使用普通 `int`（与 `MrPageRequest` 同样的 GET query coercion 问题），POST body 的 `CostFilters` 保留 `Literal`。
- 趋势图单线按 `cost_type` 切换展示 input/output/total 三个字段中的一个。
- 模型分布图和 PDU Top10 始终按 `total_tokens` 排序，不受 `cost_type` 影响排序字段（但总量会随筛选变化）。
- 人均 Token = 总 Token / 活跃用户数；活跃用户数从 mock 数据中计算或复用概览逻辑。
