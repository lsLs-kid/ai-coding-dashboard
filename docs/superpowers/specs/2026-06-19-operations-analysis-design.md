# 运营分析页面 Design Spec

## Goal

新增"运营分析"页面，面向平台运营者展示 AI Coding 平台的运营类指标。聚焦工具调用、AI 采纳、AI 生成代码被采纳情况，以及用户问题单分布与趋势。不围绕活跃用户展开。

## Confirmed Decisions

| 问题 | 决策 |
|---|---|
| 目标用户 | 平台运营者 |
| 数据口径 | 工具调用次数、AI 采纳率、AI 生成被采纳代码行数、用户反馈/Bug 工单数 |
| AI 采纳率定义 | AI 生成的代码中被用户接受/保留的比例 |
| 用户问题单类型 | 功能咨询 / Bug 反馈 / 使用障碍 / 需求建议 / 其他 |
| 筛选维度 | 复用 `DashboardFilters`（日期范围、粒度、PDU、LM 团队、用户、端类型、客户端版本、IDE 类型、模型），无额外新增 |
| 页面布局 | 4 KPI 卡 + 6 图表（两行三列） |
| 后端路由架构 | 新建独立 `/api/operations` 路由组 |

## Page Layout

### Filters

复用现有 `DashboardFilters` 字段：

- 日期范围（date_range）
- 粒度（granularity）
- PDU
- LM 团队
- 用户
- 端类型
- 客户端版本
- IDE 类型
- 模型

筛选栏任意字段变化时，重新请求 `overview`。

### KPI Cards（4 张）

| # | 指标 | 字段 | 说明 |
|---|---|---|---|
| 1 | AI 采纳率 | `ai_adoption_rate` | 百分比，带环比 `ai_adoption_rate_change` |
| 2 | AI 生成被采纳代码行数 | `ai_accepted_lines` | 带环比 `ai_accepted_lines_change` |
| 3 | 总工具调用次数 | `total_tool_calls` | 带环比 `total_tool_calls_change` |
| 4 | 用户问题单总数 | `total_user_issues` | 带环比 `total_user_issues_change` |

### Charts（6 张，两行三列）

| 位置 | 图表 | 字段 | 类型 | 说明 |
|---|---|---|---|---|
| 第一行左 | 工具调用 Top 10 | `top_tools` | 横向柱状图 | 按调用次数排序 |
| 第一行中 | 工具调用趋势 | `tool_call_trend` | 折线图 | X 轴时间，Y 轴调用次数 |
| 第一行右 | AI 采纳率趋势 | `ai_adoption_trend` | 折线图 | X 轴时间，Y 轴采纳率百分比 |
| 第二行左 | AI 生成代码行数趋势 | `ai_accepted_lines_trend` | 折线图 | X 轴时间，Y 轴被采纳代码行数 |
| 第二行中 | 用户问题单趋势 | `user_issue_trend` | 折线图 | X 轴时间，Y 轴问题单数量 |
| 第二行右 | 不同类型用户问题单 | `user_issues_by_type` | 柱状图 | 每类问题一个柱子，展示时间段内总量 |

## Backend API

### New Route Group

文件：`backend/app/api/operations_routes.py`，挂载前缀 `/api/operations`，在 `main.py` 中注册。

| 方法 | 路径 | 请求体 | 响应体 |
|---|---|---|---|
| POST | `/api/operations/overview` | `DashboardFilters` | `OperationsOverview` |

### New Schemas（追加到 `backend/app/schemas.py`）

```python
class OperationsKpi(BaseModel):
    ai_adoption_rate: float
    ai_adoption_rate_change: str
    ai_accepted_lines: int
    ai_accepted_lines_change: str
    total_tool_calls: int
    total_tool_calls_change: str
    total_user_issues: int
    total_user_issues_change: str


class ToolCallTopItem(BaseModel):
    tool_name: str
    call_count: int


class TrendPoint(BaseModel):
    date: str
    value: float


class ToolCallTrendPoint(TrendPoint):
    value: int


class AiAdoptionTrendPoint(TrendPoint):
    value: float


class AiAcceptedLinesTrendPoint(TrendPoint):
    value: int


class UserIssueTrendPoint(TrendPoint):
    value: int


class UserIssueByType(BaseModel):
    issue_type: str
    count: int


class OperationsOverview(BaseModel):
    kpis: OperationsKpi
    top_tools: list[ToolCallTopItem]
    tool_call_trend: list[ToolCallTrendPoint]
    ai_adoption_trend: list[AiAdoptionTrendPoint]
    ai_accepted_lines_trend: list[AiAcceptedLinesTrendPoint]
    user_issue_trend: list[UserIssueTrendPoint]
    user_issues_by_type: list[UserIssueByType]
```

### Provider Interface（追加到 `backend/app/services/provider.py`）

```python
@abstractmethod
def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview: ...
```

## Frontend Structure

### File Changes

```
frontend/src/
├── App.tsx                         # 新增 /operations 路由
├── pages/
│   └── OperationsPage.tsx          # 新页面
├── api.ts                          # 新增 getOperationsOverview
├── types.ts                        # 新增 Operations* 类型
└── styles.css                      # 新增运营分析页面样式
```

### OperationsPage 内部组件树

```
OperationsPage
├── FilterBar（复用现有筛选栏）
├── OperationsKpiSection（4 张 KPI 卡片）
└── OperationsChartsSection（6 张图表，两行三列）
    ├── ToolCallTopChart
    ├── ToolCallTrendChart
    ├── AiAdoptionTrendChart
    ├── AiAcceptedLinesTrendChart
    ├── UserIssueTrendChart
    └── UserIssuesByTypeChart
```

### Data Loading

1. 页面挂载时请求 overview
2. 筛选变化 → 重新请求 overview

## Notes

- 趋势图时间粒度由 `granularity` 筛选字段控制。
- 问题单类型目前固定为：功能咨询、Bug 反馈、使用障碍、需求建议、其他。若未来类型扩展，后端返回动态列表，前端按返回数据渲染。
- AI 采纳率和 AI 生成代码行数趋势的数据口径需保持一致：两者都基于同一批 AI 生成事件计算。
