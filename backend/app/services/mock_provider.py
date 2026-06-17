from app.schemas import (
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOption,
    FilterOptions,
    Insight,
    KpiMetric,
    MrDetail,
    QuadrantPoint,
    RankingRow,
    TokenDetail,
    TrendPoint,
    UserDetail,
)
from app.services.provider import DashboardDataProvider


class MockDashboardDataProvider(DashboardDataProvider):
    def get_filter_options(self) -> FilterOptions:
        return FilterOptions(
            date_ranges=[
                FilterOption(label="近30天（04-21 ~ 05-20）", value="last_30_days"),
                FilterOption(label="本周", value="this_week"),
                FilterOption(label="本月", value="this_month"),
            ],
            granularities=[
                FilterOption(label="日", value="day"),
                FilterOption(label="周", value="week"),
                FilterOption(label="月", value="month"),
            ],
            pdus=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="无线", value="wireless"),
                FilterOption(label="PDU", value="pdu"),
            ],
            lm_teams=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="架构与算法LM", value="arch_algo"),
                FilterOption(label="软件平台LM", value="platform"),
                FilterOption(label="协议栈LM", value="protocol"),
                FilterOption(label="驱动开发LM", value="driver"),
                FilterOption(label="测试验证LM", value="qa"),
            ],
            users=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="张三", value="zhangsan"),
                FilterOption(label="李四", value="lisi"),
                FilterOption(label="王五", value="wangwu"),
            ],
            terminal_types=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="GUI", value="gui"),
                FilterOption(label="CLI", value="cli"),
            ],
            client_versions=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="v2.9.1", value="2.9.1"),
                FilterOption(label="v2.8.3", value="2.8.3"),
                FilterOption(label="v2.7.9", value="2.7.9"),
            ],
            ide_types=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="VS Code", value="vscode"),
                FilterOption(label="JetBrains", value="jetbrains"),
            ],
            models=[
                FilterOption(label="全部", value="all"),
                FilterOption(label="MiniMax-M2.7", value="minimax-m2.7"),
                FilterOption(label="DeepSeek-V3", value="deepseek-v3"),
            ],
        )

    def get_overview(self, filters: DashboardFilters) -> DashboardOverview:
        return DashboardOverview(
            filters=filters,
            updated_at="2025-05-20 10:30",
            kpis=[
                KpiMetric(key="active_users", label="活跃用户数", value="1,268", change="12.6%", direction="up", accent="blue"),
                KpiMetric(key="rollout_ratio", label="用户上量占比", value="56.8%", change="3.2pp", direction="down", accent="red"),
                KpiMetric(key="token_cost", label="Token 总消耗", value="48.72", unit="亿", change="18.7%", direction="up", accent="red"),
                KpiMetric(key="ai_mr_ratio", label="AI MR代码入库占比", value="31.6%", change="4.5pp", direction="up", accent="red"),
                KpiMetric(key="ai_lines", label="AI入库代码行数", value="2,456,892", change="24.3%", direction="up", accent="cyan"),
                KpiMetric(key="avg_token", label="人均Token", value="3.84M", change="5.4%", direction="up", accent="cyan"),
            ],
            trends=self._trends(),
            rankings=self._rankings(),
            quadrant=self._quadrant(),
            insights=self._insights(),
            users=self.get_users(filters),
            mrs=self.get_mrs(filters),
            tokens=self.get_tokens(filters),
        )

    def get_users(self, filters: DashboardFilters) -> list[UserDetail]:
        rows = [
            ("u001", "张三", "无线", "架构与算法LM", "GUI", "v2.9.1", "VS Code", "2025-05-20 10:15", 128, 152.6, 18, 12842, "active"),
            ("u002", "李四", "PDU", "软件平台LM", "CLI", "v2.9.1", "JetBrains", "2025-05-20 10:08", 96, 98.3, 14, 8731, "active"),
            ("u003", "王五", "无线", "协议栈LM", "GUI", "v2.8.3", "VS Code", "2025-05-20 09:54", 84, 76.1, 11, 6542, "active"),
            ("u004", "赵六", "PDU", "驱动开发LM", "GUI", "v2.9.0", "VS Code", "2025-05-20 09:40", 72, 65.4, 9, 5231, "low"),
            ("u005", "孙七", "无线", "测试验证LM", "CLI", "v2.7.9", "VS Code", "2025-05-20 09:32", 68, 54.2, 7, 4112, "low"),
        ]
        return [UserDetail(id=r[0], name=r[1], pdu=r[2], lm_team=r[3], terminal_type=r[4], client_version=r[5], ide_type=r[6], last_active_at=r[7], prompt_count=r[8], token_cost=r[9], mr_count=r[10], ai_lines=r[11], status=r[12]) for r in rows]

    def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]:
        rows = [
            ("MR-10291", "wireless/baseband", "张三", "无线", "架构与算法LM", "2025-05-20 09:42", 34820, 12842, 36.9, "merged"),
            ("MR-10276", "platform/runtime", "李四", "PDU", "软件平台LM", "2025-05-19 18:21", 26320, 8731, 33.2, "merged"),
            ("MR-10248", "protocol/stack", "王五", "无线", "协议栈LM", "2025-05-19 16:08", 18160, 6542, 36.0, "merged"),
        ]
        return [MrDetail(mr_id=r[0], repository=r[1], author=r[2], pdu=r[3], lm_team=r[4], merged_at=r[5], total_lines=r[6], ai_lines=r[7], ai_mr_ratio=r[8], status=r[9]) for r in rows]

    def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]:
        rows = [
            ("tk-001", "2025-05-20", "张三", "MiniMax-M2.7", 423000, 326000, 749000, "trace_a19f", 200),
            ("tk-002", "2025-05-20", "李四", "MiniMax-M2.7", 351000, 224000, 575000, "trace_b27e", 200),
            ("tk-003", "2025-05-19", "王五", "DeepSeek-V3", 284000, 189000, 473000, "trace_c38a", 200),
        ]
        return [TokenDetail(id=r[0], date=r[1], user=r[2], model=r[3], input_tokens=r[4], output_tokens=r[5], total_tokens=r[6], trace_id=r[7], status_code=r[8]) for r in rows]

    def export_report(self, filters: DashboardFilters) -> ExportReportResponse:
        return ExportReportResponse(report_id="mock-report-20250520-1030", status="mocked", message="Mock report export accepted. Replace this provider method with a real export job.")

    def _trends(self) -> list[TrendPoint]:
        dates = ["04-21", "04-22", "04-23", "04-24", "04-25", "04-26", "04-27", "04-28", "04-29", "04-30", "05-01", "05-02", "05-03", "05-04", "05-05", "05-06", "05-07", "05-08", "05-09", "05-10", "05-11", "05-12", "05-13", "05-14", "05-15", "05-16", "05-17", "05-18", "05-19", "05-20"]
        users = [680, 810, 930, 1050, 860, 870, 1040, 910, 850, 960, 990, 820, 1060, 1210, 1030, 1170, 1120, 1020, 1240, 1060, 820, 990, 1370, 1510, 1200, 1330, 1190, 1400, 1240, 1290]
        tokens = [1.1, 1.7, 1.4, 2.0, 1.6, 1.3, 1.2, 1.5, 2.0, 1.1, 1.5, 2.1, 1.7, 1.3, 2.5, 1.6, 1.8, 2.0, 1.7, 1.6, 2.0, 0.8, 1.0, 1.8, 2.4, 1.7, 2.2, 2.1, 1.9, 1.7]
        ratios = [24, 27, 30, 28, 26, 29, 27, 28, 31, 29, 27, 30, 31, 28, 30, 29, 32, 35, 33, 31, 34, 35, 30, 32, 35, 36, 34, 37, 36, 35]
        return [TrendPoint(date=d, active_users=u, token_cost=t, ai_mr_ratio=r) for d, u, t, r in zip(dates, users, tokens, ratios)]

    def _rankings(self) -> list[RankingRow]:
        rows = [
            (1, "无线", "架构与算法LM", 286, 72.3, 12.46, 685432, 36.8),
            (2, "PDU", "软件平台LM", 241, 61.5, 9.87, 512738, 33.1),
            (3, "无线", "协议栈LM", 198, 55.2, 7.65, 397182, 30.4),
            (4, "PDU", "驱动开发LM", 177, 49.8, 6.31, 312664, 28.6),
            (5, "无线", "测试验证LM", 153, 42.6, 5.28, 248876, 27.2),
        ]
        return [RankingRow(rank=r[0], pdu=r[1], lm_team=r[2], active_users=r[3], rollout_ratio=r[4], token_cost=r[5], ai_lines=r[6], ai_mr_ratio=r[7]) for r in rows]

    def _quadrant(self) -> list[QuadrantPoint]:
        rows = [
            ("测试验证LM", 3.2, 62, 248876, "低投入高产出"),
            ("协议栈LM", 6.4, 60, 397182, "低投入高产出"),
            ("架构与算法LM", 12.5, 92, 685432, "高投入高产出"),
            ("软件平台LM", 12.0, 78, 512738, "高投入高产出"),
            ("驱动开发LM", 11.4, 38, 312664, "高投入低产出"),
        ]
        return [QuadrantPoint(name=r[0], token_cost=r[1], ai_mr_ratio=r[2], ai_lines=r[3], category=r[4]) for r in rows]

    def _insights(self) -> list[Insight]:
        return [
            Insight(type="risk", title="架构与算法LM 团队 Token 消耗高", description="但 AI MR代码入库占比偏低，建议优化生成策略与评审流程。"),
            Insight(type="warning", title="测试验证LM 团队上量占比不足 45%", description="建议加强推广与使用引导，优先确认账号覆盖范围。"),
            Insight(type="info", title="客户端版本 v2.8.3 错误率偏高", description="较均值高 18%，建议排查并修复插件侧异常。"),
            Insight(type="success", title="软件平台LM 连续 3 周上升", description="AI MR代码入库占比持续提升，建议复制经验。"),
        ]
