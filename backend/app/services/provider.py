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
