# 代码入库分析页面 Design Spec

## Goal

新增"代码入库分析"页面，展示各 PDU 下 MR 入库中 AI 生成代码的占比情况，包含整体 KPI、多维图表和可分页的 MR 明细列表。

## Confirmed Decisions

| 问题 | 决策 |
|---|---|
| AI 辅助 MR 阈值 | 可配置筛选项，选项 30% / 50% / 70%，默认 50% |
| 趋势图 | 单线（整体趋势），PDU 作为筛选条件 |
| MR 列表 | 独立分页接口，每页 20 条 |
| 后端路由架构 | 新独立路由组 `/api/codemerge`，不扩展现有 dashboard 路由 |

## Page Layout

### Filters

复用现有 `DashboardFilters` 字段（日期范围、粒度、PDU、LM 团队），新增：

- `ai_ratio_threshold: Literal[30, 50, 70]`，默认 `50`

筛选栏任意字段变化时，同时重新请求 overview 和 mrs（重置到第 1 页）。

### KPI Cards（5 张）

| # | 指标 | 字段 | 备注 |
|---|---|---|---|
| 1 | AI 代码入库行数 | `total_ai_lines` | 带环比 `ai_lines_change` |
| 2 | 整体 AI 代码占比 | `overall_ai_ratio` | `ai_lines / total_lines`，带环比 |
| 3 | 入库 MR 总数 | `total_mrs` | 带环比 `mr_count_change` |
| 4 | AI 辅助 MR 占比 | `ai_assisted_ratio` | `ai_ratio >= threshold` 的 MR 占比，带环比 |
| 5 | 涉及仓库数 | `total_repos` | 当期有 MR 入库的仓库数，无环比 |

### Charts（2 × 2）

| 位置 | 图表 | 数据来源 | 说明 |
|---|---|---|---|
| 左上 | PDU 横向叠加柱状图 | `pdu_breakdown` | Y 轴 PDU，X 轴代码行数；AI 行数高亮色叠加在总行数上 |
| 右上 | AI 代码占比趋势折线图 | `trend` | 单线，X 轴时间，Y 轴 `ai_ratio %` |
| 左下 | 仓库 Top 10 水平柱状图 | `top_repos` | 按 `ai_lines` 降序排列 |
| 右下 | 开发者贡献散点图 | `contributors` | X=`total_lines`，Y=`ai_ratio`，气泡大小=`mr_count`，颜色=PDU |

### MR Detail Table

- 独立请求 `GET /api/codemerge/mrs`
- 列：MR ID、仓库、作者、PDU、团队、入库时间、总行数、AI 行数、AI 占比、状态
- 支持列排序（`sort_by` + `sort_order`）
- 分页：每页 20 条，显示总数和翻页控件

## Backend API

### New Route Group

文件：`backend/app/api/codemerge_routes.py`，挂载前缀 `/api/codemerge`，在 `main.py` 中注册。

| 方法 | 路径 | 请求体 | 响应体 |
|---|---|---|---|
| POST | `/api/codemerge/overview` | `CodeMergeFilters` | `CodeMergeOverview` |
| GET | `/api/codemerge/mrs` | query params from `MrPageRequest` | `MrPageResponse` |

> `/mrs` 使用 GET + query params 以便支持浏览器直链和前端 URL 状态同步。

### New Schemas（`backend/app/schemas.py` 追加）

```python
class CodeMergeFilters(DashboardFilters):
    ai_ratio_threshold: Literal[30, 50, 70] = 50

class CodeMergeKpi(BaseModel):
    total_ai_lines: int
    total_lines: int
    overall_ai_ratio: float
    total_mrs: int
    ai_assisted_mrs: int
    ai_assisted_ratio: float
    total_repos: int
    ai_lines_change: str          # e.g. "+12.3%"
    ai_ratio_change: str
    mr_count_change: str
    ai_assisted_ratio_change: str

class PduMergeStats(BaseModel):
    pdu: str
    total_lines: int
    ai_lines: int
    ai_ratio: float
    mr_count: int
    active_contributors: int

class MergeTrendPoint(BaseModel):
    date: str
    total_lines: int
    ai_lines: int
    ai_ratio: float
    mr_count: int

class RepoMergeStats(BaseModel):
    repository: str
    mr_count: int
    total_lines: int
    ai_lines: int
    ai_ratio: float

class ContributorMergeStats(BaseModel):
    name: str
    pdu: str
    mr_count: int
    total_lines: int
    ai_lines: int
    ai_ratio: float

class CodeMergeOverview(BaseModel):
    kpis: CodeMergeKpi
    pdu_breakdown: list[PduMergeStats]
    trend: list[MergeTrendPoint]
    top_repos: list[RepoMergeStats]
    contributors: list[ContributorMergeStats]

class MrPageRequest(BaseModel):
    # filters (duplicated from CodeMergeFilters for GET query param compatibility)
    date_range: str = "last_30_days"
    granularity: Literal["day", "week", "month"] = "day"
    pdu: str = "all"
    lm_team: str = "all"
    ai_ratio_threshold: Literal[30, 50, 70] = 50
    # pagination
    page: int = 1
    page_size: int = 20
    sort_by: str = "merged_at"
    sort_order: Literal["asc", "desc"] = "desc"

class MrPageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MrDetail]
```

### Provider Interface（`backend/app/services/provider.py` 新增）

```python
@abstractmethod
def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview: ...

@abstractmethod
def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse: ...
```

## Frontend Structure

### File Changes

```
frontend/src/
├── App.tsx                    # 精简为 shell：导航栏 + active page 状态 + 页面切换
├── pages/
│   ├── OverviewPage.tsx       # 从 App.tsx 提取现有概览页全部内容
│   └── CodeMergePage.tsx      # 新页面
├── api.ts                     # 新增 getCodeMergeOverview / getCodeMergeMrs
└── types.ts                   # 新增 CodeMergeFilters / CodeMergeOverview 等类型
```

`styles.css` 不新建 CSS 文件，在现有文件末尾追加新选择器。

### CodeMergePage 内部组件树

```
CodeMergePage
├── FilterBar（筛选栏，含阈值下拉）
├── KpiSection（5 张 KPI 卡片，复用现有卡片样式）
├── ChartsSection（2×2 grid）
│   ├── PduBarChart
│   ├── TrendChart
│   ├── RepoBarChart
│   └── ContributorScatterChart
└── MrTable（独立 state：page / sort_by / sort_order）
```

### Data Loading

1. 页面挂载时，并行请求 overview + mrs（第 1 页）
2. 筛选变化 → 重新请求 overview + mrs（重置 page = 1）
3. 翻页 / 排序变化 → 仅重新请求 mrs，不触发 overview
