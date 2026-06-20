from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import CostFilters, CostOverview, TokenPageRequest, TokenPageResponse
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/cost", tags=["cost"])


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
