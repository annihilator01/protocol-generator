import pytest

from pytest_mock import MockerFixture

from core.db.repo import BaseRepo
from core.db.repo import ProtocolTokenRepo
from core.db.repo import TVLHistoryRepo
from core.service import ProtocolDataGeneratorService


@pytest.fixture
def protocol_data_generator_service(
    mocker: MockerFixture,
) -> ProtocolDataGeneratorService:
    db_session = mocker.AsyncMock()

    base_repo = BaseRepo(db_session)
    protocol_token_repo = ProtocolTokenRepo(db_session)
    tvl_history_repo = TVLHistoryRepo(db_session)

    service = ProtocolDataGeneratorService(
        base_repo=base_repo,
        protocol_token_repo=protocol_token_repo,
        tvl_history_repo=tvl_history_repo,
    )
    return service
