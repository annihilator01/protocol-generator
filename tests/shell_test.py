import datetime as dt
import pytest

from freezegun import freeze_time

from core.shell.model import GenerateProtocolDataCommandOptions


@freeze_time("2022-01-01")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "--accounts 100 --start 2021-01-01",
            GenerateProtocolDataCommandOptions(
                accounts=100,
                start=dt.datetime(2021, 1, 1),
                end=dt.datetime(2022, 1, 1),
            ),
        ),

        (
            "--accounts 100 --start 2021-01-01 "
            "--end 2021-01-10 --deposit 3000000",
            GenerateProtocolDataCommandOptions(
                accounts=100,
                start=dt.datetime(2021, 1, 1),
                end=dt.datetime(2021, 1, 10),
                deposit=3_000_000,
            ),
        ),

        (
            "",
            GenerateProtocolDataCommandOptions(
                start=dt.datetime(2022, 1, 1) - dt.timedelta(days=5),
                end=dt.datetime(2022, 1, 1),
            ),
        ),
    ]
)
async def test_generate_protocol_data_command_options_parse(
    test_input: str,
    expected: GenerateProtocolDataCommandOptions,
):
    opts = GenerateProtocolDataCommandOptions.parse_args(test_input)
    assert opts == expected
