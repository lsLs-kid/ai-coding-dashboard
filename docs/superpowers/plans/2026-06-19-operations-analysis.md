# 运营分析页面 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 AI Coding 运营看板中新增"运营分析"页面，展示工具调用、AI 采纳、AI 生成代码被采纳情况、用户问题单四类运营指标（4 KPI + 6 图表）。

**Architecture:** 后端沿用 DashboardDataProvider 抽象模式，新增 `/api/operations` 路由组与 `get_operations_overview` 方法；前端复用现有筛选栏与 KPI 卡片样式，新增 `OperationsPage` 页面并通过 react-router 注册 `/operations` 路由。

**Tech Stack:** Python 3.11 + FastAPI + Pydantic v2；React 19 + TypeScript 5 + ECharts 6 (echarts-for-react) + react-router-dom 7 + lucide-react。

## Global Constraints

- 后端路由统一挂载在 `settings.api_prefix`（`/api`）下。
- 筛选维度必须复用 `DashboardFilters`，不新增额外筛选字段。
- 所有新增 Pydantic 模型必须保持可选字段有默认值，便于前端 mock 与测试。
- 前端类型 `types.ts` 必须与后端 `schemas.py` 保持同步。
- 前端页面统一通过 `App.tsx` 的 `Routes` 注册，并通过 `onUpdatedAt` 回调更新顶部数据更新时间。
- 运营分析页面不包含活跃用户指标，不展示明细表格。
- KPI 卡片沿用现有 `.kpi-card` 样式；图表容器沿用现有 `.panel` 样式。
- Mock 数据需覆盖 30 天时间范围（04-21 ~ 05-20），与现有概览页一致。

---

## File Structure

| 文件 | 责任 |
|---|---|
| `backend/app/schemas.py` | 新增运营分析相关 Pydantic 模型 |
| `backend/app/services/provider.py` | 新增 `get_operations_overview` 抽象方法 |
| `backend/app/services/mock_provider.py` | `MockDashboardDataProvider` 实现 `get_operations_overview` |
| `backend/app/api/operations_routes.py` | 新增 `/api/operations/overview` POST 路由 |
| `backend/app/main.py` | 注册 `operations_routes` |
| `frontend/src/types.ts` | 新增 TypeScript 类型，镜像后端 schema |
| `frontend/src/api.ts` | 新增 `getOperationsOverview` 请求函数 |
| `frontend/src/pages/OperationsPage.tsx` | 运营分析页面组件 |
| `frontend/src/App.tsx` | `/operations` 路由指向 `OperationsPage` |
| `frontend/src/styles.css` | 新增运营分析页面 2x3 图表网格样式 |

---

### Task 1: Backend schemas

**Files:**
- Modify: `backend/app/schemas.py`

**Interfaces:**
- Produces: `OperationsKpi`, `ToolCallTopItem`, `ToolCallTrendPoint`, `AiAdoptionTrendPoint`, `AiAcceptedLinesTrendPoint`, `UserIssueTrendPoint`, `UserIssueByType`, `OperationsOverview`

- [ ] **Step 1: Append operations analysis schemas to `schemas.py`**

在文件末尾 `# ── Cost Analysis ───────────────────────────────────────────────────────────` 之后新增 `# ── Operations Analysis ─────────────────────────────────────────────────────` 区块：

```python
# ── Operations Analysis ─────────────────────────────────────────────────────

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


class ToolCallTrendPoint(BaseModel):
    date: str
    value: int


class AiAdoptionTrendPoint(BaseModel):
    date: str
    value: float


class AiAcceptedLinesTrendPoint(BaseModel):
    date: str
    value: int


class UserIssueTrendPoint(BaseModel):
    date: str
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

- [ ] **Step 2: Verify syntax**

Run:
```bash
cd backend
python -c "import app.schemas"
```

Expected: no output / exit 0

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas.py
git commit -m "feat(schemas): add operations analysis models"
```

---

### Task 2: Provider interface

**Files:**
- Modify: `backend/app/services/provider.py`

**Interfaces:**
- Consumes: `OperationsOverview` from `app.schemas`
- Produces: `DashboardDataProvider.get_operations_overview(filters: DashboardFilters) -> OperationsOverview`

- [ ] **Step 1: Update imports and add abstract method**

修改 `backend/app/services/provider.py`：

```python
from app.schemas import (
    CodeMergeFilters,
    CodeMergeOverview,
    CostFilters,
    CostOverview,
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOptions,
    MrDetail,
    MrPageRequest,
    MrPageResponse,
    OperationsOverview,
    TokenDetail,
    TokenPageRequest,
    TokenPageResponse,
    UserDetail,
)
```

在 `get_cost_tokens` 之后添加：

```python
    @abstractmethod
    def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview:
        raise NotImplementedError
```

- [ ] **Step 2: Verify syntax**

Run:
```bash
cd backend
python -c "import app.services.provider"
```

Expected: no output / exit 0

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/provider.py
git commit -m "feat(provider): add get_operations_overview interface"
```

---

### Task 3: Mock provider implementation

**Files:**
- Modify: `backend/app/services/mock_provider.py`

**Interfaces:**
- Consumes: `DashboardFilters`, 新增 `OperationsKpi`, `OperationsOverview`, `ToolCallTopItem`, `ToolCallTrendPoint`, `AiAdoptionTrendPoint`, `AiAcceptedLinesTrendPoint`, `UserIssueTrendPoint`, `UserIssueByType`
- Produces: `get_operations_overview` 返回完整 mock `OperationsOverview`

- [ ] **Step 1: Update imports**

在 `backend/app/services/mock_provider.py` 的 imports 中追加：

```python
from app.schemas import (
    ...,
    AiAcceptedLinesTrendPoint,
    AiAdoptionTrendPoint,
    OperationsKpi,
    OperationsOverview,
    ToolCallTopItem,
    ToolCallTrendPoint,
    UserIssueByType,
    UserIssueTrendPoint,
)
```

- [ ] **Step 2: Implement `get_operations_overview`**

在 `MockDashboardDataProvider` 类末尾（`get_cost_tokens` 之后）添加：

```python
    def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview:
        return OperationsOverview(
            kpis=OperationsKpi(
                ai_adoption_rate=78.5,
                ai_adoption_rate_change="+3.2pp",
                ai_accepted_lines=1_245_600,
                ai_accepted_lines_change="+18.4%",
                total_tool_calls=856_432,
                total_tool_calls_change="+12.7%",
                total_user_issues=328,
                total_user_issues_change="-5.3%",
            ),
            top_tools=self._top_tools(),
            tool_call_trend=self._tool_call_trend(),
            ai_adoption_trend=self._ai_adoption_trend(),
            ai_accepted_lines_trend=self._ai_accepted_lines_trend(),
            user_issue_trend=self._user_issue_trend(),
            user_issues_by_type=self._user_issues_by_type(),
        )

    def _top_tools(self) -> list[ToolCallTopItem]:
        rows = [
            ("代码补全", 245_800),
            ("代码解释", 186_400),
            ("生成单测", 142_300),
            ("生成注释", 98_700),
            ("重构建议", 76_500),
            ("错误诊断", 64_200),
            ("提交信息生成", 48_900),
            ("文档生成", 32_100),
            ("代码审查", 28_400),
            ("API 查询", 15_600),
        ]
        return [ToolCallTopItem(tool_name=r[0], call_count=r[1]) for r in rows]

    def _tool_call_trend(self) -> list[ToolCallTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        values = [21000,23500,22800,26100,24200,23800,25500,26900,28100,26400,27300,28600,27900,26800,29200,28100,29500,30800,28700,27600,29900,26200,28400,31100,32500,29800,31600,30400,29100,28500]
        return [ToolCallTrendPoint(date=d, value=v) for d, v in zip(dates, values)]

    def _ai_adoption_trend(self) -> list[AiAdoptionTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        values = [71.2,72.5,71.8,73.4,72.9,73.8,74.2,73.5,75.1,74.6,75.3,76.1,75.7,76.4,77.0,76.8,77.5,78.1,77.6,78.4,78.9,78.2,79.1,79.6,80.2,79.8,80.5,80.1,81.0,78.5]
        return [AiAdoptionTrendPoint(date=d, value=v) for d, v in zip(dates, values)]

    def _ai_accepted_lines_trend(self) -> list[AiAcceptedLinesTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        values = [32000,35100,33800,38200,36100,35500,37400,39100,40800,38700,39900,41600,40700,39400,42300,41200,42800,44100,42100,40900,43500,39800,41900,44800,46200,43600,45300,44200,42900,41500]
        return [AiAcceptedLinesTrendPoint(date=d, value=v) for d, v in zip(dates, values)]

    def _user_issue_trend(self) -> list[UserIssueTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        values = [14,16,13,18,15,14,17,19,21,16,18,20,17,15,22,19,21,23,20,18,24,21,22,25,27,23,26,24,22,20]
        return [UserIssueTrendPoint(date=d, value=v) for d, v in zip(dates, values)]

    def _user_issues_by_type(self) -> list[UserIssueByType]:
        rows = [
            ("功能咨询", 98),
            ("Bug 反馈", 76),
            ("使用障碍", 62),
            ("需求建议", 58),
            ("其他", 34),
        ]
        return [UserIssueByType(issue_type=r[0], count=r[1]) for r in rows]
```

- [ ] **Step 3: Verify syntax and run backend**

Run:
```bash
cd backend
python -c "import app.services.mock_provider"
```

Expected: no output / exit 0

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/mock_provider.py
git commit -m "feat(mock): add operations overview mock data"
```

---

### Task 4: Backend routes

**Files:**
- Create: `backend/app/api/operations_routes.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `DashboardFilters`, `OperationsOverview`, `DashboardDataProvider`
- Produces: `POST /api/operations/overview` returning `OperationsOverview`

- [ ] **Step 1: Create operations routes file**

创建 `backend/app/api/operations_routes.py`：

```python
from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import DashboardFilters, OperationsOverview
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post("/overview", response_model=OperationsOverview)
def get_operations_overview(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> OperationsOverview:
    return provider.get_operations_overview(filters)
```

- [ ] **Step 2: Register router in `main.py`**

修改 `backend/app/main.py`：

```python
from app.api.codemerge_routes import router as codemerge_router
from app.api.cost_routes import router as cost_router
from app.api.operations_routes import router as operations_router
from app.api.routes import router as dashboard_router
```

在 `app.include_router(cost_router, prefix=settings.api_prefix)` 之后添加：

```python
    app.include_router(operations_router, prefix=settings.api_prefix)
```

- [ ] **Step 3: Smoke test the endpoint**

Run:
```bash
cd backend
python -c "from app.main import app; print([r.path for r in app.routes])" | grep operations
```

Expected output contains `/api/operations/overview`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/operations_routes.py backend/app/main.py
git commit -m "feat(api): add operations overview route"
```

---

### Task 5: Frontend types

**Files:**
- Modify: `frontend/src/types.ts`

**Interfaces:**
- Produces: TypeScript interfaces mirroring backend operations schemas

- [ ] **Step 1: Append operations types**

在 `frontend/src/types.ts` 末尾（`TokenPageResponse` 之后）追加：

```typescript
// ── Operations Analysis ─────────────────────────────────────────────────────

export interface OperationsKpi {
  ai_adoption_rate: number;
  ai_adoption_rate_change: string;
  ai_accepted_lines: number;
  ai_accepted_lines_change: string;
  total_tool_calls: number;
  total_tool_calls_change: string;
  total_user_issues: number;
  total_user_issues_change: string;
}

export interface ToolCallTopItem {
  tool_name: string;
  call_count: number;
}

export interface ToolCallTrendPoint {
  date: string;
  value: number;
}

export interface AiAdoptionTrendPoint {
  date: string;
  value: number;
}

export interface AiAcceptedLinesTrendPoint {
  date: string;
  value: number;
}

export interface UserIssueTrendPoint {
  date: string;
  value: number;
}

export interface UserIssueByType {
  issue_type: string;
  count: number;
}

export interface OperationsOverview {
  kpis: OperationsKpi;
  top_tools: ToolCallTopItem[];
  tool_call_trend: ToolCallTrendPoint[];
  ai_adoption_trend: AiAdoptionTrendPoint[];
  ai_accepted_lines_trend: AiAcceptedLinesTrendPoint[];
  user_issue_trend: UserIssueTrendPoint[];
  user_issues_by_type: UserIssueByType[];
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run:
```bash
cd frontend
pnpm exec tsc -b --noEmit
```

Expected: no errors (only pre-existing)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat(types): add operations analysis types"
```

---

### Task 6: Frontend API

**Files:**
- Modify: `frontend/src/api.ts`

**Interfaces:**
- Consumes: `DashboardFilters`, `OperationsOverview`
- Produces: `getOperationsOverview(filters: DashboardFilters): Promise<OperationsOverview>`

- [ ] **Step 1: Update imports and add function**

修改 `frontend/src/api.ts`：

```typescript
import type {
  CodeMergeFilters,
  CodeMergeOverview,
  CostFilters,
  CostOverview,
  DashboardFilters,
  DashboardOverview,
  FilterOptions,
  MrPageRequest,
  MrPageResponse,
  OperationsOverview,
  TokenPageRequest,
  TokenPageResponse,
} from "./types";
```

在 `getCostTokens` 之后追加：

```typescript
export function getOperationsOverview(filters: DashboardFilters): Promise<OperationsOverview> {
  return request<OperationsOverview>("/operations/overview", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}
```

- [ ] **Step 2: Verify TypeScript**

Run:
```bash
cd frontend
pnpm exec tsc -b --noEmit
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api.ts
git commit -m "feat(api): add getOperationsOverview client"
```

---

### Task 7: OperationsPage component

**Files:**
- Create: `frontend/src/pages/OperationsPage.tsx`

**Interfaces:**
- Consumes: `DashboardFilters`, `FilterOptions`, `OperationsOverview`, `getFilterOptions`, `getOperationsOverview`, `defaultFilters`
- Produces: `OperationsPage` React component

- [ ] **Step 1: Create `OperationsPage.tsx`**

创建 `frontend/src/pages/OperationsPage.tsx`：

```tsx
import { useEffect, useState, type ReactNode } from "react";
import {
  BarChart3,
  Bot,
  ChevronDown,
  Code2,
  Loader2,
  PhoneCall,
  Wrench,
} from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultFilters, getFilterOptions, getOperationsOverview } from "../api";
import type {
  DashboardFilters,
  FilterOptions,
  OperationsOverview,
} from "../types";

const kpiIcons = [Bot, Code2, Wrench, PhoneCall];

export function OperationsPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<DashboardFilters>(defaultFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<OperationsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, data] = await Promise.all([
        getFilterOptions(),
        getOperationsOverview(filters),
      ]);
      setFilterOptions(options);
      setOverview(data);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters = filters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getOperationsOverview(nextFilters);
      setOverview(data);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  const activeFilters = overview?.filters ?? filters;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>运营分析</h1>
          <p>工具调用、AI 采纳、代码生成与用户问题单运营分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <FilterGrid
            options={filterOptions}
            filters={activeFilters}
            onChange={setFilters}
            onQuery={() => query(filters)}
          />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载运营数据
        </div>
      ) : overview ? (
        <>
          <section className="kpi-grid">
            <KpiCard
              label="AI 采纳率"
              value={`${overview.kpis.ai_adoption_rate.toFixed(1)}%`}
              change={overview.kpis.ai_adoption_rate_change}
              accent="blue"
              iconIdx={0}
            />
            <KpiCard
              label="AI 生成被采纳代码行数"
              value={overview.kpis.ai_accepted_lines.toLocaleString()}
              change={overview.kpis.ai_accepted_lines_change}
              accent="cyan"
              iconIdx={1}
            />
            <KpiCard
              label="总工具调用次数"
              value={overview.kpis.total_tool_calls.toLocaleString()}
              change={overview.kpis.total_tool_calls_change}
              accent="green"
              iconIdx={2}
            />
            <KpiCard
              label="用户问题单总数"
              value={overview.kpis.total_user_issues.toLocaleString()}
              change={overview.kpis.total_user_issues_change}
              accent="red"
              iconIdx={3}
            />
          </section>

          <section className="operations-chart-grid">
            <ChartPanel title="工具调用 Top 10">
              <ReactECharts option={toolCallTopOption(overview.top_tools)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="工具调用趋势">
              <ReactECharts option={toolCallTrendOption(overview.tool_call_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI 采纳率趋势">
              <ReactECharts option={aiAdoptionTrendOption(overview.ai_adoption_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI 生成代码行数趋势">
              <ReactECharts option={aiAcceptedLinesTrendOption(overview.ai_accepted_lines_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="用户问题单趋势">
              <ReactECharts option={userIssueTrendOption(overview.user_issue_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="不同类型用户问题单">
              <ReactECharts option={userIssuesByTypeOption(overview.user_issues_by_type)} notMerge className="chart" />
            </ChartPanel>
          </section>
        </>
      ) : null}
    </>
  );
}

function FilterGrid({
  options,
  filters,
  onChange,
  onQuery,
}: {
  options: FilterOptions;
  filters: DashboardFilters;
  onChange: (filters: DashboardFilters) => void;
  onQuery: () => void;
}) {
  const fields = [
    ["时间范围", "date_range", options.date_ranges],
    ["统计粒度", "granularity", options.granularities],
    ["PDU", "pdu", options.pdus],
    ["LM团队", "lm_team", options.lm_teams],
    ["用户", "user", options.users],
    ["端类型", "terminal_type", options.terminal_types],
    ["客户端版本", "client_version", options.client_versions],
    ["IDE类型", "ide_type", options.ide_types],
    ["模型", "model", options.models],
  ] as const;

  return (
    <div className="filter-grid">
      {fields.map(([label, key, items]) => (
        <label key={key} className="filter-field">
          <span>{label}</span>
          <select
            value={filters[key]}
            onChange={(event) => onChange({ ...filters, [key]: event.target.value })}
          >
            {items.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <ChevronDown size={14} />
        </label>
      ))}
      <button className="query-button" onClick={onQuery}>
        查询
      </button>
    </div>
  );
}

function KpiCard({
  label,
  value,
  change,
  accent,
  iconIdx,
}: {
  label: string;
  value: string;
  change: string;
  accent: "blue" | "cyan" | "green" | "red";
  iconIdx: number;
}) {
  const Icon = kpiIcons[iconIdx] ?? BarChart3;
  const direction = change.startsWith("-") ? "down" : "up";
  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{label}</h3>
        <div className="kpi-value">{value}</div>
        <p className={`delta ${direction}`}>
          较上期
          <span>
            {direction === "down" ? "▼" : "▲"} {change}
          </span>
        </p>
      </div>
    </article>
  );
}

function ChartPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="panel">
      <div className="panel-header">
        <h2>
          {title}
          <span className="info-dot">i</span>
        </h2>
      </div>
      {children}
    </article>
  );
}

function toolCallTopOption(items: { tool_name: string; call_count: number }[]) {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 16, right: 32, top: 16, bottom: 16, containLabel: true },
    xAxis: { type: "value" },
    yAxis: {
      type: "category",
      data: items.map((i) => i.tool_name).reverse(),
      axisLabel: { width: 90, overflow: "truncate" },
    },
    series: [
      {
        type: "bar",
        data: items.map((i) => i.call_count).reverse(),
        itemStyle: { color: "#3b82f6", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function lineTrendOption(dates: string[], values: number[], color: string, unit?: string) {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 16, right: 24, top: 24, bottom: 24, containLabel: true },
    xAxis: { type: "category", data: dates, boundaryGap: false },
    yAxis: { type: "value", axisLabel: { formatter: unit ? `{value}${unit}` : "{value}" } },
    series: [
      {
        type: "line",
        data: values,
        smooth: true,
        symbol: "none",
        lineStyle: { color, width: 2 },
        areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color }, { offset: 1, color: "rgba(0,0,0,0)" }] } },
      },
    ],
  };
}

function toolCallTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#10b981",
  );
}

function aiAdoptionTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#3b82f6",
    "%",
  );
}

function aiAcceptedLinesTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#06b6d4",
  );
}

function userIssueTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#ef4444",
  );
}

function userIssuesByTypeOption(items: { issue_type: string; count: number }[]) {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 16, right: 24, top: 24, bottom: 24, containLabel: true },
    xAxis: { type: "category", data: items.map((i) => i.issue_type) },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: items.map((i) => i.count),
        itemStyle: { color: "#f59e0b", borderRadius: [4, 4, 0, 0] },
      },
    ],
  };
}
```

- [ ] **Step 2: Verify TypeScript**

Run:
```bash
cd frontend
pnpm exec tsc -b --noEmit
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/OperationsPage.tsx
git commit -m "feat(page): add OperationsPage with 4 KPIs and 6 charts"
```

---

### Task 8: App routing

**Files:**
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `OperationsPage`
- Produces: `/operations` route renders `OperationsPage` instead of placeholder

- [ ] **Step 1: Import and register route**

修改 `frontend/src/App.tsx`：

```typescript
import { OperationsPage } from "./pages/OperationsPage";
```

将：
```tsx
<Route path="/operations" element={<PlaceholderPage title="运营分析" />} />
```
替换为：
```tsx
<Route path="/operations" element={<OperationsPage onUpdatedAt={setUpdatedAt} />} />
```

- [ ] **Step 2: Verify TypeScript**

Run:
```bash
cd frontend
pnpm exec tsc -b --noEmit
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(app): wire /operations route to OperationsPage"
```

---

### Task 9: Styles

**Files:**
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Produces: `.operations-chart-grid` CSS class

- [ ] **Step 1: Append grid styles**

在 `frontend/src/styles.css` 末尾追加：

```css
/* Operations Analysis */

.operations-chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 20px 0;
}

@media (max-width: 1280px) {
  .operations-chart-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .operations-chart-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Verify build**

Run:
```bash
cd frontend
pnpm build
```

Expected: build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles.css
git commit -m "feat(styles): add operations analysis chart grid styles"
```

---

### Task 10: Verification

**Files:**
- None (read-only verification)

- [ ] **Step 1: Backend smoke test**

Run:
```bash
cd backend
python -c "from app.main import app; print([r.path for r in app.routes])"
```

Expected: `/api/operations/overview` present, no exceptions

- [ ] **Step 2: Frontend production build**

Run:
```bash
cd frontend
pnpm build
```

Expected: `dist/` generated with no errors

- [ ] **Step 3: Commit any fixes**

If smoke/build found issues, fix and commit. If clean, no commit needed.

---

## Self-Review Checklist

- [ ] Spec coverage: 4 KPI 卡 + 6 图表全部在 Task 7 实现；后端路由、mock、类型同步覆盖。
- [ ] Placeholder scan: 计划中没有 TBD / TODO / "implement later"。
- [ ] Type consistency: 后端 `OperationsOverview` 与前端 `OperationsOverview` 字段一致；`get_operations_overview` 签名前后端一致。
