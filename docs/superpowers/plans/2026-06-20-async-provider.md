# Async Provider 全链路改造 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 DashboardDataProvider ABC、所有实现、所有路由从 sync 改为 async，使 SQL provider 可以自然使用 `await` 查询。

**Architecture:** 纯机械改动——每个方法/路由前面加 `async`，每个调用点加 `await`。不改任何业务逻辑。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 async

## Global Constraints

- 不改任何业务逻辑，只加 `async`/`await` 关键字
- 不改 schemas.py、dependencies.py、models/、db/
- mock provider 行为完全不变
- sql provider 行为完全不变（仍委托 mock）

---

### Task 1: Provider 层异步化

**Files:**
- Modify: `backend/app/services/provider.py`
- Modify: `backend/app/services/mock_provider.py`
- Modify: `backend/app/services/sql_provider.py`

**Interfaces:**
- Consumes: nothing (Task 1 goes first)
- Produces: 11 async ABC methods; mock + sql implementations

`provider.py` 的 11 个抽象方法，每个前面加 `async`：

```python
class DashboardDataProvider(ABC):
    @abstractmethod
    async def get_filter_options(self) -> FilterOptions: ...

    @abstractmethod
    async def get_overview(self, filters: DashboardFilters) -> DashboardOverview: ...

    @abstractmethod
    async def get_users(self, filters: DashboardFilters) -> list[UserDetail]: ...

    @abstractmethod
    async def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]: ...

    @abstractmethod
    async def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]: ...

    @abstractmethod
    async def export_report(self, filters: DashboardFilters) -> ExportReportResponse: ...

    @abstractmethod
    async def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview: ...

    @abstractmethod
    async def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse: ...

    @abstractmethod
    async def get_cost_overview(self, filters: CostFilters) -> CostOverview: ...

    @abstractmethod
    async def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse: ...

    @abstractmethod
    async def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview: ...
```

`mock_provider.py` 的 11 个方法，每个 `def` → `async def`，方法体不改。

`sql_provider.py` 的 11 个方法，每个 `def` → `async def`，每个 `self._mock.xxx(...)` 调用前加 `await`。

- [ ] **Step 1: 改 provider.py** — 11 个方法签名的 `def` → `async def`
- [ ] **Step 2: 改 mock_provider.py** — 11 个方法的 `def` → `async def`（不改方法体）
- [ ] **Step 3: 改 sql_provider.py** — 11 个方法的 `def` → `async def`，返回值表达式加 `await`
- [ ] **Step 4: 验证 mock 和 sql provider 可正常导入**

```bash
cd backend && source .venv/bin/activate
python -c "from app.services.mock_provider import MockDashboardDataProvider; print('mock OK')"
python -c "from app.services.sql_provider import SqlDashboardDataProvider; print('sql OK')"
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/provider.py backend/app/services/mock_provider.py backend/app/services/sql_provider.py
git commit -m "refactor: convert provider ABC and implementations to async"
```

---

### Task 2: 路由层异步化

**Files:**
- Modify: `backend/app/api/routes.py`
- Modify: `backend/app/api/codemerge_routes.py`
- Modify: `backend/app/api/cost_routes.py`
- Modify: `backend/app/api/operations_routes.py`

每个路由函数 `def` → `async def`，provider 调用前加 `await`。

`routes.py` — 6 个端点：

```python
@router.get("/filters", response_model=FilterOptions)
async def get_filters(provider: DashboardDataProvider = Depends(get_data_provider)) -> FilterOptions:
    return await provider.get_filter_options()

@router.post("/overview", response_model=DashboardOverview)
async def get_overview(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> DashboardOverview:
    return await provider.get_overview(filters)

@router.post("/users", response_model=list[UserDetail])
async def get_users(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> list[UserDetail]:
    return await provider.get_users(filters)

@router.post("/mrs", response_model=list[MrDetail])
async def get_mrs(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> list[MrDetail]:
    return await provider.get_mrs(filters)

@router.post("/tokens", response_model=list[TokenDetail])
async def get_tokens(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> list[TokenDetail]:
    return await provider.get_tokens(filters)

@router.post("/reports/export", response_model=ExportReportResponse)
async def export_report(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> ExportReportResponse:
    return await provider.export_report(filters)
```

`codemerge_routes.py` — 2 个端点：

```python
@router.post("/overview", response_model=CodeMergeOverview)
async def get_codemerge_overview(
    filters: CodeMergeFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> CodeMergeOverview:
    return await provider.get_codemerge_overview(filters)

@router.get("/mrs", response_model=MrPageResponse)
async def get_codemerge_mrs(
    request: Annotated[MrPageRequest, Depends()],
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> MrPageResponse:
    return await provider.get_codemerge_mrs(request)
```

`cost_routes.py` — 2 个端点：

```python
@router.post("/overview", response_model=CostOverview)
async def get_cost_overview(
    filters: CostFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> CostOverview:
    return await provider.get_cost_overview(filters)

@router.get("/tokens", response_model=TokenPageResponse)
async def get_cost_tokens(
    request: Annotated[TokenPageRequest, Depends()],
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> TokenPageResponse:
    return await provider.get_cost_tokens(request)
```

`operations_routes.py` — 1 个端点：

```python
@router.post("/overview", response_model=OperationsOverview)
async def get_operations_overview(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> OperationsOverview:
    return await provider.get_operations_overview(filters)
```

- [ ] **Step 1: 改 routes.py** — 6 个路由的 `def` → `async def`，调用加 `await`
- [ ] **Step 2: 改 codemerge_routes.py** — 2 个路由加 `async`/`await`
- [ ] **Step 3: 改 cost_routes.py** — 2 个路由加 `async`/`await`
- [ ] **Step 4: 改 operations_routes.py** — 1 个路由加 `async`/`await`
- [ ] **Step 5: Commit**

```bash
git add backend/app/api/routes.py backend/app/api/codemerge_routes.py backend/app/api/cost_routes.py backend/app/api/operations_routes.py
git commit -m "refactor: convert all API routes to async"
```

---

### Task 3: 端到端验证

- [ ] **Step 1: 启动后端（mock 模式）并测试所有端点**

```bash
cd backend && source .venv/bin/activate
AICODING_DATA_PROVIDER=mock uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 2

# 测试关键端点
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/dashboard/filters | python -c "import sys,json; d=json.load(sys.stdin); assert len(d['date_ranges'])==3; print('filters OK')"
curl -s -X POST http://127.0.0.1:8000/api/dashboard/overview -H "Content-Type: application/json" -d '{"date_range":"last_30_days"}' | python -c "import sys,json; d=json.load(sys.stdin); assert len(d['kpis'])==6; print('overview OK')"
curl -s -X POST http://127.0.0.1:8000/api/operations/overview -H "Content-Type: application/json" -d '{}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'kpis' in d; print('operations OK')"
curl -s -X POST http://127.0.0.1:8000/api/cost/overview -H "Content-Type: application/json" -d '{}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'kpis' in d; print('cost OK')"
curl -s -X POST http://127.0.0.1:8000/api/codemerge/overview -H "Content-Type: application/json" -d '{}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'kpis' in d; print('codemerge OK')"

kill %1 2>/dev/null
```

- [ ] **Step 2: 启动后端（sql 模式）并测试**

```bash
AICODING_DATA_PROVIDER=sql uvicorn app.main:app --host 127.0.0.1 --port 8001 &
sleep 2

curl -s http://127.0.0.1:8001/health
curl -s http://127.0.0.1:8001/api/dashboard/filters | python -c "import sys,json; d=json.load(sys.stdin); assert len(d['date_ranges'])==3; print('sql: filters OK')"
curl -s -X POST http://127.0.0.1:8001/api/operations/overview -H "Content-Type: application/json" -d '{}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'kpis' in d; print('sql: operations OK')"

kill %1 2>/dev/null
```

- [ ] **Step 3: Commit (if any fixups needed)**

```bash
git add -A && git commit -m "chore: verification after async conversion"
```
