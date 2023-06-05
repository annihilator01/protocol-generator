import pytest
import string

from core.service import ProtocolDataGeneratorService


@pytest.mark.asyncio
async def test_generate_name(
    protocol_data_generator_service: ProtocolDataGeneratorService,
):
    from_k = 4
    to_k = 10

    name = protocol_data_generator_service.generate_name(from_k=4, to_k=10)
    name_length = len(name)

    assert from_k <= name_length <= to_k
    assert len(set(name) - set(string.ascii_letters)) == 0


@pytest.mark.asyncio
async def test_generate_protocol_with_tokens(
    protocol_data_generator_service: ProtocolDataGeneratorService,
):
    protocol = (
        await protocol_data_generator_service.generate_protocol_with_tokens()
    )
    assert len(protocol.tokens) == protocol_data_generator_service.token_number


@pytest.mark.asyncio
async def test_generate_accounts(
    protocol_data_generator_service: ProtocolDataGeneratorService,
):
    accounts_number = 100
    accounts = (
        await protocol_data_generator_service.generate_accounts(
            accounts_number
        )
    )

    assert len(accounts) == accounts_number
    assert set(map(lambda acc: len(acc.wallet_address), accounts)) == {40}
