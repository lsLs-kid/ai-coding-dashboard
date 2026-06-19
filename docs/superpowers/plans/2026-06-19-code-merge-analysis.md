# 代码入库分析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增"代码入库分析"页面，含 KPI 卡片、4 张 ECharts 图表、分页 MR 明细表，后端新增 `/api/codemerge` 路由组。

**Architecture:** 后端新增独立路由文件 `codemerge_routes.py`，挂载于 `/api/codemerge`；`DashboardDataProvider` 增加两个抽象方法；`MockDashboardDataProvider` 提供 mock 实现。前端将 `App.tsx` 拆分为 shell + `OverviewPage` + `CodeMergePage`，页面间通过 `activePage` 状态切换。

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, React 19, TypeScript 5, ECharts 6, lucide-react

## Global Constraints

- Python 文件用 4 空格缩进
- TypeScript 文件用 2 空格缩进
- 后端无测试框架，验证使用 `curl`；前端无测试框架，验证使用浏览器目测
- 后端须在 `backend/` 目录下、虚拟环境激活状态下运行
- 前端须在 `frontend/` 目录下运行
- 不改动现有 dashboard 路由和 schema；只追加
- 所有新 schema 追加至 `backend/app/schemas.py` 末尾
- 前端新页面放入 `frontend/src/pages/`

---

### Task 1: 后端新增 Schema

**Files:**
- Modify: `backend/app/schemas.py`

**Interfaces:**
- Produces: `CodeMergeFilters`, `CodeMergeKpi`, `PduMergeStats`, `MergeTrendPoint`, `RepoMergeStats`, `ContributorMergeStats`, `CodeMergeOverview`, `MrPageRequest`, `MrPageResponse`（供 Task 2、3、4 使用）

- [ ] **Step 1: 追加 schema 到 `backend/app/schemas.py` 末尾**

在文件末尾（第 140 行之后）追加以下内容：

```python


# ── Code Merge Analysis ─────────────────────────────────────────────────────

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
    ai_lines_change: str
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
    date_range: str = "last_30_days"
    granularity: Literal["day", "week", "month"] = "day"
    pdu: str = "all"
    lm_team: str = "all"
    ai_ratio_threshold: Literal[30, 50, 70] = 50
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

- [ ] **Step 2: 验证 schema 可正常导入**

```bash
cd backend && source .venv/bin/activate
python -c "from app.schemas import CodeMergeOverview, MrPageResponse; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas.py
git commit -m "feat: add code merge analysis schemas"
```

---

### Task 2: Provider 接口新增抽象方法

**Files:**
- Modify: `backend/app/services/provider.py`

**Interfaces:**
- Consumes: `CodeMergeFilters`, `CodeMergeOverview`, `MrPageRequest`, `MrPageResponse`（来自 Task 1）
- Produces: `DashboardDataProvider.get_codemerge_overview`, `DashboardDataProvider.get_codemerge_mrs`（供 Task 3、4 使用）

- [ ] **Step 1: 更新 `backend/app/services/provider.py` 的 import 和类定义**

将文件改为：

```python
from abc import ABC, abstractmethod

from app.schemas import (
    CodeMergeFilters,
    CodeMergeOverview,
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOptions,
    MrDetail,
    MrPageRequest,
    MrPageResponse,
    TokenDetail,
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
git commit -m "feat: add codemerge abstract methods to provider interface"
```

---

### Task 3: Mock Provider 实现

**Files:**
- Modify: `backend/app/services/mock_provider.py`

**Interfaces:**
- Consumes: `CodeMergeFilters`, `CodeMergeKpi`, `CodeMergeOverview`, `ContributorMergeStats`, `MergeTrendPoint`, `MrPageRequest`, `MrPageResponse`, `PduMergeStats`, `RepoMergeStats`（来自 Task 1）
- Produces: `MockDashboardDataProvider.get_codemerge_overview`, `MockDashboardDataProvider.get_codemerge_mrs`

- [ ] **Step 1: 更新 `backend/app/services/mock_provider.py` 的 import 块**

将文件顶部 import 替换为：

```python
from app.schemas import (
    CodeMergeFilters,
    CodeMergeKpi,
    CodeMergeOverview,
    ContributorMergeStats,
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOption,
    FilterOptions,
    Insight,
    KpiMetric,
    MergeTrendPoint,
    MrDetail,
    MrPageRequest,
    MrPageResponse,
    PduMergeStats,
    QuadrantPoint,
    RankingRow,
    RepoMergeStats,
    TokenDetail,
    TrendPoint,
    UserDetail,
)
from app.services.provider import DashboardDataProvider
```

- [ ] **Step 2: 在 `MockDashboardDataProvider` 类末尾追加两个公开方法和四个私有辅助方法**

在 `_insights` 方法之后、类定义结束前追加：

```python
    def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview:
        return CodeMergeOverview(
            kpis=CodeMergeKpi(
                total_ai_lines=2_456_892,
                total_lines=7_842_314,
                overall_ai_ratio=31.3,
                total_mrs=1847,
                ai_assisted_mrs=892,
                ai_assisted_ratio=48.3,
                total_repos=127,
                ai_lines_change="+24.3%",
                ai_ratio_change="+4.5pp",
                mr_count_change="+18.2%",
                ai_assisted_ratio_change="+6.1pp",
            ),
            pdu_breakdown=[
                PduMergeStats(pdu="无线PDU", total_lines=2_456_000, ai_lines=904_000, ai_ratio=36.8, mr_count=524, active_contributors=186),
                PduMergeStats(pdu="软件PDU", total_lines=1_987_000, ai_lines=658_000, ai_ratio=33.1, mr_count=412, active_contributors=141),
                PduMergeStats(pdu="协议栈PDU", total_lines=1_542_000, ai_lines=469_000, ai_ratio=30.4, mr_count=318, active_contributors=108),
                PduMergeStats(pdu="驱动PDU", total_lines=1_287_000, ai_lines=368_000, ai_ratio=28.6, mr_count=284, active_contributors=97),
                PduMergeStats(pdu="测试PDU", total_lines=570_314, ai_lines=155_000, ai_ratio=27.2, mr_count=209, active_contributors=83),
            ],
            trend=self._codemerge_trend(),
            top_repos=self._top_repos(),
            contributors=self._contributors(),
        )

    def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse:
        all_mrs = self._mr_list()
        if request.pdu != "all":
            all_mrs = [m for m in all_mrs if m.pdu == request.pdu]
        if request.lm_team != "all":
            all_mrs = [m for m in all_mrs if m.lm_team == request.lm_team]
        sort_fields = {
            "merged_at": lambda m: m.merged_at,
            "ai_mr_ratio": lambda m: m.ai_mr_ratio,
            "ai_lines": lambda m: m.ai_lines,
            "total_lines": lambda m: m.total_lines,
        }
        key_fn = sort_fields.get(request.sort_by, sort_fields["merged_at"])
        all_mrs.sort(key=key_fn, reverse=(request.sort_order == "desc"))
        total = len(all_mrs)
        start = (request.page - 1) * request.page_size
        return MrPageResponse(
            total=total,
            page=request.page,
            page_size=request.page_size,
            items=all_mrs[start : start + request.page_size],
        )

    def _codemerge_trend(self) -> list[MergeTrendPoint]:
        dates = [
            "04-21","04-22","04-23","04-24","04-25","04-26","04-27","04-28","04-29","04-30",
            "05-01","05-02","05-03","05-04","05-05","05-06","05-07","05-08","05-09","05-10",
            "05-11","05-12","05-13","05-14","05-15","05-16","05-17","05-18","05-19","05-20",
        ]
        ai_lines =    [62000,78000,71000,85000,68000,64000,72000,80000,89000,75000,83000,91000,88000,76000,95000,84000,92000,98000,87000,81000,94000,72000,88000,104000,112000,96000,108000,103000,97000,92000]
        total_lines = [248000,292000,248000,306000,255000,226000,263000,293000,313000,271000,303000,318000,305000,272000,332000,296000,318000,338000,296000,278000,319000,245000,296000,345000,368000,315000,349000,340000,318000,301000]
        ratios =      [25.0,26.7,28.6,27.8,26.7,28.3,27.4,27.3,28.4,27.7,27.4,28.6,28.9,27.9,28.6,28.4,28.9,29.0,29.4,29.1,29.5,29.4,29.7,30.1,30.4,30.5,30.9,30.3,30.5,30.6]
        mr_counts =   [42,55,48,61,51,44,53,58,64,52,60,67,63,55,70,62,68,72,65,58,69,51,63,77,83,70,79,76,72,68]
        return [
            MergeTrendPoint(date=d, total_lines=tl, ai_lines=al, ai_ratio=ar, mr_count=mc)
            for d, tl, al, ar, mc in zip(dates, total_lines, ai_lines, ratios, mr_counts)
        ]

    def _top_repos(self) -> list[RepoMergeStats]:
        rows = [
            ("wireless/baseband", 98, 1_234_000, 487_000, 39.5),
            ("platform/runtime",  84,   987_000, 368_000, 37.3),
            ("protocol/stack",    76,   842_000, 312_000, 37.1),
            ("driver/kernel",     68,   756_000, 268_000, 35.4),
            ("qa/framework",      54,   489_000, 168_000, 34.4),
            ("wireless/modem",    49,   432_000, 145_000, 33.6),
            ("platform/sdk",      43,   378_000, 124_000, 32.8),
            ("driver/display",    38,   312_000,  98_000, 31.4),
            ("protocol/mac",      34,   278_000,  86_000, 30.9),
            ("qa/integration",    29,   234_000,  70_000, 29.9),
        ]
        return [RepoMergeStats(repository=r[0], mr_count=r[1], total_lines=r[2], ai_lines=r[3], ai_ratio=r[4]) for r in rows]

    def _contributors(self) -> list[ContributorMergeStats]:
        rows = [
            ("张三", "无线PDU", 18, 34820, 12842, 36.9),
            ("李四", "软件PDU", 14, 26320,  8731, 33.2),
            ("王五", "协议栈PDU", 11, 18160, 6542, 36.0),
            ("赵六", "驱动PDU",   9, 15240,  5231, 34.3),
            ("孙七", "测试PDU",   7, 12840,  4112, 32.0),
            ("周八", "无线PDU",  15, 28640, 10234, 35.7),
            ("吴九", "软件PDU",  12, 22180,  7124, 32.1),
            ("郑十", "协议栈PDU", 8, 16420,  5432, 33.1),
            ("陈一", "驱动PDU",  11, 19820,  6234, 31.5),
            ("林二", "测试PDU",   6, 10640,  3124, 29.4),
            ("黄三", "无线PDU",  20, 38240, 14982, 39.2),
            ("冯四", "软件PDU",   9, 17640,  5824, 33.0),
            ("袁五", "协议栈PDU",13, 23840,  8124, 34.1),
            ("许六", "驱动PDU",   7, 13280,  4012, 30.2),
            ("曹七", "无线PDU",  16, 30480, 11824, 38.8),
        ]
        return [ContributorMergeStats(name=r[0], pdu=r[1], mr_count=r[2], total_lines=r[3], ai_lines=r[4], ai_ratio=r[5]) for r in rows]

    def _mr_list(self) -> list[MrDetail]:
        pdus    = ["无线PDU",   "软件PDU",   "协议栈PDU", "驱动PDU",   "测试PDU"]
        teams   = ["架构与算法LM","软件平台LM","协议栈LM",  "驱动开发LM","测试验证LM"]
        repos   = ["wireless/baseband","platform/runtime","protocol/stack","driver/kernel","qa/framework",
                   "wireless/modem",   "platform/sdk",    "driver/display","protocol/mac", "qa/integration"]
        authors = ["张三","李四","王五","赵六","孙七","周八","吴九","郑十"]
        rows = []
        for i in range(50):
            idx = i % 5
            total = max(1000, 34820 - i * 520)
            ratio = round(max(10.0, 36.9 - i * 0.3), 1)
            ai = int(total * ratio / 100)
            rows.append(MrDetail(
                mr_id=f"MR-{10291 - i}",
                repository=repos[i % 10],
                author=authors[i % 8],
                pdu=pdus[idx],
                lm_team=teams[idx],
                merged_at=f"2025-05-{max(1, 20 - i // 5):02d} {max(0, 10 - i % 5):02d}:42",
                total_lines=total,
                ai_lines=ai,
                ai_mr_ratio=ratio,
                status="merged",
            ))
        return rows
```

- [ ] **Step 3: 验证 mock provider 可导入**

```bash
cd backend && source .venv/bin/activate
python -c "
from app.services.mock_provider import MockDashboardDataProvider
from app.schemas import CodeMergeFilters, MrPageRequest
p = MockDashboardDataProvider()
ov = p.get_codemerge_overview(CodeMergeFilters())
print('kpis ok:', ov.kpis.total_ai_lines)
mrs = p.get_codemerge_mrs(MrPageRequest())
print('mrs ok: total =', mrs.total, 'items =', len(mrs.items))
"
```

Expected:
```
kpis ok: 2456892
mrs ok: total = 50 items = 20
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/mock_provider.py
git commit -m "feat: implement codemerge mock data provider"
```

---

### Task 4: 新路由文件 + 挂载到 main.py

**Files:**
- Create: `backend/app/api/codemerge_routes.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `CodeMergeFilters`, `CodeMergeOverview`, `MrPageRequest`, `MrPageResponse`（Task 1）；`get_codemerge_overview`, `get_codemerge_mrs`（Task 2/3）
- Produces: `GET /api/codemerge/mrs`, `POST /api/codemerge/overview`

- [ ] **Step 1: 创建 `backend/app/api/codemerge_routes.py`**

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import CodeMergeFilters, CodeMergeOverview, MrPageRequest, MrPageResponse
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/codemerge", tags=["codemerge"])


@router.post("/overview", response_model=CodeMergeOverview)
def get_codemerge_overview(
    filters: CodeMergeFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> CodeMergeOverview:
    return provider.get_codemerge_overview(filters)


@router.get("/mrs", response_model=MrPageResponse)
def get_codemerge_mrs(
    request: Annotated[MrPageRequest, Depends()],
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> MrPageResponse:
    return provider.get_codemerge_mrs(request)
```

- [ ] **Step 2: 在 `backend/app/main.py` 中挂载新路由**

在 `from app.api.routes import router as dashboard_router` 下方追加一行，并在 `app.include_router(dashboard_router, ...)` 下方追加挂载：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.codemerge_routes import router as codemerge_router
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
curl -s -X POST http://127.0.0.1:8000/api/codemerge/overview \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool | head -20
curl -s "http://127.0.0.1:8000/api/codemerge/mrs?page=1&page_size=3" | python -m json.tool | head -20
```

Expected: 两次 curl 均返回合法 JSON，第一个包含 `"kpis"` 字段，第二个包含 `"total": 50`。

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/codemerge_routes.py backend/app/main.py
git commit -m "feat: add /api/codemerge routes and mount in main"
```

---

### Task 5: 前端新增类型定义

**Files:**
- Modify: `frontend/src/types.ts`

**Interfaces:**
- Produces: `CodeMergeFilters`, `CodeMergeKpi`, `PduMergeStats`, `MergeTrendPoint`, `RepoMergeStats`, `ContributorMergeStats`, `CodeMergeOverview`, `MrPageRequest`, `MrPageResponse`（供 Task 6、7、8 使用）

- [ ] **Step 1: 在 `frontend/src/types.ts` 末尾追加**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat: add code merge analysis TypeScript types"
```

---

### Task 6: 前端 API 层新增函数

**Files:**
- Modify: `frontend/src/api.ts`

**Interfaces:**
- Consumes: `CodeMergeFilters`, `CodeMergeOverview`, `MrPageRequest`, `MrPageResponse`（Task 5）
- Produces: `defaultCodeMergeFilters`, `getCodeMergeOverview`, `getCodeMergeMrs`（供 Task 8 使用）

- [ ] **Step 1: 更新 `frontend/src/api.ts`**

将文件替换为：

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api.ts
git commit -m "feat: add getCodeMergeOverview and getCodeMergeMrs API functions"
```

---

### Task 7: App.tsx 拆分 — shell + OverviewPage

**Files:**
- Create: `frontend/src/pages/OverviewPage.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Produces: `OverviewPage({ onUpdatedAt })`, 精简后的 `App`（含 `activePage` 状态）（供 Task 8 使用）

- [ ] **Step 1: 创建 `frontend/src/pages/` 目录并写入 `OverviewPage.tsx`**

新建文件 `frontend/src/pages/OverviewPage.tsx`：

```tsx
import { useEffect, useState, type ReactNode } from "react";
import {
  BarChart3,
  ChevronDown,
  Code2,
  Database,
  Download,
  Loader2,
  Users,
} from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultFilters, exportReport, getFilterOptions, getOverview } from "../api";
import type {
  DashboardFilters,
  DashboardOverview,
  FilterOptions,
  Insight,
  KpiMetric,
  MrDetail,
  RankingRow,
  TokenDetail,
  UserDetail,
} from "../types";

const kpiIcons = [Users, Users, Database, Code2, Code2, Database];

export function OverviewPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<DashboardFilters>(defaultFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, data] = await Promise.all([getFilterOptions(), getOverview(filters)]);
      setFilterOptions(options);
      setOverview(data);
      onUpdatedAt(data.updated_at);
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
      const data = await getOverview(nextFilters);
      setOverview(data);
      onUpdatedAt(data.updated_at);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function onExport() {
    await exportReport(filters);
  }

  const activeFilters = overview?.filters ?? filters;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>AI Coding 运营看板</h1>
          <p>面向无线 / PDU / LM 团队的 AI Coding 使用、成本与入库效果运营分析</p>
        </div>
        <button className="export-button" onClick={onExport}>
          <Download size={16} />
          导出报告
        </button>
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
            {overview.kpis.map((metric, index) => (
              <KpiCard key={metric.key} metric={metric} iconIndex={index} />
            ))}
          </section>

          <section className="chart-grid">
            <ChartPanel title="活跃用户趋势" action="按日">
              <ReactECharts option={activeUserOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="Token 消耗趋势" action="按日">
              <ReactECharts option={tokenOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI MR代码入库占比趋势" action="按日">
              <ReactECharts option={aiRatioOption(overview)} notMerge className="chart" />
            </ChartPanel>
          </section>

          <section className="analysis-grid">
            <RankingPanel rows={overview.rankings} />
            <ChartPanel title="成本-产出分析" action="按团队">
              <ReactECharts option={quadrantOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <InsightsPanel insights={overview.insights} />
          </section>

          <DetailTabs users={overview.users} mrs={overview.mrs} tokens={overview.tokens} />
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

function KpiCard({ metric, iconIndex }: { metric: KpiMetric; iconIndex: number }) {
  const Icon = kpiIcons[iconIndex] ?? BarChart3;
  return (
    <article className={`kpi-card accent-${metric.accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{metric.label}</h3>
        <div className="kpi-value">
          {metric.value}
          {metric.unit ? <span>{metric.unit}</span> : null}
        </div>
        <p className={`delta ${metric.direction}`}>
          {metric.previous_label}
          <span>
            {metric.direction === "down" ? "▼" : "▲"} {metric.change}
          </span>
        </p>
      </div>
    </article>
  );
}

function ChartPanel({
  title,
  action,
  children,
}: {
  title: string;
  action?: string;
  children: ReactNode;
}) {
  return (
    <article className="panel">
      <div className="panel-header">
        <h2>
          {title}
          <span className="info-dot">i</span>
        </h2>
        {action ? (
          <button className="small-select">
            {action}
            <ChevronDown size={14} />
          </button>
        ) : null}
      </div>
      {children}
    </article>
  );
}

function RankingPanel({ rows }: { rows: RankingRow[] }) {
  return (
    <article className="panel ranking-panel">
      <div className="panel-header">
        <h2>
          PDU / LM 团队运营排行<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="ranking-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>PDU</th>
            <th>LM团队</th>
            <th>活跃用户</th>
            <th>上量占比</th>
            <th>Token（亿）</th>
            <th>AI入库行数</th>
            <th>AI MR占比</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.rank}>
              <td>
                <span className={`rank rank-${row.rank}`}>{row.rank}</span>
              </td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.active_users}</td>
              <td>{row.rollout_ratio}%</td>
              <td>{row.token_cost}</td>
              <td>{row.ai_lines.toLocaleString()}</td>
              <td>{row.ai_mr_ratio}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="panel-footer">1 / 8</div>
    </article>
  );
}

function InsightsPanel({ insights }: { insights: Insight[] }) {
  return (
    <article className="panel insights-panel">
      <div className="panel-header">
        <h2>
          重点运营关注<span className="info-dot">i</span>
        </h2>
      </div>
      <div className="insight-list">
        {insights.map((item) => (
          <div key={item.title} className={`insight ${item.type}`}>
            <div className="insight-icon">
              {item.type === "risk" ? "!" : item.type === "warning" ? "?" : item.type === "success" ? "↗" : "i"}
            </div>
            <div>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function DetailTabs({
  users,
  mrs,
  tokens,
}: {
  users: UserDetail[];
  mrs: MrDetail[];
  tokens: TokenDetail[];
}) {
  const [activeTab, setActiveTab] = useState<"users" | "mrs" | "tokens">("users");
  const tabs = [
    ["users", "用户明细"],
    ["mrs", "MR明细"],
    ["tokens", "Token明细"],
  ] as const;

  return (
    <section className="panel detail-panel">
      <div className="tabs">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            className={activeTab === key ? "is-active" : ""}
            onClick={() => setActiveTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {activeTab === "users" ? <UsersTable rows={users} /> : null}
      {activeTab === "mrs" ? <MrsTable rows={mrs} /> : null}
      {activeTab === "tokens" ? <TokensTable rows={tokens} /> : null}
      <div className="table-footer">
        <span>共 1,268 条</span>
        <button disabled>‹</button>
        <button className="is-active">1</button>
        <button>2</button>
        <button>3</button>
        <button>›</button>
        <span>每页 10 条</span>
      </div>
    </section>
  );
}

function UsersTable({ rows }: { rows: UserDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>用户</th>
          <th>PDU</th>
          <th>LM团队</th>
          <th>端类型</th>
          <th>客户端版本</th>
          <th>IDE类型</th>
          <th>最近活跃时间</th>
          <th>Prompt数</th>
          <th>Token（万）</th>
          <th>MR数</th>
          <th>AI入库行数</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.name}</td>
            <td>{row.pdu}</td>
            <td>{row.lm_team}</td>
            <td>{row.terminal_type}</td>
            <td>{row.client_version}</td>
            <td>{row.ide_type}</td>
            <td>{row.last_active_at ?? "-"}</td>
            <td>{row.prompt_count}</td>
            <td>{row.token_cost}</td>
            <td>{row.mr_count}</td>
            <td>{row.ai_lines.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function MrsTable({ rows }: { rows: MrDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>MR</th>
          <th>仓库</th>
          <th>作者</th>
          <th>PDU</th>
          <th>LM团队</th>
          <th>合入时间</th>
          <th>有效代码行</th>
          <th>AI代码行</th>
          <th>AI MR占比</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.mr_id}>
            <td>{row.mr_id}</td>
            <td>{row.repository}</td>
            <td>{row.author}</td>
            <td>{row.pdu}</td>
            <td>{row.lm_team}</td>
            <td>{row.merged_at}</td>
            <td>{row.total_lines.toLocaleString()}</td>
            <td>{row.ai_lines.toLocaleString()}</td>
            <td>{row.ai_mr_ratio}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TokensTable({ rows }: { rows: TokenDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>日期</th>
          <th>用户</th>
          <th>模型</th>
          <th>输入Token</th>
          <th>输出Token</th>
          <th>总Token</th>
          <th>Trace ID</th>
          <th>状态码</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.date}</td>
            <td>{row.user}</td>
            <td>{row.model}</td>
            <td>{row.input_tokens.toLocaleString()}</td>
            <td>{row.output_tokens.toLocaleString()}</td>
            <td>{row.total_tokens.toLocaleString()}</td>
            <td>{row.trace_id}</td>
            <td>{row.status_code}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function baseGrid() {
  return {
    grid: { left: 48, right: 20, top: 36, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" },
  };
}

function activeUserOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "活跃用户数（人）", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        data: data.trends.map((d) => d.active_users),
        type: "line",
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: "rgba(37, 111, 246, .12)" },
        lineStyle: { width: 3, color: "#256ff6" },
        itemStyle: { color: "#256ff6" },
      },
    ],
  };
}

function tokenOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "Token 消耗（亿）", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        data: data.trends.map((d) => d.token_cost),
        type: "bar",
        barWidth: 10,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: "#2f7df6" },
      },
    ],
  };
}

function aiRatioOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "%", min: 0, max: 50, splitLine: { lineStyle: { color: "#f0dada" } } },
    series: [
      {
        data: data.trends.map((d) => d.ai_mr_ratio),
        type: "line",
        smooth: true,
        symbolSize: 6,
        areaStyle: { color: "rgba(238, 51, 66, .10)" },
        lineStyle: { width: 3, color: "#ef3445" },
        itemStyle: { color: "#ef3445" },
      },
    ],
  };
}

function quadrantOption(data: DashboardOverview) {
  return {
    grid: { left: 58, right: 44, top: 34, bottom: 48 },
    tooltip: {
      formatter: (params: { data: [number, number, number, string] }) =>
        `${params.data[3]}<br/>Token: ${params.data[0]}亿<br/>AI MR占比: ${params.data[1]}%`,
    },
    xAxis: { name: "Token 消耗（亿）", splitLine: { lineStyle: { color: "#e7edf6" } } },
    yAxis: { name: "AI入库代码行数（万行）", splitLine: { lineStyle: { color: "#e7edf6" } } },
    series: [
      {
        type: "scatter",
        symbolSize: (value: number[]) => Math.max(16, Math.min(34, value[2] / 18000)),
        data: data.quadrant.map((d) => [d.token_cost, d.ai_mr_ratio, d.ai_lines, d.name]),
        itemStyle: {
          color: (params: { dataIndex: number }) =>
            ["#10b99a", "#17a48d", "#2c73f6", "#1f8cff", "#ef3445"][params.dataIndex % 5],
        },
        label: {
          show: true,
          formatter: (params: { data: [number, number, number, string] }) => params.data[3],
          position: "top",
          fontSize: 10,
          color: "#27344c",
        },
        labelLayout: { hideOverlap: true },
      },
    ],
  };
}
```

- [ ] **Step 2: 将 `frontend/src/App.tsx` 替换为精简的 shell**

```tsx
import { useState } from "react";
import { Bell, Box, Code2, Database, Home, LineChart, RefreshCcw, Settings, Users, WalletCards } from "lucide-react";
import { CodeMergePage } from "./pages/CodeMergePage";
import { OverviewPage } from "./pages/OverviewPage";

type Page = "overview" | "codemerge";

const navItems: { label: string; icon: React.ComponentType<{ size?: number }>; page: Page | null }[] = [
  { label: "概览", icon: Home, page: "overview" },
  { label: "运营分析", icon: LineChart, page: null },
  { label: "团队分析", icon: Users, page: null },
  { label: "用户分析", icon: Box, page: null },
  { label: "成本分析", icon: WalletCards, page: null },
  { label: "代码入库分析", icon: Database, page: "codemerge" },
  { label: "告警中心", icon: Bell, page: null },
  { label: "设置", icon: Settings, page: null },
];

export function App() {
  const [activePage, setActivePage] = useState<Page>("overview");
  const [updatedAt, setUpdatedAt] = useState("--");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <Code2 size={30} />
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`nav-item${activePage === item.page ? " is-active" : ""}`}
              onClick={() => {
                if (item.page) setActivePage(item.page);
              }}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sync-time">
          <RefreshCcw size={14} />
          <span>数据更新时间</span>
          <strong>{updatedAt}</strong>
        </div>
      </aside>
      <main className="dashboard">
        {activePage === "overview" && <OverviewPage onUpdatedAt={setUpdatedAt} />}
        {activePage === "codemerge" && <CodeMergePage onUpdatedAt={setUpdatedAt} />}
      </main>
    </div>
  );
}
```

- [ ] **Step 3: 验证 TypeScript 编译无错误**

```bash
cd frontend && pnpm build 2>&1 | tail -20
```

Expected: `built in` 字样，无 `error TS` 输出。若 `CodeMergePage` 尚未创建，期望只看到 `Cannot find module './pages/CodeMergePage'` 错误，其余无错。

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx frontend/src/pages/OverviewPage.tsx
git commit -m "refactor: split App.tsx into shell + OverviewPage"
```

---

### Task 8: 新建 CodeMergePage

**Files:**
- Create: `frontend/src/pages/CodeMergePage.tsx`

**Interfaces:**
- Consumes: `defaultCodeMergeFilters`, `getCodeMergeOverview`, `getCodeMergeMrs`, `getFilterOptions`（Task 6）；所有 code-merge 类型（Task 5）
- Produces: `CodeMergePage({ onUpdatedAt })`（供 App.tsx Task 7 使用）

- [ ] **Step 1: 创建 `frontend/src/pages/CodeMergePage.tsx`**

```tsx
import { useEffect, useState } from "react";
import { BarChart3, Box, ChevronDown, Code2, Database, Loader2, Users } from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultCodeMergeFilters, getCodeMergeMrs, getCodeMergeOverview, getFilterOptions } from "../api";
import type {
  CodeMergeFilters,
  CodeMergeOverview,
  ContributorMergeStats,
  FilterOptions,
  MergeTrendPoint,
  MrPageResponse,
  PduMergeStats,
  RepoMergeStats,
} from "../types";

const cmKpiIcons = [Code2, BarChart3, Database, Database, Box];

export function CodeMergePage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<CodeMergeFilters>(defaultCodeMergeFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<CodeMergeOverview | null>(null);
  const [mrs, setMrs] = useState<MrPageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tableState, setTableState] = useState({
    page: 1,
    sort_by: "merged_at",
    sort_order: "desc" as "asc" | "desc",
  });

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, ovData, mrData] = await Promise.all([
        getFilterOptions(),
        getCodeMergeOverview(filters),
        getCodeMergeMrs({ ...filters, ...tableState, page_size: 20 }),
      ]);
      setFilterOptions(options);
      setOverview(ovData);
      setMrs(mrData);
      onUpdatedAt("2025-05-20 10:30");
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters: CodeMergeFilters) {
    setIsLoading(true);
    setError(null);
    const nextTable = { ...tableState, page: 1 };
    setTableState(nextTable);
    try {
      const [ovData, mrData] = await Promise.all([
        getCodeMergeOverview(nextFilters),
        getCodeMergeMrs({ ...nextFilters, ...nextTable, page_size: 20 }),
      ]);
      setOverview(ovData);
      setMrs(mrData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchMrs(next: typeof tableState, currentFilters: CodeMergeFilters) {
    setTableLoading(true);
    try {
      const mrData = await getCodeMergeMrs({ ...currentFilters, ...next, page_size: 20 });
      setMrs(mrData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setTableLoading(false);
    }
  }

  function handleSort(col: string) {
    const nextOrder =
      tableState.sort_by === col && tableState.sort_order === "desc" ? "asc" : "desc";
    const next = { ...tableState, sort_by: col, sort_order: nextOrder, page: 1 };
    setTableState(next);
    void fetchMrs(next, filters);
  }

  function handlePage(page: number) {
    const next = { ...tableState, page };
    setTableState(next);
    void fetchMrs(next, filters);
  }

  function handleFilterChange(f: CodeMergeFilters) {
    setFilters(f);
    void query(f);
  }

  return (
    <>
      <header className="page-header">
        <div>
          <h1>代码入库分析</h1>
          <p>各 PDU 下 MR 入库中 AI 生成代码占比分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <CodeMergeFilterBar options={filterOptions} filters={filters} onChange={handleFilterChange} />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载入库数据
        </div>
      ) : overview ? (
        <>
          <section className="codemerge-kpi-grid">
            <CmKpiCard
              label="AI 代码入库行数"
              value={overview.kpis.total_ai_lines.toLocaleString()}
              change={overview.kpis.ai_lines_change}
              accent="blue"
              iconIdx={0}
            />
            <CmKpiCard
              label="整体 AI 代码占比"
              value={`${overview.kpis.overall_ai_ratio}%`}
              change={overview.kpis.ai_ratio_change}
              accent="cyan"
              iconIdx={1}
            />
            <CmKpiCard
              label="入库 MR 总数"
              value={overview.kpis.total_mrs.toLocaleString()}
              change={overview.kpis.mr_count_change}
              accent="green"
              iconIdx={2}
            />
            <CmKpiCard
              label="AI 辅助 MR 占比"
              value={`${overview.kpis.ai_assisted_ratio}%`}
              change={overview.kpis.ai_assisted_ratio_change}
              accent="red"
              iconIdx={3}
            />
            <CmKpiCard
              label="涉及仓库数"
              value={overview.kpis.total_repos.toLocaleString()}
              change={null}
              accent="blue"
              iconIdx={4}
            />
          </section>

          <section className="codemerge-chart-grid">
            <article className="panel">
              <div className="panel-header">
                <h2>
                  PDU 代码行数分布<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={pduBarOption(overview.pdu_breakdown)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  AI 代码占比趋势<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={trendOption(overview.trend)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  仓库 AI 代码行 Top 10<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={repoBarOption(overview.top_repos)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  开发者贡献分布<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts
                option={contributorScatterOption(overview.contributors)}
                notMerge
                style={{ height: 220 }}
              />
            </article>
          </section>

          {mrs ? (
            <MrTable
              response={mrs}
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

// ── Filter bar ─────────────────────────────────────────────────────────────

const thresholdOptions = [
  { label: "AI辅助MR阈值 ≥30%", value: 30 as const },
  { label: "AI辅助MR阈值 ≥50%", value: 50 as const },
  { label: "AI辅助MR阈值 ≥70%", value: 70 as const },
];

function CodeMergeFilterBar({
  options,
  filters,
  onChange,
}: {
  options: FilterOptions;
  filters: CodeMergeFilters;
  onChange: (f: CodeMergeFilters) => void;
}) {
  return (
    <div className="codemerge-filter-grid">
      <label className="filter-field">
        <span>时间范围</span>
        <select
          value={filters.date_range}
          onChange={(e) => onChange({ ...filters, date_range: e.target.value })}
        >
          {options.date_ranges.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>统计粒度</span>
        <select
          value={filters.granularity}
          onChange={(e) =>
            onChange({ ...filters, granularity: e.target.value as CodeMergeFilters["granularity"] })
          }
        >
          {options.granularities.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>PDU</span>
        <select
          value={filters.pdu}
          onChange={(e) => onChange({ ...filters, pdu: e.target.value })}
        >
          {options.pdus.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>LM团队</span>
        <select
          value={filters.lm_team}
          onChange={(e) => onChange({ ...filters, lm_team: e.target.value })}
        >
          {options.lm_teams.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>AI辅助MR阈值</span>
        <select
          value={filters.ai_ratio_threshold}
          onChange={(e) =>
            onChange({
              ...filters,
              ai_ratio_threshold: Number(e.target.value) as 30 | 50 | 70,
            })
          }
        >
          {thresholdOptions.map((o) => (
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

// ── KPI card ───────────────────────────────────────────────────────────────

function CmKpiCard({
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
  const Icon = cmKpiIcons[iconIdx] ?? BarChart3;
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

// ── MR table ───────────────────────────────────────────────────────────────

function MrTable({
  response,
  sortBy,
  sortOrder,
  onSort,
  onPage,
  loading,
}: {
  response: MrPageResponse;
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
          MR 明细<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>MR</th>
            <th>仓库</th>
            <th>作者</th>
            <th>PDU</th>
            <th>团队</th>
            <SortTh label="入库时间" col="merged_at" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="总行数" col="total_lines" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="AI行数" col="ai_lines" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="AI占比" col="ai_mr_ratio" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {response.items.map((row) => (
            <tr key={row.mr_id}>
              <td>{row.mr_id}</td>
              <td style={{ textAlign: "left" }}>{row.repository}</td>
              <td>{row.author}</td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.merged_at}</td>
              <td>{row.total_lines.toLocaleString()}</td>
              <td>{row.ai_lines.toLocaleString()}</td>
              <td>{row.ai_mr_ratio}%</td>
              <td>{row.status === "merged" ? "已合入" : "待合入"}</td>
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

// ── ECharts option builders ────────────────────────────────────────────────

function baseTextStyle() {
  return { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" };
}

function pduBarOption(pduBreakdown: PduMergeStats[]) {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { data: ["AI代码行", "非AI代码行"], bottom: 0, textStyle: baseTextStyle() },
    grid: { left: 90, right: 20, top: 20, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value" },
    yAxis: { type: "category", data: pduBreakdown.map((d) => d.pdu) },
    series: [
      {
        name: "非AI代码行",
        type: "bar",
        stack: "total",
        data: pduBreakdown.map((d) => d.total_lines - d.ai_lines),
        itemStyle: { color: "#e8edf5" },
      },
      {
        name: "AI代码行",
        type: "bar",
        stack: "total",
        data: pduBreakdown.map((d) => d.ai_lines),
        itemStyle: { color: "#256ff6" },
      },
    ],
  };
}

function trendOption(trend: MergeTrendPoint[]) {
  return {
    grid: { left: 56, right: 20, top: 28, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: baseTextStyle(),
    xAxis: { type: "category", data: trend.map((d) => d.date), axisTick: { show: false } },
    yAxis: {
      type: "value",
      name: "%",
      min: 0,
      splitLine: { lineStyle: { color: "#e8edf5" } },
    },
    series: [
      {
        data: trend.map((d) => d.ai_ratio),
        type: "line",
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: "rgba(37, 111, 246, .12)" },
        lineStyle: { width: 3, color: "#256ff6" },
        itemStyle: { color: "#256ff6" },
      },
    ],
  };
}

function repoBarOption(topRepos: RepoMergeStats[]) {
  const reversed = [...topRepos].reverse();
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 140, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "AI代码行数" },
    yAxis: { type: "category", data: reversed.map((d) => d.repository) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.ai_lines),
        itemStyle: { color: "#10b99a", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function contributorScatterOption(contributors: ContributorMergeStats[]) {
  const pdus = [...new Set(contributors.map((c) => c.pdu))];
  const colors = ["#256ff6", "#10b99a", "#ef3445", "#f5a623", "#9b59b6"];
  return {
    tooltip: {
      formatter: (params: { data: [number, number, number, string] }) =>
        `${params.data[3]}<br/>总代码行：${params.data[0].toLocaleString()}<br/>AI占比：${params.data[1]}%<br/>MR数：${params.data[2]}`,
    },
    legend: { data: pdus, bottom: 0, textStyle: baseTextStyle() },
    grid: { left: 58, right: 20, top: 16, bottom: 40 },
    textStyle: baseTextStyle(),
    xAxis: {
      type: "value",
      name: "总代码行数",
      splitLine: { lineStyle: { color: "#e8edf5" } },
    },
    yAxis: {
      type: "value",
      name: "AI占比（%）",
      min: 0,
      max: 50,
      splitLine: { lineStyle: { color: "#e8edf5" } },
    },
    series: pdus.map((pdu, i) => ({
      name: pdu,
      type: "scatter",
      symbolSize: (val: number[]) => Math.max(10, Math.min(36, val[2] * 2)),
      data: contributors
        .filter((c) => c.pdu === pdu)
        .map((c) => [c.total_lines, c.ai_ratio, c.mr_count, c.name]),
      itemStyle: { color: colors[i % colors.length] },
      label: {
        show: true,
        formatter: (p: { data: [number, number, number, string] }) => p.data[3],
        position: "top",
        fontSize: 10,
        color: "#27344c",
      },
      labelLayout: { hideOverlap: true },
    })),
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
git add frontend/src/pages/CodeMergePage.tsx
git commit -m "feat: add CodeMergePage with KPI cards, 4 charts, and paginated MR table"
```

---

### Task 9: 追加 CSS

**Files:**
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `.codemerge-kpi-grid`, `.codemerge-chart-grid`, `.codemerge-filter-grid`, `.th-sortable`（在 Task 8 的 JSX 中使用）

- [ ] **Step 1: 在 `frontend/src/styles.css` 末尾追加**

```css

/* ── Code Merge Analysis ──────────────────────────────────────────────────── */

.codemerge-kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.codemerge-chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.codemerge-filter-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  align-items: end;
}

.th-sortable {
  cursor: pointer;
  user-select: none;
}

.th-sortable:hover {
  background: #edf2f9;
}

@media (max-width: 1500px) {
  .codemerge-kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .codemerge-chart-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: 启动前端，目测验证**

```bash
cd frontend && pnpm dev
```

在浏览器打开 `http://127.0.0.1:5173`，点击左侧导航「代码入库分析」，检查：
1. 5 张 KPI 卡片正常显示数字和环比
2. 4 张图表均有内容（PDU 叠加柱、趋势线、仓库 Top 10、开发者散点）
3. MR 明细表显示 20 行，共 50 条
4. 点击「入库时间」列头，表格排序切换，翻页按钮正常
5. 切换 AI辅助MR阈值筛选项，页面重新请求数据
6. 切回「概览」，原有页面功能正常（回归）

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles.css
git commit -m "feat: add CSS for code merge analysis page"
```

---

## 执行方式

Plan complete and saved to `docs/superpowers/plans/2026-06-19-code-merge-analysis.md`. Two execution options:

**1. Subagent-Driven (recommended)** — 每个 Task 派发独立 subagent，任务间 review，快速迭代

**2. Inline Execution** — 在当前 session 中逐 Task 执行，每步有 checkpoint

Which approach?
