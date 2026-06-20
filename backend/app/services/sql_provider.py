"""SqlDashboardDataProvider — skeleton that delegates to mock.

When real database queries are implemented, each method will:
1. Accept an async session (or manage its own session lifecycle)
2. Build SQLAlchemy queries against the ORM models
3. Map ORM results to Pydantic response schemas
4. Fall back to mock delegation where not yet implemented
"""

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
from app.services.mock_provider import MockDashboardDataProvider
from app.services.provider import DashboardDataProvider


class SqlDashboardDataProvider(DashboardDataProvider):
    """SQL-backed provider.

    Initially delegates all methods to MockDashboardDataProvider.
    Replace individual methods with real SQLAlchemy queries as data
    sources become available.
    """

    def __init__(self) -> None:
        self._mock = MockDashboardDataProvider()

    # ── Dashboard Overview ──────────────────────────────────────────────

    def get_filter_options(self) -> FilterOptions:
        # TODO: Query pdu, lm_team, user, ai_model tables for distinct values
        return self._mock.get_filter_options()

    def get_overview(self, filters: DashboardFilters) -> DashboardOverview:
        # TODO: Run aggregate queries against token_usage, merge_request,
        #       user tables, grouped by date / user / pdu
        return self._mock.get_overview(filters)

    def get_users(self, filters: DashboardFilters) -> list[UserDetail]:
        # TODO: Query user table with joins to pdu, lm_team;
        #       aggregate prompt_count from token_usage,
        #       aggregate mr_count / ai_lines from merge_request
        return self._mock.get_users(filters)

    def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]:
        # TODO: Query merge_request with joins to user, repository
        return self._mock.get_mrs(filters)

    def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]:
        # TODO: Query token_usage with joins to user, ai_model
        return self._mock.get_tokens(filters)

    def export_report(self, filters: DashboardFilters) -> ExportReportResponse:
        # TODO: Enqueue a background export job or run a large query
        return self._mock.export_report(filters)

    # ── Code Merge Analysis ────────────────────────────────────────────

    def get_codemerge_overview(
        self, filters: CodeMergeFilters
    ) -> CodeMergeOverview:
        # TODO: Aggregate merge_request by date, pdu, repository;
        #       compute distributions by ai_mr_ratio buckets
        return self._mock.get_codemerge_overview(filters)

    def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse:
        # TODO: Paginated query against merge_request with joins,
        #       server-side sorting and filtering
        return self._mock.get_codemerge_mrs(request)

    # ── Cost Analysis ──────────────────────────────────────────────────

    def get_cost_overview(self, filters: CostFilters) -> CostOverview:
        # TODO: Aggregate token_usage by date, model, pdu;
        #       apply cost_type filter (input / output / total)
        return self._mock.get_cost_overview(filters)

    def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse:
        # TODO: Paginated query against token_usage with joins,
        #       server-side sorting and cost_type filtering
        return self._mock.get_cost_tokens(request)

    # ── Operations Analysis ────────────────────────────────────────────

    def get_operations_overview(
        self, filters: DashboardFilters
    ) -> OperationsOverview:
        # TODO: Aggregate tool_call by date and tool_name;
        #       aggregate user_issue by date and issue_type;
        #       compute AI adoption rate from merge_request
        return self._mock.get_operations_overview(filters)
