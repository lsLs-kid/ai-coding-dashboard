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
    OperationsOverview,
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
    async def get_filter_options(self) -> FilterOptions:
        raise NotImplementedError

    @abstractmethod
    async def get_overview(self, filters: DashboardFilters) -> DashboardOverview:
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, filters: DashboardFilters) -> list[UserDetail]:
        raise NotImplementedError

    @abstractmethod
    async def get_mrs(self, filters: DashboardFilters) -> list[MrDetail]:
        raise NotImplementedError

    @abstractmethod
    async def get_tokens(self, filters: DashboardFilters) -> list[TokenDetail]:
        raise NotImplementedError

    @abstractmethod
    async def export_report(self, filters: DashboardFilters) -> ExportReportResponse:
        raise NotImplementedError

    @abstractmethod
    async def get_codemerge_overview(self, filters: CodeMergeFilters) -> CodeMergeOverview:
        raise NotImplementedError

    @abstractmethod
    async def get_codemerge_mrs(self, request: MrPageRequest) -> MrPageResponse:
        raise NotImplementedError

    @abstractmethod
    async def get_cost_overview(self, filters: CostFilters) -> CostOverview:
        raise NotImplementedError

    @abstractmethod
    async def get_cost_tokens(self, request: TokenPageRequest) -> TokenPageResponse:
        raise NotImplementedError

    @abstractmethod
    async def get_operations_overview(self, filters: DashboardFilters) -> OperationsOverview:
        raise NotImplementedError
