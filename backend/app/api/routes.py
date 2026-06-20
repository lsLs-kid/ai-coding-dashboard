from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import (
    DashboardFilters,
    DashboardOverview,
    ExportReportResponse,
    FilterOptions,
    MrDetail,
    TokenDetail,
    UserDetail,
)
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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
