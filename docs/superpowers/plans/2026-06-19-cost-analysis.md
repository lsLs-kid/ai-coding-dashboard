# 成本分析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增"成本分析"页面，展示 Token 消耗趋势、模型 Token 分布、PDU Token 排行和可分页的 Token 明细表格。

**Architecture:** 后端新增独立路由组 `/api/cost`；`DashboardDataProvider` 增加两个抽象方法；`MockDashboardDataProvider` 提供 mock 实现。前端新增 `pages/CostPage.tsx`，替换现有 `/cost` 路由的占位组件。

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, React 19, TypeScript 5, ECharts 6, react-router-dom 7, lucide-react

## Global Constraints

- Python 文件用 4 空格缩进
- TypeScript 文件用 2 空格缩进
- 后端无测试框架，验证使用 `curl` 或 `python -c` 导入检查
- 前端无测试框架，验证使用 `pnpm build` 和浏览器目测
- 后端须在 `backend/` 目录下、虚拟环境激活状态下运行
- 前端须在 `frontend/` 目录下运行
- 不改动现有 dashboard/codemerge 路由和 schema；只追加
- 所有新 schema 追加至 `backend/app/schemas.py` 末尾
- 前端新页面放入 `frontend/src/pages/`
- `TokenPageRequest.cost_type` 使用普通 `int`（参考 `MrPageRequest.ai_ratio_threshold` 的 GET query coercion 处理）

---

### Task 1: 后端新增 Schema

**Files:**
- Modify: `backend/app/schemas.py`

**Interfaces:**
- Produces: `CostFilters`, `CostKpi`, `CostTrendPoint`, `ModelCostStats`, `PduCostStats`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`（供 Task 2、3、4 使用）

- [ ] **Step 1: 追加 schema 到 `backend/app/schemas.py` 末尾**

在文件末尾追加以下内容：

```python


# ── Cost Analysis ───────────────────────────────────────────────────────────

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
    cost_type: int = 0  # 0=total, 1=input, 2=output; int for GET query coercion
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

- [ ] **Step 2: 验证 schema 可正常导入**

```bash
cd backend && source .venv/bin/activate
python -c "from app.schemas import CostOverview, TokenPageResponse; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas.py
git commit -m "feat: add cost analysis schemas"
```

---

### Task 2: Provider 接口新增抽象方法

**Files:**
- Modify: `backend/app/services/provider.py`

**Interfaces:**
- Consumes: `CostFilters`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`（来自 Task 1）
- Produces: `DashboardDataProvider.get_cost_overview`, `DashboardDataProvider.get_cost_tokens`（供 Task 3、4 使用）

- [ ] **Step 1: 更新 import 和类定义**

将文件替换为：

```python
from abc import ABC, abstractmethod

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
    TokenDetail,
    TokenPageRequest,
    TokenPageResponse,
    UserDetail,
)


class DashboardDataProvider(ABC):
    """Data-provider boundary.

    Replace MockDashboardDataProvider with a lake-table or CodeHub implementation
    without changing API routes or frontend contracts.
    """

    @abstractmethod
    def get_filter_options(self) -> FilterOptions:
        raise NotImplementedError

    @abstractmethod
    def get_overview(self, filters: DashboardFilters) -> DashboardOverview:
        raise NotImplementedError

    @abstractmethod
    def get_users(self, filters: DashboardFilters) -> list[UserDetail]:
        raise NotImplementedError

    @abstractmethod
    def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]:
        raise NotImplementedError

    @abstractmethod
    def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]:
        raise NotImplementedError

    @abstractmethod
    def export_report(self, filters: DashboardFilters) -> ExportReportResponse:
        raise NotImplementedError

    @abstractmethod
    def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview:
        raise NotImplementedError

    @abstractmethod
    def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse:
        raise NotImplementedError

    @abstractmethod
    def get_cost_overview(self, filters: CostFilters) -> CostOverview:
        raise NotImplementedError

    @abstractmethod
    def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse:
        raise NotImplementedError
```

- [ ] **Step 2: 验证**

```bash
cd backend && source .venv/bin/activate
python -c "from app.services.provider import DashboardDataProvider; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/provider.py
git commit -m "feat: add cost abstract methods to provider interface"
```

---

### Task 3: Mock Provider 实现

**Files:**
- Modify: `backend/app/services/mock_provider.py`

**Interfaces:**
- Consumes: `CostFilters`, `CostKpi`, `CostOverview`, `CostTrendPoint`, `ModelCostStats`, `PduCostStats`, `TokenPageRequest`, `TokenPageResponse`（来自 Task 1）
- Produces: `MockDashboardDataProvider.get_cost_overview`, `MockDashboardDataProvider.get_cost_tokens`

- [ ] **Step 1: 更新 import 块**

在现有 import 中追加 `CostFilters`, `CostKpi`, `CostOverview`, `CostTrendPoint`, `ModelCostStats`, `PduCostStats`, `TokenPageRequest`, `TokenPageResponse`。

完整 import 块如下：

```python
from app.schemas import (
    CodeMergeFilters,
    CodeMergeKpi,
    CodeMergeOverview,
    CostFilters,
    CostKpi,
    CostOverview,
    CostTrendPoint,
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOption,
    FilterOptions,
    Insight,
    KpiMetric,
    MergeTrendPoint,
    ModelCostStats,
    MrDetail,
    MrPageRequest,
    MrPageResponse,
    MrRatioBucket,
    PduCostStats,
    PduMergeStats,
    QuadrantPoint,
    RankingRow,
    RepoMergeStats,
    TokenDetail,
    TokenPageRequest,
    TokenPageResponse,
    TrendPoint,
    UserDetail,
)
```

- [ ] **Step 2: 在 `MockDashboardDataProvider` 类末尾追加两个公开方法和三个私有辅助方法**

在 `_mr_ratio_distribution` 方法之后追加：

```python
    def get_cost_overview(self, filters: CostFilters) -> CostOverview:
        return CostOverview(
            kpis=CostKpi(
                total_tokens=42_860_000,
                input_tokens=25_716_000,
                output_tokens=17_144_000,
                per_user_tokens=33_814.0,
                total_tokens_change="+18.7%",
                input_tokens_change="+21.3%",
                output_tokens_change="+15.1%",
                per_user_tokens_change="+12.4%",
            ),
            trend=self._cost_trend(),
            model_distribution=self._model_cost_distribution(),
            top_pdus=self._top_pdu_cost(),
        )

    def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse:
        all_tokens = self._token_list()
        if request.pdu != "all":
            all_tokens = [t for t in all_tokens if t.pdu == request.pdu]
        if request.lm_team != "all":
            all_tokens = [t for t in all_tokens if t.lm_team == request.lm_team]
        if request.user != "all":
            all_tokens = [t for t in all_tokens if t.user == request.user]
        if request.model != "all":
            all_tokens = [t for t in all_tokens if t.model == request.model]
        sort_fields = {
            "date": lambda t: t.date,
            "input_tokens": lambda t: t.input_tokens,
            "output_tokens": lambda t: t.output_tokens,
            "total_tokens": lambda t: t.total_tokens,
        }
        key_fn = sort_fields.get(request.sort_by, sort_fields["date"])
        all_tokens.sort(key=key_fn, reverse=(request.sort_order == "desc"))
        total = len(all_tokens)
        start = (request.page - 1) * request.page_size
        return TokenPageResponse(
            total=total,
            page=request.page,
            page_size=request.page_size,
            items=all_tokens[start : start + request.page_size],
        )

    def _cost_trend(self) -> list[CostTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        input_tokens =  [980,1120,1050,1280, 990, 940,1100,1220,1350,1180,1260,1380,1320,1150,1420,1280,1390,1450,1310,1240,1410,1100,1340,1560,1680,1440,1620,1550,1460,1380]
        output_tokens = [620, 780, 700, 860, 650, 610, 730, 800, 890, 760, 840, 920, 880, 770, 960, 860, 940, 980, 870, 820, 950, 720, 880,1020,1100, 940,1060,1020, 960, 900]
        return [
            CostTrendPoint(date=d, input_tokens=i * 1000, output_tokens=o * 1000, total_tokens=(i + o) * 1000)
            for d, i, o in zip(dates, input_tokens, output_tokens)
        ]

    def _model_cost_distribution(self) -> list[ModelCostStats]:
        rows = [
            ("MiniMax-M2.7", 15_430_000, 10_286_000),
            ("DeepSeek-V3",  10_286_000, 6_858_000),
        ]
        return [
            ModelCostStats(model=r[0], input_tokens=r[1], output_tokens=r[2], total_tokens=r[1] + r[2])
            for r in rows
        ]

    def _top_pdu_cost(self) -> list[PduCostStats]:
        rows = [
            ("无线PDU", 18_540_000),
            ("软件PDU", 12_360_000),
            ("协议栈PDU", 7_890_000),
            ("驱动PDU", 3_270_000),
        ]
        return [PduCostStats(pdu=r[0], total_tokens=r[1]) for r in rows]

    def _token_list(self) -> list[TokenDetail]:
        models = ["MiniMax-M2.7", "DeepSeek-V3"]
        pdus = ["无线PDU", "软件PDU", "协议栈PDU", "驱动PDU", "测试PDU"]
        teams = ["架构与算法LM", "软件平台LM", "协议栈LM", "驱动开发LM", "测试验证LM"]
        users = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十"]
        rows = []
        for i in range(60):
            idx = i % 5
            base = 300000 - i * 3500
            ratio = 0.6 if i % 3 == 0 else 0.55 if i % 3 == 1 else 0.5
            inp = int(base * ratio)
            out = int(base * (1 - ratio))
            rows.append(TokenDetail(
                id=f"tk-{i + 1:03d}",
                date=f"2025-05-{max(1, 20 - i // 6):02d}",
                user=users[i % 8],
                model=models[i % 2],
                input_tokens=inp,
                output_tokens=out,
                total_tokens=inp + out,
                trace_id=f"trace_{i:04d}",
                status_code=200,
            ))
        return rows
```

注意：mock 的 `TokenDetail` 目前没有 `pdu` / `lm_team` 字段。由于 schema 里没有，任务要求表格展示 PDU/LM 团队，因此需要同时修改 `TokenDetail` 的 schema。但这是 Task 1 应该完成的工作，请在 Task 3 开始前回头修改 Task 1：给 `TokenDetail` 追加 `pdu: str` 和 `lm_team: str` 字段，并同步更新 `frontend/src/types.ts` 的 `TokenDetail` 接口。

- [ ] **Step 3: 验证 mock provider 可导入并返回预期数据**

```bash
cd backend && source .venv/bin/activate
python -c "
from app.services.mock_provider import MockDashboardDataProvider
from app.schemas import CostFilters, TokenPageRequest
p = MockDashboardDataProvider()
ov = p.get_cost_overview(CostFilters())
print('kpis ok:', ov.kpis.total_tokens)
print('trend ok:', len(ov.trend))
print('models ok:', len(ov.model_distribution))
print('top pdus ok:', len(ov.top_pdus))
toks = p.get_cost_tokens(TokenPageRequest())
print('tokens ok: total =', toks.total, 'items =', len(toks.items))
"
```

Expected:
```
kpis ok: 42860000
trend ok: 30
models ok: 2
top pdus ok: 4
tokens ok: total = 60 items = 20
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/mock_provider.py
git commit -m "feat: implement cost mock data provider"
```

---

### Task 4: 新路由文件 + 挂载到 main.py

**Files:**
- Create: `backend/app/api/cost_routes.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `CostFilters`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`（Task 1）；`get_cost_overview`, `get_cost_tokens`（Task 2/3）
- Produces: `POST /api/cost/overview`, `GET /api/cost/tokens`

- [ ] **Step 1: 创建 `backend/app/api/cost_routes.py`**

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import CostFilters, CostOverview, TokenPageRequest, TokenPageResponse
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/cost", tags=["cost"])


@router.post("/overview", response_model=CostOverview)
def get_cost_overview(
    filters: CostFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> CostOverview:
    return provider.get_cost_overview(filters)


@router.get("/tokens", response_model=TokenPageResponse)
def get_cost_tokens(
    request: Annotated[TokenPageRequest, Depends()],
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> TokenPageResponse:
    return provider.get_cost_tokens(request)
```

- [ ] **Step 2: 在 `backend/app/main.py` 中挂载新路由**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.codemerge_routes import router as codemerge_router
from app.api.cost_routes import router as cost_router
from app.api.routes import router as dashboard_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(dashboard_router, prefix=settings.api_prefix)
    app.include_router(codemerge_router, prefix=settings.api_prefix)
    app.include_router(cost_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 3: 启动后端，验证两个端点可访问**

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
sleep 2
curl -s -X POST http://127.0.0.1:8000/api/cost/overview \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool | head -20
curl -s "http://127.0.0.1:8000/api/cost/tokens?page=1&page_size=3" | python -m json.tool | head -20
```

Expected: 两次 curl 均返回合法 JSON，第一个包含 `"kpis"` 字段，第二个包含 `"total": 60`。

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/cost_routes.py backend/app/main.py
git commit -m "feat: add /api/cost routes and mount in main"
```

---

### Task 5: 前端新增类型定义

**Files:**
- Modify: `frontend/src/types.ts`

**Interfaces:**
- Produces: `CostFilters`, `CostKpi`, `CostTrendPoint`, `ModelCostStats`, `PduCostStats`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`（供 Task 6、7、8 使用）

- [ ] **Step 1: 追加类型到 `frontend/src/types.ts` 末尾**

```typescript
// ── Cost Analysis ───────────────────────────────────────────────────────────

export interface CostFilters {
  date_range: string;
  granularity: "day" | "week" | "month";
  pdu: string;
  lm_team: string;
  user: string;
  terminal_type: string;
  client_version: string;
  ide_type: string;
  model: string;
  cost_type: "input" | "output" | "total";
}

export interface CostKpi {
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  per_user_tokens: number;
  total_tokens_change: string;
  input_tokens_change: string;
  output_tokens_change: string;
  per_user_tokens_change: string;
}

export interface CostTrendPoint {
  date: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface ModelCostStats {
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface PduCostStats {
  pdu: string;
  total_tokens: number;
}

export interface CostOverview {
  kpis: CostKpi;
  trend: CostTrendPoint[];
  model_distribution: ModelCostStats[];
  top_pdus: PduCostStats[];
}

export interface TokenPageRequest {
  date_range: string;
  granularity: "day" | "week" | "month";
  pdu: string;
  lm_team: string;
  user: string;
  terminal_type: string;
  client_version: string;
  ide_type: string;
  model: string;
  cost_type: 0 | 1 | 2;
  page: number;
  page_size: number;
  sort_by: string;
  sort_order: "asc" | "desc";
}

export interface TokenPageResponse {
  total: number;
  page: number;
  page_size: number;
  items: TokenDetail[];
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat: add cost analysis TypeScript types"
```

---

### Task 6: 前端 API 层新增函数

**Files:**
- Modify: `frontend/src/api.ts`

**Interfaces:**
- Consumes: `CostFilters`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`（Task 5）
- Produces: `defaultCostFilters`, `getCostOverview`, `getCostTokens`（供 Task 8 使用）

- [ ] **Step 1: 更新 `frontend/src/api.ts`**

在文件末尾、最后一个函数之后追加：

```typescript
export const defaultCostFilters: CostFilters = {
  date_range: "last_30_days",
  granularity: "day",
  pdu: "all",
  lm_team: "all",
  user: "all",
  terminal_type: "all",
  client_version: "all",
  ide_type: "all",
  model: "all",
  cost_type: "total",
};

const COST_TYPE_MAP: Record<CostFilters["cost_type"], 0 | 1 | 2> = {
  total: 0,
  input: 1,
  output: 2,
};

export function getCostOverview(filters: CostFilters): Promise<CostOverview> {
  return request<CostOverview>("/cost/overview", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}

export function getCostTokens(req: TokenPageRequest): Promise<TokenPageResponse> {
  const params = new URLSearchParams({
    date_range: req.date_range,
    granularity: req.granularity,
    pdu: req.pdu,
    lm_team: req.lm_team,
    user: req.user,
    terminal_type: req.terminal_type,
    client_version: req.client_version,
    ide_type: req.ide_type,
    model: req.model,
    cost_type: String(req.cost_type),
    page: String(req.page),
    page_size: String(req.page_size),
    sort_by: req.sort_by,
    sort_order: req.sort_order,
  });
  return request<TokenPageResponse>(`/cost/tokens?${params.toString()}`);
}
```

同时在 `api.ts` 顶部 import 中加入 `CostFilters`, `CostOverview`, `TokenPageRequest`, `TokenPageResponse`。

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api.ts
git commit -m "feat: add getCostOverview and getCostTokens API functions"
```

---

### Task 7: 更新 App.tsx 的 /cost 路由

**Files:**
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `CostPage`（Task 8）
- Produces: `/cost` 路由渲染 `CostPage`（不再渲染 `PlaceholderPage`）

- [ ] **Step 1: 替换 PlaceholderPage 导入为 CostPage，并替换 /cost 路由**

找到 App.tsx 中的：

```tsx
import { CostMergePage } from "./pages/CostMergePage";
```

不存在，当前 App.tsx 只有 OverviewPage 和 CodeMergePage 导入。新增：

```tsx
import { CostPage } from "./pages/CostPage";
```

然后替换 Route：

```tsx
<Route path="/cost" element={<CostPage onUpdatedAt={setUpdatedAt} />} />
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: wire /cost route to CostPage"
```

---

### Task 8: 新建 CostPage

**Files:**
- Create: `frontend/src/pages/CostPage.tsx`

**Interfaces:**
- Consumes: `defaultCostFilters`, `getCostOverview`, `getCostTokens`, `getFilterOptions`（Task 6）；所有 cost 类型（Task 5）
- Produces: `CostPage({ onUpdatedAt })`（供 App.tsx Task 7 使用）

- [ ] **Step 1: 创建 `frontend/src/pages/CostPage.tsx`**

完整文件内容如下：

```tsx
import { useEffect, useState } from "react";
import { BarChart3, ChevronDown, Coins, Loader2, TrendingUp, Users } from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultCostFilters, getCostTokens, getCostOverview, getFilterOptions } from "../api";
import type {
  CostFilters,
  CostOverview,
  CostTrendPoint,
  FilterOptions,
  ModelCostStats,
  PduCostStats,
  TokenPageResponse,
} from "../types";

const costKpiIcons = [Coins, TrendingUp, TrendingUp, Users];

const costTypeOptions = [
  { label: "Total Token", value: "total" as const },
  { label: "Input Token", value: "input" as const },
  { label: "Output Token", value: "output" as const },
];

const COST_TYPE_MAP: Record<CostFilters["cost_type"], 0 | 1 | 2> = {
  total: 0,
  input: 1,
  output: 2,
};

export function CostPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<CostFilters>(defaultCostFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<CostOverview | null>(null);
  const [tokens, setTokens] = useState<TokenPageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tableState, setTableState] = useState({
    page: 1,
    sort_by: "date",
    sort_order: "desc" as "asc" | "desc",
  });

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, ovData, tokData] = await Promise.all([
        getFilterOptions(),
        getCostOverview(filters),
        getCostTokens({ ...filters, ...tableState, cost_type: COST_TYPE_MAP[filters.cost_type], page_size: 20 }),
      ]);
      setFilterOptions(options);
      setOverview(ovData);
      setTokens(tokData);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters: CostFilters) {
    setIsLoading(true);
    setError(null);
    const nextTable = { ...tableState, page: 1 };
    setTableState(nextTable);
    try {
      const [ovData, tokData] = await Promise.all([
        getCostOverview(nextFilters),
        getCostTokens({ ...nextFilters, ...nextTable, cost_type: COST_TYPE_MAP[nextFilters.cost_type], page_size: 20 }),
      ]);
      setOverview(ovData);
      setTokens(tokData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchTokens(next: typeof tableState, currentFilters: CostFilters) {
    setTableLoading(true);
    try {
      const tokData = await getCostTokens({
        ...currentFilters,
        ...next,
        cost_type: COST_TYPE_MAP[currentFilters.cost_type],
        page_size: 20,
      });
      setTokens(tokData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setTableLoading(false);
    }
  }

  function handleSort(col: string) {
    const nextOrder: "asc" | "desc" =
      tableState.sort_by === col && tableState.sort_order === "desc" ? "asc" : "desc";
    const next = { ...tableState, sort_by: col, sort_order: nextOrder, page: 1 };
    setTableState(next);
    void fetchTokens(next, filters);
  }

  function handlePage(page: number) {
    const next = { ...tableState, page };
    setTableState(next);
    void fetchTokens(next, filters);
  }

  function handleFilterChange(f: CostFilters) {
    setFilters(f);
    void query(f);
  }

  return (
    <>
      <header className="page-header">
        <div>
          <h1>成本分析</h1>
          <p>AI Coding Token 消耗趋势与分布分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <CostFilterBar options={filterOptions} filters={filters} onChange={handleFilterChange} />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载成本数据
        </div>
      ) : overview ? (
        <>
          <section className="cost-kpi-grid">
            <CostKpiCard
              label="总 Token 消耗"
              value={overview.kpis.total_tokens.toLocaleString()}
              change={overview.kpis.total_tokens_change}
              accent="blue"
              iconIdx={0}
            />
            <CostKpiCard
              label="Input Token"
              value={overview.kpis.input_tokens.toLocaleString()}
              change={overview.kpis.input_tokens_change}
              accent="cyan"
              iconIdx={1}
            />
            <CostKpiCard
              label="Output Token"
              value={overview.kpis.output_tokens.toLocaleString()}
              change={overview.kpis.output_tokens_change}
              accent="green"
              iconIdx={2}
            />
            <CostKpiCard
              label="人均 Token 消耗"
              value={Math.round(overview.kpis.per_user_tokens).toLocaleString()}
              change={overview.kpis.per_user_tokens_change}
              accent="red"
              iconIdx={3}
            />
          </section>

          <section className="cost-chart-grid">
            <article className="panel">
              <div className="panel-header">
                <h2>
                  Token 消耗趋势<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={tokenTrendOption(overview.trend, filters.cost_type)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  模型 Token 分布<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={modelDistributionOption(overview.model_distribution)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  PDU Token Top 10<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={pduTopOption(overview.top_pdus)} notMerge style={{ height: 220 }} />
            </article>
          </section>

          {tokens ? (
            <TokenTable
              response={tokens}
              sortBy={tableState.sort_by}
              sortOrder={tableState.sort_order}
              onSort={handleSort}
              onPage={handlePage}
              loading={tableLoading}
            />
          ) : null}
        </>
      ) : null}
    </>
  );
}

function CostFilterBar({
  options,
  filters,
  onChange,
}: {
  options: FilterOptions;
  filters: CostFilters;
  onChange: (f: CostFilters) => void;
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
    <div className="cost-filter-grid">
      {fields.map(([label, key, items]) => (
        <label key={key} className="filter-field">
          <span>{label}</span>
          <select
            value={filters[key]}
            onChange={(e) => onChange({ ...filters, [key]: e.target.value })}
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
      <label className="filter-field">
        <span>成本类型</span>
        <select
          value={filters.cost_type}
          onChange={(e) =>
            onChange({ ...filters, cost_type: e.target.value as CostFilters["cost_type"] })
          }
        >
          {costTypeOptions.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
    </div>
  );
}

function CostKpiCard({
  label,
  value,
  change,
  accent,
  iconIdx,
}: {
  label: string;
  value: string;
  change: string | null;
  accent: "blue" | "red" | "green" | "cyan";
  iconIdx: number;
}) {
  const Icon = costKpiIcons[iconIdx] ?? BarChart3;
  const direction =
    change == null ? "flat" : change.startsWith("+") ? "up" : change.startsWith("-") ? "down" : "flat";
  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{label}</h3>
        <div className="kpi-value">{value}</div>
        {change ? (
          <p className={`delta ${direction}`}>
            较上期<span> {change}</span>
          </p>
        ) : null}
      </div>
    </article>
  );
}

function TokenTable({
  response,
  sortBy,
  sortOrder,
  onSort,
  onPage,
  loading,
}: {
  response: TokenPageResponse;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
  onPage: (page: number) => void;
  loading: boolean;
}) {
  const totalPages = Math.ceil(response.total / response.page_size);
  const start = Math.max(1, response.page - 2);
  const end = Math.min(totalPages, start + 4);
  const pageNums: number[] = [];
  for (let p = start; p <= end; p++) pageNums.push(p);

  return (
    <section className="panel detail-panel" style={{ opacity: loading ? 0.6 : 1 }}>
      <div className="panel-header" style={{ padding: "14px 0 0" }}>
        <h2>
          Token 明细<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <SortTh label="日期" col="date" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <th>PDU</th>
            <th>LM团队</th>
            <th>用户</th>
            <th>模型</th>
            <SortTh label="Input Token" col="input_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="Output Token" col="output_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="Total Token" col="total_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
          </tr>
        </thead>
        <tbody>
          {response.items.map((row) => (
            <tr key={row.id}>
              <td>{row.date}</td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.user}</td>
              <td>{row.model}</td>
              <td>{row.input_tokens.toLocaleString()}</td>
              <td>{row.output_tokens.toLocaleString()}</td>
              <td>{row.total_tokens.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        <span>共 {response.total} 条</span>
        <button disabled={response.page <= 1} onClick={() => onPage(response.page - 1)}>
          ‹
        </button>
        {pageNums.map((p) => (
          <button
            key={p}
            className={response.page === p ? "is-active" : ""}
            onClick={() => onPage(p)}
          >
            {p}
          </button>
        ))}
        <button disabled={response.page >= totalPages} onClick={() => onPage(response.page + 1)}>
          ›
        </button>
        <span>每页 {response.page_size} 条</span>
      </div>
    </section>
  );
}

function SortTh({
  label,
  col,
  sortBy,
  sortOrder,
  onSort,
}: {
  label: string;
  col: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
}) {
  const arrow = sortBy === col ? (sortOrder === "desc" ? " ↓" : " ↑") : " ↕";
  return (
    <th className="th-sortable" onClick={() => onSort(col)}>
      {label}
      {arrow}
    </th>
  );
}

function baseTextStyle() {
  return { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" };
}

function tokenTrendOption(trend: CostTrendPoint[], costType: CostFilters["cost_type"]) {
  const fieldMap = {
    total: { field: "total_tokens" as const, color: "#256ff6", name: "Total Token" },
    input: { field: "input_tokens" as const, color: "#10b99a", name: "Input Token" },
    output: { field: "output_tokens" as const, color: "#ef3445", name: "Output Token" },
  };
  const cfg = fieldMap[costType];
  return {
    grid: { left: 56, right: 20, top: 28, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: baseTextStyle(),
    xAxis: { type: "category", data: trend.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "Token 数", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        name: cfg.name,
        data: trend.map((d) => d[cfg.field]),
        type: "line",
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: cfg.color + "1A" },
        lineStyle: { width: 3, color: cfg.color },
        itemStyle: { color: cfg.color },
      },
    ],
  };
}

function modelDistributionOption(models: ModelCostStats[]) {
  const reversed = [...models].sort((a, b) => a.total_tokens - b.total_tokens);
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 120, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "Token 数" },
    yAxis: { type: "category", data: reversed.map((d) => d.model) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.total_tokens),
        itemStyle: { color: "#256ff6", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function pduTopOption(pdus: PduCostStats[]) {
  const reversed = [...pdus].sort((a, b) => a.total_tokens - b.total_tokens);
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 90, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "Token 数" },
    yAxis: { type: "category", data: reversed.map((d) => d.pdu) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.total_tokens),
        itemStyle: { color: "#10b99a", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && pnpm build 2>&1 | tail -10
```

Expected: `built in` 字样，无 `error TS` 输出。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/CostPage.tsx
git commit -m "feat: add CostPage with KPI cards, 3 charts, and paginated Token table"
```

---

### Task 9: 追加 CSS

**Files:**
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `.cost-kpi-grid`, `.cost-chart-grid`, `.cost-filter-grid`（在 Task 8 的 JSX 中使用）

- [ ] **Step 1: 在 `frontend/src/styles.css` 末尾追加**

```css

/* ── Cost Analysis ─────────────────────────────────────────────────────────── */

.cost-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.cost-chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.cost-filter-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  align-items: end;
}

@media (max-width: 1500px) {
  .cost-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cost-chart-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && pnpm build 2>&1 | tail -4
```

Expected: `built in` 字样，无 `error TS` 输出。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles.css
git commit -m "feat: add CSS for cost analysis page"
```

---

## Spec Coverage Check

| Spec 要求 | 对应 Task |
|---|---|
| 4 张 KPI 卡 | Task 8 |
| Token 趋势图 | Task 8 |
| 模型 Token 分布 | Task 3（mock）+ Task 8（图表） |
| PDU Token Top 10 | Task 3（mock）+ Task 8（图表） |
| 分页 Token 表格 | Task 3（mock）+ Task 8（表格） |
| 成本类型筛选 | Task 1（schema）+ Task 6（API）+ Task 8（UI） |
| 独立 `/api/cost` 路由 | Task 4 |
| 不改动现有路由/schema | 所有 Task |

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-19-cost-analysis.md`. Two execution options:

**1. Subagent-Driven (recommended)** — 每个 Task 派发独立 subagent，任务间 review，快速迭代

**2. Inline Execution** — 在当前 session 中逐 Task 执行

Which approach?
