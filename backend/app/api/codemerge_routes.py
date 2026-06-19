from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_data_provider
from app.schemas import CodeMergeFilters, CodeMergeOverview, MrPageRequest, MrPageResponse
from app.services.provider import DashboardDataProvider

router = APIRouter(prefix="/codemerge", tags=["codemerge"])


@router.post("/overview", response_model=CodeMergeOverview)
def get_codemerge_overview(
    filters: CodeMergeFilters,
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> CodeMergeOverview:
    return provider.get_codemerge_overview(filters)


@router.get("/mrs", response_model=MrPageResponse)
def get_codemerge_mrs(
    request: Annotated[MrPageRequest, Depends()],
    provider: DashboardDataProvider = Depends(get_data_provider),
) -> MrPageResponse:
    return provider.get_codemerge_mrs(request)
