from abc import ABC, abstractmethod

from app.schemas import (
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOptions,
    MrDetail,
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
