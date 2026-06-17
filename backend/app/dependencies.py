from app.core.config import get_settings
from app.services.mock_provider import MockDashboardDataProvider
from app.services.provider import DashboardDataProvider


def get_data_provider() -> DashboardDataProvider:
    settings = get_settings()
    if settings.data_provider != "mock":
        # Add real providers here, for example LakeTableDashboardDataProvider.
        raise RuntimeError(f"Unsupported data provider: {settings.data_provider}")
    return MockDashboardDataProvider()
