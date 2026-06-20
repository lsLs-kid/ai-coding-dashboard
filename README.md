# AI Coding 运营看板

面向 AI Coding 使用、Token 成本、MR 入库产出的运营分析看板。项目包含 Python FastAPI 后端和 React + TypeScript 前端，当前后端交互全部通过可替换的 mock provider 实现，便于后续接入真实湖表、CodeHub、组织人员映射等业务逻辑。

## 技术栈

- 后端：Python 3.11+、FastAPI、Pydantic、Uvicorn
- 前端：React、TypeScript、Vite、ECharts、Lucide Icons
- 数据：当前为 Mock 数据，已建立 PostgreSQL + SQLAlchemy 2.0 ORM 模型层（暂未对接真实库）

## 项目结构

```text
backend/
  app/
    api/                        # API 路由
    core/config.py              # 环境配置
    models/                     # SQLAlchemy ORM 模型（9 张表）
    db/session.py               # 异步数据库会话管理
    services/provider.py        # 数据服务抽象接口
    services/mock_provider.py   # Mock 数据实现
    services/sql_provider.py    # SQL 数据提供者骨架
    schemas.py                  # 前后端 API 契约
    main.py                     # FastAPI 应用入口
  alembic/                      # 数据库迁移
  requirements.txt
frontend/
  src/
    api.ts                      # 前端 API Client
    App.tsx                     # 页面主实现
    styles.css                  # 原型视觉样式
    types.ts                    # 前端类型定义
  package.json
  vite.config.ts
```

## API 接口

所有接口默认前缀为 `/api`。

| 方法 | 路径 | 说明 | 状态 |
| --- | --- | --- | --- |
| GET | `/health` | 后端健康检查 | 已实现 |
| GET | `/api/dashboard/filters` | 获取筛选项 | Mock 已实现 |
| POST | `/api/dashboard/overview` | 获取总览、KPI、图表、明细数据 | Mock 已实现 |
| POST | `/api/dashboard/users` | 获取用户明细 | Mock 已实现 |
| POST | `/api/dashboard/mrs` | 获取 MR 入库明细 | Mock 已实现 |
| POST | `/api/dashboard/tokens` | 获取 Token 明细 | Mock 已实现 |
| POST | `/api/dashboard/reports/export` | 导出报告任务 | Mock 已实现 |

请求筛选体：

```json
{
  "date_range": "last_30_days",
  "granularity": "day",
  "pdu": "all",
  "lm_team": "all",
  "user": "all",
  "terminal_type": "all",
  "client_version": "all",
  "ide_type": "all",
  "model": "all"
}
```

## 替换真实业务逻辑

后端数据读取被抽象为 `DashboardDataProvider`：

- 当前实现：`MockDashboardDataProvider`
- 替换位置：`backend/app/dependencies.py`
- 建议新增：`LakeTableDashboardDataProvider` 或 `ProductionDashboardDataProvider`

真实接入时建议按以下来源实现：

- CodeAgent GUI / CLI 湖表：用户数、Session、Prompt、Token、工具调用、错误数据
- CodeHub MR 数据：MR 总有效代码行、AI 生成并入库代码行、仓库、作者、合入时间
- 组织映射表：`user_id -> PDU -> LM团队`
- VersionPlan / AR 数据：后续补充 AR 维度指标

## 数据库与迁移

ORM 模型与 API Schema 严格分离，互不依赖。当前 `AICODING_DATA_PROVIDER=mock` 免数据库运行，设为 `sql` 则走 SQL 骨架（仍委托 mock）。

**首次建库（有 PostgreSQL 时）：**

```bash
cd backend
# 1. 创建数据库
createdb aicoding

# 2. 配置连接（backend/.env）
# AICODING_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aicoding

# 3. 执行迁移
source .venv/bin/activate
alembic upgrade head

# 4. 启动
AICODING_DATA_PROVIDER=sql uvicorn app.main:app --reload
```

**日常迁移：**

```bash
alembic revision --autogenerate -m "描述你的变更"  # 生成迁移文件
alembic upgrade head                                  # 应用迁移
alembic downgrade -1                                  # 回滚一步
alembic current                                       # 查看当前状态
alembic upgrade head --sql                            # 仅输出 SQL，不执行
```

## 本地运行

### 1. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

访问：

- 健康检查：http://127.0.0.1:8000/health
- API 文档：http://127.0.0.1:8000/docs

### 2. 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

访问：http://127.0.0.1:5173

前端 Vite 已配置 `/api` 代理到 `http://127.0.0.1:8000`。

## 构建部署

后端生产启动示例：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

前端构建：

```bash
cd frontend
pnpm install
pnpm build
```

构建产物位于 `frontend/dist`，可由 Nginx、静态资源服务器或后端网关托管。生产环境建议：

- 将前端静态资源部署到统一 Web 服务器。
- 将 `/api` 反向代理到 FastAPI 服务。
- 设置 `AICODING_CORS_ORIGINS` 为真实前端域名。
- 将 `AICODING_DATA_PROVIDER` 切换到真实 provider。

## 环境变量

后端 `.env` 示例见 `backend/.env.example`。

```env
AICODING_DATA_PROVIDER=mock
AICODING_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
AICODING_DATABASE_URL=postgresql+asyncpg://aicoding:aicoding@localhost:5432/aicoding
```

前端 `.env` 示例见 `frontend/.env.example`。

```env
VITE_API_BASE_URL=/api
```

## 待实现事项

- 接入真实湖表查询与权限控制。
- 接入 CodeHub MR AI 代码行与有效代码行数据。
- 增加组织人员映射同步任务。
- 增加真实导出报告能力。
- 增加接口鉴权、审计日志、异常告警。
- 增加单元测试和端到端测试。
