from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import DashboardFilters, OperationsOverview
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post("/overview", response_model=OperationsOverview)
def get_operations_overview(
    filters: DashboardFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> OperationsOverview:
    return provider.get_operations_overview(filters)
