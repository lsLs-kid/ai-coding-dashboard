from app.core.config import get_settings
from app.services.mock_provider import MockDashboardDataProvider
from app.services.provider import DashboardDataProvider
from app.services.sql_provider import SqlDashboardDataProvider


def get_data_provider() -> DashboardDataProvider:
    """Select the data provider based on AICODING_DATA_PROVIDER config.

    Supported values:
        "mock"  — In-memory mock data (default, no DB needed)
        "sql"   — SQLAlchemy-backed (currently delegates to mock; skeleton)
    """
    settings = get_settings()
    name = settings.data_provider.lower()

    if name == "mock":
        return MockDashboardDataProvider()
    if name == "sql":
        return SqlDashboardDataProvider()
    raise RuntimeError(
        f"Unsupported data provider: {settings.data_provider!r}. "
        f"Supported values: 'mock', 'sql'."
    )
