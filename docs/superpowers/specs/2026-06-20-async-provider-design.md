# Async Provider 全链路改造 设计文档

> **目标**: 以最小改动让代码从 mock 切换到真实 PostgreSQL 数据。切换时只改 `sql_provider.py`，不动路由和 schemas。

## 核心思路

将 `DashboardDataProvider` ABC 及其所有实现、所有路由从 **同步改为异步**。改动纯机械——每个文件加 `async`/`await`，不改任何逻辑。

## 为什么选全链路 async

- FastAPI 原生支持 `async def` 路由，在事件循环中运行，和 SQLAlchemy async 完美配合
- mock provider 加 `async` 无任何副作用（`async` 函数内部可以不 `await`）
- SQL provider 可以自然使用 `await db.execute(select(...))`，不需要 `asyncio.run()` 包一层
- 每次改动模式完全一致，没有需要动脑的地方

## 改动范围（7 个文件）

| 文件 | 改动 |
|------|------|
| `backend/app/services/provider.py` | 11 个抽象方法加 `async` |
| `backend/app/services/mock_provider.py` | 11 个实现方法加 `async` |
| `backend/app/services/sql_provider.py` | 11 个委托方法加 `async` |
| `backend/app/api/routes.py` | 6 个路由 `def` → `async def`，调用加 `await` |
| `backend/app/api/codemerge_routes.py` | 2 个路由加 `async`/`await` |
| `backend/app/api/cost_routes.py` | 2 个路由加 `async`/`await` |
| `backend/app/api/operations_routes.py` | 1 个路由加 `async`/`await` |

## 不改的文件

- `schemas.py` — Pydantic 模型零改动
- `dependencies.py` — `get_data_provider()` 只是 new 对象，不需要 async
- `models/` — ORM 模型不变
- `db/session.py` — 已经是 async，不变
- `config.py` — 不变
- 前端 — 完全不涉及

## 改动模式

### ABC（provider.py）

```python
# 改前
@abstractmethod
def get_overview(self, filters: DashboardFilters) -> DashboardOverview: ...

# 改后
@abstractmethod
async def get_overview(self, filters: DashboardFilters) -> DashboardOverview: ...
```

### Mock 实现

```python
# 改前
def get_filter_options(self) -> FilterOptions:
    return FilterOptions(...)

# 改后
async def get_filter_options(self) -> FilterOptions:
    return FilterOptions(...)
```

### 路由

```python
# 改前
@router.post("/overview")
def get_overview(filters, provider = Depends(get_data_provider)):
    return provider.get_overview(filters)

# 改后
@router.post("/overview")
async def get_overview(filters, provider = Depends(get_data_provider)):
    return await provider.get_overview(filters)
```

## 切换 mock → SQL 的改动量

改造完成后，从 mock 切到真实 PG 只需改 **1 个文件**：`sql_provider.py`。

例如 `get_cost_overview` 方法：

```python
# 当前（委托 mock）
async def get_cost_overview(self, filters: CostFilters) -> CostOverview:
    return await self._mock.get_cost_overview(filters)

# 切真实数据后
async def get_cost_overview(self, filters: CostFilters) -> CostOverview:
    async with get_session_factory()() as session:
        result = await session.execute(
            select(
                TokenUsage.event_date,
                func.sum(TokenUsage.input_tokens),
                func.sum(TokenUsage.output_tokens),
            )
            .where(TokenUsage.event_date.between(start, end))
            .group_by(TokenUsage.event_date)
        )
        return CostOverview(...)
```

路由、schemas、前端全部不受影响。

## 验证

- 启动 `AICODING_DATA_PROVIDER=mock`，所有 API 返回数据不变
- 启动 `AICODING_DATA_PROVIDER=sql`，所有 API 返回数据不变（仍委托 mock）
- `alembic upgrade head --sql` 输出正确 DDL
