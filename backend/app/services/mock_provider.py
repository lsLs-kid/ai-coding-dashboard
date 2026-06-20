from app.schemas import (
    AiAcceptedLinesTrendPoint,
    AiAdoptionTrendPoint,
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
    OperationsKpi,
    OperationsOverview,
    PduCostStats,
    PduMergeStats,
    QuadrantPoint,
    RankingRow,
    RepoMergeStats,
    TokenDetail,
    TokenPageRequest,
    TokenPageResponse,
    ToolCallTopItem,
    ToolCallTrendPoint,
    TrendPoint,
    UserDetail,
    UserIssueByType,
    UserIssueTrendPoint,
)
from app.services.provider import DashboardDataProvider


class MockDashboardDataProvider(DashboardDataProvider):
    async def get_filter_options(self) -> FilterOptions:
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

    async def get_overview(self, filters: DashboardFilters) -> DashboardOverview:
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

    async def get_users(self, filters: DashboardFilters) -> list[UserDetail]:
        rows = [
            ("u001", "张三", "无线", "架构与算法LM", "GUI", "v2.9.1", "VS Code", "2025-05-20 10:15", 128, 152.6, 18, 12842, "active"),
            ("u002", "李四", "PDU", "软件平台LM", "CLI", "v2.9.1", "JetBrains", "2025-05-20 10:08", 96, 98.3, 14, 8731, "active"),
            ("u003", "王五", "无线", "协议栈LM", "GUI", "v2.8.3", "VS Code", "2025-05-20 09:54", 84, 76.1, 11, 6542, "active"),
            ("u004", "赵六", "PDU", "驱动开发LM", "GUI", "v2.9.0", "VS Code", "2025-05-20 09:40", 72, 65.4, 9, 5231, "low"),
            ("u005", "孙七", "无线", "测试验证LM", "CLI", "v2.7.9", "VS Code", "2025-05-20 09:32", 68, 54.2, 7, 4112, "low"),
        ]
        return [UserDetail(id=r[0], name=r[1], pdu=r[2], lm_team=r[3], terminal_type=r[4], client_version=r[5], ide_type=r[6], last_active_at=r[7], prompt_count=r[8], token_cost=r[9], mr_count=r[10], ai_lines=r[11], status=r[12]) for r in rows]

    async def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]:
        rows = [
            ("MR-10291", "wireless/baseband", "张三", "无线", "架构与算法LM", "2025-05-20 09:42", 34820, 12842, 36.9, "merged"),
            ("MR-10276", "platform/runtime", "李四", "PDU", "软件平台LM", "2025-05-19 18:21", 26320, 8731, 33.2, "merged"),
            ("MR-10248", "protocol/stack", "王五", "无线", "协议栈LM", "2025-05-19 16:08", 18160, 6542, 36.0, "merged"),
        ]
        return [MrDetail(mr_id=r[0], repository=r[1], author=r[2], pdu=r[3], lm_team=r[4], merged_at=r[5], total_lines=r[6], ai_lines=r[7], ai_mr_ratio=r[8], status=r[9]) for r in rows]

    async def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]:
        rows = [
            ("tk-001", "2025-05-20", "张三", "无线PDU", "架构与算法LM", "MiniMax-M2.7", 423000, 326000, 749000, "trace_a19f", 200),
            ("tk-002", "2025-05-20", "李四", "软件PDU", "软件平台LM", "MiniMax-M2.7", 351000, 224000, 575000, "trace_b27e", 200),
            ("tk-003", "2025-05-19", "王五", "协议栈PDU", "协议栈LM", "DeepSeek-V3", 284000, 189000, 473000, "trace_c38a", 200),
        ]
        return [TokenDetail(id=r[0], date=r[1], user=r[2], pdu=r[3], lm_team=r[4], model=r[5], input_tokens=r[6], output_tokens=r[7], total_tokens=r[8], trace_id=r[9], status_code=r[10]) for r in rows]

    async def export_report(self, filters: DashboardFilters) -> ExportReportResponse:
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

    async def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview:
        # ai_assisted counts vary by threshold so the selector has visible effect
        threshold_data = {
            30: (1324, 71.7, "+8.2pp"),
            50: (892,  48.3, "+6.1pp"),
            70: (421,  22.8, "+3.4pp"),
        }
        ai_assisted_mrs, ai_assisted_ratio, ai_assisted_ratio_change = threshold_data[filters.ai_ratio_threshold]
        return CodeMergeOverview(
            kpis=CodeMergeKpi(
                total_ai_lines=2_456_892,
                total_lines=7_842_314,
                overall_ai_ratio=31.3,
                total_mrs=1847,
                ai_assisted_mrs=ai_assisted_mrs,
                ai_assisted_ratio=ai_assisted_ratio,
                total_repos=127,
                ai_lines_change="+24.3%",
                ai_ratio_change="+4.5pp",
                mr_count_change="+18.2%",
                ai_assisted_ratio_change=ai_assisted_ratio_change,
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
            mr_ratio_distribution=self._mr_ratio_distribution(),
        )

    async def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse:
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

    def _mr_ratio_distribution(self) -> list[MrRatioBucket]:
        buckets = {f"{i * 10}–{(i + 1) * 10}%": 0 for i in range(10)}
        for mr in self._mr_list():
            idx = min(int(mr.ai_mr_ratio // 10), 9)
            buckets[f"{idx * 10}–{(idx + 1) * 10}%"] += 1
        return [MrRatioBucket(label=k, count=v) for k, v in buckets.items()]

    async def get_cost_overview(self, filters: CostFilters) -> CostOverview:
        """Return cost analysis KPIs and charts.

        Notes: mock returns static KPI values; real provider must apply
        date_range, pdu, lm_team, user, terminal_type, client_version,
        ide_type, model, and cost_type filters.
        """
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

    async def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse:
        """Return paginated, sorted token detail list.

        Notes: mock applies pdu, lm_team, user, model filters and
        server-side sorting/pagination; real provider should also apply
        date_range and cost_type filters.
        """
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

    async def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview:
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
                pdu=pdus[idx],
                lm_team=teams[idx],
                model=models[i % 2],
                input_tokens=inp,
                output_tokens=out,
                total_tokens=inp + out,
                trace_id=f"trace_{i:04d}",
                status_code=200,
            ))
        return rows

    def _mr_list(self) -> list[MrDetail]:
        pdus    = ["无线PDU",   "软件PDU",   "协议栈PDU", "驱动PDU",   "测试PDU"]
        teams   = ["架构与算法LM","软件平台LM","协议栈LM",  "驱动开发LM","测试验证LM"]
        repos   = ["wireless/baseband","platform/runtime","protocol/stack","driver/kernel","qa/framework",
                   "wireless/modem",   "platform/sdk",    "driver/display","protocol/mac", "qa/integration"]
        authors = ["张三","李四","王五","赵六","孙七","周八","吴九","郑十"]
        # Varied ratios that produce a realistic distribution across 5 buckets
        ratios = [
            8.4, 14.2, 17.8, 12.6, 9.1, 16.3, 11.7, 18.9,           # 0–20%:  8
            21.4, 34.7, 28.3, 36.9, 25.1, 38.2, 22.8, 31.6,
            29.4, 33.8, 27.2, 35.5, 24.9, 32.1, 26.7, 37.4,
            30.8, 23.5, 28.9, 35.1, 22.4, 34.3,                      # 20–40%: 22
            41.2, 53.8, 47.6, 56.1, 44.3, 58.9, 42.7, 49.4,
            51.8, 45.2, 55.3, 48.7, 43.9, 52.4,                      # 40–60%: 14
            62.4, 71.8, 67.3, 74.1, 69.5,                            # 60–80%:  5
            83.7, 91.2,                                               # 80–100%: 2 (total=51, trim last)
        ]
        rows = []
        for i in range(50):
            idx = i % 5
            total = max(1000, 34820 - i * 520)
            ratio = ratios[i]
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
